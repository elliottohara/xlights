"""Import the Lyrics 1 timing track and place singing-face effects.

Casting (Holy Forever 2026):
  Snowman  = Chris Tomlin lead:   V1 + PC1 + C1, 'amen' line of V2, C2 first
             half + 'You will always be holy', both pre-choruses, final chorus,
             outro tag (solo).
  Teddy    = Jenn Johnson female lead: V2, 'Hear Your people sing...' half of
             C2, both pre-choruses, final chorus.
  Bulbs    = choir: choruses (C1 on), second pre-chorus pass, final chorus.
  Santa/Grinch/SingingTree = join at the big double pre-chorus (pass 1).
  Penguins = join on pre-chorus pass 2.
  Everyone sings the final chorus.

Not saved, not rendered.
"""
import json
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

TEMPLATE = '/Users/elliott.ohara/xlights/Timing Templates/Holy Forever Lyrics.xsq'
SECTIONS = json.load(open('/Users/elliott.ohara/xlights/Tools/tmp_holy/sections.json'))

def sec(name):
    s = SECTIONS[name]
    return int(s['s']), int(s['e'])

def line(section, needle):
    for L in SECTIONS[section]['lines']:
        if needle.lower() in L['text'].lower():
            return int(L['s']), int(L['e'])
    raise KeyError(f'{needle} not in {section}')

def face(defn, state=None, fadeout=None):
    s = ('E_CHECKBOX_Faces_Outline=1,E_CHOICE_Faces_EyeBlinkFrequency=Normal,'
         'E_CHOICE_Faces_Eyes=Auto,'
         f'E_CHOICE_Faces_FaceDefinition={defn},E_CHOICE_Faces_TimingTrack=Lyrics 1')
    if state:
        s += f',E_CHOICE_Faces_UseState={state}'
    if fadeout:
        s += f',T_TEXTCTRL_Fadeout={fadeout}'
    return s

WHITE = 'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'

SINGERS = {
    'GE 8ft Snowman Singing': ('8ft Snowman Singing', 'Colored'),
    'EFL Teddy': ('Teddy ', 'Teddy RedBow static'),
    'GE Santa Singing': ('Santa Singing', 'hat'),
    'GE Grinch Talk': ('Grinch', None),
    'SingingTree': ('Tree', None),
    'Toni - Penguin 1': ('Penguin v.1.1 - No Tongue', None),
    'Toni - Penguin 2': ('Penguin v.1.1 - No Tongue', None),
    'Singing Bulb - Left': ('Boscoyo ChromaBulb Face', None),
    'Singing Bulb - Center': ('Boscoyo ChromaBulb Face', None),
    'Singing Bulb - Right': ('Boscoyo ChromaBulb Face', None),
}

def spans():
    v1s, _ = sec('V1'); _, c1e = sec('C1')
    v2s, v2e = sec('V2')
    amen_s, _ = line('V2', "We'll sing the song forever and amen")
    c2a_s, c2a_e = sec('C2a'); c2b_s, _ = sec('C2b'); c2c_s, c2c_e = sec('C2c')
    pc2a_s, _ = sec('PC2a'); pc2b_s, _ = sec('PC2b')
    _, c3e = sec('C3c')
    outs, oute = sec('OUT')

    lead = [(v1s, c1e), (amen_s, v2e), (c2a_s, c2a_e), (c2c_s, c2c_e),
            (pc2a_s, c3e), (outs, oute)]
    female = [(v2s, v2e), (c2b_s, c2c_e), (pc2a_s, c3e)]
    choir = [(sec('C1')), (c2a_s, c2c_e), (pc2b_s, c3e)]
    joiners1 = [(pc2a_s, c3e)]     # santa, grinch, singing tree
    joiners2 = [(pc2b_s, c3e)]     # penguins

    return {
        'GE 8ft Snowman Singing': lead,
        'EFL Teddy': female,
        'Singing Bulb - Left': choir,
        'Singing Bulb - Center': choir,
        'Singing Bulb - Right': choir,
        'GE Santa Singing': joiners1,
        'GE Grinch Talk': joiners1,
        'SingingTree': joiners1,
        'Toni - Penguin 1': joiners2,
        'Toni - Penguin 2': joiners2,
    }

def main():
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence open: {info}'

    print('importing timing template...')
    x.import_timings(TEMPLATE)

    n = 0
    for el, blocks in spans().items():
        defn, state = SINGERS[el]
        blocks = sorted(blocks)
        for k, (s, e) in enumerate(blocks):
            last = k == len(blocks) - 1
            # tail lets the mouth close on 'rest'; last block fades out after it
            s, e = int(s), int(e) + (1500 if last else 300)
            if not last:                         # never overlap the next block
                e = min(e, int(blocks[k + 1][0]))
            x.add_effect(el, 0, 'Faces', face(defn, state, 1.5 if last else None),
                         WHITE, s, e)
            n += 1
        print(f'  {el}: {len(blocks)} face blocks')
    print(f'done: {n} face effects (not saved, not rendered)')

if __name__ == '__main__':
    main()
