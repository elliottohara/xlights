"""Chorus 1 Rosa Grande — slow constant motion, Christmas Song style (v3).

v1 (rejected: seizure strobing) fired 20 short Shockwave hits. v2 (rejected:
buffer styles wrong) ran Overlay-Centered bases that ignore the prop's real
geometry. v3 is a direct port of the pros' Rosa stacks in
`/Volumes/Personal-Drive/xlights/Christmas/The Christmas Song .xsq`
(their ballad — one long slow effect per bank, 4-6 banks per section):

  - GE Rosa Grande GRP L0+L1 (whole-prop group, 2 layers): their hero move —
    the SAME slow 2-arm 3D-Inverted twisted Pinwheel on both layers, L1 with
    BufferTransform=Flip Horizontal, so the two sweeps counter-rotate through
    each other. Per Model Per Preview + PerPreviewCamera=2D + Blur 3 renders
    through the prop's real geometry. Gradient palette (red-gold-green).
  - GE Rosa Grande Torch Long Even GRP L0: slow 4-arm Pinwheel, Per Model
    Per Preview 2D, thickness 82, speed 2 (their verse recipe), deep red.
  - GE Rosa Grande Spoke GRP L0: Fan, Overlay-Centered, overscanned
    End_Radius=333, Blur 2 (their exact verse Fan), gold.
  - GE Rosa Grande Feather Long Odd GRP L0: Spirals, Overlay-Centered +
    Flip Horizontal, rotation 20 / movement 4 (their exact recipe), green.
  - GE Rosa Grande Outer Ball GRP L0: SingleStrand Bounce chase,
    8 rotations across the chorus, long fades (their exact recipe), white.

Window: 67275-93925 (Chorus 1 / Anthemic). No beat hits, no brightness
tricks — movement only, per user direction 2026-07-21.

Rework: --rework clears ALL layers of every bank this feature has ever
owned inside the window via direct .xsq edit (close -> strip -> reopen).

Run (xLights slot A):
    python3 rosa_c1_constant_motion.py [--dry-run] [--clear-only] [--rework]
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

WHOLE = 'GE Rosa Grande GRP'
SPOKE = 'GE Rosa Grande Spoke GRP'
TORCH_EVEN = 'GE Rosa Grande Torch Long Even GRP'
FEATHER_ODD = 'GE Rosa Grande Feather Long Odd GRP'
OUTER_BALL = 'GE Rosa Grande Outer Ball GRP'
# every bank v1/v2/v3 ever wrote in the window — all cleared on rework
OWNED = [WHOLE, SPOKE, TORCH_EVEN, FEATHER_ODD, OUTER_BALL,
         'GE Rosa Grande Ribbon GRP', 'GE Rosa Grande Ring GRP',
         'GE Rosa Grande Snowflake Spoke GRP',
         'GE Rosa Grande Torch Long Odd GRP']

# traditional palette
RED = '#B01212'
GREEN = '#0B6B3A'
GOLD = '#FFD89A'
WHITE = '#FFFFFF'

# gradient button for the mirrored whole-prop pinwheels (red -> gold -> green)
GRADIENT = ('Active=TRUE|Id=ID_BUTTON_Palette1|'
            'Values=x=0.000^c=#b01212;x=0.400^c=#ffd89a;'
            'x=0.700^c=#0b6b3a;x=1.000^c=#b01212|')


def flat_pal(c1, c2=None):
    p = f'C_BUTTON_Palette1={c1},C_CHECKBOX_Palette1=1'
    if c2:
        p += f',C_BUTTON_Palette2={c2},C_CHECKBOX_Palette2=1'
    return p


GRADIENT_PAL = f'C_BUTTON_Palette1={GRADIENT},C_CHECKBOX_Palette1=1'

# their hero: slow mirrored 2-arm inverted pinwheel pair on the whole prop
HERO_PINWHEEL = (
    'B_CHOICE_BufferStyle=Per Model Per Preview,'
    'B_CHOICE_PerPreviewCamera=2D,'
    'B_SLIDER_Blur=3,'
    'E_CHECKBOX_Pinwheel_Rotation=0,'
    'E_CHOICE_Pinwheel_3D=3D Inverted,'
    'E_CHOICE_Pinwheel_Style=New Render Method,'
    'E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,'
    'E_SLIDER_Pinwheel_ArmSize=271,'
    'E_SLIDER_Pinwheel_Arms=2,'
    'E_SLIDER_Pinwheel_Speed=3,'
    'E_SLIDER_Pinwheel_Thickness=40,'
    'E_SLIDER_Pinwheel_Twist=-65,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)
HERO_PINWHEEL_FLIP = HERO_PINWHEEL.replace(
    'B_CHOICE_PerPreviewCamera=2D,',
    'B_CHOICE_PerPreviewCamera=2D,B_CHOICE_BufferTransform=Flip Horizontal,')

# their verse torch pinwheel: 4 fat slow arms through the real torch geometry
TORCH_PINWHEEL = (
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
    'E_SLIDER_Pinwheel_Twist=-60,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

# their exact verse Fan on the Spoke bank (overscanned radius, blurred)
SPOKE_FAN = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
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

# their exact feather Spirals (flipped, gentle drift)
FEATHER_SPIRALS = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'B_CHOICE_BufferTransform=Flip Horizontal,'
    'E_CHECKBOX_Spirals_3D=1,'
    'E_SLIDER_Spirals_Count=2,'
    'E_SLIDER_Spirals_Rotation=20,'
    'E_SLIDER_Spirals_Thickness=50,'
    'E_TEXTCTRL_Spirals_Movement=4,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

# their exact outer-ball bounce chase
BALL_CHASE = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=Bounce from Left,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=10,'
    'E_SLIDER_Number_Chases=1,'
    'E_TEXTCTRL_Chase_Rotations=8,'
    'T_TEXTCTRL_Fadein=2.5,'
    'T_TEXTCTRL_Fadeout=2.5'
)

PLAN = [
    (WHOLE, 0, 'Pinwheel', HERO_PINWHEEL, GRADIENT_PAL),
    (WHOLE, 1, 'Pinwheel', HERO_PINWHEEL_FLIP, GRADIENT_PAL),
    (TORCH_EVEN, 0, 'Pinwheel', TORCH_PINWHEEL, flat_pal(RED)),
    (SPOKE, 0, 'Fan', SPOKE_FAN, flat_pal(GOLD)),
    (FEATHER_ODD, 0, 'Spirals', FEATHER_SPIRALS, flat_pal(GREEN)),
    (OUTER_BALL, 0, 'SingleStrand', BALL_CHASE, flat_pal(WHITE, GOLD)),
]


def window_effects(model):
    """(layer, id) pairs of effects on `model` touching the C1 window."""
    layers = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for li, ids in enumerate(layers):
        for eid in ids:
            s = x.xl('getEffectSettings', model=model, layer=li, id=eid)
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                hits.append((li, eid))
    return hits


def clear_window_via_xsq():
    """Strip this feature's window effects (ALL layers) from OWNED banks.
    Sequence must be CLOSED in xLights first."""
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
        print(f'  {m:38s} L{li} {e:13s} {WIN_START}-{WIN_END}')
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
