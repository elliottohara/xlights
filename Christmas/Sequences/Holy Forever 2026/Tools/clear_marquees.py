"""Delete ALL Marquee effects from Holy Forever 2026.

The xLights API cannot delete effects, so this edits the .xsq directly
(line-oriented; one self-closing <Effect .../> per line). Timing elements
and every non-Marquee model effect are untouched. Orphaned EffectDB /
ColorPalettes entries are left alone (harmless on reload).

Run with --dry-run first to list what goes. Pattern per AGENT NOTES:
saveSequence -> cp backup -> run this -> closeSequence + openSequence via
the API so the live session matches disk.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

XSQ = Path(__file__).resolve().parents[1] / "Holy Forever 2026.xsq"

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
kept = 0

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
        elif "<EffectLayer" in line:
            layer_idx += 1
        elif cur_type == "model":
            em = EFFECT_RE.search(line)
            if em:
                name = NAME_RE.search(line).group(1)
                if name == "Marquee":
                    start, end = int(em.group(1)), int(em.group(2))
                    deleted[(cur_name, layer_idx)].append((name, start, end))
                    continue
                kept += 1
    out.append(line)

total = sum(len(v) for v in deleted.values())
print(f"{'DRY RUN — ' if dry else ''}deleting {total} Marquee effects "
      f"across {len(deleted)} element/layer rows:\n")
for (el, layer), effs in sorted(deleted.items()):
    span = f"{min(s for _, s, _ in effs)}-{max(e for *_, e in effs)}"
    print(f"  {el} L{layer}: {len(effs)} [{span}]")
print(f"\nnon-Marquee model effects kept: {kept}")

if not dry:
    with open(XSQ, "w", encoding="utf-8") as f:
        f.writelines(out)
    print(f"\nwrote {XSQ}")
