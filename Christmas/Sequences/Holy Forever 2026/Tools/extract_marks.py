"""Extract kick/snare/crash timing marks on the audio-true grid.

The sequence's documented grid (anchor 180) is half a beat EARLY vs the audio:
strong snares fold at +~400 ms. Here we (1) fit the anchor precisely by
maximizing backbeat snare flux, (2) gate per-16th-slot band flux into hit
marks, (3) dump per-bar RMS for the mood track.

Writes marks.json. Run:
Christmas/Sequences/Holy Forever 2026/Tools/.venv/bin/python Christmas/Sequences/Holy Forever 2026/Tools/extract_marks.py
"""
import json
import wave

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav'
OUT = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/marks.json'

BAR = 3333.0 + 1.0 / 3.0
BEAT = BAR / 4
SIXT = BAR / 16
N_FFT = 2048
HOP = 256
FRAME = 25

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


def snap(t):
    return int(round(t / FRAME) * FRAME)


def main():
    x, sr = load()
    win = np.hanning(N_FFT)
    n = 1 + (len(x) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    mag = np.abs(np.fft.rfft(x[idx] * win, axis=1))
    freqs = np.fft.rfftfreq(N_FFT, 1 / sr)
    tms = (np.arange(n) * HOP + N_FFT / 2) / sr * 1000.0
    hop_ms = tms[1] - tms[0]

    logm = np.log1p(1000 * mag)
    d = np.maximum(np.diff(logm, axis=0, prepend=logm[:1]), 0)

    def flux(lo, hi):
        return d[:, (freqs >= lo) & (freqs < hi)].sum(axis=1)

    kick_env = flux(40, 110)
    snare_env = flux(2000, 7500) + 0.5 * flux(160, 400)
    crash_env = flux(8000, 16000)

    # ---- fit anchor: maximize snare flux at beats 2/4 over V2..C3c ----
    sel = (tms >= 94375) & (tms < 286700)
    best = None
    for a in np.arange(480, 700, 5):
        beats = []
        t = a + BEAT
        while t < 286700:
            if t >= 94375:
                beats.append(t)
            t += BEAT * 2  # beats 2 and 4 given downbeat at a
        score = 0.0
        for bt in beats:
            i = int(round((bt - tms[0]) / hop_ms))
            w = int(40 / hop_ms)
            score += snare_env[max(0, i - w):i + w + 1].max()
        if best is None or score > best[1]:
            best = (a, score)
    anchor = float(best[0])
    print(f'fitted anchor = {anchor} ms (snare backbeat score {best[1]:.0f})')

    # ---- per-slot matrices on the true grid ----
    n_bars = int((tms[-1] - anchor) / BAR) + 1
    tol = int(45 / hop_ms)

    def slots(env):
        med = np.median(env[env > 0]) + 1e-9
        m = np.zeros((n_bars, 16))
        tt = np.zeros((n_bars, 16))
        for b in range(n_bars):
            for s in range(16):
                t = anchor + b * BAR + s * SIXT
                i = int(round((t - tms[0]) / hop_ms))
                a, z = max(0, i - tol), min(len(env), i + tol + 1)
                if a >= z:
                    continue
                j = a + int(np.argmax(env[a:z]))
                m[b, s] = env[j] / med
                tt[b, s] = tms[j]
        return m, tt

    km, ktt = slots(kick_env)
    sm, stt = slots(snare_env)
    cm, ctt = slots(crash_env)

    def sec_of(t):
        for name, a, b in SECTIONS:
            if a <= t < b:
                return name
        return 'TAIL'

    # ---- gates ----
    # snare: backbeat slots 4/12 with modest threshold; other slots only if
    # very strong (fills). kick: 8th slots (even) with strong threshold,
    # 16ths only if very strong. crash: quarter slots, high threshold.
    marks = {'kick': [], 'snare': [], 'crash': []}
    for b in range(n_bars):
        for s in range(16):
            t_grid = anchor + b * BAR + s * SIXT
            sec = sec_of(t_grid)
            if sec in ('INTRO', 'TAIL'):
                continue
            # snare
            v = sm[b, s]
            if (s in (4, 12) and v >= 2.2) or (s not in (4, 12) and v >= 4.5):
                marks['snare'].append((snap(t_grid), round(v, 2), sec, s))
            # kick
            v = km[b, s]
            if (s % 2 == 0 and v >= 6.0) or (s % 2 == 1 and v >= 9.0):
                marks['kick'].append((snap(t_grid), round(v, 2), sec, s))
            # crash
            v = cm[b, s]
            if s % 4 == 0 and v >= 3.5:
                marks['crash'].append((snap(t_grid), round(v, 2), sec, s))

    for name in marks:
        rows = marks[name]
        print(f'== {name}: {len(rows)} marks ==')
        per = {}
        slots_used = {}
        for t, v, sec, s in rows:
            per[sec] = per.get(sec, 0) + 1
            slots_used[s] = slots_used.get(s, 0) + 1
        print('  per section:', {k: per.get(k, 0) for k, _, _ in SECTIONS
                                 if per.get(k)})
        print('  per slot:', dict(sorted(slots_used.items())))

    # ---- per-bar energies (for mood) ----
    def band_e(lo, hi):
        s = (freqs >= lo) & (freqs < hi)
        return (mag[:, s] ** 2).sum(axis=1)

    total, low, high = band_e(30, 16000), band_e(30, 150), band_e(4000, 12000)
    bars = []
    for b in range(n_bars):
        t0 = anchor + b * BAR
        s = (tms >= t0) & (tms < t0 + BAR)
        if s.any():
            bars.append({'bar': b, 't': round(t0, 1),
                         'rms': round(10 * np.log10(total[s].mean() + 1e-12), 1),
                         'low': round(10 * np.log10(low[s].mean() + 1e-12), 1),
                         'high': round(10 * np.log10(high[s].mean() + 1e-12), 1)})
    print('== per-bar energy ==')
    for r in bars:
        blip = '#' * max(0, int((r['rms'] + 5) / 2))
        print(f"  bar {r['bar']:3} t={r['t']:8.0f} rms={r['rms']:6.1f} "
              f"low={r['low']:6.1f} high={r['high']:6.1f} {blip}")

    with open(OUT, 'w') as f:
        json.dump({'anchor': anchor, 'bar_ms': BAR, 'marks': marks,
                   'bars': bars}, f)
    print(f'WROTE {OUT}')


if __name__ == '__main__':
    main()
