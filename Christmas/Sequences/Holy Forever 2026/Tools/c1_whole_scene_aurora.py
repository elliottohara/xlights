"""Chorus 1 experiment — Aurora Solid on Whole Scene (shared Per Preview field).

Same recipe as live Flakes/All Shrubs C1 aurora. One Whole Scene Per Preview
field means roof flakes + ground shrubs sample the same aurora. Clears the
separate Flakes GRP / All Shrubs GRP C1 shaders so those props don't double up
(restore via c1_flakes_blue_amber.py / c1_shrubs_aurora.py if rejected).

With ModelBlending, model-specific C1 beds (Rosa, house reveal, Mega Tree, …)
still render on those props and blend with this base — they don't hard-replace it.

Window: 67275–93925. Whole Scene L0 intro Snowflakes (0–41850) left alone.

Run (Slot A):
    python3 c1_whole_scene_aurora.py [--dry-run] [--clear-only] [--rework]
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

WHOLE = 'Whole Scene'
# Group-level copies — clear so flakes/shrubs join the shared field.
STALE = {
    'Flakes GRP': {0},
    'All Shrubs GRP': {0},
}
OWNED = {WHOLE: {0}}
CLEAR = {**OWNED, **STALE}

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
    print(f'plan: 1x Aurora Solid Shader (Per Preview) on {WHOLE} L0 '
          f'{WIN_START}-{WIN_END}; clear Flakes/All Shrubs C1 copies')
    if dirty:
        print(f'  will clear in-window: { {m: len(h) for m, h in dirty.items()} }')

    if dry:
        print('dry-run: no writes')
        return

    # Always clear stale group copies + any prior Whole Scene C1 when reworking.
    if dirty or not clear_only:
        need_clear = bool(dirty)
        if need_clear and WHOLE in dirty and not rework:
            raise SystemExit(
                f'C1 window not empty on {WHOLE} — rerun with --rework.')
        if need_clear:
            x.save(XSQ)
            x.xl('closeSequence', force='true', quiet='true')
            removed = clear_window_via_xsq()
            print(f'cleared {removed} window effects via .xsq')
            x.xl('openSequence', seq=XSQ, timeout=120)
            info = x.xl('getOpenSequence')
            assert int(info.get('len', 0)) == SEQ_LEN, info

    if not clear_only:
        x.add_effect(WHOLE, 0, 'Shader', SETTINGS, PALETTE, WIN_START, WIN_END)
        print(f'  + {WHOLE} L0 Aurora Solid Shader (Per Preview)')

    got = window_effects(WHOLE, {0})
    expected = 0 if clear_only else 1
    assert len(got) == expected, f'expected {expected} on {WHOLE}, got {got}'

    for m in STALE:
        left = window_effects(m)
        assert not left, f'stale leftovers on {m}: {left}'

    # Intro Whole Scene snow must remain.
    snow_ids = x.xl('getEffectIDs', model=WHOLE)['effects'][0]
    snow = [eid for eid in snow_ids
            if int(x.xl('getEffectSettings', model=WHOLE, layer='0',
                        id=str(eid))['endTime']) <= WIN_START]
    assert snow, 'Whole Scene L0 intro Snowflakes missing'
    s0 = x.xl('getEffectSettings', model=WHOLE, layer='0', id=str(snow[0]))
    assert s0['name'] == 'Snowflakes' and int(s0['startTime']) == 0, s0

    if not clear_only:
        s = x.xl('getEffectSettings', model=WHOLE, layer='0', id=str(got[0][1]))
        assert s['name'] == 'Shader', s
        sett = s.get('settings') or {}
        assert 'Aurora' in sett.get('E_0FILEPICKERCTRL_IFS', ''), sett
        assert sett.get('B_CHOICE_BufferStyle') == 'Per Preview', sett

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
