"""Chorus 1 shrubs — same Aurora Solid shader as Flakes GRP (user hand-tune).

Mirrors `c1_flakes_blue_amber.py` v4: `Aurora Solid.fs` on `All Shrubs GRP` L0,
`Per Preview` (one aurora field across the whole shrub bank), continuous
rotation uRotate=-6083, uZoom=301, blue/amber alternate palette, Speed 60,
intensity 220, 2 s fades. Window 67275–93925.

Does not touch individual shrub/rose-bush members (V1 piano notes stay).

Run (Slot A):
    python3 c1_shrubs_aurora.py [--dry-run] [--clear-only] [--rework]
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

SHRUBS = 'All Shrubs GRP'
OWNED = {SHRUBS: {0}}
CLEAR = OWNED

# Same shader + settings as live Flakes GRP C1 (c1_flakes_blue_amber.py v4).
SHADER = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
          'Holy Forever 2026/Media/Shaders/Aurora Solid.fs')

SAPPHIRE = '#2864FF'
NAVY = '#0A1E50'
AMBER = '#FFC800'

PALETTE = (
    f'C_BUTTON_Palette1={AMBER},C_CHECKBOX_Palette1=1,'
    f'C_BUTTON_Palette2={NAVY},C_CHECKBOX_Palette2=1,'
    f'C_BUTTON_Palette3={SAPPHIRE},C_CHECKBOX_Palette3=1'
)

SETTINGS = (
    'B_CHOICE_BufferStyle=Per Preview,'
    f'E_0FILEPICKERCTRL_IFS={SHADER},'
    'E_CHECKBOX_SHADERXYZZY_uContRot=1,'
    'E_CHOICE_SHADERXYZZY_uColMode=Alternate Color Palette (3 used) ,'
    'E_SLIDER_SHADERXYZZY_uIntensity=220,'
    'E_SLIDER_SHADERXYZZY_uOffsetX=0,'
    'E_SLIDER_SHADERXYZZY_uOffsetY=0,'
    'E_SLIDER_SHADERXYZZY_uRotate=-6083,'
    'E_SLIDER_SHADERXYZZY_uZoom=301,'
    'E_SLIDER_Shader_Speed=60,'
    'E_TEXTCTRL_Shader_LeadIn=0,'
    'E_TEXTCTRL_Shader_Offset_X=0,'
    'E_TEXTCTRL_Shader_Offset_Y=0,'
    'E_TEXTCTRL_Shader_Zoom=0,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
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
    print(f'plan: 1x Aurora Solid Shader (Per Preview, rotating, blue/amber) '
          f'on {SHRUBS} L0 {WIN_START}-{WIN_END}')
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
        x.add_effect(SHRUBS, 0, 'Shader', SETTINGS, PALETTE, WIN_START, WIN_END)
        print(f'  + {SHRUBS} L0 Aurora Solid Shader (Per Preview)')

    got = window_effects(SHRUBS, {0})
    expected = 0 if clear_only else 1
    assert len(got) == expected, f'expected {expected} on {SHRUBS}, got {got}'

    if not clear_only:
        s = x.xl('getEffectSettings', model=SHRUBS, layer='0', id=str(got[0][1]))
        assert s['name'] == 'Shader', s
        sett = s.get('settings') or {}
        assert 'Aurora' in sett.get('E_0FILEPICKERCTRL_IFS', ''), sett
        assert sett.get('B_CHOICE_BufferStyle') == 'Per Preview', sett

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
