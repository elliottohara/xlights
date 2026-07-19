"""Verify beat phase: histogram strong kick/snare onsets against the bar.

If the strongest snares sit ~1250 ms into each half-bar (slots 6/14 of the
180-anchored grid) the true downbeat is anchor+416.7 ms, not 180 ms.
"""
import json

import numpy as np

D = json.load(open('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/drums.json'))
ANCHOR = 180.0
BAR = 3333.0 + 1.0 / 3.0
HALF = BAR / 2

for name, lo_t, str_min in (('snare', 94000, 1.4), ('kick', 94000, 1.3)):
    hits = [r for r in D[name] if r['t'] >= lo_t and r['t'] < 300000
            and r['str'] >= str_min]
    ph = np.array([(r['t'] - ANCHOR) % HALF for r in hits])
    hist, edges = np.histogram(ph, bins=16, range=(0, HALF))
    print(f'{name}: {len(hits)} strong hits, phase-in-half-bar histogram '
          f'(bin={HALF/16:.0f} ms):')
    for i, c in enumerate(hist):
        mark = ' <-- beat (old grid)' if i in (0, 8) else ''
        mark = ' <-- slot 6/14 (8th later)' if i == 12 else mark
        print(f'  {edges[i]:6.0f}-{edges[i+1]:6.0f}  {"#" * c}{mark}')
    # weighted circular mean around the dominant bin
    print(f'  median phase: {np.median(ph):.0f} ms '
          f'(beat2/4 old grid = 833, 8th later = 1250)')
    print()

# strongest 20 snares with absolute times and slot positions
SIXT = BAR / 16
print('top snares:')
for r in sorted(D['snare'], key=lambda r: -r['str'])[:20]:
    s = (r['t'] - ANCHOR) / SIXT
    print(f"  t={r['t']:8.1f}  str={r['str']:.2f}  slot={s % 16:5.2f}")
