"""Split singers onto per-voice lyric tracks + dress the ChromaBulbs.

1. Imports the rebuilt 3-track template (Lyrics Lead / Female / Choir).
2. Re-points every existing Faces effect at its singer's voice track.
3. Lights each Singing Bulb during its choir blocks: amber base + red/green/blue
   glass (Left/Center/Right), mirroring the face block spans and fades.

Old 'Lyrics 1' track is left in place (no API delete) - remove in the GUI.
Not saved, not rendered.
"""
import json
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

TEMPLATE = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Christmas/Sequences/Holy Forever 2026/Timing Templates/Holy Forever Lyrics.xsq'
SECTIONS = json.load(open('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Tools/sections.json'))

VOICE = {
    'GE 8ft Snowman Singing': 'Lyrics Lead',
    'EFL Teddy': 'Lyrics Female',
    'Singing Bulb - Left': 'Lyrics Choir',
    'Singing Bulb - Center': 'Lyrics Choir',
    'Singing Bulb - Right': 'Lyrics Choir',
    'GE Santa Singing': 'Lyrics Choir',
    'GE Grinch Talk': 'Lyrics Choir',
    'SingingTree': 'Lyrics Choir',
    'Toni - Penguin 1': 'Lyrics Choir',
    'Toni - Penguin 2': 'Lyrics Choir',
}

# prop -> (base submodel, glass submodel, glass color)
BULBS = {
    'Singing Bulb - Left': ('Bulb Stem', 'Bulb Outline', '#FF0000'),
    'Singing Bulb - Center': ('Base', 'Bulb', '#00FF00'),
    'Singing Bulb - Right': ('Bulb Stem', 'Bulb Outline', '#0000FF'),
}
AMBER = '#FFC800'

def pal(color):
    return f'C_BUTTON_Palette1={color},C_CHECKBOX_Palette1=1'

def sec(name):
    s = SECTIONS[name]
    return int(s['s']), int(s['e'])

def choir_bulb_blocks():
    """Identical spans/caps to the bulbs' face blocks in place_faces.py."""
    c1s, c1e = sec('C1')
    c2s, _ = sec('C2a'); _, c2e = sec('C2c')
    pcbs, _ = sec('PC2b'); _, c3e = sec('C3c')
    raw = [(c1s, c1e), (c2s, c2e), (pcbs, c3e)]
    out = []
    for k, (s, e) in enumerate(raw):
        last = k == len(raw) - 1
        e += 1500 if last else 300
        if not last:
            e = min(e, raw[k + 1][0])
        out.append((s, e, last))
    return out

def repoint_faces():
    n = 0
    for el, track in VOICE.items():
        ids = x.xl('getEffectIDs', model=el)['effects']
        for layer, layer_ids in enumerate(ids):
            for eid in layer_ids:
                eff = x.xl('getEffectSettings', model=el, layer=str(layer), id=str(eid))
                if eff.get('name') != 'Faces':
                    continue
                st = dict(eff['settings'])
                st['E_CHOICE_Faces_TimingTrack'] = track
                palette = dict(eff['palette'])
                if el in BULBS:   # tint bulb face (outline/mouth/eyes) to its glass color
                    palette['C_BUTTON_Palette1'] = BULBS[el][2]
                    palette['C_CHECKBOX_Palette1'] = '1'
                x.xl('setEffectSettings', model=el, layer=str(layer), id=str(eid),
                     name='Faces', settings=st, palette=palette,
                     startTime=eff['startTime'], endTime=eff['endTime'])
                n += 1
        print(f'  {el} -> {track}')
    return n

def dress_bulbs():
    blocks = choir_bulb_blocks()
    targets = [(f'{prop}/{sm}', col)
               for prop, (base_sm, glass_sm, color) in BULBS.items()
               for sm, col in ((base_sm, AMBER), (glass_sm, color))]
    missing = [t for t, _ in targets if not x.element_exists(t)]
    if missing:
        raise SystemExit(f'submodels not addressable: {missing}')
    n = 0
    for target, col in targets:
        for s, e, last in blocks:
            settings = 'T_TEXTCTRL_Fadeout=1.5' if last else ''
            x.add_effect(target, 0, 'On', settings, pal(col), s, e)
            n += 1
        print(f'  {target}: {col}')
    return n

def main():
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence open: {info}'
    print('importing 3-voice timing template...')
    x.import_timings(TEMPLATE)
    nf = repoint_faces()
    nb = dress_bulbs()
    print(f'done: {nf} faces re-pointed, {nb} bulb color effects added '
          '(not saved, not rendered)')

if __name__ == '__main__':
    main()
