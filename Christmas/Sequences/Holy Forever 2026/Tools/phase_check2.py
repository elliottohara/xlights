"""Resolve beat phase independently of the assumed anchor.

1. Fold full-band + band flux at the beat period over V2->C3 (drums present).
2. Check stressed-syllable word onsets from words.json against both candidate
   grids (anchor 180 vs anchor 180+416.7).
"""
import json
import wave

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav'
WORDS = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/words.json'

BAR = 3333.0 + 1.0 / 3.0
BEAT = BAR / 4
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

logm = np.log1p(1000 * mag)
d = np.maximum(np.diff(logm, axis=0, prepend=logm[:1]), 0)
full = d.sum(axis=1)
kick = d[:, (freqs >= 40) & (freqs < 110)].sum(axis=1)

sel = (tms >= 94375) & (tms < 286700)
for name, env in (('full-band', full), ('kick-band', kick)):
    ph = (tms[sel] - 180.0) % BEAT
    w = env[sel]
    bins = 32
    hist = np.zeros(bins)
    for p, v in zip(ph, w):
        hist[int(p / BEAT * bins) % bins] += v
    hist /= hist.mean()
    peak = int(np.argmax(hist))
    print(f'{name}: flux-weighted phase within a beat (bin={BEAT/bins:.0f} ms), '
          f'peak at {peak * BEAT / bins:.0f}-{(peak+1) * BEAT / bins:.0f} ms')
    for i, v in enumerate(hist):
        tag = ''
        if i == 0:
            tag = ' <-- old-grid beat'
        if i == bins // 2:
            tag = ' <-- eighth later'
        print(f'  {i * BEAT / bins:6.0f}  {"#" * int(v * 12)}{tag}')
    print()

# vocal check: where do stressed word starts fall?
words = json.load(open(WORDS))
STRESSED = {'thousand', 'sing', 'song', 'name', 'holy', 'angels', 'creation',
            'lifted', 'king', 'thrones', 'powers', 'forever', 'lamb'}
offs_old, offs_new = [], []
for w in words:
    lw = w['w'].lower().strip('.,!?')
    if lw in STRESSED:
        t = w['s'] * 1000
        offs_old.append((t - 180.0) % BEAT)
        offs_new.append((t - 180.0 - BEAT / 2) % BEAT)


def spread(offs):
    a = np.array(offs) / BEAT * 2 * np.pi
    r = np.abs(np.exp(1j * a).mean())
    mean = (np.angle(np.exp(1j * a).mean()) % (2 * np.pi)) / (2 * np.pi) * BEAT
    return r, mean


for label, offs in (('old grid (180)', offs_old),
                    ('shifted grid (596.7)', offs_new)):
    r, mean = spread(offs)
    print(f'stressed words vs {label}: n={len(offs)}, concentration={r:.2f}, '
          f'mean offset={mean:.0f} ms after beat')
