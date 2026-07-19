"""Canonical wipe-and-rebuild of ALL singing-face effects for Holy Forever 2026.

Reproduces the reviewed live state. Prereq: the sequence already contains the
timing tracks 'Lyrics 1' (full lyric) and 'Lyrics Lead/Female/Choir' (imported
ONCE from Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Lyrics.xsq). Do not re-import over
existing tracks (mark duplication risk).

Casting:
  Snowman = Tomlin lead. Verse 2 through chorus 2 is ONE block on 'Lyrics 1'
            so he sings WITH Teddy from her 1:34 entrance and backs her up on
            the female feature (in-sequence 'Lyrics Lead' lacks the V2/C2b
            phrases; 'Lyrics 1' has everything).
  Teddy   = Jenn Johnson: V2, C2b+C2c, both pre-choruses, final chorus.
  Bulbs   = choir from chorus 1; Santa/Grinch/SingingTree join at PC2a;
            Penguins at PC2b; everyone sings the final chorus.

Bulb C9 look is done entirely by the Faces palette (no submodel effects).
With CustomColors=0 the Faces effect maps checked palette colors in order to
mouth, eyes, FaceOutline (glass), FaceOutline2 (base) - verified in
FacesEffect.cpp. So bulbs get: white mouth/eyes, R/G/B glass, amber base.
This script also wipes any legacy On effects off the bulb submodels.

Why wipe+re-add: setEffectSettings mangles values (see AGENTS.md) - the only
safe effect edit is cloneModelEffects(eraseModel) from an effect-free element
then addEffect.

Not saved, not rendered.
"""
import json
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

SECTIONS = json.load(open('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/sections.json'))
EMPTY_SOURCE = 'House'          # element with a single empty effect layer

def sec(name):
    s = SECTIONS[name]
    return int(s['s']), int(s['e'])

def line(section, needle):
    for L in SECTIONS[section]['lines']:
        if needle.lower() in L['text'].lower():
            return int(L['s']), int(L['e'])
    raise KeyError(f'{needle} not in {section}')

#            element:               (definition, state, default voice track)
SINGERS = {
    'GE 8ft Snowman Singing': ('8ft Snowman Singing', 'Colored', 'Lyrics Lead'),
    # Teddy is the ONE face that keeps its forced colors (brown mouth, blue/brown
    # eyes) per user preference - everyone else renders white mouth/eyes.
    # ('No Forced Colors' = identical nodes rendering white, if ever wanted.)
    'EFL Teddy': ('Teddy ', 'Teddy RedBow static', 'Lyrics Female'),
    'GE Santa Singing': ('Santa Singing', 'hat', 'Lyrics Choir'),
    'GE Grinch Talk': ('Grinch', None, 'Lyrics Choir'),
    'SingingTree': ('Tree', None, 'Lyrics Choir'),
    'Toni - Penguin 1': ('Penguin v.1.1 - No Tongue', None, 'Lyrics Choir'),
    'Toni - Penguin 2': ('Penguin v.1.1 - No Tongue', None, 'Lyrics Choir'),
    'Singing Bulb - Left': ('Boscoyo ChromaBulb Face', None, 'Lyrics Choir'),
    'Singing Bulb - Center': ('Boscoyo ChromaBulb Face', None, 'Lyrics Choir'),
    'Singing Bulb - Right': ('Boscoyo ChromaBulb Face', None, 'Lyrics Choir'),
}

AMBER = '#FFC800'
BULB_GLASS = {
    'Singing Bulb - Left': '#FF0000',
    'Singing Bulb - Center': '#00FF00',
    'Singing Bulb - Right': '#0000FF',
}
# legacy targets from the submodel-On approach; kept clean by this script
BULB_SUBMODELS = [
    'Singing Bulb - Left/Bulb Stem', 'Singing Bulb - Left/Bulb Outline',
    'Singing Bulb - Center/Base', 'Singing Bulb - Center/Bulb',
    'Singing Bulb - Right/Bulb Stem', 'Singing Bulb - Right/Bulb Outline',
]

def palette_for(el):
    """Faces palette. Order (CustomColors=0): mouth, eyes, outline, outline2."""
    if el in BULB_GLASS:
        cols = ['#FFFFFF', '#FFFFFF', BULB_GLASS[el], AMBER]
        return ','.join(
            [f'C_BUTTON_Palette{i}={c}' for i, c in enumerate(cols, 1)] +
            [f'C_CHECKBOX_Palette{i}=1' for i in range(1, len(cols) + 1)])
    return 'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'

def face_settings(defn, state, track, fadeout=None):
    s = ('E_CHECKBOX_Faces_Outline=1,E_CHOICE_Faces_EyeBlinkFrequency=Normal,'
         'E_CHOICE_Faces_Eyes=Auto,'
         f'E_CHOICE_Faces_FaceDefinition={defn},E_CHOICE_Faces_TimingTrack={track}')
    if state:
        s += f',E_CHOICE_Faces_UseState={state}'
    if fadeout:
        s += f',T_TEXTCTRL_Fadeout={fadeout}'
    return s

def spans():
    """blocks per singer: (start, end) or (start, end, track_override)"""
    v1s, _ = sec('V1'); _, c1e = sec('C1')
    v2s, v2e = sec('V2')
    c2a_s, _ = sec('C2a'); c2b_s, _ = sec('C2b'); _, c2c_e = sec('C2c')
    pc2a_s, _ = sec('PC2a'); pc2b_s, _ = sec('PC2b')
    _, c3e = sec('C3c')
    outs, oute = sec('OUT')

    lead = [(v1s, c1e),
            (v2s, c2c_e, 'Lyrics 1'),        # V2 + chorus 2 = duet with Teddy
            (pc2a_s, c3e), (outs, oute)]
    female = [(v2s, v2e), (c2b_s, c2c_e), (pc2a_s, c3e)]
    choir = [sec('C1'), (c2a_s, c2c_e), (pc2b_s, c3e)]
    joiners1 = [(pc2a_s, c3e)]
    joiners2 = [(pc2b_s, c3e)]

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

    src = x.xl('getEffectIDs', model=EMPTY_SOURCE)['effects']
    assert all(not l for l in src), f'{EMPTY_SOURCE} is not effect-free: {src}'

    # clear legacy submodel On effects (base/glass now come from the Faces palette)
    for sm in BULB_SUBMODELS:
        x.xl('cloneModelEffects', target=sm, source=EMPTY_SOURCE, eraseModel='true')
        left = x.xl('getEffectIDs', model=sm)['effects']
        assert all(not l for l in left), f'{sm} still has effects: {left}'
    print(f'  bulb submodels cleared: {len(BULB_SUBMODELS)}')

    n = 0
    expected = {}          # el -> [(s, e, track)] for verification
    for el, blocks in spans().items():
        defn, state, deftrack = SINGERS[el]
        blocks = sorted((b[0], b[1], b[2] if len(b) > 2 else deftrack) for b in blocks)
        x.xl('cloneModelEffects', target=el, source=EMPTY_SOURCE, eraseModel='true')
        pal = palette_for(el)
        final = []
        for k, (s, e, track) in enumerate(blocks):
            last = k == len(blocks) - 1
            s, e = int(s), int(e) + (1500 if last else 300)
            if not last:
                e = min(e, int(blocks[k + 1][0]))
            x.add_effect(el, 0, 'Faces',
                         face_settings(defn, state, track, 1.5 if last else None),
                         pal, s, e)
            final.append((s, e, track))
            n += 1
        expected[el] = final
        print(f'  {el}: wiped, {len(final)} faces '
              f'({", ".join(sorted(set(t for _, _, t in final)))})')

    print('verifying...')
    bad = []
    for el, (defn, state, _) in SINGERS.items():
        glass = BULB_GLASS.get(el)
        ids = x.xl('getEffectIDs', model=el)['effects'][0]
        got = []
        for eid in ids:
            e = x.xl('getEffectSettings', model=el, layer='0', id=str(eid))
            st, p = e['settings'], e['palette']
            got.append((int(e['startTime']), int(e['endTime']),
                        st.get('E_CHOICE_Faces_TimingTrack')))
            ok = (e.get('name') == 'Faces'
                  and st.get('E_CHOICE_Faces_FaceDefinition') == defn
                  and st.get('E_CHECKBOX_Faces_Outline') == '1'
                  and (state is None or st.get('E_CHOICE_Faces_UseState') == state))
            if glass:
                ok = ok and (p.get('C_BUTTON_Palette3', '').upper() == glass
                             and p.get('C_BUTTON_Palette4', '').upper() == AMBER
                             and all(p.get(f'C_CHECKBOX_Palette{i}') == '1'
                                     for i in range(1, 5)))
            else:
                ok = ok and p.get('C_BUTTON_Palette1', '').upper() == '#FFFFFF'
            if not ok:
                bad.append((el, eid, st.get('E_CHOICE_Faces_FaceDefinition'), p))
        if sorted(got) != expected[el]:
            bad.append((el, 'blocks', sorted(got), expected[el]))
    if bad:
        for b in bad:
            print('  MISMATCH:', b)
        raise SystemExit('verification failed')
    print(f'done: {n} face effects rebuilt and verified (not saved, not rendered)')

if __name__ == '__main__':
    main()
