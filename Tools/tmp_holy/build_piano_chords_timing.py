"""Detect big wide piano chord hits and write a timing-only template.

Analysis (intimate acoustic V1): spectral flux that requires a simultaneous
low+mid rise (wide voicing) + RMS jump. That lands ~1.6 s AFTER bar
downbeats — the downbeat grid is the wrong place for these chords.

Produces: Timing Templates/Holy Forever Piano Chords.xsq
Track name: Piano Chords  (label 'P' on each hit; contiguous gap fillers)

Import ONCE into the open sequence (do not re-import — mark duplication).
Then rebuild arches with intimate_arch_chords.py (reads this track).

Run: Tools/tmp_holy/.venv/bin/python Tools/tmp_holy/build_piano_chords_timing.py
"""
import wave
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Tools/tmp_holy/holy_44k.wav'
OUT_XSQ = ('/Users/elliott.ohara/xlights/Timing Templates/'
           'Holy Forever Piano Chords.xsq')
MEDIA = ('/Users/elliott.ohara/xlights/Videos/'
         'Chris Tomlin - Holy Forever (Lyric Video).mp4')
AUDITION = '/Users/elliott.ohara/xlights/Tools/tmp_holy/piano_chord_audition.mp3'

FRAME = 25
SONG_END = 308300
# Intimate Mood → just before PC1 Building; piano chords live here
RANGE_START = 14000
RANGE_END = 40000
HIT_DUR = 400  # labeled mark length (ms)


def snap(t):
    return int(round(t / FRAME) * FRAME)


def detect():
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    x = x.astype(np.float64) / 32768.0

    s0, s1 = int(RANGE_START / 1000 * sr), int(RANGE_END / 1000 * sr)
    seg = x[s0:s1]
    hop = int(0.010 * sr)
    win = int(0.080 * sr)
    nfft = 8192
    window = np.hanning(win)
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    low = (freqs >= 80) & (freqs <= 250)
    mid = (freqs >= 250) & (freqs <= 800)
    hi = (freqs >= 800) & (freqs <= 2500)

    low_e, mid_e, hi_e, rms = [], [], [], []
    for i in range(0, len(seg) - win, hop):
        frame = seg[i:i + win] * window
        spec = np.abs(np.fft.rfft(frame, nfft))
        low_e.append(spec[low].sum())
        mid_e.append(spec[mid].sum())
        hi_e.append(spec[hi].sum())
        rms.append(np.sqrt(np.mean(frame ** 2)))
    low_e, mid_e, hi_e, rms = map(np.array, (low_e, mid_e, hi_e, rms))

    def flux(a):
        return np.maximum(np.diff(a, prepend=a[0]), 0)

    def nrm(a):
        return a / (np.percentile(a, 95) + 1e-12)

    # wide chord = low+mid fire together (breadth) + some upper partials + loudness
    breadth = np.sqrt(nrm(flux(low_e)) * nrm(flux(mid_e)))
    score = (0.45 * breadth
             + 0.25 * nrm(flux(low_e))
             + 0.15 * nrm(flux(hi_e))
             + 0.15 * nrm(flux(rms)))

    # Sparse: one hit per ~bar, keep only strong attacks
    thr, sep = 0.50, int(2800 / 10)
    peaks = []
    for i in range(5, len(score) - 5):
        if score[i] < thr:
            continue
        if score[i] != score[i - 5:i + 6].max():
            continue
        if not peaks or i - peaks[-1][0] >= sep:
            peaks.append((i, float(score[i])))
        elif score[i] > peaks[-1][1]:
            peaks[-1] = (i, float(score[i]))

    hits = []
    for i, v in peaks:
        ms = snap(RANGE_START + i * 10)
        # drop weak false positives (need a real wide attack)
        if RANGE_START <= ms < RANGE_END and v >= 1.5:
            hits.append((ms, v))
    return hits


def hit_track(hits):
    """Contiguous: unlabeled gaps + short labeled 'P' marks."""
    marks = []
    cur = 0
    for i, (t, _v) in enumerate(hits):
        nxt = hits[i + 1][0] if i + 1 < len(hits) else SONG_END
        end = min(t + HIT_DUR, nxt, SONG_END)
        if t > cur:
            marks.append((cur, t, ''))
        marks.append((t, end, 'P'))
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
        '    <Element collapsed="0" type="timing" name="Piano Chords" '
        'visible="1" views="" active="1" />',
        '  </DisplayElements>',
        '  <ElementEffects>',
        '    <Element type="timing" name="Piano Chords">',
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
    """Ducked intimate window + click on each Piano Chord mark."""
    import subprocess
    with wave.open(AUDIO) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    x = x.astype(np.float64) / 32768.0
    a0, a1 = int(12 * sr), int(43 * sr)
    y = x[a0:a1] * 0.35
    n = int(sr * 0.045)
    t = np.arange(n) / sr
    click = np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 35) * 0.95
    for ms, _ in hits:
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
    print(f'audition: {AUDITION}')


def main():
    hits = detect()
    print(f'{len(hits)} piano chord hits in {RANGE_START}-{RANGE_END}:')
    for ms, v in hits:
        print(f'  {ms:6d} ({ms/1000:5.2f}s) score={v:.2f}')
    marks = hit_track(hits)
    # validate contiguous
    cur = 0
    for s, e, _ in marks:
        assert e > s and s == cur and s % FRAME == 0 and e % FRAME == 0
        cur = e
    assert cur == SONG_END
    write_xsq(marks)
    write_audition(hits)
    print(f'WROTE {OUT_XSQ} ({sum(1 for *_, lab in marks if lab == "P")} P marks)')


if __name__ == '__main__':
    main()
