"""Continue the Chorus 1 treatments across Verse 2 on all non-singing props.

User ask (2026-08-01): "I'd like verse 2 to continue the effects the chorus
had on all the non singing props."

C1 window was 67275-93925 (Anthemic downbeat -> Groove downbeat). This pass
carries every continuous C1 effect through **127275** (Soaring/C2 downbeat =
end of V2). Ratio 60000/26650 = 2.2514.

Three treatment classes:
  1. EXTEND — time-based effects (shaders, pinwheels, marquees, washes,
     pictures, On/Off holds): endTime edit only, settings untouched.
  2. RESCALE — effects whose motion params are TOTALS over the effect
     duration (SingleStrand Chase_Rotations, Bars/ColorWash Cycles, Spirals
     Movement, Fan/Galaxy Revolutions, Galaxy Duration%): deleted from the
     .xsq and re-added via addEffect over 67275-127275 with the totals
     scaled x2.2514 so the visible speed is unchanged.
  3. ARCHES — the live hand-tuned ~2-bar alternating chase segments: the
     final fading segment (88950-95575, Fadeout=4) is replaced with a plain
     one, then 5 more alternating segments tile through V2 (last one clipped
     at 127275 with proportional rotations + a 2 s fadeout). L1 Off underlay
     extended.

NOT extended (musical moments, not section bases): Tree Topper L1/L2 bass
pops, EFL Wings "angels cry" stack, PC1 leftovers. Singing props untouched.
The Starlord pinwheel Twist value-curve stretches with the effect (wobble
~2.25x slower) — Custom VC, left as-is.

Run in Slot B (XLIGHTS_API_PORT=49914), sequence open:
    python3 v2_continue_c1.py [--dry-run]
Revert: git checkout the .xsq (or the .bak-before-v2-continue backup).
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
C1_END = 93925
V2_END = 127275

# --- class 1: (element, layer, effect name, old_start, old_end, new_end)
EXTEND = [
    ('Whole Scene', 0, 'Shader', 67275, 93925, V2_END),
    ('Windows', 0, 'Marquee', 67275, 93925, V2_END),
    ('Windows', 1, 'Color Wash', 67275, 93925, V2_END),
    ('Icicles GRP', 1, 'Color Wash', 67275, 93925, V2_END),
    ('Yard Borders', 0, 'Marquee', 67275, 93925, V2_END),
    ('Yard Borders', 1, 'Color Wash', 67275, 93925, V2_END),
    ('Verts', 0, 'Marquee', 67275, 93925, V2_END),
    ('Verts', 1, 'Color Wash', 67275, 93925, V2_END),
    ('Roof', 0, 'Marquee', 67275, 93925, V2_END),
    ('Roof', 1, 'Color Wash', 67275, 93925, V2_END),
    ('GE MOAW GRP', 0, 'Pinwheel', 67275, 93925, V2_END),
    ('GE MOAW GRP', 1, 'Pinwheel', 67275, 93925, V2_END),
    ('GE Rosa Grande GRP', 0, 'Pinwheel', 67275, 93925, V2_END),
    ('GE Rosa Grande GRP', 1, 'Pinwheel', 67275, 93925, V2_END),
    ('GE Rosa Grande Torch Long Even GRP', 0, 'Pinwheel', 67275, 93925, V2_END),
    ('GE Starlord GRP', 1, 'Pinwheel', 67275, 93925, V2_END),
    ('GE Starlord GRP', 2, 'Pinwheel', 67275, 93925, V2_END),
    ('GE Reel Max GRP', 0, 'Pinwheel', 67275, 93925, V2_END),
    ('GE Reel Max GRP', 1, 'Pinwheel', 67275, 93925, V2_END),
    ('GE Merry Christmas', 0, 'Off', 67275, 93925, V2_END),
    ('Mega Tree', 1, 'Pictures', 67275, 93925, V2_END),
    ('Mega Tree', 2, 'Shader', 67275, 93925, V2_END),
    ('Toni - Flat Tree', 1, 'Pictures', 67275, 93925, V2_END),
    ('Toni - Flat Tree', 2, 'Shader', 67275, 93925, V2_END),
    ('Tree Topper', 3, 'On', 67275, 93925, V2_END),
    # Mini Grand cross keeps its own Song Sections convention (67575-95100)
    ('GE Mini Grand Illusion', 0, 'Pictures', 67575, 95100, 127625),
    # arches Off underlay under the chase segments
    ('Arches - All', 1, 'Off', 67275, 95575, V2_END),
]

# Christ submodel reveal — stored as <SubModelEffectLayer name="Christ"> under
# the GE Merry Christmas Element (NOT <SubModel>; plain Element scans miss it,
# which is how this pair was initially overlooked). (parent, submodel, layer,
# effect, old_start, old_end, new_end); extended by extend_submodels().
EXTEND_SUBMODEL = [
    ('GE Merry Christmas', 'Christ', 0, 'Marquee', 67275, 93925, V2_END),
    ('GE Merry Christmas', 'Christ', 1, 'Color Wash', 67275, 93925, V2_END),
]

RATIO = (V2_END - C1_START) / (C1_END - C1_START)  # 2.2514

# --- class 2: (element, layer, effect name, {param: scaled value})
RESCALE = [
    ('Icicles GRP', 0, 'SingleStrand', {'E_TEXTCTRL_Chase_Rotations': '6.8'}),
    ('GE MOAW Spokes GRP', 0, 'SingleStrand', {'E_TEXTCTRL_Chase_Rotations': '3.2'}),
    ('GE MOAW Swag GRP', 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '4.5'}),
    ('GE MOAW Diamonds GRP', 0, 'Color Wash', {'E_TEXTCTRL_ColorWash_Cycles': '4.5'}),
    ('GE MOAW Snowflake Spoke GRP', 0, 'Galaxy',
     {'E_SLIDER_Galaxy_Revolutions': '1620', 'E_SLIDER_Galaxy_Duration': '9'}),
    ('GE Reel Max Chevrons GRP', 0, 'SingleStrand', {'E_TEXTCTRL_Chase_Rotations': '9'}),
    ('GE Reel Max Circles Outer GRP', 0, 'SingleStrand', {'E_TEXTCTRL_Chase_Rotations': '18'}),
    ('GE Reel Max Kites GRP', 0, 'SingleStrand', {'E_TEXTCTRL_Chase_Rotations': '6.8'}),
    ('GE Reel Max Spokes GRP', 0, 'Spirals', {'E_TEXTCTRL_Spirals_Movement': '9'}),
    ('GE Rosa Grande Feather Long Odd GRP', 0, 'Spirals', {'E_TEXTCTRL_Spirals_Movement': '9'}),
    ('GE Rosa Grande Outer Ball GRP', 0, 'SingleStrand', {'E_TEXTCTRL_Chase_Rotations': '18'}),
    ('GE Rosa Grande Spoke GRP', 0, 'Fan', {'E_SLIDER_Fan_Revolutions': '1620'}),
    ('GE Starlord GRP', 0, 'Fan', {'E_SLIDER_Fan_Revolutions': '1620'}),
    ('GE Starlord Cross GRP', 0, 'SingleStrand', {'E_TEXTCTRL_Chase_Rotations': '12.4'}),
    ('GE Starlord Plunger All GRP', 0, 'Spirals', {'E_TEXTCTRL_Spirals_Movement': '4.5'}),
    ('GE Starlord Spoke GRP', 0, 'SingleStrand', {'E_TEXTCTRL_Chase_Rotations': '9'}),
    ('Candy Cane - 1', 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '18'}),
    ('Candy Cane - 2', 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '18'}),
    ('Candy Cane - 3', 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '18'}),
    ('Candy Cane - 4', 0, 'Bars', {'E_TEXTCTRL_Bars_Cycles': '18'}),
]

# --- class 3: arches — live segments end 95575; continue period 6650
ARCH = 'Arches - All'
ARCH_LAST = (88950, 95575)     # current final (fading) segment, replaced
ARCH_SEGMENTS = [              # (start, end, direction, rotations, fadeout)
    (88950, 95575, 'Left-Right', '2', None),
    (95575, 102225, 'Right-Left', '2', None),
    (102225, 108875, 'Left-Right', '2', None),
    (108875, 115525, 'Right-Left', '2', None),
    (115525, 122175, 'Left-Right', '2', None),
    (122175, 127275, 'Right-Left', '1.5', '2'),   # clipped tail
]


def parse(settings):
    return dict(kv.split('=', 1) for kv in settings.split(',') if '=' in kv)


def fmt(d):
    return ','.join(f'{k}={v}' for k, v in d.items())


def main():
    dry = '--dry-run' in sys.argv

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info
    x.xl('closeSequence', force='true', quiet='true')

    if not dry:
        shutil.copy(XSQ, XSQ + '.bak-before-v2-continue')

    tree = ET.parse(XSQ)
    root = tree.getroot()
    db = [t.text or '' for t in root.find('EffectDB').findall('Effect')]
    palettes = [t.text or '' for t in root.find('ColorPalettes').findall('ColorPalette')]
    elements = {el.get('name'): el
                for el in root.find('ElementEffects').findall('Element')}

    readds = []   # (element, layer, effect, settings str, palette str, start, end)

    def find_effect(el_name, layer_i, name, start=None, end=None):
        layers = elements[el_name].findall('EffectLayer')
        assert layer_i < len(layers), f'{el_name} has no L{layer_i}'
        for e in layers[layer_i].findall('Effect'):
            if e.get('name') != name:
                continue
            if start is not None and int(e.get('startTime')) != start:
                continue
            if end is not None and int(e.get('endTime')) != end:
                continue
            return layers[layer_i], e
        raise SystemExit(f'not found: {el_name} L{layer_i} {name} '
                         f'{start}-{end} (already extended, or hand-edited?)')

    # sanity: V2 window must be empty on every touched layer beyond the
    # effects we are about to extend/replace
    for el_name, li, name, s, en, new_end in EXTEND:
        layers = elements[el_name].findall('EffectLayer')
        for e in layers[li].findall('Effect'):
            es, ee = int(e.get('startTime')), int(e.get('endTime'))
            if ee > C1_END and es < new_end and not (es == s and ee == en):
                raise SystemExit(f'V2 collision on {el_name} L{li}: '
                                 f'{e.get("name")} {es}-{ee}')

    # class 1: extend
    for el_name, li, name, s, en, new_end in EXTEND:
        _, e = find_effect(el_name, li, name, s, en)
        if not dry:
            e.set('endTime', str(new_end))
    print(f'extend: {len(EXTEND)} effects -> {V2_END} (mini grand -> 127625)')

    # class 1b: submodel effect layers (SubModelEffectLayer nodes)
    for parent, sub, li, name, s, en, new_end in EXTEND_SUBMODEL:
        hit = False
        for sml in elements[parent].findall('SubModelEffectLayer'):
            if sml.get('name') != sub or int(sml.get('layer') or 0) != li:
                continue
            for e in sml.findall('Effect'):
                if (e.get('name') == name and int(e.get('startTime')) == s
                        and int(e.get('endTime')) == en):
                    if not dry:
                        e.set('endTime', str(new_end))
                    hit = True
        if not hit:
            raise SystemExit(f'not found: {parent}/{sub} L{li} {name} {s}-{en}')
    print(f'extend submodels: {len(EXTEND_SUBMODEL)} effects -> {V2_END}')

    # class 2: delete + record for scaled re-add
    for el_name, li, name, scaled in RESCALE:
        layer, e = find_effect(el_name, li, name, C1_START, C1_END)
        sett = parse(db[int(e.get('ref'))])
        for k, v in scaled.items():
            assert k in sett, f'{el_name}: {k} missing in settings'
            sett[k] = v
        pal = palettes[int(e.get('palette'))]
        readds.append((el_name, li, name, fmt(sett), pal, C1_START, V2_END))
        if not dry:
            layer.remove(e)
    print(f'rescale: {len(RESCALE)} effects re-added {C1_START}-{V2_END} '
          f'with totals x{RATIO:.2f}')

    # class 3: arches
    layer, e = find_effect(ARCH, 0, 'SingleStrand', *ARCH_LAST)
    base = parse(db[int(e.get('ref'))])
    base.pop('T_TEXTCTRL_Fadeout', None)
    arch_pal = palettes[int(e.get('palette'))]
    if not dry:
        layer.remove(e)
    for s, en, direction, rot, fadeout in ARCH_SEGMENTS:
        sett = dict(base)
        sett['E_CHOICE_Chase_Type1'] = direction
        sett['E_TEXTCTRL_Chase_Rotations'] = rot
        if fadeout:
            sett['T_TEXTCTRL_Fadeout'] = fadeout
        readds.append((ARCH, 0, 'SingleStrand', fmt(sett), arch_pal, s, en))
    print(f'arches: replaced fading tail; {len(ARCH_SEGMENTS)} segments '
          f'tile to {V2_END}')

    if dry:
        print('dry-run: no writes')
        x.xl('openSequence', seq=XSQ, timeout=300)
        return

    tree.write(XSQ, encoding='UTF-8', xml_declaration=True)
    x.xl('openSequence', seq=XSQ, timeout=300)
    info = x.xl('getOpenSequence')
    assert int(info.get('len', 0)) == SEQ_LEN, info

    for el_name, li, name, sett, pal, s, en in readds:
        x.add_effect(el_name, li, name, sett, pal, s, en)
    print(f'added {len(readds)} effects via API')

    # verify: every touched element now has its effect ending at the new end
    checks = ([(m, li, V2_END if m != 'GE Mini Grand Illusion' else 127625)
               for m, li, *_ in EXTEND] +
              [(m, li, V2_END) for m, li, _, _ in RESCALE] +
              [(ARCH, 0, V2_END)])
    for m, li, want_end in checks:
        ids = x.xl('getEffectIDs', model=m)['effects']
        ends = []
        for eid in ids[li]:
            st = x.xl('getEffectSettings', model=m, layer=str(li), id=str(eid))
            ends.append(int(st['endTime']))
        assert want_end in ends, f'{m} L{li}: no effect ends at {want_end}: {ends}'

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
