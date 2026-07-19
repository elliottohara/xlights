"""Detect piano note onsets + pitches for the whole song.

Produces a timing-only template with mark labels usable by the xLights Piano
effect (MIDI integers / space-separated chord clusters).

Produces: Timing Templates/Holy Forever Piano Notes.xsq
Track name: Piano Notes

Import ONCE into the open sequence (do not re-import — mark duplication).

Run:
  Christmas/Sequences/Holy Forever 2026/Tools/.venv/bin/python \\
    Christmas/Sequences/Holy Forever 2026/Tools/build_piano_notes_timing.py
"""
import subprocess
import wave
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav'
OUT_XSQ = ('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/'
           'Timing Templates/Holy Forever Piano Notes.xsq')
MEDIA = ('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Media/'
         'Chris Tomlin - Holy Forever (Lyric Video).mp4')
AUDITION = ('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/'
            'Tools/piano_notes_audition.mp3')

FRAME = 25
SONG_END = 308300
# Piano presence starts with V1 acoustic; pad before first hit stays empty labels
RANGE_START = 14000
NOTE_DUR = 350  # labeled mark length (ms); Piano fades within this
CLUSTER_MS = 80  # merge near-simultaneous pitches into one chord label

# Section-aware density: intimate acoustic is sparse; full-band is gated harder
# (start_ms, end_ms, score_thr, min_sep_ms, max_notes_in_cluster)
SECTION_GATES = [
    (14000, 40950, 0.42, 180, 4),    # V1 intimate — denser notes OK
    (40950, 66700, 0.55, 280, 3),    # PC1 building
    (66700, 94375, 0.70, 400, 3),    # C1
    (94375, 126725, 0.58, 300, 3),   # V2
    (126725, 181450, 0.72, 420, 3),  # C2*
    (181450, 233350, 0.75, 450, 3),  # PC2*
    (233350, 286700, 0.78, 480, 2),  # C3*
    (286700, 308300, 0.60, 350, 3),  # outro tag
]


def snap(t):
    return int(round(t / FRAME) * FRAME)


def hz_to_midi(hz):
    if hz <= 0:
        return None
    return int(round(69 + 12 * np.log2(hz / 440.0)))


def midi_clamp(m):
    if m is None:
        return None
    if 36 <= m <= 96:  # C2..C7 piano-ish
        return m
    return None


def gate_for(ms):
    for a, b, thr, sep, nmax in SECTION_GATES:
        if a <= ms < b:
            return thr, sep, nmax
    return 0.75, 450, 2


def detect():
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    x = x.astype(np.float64) / 32768.0

    hop = int(0.010 * sr)
    win = int(0.080 * sr)
    nfft = 8192
    window = np.hanning(win)
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    low = (freqs >= 80) & (freqs <= 250)
    mid = (freqs >= 250) & (freqs <= 900)
    hi = (freqs >= 900) & (freqs <= 2800)
    # kick-heavy / cymbal-heavy reject bands
    sub = (freqs >= 40) & (freqs < 80)
    air = (freqs >= 4000) & (freqs <= 10000)

    s0 = int(RANGE_START / 1000 * sr)
    seg = x[s0:]
    n_frames = max(0, (len(seg) - win) // hop)

    low_e = np.empty(n_frames)
    mid_e = np.empty(n_frames)
    hi_e = np.empty(n_frames)
    sub_e = np.empty(n_frames)
    air_e = np.empty(n_frames)
    rms = np.empty(n_frames)

    for i in range(n_frames):
        frame = seg[i * hop:i * hop + win] * window
        spec = np.abs(np.fft.rfft(frame, nfft))
        low_e[i] = spec[low].sum()
        mid_e[i] = spec[mid].sum()
        hi_e[i] = spec[hi].sum()
        sub_e[i] = spec[sub].sum()
        air_e[i] = spec[air].sum()
        rms[i] = np.sqrt(np.mean(frame ** 2))

    def flux(a):
        return np.maximum(np.diff(a, prepend=a[0]), 0)

    def nrm(a):
        return a / (np.percentile(a, 95) + 1e-12)

    breadth = np.sqrt(nrm(flux(low_e)) * nrm(flux(mid_e)))
    score = (0.40 * breadth
             + 0.25 * nrm(flux(mid_e))
             + 0.15 * nrm(flux(hi_e))
             + 0.20 * nrm(flux(rms)))
    # penalize kick thump / cymbal splash
    score = score * (1.0 - 0.55 * np.clip(nrm(flux(sub_e)), 0, 1))
    score = score * (1.0 - 0.45 * np.clip(nrm(flux(air_e)), 0, 1))

    # local peaks
    raw = []
    for i in range(5, n_frames - 5):
        ms = RANGE_START + i * 10
        thr, sep, _ = gate_for(ms)
        if score[i] < thr:
            continue
        if score[i] != score[i - 5:i + 6].max():
            continue
        raw.append((i, float(score[i]), ms))

    # section-aware NMS
    kept = []
    for i, v, ms in raw:
        thr, sep, _ = gate_for(ms)
        sep_frames = max(1, int(sep / 10))
        if v < thr:
            continue
        if kept and (i - kept[-1][0]) < sep_frames:
            if v > kept[-1][1]:
                kept[-1] = (i, v, ms)
            continue
        kept.append((i, v, ms))

    # pitch per onset (+ nearby harmonic peaks for chords)
    notes = []  # (ms, [midi...], score)
    for i, v, ms in kept:
        thr, sep, nmax = gate_for(ms)
        frame = seg[i * hop:i * hop + win] * window
        spec = np.abs(np.fft.rfft(frame, nfft))
        band = (freqs >= 90) & (freqs <= 2000)
        s = spec.copy()
        s[~band] = 0
        # top spectral peaks → candidate fundamentals
        peak_idx = []
        s2 = s.copy()
        for _ in range(8):
            j = int(np.argmax(s2))
            if s2[j] <= 0:
                break
            peak_idx.append(j)
            # zero neighborhood ±35 Hz
            lo = np.searchsorted(freqs, freqs[j] - 35)
            hi_i = np.searchsorted(freqs, freqs[j] + 35)
            s2[lo:hi_i] = 0
        midis = []
        for j in peak_idx:
            m = midi_clamp(hz_to_midi(float(freqs[j])))
            if m is None:
                continue
            # prefer fundamentals: drop if strong subharmonic already chosen
            if any(abs(m - p) % 12 == 0 and abs(m - p) >= 12 for p in midis):
                # keep lower of octave pair
                continue
            if m not in midis:
                midis.append(m)
            if len(midis) >= nmax:
                break
        if not midis:
            # fallback: spectral centroid → single note
            wsum = s[band].sum()
            if wsum > 0:
                f0 = float(np.sum(freqs[band] * s[band]) / wsum)
                m = midi_clamp(hz_to_midi(f0))
                if m is not None:
                    midis = [m]
        if midis:
            notes.append((snap(ms), sorted(midis), v))

    # cluster near-simultaneous onsets into one labeled mark
    if not notes:
        return []
    notes.sort(key=lambda t: t[0])
    clusters = []
    cur_t, cur_m, cur_v = notes[0][0], set(notes[0][1]), notes[0][2]
    for t, midis, v in notes[1:]:
        if t - cur_t <= CLUSTER_MS:
            cur_m.update(midis)
            cur_v = max(cur_v, v)
        else:
            clusters.append((cur_t, sorted(cur_m)[:4], cur_v))
            cur_t, cur_m, cur_v = t, set(midis), v
    clusters.append((cur_t, sorted(cur_m)[:4], cur_v))
    return clusters


def hit_track(hits):
    """Contiguous: unlabeled gaps + short labeled note marks."""
    marks = []
    cur = 0
    for i, (t, midis, _v) in enumerate(hits):
        nxt = hits[i + 1][0] if i + 1 < len(hits) else SONG_END
        end = min(t + NOTE_DUR, nxt, SONG_END)
        end = snap(end)
        t = snap(t)
        if end <= t:
            end = min(t + FRAME, SONG_END)
        if t > cur:
            marks.append((cur, t, ''))
        label = ' '.join(str(m) for m in midis)
        marks.append((t, end, label))
        cur = end
    if cur < SONG_END:
        marks.append((cur, SONG_END, ''))
    return marks


def write_xsq(marks):
    Path(OUT_XSQ).parent.mkdir(parents=True, exist_ok=True)
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
        '    <Element collapsed="0" type="timing" name="Piano Notes" '
        'visible="1" views="" active="1" />',
        '  </DisplayElements>',
        '  <ElementEffects>',
        '    <Element type="timing" name="Piano Notes">',
        '      <EffectLayer>',
    ]
    for s, e, lab in marks:
        if e <= s:
            continue
        lines.append(f'        <Effect label="{escape(lab)}" '
                     f'startTime="{s}" endTime="{e}" />')
    lines += [
        '      </EffectLayer>',
        '    </Element>',
        '  </ElementEffects>',
        '</xsequence>',
    ]
    Path(OUT_XSQ).write_text('\n'.join(lines) + '\n')


def write_audition(hits):
    """Ducked full song + click on each note mark (first 90s for quick check)."""
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    x = x.astype(np.float64) / 32768.0
    a0, a1 = 0, min(len(x), int(90 * sr))
    y = x[a0:a1] * 0.32
    n = int(sr * 0.035)
    t = np.arange(n) / sr
    click = np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 40) * 0.9
    for ms, _m, _v in hits:
        i = int(ms / 1000 * sr) - a0
        if 0 <= i < len(y) - n:
            y[i:i + n] += click
    y = np.clip(y, -1, 1)
    tmp = AUDITION.replace('.mp3', '.wav')
    with wave.open(tmp, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    subprocess.run(
        ['ffmpeg', '-y', '-i', tmp, '-codec:a', 'libmp3lame', '-q:a', '4', AUDITION],
        check=True, capture_output=True)
    print(f'audition (0-90s): {AUDITION}')


def main():
    hits = detect()
    print(f'{len(hits)} piano note/chord marks:')
    by_sec = defaultdict(int)
    all_midi = []
    for ms, midis, v in hits:
        by_sec[ms // 30000] += 1
        all_midi.extend(midis)
        if ms < 45000 or len(hits) < 40:
            print(f'  {ms:6d} ({ms/1000:6.2f}s) midi={midis} score={v:.2f}')
    print('density per 30s bucket:', dict(sorted(by_sec.items())))
    if all_midi:
        print(f'MIDI range: {min(all_midi)}-{max(all_midi)} '
              f'(median {int(np.median(all_midi))})')
    marks = hit_track(hits)
    cur = 0
    for s, e, _ in marks:
        assert e > s and s == cur and s % FRAME == 0 and e % FRAME == 0
        cur = e
    assert cur == SONG_END
    write_xsq(marks)
    write_audition(hits)
    nlab = sum(1 for *_, lab in marks if lab)
    print(f'WROTE {OUT_XSQ} ({nlab} labeled marks)')


if __name__ == '__main__':
    main()
