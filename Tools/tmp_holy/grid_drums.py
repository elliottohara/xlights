"""Grid-slot drum analysis: per-16th-slot band flux across the verified grid.

For every bar and 16th slot, take the max band-limited flux within +/-45 ms of
the slot time. Prints a per-section heatmap (mean slot strength) so the actual
kick/snare pattern per section is readable, and writes grid_flux.json with the
full per-slot matrix for mark generation.

Run: Tools/tmp_holy/.venv/bin/python Tools/tmp_holy/grid_drums.py
"""
import json
import wave

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Tools/tmp_holy/holy_44k.wav'
OUT = '/Users/elliott.ohara/xlights/Tools/tmp_holy/grid_flux.json'

ANCHOR = 180.0
BAR = 3333.0 + 1.0 / 3.0
SIXT = BAR / 16
N_FFT = 2048
HOP = 256
TOL = 45.0  # ms around slot

SECTIONS = [
    ('INTRO', 0, 15275), ('V1', 15275, 40950), ('PC1', 40950, 66700),
    ('C1', 66700, 94375), ('V2', 94375, 126725), ('C2a', 126725, 153250),
    ('C2b', 153250, 166850), ('C2c', 166850, 181450),
    ('PC2a', 181450, 207775), ('PC2b', 207775, 233350),
    ('C3a', 233350, 259850), ('C3b', 259850, 273650), ('C3c', 273650, 286700),
    ('OUT', 286700, 301500), ('TAIL', 301500, 308314),
]


def load():
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return x.astype(np.float64) / 32768.0, sr


def stft_mag(x, sr):
    win = np.hanning(N_FFT)
    n = 1 + (len(x) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    mag = np.abs(np.fft.rfft(x[idx] * win, axis=1))
    freqs = np.fft.rfftfreq(N_FFT, 1 / sr)
    tms = (np.arange(n) * HOP + N_FFT / 2) / sr * 1000.0
    return mag, freqs, tms


def band_flux(mag, freqs, lo, hi):
    sel = (freqs >= lo) & (freqs < hi)
    logm = np.log1p(1000 * mag[:, sel])
    d = np.diff(logm, axis=0, prepend=logm[:1])
    return np.maximum(d, 0).sum(axis=1)


def slot_matrix(env, tms, n_bars):
    """(bar, slot) -> max env within TOL of the slot, normalized per-band."""
    hop_ms = tms[1] - tms[0]
    w = int(TOL / hop_ms)
    med = np.median(env[env > 0]) + 1e-9
    m = np.zeros((n_bars, 16))
    t_at = np.zeros((n_bars, 16))
    for b in range(n_bars):
        for s in range(16):
            t = ANCHOR + b * BAR + s * SIXT
            i = int(round((t - tms[0]) / hop_ms))
            a, z = max(0, i - w), min(len(env), i + w + 1)
            if a >= z:
                continue
            j = a + int(np.argmax(env[a:z]))
            m[b, s] = env[j] / med
            t_at[b, s] = tms[j]
    return m, t_at


def main():
    x, sr = load()
    mag, freqs, tms = stft_mag(x, sr)
    n_bars = int((tms[-1] - ANCHOR) / BAR) + 1

    bands = {
        'kick': band_flux(mag, freqs, 40, 110),
        'snare': band_flux(mag, freqs, 2000, 7500),
        'crash': band_flux(mag, freqs, 8000, 16000),
    }
    out = {'anchor': ANCHOR, 'bar': BAR, 'n_bars': n_bars}
    for name, env in bands.items():
        m, t_at = slot_matrix(env, tms, n_bars)
        out[name] = {'m': np.round(m, 2).tolist(),
                     't': np.round(t_at, 1).tolist()}
        print(f'== {name}: per-section mean slot strength '
              f'(slots 0..15, beat = 0/4/8/12) ==')
        hdr = '   '.join(f'{s:>4}' for s in range(16))
        print(f'  {"sec":6} {hdr}')
        for sec, a, b in SECTIONS:
            b0 = max(0, int(np.ceil((a - ANCHOR) / BAR)))
            b1 = min(n_bars, int(np.ceil((b - ANCHOR) / BAR)))
            if b1 <= b0:
                continue
            mean = m[b0:b1].mean(axis=0)
            row = '  '.join(f'{v:5.1f}' for v in mean)
            print(f'  {sec:6} {row}')
        print()

    with open(OUT, 'w') as f:
        json.dump(out, f)
    print(f'WROTE {OUT}')


if __name__ == '__main__':
    main()
