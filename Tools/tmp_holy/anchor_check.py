"""Sanity-check the corrected downbeat anchor (596.7 ms) at section starts.

Prints strong crash/kick events near each section boundary and their distance
to the nearest candidate downbeat on both grids, plus per-bar energy around
key transitions (drum entry, C3b drop).
"""
import json

import numpy as np

D = json.load(open('/Users/elliott.ohara/xlights/Tools/tmp_holy/drums.json'))
BAR = 3333.0 + 1.0 / 3.0

SECTION_STARTS = [
    ('V1', 15275), ('PC1', 40950), ('C1', 66700), ('V2', 94375),
    ('C2a', 126725), ('C2b', 153250), ('C2c', 166850), ('PC2a', 181450),
    ('PC2b', 207775), ('C3a', 233350), ('C3b', 259850), ('C3c', 273650),
    ('OUT', 286700), ('HOLD', 301500),
]


def near_db(t, anchor):
    n = round((t - anchor) / BAR)
    return t - (anchor + n * BAR)


print('strong crashes near section starts (within +/-2500 ms):')
for name, s in SECTION_STARTS:
    ev = [r for r in D['crash'] if abs(r['t'] - s) < 2500 and r['str'] > 1.3]
    ev.sort(key=lambda r: -r['str'])
    for r in ev[:3]:
        print(f"  {name:5} start={s:6}  crash t={r['t']:8.1f} str={r['str']:.2f} "
              f"d180={near_db(r['t'], 180):+7.1f}  d596={near_db(r['t'], 596.667):+7.1f}")
    if not ev:
        print(f'  {name:5} start={s:6}  (none)')

print()
print('per-bar energy (rms/low/high dB) around transitions:')
bars = D['bars']
for label, lo, hi in (('drum entry V1->C1', 12000, 72000),
                      ('C2b feature', 150000, 170000),
                      ('C3b drop', 255000, 278000),
                      ('outro fade', 283000, 308314)):
    print(f'  -- {label} --')
    for b in bars:
        if lo <= b['t'] < hi:
            print(f"    bar {b['bar']:3} t={b['t']:8.1f}  rms={b['rms_db']:6.1f} "
                  f"low={b['low_db']:6.1f} high={b['high_db']:6.1f}")
