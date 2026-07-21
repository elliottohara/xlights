"""Chorus 1 — red/white barber-pole spin on the candy canes.

User ask: "make those candy canes look like candy canes" (scoped to the
first chorus).

v1 (REJECTED — "looks like shit... shouldn't be vertical"): one Bars
effect on the `Canes` GROUP, `Per Model Per Preview` buffer,
`Direction=up`. That buffer style projects each model through the 2D
preview camera and stripes by real-world Y position — but each
`Candy Cane - N` is a single 48-node curved strand (node 1 at the base,
node 48 near the hook tip), so Y-based striping cuts across the curve
instead of following it and just looks like blotchy horizontal bands.

v2 (current): Bars on each `Candy Cane - 1..4` INDIVIDUALLY (not the
group), `B_CHOICE_BufferStyle=Single Line` — this remaps the model to a
virtual 1xN strip ordered by NODE INDEX regardless of physical XY
position, so stripes follow the actual wire path (base to hook-tip),
which is what makes it read as a real spiral candy-cane pattern. Same
proven technique as the Verts/Yard Borders/Arches marquees elsewhere in
this sequence. `Direction=Left` scrolls along the string for the
barber-pole spin.

L0 on each individual cane was previously empty (all base effects lived
on the `Canes` GROUP element, not the members) — group and member
elements have independent layer stacks, so this doesn't touch the
group's own L0 Shockwave accents.

Run (Slot A):
    python3 candy_canes_barberpole.py [--dry-run] [--clear-only] [--rework]
"""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-a/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
SEQ_LEN = 308314

WIN_START = 67275
WIN_END = 93925

CANES = ['Candy Cane - 1', 'Candy Cane - 2', 'Candy Cane - 3', 'Candy Cane - 4']
GROUP = 'Canes'

# v1 left a stray vertical Bars on the GROUP's L1 — must be cleared.
# Individual canes only ever get L0 from this script.
OWNED = {c: {0} for c in CANES}
CLEAR = dict(OWNED)
CLEAR[GROUP] = {1}

CANDY_RED = '#FF0000'
CANDY_WHITE = '#FFFFFF'

PALETTE = (
    f'C_BUTTON_Palette1={CANDY_RED},C_CHECKBOX_Palette1=1,'
    f'C_BUTTON_Palette2={CANDY_WHITE},C_CHECKBOX_Palette2=1,'
    'C_SLIDER_Brightness=65'
)

SETTINGS = (
    'B_CHOICE_BufferStyle=Single Line,'
    'E_CHECKBOX_Bars_3D=1,'
    'E_CHECKBOX_Bars_Gradient=0,'
    'E_CHECKBOX_Bars_Highlight=0,'
    'E_CHOICE_Bars_Direction=Left,'
    'E_SLIDER_Bars_BarCount=4,'
    'E_TEXTCTRL_Bars_Cycles=8,'
    'T_TEXTCTRL_Fadein=.5,'
    'T_TEXTCTRL_Fadeout=.5'
)


def window_effects(model, layers=None):
    want = layers if layers is not None else CLEAR.get(model)
    layer_list = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for li, ids in enumerate(layer_list):
        if want is not None and li not in want:
            continue
        for eid in ids:
            s = x.xl('getEffectSettings', model=model, layer=str(li), id=str(eid))
            hits.append((li, eid, s.get('name'), int(s['startTime']), int(s['endTime'])))
    return hits


def clear_via_xsq():
    tree = ET.parse(XSQ)
    ee = tree.getroot().find('ElementEffects')
    removed = 0
    for el in ee.findall('Element'):
        name = el.get('name')
        if name not in CLEAR:
            continue
        want = CLEAR[name]
        for li, layer in enumerate(el.findall('EffectLayer')):
            if li not in want:
                continue
            for eff in list(layer.findall('Effect')):
                layer.remove(eff)
                removed += 1
    tree.write(XSQ, encoding='UTF-8', xml_declaration=True)
    return removed


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    rework = '--rework' in sys.argv

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info

    dirty = {m: hits for m in CLEAR if (hits := window_effects(m))}
    print(f'plan: {CANES} L0 red/white Bars (Single Line), C1 window '
          f'{WIN_START}-{WIN_END}; clear stale {GROUP} L1')
    if dirty:
        print(f'  currently dirty: {dirty}')

    if dry:
        print('dry-run: no writes')
        return

    if dirty:
        if not rework:
            raise SystemExit('targets not empty — rerun with --rework.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_via_xsq()
        print(f'cleared {removed} effects via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        assert int(x.xl('getOpenSequence').get('len', 0)) == SEQ_LEN

    if not clear_only:
        for c in CANES:
            x.add_effect(c, 0, 'Bars', SETTINGS, PALETTE, WIN_START, WIN_END)
            print(f'  + {c} L0 Bars ({WIN_START}-{WIN_END})')

    for c in CANES:
        got = window_effects(c)
        expected = 0 if clear_only else 1
        assert len(got) == expected, (c, got)

    assert not window_effects(GROUP), window_effects(GROUP)

    # Canes GROUP's own L0 Shockwave accents must survive untouched.
    l0 = window_effects(GROUP, {0})
    assert len(l0) == 2 and all(n == 'Shockwave' for _, _, n, *_ in l0), l0

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
