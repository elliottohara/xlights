"""Chorus 1 — Mega Tree glowing cross over a blue/amber Aurora shader,
with the same aurora bed under the Tree Topper's existing accent pops.

Look: the intro's Glowing Cross image holds the foreground of the Mega Tree
(TransparentBlack so the shader shows through), while Aurora.fs ribbons in
sapphire/navy/amber drift behind it. Tree Topper L3 carries a dimmer copy of
the same aurora so the star reads as part of the same sky; its L1/L2 white
On accents (bass hits) still pop on top.

Aurora.fs color mode "Alternate Color Palette (3 used) " maps palette slots
1-3 onto the shader's r/g/b channels (uC1*r + uC2*g + uC3*b, verified in the
shader source). The blue channel is the hottest (1.2x), so sapphire rides
uC3; the pulsing red channel gets amber; green gets a dim navy so the mix
doesn't wash to white.

Window: 67275-93925 (Anthemic downbeat -> V2 downbeat, same as the C1
spinner/house/flake set). 2 s fades, ballad dosage: long effects, no hits.

Run (Slot A):
    python3 c1_megatree_cross_shader.py [--dry-run] [--clear-only] [--rework]
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

# Aurora Solid = Aurora.fs with the central inversion blow-up clamped so the
# ribbons cover the whole field (user 2026-07-21: "don't like the hole in the
# middle... I want something that's more solid"). Gain/falloff retuned since
# all 18 taps now land everywhere.
SHADER = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
          'Holy Forever 2026/Media/Shaders/Aurora Solid.fs')
CROSS = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
         'Holy Forever 2026/Media/Images/Glowing Cross.png')

SAPPHIRE = '#2864FF'
NAVY = '#0A1E50'
AMBER = '#FFC800'

# uC1 <- slot 1 (amber, rides the pulsing r channel), uC2 <- slot 2 (dim
# navy on g), uC3 <- slot 3 (sapphire on the hot b channel).
AURORA_PALETTE = (
    f'C_BUTTON_Palette1={AMBER},C_CHECKBOX_Palette1=1,'
    f'C_BUTTON_Palette2={NAVY},C_CHECKBOX_Palette2=1,'
    f'C_BUTTON_Palette3={SAPPHIRE},C_CHECKBOX_Palette3=1'
)


def aurora_settings(intensity):
    return (
        f'E_0FILEPICKERCTRL_IFS={SHADER},'
        'E_CHECKBOX_SHADERXYZZY_uContRot=1,'
        'E_CHOICE_SHADERXYZZY_uColMode=Alternate Color Palette (3 used) ,'
        f'E_SLIDER_SHADERXYZZY_uIntensity={intensity},'
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

# Star: steady amber glow with sparkles (user 2026-07-21: no shader on the
# star). Sparkle color = palette slot 2 per xLights convention (ivory).
TOPPER_SETTINGS = 'T_TEXTCTRL_Fadein=2,T_TEXTCTRL_Fadeout=2'
TOPPER_PALETTE = (
    f'C_BUTTON_Palette1={AMBER},C_CHECKBOX_Palette1=1,'
    'C_BUTTON_Palette2=#EEEAE2,'
    'C_SLIDER_SparkleFrequency=40,'
    'C_SLIDER_Brightness=70'
)

# (target, layer, effect, settings, palette)
PLAN = [
    ('Mega Tree', 1, 'Pictures', CROSS_SETTINGS, CROSS_PALETTE),
    ('Mega Tree', 2, 'Shader', aurora_settings(80), AURORA_PALETTE),
    ('Tree Topper', 3, 'On', TOPPER_SETTINGS, TOPPER_PALETTE),
]
OWNED = sorted({(t, l) for t, l, *_ in PLAN})


def window_effects():
    hits = []
    for target, lyr in OWNED:
        layers = x.xl('getEffectIDs', model=target)['effects']
        if lyr >= len(layers):
            continue
        for eid in layers[lyr]:
            s = x.xl('getEffectSettings', model=target, layer=str(lyr),
                     id=str(eid))
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                hits.append((target, lyr, eid, s.get('name')))
    return hits


def clear_window_via_xsq():
    tree = ET.parse(XSQ)
    ee = tree.getroot().find('ElementEffects')
    owned_by_name = {}
    for t, l in OWNED:
        owned_by_name.setdefault(t, set()).add(l)
    removed = 0
    for el in ee.findall('Element'):
        lyrs = owned_by_name.get(el.get('name'))
        if not lyrs:
            continue
        for li, layer in enumerate(el.findall('EffectLayer')):
            if li not in lyrs:
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
    print(f'plan: cross+aurora {WIN_START}-{WIN_END} on '
          + ', '.join(f'{t} L{l} {e}' for t, l, e, *_ in PLAN))

    if dry:
        if dirty:
            print(f'window dirty: {dirty} (use --rework)')
        print('dry-run: no writes')
        return

    if dirty:
        if not rework and not clear_only:
            raise SystemExit('C1 window not empty on owned layers — '
                             'rerun with --rework.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        assert int(x.xl('getOpenSequence').get('len', 0)) == SEQ_LEN

    if not clear_only:
        for target, lyr, effect, settings, palette in PLAN:
            x.add_effect(target, lyr, effect, settings, palette,
                         WIN_START, WIN_END)
            print(f'  + {target} L{lyr} {effect}')

    got = window_effects()
    expected = 0 if clear_only else len(PLAN)
    assert len(got) == expected, got

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
