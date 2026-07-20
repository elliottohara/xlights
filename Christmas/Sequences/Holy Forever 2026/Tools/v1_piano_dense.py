"""Dense intimate-V1 piano onsets -> one shrub prop per note.

The imported `Piano Notes` timing track is deliberately sparse (density-
gated), so driving the shrubs off it felt thin ("the piano is playing a lot
more notes"). This detects the real note attacks straight from the verse
audio and lights one `All Shrubs GRP` member per note, mapped low-note-left
across the row (same spatial rule as before).

Pipeline (numpy only, in Tools/.venv):
  1. read Tools/holy_44k.wav, slice the V1 span
  2. STFT -> band-limited spectral flux -> adaptive peak pick (dense)
  3. rough dominant pitch per onset (spectral peak in a melodic band)
  4. rank pitches across the 14 members, low -> leftmost
  5. wipe L0 of the props (API) and add one short warm-gold On per onset

Run under the venv so numpy is importable:
    Tools/.venv/bin/python Tools/v1_piano_dense.py [--dry-run] [--clear-only]

Detection knobs live in the CONFIG block; --dry-run prints the onset list
and per-prop counts without touching the sequence.
"""
import json
import math
import sys
import wave

import numpy as np

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-a/Tools')
import xlights_api as x

WAV = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Tools/holy_44k.wav')
OUT = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
EMPTY_SOURCE = 'House'

PROPS = [
    'Shrub Left', 'Rose Bush 1', 'Rose Bush 2', 'Door Tree Left',
    'Rose Bush 3', 'Rose Bush 4', 'Door Tree Right', 'Shrub Center',
    'Rose Bush 5', 'Rose Bush 6', 'Rose Bush 7', 'Rose Bush 8',
    'Shrub Right', 'Rose Bush 9',
]
LEGACY_TARGETS = ['All Shrubs GRP'] + [f'Mini Tree - {i}' for i in range(1, 5)]

# --- CONFIG -----------------------------------------------------------
V1_START_MS, V1_END_MS = 15275, 39975
HOP = 441                 # 10 ms @ 44100
WIN = 2048
FLUX_LO_HZ, FLUX_HI_HZ = 150.0, 2500.0      # onset detection band
PITCH_LO_HZ, PITCH_HI_HZ = 160.0, 1600.0    # melodic pitch band
THRESH_MULT = 1.35        # onset must exceed local-avg flux * this
THRESH_WIN_MS = 250       # local average window for the threshold
MIN_SEP_MS = 150          # min gap between onsets (max density)
PULSE_MS = 260
FRAME_MS = 25
# ----------------------------------------------------------------------

SETTINGS = (
    'E_CHECKBOX_On_Shimmer=0,'
    'T_TEXTCTRL_Fadein=.02,'
    'T_TEXTCTRL_Fadeout=.20'
)
PALETTE = (
    'C_BUTTON_Palette1=#FFD89A,'
    'C_CHECKBOX_Palette1=1,'
    'C_SLIDER_Brightness=55'
)


def read_wav():
    with wave.open(WAV, 'rb') as w:
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
    a /= 32768.0
    return sr, a


def detect():
    sr, a = read_wav()
    i0 = int(V1_START_MS / 1000 * sr)
    i1 = int(V1_END_MS / 1000 * sr)
    seg = a[max(0, i0 - WIN):i1 + WIN]
    base = max(0, i0 - WIN)

    win = np.hanning(WIN)
    n_frames = 1 + (len(seg) - WIN) // HOP
    freqs = np.fft.rfftfreq(WIN, 1.0 / sr)
    flux_band = (freqs >= FLUX_LO_HZ) & (freqs <= FLUX_HI_HZ)
    pitch_band = (freqs >= PITCH_LO_HZ) & (freqs <= PITCH_HI_HZ)

    mags = np.empty((n_frames, flux_band.sum()))
    full = np.empty((n_frames, len(freqs)))
    for f in range(n_frames):
        s = f * HOP
        frame = seg[s:s + WIN] * win
        m = np.abs(np.fft.rfft(frame))
        full[f] = m
        mags[f] = m[flux_band]

    flux = np.zeros(n_frames)
    diff = np.maximum(0.0, mags[1:] - mags[:-1]).sum(axis=1)
    flux[1:] = diff
    if flux.max() > 0:
        flux /= flux.max()

    # adaptive threshold + peak pick
    win_frames = max(1, int(THRESH_WIN_MS / 1000 * sr / HOP))
    onsets = []
    last = -1e9
    min_sep_frames = MIN_SEP_MS / 1000 * sr / HOP
    for f in range(1, n_frames - 1):
        lo = max(0, f - win_frames)
        hi = min(n_frames, f + win_frames)
        local = flux[lo:hi].mean()
        if (flux[f] > local * THRESH_MULT and flux[f] > 0.04
                and flux[f] >= flux[f - 1] and flux[f] >= flux[f + 1]
                and f - last >= min_sep_frames):
            # pitch proxy: spectral centroid in the melodic band (more stable
            # than a single peak bin in a vocal mix; higher = brighter/higher)
            spec = full[f, pitch_band]
            pf = freqs[pitch_band]
            denom = spec.sum()
            fhz = float((spec * pf).sum() / denom) if denom > 0 else 440.0
            midi = 69 + 12 * math.log2(fhz / 440.0) if fhz > 0 else 60
            t_ms = (base + f * HOP) / sr * 1000.0
            onsets.append((t_ms, midi))
            last = f
    return onsets


def snap(ms):
    return int(round(ms / FRAME_MS) * FRAME_MS)


def plan():
    onsets = detect()
    onsets = [(snap(t), m) for t, m in onsets if V1_START_MS <= t <= V1_END_MS]
    print(f'{len(onsets)} onsets detected in V1 '
          f'({(V1_END_MS - V1_START_MS) / 1000:.1f}s -> '
          f'{len(onsets) / ((V1_END_MS - V1_START_MS) / 1000):.1f}/s)')

    # percentile-rank each onset's pitch across all onsets so the row is used
    # evenly (low pitch -> leftmost prop, high -> rightmost), instead of
    # clustering when the centroid estimate bunches up.
    order = sorted(range(len(onsets)), key=lambda i: onsets[i][1])
    n_props = len(PROPS)
    prop_of = [0] * len(onsets)
    for rank, idx in enumerate(order):
        frac = rank / max(len(onsets) - 1, 1)
        prop_of[idx] = min(n_props - 1, int(frac * n_props))

    raw = []
    for i, (t, m) in enumerate(onsets):
        raw.append([prop_of[i], t, t + PULSE_MS, round(m)])

    # clamp same-prop overlaps (shorten earlier pulse) — keep everything on L0
    by_prop = {}
    for p in raw:
        by_prop.setdefault(p[0], []).append(p)
    for pidx, ps in by_prop.items():
        ps.sort(key=lambda p: p[1])
        for cur, nxt in zip(ps, ps[1:]):
            if cur[2] > nxt[1] - FRAME_MS:
                cur[2] = nxt[1] - FRAME_MS
    final = [p for p in raw if p[2] - p[1] >= 75]
    final.sort(key=lambda p: p[1])
    return final


def wipe(model):
    x.xl('cloneModelEffects', target=model, source=EMPTY_SOURCE,
         eraseModel='true')
    assert not x.xl('getEffectIDs', model=model)['effects'][0], \
        f'{model} L0 not empty after wipe'


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    pulses = plan()
    counts = {}
    for pidx, s, e, m in pulses:
        counts[PROPS[pidx]] = counts.get(PROPS[pidx], 0) + 1
    print(f'{len(pulses)} pulses; per-prop: '
          + ', '.join(f'{k}={v}' for k, v in sorted(counts.items())))
    for pidx, s, e, m in pulses:
        print(f'  {s}-{e}  midi~{m}  {PROPS[pidx]}')

    if dry:
        print('dry-run: no writes')
        return

    for t in LEGACY_TARGETS:
        wipe(t)
    for p in PROPS:
        wipe(p)

    if not clear_only:
        for pidx, s, e, _m in pulses:
            x.add_effect(PROPS[pidx], 0, 'On', SETTINGS, PALETTE, s, e)

    total = sum(len(x.xl('getEffectIDs', model=p)['effects'][0]) for p in PROPS)
    expected = 0 if clear_only else len(pulses)
    assert total == expected, f'expected {expected}, found {total}'
    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
