"""Remove superseded PC1 convergence effects and Off stubs from the .xsq.

This is the direct-delete reset step used before rebuilding the final
Mega Tree / Christ / expanded-scene choreography. Timing elements and all
unrelated model effects are preserved.

Close the sequence in xLights before running without --dry-run.
"""
from collections import defaultdict
from pathlib import Path
import re
import shutil
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
XSQ = SCRIPT_DIR.parent / "Holy Forever 2026.xsq"
BACKUP = SCRIPT_DIR.parent / "Backups" / "Holy Forever 2026.xsq.bak-before-pc1-clean-reapply"

PC1_START = 40950
PC1_END = 67570

HOUSE_CHASE_TARGETS = (
    "Colum Shrubs",
    "House Outline",
    "Roof",
    "Verts",
    "Windows",
    "Colums",
    "Icicles GRP",
)

ELEMENT_RE = re.compile(r'<Element type="(\w+)" name="([^"]*)"')
SUBMODEL_RE = re.compile(
    r'<SubModelEffectLayer\b[^>]*\bname="([^"]*)"'
)
EFFECT_RE = re.compile(
    r'<Effect\b[^>]*\bname="([^"]*)"[^>]*\bstartTime="(\d+)"'
    r'[^>]*\bendTime="(\d+)"[^>]*/>'
)


def overlaps_pc1(start, end):
    return end > PC1_START and start < PC1_END


def should_delete(element, submodel, name, start, end):
    if element == "Mega Tree":
        if name == "Off":
            return True
        return (
            overlaps_pc1(start, end)
            and name in {"Morph", "Meteors", "Shockwave"}
        )

    if element == "Whole Scene":
        return name == "Off" or (
            name == "Meteors" and overlaps_pc1(start, end)
        )

    if element == "Whole Scene w Matrixes":
        return name == "Off" or (
            name == "Meteors" and overlaps_pc1(start, end)
        )

    if element == "GE Merry Christmas":
        if submodel == "Christ":
            return name == "Off" or overlaps_pc1(start, end)
        if submodel is None:
            return name == "Off" or (
                name in {"On", "Shockwave", "Meteors"}
                and overlaps_pc1(start, end)
            )

    if element in HOUSE_CHASE_TARGETS:
        return name == "Meteors" and overlaps_pc1(start, end)

    return False


def main():
    dry_run = "--dry-run" in sys.argv
    lines = XSQ.read_text(encoding="utf-8").splitlines(keepends=True)

    out = []
    in_effects = False
    element = None
    submodel = None
    deleted = defaultdict(list)

    for line in lines:
        stripped = line.strip()
        if stripped == "<ElementEffects>":
            in_effects = True
        elif stripped == "</ElementEffects>":
            in_effects = False
        elif in_effects:
            element_match = ELEMENT_RE.search(line)
            if element_match:
                element = element_match.group(2)
                submodel = None
            else:
                submodel_match = SUBMODEL_RE.search(line)
                if submodel_match:
                    submodel = submodel_match.group(1)
                elif stripped == "</SubModelEffectLayer>":
                    submodel = None

                effect_match = EFFECT_RE.search(line)
                if effect_match:
                    name = effect_match.group(1)
                    start = int(effect_match.group(2))
                    end = int(effect_match.group(3))
                    if should_delete(element, submodel, name, start, end):
                        deleted[(element, submodel)].append((name, start, end))
                        continue
        out.append(line)

    total = sum(len(rows) for rows in deleted.values())
    print(f"{'DRY RUN — ' if dry_run else ''}deleting {total} superseded effects")
    for (element, submodel), rows in sorted(
        deleted.items(), key=lambda item: (item[0][0], item[0][1] or "")
    ):
        target = f"{element}/{submodel}" if submodel else element
        counts = defaultdict(int)
        for name, _, _ in rows:
            counts[name] += 1
        summary = ", ".join(
            f"{name}x{count}" for name, count in sorted(counts.items())
        )
        print(f"  {target}: {len(rows)} ({summary})")

    if dry_run:
        return
    if total == 0:
        print("nothing to delete")
        return

    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(XSQ, BACKUP)
    XSQ.write_text("".join(out), encoding="utf-8")
    print(f"backup: {BACKUP}")
    print(f"wrote:  {XSQ}")


if __name__ == "__main__":
    main()
