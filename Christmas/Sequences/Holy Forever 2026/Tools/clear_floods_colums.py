"""Delete ALL effects on Floods GRP and Colums (Holy Forever 2026).
User request 2026-07-13, follow-up to clear_yard_props.py.

Direct .xsq edit (API cannot delete effects); one <Effect .../> per line.
Run with --dry-run first. Pattern: saveSequence -> cp backup -> run ->
closeSequence + openSequence via the API.
"""
import re
import sys
from collections import defaultdict

XSQ = "/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq"

TARGETS = {"Floods GRP", "Colums"}

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
is_target = False
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
            is_target = cur_type == "model" and cur_name.strip() in TARGETS
            if is_target:
                seen_targets.add(cur_name.strip())
        elif "<EffectLayer" in line:
            layer_idx += 1
        elif is_target:
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
    print(f"\ntarget elements not found in sequence: {sorted(missing)}")

if not dry:
    with open(XSQ, "w", encoding="utf-8") as f:
        f.writelines(out)
    print(f"\nwrote {XSQ}")
