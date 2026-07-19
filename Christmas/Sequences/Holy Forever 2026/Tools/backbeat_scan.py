"""Bar-by-bar backbeat/kick strength on the true grid (anchor 600).

For each bar: snare flux at slots 4/12 vs the bar's off-backbeat median, and
kick flux at slots 0/8. Prints one row per bar so groove presence per section
is directly readable.
"""
import wave

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav'
ANCHOR = 600.0
BAR = 3333.0 + 1.0 / 3.0
SIXT = BAR / 16
N_FFT = 2048
HOP = 256

SECTIONS = [
    ('INTRO', 0, 15275), ('V1', 15275, 40950), ('PC1', 40950, 66700),
    ('C1', 66700, 94375), ('V2', 94375, 126725), ('C2a', 126725, 153250),
    ('C2b', 153250, 166850), ('C2c', 166850, 181450),
    ('PC2a', 181450, 207775), ('PC2b', 207775, 233350),
    ('C3a', 233350, 259850), ('C3b', 259850, 273650), ('C3c', 273650, 286700),
    ('OUT', 286700, 301500), ('TAIL', 301500, 308314),
]


def sec_of(t):
    for name, a, b in SECTIONS:
        if a <= t < b:
            return name
    return 'TAIL'


with wave.open(AUDIO) as w:
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
x = x.astype(np.float64) / 32768.0

win = np.hanning(N_FFT)
n = 1 + (len(x) - N_FFT) // HOP
idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
mag = np.abs(np.fft.rfft(x[idx] * win, axis=1))
freqs = np.fft.rfftfreq(N_FFT, 1 / sr)
tms = (np.arange(n) * HOP + N_FFT / 2) / sr * 1000.0
hop_ms = tms[1] - tms[0]

logm = np.log1p(1000 * mag)
d = np.maximum(np.diff(logm, axis=0, prepend=logm[:1]), 0)
snare = d[:, (freqs >= 2000) & (freqs < 7500)].sum(axis=1)
kick = d[:, (freqs >= 40) & (freqs < 110)].sum(axis=1)

n_bars = int((tms[-1] - ANCHOR) / BAR) + 1
tol = int(45 / hop_ms)


def slot(env, b, s):
    t = ANCHOR + b * BAR + s * SIXT
    i = int(round((t - tms[0]) / hop_ms))
    a, z = max(0, i - tol), min(len(env), i + tol + 1)
    return env[a:z].max() if z > a else 0.0


print(f'{"bar":>3} {"t":>7} {"sec":6} | snare: b2, b4 / offmed | kick: b1, b3 / offmed')
for b in range(n_bars):
    t0 = ANCHOR + b * BAR
    sec = sec_of(t0 + BAR / 2)
    s_off = np.median([slot(snare, b, s) for s in range(16)
                       if s not in (4, 12)]) + 1e-9
    k_off = np.median([slot(kick, b, s) for s in range(16)
                       if s not in (0, 8)]) + 1e-9
    s2, s4 = slot(snare, b, 4) / s_off, slot(snare, b, 12) / s_off
    k1, k3 = slot(kick, b, 0) / k_off, slot(kick, b, 8) / k_off
    def tag(v, hi=1.8, mid=1.3):
        return '**' if v >= hi else ('* ' if v >= mid else '  ')
    print(f'{b:3} {t0:7.0f} {sec:6} |  {s2:5.2f}{tag(s2)} {s4:5.2f}{tag(s4)} '
          f'|  {k1:5.2f}{tag(k1)} {k3:5.2f}{tag(k3)}')
