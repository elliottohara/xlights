"""Chorus 2: ramp the V2 look back up with red<->blue swapped; crosses stay.

User ask (2026-08-02): "let's ramp back up to what we had, but where it was
blue, make it red, and where it was red make it blue... just color swap,
except crosses, they stay the same--- all through chorus 2."

C2 window = 127275 (Soaring downbeat, where the V2 blackout landed) ->
180600 (Regather downbeat = end of C2 on the Mood track; the Mega Tree
cross already ends there). Everything that plunged at the end of V2 comes
back:

  - BEDS (41 effects): re-added 127275-180600, Fadein=1.68 (mirrors the
    1.68 plunge) + Fadeout=2 (stock section exit). Motion totals
    (rotations/cycles/revolutions/movement) rescaled x53325/60000 so visible
    speed matches V2. Palettes swapped red<->blue (below).
  - MARQUEES (5 targets): the per-felt-bar direction flips continue through
    C2 — one segment per Beat Count labeled-"3" mark (felt beat 1, see
    v2_marquee_bar_flip.py), alternating Reverse, continuing the V2
    alternation (V2 tail was forward -> first C2 segment reversed). First
    segment Fadein=1.68, last Fadeout=2, the rest fade-free. Amber/white —
    no color change.
  - ARCHES: the alternating ~2-bar SingleStrand chase tiles continue on the
    established 6650 ms phase grid (88950 + 6650n), clipped at both ends,
    rotations proportional (2 per full tile). Amber — unchanged.
  - OFFS: GE Merry Christmas sign blackout + Arches L1 Off underlay,
    re-added 127275-180600.

COLOR SWAP (checked palette slots + gradient stops only): blue family
(hue 190-260) -> hue 0 keeping saturation/lightness; red family (hue <=15
or >=345) -> hue 226 (the show's sapphire) keeping S/L. So sapphire
#2864FF -> #FF2828, navy #0A1E50 -> #500A0A, ice blue #8080FF -> #FF8080,
Rosa red #B01212 -> #1230B0, pure red #FF0000 -> #0028FF. Amber/gold/
white/green and UNCHECKED slots are untouched.

CROSSES STAY: Mega Tree cross (already 67275-180600 with its swell VC) and
the full-song Mini Grand cross are not touched; the Toni cross returns
white (its palette is exempt from the swap). Faces untouched.

Run in Slot B (XLIGHTS_API_PORT=49914), sequence open:
    python3 c2_ramp_color_swap.py [--dry-run]
Revert: git checkout the .xsq (or the .bak-before-c2-color-swap backup).
"""
import colorsys
import re
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
C2_START = 127275
C2_END = 180600           # Mood Regather downbeat
FADEIN = '1.68'           # mirrors the V2-end plunge
FADEOUT = '2'

SAPPHIRE_HUE = 226.0 / 360.0

# (element, submodel|None, layer, name, {motion param: new total} or None,
#  swap palette?)
RESTORE = [
    ('Whole Scene', None, 0, 'Shader', None, True),
    ('Windows', None, 1, 'Color Wash', None, True),
    ('Icicles GRP', None, 1, 'Color Wash', None, True),
    ('Icicles GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '6.0'}, True),
    ('Yard Borders', None, 1, 'Color Wash', None, True),
    ('Verts', None, 1, 'Color Wash', None, True),
    ('Roof', None, 1, 'Color Wash', None, True),
    ('GE Merry Christmas', 'Christ', 1, 'Color Wash', None, True),
    ('GE MOAW GRP', None, 0, 'Pinwheel', None, True),
    ('GE MOAW GRP', None, 1, 'Pinwheel', None, True),
    ('GE MOAW Snowflake Spoke GRP', None, 0, 'Galaxy',
     {'E_SLIDER_Galaxy_Revolutions': '1440', 'E_SLIDER_Galaxy_Duration': '8'}, True),
    ('GE MOAW Spokes GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '2.8'}, True),
    ('GE MOAW Swag GRP', None, 0, 'Bars',
     {'E_TEXTCTRL_Bars_Cycles': '4.0'}, True),
    ('GE MOAW Diamonds GRP', None, 0, 'Color Wash',
     {'E_TEXTCTRL_ColorWash_Cycles': '4.0'}, True),
    ('GE Rosa Grande GRP', None, 0, 'Pinwheel', None, True),
    ('GE Rosa Grande GRP', None, 1, 'Pinwheel', None, True),
    ('GE Rosa Grande Torch Long Even GRP', None, 0, 'Pinwheel', None, True),
    ('GE Rosa Grande Feather Long Odd GRP', None, 0, 'Spirals',
     {'E_TEXTCTRL_Spirals_Movement': '8'}, True),
    ('GE Rosa Grande Outer Ball GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '16'}, True),
    ('GE Rosa Grande Spoke GRP', None, 0, 'Fan',
     {'E_SLIDER_Fan_Revolutions': '1440'}, True),
    ('GE Starlord GRP', None, 0, 'Fan',
     {'E_SLIDER_Fan_Revolutions': '1440'}, True),
    ('GE Starlord GRP', None, 1, 'Pinwheel', None, True),
    ('GE Starlord GRP', None, 2, 'Pinwheel', None, True),
    ('GE Starlord Cross GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '11.0'}, True),
    ('GE Starlord Plunger All GRP', None, 0, 'Spirals',
     {'E_TEXTCTRL_Spirals_Movement': '4.0'}, True),
    ('GE Starlord Spoke GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '8'}, True),
    ('GE Reel Max GRP', None, 0, 'Pinwheel', None, True),
    ('GE Reel Max GRP', None, 1, 'Pinwheel', None, True),
    ('GE Reel Max Chevrons GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '8'}, True),
    ('GE Reel Max Circles Outer GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '16'}, True),
    ('GE Reel Max Kites GRP', None, 0, 'SingleStrand',
     {'E_TEXTCTRL_Chase_Rotations': '6.0'}, True),
    ('GE Reel Max Spokes GRP', None, 0, 'Spirals',
     {'E_TEXTCTRL_Spirals_Movement': '8'}, True),
    ('Candy Cane - 1', None, 0, 'Bars',
     {'E_TEXTCTRL_Bars_Cycles': '16'}, True),
    ('Candy Cane - 2', None, 0, 'Bars',
     {'E_TEXTCTRL_Bars_Cycles': '16'}, True),
    ('Candy Cane - 3', None, 0, 'Bars',
     {'E_TEXTCTRL_Bars_Cycles': '16'}, True),
    ('Candy Cane - 4', None, 0, 'Bars',
     {'E_TEXTCTRL_Bars_Cycles': '16'}, True),
    ('Mega Tree', None, 2, 'Shader', None, True),
    ('Toni - Flat Tree', None, 1, 'Pictures', None, False),   # cross stays white
    ('Toni - Flat Tree', None, 2, 'Shader', None, True),
    ('Tree Topper', None, 3, 'On', None, True),
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
# V2 tile grid: boundaries at 122175 + 6650n (the live V2 segments are
# 88950, 95575, then +6650 — not a clean 6650 grid from 88950). Even n =
# Right-Left (the direction of V2's last tile, 122175-127275).
ARCH_GRID_START = 122175
ARCH_TILE = 6650
ARCH_ROT_PER_TILE = 2.0

HEX = re.compile(r'#([0-9a-fA-F]{6})')


def parse(settings):
    return dict(kv.split('=', 1) for kv in settings.split(',') if '=' in kv)


def fmt(d):
    return ','.join(f'{k}={v}' for k, v in d.items())


def swap_hex(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    deg = hue * 360
    if sat < 0.05:
        return h.upper()
    if 190 <= deg <= 260:
        hue = 0.0                      # blue -> red
    elif deg <= 15 or deg >= 345:
        hue = SAPPHIRE_HUE             # red -> show sapphire
    else:
        return h.upper()               # amber/gold/green — unchanged
    r2, g2, b2 = colorsys.hls_to_rgb(hue, light, sat)
    return '#%02X%02X%02X' % (round(r2 * 255), round(g2 * 255),
                              round(b2 * 255))


def swap_palette(pal):
    """Swap red<->blue in CHECKED slots and their gradient stops."""
    checked = {n: v == '1' for n, v in
               re.findall(r'C_CHECKBOX_Palette(\d+)=(\d)', pal)}
    out = []
    for part in pal.split(','):
        m = re.match(r'C_BUTTON_Palette(\d+)=(.*)', part)
        if m and checked.get(m.group(1)):
            n, val = m.group(1), m.group(2)
            if val.startswith('#'):
                val = swap_hex(val)
            else:                       # gradient: swap each c=# stop
                val = HEX.sub(lambda mm: swap_hex('#' + mm.group(1)), val)
            part = f'C_BUTTON_Palette{n}={val}'
        out.append(part)
    return ','.join(out)


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


def felt_one_marks(root, lo, hi):
    for el in root.find('ElementEffects').findall('Element'):
        if el.get('name') == 'Beat Count' and el.get('type') == 'timing':
            return [int(e.get('startTime'))
                    for e in el.find('EffectLayer').findall('Effect')
                    if (e.get('label') or '').strip() == '3'
                    and lo < int(e.get('startTime')) < hi]
    raise SystemExit('Beat Count track not found')


def main():
    dry = '--dry-run' in sys.argv

    tree = ET.parse(XSQ)
    root = tree.getroot()
    db = [t.text or '' for t in root.find('EffectDB').findall('Effect')]
    pals = [t.text or '' for t in root.find('ColorPalettes').findall('ColorPalette')]
    elements = {el.get('name'): el
                for el in root.find('ElementEffects').findall('Element')}

    readds = []   # (api target, layer, name, settings, palette, start, end)

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
            assert ee <= C2_START or es >= C2_END, \
                f'{api_target(owner, sub)} L{layer_i} collision: ' \
                f'{e.get("name")} {es}-{ee}'

    # beds
    for owner, sub, li, name, totals, swap in RESTORE:
        layer, sett, pal = grab(owner, sub, li, name, C1_START, V2_END)
        assert_clear(owner, sub, li)
        if totals:
            for k, v in totals.items():
                assert k in sett, f'{owner}: {k} missing'
                sett[k] = v
        sett['T_TEXTCTRL_Fadein'] = FADEIN
        sett['T_TEXTCTRL_Fadeout'] = FADEOUT
        new_pal = swap_palette(pal) if swap else pal
        readds.append((api_target(owner, sub), li, name, fmt(sett), new_pal,
                       C2_START, C2_END))
    print(f'beds: {len(RESTORE)} effects restored {C2_START}-{C2_END} '
          f'(fadein {FADEIN} / fadeout {FADEOUT})')

    # offs
    for owner, sub, li, name in OFFS:
        layer, sett, pal = grab(owner, sub, li, name, C1_START, V2_END)
        assert_clear(owner, sub, li)
        readds.append((api_target(owner, sub), li, name, fmt(sett), pal,
                       C2_START, C2_END))
    print(f'offs: {len(OFFS)} masks extended through C2')

    # marquees — per-felt-bar flip segments through C2
    flips = felt_one_marks(root, C2_START, C2_END)
    assert len(flips) == 16 and flips[0] == 128925 and flips[-1] == 178925, flips
    bounds = [C2_START] + flips + [C2_END]
    for owner, sub in MARQUEES:
        # base = the fade-free 122275-125600 V2 segment
        layer, sett, pal = grab(owner, sub, 0, 'Marquee', 122275, 125600)
        assert_clear(owner, sub, 0)
        sett.pop('T_TEXTCTRL_Fadein', None)
        sett.pop('T_TEXTCTRL_Fadeout', None)
        for i, (s, en) in enumerate(zip(bounds, bounds[1:])):
            d = dict(sett)
            d['E_CHECKBOX_Marquee_Reverse'] = '1' if i % 2 == 0 else '0'
            if i == 0:
                d['T_TEXTCTRL_Fadein'] = FADEIN
            if i == len(bounds) - 2:
                d['T_TEXTCTRL_Fadeout'] = FADEOUT
            readds.append((api_target(owner, sub), 0, 'Marquee', fmt(d), pal,
                           s, en))
    print(f'marquees: {len(MARQUEES)} targets x {len(bounds) - 1} segments, '
          f'flips at felt beat 1 ({flips[0]}..{flips[-1]})')

    # arches — continue the 6650 ms alternating tile grid through C2
    owner, sub, li, name = ARCH
    layer, sett, pal = grab(owner, sub, li, name, 122175, V2_END)
    assert_clear(owner, sub, li)
    sett.pop('T_TEXTCTRL_Fadein', None)
    sett.pop('T_TEXTCTRL_Fadeout', None)
    t = ARCH_GRID_START + ARCH_TILE          # first boundary inside C2: 128825
    starts = [C2_START]
    while t < C2_END:
        starts.append(t)
        t += ARCH_TILE
    segs = [(s, min(s2, C2_END)) for s, s2 in
            zip(starts, starts[1:] + [C2_END + 1])]
    for i, (s, en) in enumerate(segs):
        d = dict(sett)
        # tile containing s: index n where tile start = 122175 + 6650n
        n = 0 if s == C2_START else round((s - ARCH_GRID_START) / ARCH_TILE)
        d['E_CHOICE_Chase_Type1'] = 'Right-Left' if n % 2 == 0 else 'Left-Right'
        rot = ARCH_ROT_PER_TILE * (en - s) / ARCH_TILE
        d['E_TEXTCTRL_Chase_Rotations'] = f'{rot:.2f}'.rstrip('0').rstrip('.')
        if i == 0:
            d['T_TEXTCTRL_Fadein'] = FADEIN
        if i == len(segs) - 1:
            d['T_TEXTCTRL_Fadeout'] = FADEOUT
        readds.append((api_target(owner, sub), li, name, fmt(d), pal, s, en))
    print(f'arches: {len(segs)} chase tiles {segs[0][0]}-{segs[-1][1]}')

    if dry:
        print('dry-run: no writes')
        return

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info
    x.save(XSQ)
    shutil.copy(XSQ, XSQ + '.bak-before-c2-color-swap')

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
        out = []
        for e in layer.findall('Effect'):
            es, ee = int(e.get('startTime')), int(e.get('endTime'))
            if ee > C2_START and es < C2_END:
                out.append((es, ee, e))
        return sorted(out)

    old_colors = ('#2864FF', '#0A1E50', '#8080FF', '#B01212', '#FF0000')
    for owner, sub, li, name, totals, swap in RESTORE:
        wins = effects_in_window(owner, sub, li)
        assert len(wins) == 1 and wins[0][0] == C2_START \
            and wins[0][1] == C2_END, f'{owner} L{li}: {[(w[0], w[1]) for w in wins]}'
        sett = parse(db2[int(wins[0][2].get('ref'))])
        assert sett.get('T_TEXTCTRL_Fadein') == FADEIN, (owner, sett)
        assert sett.get('T_TEXTCTRL_Fadeout') == FADEOUT, (owner, sett)
        pal = pals2[int(wins[0][2].get('palette'))] if wins[0][2].get('palette') else ''
        if swap:
            checked = {n for n, v in
                       re.findall(r'C_CHECKBOX_Palette(\d+)=(\d)', pal) if v == '1'}
            for n in checked:
                m = re.search(rf'C_BUTTON_Palette{n}=([^,]*)', pal)
                if m:
                    assert not any(c.lower() in m.group(1).lower()
                                   for c in old_colors), (owner, m.group(1))
    print(f'verified beds: {len(RESTORE)} restored, palettes swapped, fades set')

    for owner, sub, li, name in OFFS:
        wins = effects_in_window(owner, sub, li)
        assert len(wins) == 1 and wins[0][0] == C2_START and wins[0][1] == C2_END
    print('verified offs')

    for owner, sub in MARQUEES:
        wins = effects_in_window(owner, sub, 0)
        assert len(wins) == len(bounds) - 1, (owner, len(wins))
        rev = ''
        for i, (s, en, e) in enumerate(wins):
            assert (s, en) == (bounds[i], bounds[i + 1]), (owner, s, en)
            d = parse(db2[int(e.get('ref'))])
            rev += d['E_CHECKBOX_Marquee_Reverse']
            if i == 0:
                assert d.get('T_TEXTCTRL_Fadein') == FADEIN
            elif 'T_TEXTCTRL_Fadein' in d:
                raise AssertionError((owner, s))
            if i == len(wins) - 1:
                assert d.get('T_TEXTCTRL_Fadeout') == FADEOUT
            elif 'T_TEXTCTRL_Fadeout' in d:
                raise AssertionError((owner, s))
        assert rev == '10' * 8 + '1', (owner, rev)
    print('verified marquees: 5 x 17 segments, reverse pattern 1010...')

    wins = effects_in_window('Arches - All', None, 0)
    assert len(wins) == len(segs), len(wins)
    dirs = ''.join('L' if parse(db2[int(e.get('ref'))])['E_CHOICE_Chase_Type1']
                   == 'Left-Right' else 'R' for _, _, e in wins)
    assert dirs == 'RLRLRLRLR', dirs
    print(f'verified arches: {len(wins)} tiles, directions {dirs}')

    # crosses untouched
    mt = effects_in_window('Mega Tree', None, 1)
    assert len(mt) == 1 and mt[0][0] == C1_START and mt[0][1] == C2_END
    mg = effects_in_window('GE Mini Grand Illusion', None, 1)
    assert [w[0] for w in mg] == [127275, 130600], mg
    print('verified crosses untouched')
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
