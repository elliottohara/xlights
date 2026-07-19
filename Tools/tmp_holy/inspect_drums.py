"""Inspect drum detections: per-section density and 16th-grid alignment."""
import json

import numpy as np

D = json.load(open('/Users/elliott.ohara/xlights/Tools/tmp_holy/drums.json'))

ANCHOR = 180.0
BAR = 3333.0 + 1.0 / 3.0
SIXT = BAR / 16

SECTIONS = [
    ('INTRO', 0, 15275), ('V1', 15275, 40950), ('PC1', 40950, 66700),
    ('C1', 66700, 94375), ('V2', 94375, 126725), ('C2a', 126725, 153250),
    ('C2b', 153250, 166850), ('C2c', 166850, 181450),
    ('PC2a', 181450, 207775), ('PC2b', 207775, 233350),
    ('C3a', 233350, 259850), ('C3b', 259850, 273650), ('C3c', 273650, 286700),
    ('OUT', 286700, 301500), ('TAIL', 301500, 308314),
]


def sixt_pos(t):
    s = (t - ANCHOR) / SIXT
    near = round(s)
    off = t - (ANCHOR + near * SIXT)
    return int(near % 16), off  # 0 = downbeat, 4 = beat2, 8 = beat3, 12 = beat4


for name in ('kick', 'snare', 'crash'):
    rows = D[name]
    print(f'== {name} ({len(rows)} raw) ==')
    for sec, a, b in SECTIONS:
        hits = [r for r in rows if a <= r['t'] < b]
        if not hits:
            print(f'  {sec:6} none')
            continue
        strs = np.array([r['str'] for r in hits])
        aligned = [r for r in hits if abs(sixt_pos(r['t'])[1]) < 55]
        pos = {}
        for r in aligned:
            p = sixt_pos(r['t'])[0]
            pos[p] = pos.get(p, 0) + 1
        dur_bars = (b - a) / BAR
        print(f'  {sec:6} {len(hits):4} hits ({len(hits)/dur_bars:4.1f}/bar) '
              f'str med={np.median(strs):4.2f} max={strs.max():5.2f} '
              f'| 16th-aligned {len(aligned):4} pos={dict(sorted(pos.items()))}')
    print()

# strength distribution for choosing thresholds
for name in ('kick', 'snare', 'crash'):
    strs = sorted(r['str'] for r in D[name])
    q = lambda p: strs[int(p * (len(strs) - 1))]
    print(f'{name}: str quartiles {q(0):.2f}/{q(.25):.2f}/{q(.5):.2f}/'
          f'{q(.75):.2f}/{q(1):.2f}')
