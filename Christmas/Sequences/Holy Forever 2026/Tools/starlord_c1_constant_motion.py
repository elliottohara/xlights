"""Chorus 1 Starlords — slow constant motion, contrasting the Rosa (blue-led).

Companion to rosa_c1_constant_motion.py (v3, user-approved). Same window
(67275-93925, Chorus 1 / Anthemic), same style rules (long slow effects,
geometry-aware render styles, 2 s fades, no hits) but CONTRASTING motion,
ported from the pros' Starlord verse stack in
`/Volumes/Personal-Drive/xlights/Christmas/The Christmas Song .xsq`:

  Rosa (approved)                     Starlord (this script)
  - thin 2-arm 3D-Inverted sweeps     - fat 4-arm 3D pinwheels, twist
    pulling INWARD                      wobbling via value curve
  - red-led                           - blue-led
  - mirrored pair on whole GRP        - Fan underneath + mirrored pair
                                        (their exact verse trio)
  - Overlay Spirals on feathers       - per-plunger VERTICAL Spiral drips
                                        (Vertical Per Model/Strand)

Banks (both fixtures via the shared GRPs):
  - GE Starlord GRP L0: Fan, Per Model Per Preview 2D + Blur 2 (their
    exact verse Fan), gold.
  - GE Starlord GRP L1+L2: identical 4-arm 3D Pinwheel (Speed 2,
    Thickness 82, Twist value-curve wobble), Per Model Per Preview 2D,
    L2 = Flip Horizontal -> counter-rotating pair. Blue gradient.
  - GE Starlord Plunger All GRP L0: Spirals on Vertical Per Model/Strand
    (each plunger drips its own spiral - their exact recipe), sapphire.
  - GE Starlord Spoke GRP L0: slow SingleStrand chase, Vertical Per
    Model/Strand, 3 chases (TSO recipe, slowed), white.
  - GE Starlord Cross GRP L0: SingleStrand From Middle drip, Vertical Per
    Model/Strand (Imperial recipe, slowed), ice blue.

Plunger All L0 also holds the V1 chord-bank Shockwave (25550) — outside
the window; only window effects are ever cleared on --rework.

Run (xLights slot A):
    python3 starlord_c1_constant_motion.py [--dry-run] [--clear-only] [--rework]
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

WHOLE = 'GE Starlord GRP'
PLUNGER = 'GE Starlord Plunger All GRP'
SPOKE = 'GE Starlord Spoke GRP'
CROSS = 'GE Starlord Cross GRP'
OWNED = [WHOLE, PLUNGER, SPOKE, CROSS]

SAPPHIRE = '#2864FF'
ICE = '#8080FF'
GOLD = '#FFD89A'
WHITE = '#FFFFFF'

# blue-led gradient for the mirrored pinwheel pair (blue -> gold -> white)
GRADIENT = ('Active=TRUE|Id=ID_BUTTON_Palette1|'
            'Values=x=0.000^c=#2864ff;x=0.400^c=#ffd89a;'
            'x=0.700^c=#ffffff;x=1.000^c=#2864ff|')
GRADIENT_PAL = f'C_BUTTON_Palette1={GRADIENT},C_CHECKBOX_Palette1=1'

# their twist wobble curve (verbatim from The Christmas Song verse pinwheels)
TWIST_VC = ('Active=TRUE|Id=ID_VALUECURVE_Pinwheel_Twist|Type=Custom|'
            'Min=-360.00|Max=360.00|RV=TRUE|'
            'Values=0.00:0.19;0.11:0.49;0.24:0.18;0.37:0.52;0.49:0.60;'
            '0.62:0.57;0.74:0.49;0.88:0.53;1.00:0.18|')


def flat_pal(c1, c2=None):
    p = f'C_BUTTON_Palette1={c1},C_CHECKBOX_Palette1=1'
    if c2:
        p += f',C_BUTTON_Palette2={c2},C_CHECKBOX_Palette2=1'
    return p


WHOLE_FAN = (
    'B_CHOICE_BufferStyle=Per Model Per Preview,'
    'B_CHOICE_PerPreviewCamera=2D,'
    'B_SLIDER_Blur=2,'
    'E_CHECKBOX_Fan_Blend_Edges=1,'
    'E_NOTEBOOK_Fan=Position,'
    'E_SLIDER_Fan_Blade_Angle=90,'
    'E_SLIDER_Fan_Blade_Width=100,'
    'E_SLIDER_Fan_CenterX=50,'
    'E_SLIDER_Fan_CenterY=50,'
    'E_SLIDER_Fan_Duration=100,'
    'E_SLIDER_Fan_Element_Width=100,'
    'E_SLIDER_Fan_End_Radius=333,'
    'E_SLIDER_Fan_Num_Blades=3,'
    'E_SLIDER_Fan_Num_Elements=1,'
    'E_SLIDER_Fan_Revolutions=720,'
    'E_SLIDER_Fan_Start_Radius=1,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

WHOLE_PINWHEEL = (
    'B_CHOICE_BufferStyle=Per Model Per Preview,'
    'B_CHOICE_PerPreviewCamera=2D,'
    'E_CHECKBOX_Pinwheel_Rotation=1,'
    'E_CHOICE_Pinwheel_3D=3D,'
    'E_CHOICE_Pinwheel_Style=New Render Method,'
    'E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,'
    'E_SLIDER_Pinwheel_ArmSize=100,'
    'E_SLIDER_Pinwheel_Arms=4,'
    'E_SLIDER_Pinwheel_Speed=2,'
    'E_SLIDER_Pinwheel_Thickness=82,'
    f'E_VALUECURVE_Pinwheel_Twist={TWIST_VC},'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)
WHOLE_PINWHEEL_FLIP = WHOLE_PINWHEEL.replace(
    'B_CHOICE_PerPreviewCamera=2D,',
    'B_CHOICE_PerPreviewCamera=2D,B_CHOICE_BufferTransform=Flip Horizontal,')

PLUNGER_SPIRALS = (
    'B_CHOICE_BufferStyle=Vertical Per Model/Strand,'
    'E_CHECKBOX_Spirals_3D=1,'
    'E_SLIDER_Spirals_Count=2,'
    'E_SLIDER_Spirals_Rotation=20,'
    'E_SLIDER_Spirals_Thickness=50,'
    'E_TEXTCTRL_Spirals_Movement=2,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

SPOKE_CHASE = (
    'B_CHOICE_BufferStyle=Vertical Per Model/Strand,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=Left-Right,'
    'E_CHOICE_Fade_Type=From Head,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=10,'
    'E_SLIDER_Number_Chases=3,'
    'E_TEXTCTRL_Chase_Rotations=4,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

CROSS_DRIP = (
    'B_CHOICE_BufferStyle=Vertical Per Model/Strand,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=From Middle,'
    'E_CHOICE_Fade_Type=From Head,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=45,'
    'E_SLIDER_Number_Chases=1,'
    'E_TEXTCTRL_Chase_Rotations=5.5,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

PLAN = [
    (WHOLE, 0, 'Fan', WHOLE_FAN, flat_pal(GOLD)),
    (WHOLE, 1, 'Pinwheel', WHOLE_PINWHEEL, GRADIENT_PAL),
    (WHOLE, 2, 'Pinwheel', WHOLE_PINWHEEL_FLIP, GRADIENT_PAL),
    (PLUNGER, 0, 'Spirals', PLUNGER_SPIRALS, flat_pal(SAPPHIRE)),
    (SPOKE, 0, 'SingleStrand', SPOKE_CHASE, flat_pal(WHITE)),
    (CROSS, 0, 'SingleStrand', CROSS_DRIP, flat_pal(ICE, SAPPHIRE)),
]


def window_effects(model):
    layers = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for li, ids in enumerate(layers):
        for eid in ids:
            s = x.xl('getEffectSettings', model=model, layer=li, id=eid)
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                hits.append((li, eid))
    return hits


def clear_window_via_xsq():
    """Strip window effects (all layers) from OWNED banks. Sequence CLOSED."""
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
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'
    assert info.get('len') == SEQ_LEN, f'unexpected len: {info}'

    dirty = {b: ids for b in OWNED if (ids := window_effects(b))}
    for m, li, e, _, p in PLAN:
        print(f'  {m:34s} L{li} {e:13s} {WIN_START}-{WIN_END}')
    print(f'{len(PLAN)} slow continuous effects planned')

    if dry:
        if dirty:
            print(f'window currently dirty on: {list(dirty)} (use --rework)')
        print('dry-run: no writes')
        return

    if dirty:
        if not rework:
            raise SystemExit(
                f'C1 window not empty on {list(dirty)} — rerun with --rework. '
                f'Nothing written.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} window effects via .xsq')
        x.xl('openSequence', seq=XSQ)
        info = x.xl('getOpenSequence')
        assert info.get('len') == SEQ_LEN, f'reopen failed: {info}'

    if not clear_only:
        for model, layer, effect, settings, palette in PLAN:
            x.add_effect(model, layer, effect, settings, palette,
                         WIN_START, WIN_END)

    got = sum(len(window_effects(b)) for b in OWNED)
    expected = 0 if clear_only else len(PLAN)
    assert got == expected, f'expected {expected} in window, found {got}'

    x.save(XSQ)
    print(f'saved {XSQ} ({got} effects live in C1 window)')


if __name__ == '__main__':
    main()
