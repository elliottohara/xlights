"""PC1 building: Mega Tree star on the audible bass thumps (not Kick track).

The imported Kick marks are early / miss the bass figure. PC1's low end is
eight pairs of thumps (~625–650 ms apart, pairs ~2.7 s apart), located by
low-passed envelope onset on holy_44k.wav.

Each hit: gold Shockwave, fast attack, long bass fade. Pair follow-ups are
nudged ~50 ms early (onset peak lags the perceived attack) and use a snappier
Shockwave + hotter palette so the second thump doesn't feel delayed.
Alternates Tree Topper L1/L2/L3 so decays can overlap.

Owns L1–L3 only inside WINDOW (C1 holy On on L2 at 67575 untouched).

Run:
    python3 Christmas/Sequences/Holy\\ Forever\\ 2026/Tools/pc1_double_kick_star.py [--dry-run]
    python3 Christmas/Sequences/Holy\\ Forever\\ 2026/Tools/pc1_double_kick_star.py --clear-only
    python3 Christmas/Sequences/Holy\\ Forever\\ 2026/Tools/pc1_double_kick_star.py --audition
"""
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x


OUT = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq'
AUDIO = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav'
AUDITION = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/pc1_bass_thump_audition.mp3'
TARGET = 'Tree Topper'
LAYERS = (1, 2, 3)
RANGE_START = 40600
RANGE_END = 67570
WINDOW = (42000, 67570)

DECAY_MS = 1100
DECAY_FOLLOW_MS = 950  # slightly shorter ring on the punchy 2nd
DOUBLE_GAP_MS = 750  # pair spacing is ~625–650 before polish
# Envelope peak sits a touch late on the 2nd of each pair — pull it forward.
FOLLOW_EARLY_MS = 50

SHOCK = (
    'E_CHECKBOX_Shockwave_Blend_Edges=1,'
    'E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,'
    'E_SLIDER_Shockwave_Accel=8,'
    'E_SLIDER_Shockwave_CenterX=50,'
    'E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_Start_Radius=1,'
    'E_SLIDER_Shockwave_Start_Width=40,'
    'E_SLIDER_Shockwave_End_Radius=105,'
    'E_SLIDER_Shockwave_End_Width=24,'
    'T_TEXTCTRL_Fadein=.02,'
    'T_TEXTCTRL_Fadeout=1.00'
)
# Snappier bloom so the follow-up reads with the hit, not after it.
SHOCK_FOLLOW = (
    'E_CHECKBOX_Shockwave_Blend_Edges=1,'
    'E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,'
    'E_SLIDER_Shockwave_Accel=12,'
    'E_SLIDER_Shockwave_CenterX=50,'
    'E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_Start_Radius=8,'
    'E_SLIDER_Shockwave_Start_Width=55,'
    'E_SLIDER_Shockwave_End_Radius=110,'
    'E_SLIDER_Shockwave_End_Width=20,'
    'T_TEXTCTRL_Fadein=0,'
    'T_TEXTCTRL_Fadeout=.85'
)
GOLD = (
    'C_BUTTON_Palette1=#FFC857,'
    'C_BUTTON_Palette2=#FFE9B0,'
    'C_CHECKBOX_Palette1=1,'
    'C_CHECKBOX_Palette2=1,'
    'C_SLIDER_Brightness=100'
)
GOLD_HOT = (
    'C_BUTTON_Palette1=#FFD978,'
    'C_BUTTON_Palette2=#FFFFFF,'
    'C_BUTTON_Palette3=#FFC857,'
    'C_CHECKBOX_Palette1=1,'
    'C_CHECKBOX_Palette2=1,'
    'C_CHECKBOX_Palette3=1,'
    'C_SLIDER_Brightness=115'
)


def snap(t):
    return int(round(t / 25.0) * 25)


def detect_bass_thumps():
    """Strong low-passed envelope onsets in PC1 building — the bass pairs."""
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    audio = audio.astype(np.float64) / 32768.0

    lp_win = max(3, int(sr / 80))
    lp = np.convolve(audio, np.ones(lp_win) / lp_win, mode='same')
    env = np.abs(lp)
    env_s = np.convolve(env, np.ones(int(0.025 * sr)) / int(0.025 * sr), mode='same')
    onset = np.maximum(np.diff(env_s, prepend=env_s[0]), 0)
    onset_s = np.convolve(
        onset, np.ones(int(0.012 * sr)) / int(0.012 * sr), mode='same'
    )

    i0 = int(RANGE_START / 1000 * sr)
    i1 = int(RANGE_END / 1000 * sr)
    seg = onset_s[i0:i1]
    dist = int(0.38 * sr)
    floor = np.percentile(seg, 88)

    peaks = []
    i = 0
    while i < len(seg):
        if seg[i] >= floor:
            j1 = min(len(seg), i + dist)
            j = i + int(np.argmax(seg[i:j1]))
            w = int(0.02 * sr)
            a, z = max(0, j - w), min(len(seg), j + w + 1)
            j = a + int(np.argmax(seg[a:z]))
            peaks.append(j)
            i = j + dist
        else:
            i += 1

    # Strong thumps only (drops weak LP blips between the bass pairs).
    hits = []
    for p in peaks:
        t_ms = (p + i0) / sr * 1000.0
        if float(seg[p]) >= 5e-5:
            hits.append(snap(t_ms))
    hits = sorted(set(hits))

    # Polish: pull each pair's 2nd hit forward so it doesn't feel late.
    polished = []
    for i, t in enumerate(hits):
        if i > 0 and (t - hits[i - 1]) <= DOUBLE_GAP_MS:
            t = snap(t - FOLLOW_EARLY_MS)
            if polished and t <= polished[-1]:
                t = polished[-1] + 400
        polished.append(t)
    return polished


def write_audition(hits):
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    audio = audio.astype(np.float64) / 32768.0
    i0 = int(RANGE_START / 1000 * sr)
    i1 = int(RANGE_END / 1000 * sr)
    seg = audio[i0:i1] * 0.32
    for h in hits:
        n0 = int((h - RANGE_START) / 1000 * sr)
        n1 = n0 + int(0.04 * sr)
        if n0 < 0 or n0 >= len(seg):
            continue
        n1 = min(n1, len(seg))
        tt = np.arange(n1 - n0) / sr
        seg[n0:n1] += 0.7 * np.exp(-tt * 35) * np.sin(2 * np.pi * 90 * tt)
    seg = np.clip(seg, -1, 1)
    tmp = '/tmp/pc1_bass_thump_audition.wav'
    with wave.open(tmp, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((seg * 32767).astype(np.int16).tobytes())
    subprocess.run(
        ['ffmpeg', '-y', '-i', tmp, '-codec:a', 'libmp3lame', '-q:a', '4', AUDITION],
        check=True,
        capture_output=True,
    )
    print(f'audition → {AUDITION}')


def plan(hits):
    """Returns (layer, settings, palette, start, end) per thump."""
    busy_until = {layer: 0 for layer in LAYERS}
    effects = []
    for i, start in enumerate(hits):
        layer = min(LAYERS, key=lambda L: busy_until[L])
        if busy_until[layer] > start:
            raise SystemExit(f'no free layer at {start}: busy={busy_until}')
        is_follow = i > 0 and (start - hits[i - 1]) <= DOUBLE_GAP_MS
        decay = DECAY_FOLLOW_MS if is_follow else DECAY_MS
        end = min(start + decay, RANGE_END)
        settings = SHOCK_FOLLOW if is_follow else SHOCK
        palette = GOLD_HOT if is_follow else GOLD
        effects.append((layer, settings, palette, start, end))
        busy_until[layer] = end

    by_layer = {L: [] for L in LAYERS}
    for layer, _, _, start, end in effects:
        for s2, e2 in by_layer[layer]:
            assert end <= s2 or start >= e2, f'L{layer} overlap {start}-{end} vs {s2}-{e2}'
        by_layer[layer].append((start, end))
    return effects


def effects_in_window(layer):
    w0, w1 = WINDOW
    ids = x.xl('getEffectIDs', model=TARGET)['effects']
    while len(ids) <= layer:
        ids.append([])
    out = []
    for eid in ids[layer]:
        s = x.xl('getEffectSettings', model=TARGET, layer=layer, id=eid)
        start, end = int(s['startTime']), int(s['endTime'])
        if end > w0 and start < w1:
            out.append((eid, start, end, s.get('name', '')))
    return out


def _occupied_dark(layer, dark_end=400):
    """25 ms park starts already used on this layer in the dark intro."""
    ids = x.xl('getEffectIDs', model=TARGET)['effects']
    while len(ids) <= layer:
        ids.append([])
    used = set()
    for eid in ids[layer]:
        s = x.xl('getEffectSettings', model=TARGET, layer=layer, id=eid)
        start = int(s['startTime'])
        if start < dark_end:
            used.add(start)
    return used


def off_park(layer, eid, start, used=None):
    # Tree Topper is dark through the intimate intro — park anywhere t < 400.
    if used is None:
        used = _occupied_dark(layer)
    park = 25
    while park in used:
        park += 25
    assert park + 25 <= 400, f'out of dark park slots on L{layer}'
    used.add(park)
    x.xl(
        'setEffectSettings',
        model=TARGET,
        layer=layer,
        id=eid,
        name='Off',
        startTime=park,
        endTime=park + 25,
        settings='',
        palette='',
    )
    print(f'  off-parked L{layer} id={eid} (was start={start}) → {park}-{park + 25}')


def main():
    dry_run = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    audition_only = '--audition' in sys.argv

    hits = detect_bass_thumps()
    print(f'{len(hits)} audible bass thumps in PC1 building:')
    for a, b in zip(hits, hits[1:]):
        print(f'  {a}  (+{b - a}ms → next)')
    if hits:
        print(f'  {hits[-1]}')

    if audition_only:
        write_audition(hits)
        return

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    effects = [] if clear_only else plan(hits)
    print(f'plan: {len(effects)} star shocks')
    for layer, settings, _, start, end in effects:
        kind = 'follow' if settings is SHOCK_FOLLOW else 'lead'
        print(f'  L{layer} Shockwave/{kind} {start}-{end} ({end - start}ms)')

    for layer in LAYERS:
        existing = effects_in_window(layer)
        print(f'Tree Topper L{layer}: {len(existing)} effect(s) in window')

    if dry_run:
        print('dry-run: no writes')
        return

    for layer in LAYERS:
        used = _occupied_dark(layer)
        for eid, start, _, _ in effects_in_window(layer):
            off_park(layer, eid, start, used=used)

    if not clear_only:
        for layer, settings, palette, start, end in effects:
            x.add_effect(TARGET, layer, 'Shockwave', settings, palette, start, end)

    got = sum(len(effects_in_window(L)) for L in LAYERS)
    expected = 0 if clear_only else len(effects)
    assert got == expected, f'expected {expected} in window, found {got}'
    print(f'{TARGET}: {got} bass-thump shock(s)')

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
