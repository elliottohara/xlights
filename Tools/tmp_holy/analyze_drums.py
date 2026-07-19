"""Band-limited percussion + energy analysis of Holy Forever (numpy-only).

Detects kick / snare / crash onsets via per-band spectral flux and writes
`drums.json` (onset times in ms, plus per-bar band energies for mood work).

Grid (verified in the sequence notes): 72.0 BPM, 4/4, bar 3333.333 ms,
anchor 180 ms, frames 25 ms.

Run: Tools/tmp_holy/.venv/bin/python Tools/tmp_holy/analyze_drums.py
"""
import json
import wave

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Tools/tmp_holy/holy_44k.wav'
OUT = '/Users/elliott.ohara/xlights/Tools/tmp_holy/drums.json'

FRAME_MS = 25
ANCHOR = 180.0
BAR = 3333.0 + 1.0 / 3.0
BEAT = BAR / 4

N_FFT = 2048
HOP = 256


def load():
    with wave.open(AUDIO) as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return x.astype(np.float64) / 32768.0, sr


def stft_mag(x, sr):
    win = np.hanning(N_FFT)
    n = 1 + (len(x) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    frames = x[idx] * win
    mag = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(N_FFT, 1 / sr)
    times_ms = (np.arange(n) * HOP + N_FFT / 2) / sr * 1000.0
    return mag, freqs, times_ms


def band_flux(mag, freqs, lo, hi):
    """Half-wave rectified log spectral flux inside [lo, hi] Hz."""
    sel = (freqs >= lo) & (freqs < hi)
    logm = np.log1p(1000 * mag[:, sel])
    d = np.diff(logm, axis=0, prepend=logm[:1])
    return np.maximum(d, 0).sum(axis=1)


def band_energy(mag, freqs, lo, hi):
    sel = (freqs >= lo) & (freqs < hi)
    return (mag[:, sel] ** 2).sum(axis=1)


def pick_peaks(env, times_ms, min_sep_ms, k, win_ms=1500):
    """Local maxima above rolling median + k*MAD, with minimum separation."""
    hop_ms = times_ms[1] - times_ms[0]
    w = max(3, int(win_ms / hop_ms))
    n = len(env)
    thr = np.empty(n)
    for i in range(n):
        a, b = max(0, i - w), min(n, i + w)
        seg = env[a:b]
        med = np.median(seg)
        mad = np.median(np.abs(seg - med)) + 1e-9
        thr[i] = med + k * mad
    cand = [i for i in range(1, n - 1)
            if env[i] > thr[i] and env[i] >= env[i - 1] and env[i] >= env[i + 1]]
    cand.sort(key=lambda i: -env[i])
    taken, out = [], []
    min_sep = min_sep_ms
    for i in cand:
        t = times_ms[i]
        if all(abs(t - times_ms[j]) >= min_sep for j in taken):
            taken.append(i)
            out.append((t, float(env[i] / (thr[i] + 1e-9))))
    out.sort()
    return out


def grid_dist(t):
    """Distance (ms) to nearest beat, and beat position 1-4 of the nearest."""
    b = (t - ANCHOR) / BEAT
    near = round(b)
    return t - (ANCHOR + near * BEAT), int(near % 4) + 1


def main():
    x, sr = load()
    mag, freqs, tms = stft_mag(x, sr)
    print(f'{len(x)/sr:.1f}s @ {sr} Hz, {mag.shape[0]} STFT frames '
          f'({tms[1]-tms[0]:.2f} ms hop)')

    kick_env = band_flux(mag, freqs, 40, 110)
    snare_env = band_flux(mag, freqs, 2000, 7500) + \
        0.5 * band_flux(mag, freqs, 160, 400)
    crash_env = band_flux(mag, freqs, 7500, 15000)

    kick = pick_peaks(kick_env, tms, min_sep_ms=180, k=6)
    snare = pick_peaks(snare_env, tms, min_sep_ms=180, k=6)
    crash = pick_peaks(crash_env, tms, min_sep_ms=350, k=7)

    report = {}
    for name, hits in (('kick', kick), ('snare', snare), ('crash', crash)):
        rows = []
        for t, strength in hits:
            d, pos = grid_dist(t)
            rows.append({'t': round(t, 1), 'str': round(strength, 2),
                         'grid_off': round(d, 1), 'beat_pos': pos})
        report[name] = rows
        offs = np.array([r['grid_off'] for r in rows])
        on_grid = int((np.abs(offs) < 70).sum()) if len(offs) else 0
        print(f'{name}: {len(rows)} hits, {on_grid} within 70ms of a beat')
        pos_counts = {p: sum(1 for r in rows if r['beat_pos'] == p and
                             abs(r['grid_off']) < 70) for p in (1, 2, 3, 4)}
        print(f'  on-grid beat positions: {pos_counts}')

    # per-bar energies for mood analysis
    total = band_energy(mag, freqs, 30, 16000)
    low = band_energy(mag, freqs, 30, 150)
    mid = band_energy(mag, freqs, 250, 2000)
    high = band_energy(mag, freqs, 4000, 12000)
    bars = []
    t0 = ANCHOR
    bar_no = 0
    while t0 < tms[-1]:
        sel = (tms >= t0) & (tms < t0 + BAR)
        if sel.any():
            bars.append({
                'bar': bar_no, 't': round(t0, 1),
                'rms_db': round(10 * np.log10(total[sel].mean() + 1e-12), 1),
                'low_db': round(10 * np.log10(low[sel].mean() + 1e-12), 1),
                'mid_db': round(10 * np.log10(mid[sel].mean() + 1e-12), 1),
                'high_db': round(10 * np.log10(high[sel].mean() + 1e-12), 1),
            })
        t0 += BAR
        bar_no += 1
    report['bars'] = bars

    with open(OUT, 'w') as f:
        json.dump(report, f)
    print(f'WROTE {OUT}')


if __name__ == '__main__':
    main()
