"""Final kick/snare/crash mark extraction for Holy Forever timing tracks.

Grid: 72 BPM, bar 3333.33 ms, TRUE downbeat anchor 600 ms (fitted to the
audio; the sequence's documented 180 ms anchor is half a beat early —
verified by backbeat folding and section-start crashes).

Method per band:
- per-16th-slot max flux within +/-45 ms (band-limited log spectral flux)
- per-bar relative gate (slot vs that bar's median slot flux) AND absolute
  gate (slot vs song-median flux)
- spectral template match: candidate hit spectra must correlate with the
  mean spectrum of reference hits (strong V2/C2a backbeats for snare,
  strong V2 downbeat kicks for kick) — kills vocal/guitar false positives
  in the sparse early sections
- crash keeps its ring test (high band stays elevated 250-1000 ms out)

Writes drum_marks.json {kick|snare|crash: [ms,...], mood bars}.
Run: Tools/tmp_holy/.venv/bin/python Tools/tmp_holy/build_drum_marks.py
"""
import json
import wave

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Tools/tmp_holy/holy_44k.wav'
OUT = '/Users/elliott.ohara/xlights/Tools/tmp_holy/drum_marks.json'

ANCHOR = 600.0
BAR = 3333.0 + 1.0 / 3.0
SIXT = BAR / 16
N_FFT = 2048
HOP = 256
FRAME = 25
TOL_MS = 45.0

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


def snap(t):
    return int(round(t / FRAME) * FRAME)


def load():
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return x.astype(np.float64) / 32768.0, sr


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
    dflux = np.maximum(np.diff(logm, axis=0, prepend=logm[:1]), 0)

    def bflux(lo, hi):
        return dflux[:, (freqs >= lo) & (freqs < hi)].sum(axis=1)

    envs = {
        'kick': bflux(40, 110),
        'snare': bflux(2000, 7500) + 0.5 * bflux(160, 400),
        'crash': bflux(8000, 16000),
    }
    high_e = (mag[:, (freqs >= 8000) & (freqs < 16000)] ** 2).sum(axis=1)

    n_bars = int((tms[-1] - ANCHOR) / BAR) + 1
    tol = int(TOL_MS / hop_ms)

    def slot_scan(env):
        """(bar, slot) -> (value, frame index of the peak)"""
        m = np.zeros((n_bars, 16))
        ji = np.zeros((n_bars, 16), dtype=int)
        for b in range(n_bars):
            for s in range(16):
                t = ANCHOR + b * BAR + s * SIXT
                i = int(round((t - tms[0]) / hop_ms))
                a, z = max(0, i - tol), min(len(env), i + tol + 1)
                if a >= z:
                    continue
                j = a + int(np.argmax(env[a:z]))
                m[b, s] = env[j]
                ji[b, s] = j
        return m, ji

    # onset spectrum for template matching: flux profile 20-8000 Hz at peak
    tsel = (freqs >= 20) & (freqs < 8000)

    def onset_spec(j):
        seg = dflux[max(0, j - 1):j + 3, tsel].sum(axis=0)
        norm = np.linalg.norm(seg)
        return seg / norm if norm > 0 else seg

    def cos(a, b):
        return float(np.dot(a, b))

    scans = {k: slot_scan(v) for k, v in envs.items()}
    med = {k: np.median(v[v > 0]) for k, v in envs.items()}

    # ---- templates from the surest hits ----
    km, kji = scans['kick']
    sm, sji = scans['snare']
    cm, cji = scans['crash']

    def bars_in(a, b):
        b0 = max(0, int(np.ceil((a - ANCHOR) / BAR)))
        b1 = min(n_bars, int((b - ANCHOR) / BAR))
        return range(b0, b1)

    ref_snare = []
    for b in bars_in(94375, 153250):        # V2 + C2a
        for s in (4, 12):
            if sm[b, s] / med['snare'] > 2.5:
                ref_snare.append(onset_spec(sji[b, s]))
    ref_kick = []
    for b in bars_in(94375, 153250):
        for s in (0, 8):
            if km[b, s] / med['kick'] > 5.0:
                ref_kick.append(onset_spec(kji[b, s]))
    t_snare = np.mean(ref_snare, axis=0)
    t_snare /= np.linalg.norm(t_snare)
    t_kick = np.mean(ref_kick, axis=0)
    t_kick /= np.linalg.norm(t_kick)
    print(f'templates: snare from {len(ref_snare)} refs, '
          f'kick from {len(ref_kick)} refs, '
          f'snare-kick template cos = {cos(t_snare, t_kick):.2f}')

    def seg_mean(env, t0, t1):
        a = max(0, int((t0 - tms[0]) / hop_ms))
        b = min(len(env), int((t1 - tms[0]) / hop_ms))
        return env[a:b].mean() if b > a else 0.0

    marks = {'kick': [], 'snare': [], 'crash': []}
    dbg = {'kick': [], 'snare': [], 'crash': []}

    for b in range(n_bars):
        bar_med = {k: np.median(scans[k][0][b]) + 1e-9 for k in scans}
        for s in range(16):
            t_grid = ANCHOR + b * BAR + s * SIXT
            sec = sec_of(t_grid)
            if sec in ('INTRO', 'TAIL'):
                continue

            # ---- snare: backbeat slots (4, 12) + very strong offbeat fills
            v, j = sm[b, s], sji[b, s]
            rel, ab = v / bar_med['snare'], v / med['snare']
            sim = cos(onset_spec(j), t_snare)
            is_bb = s in (4, 12)
            if ((is_bb and rel >= 1.6 and ab >= 1.5 and sim >= 0.55) or
                    (not is_bb and rel >= 3.2 and ab >= 4.0 and sim >= 0.65)):
                marks['snare'].append(snap(float(tms[j])))
                dbg['snare'].append((snap(float(tms[j])), sec, s,
                                     round(ab, 1), round(sim, 2)))

            # ---- kick: 8th slots + very strong 16ths
            v, j = km[b, s], kji[b, s]
            rel, ab = v / bar_med['kick'], v / med['kick']
            sim = cos(onset_spec(j), t_kick)
            if ((s % 2 == 0 and rel >= 1.8 and ab >= 4.0 and sim >= 0.55) or
                    (s % 2 == 1 and rel >= 2.5 and ab >= 7.0 and sim >= 0.6)):
                marks['kick'].append(snap(float(tms[j])))
                dbg['kick'].append((snap(float(tms[j])), sec, s,
                                    round(ab, 1), round(sim, 2)))

            # ---- crash: quarter slots, ring test
            v, j = cm[b, s], cji[b, s]
            ab = v / med['crash']
            if s % 4 == 0 and ab >= 3.5:
                t = float(tms[j])
                attack = seg_mean(high_e, t, t + 120)
                ring = seg_mean(high_e, t + 250, t + 1000)
                before = seg_mean(high_e, t - 400, t - 80)
                if ring / (attack + 1e-12) >= 0.25 and \
                        ring / (before + 1e-12) >= 1.1:
                    marks['crash'].append(snap(t))
                    dbg['crash'].append((snap(t), sec, s, round(ab, 1),
                                         round(ring / (attack + 1e-12), 1)))

    for k in marks:
        # dedupe within 100 ms
        out = []
        for t in sorted(set(marks[k])):
            if not out or t - out[-1] >= 100:
                out.append(t)
        marks[k] = out
        per = {}
        for t, sec, *_ in dbg[k]:
            per[sec] = per.get(sec, 0) + 1
        print(f'{k}: {len(out)} marks  per-section '
              f'{ {name: per.get(name, 0) for name, _, _ in SECTIONS if per.get(name)} }')

    # backbeat coverage sanity
    print('snare backbeat coverage:')
    for name, a, b in SECTIONS:
        if name in ('INTRO', 'TAIL'):
            continue
        nb = (b - a) / BAR * 2
        cnt = sum(1 for t, sec, s, *_ in dbg['snare']
                  if sec == name and s in (4, 12))
        print(f'  {name:5} {cnt:3}/{nb:4.1f} ({cnt / nb * 100:3.0f}%)')

    print('kick slot histogram:',
          dict(sorted({}.items())) or
          {s: sum(1 for r in dbg['kick'] if r[2] == s) for s in range(16)
           if any(r[2] == s for r in dbg['kick'])})

    json.dump({'anchor': ANCHOR, 'bar_ms': BAR, 'marks': marks, 'debug': dbg},
              open(OUT, 'w'))
    print(f'WROTE {OUT}')


if __name__ == '__main__':
    main()
