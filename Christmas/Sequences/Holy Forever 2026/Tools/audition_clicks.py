"""Mix audible clicks at the extracted kick/snare/cymbal marks over the song.

kick = 80 Hz thump (left-ish low), snare = white-noise burst, cymbal = 6 kHz
ping. Output: Christmas/Sequences/Holy Forever 2026/Tools/holy_drum_audition.wav — listen to verify marks.
"""
import re
import wave

import numpy as np

AUDIO = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/holy_44k.wav'
XSQ = ('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Timing Templates/'
       'Holy Forever Drums and Mood.xsq')
OUT = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/holy_drum_audition.wav'

with wave.open(AUDIO) as w:
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
x = x.astype(np.float64) / 32768.0 * 0.5  # duck the song

text = open(XSQ).read()


def marks(track, label):
    m = re.search(rf'name="{track}">\s*<EffectLayer>(.*?)</EffectLayer>',
                  text, re.S)
    return [int(a) for lab, a in
            re.findall(r'label="([^"]*)" startTime="(\d+)"', m.group(1))
            if lab == label]


def tone(freq, dur_ms, decay_ms):
    n = int(sr * dur_ms / 1000)
    t = np.arange(n) / sr
    env = np.exp(-t / (decay_ms / 1000))
    return np.sin(2 * np.pi * freq * t) * env


def noise(dur_ms, decay_ms):
    n = int(sr * dur_ms / 1000)
    t = np.arange(n) / sr
    rng = np.random.default_rng(1)
    return rng.standard_normal(n) * np.exp(-t / (decay_ms / 1000))


sounds = {
    'Kick': ('K', tone(80, 120, 40) * 0.9),
    'Snare': ('S', noise(90, 25) * 0.5),
    'Cymbals': ('C', tone(6000, 400, 150) * 0.35),
}
y = x.copy()
for track, (label, snd) in sounds.items():
    ts = marks(track, label)
    print(f'{track}: {len(ts)} clicks')
    for tms_ in ts:
        i = int(tms_ * sr / 1000)
        j = min(len(y), i + len(snd))
        y[i:j] += snd[:j - i]

y = np.clip(y, -1, 1)
with wave.open(OUT, 'w') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes((y * 32767).astype(np.int16).tobytes())
print(f'WROTE {OUT}')
