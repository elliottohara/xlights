"""Delete all model effects before the lead vocal entrance (Holy Forever 2026).

The xLights API cannot delete effects, so this edits the .xsq directly
(line-oriented; .xsq effect rows are one self-closing <Effect .../> per line).
Timing elements are untouched. Run with --dry-run first to list what goes.

Cutoff: effects with endTime <= CUTOFF_END are deleted. Effects that straddle
the boundary (start < CUTOFF_END < end) are reported but kept, except faces
which start at the vocal pickup (15275) and are explicitly protected anyway.
"""
import re
import sys
from collections import defaultdict

XSQ = "/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq"
CUTOFF_END = 15520          # section boundary; V1 vocal pickup is 15275
VOCAL_START = 15275

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
straddlers = []
kept_after = 0

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
                start, end = int(em.group(1)), int(em.group(2))
                name = NAME_RE.search(line).group(1)
                if end <= CUTOFF_END:
                    deleted[(cur_name, layer_idx)].append((name, start, end))
                    continue                      # drop the line
                if start < VOCAL_START:
                    straddlers.append((cur_name, layer_idx, name, start, end))
                else:
                    kept_after += 1
    out.append(line)

total = sum(len(v) for v in deleted.values())
print(f"{'DRY RUN — ' if dry else ''}deleting {total} effects "
      f"(endTime <= {CUTOFF_END}) across {len(deleted)} element/layer rows:\n")
for (el, layer), effs in sorted(deleted.items()):
    names = defaultdict(int)
    for n, s, e in effs:
        names[n] += 1
    span = f"{min(s for _, s, _ in effs)}-{max(e for *_, e in effs)}"
    desc = ", ".join(f"{n}x{c}" if c > 1 else n for n, c in sorted(names.items()))
    print(f"  {el} L{layer}: {len(effs)} [{span}] ({desc})")

print(f"\nstraddlers kept (start < {VOCAL_START} < end):")
for el, layer, name, s, e in straddlers:
    print(f"  {el} L{layer}: {name} {s}-{e}")
print(f"\nmodel effects kept at/after vocal start: {kept_after}")

if not dry:
    with open(XSQ, "w", encoding="utf-8") as f:
        f.writelines(out)
    print(f"\nwrote {XSQ}")
