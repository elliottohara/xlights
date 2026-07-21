"""Chorus 1 — driveway + garden borders, same Rosa reveal as Verts.

`Yard Borders` = Rose Bed Border, Front Garden Border, Driveway Left/Right.
L1 Rosa red (#B01212) Color Wash + L0 narrow Single Line Marquee with
`1 reveals 2` and Rosa amber (#FFD89A) mask — verbatim Verts recipe from
`c1_house_icicles.py`.

Window: 67275–93925. 2 s fades.

Run (Slot A):
    python3 c1_yard_borders_marquee.py [--dry-run] [--clear-only] [--rework]
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

TARGET = 'Yard Borders'
OWNED = {TARGET: {0, 1}}
CLEAR = OWNED

ROSA_RED = '#B01212'
ROSA_GOLD = '#FFD89A'

MARQUEE = (
    'B_CHOICE_BufferStyle=Single Line,'
    'E_CHECKBOX_Marquee_PixelOffsets=0,'
    'E_CHECKBOX_Marquee_Reverse=0,'
    'E_CHECKBOX_Marquee_WrapX=0,'
    'E_NOTEBOOK_Marquee=Settings,'
    'E_SLIDER_MarqueeXC=0,'
    'E_SLIDER_MarqueeYC=0,'
    'E_SLIDER_Marquee_Band_Size=4,'
    'E_SLIDER_Marquee_ScaleX=100,'
    'E_SLIDER_Marquee_ScaleY=100,'
    'E_SLIDER_Marquee_Skip_Size=9,'
    'E_SLIDER_Marquee_Speed=2,'
    'E_SLIDER_Marquee_Stagger=0,'
    'E_SLIDER_Marquee_Start=0,'
    'E_SLIDER_Marquee_Thickness=2,'
    'T_CHOICE_LayerMethod=1 reveals 2,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

WASH = (
    'E_CHECKBOX_ColorWash_HFade=0,'
    'E_CHECKBOX_ColorWash_VFade=0,'
    'E_TEXTCTRL_ColorWash_Cycles=1.0,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

PAL_MASK = f'C_BUTTON_Palette1={ROSA_GOLD},C_CHECKBOX_Palette1=1,C_SLIDER_Brightness=100'
PAL_WASH = f'C_BUTTON_Palette1={ROSA_RED},C_CHECKBOX_Palette1=1,C_SLIDER_Brightness=80'


def window_effects(model, layers=None):
    want = layers if layers is not None else CLEAR.get(model)
    layer_list = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for li, ids in enumerate(layer_list):
        if want is not None and li not in want:
            continue
        for eid in ids:
            s = x.xl('getEffectSettings', model=model, layer=str(li), id=str(eid))
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                hits.append((li, eid, s.get('name')))
    return hits


def clear_window_via_xsq():
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
                s, e = int(eff.get('startTime')), int(eff.get('endTime'))
                if e > WIN_START and s < WIN_END:
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
    print(f'plan: {TARGET} L1 Rosa wash + L0 amber Marquee (1 reveals 2, '
          f'Single Line) {WIN_START}-{WIN_END}')
    if dirty:
        print(f'  will clear in-window: { {m: len(h) for m, h in dirty.items()} }')

    if dry:
        print('dry-run: no writes')
        return

    if dirty:
        if not rework:
            raise SystemExit(
                f'C1 window not empty on {list(dirty)} — rerun with --rework.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} window effects via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        info = x.xl('getOpenSequence')
        assert int(info.get('len', 0)) == SEQ_LEN, info

    if not clear_only:
        x.add_effect(TARGET, 1, 'Color Wash', WASH, PAL_WASH, WIN_START, WIN_END)
        x.add_effect(TARGET, 0, 'Marquee', MARQUEE, PAL_MASK, WIN_START, WIN_END)
        print(f'  + {TARGET} L1 Color Wash + L0 Marquee')

    got = window_effects(TARGET)
    expected = 0 if clear_only else 2
    assert len(got) == expected, f'expected {expected} on {TARGET}, got {got}'

    if not clear_only:
        by_layer = {li: name for li, _eid, name in got}
        assert by_layer.get(0) == 'Marquee', by_layer
        assert by_layer.get(1) == 'Color Wash', by_layer
        s0 = x.xl('getEffectSettings', model=TARGET, layer='0',
                  id=str(next(e for li, e, _ in got if li == 0)))
        assert s0['settings'].get('B_CHOICE_BufferStyle') == 'Single Line', s0
        assert s0['settings'].get('T_CHOICE_LayerMethod') == '1 reveals 2', s0

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
