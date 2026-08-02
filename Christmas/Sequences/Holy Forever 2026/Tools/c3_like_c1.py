"""Final Chorus (C3): make it look like Chorus 1.

User ask (2026-08-02): "On the final chours, let's make it look like the
first chours. We can edit more later." Same message: "I made some edits...
Don't undo them." — the user's hand edits are a VU Meter on
`GE Merry Christmas/Christ` L1 (181550-233025, PC2) plus a cosmetic GUI
re-serialize of the Christ L0 marquee tail (178925-180600). Both are
outside the C3 window and this script does not go near them (verified).

C3 window = 233925 (Mood Climax downbeat) -> 287275 (Afterglow downbeat —
same boundary the approved blue House Outline marquee uses). 53350 ms, so
motion totals reuse the C2 rounded values (window within 0.05% of C2's).

The C1 look, reproduced with the ORIGINAL C1 colors (no C2 red/blue swap):
  - BEDS (40 effects): the same source set as c2_ramp_color_swap.py (live
    67275-127275 effects still carry the approved C1 palettes), re-added
    233925-287275. Each keeps its live Fadein (2, or 2.5 for the Rosa Outer
    Ball) and gets Fadeout=2 — the C1 section convention.
  - MEGA TREE CROSS: new L1 Pictures 233925-287275, plain white palette
    (the C2 swell value curve stripped), Fadein=2/Fadeout=2 — C1 had no VC.
  - MARQUEES (5 targets): ONE continuous segment per target like C1 had
    (no per-bar flips — those were a V2 invention), Reverse=0, Fadein=2,
    Fadeout=2. Amber house marquees + white Christ.
  - ARCHES: the live C1 pattern — ~6650 ms alternating chase tiles, rot 2,
    starting Right-Left like C1's first tile (68975). 8 tiles from 233925
    (last extended 150 ms to land on 287275), Fadein=2 on the first,
    Fadeout=2 on the last. L1 Off underlay re-added.
  - OFFS: GE Merry Christmas sign blackout + Arches L1 Off.
  - Toni cross returns white; Tree Topper amber sparkle star; Whole Scene
    blue/amber aurora — all as C1 had them.

NOT touched: House Outline (8 climax flashes + subtle blue marquee stay),
Mini Grand cross + per-bar rings, all faces, the user's Christ VU meter,
Tree Topper L1/L2 pops, everything in PC2.

Run in Slot B (XLIGHTS_API_PORT=49914), sequence open:
    python3 c3_like_c1.py [--dry-run]
Revert: git checkout the .xsq (or the .bak-before-c3-like-c1 backup).
"""
import shutil
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-b/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-b/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
SEQ_LEN = 308314

C1_START = 67275
V2_END = 127275
C3_START = 233925         # Mood Climax downbeat
C3_END = 287275           # Mood Afterglow downbeat
FADEOUT = '2'

# same set as the C2 restore (minus none) — sources are the live
# 67275-127275 effects, which still carry the original C1 palettes
RESTORE = [
    ('Whole Scene', None, 0, 'Shader', None),
    ('Windows', None, 1, 'Color Wash', None),
    ('Icicles GRP', None, 1, 'Color Wash', None),
    ('Icicles GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '6.0'}),
    ('Yard Borders', None, 1, 'Color Wash', None),
    ('Verts', None, 1, 'Color Wash', None),
    ('Roof', None, 1, 'Color Wash', None),
    ('GE Merry Christmas', 'Christ', 1, 'Color Wash', None),
    ('GE MOAW GRP', None, 0, 'Pinwheel', None),
    ('GE MOAW GRP', None, 1, 'Pinwheel', None),
    ('GE MOAW Snowflake Spoke GRP', None, 0, 'Galaxy',
     {'E_SLIDER_Galaxy_Revolutions': '1440', 'E_SLIDER_Galaxy_Duration': '8'}),
    ('GE MOAW Spokes GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '2.8'}),
    ('GE MOAW Swag GRP', None, 0, 'Bars',
     {'E_TEXTCTRL_Bars_Cycles': '4.0'}),
    ('GE MOAW Diamonds GRP', None, 0, 'Color Wash',
     {'E_TEXTCTRL_ColorWash_Cycles': '4.0'}),
    ('GE Rosa Grande GRP', None, 0, 'Pinwheel', None),
    ('GE Rosa Grande GRP', None, 1, 'Pinwheel', None),
    ('GE Rosa Grande Torch Long Even GRP', None, 0, 'Pinwheel', None),
    ('GE Rosa Grande Feather Long Odd GRP', None, 0, 'Spirals',
     {'E_TEXTCTRL_Spirals_Movement': '8'}),
    ('GE Rosa Grande Outer Ball GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '16'}),
    ('GE Rosa Grande Spoke GRP', None, 0, 'Fan',
     {'E_SLIDER_Fan_Revolutions': '1440'}),
    ('GE Starlord GRP', None, 0, 'Fan',
     {'E_SLIDER_Fan_Revolutions': '1440'}),
    ('GE Starlord GRP', None, 1, 'Pinwheel', None),
    ('GE Starlord GRP', None, 2, 'Pinwheel', None),
    ('GE Starlord Cross GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '11.0'}),
    ('GE Starlord Plunger All GRP', None, 0, 'Spirals',
     {'E_TEXTCTRL_Spirals_Movement': '4.0'}),
    ('GE Starlord Spoke GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '8'}),
    ('GE Reel Max GRP', None, 0, 'Pinwheel', None),
    ('GE Reel Max GRP', None, 1, 'Pinwheel', None),
    ('GE Reel Max Chevrons GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '8'}),
    ('GE Reel Max Circles Outer GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '16'}),
    ('GE Reel Max Kites GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '6.0'}),
    ('GE Reel Max Spokes GRP', None, 0, 'Spirals',
     {'E_TEXTCTRL_Spirals_Movement': '8'}),
    ('Candy Cane - 1', None, 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '16'}),
    ('Candy Cane - 2', None, 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '16'}),
    ('Candy Cane - 3', None, 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '16'}),
    ('Candy Cane - 4', None, 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '16'}),
    ('Mega Tree', None, 2, 'Shader', None),
    ('Toni - Flat Tree', None, 1, 'Pictures', None),
    ('Toni - Flat Tree', None, 2, 'Shader', None),
    ('Tree Topper', None, 3, 'On', None),
]

OFFS = [
    ('GE Merry Christmas', None, 0, 'Off'),
    ('Arches - All', None, 1, 'Off'),
]

MARQUEES = [
    ('Verts', None),
    ('Roof', None),
    ('Windows', None),
    ('Yard Borders', None),
    ('GE Merry Christmas', 'Christ'),
]

ARCH = ('Arches - All', None, 0, 'SingleStrand')
ARCH_BASE = (82275, 88925)      # a clean mid-C1 tile (R-L, rot 2, no fades)
ARCH_TILE = 6650
ARCH_ROT = '2'

# user's hand edits (2026-08-02 ~13:16) — asserted present + untouched
USER_VU = ('GE Merry Christmas', 'Christ', 1, 'VU Meter', 181550, 233025)
USER_TAIL = ('GE Merry Christmas', 'Christ', 0, 'Marquee', 178925, 180600)


def parse(settings):
    return dict(kv.split('=', 1) for kv in settings.split(',') if '=' in kv)


def fmt(d):
    return ','.join(f'{k}={v}' for k, v in d.items())


def find_layer(el, sub, layer_i):
    if sub is None:
        layers = el.findall('EffectLayer')
        assert layer_i < len(layers), f'{el.get("name")}: no L{layer_i}'
        return layers[layer_i]
    for sml in el.findall('SubModelEffectLayer'):
        if sml.get('name') == sub and int(sml.get('layer') or 0) == layer_i:
            return sml
    raise SystemExit(f'{el.get("name")}/{sub}: submodel L{layer_i} not found')


def api_target(owner, sub):
    return f'{owner}/{sub}' if sub else owner


def main():
    dry = '--dry-run' in sys.argv

    tree = ET.parse(XSQ)
    root = tree.getroot()
    db = [t.text or '' for t in root.find('EffectDB').findall('Effect')]
    pals = [t.text or '' for t in root.find('ColorPalettes').findall('ColorPalette')]
    elements = {el.get('name'): el
                for el in root.find('ElementEffects').findall('Element')}

    readds = []

    def grab(owner, sub, layer_i, name, start, end):
        layer = find_layer(elements[owner], sub, layer_i)
        for e in layer.findall('Effect'):
            if (e.get('name') == name and int(e.get('startTime')) == start
                    and int(e.get('endTime')) == end):
                sett = parse(db[int(e.get('ref'))])
                pal = pals[int(e.get('palette'))] if e.get('palette') else ''
                return layer, sett, pal
        raise SystemExit(f'not found: {api_target(owner, sub)} L{layer_i} '
                         f'{name} {start}-{end}')

    def assert_clear(owner, sub, layer_i):
        layer = find_layer(elements[owner], sub, layer_i)
        for e in layer.findall('Effect'):
            es, ee = int(e.get('startTime')), int(e.get('endTime'))
            assert ee <= C3_START or es >= C3_END, \
                f'{api_target(owner, sub)} L{layer_i} collision: ' \
                f'{e.get("name")} {es}-{ee}'

    # user's hand edits must be present before we touch anything
    grab(*USER_VU)
    grab(*USER_TAIL)

    # beds
    for owner, sub, li, name, totals in RESTORE:
        layer, sett, pal = grab(owner, sub, li, name, C1_START, V2_END)
        assert_clear(owner, sub, li)
        if totals:
            for k, v in totals.items():
                assert k in sett, f'{owner}: {k} missing'
                sett[k] = v
        sett['T_TEXTCTRL_Fadeout'] = FADEOUT      # Fadein kept as live (C1)
        readds.append((api_target(owner, sub), li, name, fmt(sett), pal,
                       C3_START, C3_END))
    print(f'beds: {len(RESTORE)} effects re-added {C3_START}-{C3_END} '
          f'with original C1 palettes')

    # mega tree cross — new plain-white L1 Pictures (strip the C2 swell VC)
    layer, sett, pal = grab('Mega Tree', None, 1, 'Pictures', C1_START, 180600)
    assert_clear('Mega Tree', None, 1)
    pal = ','.join(p for p in pal.split(',')
                   if not p.startswith('C_VALUECURVE_Brightness'))
    readds.append(('Mega Tree', 1, 'Pictures', fmt(sett), pal,
                   C3_START, C3_END))
    print('cross: Mega Tree L1 Pictures re-added plain white')

    # offs
    for owner, sub, li, name in OFFS:
        layer, sett, pal = grab(owner, sub, li, name, C1_START, V2_END)
        assert_clear(owner, sub, li)
        readds.append((api_target(owner, sub), li, name, fmt(sett), pal,
                       C3_START, C3_END))
    print(f'offs: {len(OFFS)} masks re-added')

    # marquees — one continuous segment per target, like C1
    for owner, sub in MARQUEES:
        # base = the C1 piece (67275-95600, Reverse=0, Fadein=2)
        layer, sett, pal = grab(owner, sub, 0, 'Marquee', C1_START, 95600)
        assert_clear(owner, sub, 0)
        assert sett.get('E_CHECKBOX_Marquee_Reverse') == '0'
        sett['T_TEXTCTRL_Fadeout'] = FADEOUT
        readds.append((api_target(owner, sub), 0, 'Marquee', fmt(sett), pal,
                       C3_START, C3_END))
    print(f'marquees: {len(MARQUEES)} continuous segments (no flips, like C1)')

    # arches — 8 alternating tiles from C3_START, R-L first like C1
    owner, sub, li, name = ARCH
    layer, sett, pal = grab(owner, sub, li, name, *ARCH_BASE)
    assert_clear(owner, sub, li)
    sett.pop('T_TEXTCTRL_Fadein', None)
    sett.pop('T_TEXTCTRL_Fadeout', None)
    tiles = []
    t = C3_START
    while t + ARCH_TILE <= C3_END:
        tiles.append((t, t + ARCH_TILE))
        t += ARCH_TILE
    if C3_END - t < 500:                 # absorb a tiny stub (150 ms here)
        tiles[-1] = (tiles[-1][0], C3_END)
    elif t < C3_END:
        tiles.append((t, C3_END))
    for i, (s, en) in enumerate(tiles):
        d = dict(sett)
        d['E_CHOICE_Chase_Type1'] = 'Right-Left' if i % 2 == 0 else 'Left-Right'
        d['E_TEXTCTRL_Chase_Rotations'] = ARCH_ROT
        if i == 0:
            d['T_TEXTCTRL_Fadein'] = '2'
        if i == len(tiles) - 1:
            d['T_TEXTCTRL_Fadeout'] = FADEOUT
        readds.append((api_target(owner, sub), li, name, fmt(d), pal, s, en))
    print(f'arches: {len(tiles)} chase tiles {tiles[0][0]}-{tiles[-1][1]}, '
          f'R-L first like C1')

    if dry:
        print('dry-run: no writes')
        return

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info
    x.save(XSQ)
    shutil.copy(XSQ, XSQ + '.bak-before-c3-like-c1')

    for target, li, name, sett, pal, s, en in readds:
        x.add_effect(target, li, name, sett, pal, s, en)
    print(f'added {len(readds)} effects via API')

    x.save(XSQ)

    # ---- verify from the saved file
    root2 = ET.parse(XSQ).getroot()
    db2 = [t.text or '' for t in root2.find('EffectDB').findall('Effect')]
    pals2 = [t.text or '' for t in root2.find('ColorPalettes').findall('ColorPalette')]
    elements2 = {el.get('name'): el
                 for el in root2.find('ElementEffects').findall('Element')}

    def effects_in_window(owner, sub, layer_i):
        layer = find_layer(elements2[owner], sub, layer_i)
        return sorted(
            (int(e.get('startTime')), int(e.get('endTime')), e)
            for e in layer.findall('Effect')
            if int(e.get('endTime')) > C3_START
            and int(e.get('startTime')) < C3_END)

    for owner, sub, li, name, totals in RESTORE:
        wins = effects_in_window(owner, sub, li)
        assert len(wins) == 1 and wins[0][0] == C3_START \
            and wins[0][1] == C3_END, (owner, li, [(w[0], w[1]) for w in wins])
        sett = parse(db2[int(wins[0][2].get('ref'))])
        assert sett.get('T_TEXTCTRL_Fadeout') == FADEOUT, (owner, sett)
    print(f'verified beds: {len(RESTORE)}')

    wins = effects_in_window('Mega Tree', None, 1)
    assert len(wins) == 1 and wins[0][0] == C3_START and wins[0][1] == C3_END
    pal = pals2[int(wins[0][2].get('palette'))]
    assert 'VALUECURVE' not in pal and '#FFFFFF' in pal.upper(), pal
    print('verified mega tree cross (plain white)')

    for owner, sub in MARQUEES:
        wins = effects_in_window(owner, sub, 0)
        assert len(wins) == 1 and wins[0][0] == C3_START \
            and wins[0][1] == C3_END, (owner, [(w[0], w[1]) for w in wins])
        d = parse(db2[int(wins[0][2].get('ref'))])
        assert d.get('E_CHECKBOX_Marquee_Reverse') == '0'
        assert d.get('T_TEXTCTRL_Fadeout') == FADEOUT
    print('verified marquees: 5 continuous segments')

    wins = effects_in_window('Arches - All', None, 0)
    assert len(wins) == len(tiles), len(wins)
    dirs = ''.join('L' if parse(db2[int(e.get('ref'))])['E_CHOICE_Chase_Type1']
                   == 'Left-Right' else 'R' for _, _, e in wins)
    assert dirs == 'RLRLRLRL', dirs
    print(f'verified arches: {len(wins)} tiles, directions {dirs}')

    # user's hand edits + C3 climax features still present, untouched
    for chk in (USER_VU, USER_TAIL):
        owner, sub, li, name, s, en = chk
        layer = find_layer(elements2[owner], sub, li)
        assert any(e.get('name') == name
                   and int(e.get('startTime')) == s
                   and int(e.get('endTime')) == en
                   for e in layer.findall('Effect')), f'user edit lost: {chk}'
    ho = find_layer(elements2['House Outline'], None, 0)
    assert sum(1 for e in ho.findall('Effect')
               if 233000 <= int(e.get('startTime')) <= 234800) == 8
    ho1 = find_layer(elements2['House Outline'], None, 1)
    assert any(e.get('name') == 'Marquee'
               and int(e.get('startTime')) == 234225
               for e in ho1.findall('Effect'))
    print('verified: user VU meter + Christ tail + House Outline climax '
          'features untouched')
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
