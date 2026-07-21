"""Chorus 1 snowflakes — Aurora shader on Flakes GRP, Per Model Per Preview.

v1 REJECTED: per-bank Color Wash + Kick Twinkles on Outline/Spokes/Arms —
looked wrong and was heavy.
v2 REJECTED: sapphire Color Wash (Single Line) + Color-panel music sparkles —
user replaced it after approving the Mega Tree aurora ("apply the same shader
to the snowflakes, render per model per preview, instead of the blue with
sparkles").
v3: Aurora Solid shader (blue/amber alternate palette) on Flakes GRP L0,
Per Model Per Preview — each flake rendered its own aurora.
v4 (CURRENT — user hand-tuned in the GUI 2026-07-21): render style
**Per Preview** (one aurora field sweeping across ALL flakes), continuous
rotation uRotate=-6083 (-60.83 deg/s), uZoom=301 (3.01x). Values read back
from the live session; do not "correct" them.

`--rework` also strips the stale v1 per-bank pass (Outline/Spokes/Arms).

Window: 67275–93925. Outline L0 V1 chord Shockwave @32200 left alone.

Run (Slot A):
    python3 c1_flakes_blue_amber.py [--dry-run] [--clear-only] [--rework]
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

FLAKES = 'Flakes GRP'
# Stale v1 part-bank pass — clear in-window only (Outline L0 V1 Shockwave stays).
STALE = {
    'Flakes Outline All GRP': {1},
    'Flakes Spokes All GRP': {0, 1},
    'Flakes Arms GRP': {0, 1},
}
OWNED = {FLAKES: {0}}
CLEAR = {**OWNED, **STALE}

# Aurora Solid = Aurora.fs with the central inversion blow-up clamped
# (no center hole; see c1_megatree_cross_shader.py).
SHADER = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
          'Holy Forever 2026/Media/Shaders/Aurora Solid.fs')

SAPPHIRE = '#2864FF'
NAVY = '#0A1E50'
AMBER = '#FFC800'

# Same channel mapping as the Mega Tree C1 aurora (c1_megatree_cross_shader):
# uC1 <- amber on the pulsing r channel, uC2 <- dim navy on g, uC3 <- sapphire
# on the hot b channel.
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
          f'on {FLAKES} L0 {WIN_START}-{WIN_END}')
    if dirty:
        print(f'  will clear in-window: { {m: len(h) for m, h in dirty.items()} }')

    if dry:
        print('dry-run: no writes')
        return

    if dirty:
        if not rework and FLAKES in dirty:
            raise SystemExit(
                f'C1 window not empty on {list(dirty)} — rerun with --rework.')
        if not rework and FLAKES not in dirty:
            # stale banks only — still need rework path to strip them
            rework = True
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} window effects via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        info = x.xl('getOpenSequence')
        assert int(info.get('len', 0)) == SEQ_LEN, info

    if not clear_only:
        x.add_effect(FLAKES, 0, 'Shader', SETTINGS, PALETTE, WIN_START, WIN_END)
        print(f'  + {FLAKES} L0 Aurora Solid Shader (Per Preview)')

    got = window_effects(FLAKES, {0})
    expected = 0 if clear_only else 1
    assert len(got) == expected, f'expected {expected} on Flakes GRP, got {got}'

    for m in STALE:
        left = window_effects(m)
        assert not left, f'stale leftovers on {m}: {left}'

    # V1 chord Shockwave still on Outline L0
    outline_l0 = x.xl('getEffectIDs', model='Flakes Outline All GRP')['effects'][0]
    assert outline_l0, 'Outline L0 emptied — V1 Shockwave must remain'
    s0 = x.xl('getEffectSettings', model='Flakes Outline All GRP',
              layer='0', id=str(outline_l0[0]))
    assert int(s0['startTime']) == 32200, s0

    if not clear_only:
        s = x.xl('getEffectSettings', model=FLAKES, layer='0', id=str(got[0][1]))
        assert s['name'] == 'Shader', s
        sett = s.get('settings') or {}
        assert 'Aurora' in sett.get('E_0FILEPICKERCTRL_IFS', ''), sett
        assert sett.get('B_CHOICE_BufferStyle') == 'Per Preview', sett

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
