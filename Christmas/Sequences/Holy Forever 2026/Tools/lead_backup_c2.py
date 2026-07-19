"""Snowman backs up Teddy on chorus 2's female feature (C2b).

Rebuilds Snowman faces only: chorus 2 becomes one continuous face block
(C2a–C2c). During C2b the effect points at Lyrics Female so he mouths the
same lines as Teddy; C2a/C2c stay on Lyrics Lead.

Also refreshes the on-disk timing template so Lyrics Lead includes C2b
(for future rebuilds). Does NOT re-import (would duplicate marks).

Not saved, not rendered.
"""
import subprocess
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import json
import xlights_api as x

SECTIONS = json.load(open('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/sections.json'))
EMPTY = 'House'
EL = 'GE 8ft Snowman Singing'
DEFN, STATE = '8ft Snowman Singing', 'Colored'
WHITE = 'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'

def sec(name):
    s = SECTIONS[name]
    return int(s['s']), int(s['e'])

def line(section, needle):
    for L in SECTIONS[section]['lines']:
        if needle.lower() in L['text'].lower():
            return int(L['s']), int(L['e'])
    raise KeyError(needle)

def face(track, fadeout=None):
    s = ('E_CHECKBOX_Faces_Outline=1,E_CHOICE_Faces_EyeBlinkFrequency=Normal,'
         'E_CHOICE_Faces_Eyes=Auto,'
         f'E_CHOICE_Faces_FaceDefinition={DEFN},E_CHOICE_Faces_TimingTrack={track},'
         f'E_CHOICE_Faces_UseState={STATE}')
    if fadeout:
        s += f',T_TEXTCTRL_Fadeout={fadeout}'
    return s

def main():
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info

    print('refreshing on-disk Lyrics Lead template (includes C2b)...')
    subprocess.check_call([sys.executable,
                           '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/build_lyrics.py'])

    v1s, _ = sec('V1'); _, c1e = sec('C1')
    amen_s, _ = line('V2', "We'll sing the song forever and amen")
    _, v2e = sec('V2')
    c2a_s, c2a_e = sec('C2a')
    c2b_s, c2b_e = sec('C2b')
    c2c_s, c2c_e = sec('C2c')
    pc2a_s, _ = sec('PC2a'); _, c3e = sec('C3c')
    outs, oute = sec('OUT')

    # (start, end, timing track) — C2b backs up on Lyrics Female
    blocks = [
        (v1s, c1e, 'Lyrics Lead'),
        (amen_s, v2e, 'Lyrics Lead'),
        (c2a_s, c2a_e, 'Lyrics Lead'),
        (c2b_s, c2b_e, 'Lyrics Female'),   # backup with Teddy
        (c2c_s, c2c_e, 'Lyrics Lead'),
        (pc2a_s, c3e, 'Lyrics Lead'),
        (outs, oute, 'Lyrics Lead'),
    ]

    print(f'wiping and rebuilding {EL}...')
    x.xl('cloneModelEffects', target=EL, source=EMPTY, eraseModel='true')
    for k, (s, e, track) in enumerate(blocks):
        last = k == len(blocks) - 1
        s, e = int(s), int(e) + (1500 if last else 300)
        if not last:
            e = min(e, int(blocks[k + 1][0]))
        x.add_effect(EL, 0, 'Faces', face(track, 1.5 if last else None), WHITE, s, e)
        print(f'  {s}-{e}  track={track}')

    ids = x.xl('getEffectIDs', model=EL)['effects'][0]
    assert len(ids) == 7, ids
    backup = x.xl('getEffectSettings', model=EL, layer='0', id=ids[3])
    assert backup['settings']['E_CHOICE_Faces_TimingTrack'] == 'Lyrics Female', backup
    print('done: Snowman backs up Teddy on C2b (not saved)')

if __name__ == '__main__':
    main()
