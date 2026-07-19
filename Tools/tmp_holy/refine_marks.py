"""Refine gated drum marks: crash decay test + eyeball listing of early hits.

Real crashes ring: high-band (8-16 kHz) energy stays elevated for >0.5 s.
Vocal sibilance / strums die in <200 ms. Keeps a crash only if the mean
high-band energy 250-1000 ms after the hit is at least 25% of the energy in
the first 120 ms.

Writes marks_refined.json.
"""
import json
import wave

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Tools/tmp_holy/holy_44k.wav'
IN = '/Users/elliott.ohara/xlights/Tools/tmp_holy/marks.json'
OUT = '/Users/elliott.ohara/xlights/Tools/tmp_holy/marks_refined.json'

N_FFT = 2048
HOP = 256


def load():
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return x.astype(np.float64) / 32768.0, sr


x, sr = load()
win = np.hanning(N_FFT)
n = 1 + (len(x) - N_FFT) // HOP
idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
mag = np.abs(np.fft.rfft(x[idx] * win, axis=1))
freqs = np.fft.rfftfreq(N_FFT, 1 / sr)
tms = (np.arange(n) * HOP + N_FFT / 2) / sr * 1000.0
hop_ms = tms[1] - tms[0]

high = (mag[:, (freqs >= 8000) & (freqs < 16000)] ** 2).sum(axis=1)
lowb = (mag[:, (freqs >= 40) & (freqs < 110)] ** 2).sum(axis=1)

M = json.load(open(IN))
marks = M['marks']


def seg_mean(env, t0, t1):
    a = max(0, int((t0 - tms[0]) / hop_ms))
    b = min(len(env), int((t1 - tms[0]) / hop_ms))
    return env[a:b].mean() if b > a else 0.0


print('== crash decay test ==')
kept_crash = []
for t, v, sec, s in marks['crash']:
    attack = seg_mean(high, t, t + 120)
    ring = seg_mean(high, t + 250, t + 1000)
    before = seg_mean(high, t - 400, t - 80)
    ratio = ring / (attack + 1e-12)
    ring_gain = ring / (before + 1e-12)
    keep = ratio >= 0.25 and ring_gain >= 1.1 and v >= 3.5
    kept_crash.append((t, v, sec, s)) if keep else None
    print(f'  t={t:7} {sec:5} slot={s:2} str={v:5.2f} ring/attack={ratio:5.2f} '
          f'ring/before={ring_gain:5.2f} {"KEEP" if keep else "drop"}')

print(f'crash: {len(kept_crash)} of {len(marks["crash"])} kept')

print()
print('== kick pre-V2 listing (sustain test: low band should thump) ==')
kept_kick = []
for t, v, sec, s in marks['kick']:
    if sec in ('V1', 'PC1', 'C1'):
        attack = seg_mean(lowb, t, t + 100)
        before = seg_mean(lowb, t - 300, t - 60)
        gain = attack / (before + 1e-12)
        keep = gain >= 1.6
        print(f'  t={t:7} {sec:5} slot={s:2} str={v:5.2f} low gain={gain:5.2f} '
              f'{"KEEP" if keep else "drop"}')
        if keep:
            kept_kick.append((t, v, sec, s))
    else:
        kept_kick.append((t, v, sec, s))
print(f'kick: {len(kept_kick)} of {len(marks["kick"])} kept')

print()
print('== snare pre-V2 listing ==')
kept_snare = []
for t, v, sec, s in marks['snare']:
    if sec in ('V1', 'PC1', 'C1'):
        print(f'  t={t:7} {sec:5} slot={s:2} str={v:5.2f}')
    kept_snare.append((t, v, sec, s))

# regularity: how contiguous is the backbeat per section?
print()
print('== snare backbeat coverage per section ==')
BAR = M['bar_ms']
SEC = {'V1': (15275, 40950), 'PC1': (40950, 66700), 'C1': (66700, 94375),
       'V2': (94375, 126725), 'C2a': (126725, 153250), 'C2b': (153250, 166850),
       'C2c': (166850, 181450), 'PC2a': (181450, 207775),
       'PC2b': (207775, 233350), 'C3a': (233350, 259850),
       'C3b': (259850, 273650), 'C3c': (273650, 286700), 'OUT': (286700, 301500)}
for sec, (a, b) in SEC.items():
    nbars = (b - a) / BAR
    cnt = sum(1 for t, v, sc, s in kept_snare if sc == sec and s in (4, 12))
    print(f'  {sec:5} {cnt:3} backbeats over {nbars:4.1f} bars '
          f'({cnt / (2 * nbars) * 100:3.0f}% coverage)')

json.dump({'anchor': M['anchor'], 'bar_ms': BAR,
           'kick': kept_kick, 'snare': kept_snare, 'crash': kept_crash,
           'bars': M['bars']}, open(OUT, 'w'))
print(f'WROTE {OUT}')
