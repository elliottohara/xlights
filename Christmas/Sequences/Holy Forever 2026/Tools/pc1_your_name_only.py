"""Limit PC1 meteor convergence to the four sung "name" moments.

Removes Mega Tree Meteors Up, Whole Scene w Matrixes Meteors Implode,
GE Merry Christmas/Christ On blinks, and adjusts the parent Off mask so
meteors chase to Christ only when the lead vocal says "your name" — not
during "stands above them all" tails or "all thrones / powers" lines.

Close the sequence in xLights before running without --dry-run.

    python3 "Christmas/Sequences/Holy Forever 2026/Tools/pc1_your_name_only.py" [--dry-run]
"""
from collections import defaultdict
from pathlib import Path
import re
import shutil
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
XSQ = SCRIPT_DIR.parent / "Holy Forever 2026.xsq"
BACKUP = SCRIPT_DIR.parent / "Backups" / "Holy Forever 2026.xsq.bak-before-pc1-your-name-only"

PC1_START = 40950
PC1_END = 67570
OUTER_TRAVEL_MS = 1375

# Lyrics Lead word-layer "name" marks in PC1 (40950–66700).
NAME_WORDS = (
    (42250, 43175),
    (45600, 46625),
    (48950, 50250),
    (62175, 63400),
)

# Bass-pair first-star anchors (Tree Topper lead pulse of each double-hit).
STAR_FIRSTS = (
    42325,
    45650,
    49000,
    52325,
    55650,
    58975,
    62325,
    65650,
)

ELEMENT_RE = re.compile(r'<Element type="(\w+)" name="([^"]*)"')
SUBMODEL_RE = re.compile(r'<SubModelEffectLayer\b[^>]*\bname="([^"]*)"')
EFFECT_RE = re.compile(
    r'<Effect\b([^>]*)\bname="([^"]*)"[^>]*\bstartTime="(\d+)"'
    r'[^>]*\bendTime="(\d+)"[^>]*/>'
)


def cluster_for_first_star(first_star):
    return (first_star - OUTER_TRAVEL_MS, None)


def kept_clusters():
    kept = []
    for first_star in STAR_FIRSTS:
        if any(word_start <= first_star < word_end for word_start, word_end in NAME_WORDS):
            start = first_star - OUTER_TRAVEL_MS
            # End times match the live eight-window build (pair overlap through follow).
            ends = {
                42325: 43875,
                45650: 47175,
                49000: 50525,
                62325: 63875,
            }
            kept.append((start, ends[first_star], first_star))
    return kept


def in_kept_window(start, end, kept):
    return any(
        end > cluster_start and start < cluster_end
        for cluster_start, cluster_end, _ in kept
    )


def overlaps_pc1(start, end):
    return end > PC1_START and start < PC1_END


def main():
    dry_run = "--dry-run" in sys.argv
    kept = kept_clusters()
    kept_ranges = {(start, end) for start, end, _ in kept}

    print("Keeping meteor/Christ windows on 'name' only:")
    for start, end, first_star in kept:
        print(f"  {start}-{end} (first star {first_star})")

    lines = XSQ.read_text(encoding="utf-8").splitlines(keepends=True)
    out = []
    in_effects = False
    element = None
    submodel = None
    deleted = defaultdict(list)
    off_masks = []

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
                    name = effect_match.group(2)
                    start = int(effect_match.group(3))
                    end = int(effect_match.group(4))

                    if element == "Mega Tree" and name == "Meteors":
                        if overlaps_pc1(start, end) and not in_kept_window(start, end, kept):
                            deleted["Mega Tree"].append((name, start, end))
                            continue

                    if element == "Whole Scene w Matrixes" and name == "Meteors":
                        if overlaps_pc1(start, end) and not in_kept_window(start, end, kept):
                            deleted["Whole Scene w Matrixes"].append((name, start, end))
                            continue

                    if (
                        element == "GE Merry Christmas"
                        and submodel == "Christ"
                        and name == "On"
                        and overlaps_pc1(start, end)
                        and not in_kept_window(start, end, kept)
                    ):
                        deleted["GE Merry Christmas/Christ"].append((name, start, end))
                        continue

                    if (
                        element == "GE Merry Christmas"
                        and submodel is None
                        and name == "Off"
                        and start == PC1_START
                        and end == 67175
                    ):
                        deleted["GE Merry Christmas Off mask"].append((name, start, end))
                        continue

        out.append(line)

    # Replace the single continuous Off mask with one mask per kept window.
    insert_at = None
    for index, line in enumerate(out):
        if '<Element type="model" name="GE Merry Christmas">' in line:
            for j in range(index, min(index + 8, len(out))):
                if "<EffectLayer>" in out[j]:
                    insert_at = j + 1
                    break
            break

    if insert_at is None:
        raise RuntimeError("Could not locate GE Merry Christmas EffectLayer")

    off_lines = []
    for start, end, _ in kept:
        off_lines.append(
            f'        <Effect ref="11" name="Off" startTime="{start}" endTime="{end}" />\n'
        )

    for line in off_lines:
        deleted["GE Merry Christmas Off mask (add)"].append(("Off", "new", "new"))
    out[insert_at:insert_at] = off_lines

    total = sum(len(rows) for rows in deleted.values())
    print(f"\n{'DRY RUN — ' if dry_run else ''}{total} deletions, {len(off_lines)} Off masks to add")
    for target, rows in sorted(deleted.items()):
        print(f"  {target}: {len(rows)}")

    if dry_run:
        return

    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(XSQ, BACKUP)
    XSQ.write_text("".join(out), encoding="utf-8")
    print(f"backup: {BACKUP}")
    print(f"wrote:  {XSQ}")


if __name__ == "__main__":
    main()
