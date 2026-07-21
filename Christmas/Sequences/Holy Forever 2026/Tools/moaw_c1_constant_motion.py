"""Chorus 1 BMOAW Left/Right — red/amber constant motion (v2).

v1 REJECTED: guessed Per Model Per Preview pinwheels (Rosa pattern) — wrong
for MOAW. Pros' mapped MOAW banks almost never use PMPP for continuous
motion; survey of 8 mapped sequences on this layout (2026-07-21):

  Pinwheel  → buffer OMITTED (default) + Blur 4, 3D Inverted, 7 arms
              (Hallelujah.xsq — identical clone across all MOAW banks)
  Galaxy    → B_CHOICE_BufferStyle=Per Preview + PerPreviewCamera=2D
              (Hallelujah.xsq)
  SingleStrand → Single Line + Chase_Group_All=1, Bounce from Left
              (Carol of the Bells Instrumental.xsq)
  Bars      → Overlay - Scaled (Feliz Navidad.xsq)
  Color Wash→ Single Line (corpus histogram)

v2 ports those exact buffer styles. Same C1 window / ballad dosage as Rosa
(67275–93925, one long effect per bank, 2 s fades, red/amber, no white).

Run (Slot A):
    python3 moaw_c1_constant_motion.py [--dry-run] [--clear-only] [--rework]
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

WHOLE = 'GE MOAW GRP'
SPOKES = 'GE MOAW Spokes GRP'
SNOWFLAKE = 'GE MOAW Snowflake Spoke GRP'
SWAG = 'GE MOAW Swag GRP'
DIAMONDS = 'GE MOAW Diamonds GRP'
OWNED = [WHOLE, SPOKES, SNOWFLAKE, SWAG, DIAMONDS]

RED = '#B01212'
GOLD = '#FFD89A'

GRADIENT = ('Active=TRUE|Id=ID_BUTTON_Palette1|'
            'Values=x=0.000^c=#b01212;x=0.450^c=#ffd89a;'
            'x=0.750^c=#b01212;x=1.000^c=#ffd89a|')
GRADIENT_PAL = f'C_BUTTON_Palette1={GRADIENT},C_CHECKBOX_Palette1=1'


def flat_pal(*colors):
    parts = []
    for i, c in enumerate(colors, 1):
        parts.append(f'C_BUTTON_Palette{i}={c},C_CHECKBOX_Palette{i}=1')
    return ','.join(parts)


# Hallelujah MOAW Pinwheel — NO B_CHOICE_BufferStyle (default). Centered for
# this layout (their XC/YC/ArmSize were a SubBuffer hack for their preview).
HERO_PINWHEEL = (
    'B_SLIDER_Blur=4,'
    'E_CHECKBOX_Pinwheel_Rotation=1,'
    'E_CHOICE_Pinwheel_3D=3D Inverted,'
    'E_CHOICE_Pinwheel_Style=New Render Method,'
    'E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,'
    'E_SLIDER_Pinwheel_ArmSize=100,'
    'E_SLIDER_Pinwheel_Arms=7,'
    'E_SLIDER_Pinwheel_Speed=2,'
    'E_SLIDER_Pinwheel_Thickness=80,'
    'E_SLIDER_Pinwheel_Twist=67,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)
HERO_PINWHEEL_FLIP = (
    'B_CHOICE_BufferTransform=Flip Horizontal,' + HERO_PINWHEEL
)

# Carol of the Bells — Single Line + Group_All bounce (rotations scaled for
# ~26.6 s window; their 0.4 over 7.5 s ≈ same visual speed at ~1.4).
SPOKES_CHASE = (
    'B_CHOICE_BufferStyle=Single Line,'
    'E_CHECKBOX_Chase_Group_All=1,'
    'E_CHOICE_Chase_Type1=Bounce from Left,'
    'E_CHOICE_Fade_Type=From Head,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=28,'
    'E_SLIDER_Number_Chases=1,'
    'E_TEXTCTRL_Chase_Rotations=1.4,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

# Hallelujah Galaxy — Per Preview + 2D (NOT Per Model Per Preview).
SNOW_GALAXY = (
    'B_CHOICE_BufferStyle=Per Preview,'
    'B_CHOICE_PerPreviewCamera=2D,'
    'E_CHECKBOX_Galaxy_Blend_Edges=1,'
    'E_CHECKBOX_Galaxy_Inward=0,'
    'E_CHECKBOX_Galaxy_Reverse=0,'
    'E_NOTEBOOK_Galaxy=End,'
    'E_SLIDER_Galaxy_Accel=0,'
    'E_SLIDER_Galaxy_CenterX=50,'
    'E_SLIDER_Galaxy_CenterY=50,'
    'E_SLIDER_Galaxy_Duration=20,'
    'E_SLIDER_Galaxy_End_Radius=0,'
    'E_SLIDER_Galaxy_End_Width=124,'
    'E_SLIDER_Galaxy_Revolutions=720,'
    'E_SLIDER_Galaxy_Start_Angle=0,'
    'E_SLIDER_Galaxy_Start_Radius=199,'
    'E_SLIDER_Galaxy_Start_Width=92,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

# Feliz Navidad Bars — Overlay - Scaled.
SWAG_BARS = (
    'B_CHOICE_BufferStyle=Overlay - Scaled,'
    'E_CHECKBOX_Bars_3D=1,'
    'E_CHECKBOX_Bars_Gradient=0,'
    'E_CHECKBOX_Bars_Highlight=0,'
    'E_CHOICE_Bars_Direction=Right,'
    'E_SLIDER_Bars_BarCount=3,'
    'E_TEXTCTRL_Bars_Cycles=2.0,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

# Corpus Color Wash on MOAW — Single Line.
DIAMOND_WASH = (
    'B_CHOICE_BufferStyle=Single Line,'
    'E_CHECKBOX_ColorWash_HFade=1,'
    'E_CHECKBOX_ColorWash_VFade=0,'
    'E_TEXTCTRL_ColorWash_Cycles=2.0,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

PLAN = [
    (WHOLE, 0, 'Pinwheel', HERO_PINWHEEL, GRADIENT_PAL),
    (WHOLE, 1, 'Pinwheel', HERO_PINWHEEL_FLIP, GRADIENT_PAL),
    (SPOKES, 0, 'SingleStrand', SPOKES_CHASE, flat_pal(GOLD, RED)),
    (SNOWFLAKE, 0, 'Galaxy', SNOW_GALAXY, flat_pal(RED, GOLD)),
    (SWAG, 0, 'Bars', SWAG_BARS, flat_pal(RED, GOLD)),
    (DIAMONDS, 0, 'Color Wash', DIAMOND_WASH, flat_pal(GOLD, RED)),
]


def window_effects(model):
    layers = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for li, ids in enumerate(layers):
        for eid in ids:
            s = x.xl('getEffectSettings', model=model, layer=str(li), id=str(eid))
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                hits.append((li, eid))
    return hits


def clear_window_via_xsq():
    tree = ET.parse(XSQ)
    root = tree.getroot()
    removed = 0
    for el in root.find('ElementEffects').findall('Element'):
        if el.get('name') not in OWNED:
            continue
        for layer in el.findall('EffectLayer'):
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

    dirty = {b: ids for b in OWNED if (ids := window_effects(b))}
    print('v2 — measured MOAW render styles (default pinwheel / Single Line / '
          'Per Preview Galaxy / Overlay-Scaled Bars)')
    for m, li, e, _, p in PLAN:
        print(f'  {m:34s} L{li} {e:13s} {WIN_START}-{WIN_END}')
    print(f'{len(PLAN)} effects planned')

    if dry:
        if dirty:
            print(f'window dirty on: {list(dirty)} (use --rework)')
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
        for model, layer, effect, settings, palette in PLAN:
            x.add_effect(model, layer, effect, settings, palette,
                         WIN_START, WIN_END)
            print(f'  + {model} L{layer} {effect}')

    got = sum(len(window_effects(b)) for b in OWNED)
    expected = 0 if clear_only else len(PLAN)
    assert got == expected, f'expected {expected} in window, found {got}'

    x.save(XSQ)
    print(f'saved {XSQ} ({got} effects live)')


if __name__ == '__main__':
    main()
