"""Build the drum/mood/section timing template for Holy Forever 2026.

Produces `Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Drums and Mood.xsq` with six tracks:

- Song Sections  — labeled, original effect-section boundaries (+C2c/C3c)
- Mood           — labeled energy/mood arcs on true-grid downbeats
- Beat Count     — 1-4 labels on the AUDIO-TRUE grid (anchor 600 ms, 72 BPM)
- Kick           — detected kick-drum hits (band flux + template match)
- Snare          — steady 2&4 backbeat V2..C3c end + detected fills
- Cymbals        — crash hits that pass the ring (sustain) test

Grid truth (this script's analysis): downbeats at 600 + n*3333.333 ms.
The sequence's older documented anchor (180 ms) is half a beat early vs
the audio; snares fold exactly on beats 2/4 of the 600-anchor grid.

Run: Christmas/Sequences/Holy Forever 2026/Tools/.venv/bin/python Christmas/Sequences/Holy Forever 2026/Tools/build_timing_template.py
"""
import wave
from xml.sax.saxutils import escape

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav'
OUT_XSQ = ('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Timing Templates/'
           'Holy Forever Drums and Mood.xsq')
MEDIA = ('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Media/'
         'Chris Tomlin - Holy Forever (Lyric Video).mp4')

ANCHOR = 600.0
BAR = 3333.0 + 1.0 / 3.0
BEAT = BAR / 4
SIXT = BAR / 16
FRAME = 25
SONG_END = 308300
N_FFT = 2048
HOP = 256
TOL = 45.0

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


def bar_t(b, slot=0):
    return ANCHOR + b * BAR + slot * SIXT


# --------------------------------------------------------------- analysis
def analyze():
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
    dflux = np.maximum(np.diff(logm, axis=0, prepend=logm[:1]), 0)

    def bflux(lo, hi):
        return dflux[:, (freqs >= lo) & (freqs < hi)].sum(axis=1)

    kick_env = bflux(40, 110)
    snare_env = bflux(2000, 7500) + 0.5 * bflux(160, 400)
    crash_env = bflux(8000, 16000)
    high_e = (mag[:, (freqs >= 8000) & (freqs < 16000)] ** 2).sum(axis=1)

    n_bars = int((tms[-1] - ANCHOR) / BAR) + 1
    tol = int(TOL / hop_ms)

    def slot_scan(env):
        m = np.zeros((n_bars, 16))
        ji = np.zeros((n_bars, 16), dtype=int)
        for b in range(n_bars):
            for s in range(16):
                t = bar_t(b, s)
                i = int(round((t - tms[0]) / hop_ms))
                a, z = max(0, i - tol), min(len(env), i + tol + 1)
                if a >= z:
                    continue
                j = a + int(np.argmax(env[a:z]))
                m[b, s] = env[j]
                ji[b, s] = j
        return m, ji

    tsel = (freqs >= 20) & (freqs < 8000)

    def onset_spec(j):
        seg = dflux[max(0, j - 1):j + 3, tsel].sum(axis=0)
        norm = np.linalg.norm(seg)
        return seg / norm if norm > 0 else seg

    km, kji = slot_scan(kick_env)
    sm, sji = slot_scan(snare_env)
    cm, cji = slot_scan(crash_env)
    med_k = np.median(kick_env[kick_env > 0])
    med_s = np.median(snare_env[snare_env > 0])
    med_c = np.median(crash_env[crash_env > 0])

    def bars_in(a, b):
        return range(max(0, int(np.ceil((a - ANCHOR) / BAR))),
                     min(n_bars, int((b - ANCHOR) / BAR)))

    ref_kick = [onset_spec(kji[b, s]) for b in bars_in(94375, 153250)
                for s in (0, 8) if km[b, s] / med_k > 5.0]
    t_kick = np.mean(ref_kick, axis=0)
    t_kick /= np.linalg.norm(t_kick)

    def seg_mean(env, t0, t1):
        a = max(0, int((t0 - tms[0]) / hop_ms))
        b = min(len(env), int((t1 - tms[0]) / hop_ms))
        return env[a:b].mean() if b > a else 0.0

    # ---- kick: even slots moderate gate, odd 16ths strict; no V1/OUT ----
    kicks = []
    for b in range(n_bars):
        bar_med = np.median(km[b]) + 1e-9
        for s in range(16):
            t_grid = bar_t(b, s)
            sec = sec_of(t_grid)
            if sec in ('INTRO', 'V1', 'OUT', 'TAIL'):
                continue
            v, j = km[b, s], kji[b, s]
            rel, ab = v / bar_med, v / med_k
            sim = float(np.dot(onset_spec(j), t_kick))
            if ((s % 2 == 0 and rel >= 1.5 and ab >= 3.2 and sim >= 0.5) or
                    (s % 2 == 1 and rel >= 2.4 and ab >= 6.0 and sim >= 0.6)):
                kicks.append((snap(float(tms[j])), sec, s, round(ab, 1)))

    # ---- snare: steady backbeat bars(V2 start)..(C3c end) + fills ----
    snares = []
    v2_bar = int(round((93933.33 - ANCHOR) / BAR))      # 28
    last_bar = int(round((287266.67 - ANCHOR) / BAR))   # 86 (exclusive)
    for b in range(v2_bar, last_bar):
        for s in (4, 12):
            t_grid = bar_t(b, s)
            j = sji[b, s]
            # use detected peak if it is credible, else the grid slot
            t = float(tms[j]) if sm[b, s] / med_s >= 1.2 else t_grid
            snares.append((snap(t), sec_of(t_grid), s, round(sm[b, s] / med_s, 1)))
    # fills: strong non-backbeat hits inside the groove span
    for b in range(v2_bar - 1, last_bar):   # include the pickup fill bar
        bar_med = np.median(sm[b]) + 1e-9
        for s in range(16):
            if s in (4, 12):
                continue
            t_grid = bar_t(b, s)
            v = sm[b, s]
            if v / bar_med >= 3.2 and v / med_s >= 4.0:
                snares.append((snap(float(tms[sji[b, s]])), sec_of(t_grid),
                               s, round(v / med_s, 1)))
    snares = sorted(set(snares))

    # ---- crash: quarter slots + ring test ----
    crashes = []
    for b in range(n_bars):
        for s in (0, 4, 8, 12):
            t_grid = bar_t(b, s)
            sec = sec_of(t_grid)
            if sec in ('INTRO', 'TAIL'):
                continue
            v, j = cm[b, s], cji[b, s]
            if v / med_c < 3.5:
                continue
            t = float(tms[j])
            attack = seg_mean(high_e, t, t + 120)
            ring = seg_mean(high_e, t + 250, t + 1000)
            before = seg_mean(high_e, t - 400, t - 80)
            if ring / (attack + 1e-12) >= 0.25 and ring / (before + 1e-12) >= 1.1:
                crashes.append((snap(t), sec, s, round(v / med_c, 1)))

    return kicks, snares, crashes


# --------------------------------------------------------------- tracks
def dedupe(hits, min_gap=100):
    out = []
    for h in sorted(hits):
        if not out or h[0] - out[-1][0] >= min_gap:
            out.append(h)
    return out


def hit_track(hits, dur, label):
    """Contiguous marks: unlabeled gap fillers + short labeled hit marks."""
    marks = []
    cur = 0
    for i, (t, *_rest) in enumerate(hits):
        if t < cur:
            continue
        nxt = hits[i + 1][0] if i + 1 < len(hits) else SONG_END
        end = min(t + dur, nxt, SONG_END)
        if t > cur:
            marks.append((cur, t, ''))
        marks.append((t, end, label))
        cur = end
    if cur < SONG_END:
        marks.append((cur, SONG_END, ''))
    return marks


def beat_count_track():
    marks = [(0, 600, '')]
    k = 0
    while True:
        s = snap(ANCHOR + k * BEAT)
        e = snap(ANCHOR + (k + 1) * BEAT)
        if s >= SONG_END:
            break
        e = min(e, SONG_END)
        marks.append((s, e, str(k % 4 + 1)))
        k += 1
    return marks


def labeled_track(bounds):
    """bounds = [(t, label), ...] contiguous to SONG_END."""
    marks = []
    for i, (t, lab) in enumerate(bounds):
        e = bounds[i + 1][0] if i + 1 < len(bounds) else SONG_END
        marks.append((snap(t), snap(e), lab))
    return marks


SECTION_BOUNDS = [
    (0, 'Intro - choir pad'),
    (15520, 'Verse 1'),
    (41850, 'Pre-Chorus 1'),
    (67570, 'Chorus 1'),
    (95100, 'Verse 2'),
    (127630, 'Chorus 2'),
    (154150, 'Chorus 2 - Hear Your People (female feature)'),
    (166850, 'Chorus 2 - Holy Forever'),
    (181900, 'Pre-Chorus 2 (pass 1)'),
    (207210, 'Pre-Chorus 2 (pass 2 - full cast)'),
    (234230, 'Final Chorus'),
    (260760, 'Final Chorus - Hear Your People'),
    (273650, 'Final Chorus - Holy Forever'),
    (287290, 'Outro - solo tag'),
    (301500, 'Final hold - fade'),
]

MOOD_BOUNDS = [
    (0, 'Ethereal - dark reverent choir pad'),
    (13900, 'Intimate - acoustic verse, light percussion'),
    (40600, 'Building - bass and kick enter, lift'),
    (67275, 'Anthemic - full band chorus, warm'),
    (93925, 'Groove - drum kit settles in, duet verse'),
    (127275, 'Soaring - chorus grows, choir swells'),
    (153925, 'Featured - female lead soars over band'),
    (180600, 'Regather - pull back and rebuild'),
    (207275, 'Climbing - second pass, full cast piles on'),
    (233925, 'Climax - maximum praise, everyone'),
    (287275, 'Afterglow - band falls away, solo benediction'),
    (300600, 'Silence - final fade'),
]


# --------------------------------------------------------------- xsq out
def write_xsq(tracks):
    lines = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        '<xsequence BaseChannel="0" ChanCtrlBasic="0" ChanCtrlColor="0" '
        'FixedPointTiming="1" ModelBlending="false">',
        '  <head>',
        '    <version>2026.12</version>',
        '    <author />',
        '    <song>Holy Forever</song>',
        '    <artist>Chris Tomlin</artist>',
        '    <sequenceTiming>25 ms</sequenceTiming>',
        '    <sequenceType>Media</sequenceType>',
        f'    <mediaFile>{escape(MEDIA)}</mediaFile>',
        '    <sequenceDuration>308.314</sequenceDuration>',
        '  </head>',
        '  <nextid>1</nextid>',
        '  <Jukebox />',
        '  <ColorPalettes />',
        '  <EffectDB />',
        '  <DataLayers />',
        '  <DisplayElements>',
    ]
    for name, _ in tracks:
        lines.append(f'    <Element collapsed="0" type="timing" '
                     f'name="{escape(name)}" visible="1" views="" active="1" />')
    lines.append('  </DisplayElements>')
    lines.append('  <ElementEffects>')
    for name, marks in tracks:
        lines.append(f'    <Element type="timing" name="{escape(name)}">')
        lines.append('      <EffectLayer>')
        for s, e, lab in marks:
            if e <= s:
                continue
            lines.append(f'        <Effect label="{escape(lab)}" '
                         f'startTime="{s}" endTime="{e}" />')
        lines.append('      </EffectLayer>')
        lines.append('    </Element>')
    lines.append('  </ElementEffects>')
    lines.append('</xsequence>')
    with open(OUT_XSQ, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def validate(marks, name):
    cur = 0
    for s, e, _ in marks:
        assert e > s, f'{name}: empty mark {s}-{e}'
        assert s == cur, f'{name}: gap/overlap at {s} (expected {cur})'
        assert s % FRAME == 0 and e % FRAME == 0, f'{name}: off-frame {s}-{e}'
        cur = e
    assert cur == SONG_END, f'{name}: ends at {cur}'


def main():
    kicks, snares, crashes = analyze()
    kicks, snares, crashes = dedupe(kicks), dedupe(snares), dedupe(crashes)

    for name, hits in (('kick', kicks), ('snare', snares), ('crash', crashes)):
        per = {}
        for t, sec, s, ab in hits:
            per[sec] = per.get(sec, 0) + 1
        print(f'{name}: {len(hits)} hits {per}')
    print('kick slots:', {s: sum(1 for h in kicks if h[2] == s)
                          for s in range(16) if any(h[2] == s for h in kicks)})

    tracks = [
        ('Song Sections', labeled_track(SECTION_BOUNDS)),
        ('Mood', labeled_track(MOOD_BOUNDS)),
        ('Beat Count', beat_count_track()),
        ('Kick', hit_track([(t,) for t, *_ in kicks], dur=150, label='K')),
        ('Snare', hit_track([(t,) for t, *_ in snares], dur=150, label='S')),
        ('Cymbals', hit_track([(t,) for t, *_ in crashes], dur=400, label='C')),
    ]
    for name, marks in tracks:
        validate(marks, name)
        n_hits = sum(1 for _, _, lab in marks if lab in ('K', 'S', 'C'))
        print(f'track {name!r}: {len(marks)} marks'
              + (f' ({n_hits} hits)' if n_hits else ''))
    write_xsq(tracks)
    print(f'WROTE {OUT_XSQ}')


if __name__ == '__main__':
    main()
