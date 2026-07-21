"""Chorus 1 — Toni Flat Tree same as Mega Tree: glowing cross over Aurora.

Mirrors `c1_megatree_cross_shader.py` on `Toni - Flat Tree` only (no Tree
Topper). L1 = Glowing Cross Pictures (TransparentBlack), L2 = Aurora Solid
blue/amber shader. Window 67275–93925, 2 s fades.

Run (Slot A):
    python3 c1_toni_flat_tree_cross_shader.py [--dry-run] [--clear-only] [--rework]
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

TONI = 'Toni - Flat Tree'

SHADER = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
          'Holy Forever 2026/Media/Shaders/Aurora Solid.fs')
CROSS = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
         'Holy Forever 2026/Media/Images/Glowing Cross.png')

SAPPHIRE = '#2864FF'
NAVY = '#0A1E50'
AMBER = '#FFC800'

AURORA_PALETTE = (
    f'C_BUTTON_Palette1={AMBER},C_CHECKBOX_Palette1=1,'
    f'C_BUTTON_Palette2={NAVY},C_CHECKBOX_Palette2=1,'
    f'C_BUTTON_Palette3={SAPPHIRE},C_CHECKBOX_Palette3=1'
)

AURORA_SETTINGS = (
    f'E_0FILEPICKERCTRL_IFS={SHADER},'
    'E_CHECKBOX_SHADERXYZZY_uContRot=1,'
    'E_CHOICE_SHADERXYZZY_uColMode=Alternate Color Palette (3 used) ,'
    'E_SLIDER_SHADERXYZZY_uIntensity=80,'
    'E_SLIDER_SHADERXYZZY_uOffsetX=0,'
    'E_SLIDER_SHADERXYZZY_uOffsetY=0,'
    'E_SLIDER_SHADERXYZZY_uRotate=0,'
    'E_SLIDER_SHADERXYZZY_uZoom=100,'
    'E_SLIDER_Shader_Speed=60,'
    'E_TEXTCTRL_Shader_LeadIn=0,'
    'E_TEXTCTRL_Shader_Offset_X=0,'
    'E_TEXTCTRL_Shader_Offset_Y=0,'
    'E_TEXTCTRL_Shader_Zoom=0,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

CROSS_SETTINGS = (
    'E_CHECKBOX_Pictures_PixelOffsets=0,'
    'E_CHECKBOX_Pictures_Shimmer=0,'
    'E_CHECKBOX_Pictures_TransparentBlack=1,'
    'E_CHECKBOX_Pictures_WrapX=0,'
    'E_CHOICE_Pictures_Direction=none,'
    'E_CHOICE_Scaling=Scale To Fit,'
    'E_SLIDER_PicturesXC=0,'
    'E_SLIDER_PicturesYC=0,'
    'E_SLIDER_Pictures_EndScale=100,'
    'E_SLIDER_Pictures_StartScale=100,'
    f'E_TEXTCTRL_Pictures_Filename={CROSS},'
    'E_TEXTCTRL_Pictures_FrameRateAdj=1.0,'
    'E_TEXTCTRL_Pictures_Speed=1.0,'
    'E_TEXTCTRL_Pictures_TransparentBlack=30,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)
CROSS_PALETTE = 'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'

# Same layer stack as Mega Tree C1 (L1 cross over L2 aurora).
PLAN = [
    (TONI, 1, 'Pictures', CROSS_SETTINGS, CROSS_PALETTE),
    (TONI, 2, 'Shader', AURORA_SETTINGS, AURORA_PALETTE),
]
OWNED = {TONI: {1, 2}}
CLEAR = OWNED


def window_effects(model=None, layers=None):
    hits = []
    models = [model] if model else list(CLEAR)
    for m in models:
        want = layers if layers is not None else CLEAR[m]
        layer_list = x.xl('getEffectIDs', model=m)['effects']
        for li, ids in enumerate(layer_list):
            if li not in want:
                continue
            for eid in ids:
                s = x.xl('getEffectSettings', model=m, layer=str(li), id=str(eid))
                if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                    hits.append((m, li, eid, s.get('name')))
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

    dirty = window_effects()
    print(f'plan: {TONI} L1 Glowing Cross + L2 Aurora Solid '
          f'{WIN_START}-{WIN_END} (Mega Tree twin)')
    if dirty:
        print(f'  will clear in-window: {dirty}')

    if dry:
        print('dry-run: no writes')
        return

    if dirty:
        if not rework:
            raise SystemExit(
                f'C1 window not empty on {TONI} — rerun with --rework.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} window effects via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        info = x.xl('getOpenSequence')
        assert int(info.get('len', 0)) == SEQ_LEN, info

    if not clear_only:
        for target, lyr, effect, settings, palette in PLAN:
            x.add_effect(target, lyr, effect, settings, palette,
                         WIN_START, WIN_END)
            print(f'  + {target} L{lyr} {effect}')

    got = window_effects()
    expected = 0 if clear_only else len(PLAN)
    assert len(got) == expected, got

    if not clear_only:
        by_layer = {li: name for _m, li, _e, name in got}
        assert by_layer.get(1) == 'Pictures', by_layer
        assert by_layer.get(2) == 'Shader', by_layer

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
