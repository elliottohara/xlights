"""Delete ALL effects on the house-face snowflake and spinner props
(Holy Forever 2026). User request 2026-07-13: clear the non-matrix props
on the face of the house (snowflakes + spinner-type props).

The xLights API cannot delete effects, so this edits the .xsq directly
(line-oriented; one self-closing <Effect .../> per line). Timing elements
and every other model element are untouched. Run with --dry-run first.

Pattern per AGENT NOTES: saveSequence -> cp backup -> run this ->
closeSequence + openSequence via the API so the live session matches disk.
"""
import re
import sys
from collections import defaultdict

XSQ = "/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq"

TARGETS = {
    # snowflakes (Flakes GRP = all Boscoyo + GE flakes; individual flakes carry no effects)
    "Flakes GRP",
    "Flakes Outline All GRP",
    "Flakes Spokes All GRP",
    "GE Flake N 1",
    "GE Flake N 2",
    # spinner full props on the house face
    "GE Reel Max 1",
    "GE Reel Max 2",
    "GE Starlord 1",
    "GE Starlord 2",
    "GE Rosa Grande 1",
    "GE Mini Grand Illusion",
    # spinner submodel groups (span the same house-face fixtures)
    "GE Reel Max Arrows GRP",
    "GE Reel Max Chevron Rings GRP",
    "GE Reel Max Spokes GRP",
    "GE Starlord Plunger All GRP",
    "GE Starlord Spoke GRP",
    "GE Starlord Star GRP",
    "GE Rosa Grande Ring GRP",
    "GE Rosa Grande Spoke GRP",
    "GE Rosa Grande Web Spoke GRP",
    "GE Baby Grand Illusion Rings GRP",
    "GE Baby Grand Illusion Spokes GRP",
    "GE MOAW Diamonds GRP",
    "GE MOAW Snowflake Spoke GRP",
    "GE MOAW Spokes GRP",
}

EFFECT_RE = re.compile(
    r'<Effect\b[^>]*\bstartTime="(\d+)"[^>]*\bendTime="(\d+)"[^>]*/>')
ELEMENT_RE = re.compile(r'<Element type="(\w+)" name="([^"]*)"')
NAME_RE = re.compile(r'\bname="([^"]*)"')

dry = "--dry-run" in sys.argv

with open(XSQ, encoding="utf-8") as f:
    lines = f.readlines()

out = []
in_effects_section = False
cur_type = cur_name = None
layer_idx = -1
deleted = defaultdict(list)
seen_targets = set()

for line in lines:
    stripped = line.strip()
    if stripped == "<ElementEffects>":
        in_effects_section = True
    elif stripped == "</ElementEffects>":
        in_effects_section = False
    elif in_effects_section:
        m = ELEMENT_RE.search(line)
        if m:
            cur_type, cur_name = m.group(1), m.group(2)
            layer_idx = -1
            if cur_type == "model" and cur_name in TARGETS:
                seen_targets.add(cur_name)
        elif "<EffectLayer" in line:
            layer_idx += 1
        elif cur_type == "model" and cur_name in TARGETS:
            em = EFFECT_RE.search(line)
            if em:
                start, end = int(em.group(1)), int(em.group(2))
                name = NAME_RE.search(line).group(1)
                deleted[(cur_name, layer_idx)].append((name, start, end))
                continue                      # drop the line
    out.append(line)

total = sum(len(v) for v in deleted.values())
print(f"{'DRY RUN — ' if dry else ''}deleting {total} effects "
      f"across {len(deleted)} element/layer rows:\n")
for (el, layer), effs in sorted(deleted.items()):
    names = defaultdict(int)
    for n, s, e in effs:
        names[n] += 1
    span = f"{min(s for _, s, _ in effs)}-{max(e for *_, e in effs)}"
    desc = ", ".join(f"{n}x{c}" if c > 1 else n for n, c in sorted(names.items()))
    print(f"  {el} L{layer}: {len(effs)} [{span}] ({desc})")

missing = TARGETS - seen_targets
if missing:
    print(f"\ntarget elements not found in sequence (ok if never sequenced): "
          f"{sorted(missing)}")

if not dry:
    with open(XSQ, "w", encoding="utf-8") as f:
        f.writelines(out)
    print(f"\nwrote {XSQ}")
