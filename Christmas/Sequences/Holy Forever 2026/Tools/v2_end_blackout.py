"""End-of-V2 blackout: everything plunges to black; the Mega Tree cross swells.

User ask (2026-08-02): "and the end of verse 2, lets dim everything to total
black except the cross on the mega tree, let's have it get brighter."

User choices (AskQuestion same day):
  - window: **quick plunge** — the last ~1.7 s (125600 -> 127275, the final
    felt-beat-1 flip point -> the Soaring/C2 downbeat where all beds end).
  - faces: **keep the singers lit** — no Faces/State effect is touched.
  - crosses: **mega-only** — the Toni flat-tree cross dims with the beds (it
    ends 127275 anyway); the hand-extended full-song Mini Grand cross dips to
    black at the downbeat and comes back up over the first C2 bar (its
    song-end span is preserved).
  - cross-end: **keep it lit through all of C2** — the Mega Tree cross no
    longer ends at 127275; it runs to the Regather downbeat 180600 (C2 end
    per the Mood track) with the stock 2 s fadeout there.

What the script does (all via close -> .xsq delete -> reopen -> addEffect):

  1. BEDS (41 effects, all ending 127275): T_TEXTCTRL_Fadeout -> 1.68 so the
     fade spans exactly the plunge window (fade start 125595 ~= 125600).
     Includes the Whole Scene aurora, all MOAW/Rosa/Starlord/Reel Max banks,
     canes, icicles, house washes, Christ wash, Toni cross+shader, Mega Tree
     aurora (L2), Tree Topper amber On, and the last arches chase segment.
  2. MARQUEE TAILS (5): the 125600-127275 flip segment on Verts / Roof /
     Windows / Yard Borders / Christ gets Fadeout=1.68 (they had none — the
     per-bar flip at 125600 still happens, now into the plunge).
  3. MEGA TREE CROSS (L1 Pictures): re-added 67275-180600 with a brightness
     value curve (Min 0 / Max 400): hold 100 -> ramp to 300 across the plunge
     -> ease back to 100 over the first C2 bar (by ~130600) -> hold through
     C2. Fadein 2 / Fadeout 2 unchanged.
  4. MINI GRAND CROSS (L1 Pictures, 67575-308400): split into 4 segments to
     carve the dip — plain to 125600, Fadeout 1.68 into the downbeat, Fadein
     3.33 recovery over the first C2 bar, plain to song end. (A brightness
     VC can't hit 127275 on a 240 s effect — 2-decimal x points = 2.4 s
     slop; segments are exact.)

Run in Slot B (XLIGHTS_API_PORT=49914), sequence open:
    python3 v2_end_blackout.py [--dry-run]
Revert: git checkout the .xsq (or the .bak-before-v2-end-blackout backup).
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
V2_END = 127275           # Soaring/C2 downbeat — total black here
PLUNGE = 125600           # last felt-beat-1 flip point; dim starts here
C2_BAR1_END = 130600      # recovery/ease-down complete (first C2 felt bar)
C2_END = 180600           # Mood Regather downbeat — end of C2
FADEOUT = '1.68'          # 127275 - 1680 = 125595 ~= PLUNGE

# --- class 1: beds -> Fadeout 1.68 (element, submodel|None, layer, name,
#     start, end)
DIM_BEDS = [
    ('Whole Scene', None, 0, 'Shader', C1_START, V2_END),
    ('Windows', None, 1, 'Color Wash', C1_START, V2_END),
    ('Icicles GRP', None, 1, 'Color Wash', C1_START, V2_END),
    ('Icicles GRP', None, 0, 'SingleStrand', C1_START, V2_END),
    ('Yard Borders', None, 1, 'Color Wash', C1_START, V2_END),
    ('Verts', None, 1, 'Color Wash', C1_START, V2_END),
    ('Roof', None, 1, 'Color Wash', C1_START, V2_END),
    ('GE Merry Christmas', 'Christ', 1, 'Color Wash', C1_START, V2_END),
    ('GE MOAW GRP', None, 0, 'Pinwheel', C1_START, V2_END),
    ('GE MOAW GRP', None, 1, 'Pinwheel', C1_START, V2_END),
    ('GE MOAW Snowflake Spoke GRP', None, 0, 'Galaxy', C1_START, V2_END),
    ('GE MOAW Spokes GRP', None, 0, 'SingleStrand', C1_START, V2_END),
    ('GE MOAW Swag GRP', None, 0, 'Bars', C1_START, V2_END),
    ('GE MOAW Diamonds GRP', None, 0, 'Color Wash', C1_START, V2_END),
    ('GE Rosa Grande GRP', None, 0, 'Pinwheel', C1_START, V2_END),
    ('GE Rosa Grande GRP', None, 1, 'Pinwheel', C1_START, V2_END),
    ('GE Rosa Grande Torch Long Even GRP', None, 0, 'Pinwheel', C1_START, V2_END),
    ('GE Rosa Grande Feather Long Odd GRP', None, 0, 'Spirals', C1_START, V2_END),
    ('GE Rosa Grande Outer Ball GRP', None, 0, 'SingleStrand', C1_START, V2_END),
    ('GE Rosa Grande Spoke GRP', None, 0, 'Fan', C1_START, V2_END),
    ('GE Starlord GRP', None, 0, 'Fan', C1_START, V2_END),
    ('GE Starlord GRP', None, 1, 'Pinwheel', C1_START, V2_END),
    ('GE Starlord GRP', None, 2, 'Pinwheel', C1_START, V2_END),
    ('GE Starlord Cross GRP', None, 0, 'SingleStrand', C1_START, V2_END),
    ('GE Starlord Plunger All GRP', None, 0, 'Spirals', C1_START, V2_END),
    ('GE Starlord Spoke GRP', None, 0, 'SingleStrand', C1_START, V2_END),
    ('GE Reel Max GRP', None, 0, 'Pinwheel', C1_START, V2_END),
    ('GE Reel Max GRP', None, 1, 'Pinwheel', C1_START, V2_END),
    ('GE Reel Max Chevrons GRP', None, 0, 'SingleStrand', C1_START, V2_END),
    ('GE Reel Max Circles Outer GRP', None, 0, 'SingleStrand', C1_START, V2_END),
    ('GE Reel Max Kites GRP', None, 0, 'SingleStrand', C1_START, V2_END),
    ('GE Reel Max Spokes GRP', None, 0, 'Spirals', C1_START, V2_END),
    ('Candy Cane - 1', None, 0, 'Bars', C1_START, V2_END),
    ('Candy Cane - 2', None, 0, 'Bars', C1_START, V2_END),
    ('Candy Cane - 3', None, 0, 'Bars', C1_START, V2_END),
    ('Candy Cane - 4', None, 0, 'Bars', C1_START, V2_END),
    ('Mega Tree', None, 2, 'Shader', C1_START, V2_END),
    ('Toni - Flat Tree', None, 1, 'Pictures', C1_START, V2_END),
    ('Toni - Flat Tree', None, 2, 'Shader', C1_START, V2_END),
    ('Tree Topper', None, 3, 'On', C1_START, V2_END),
    ('Arches - All', None, 0, 'SingleStrand', 122175, V2_END),
]

# --- class 2: marquee tail segments get Fadeout (element, submodel|None)
MARQUEE_TAILS = [
    ('Verts', None),
    ('Roof', None),
    ('Windows', None),
    ('Yard Borders', None),
    ('GE Merry Christmas', 'Christ'),
]

CROSS = ('Mega Tree', None, 1, 'Pictures', C1_START, V2_END)
CROSS_PALETTE_VC = (
    'C_VALUECURVE_Brightness=Active=TRUE|Id=ID_VALUECURVE_Brightness|'
    'Type=Custom|Min=0.00|Max=400.00|P1=1.00|RV=TRUE|'
    'Values=0.00:0.25;0.51:0.25;0.53:0.75;0.56:0.25;1.00:0.25|')

MINI = ('GE Mini Grand Illusion', None, 1, 'Pictures', 67575, 308400)
MINI_SEGMENTS = [           # (start, end, fadein, fadeout)
    (67575, PLUNGE, '2', None),
    (PLUNGE, V2_END, None, FADEOUT),
    (V2_END, C2_BAR1_END, '3.33', None),
    (C2_BAR1_END, 308400, None, '2'),
]


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

    readds = []   # (api target, layer, name, settings, palette, start, end)

    def grab(owner, sub, layer_i, name, start, end):
        layer = find_layer(elements[owner], sub, layer_i)
        for e in layer.findall('Effect'):
            if (e.get('name') == name and int(e.get('startTime')) == start
                    and int(e.get('endTime')) == end):
                sett = parse(db[int(e.get('ref'))])
                pal = pals[int(e.get('palette'))] if e.get('palette') else ''
                return layer, e, sett, pal
        raise SystemExit(f'not found: {api_target(owner, sub)} L{layer_i} '
                         f'{name} {start}-{end} (hand-edited?)')

    # class 1: beds
    for owner, sub, li, name, s, en in DIM_BEDS:
        layer, e, sett, pal = grab(owner, sub, li, name, s, en)
        sett['T_TEXTCTRL_Fadeout'] = FADEOUT
        readds.append((api_target(owner, sub), li, name, fmt(sett), pal, s, en))
        if not dry:
            layer.remove(e)
    print(f'beds: {len(DIM_BEDS)} effects get Fadeout={FADEOUT} '
          f'(plunge {PLUNGE}->{V2_END})')

    # class 2: marquee tails
    for owner, sub in MARQUEE_TAILS:
        layer, e, sett, pal = grab(owner, sub, 0, 'Marquee', PLUNGE, V2_END)
        assert 'T_TEXTCTRL_Fadeout' not in sett, f'{owner}: tail already fades?'
        sett['T_TEXTCTRL_Fadeout'] = FADEOUT
        readds.append((api_target(owner, sub), 0, 'Marquee', fmt(sett), pal,
                       PLUNGE, V2_END))
        if not dry:
            layer.remove(e)
    print(f'marquees: {len(MARQUEE_TAILS)} tail segments get Fadeout={FADEOUT}')

    # class 3: mega tree cross — extend through C2 with brightness swell
    owner, sub, li, name, s, en = CROSS
    layer, e, sett, pal = grab(owner, sub, li, name, s, en)
    # nothing else may live on Mega Tree L1 between V2_END and C2_END
    for other in layer.findall('Effect'):
        if other is e:
            continue
        os_, oe = int(other.get('startTime')), int(other.get('endTime'))
        assert oe <= V2_END or os_ >= C2_END, \
            f'Mega Tree L1 collision: {other.get("name")} {os_}-{oe}'
    new_pal = pal + ',' + CROSS_PALETTE_VC
    readds.append(('Mega Tree', li, name, fmt(sett), new_pal, s, C2_END))
    if not dry:
        layer.remove(e)
    print(f'cross: Mega Tree L1 Pictures {s}-{C2_END}, brightness 100->300 '
          f'across the plunge, ease to 100 by {C2_BAR1_END}')

    # class 4: mini grand cross — 4 segments carve the dip
    owner, sub, li, name, s, en = MINI
    layer, e, sett, pal = grab(owner, sub, li, name, s, en)
    for other in layer.findall('Effect'):
        if other is not e:
            raise SystemExit(f'Mini Grand L1 collision: '
                             f'{other.get("name")} {other.get("startTime")}-'
                             f'{other.get("endTime")}')
    for ms, me, fi, fo in MINI_SEGMENTS:
        d = dict(sett)
        d.pop('T_TEXTCTRL_Fadein', None)
        d.pop('T_TEXTCTRL_Fadeout', None)
        if fi:
            d['T_TEXTCTRL_Fadein'] = fi
        if fo:
            d['T_TEXTCTRL_Fadeout'] = fo
        readds.append(('GE Mini Grand Illusion', li, name, fmt(d), pal, ms, me))
    if not dry:
        layer.remove(e)
    print(f'mini grand: {len(MINI_SEGMENTS)} segments dip to black at '
          f'{V2_END}, recover by {C2_BAR1_END}')

    if dry:
        print('dry-run: no writes')
        return

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info
    x.save(XSQ)
    x.xl('closeSequence', force='true', quiet='true')
    shutil.copy(XSQ, XSQ + '.bak-before-v2-end-blackout')

    # re-parse the freshly saved file and redo the deletions on live state
    tree = ET.parse(XSQ)
    root = tree.getroot()
    elements = {el.get('name'): el
                for el in root.find('ElementEffects').findall('Element')}

    def remove(owner, sub, layer_i, name, start, end):
        layer = find_layer(elements[owner], sub, layer_i)
        for e in layer.findall('Effect'):
            if (e.get('name') == name and int(e.get('startTime')) == start
                    and int(e.get('endTime')) == end):
                layer.remove(e)
                return
        raise SystemExit(f're-remove failed: {owner} L{layer_i} {name}')

    for owner, sub, li, name, s, en in DIM_BEDS:
        remove(owner, sub, li, name, s, en)
    for owner, sub in MARQUEE_TAILS:
        remove(owner, sub, 0, 'Marquee', PLUNGE, V2_END)
    remove(*CROSS)
    remove(*MINI)
    tree.write(XSQ, encoding='UTF-8', xml_declaration=True)

    x.xl('openSequence', seq=XSQ, timeout=300)
    assert int(x.xl('getOpenSequence').get('len', 0)) == SEQ_LEN

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

    def get(owner, sub, layer_i, name, start, end):
        layer = find_layer(elements2[owner], sub, layer_i)
        for e in layer.findall('Effect'):
            if (e.get('name') == name and int(e.get('startTime')) == start
                    and int(e.get('endTime')) == end):
                return parse(db2[int(e.get('ref'))]), \
                    (pals2[int(e.get('palette'))] if e.get('palette') else '')
        raise SystemExit(f'verify: missing {api_target(owner, sub)} '
                         f'L{layer_i} {name} {start}-{end}')

    for owner, sub, li, name, s, en in DIM_BEDS:
        sett, _ = get(owner, sub, li, name, s, en)
        assert sett.get('T_TEXTCTRL_Fadeout') == FADEOUT, (owner, sett)
    for owner, sub in MARQUEE_TAILS:
        sett, _ = get(owner, sub, 0, 'Marquee', PLUNGE, V2_END)
        assert sett.get('T_TEXTCTRL_Fadeout') == FADEOUT, (owner, sett)
    sett, pal = get('Mega Tree', None, 1, 'Pictures', C1_START, C2_END)
    assert sett.get('T_TEXTCTRL_Fadeout') == '2'
    assert 'VALUECURVE_Brightness' in pal and '0.53:0.75' in pal, pal
    for ms, me, fi, fo in MINI_SEGMENTS:
        sett, _ = get('GE Mini Grand Illusion', None, 1, 'Pictures', ms, me)
        assert sett.get('T_TEXTCTRL_Fadein') == fi, (ms, sett)
        assert sett.get('T_TEXTCTRL_Fadeout') == fo, (ms, sett)
    print(f'verified: {len(DIM_BEDS)} beds + {len(MARQUEE_TAILS)} marquee '
          f'tails fade the plunge; cross swells to {C2_END}; mini grand dips')
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
