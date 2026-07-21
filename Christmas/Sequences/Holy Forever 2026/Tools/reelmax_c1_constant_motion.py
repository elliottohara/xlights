"""Chorus 1 Reel Maxes — slow constant motion, blue-led (companion #3).

Completes the C1 spinner set: Rosa (red-led, thin inverted sweeps) and
Starlord (blue-led, fat wobble pinwheels + fan) are approved/live; this adds
both Reel Maxes via the shared GRPs, blue like the Starlords but with the
Reel Max's own motion vocabulary (measured across the mapped pro sequences —
crisp twisted pinwheel + linear chases on its ring banks):

  - GE Reel Max GRP L0+L1: mirrored pair of 4-arm 3D Pinwheels with fixed
    Twist=82 / Thickness=47 (the pros' signature Reel Max whole-prop
    pinwheel, slowed to Speed 3), Per Model Per Preview 2D so each fixture
    spins about its own center; L1 Flip Horizontal -> counter-rotation.
    Blue gradient (sapphire -> gold -> white), same family as Starlord.
  - GE Reel Max Spokes GRP L0: thin fast-ish Spirals (Rotation 85,
    Thickness 10, Movement 4, flipped) - their spoke shimmer, white.
  - GE Reel Max Chevrons GRP L0: SingleStrand Left-Right, 1 chase,
    rotations 4, 2 s fades (their exact Christmas Song ballad recipe),
    ice blue.
  - GE Reel Max Kites GRP L0: SingleStrand Bounce, rotations 3 (TSO
    recipe), sapphire.
  - GE Reel Max Circles Outer GRP L0: SingleStrand Left-Right on Vertical
    Per Model/Strand, rotations 8 - each circle drips individually
    (I Saw Mommy Kissing Santa Claus recipe), gold.

Window: 67275-93925 (Chorus 1 / Anthemic), 2 s fades, no hits.
Circles Outer L0 also holds the V1 chord Shockwave (28850) - outside the
window; --rework only clears window effects.

Run (xLights slot A):
    python3 reelmax_c1_constant_motion.py [--dry-run] [--clear-only] [--rework]
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

WHOLE = 'GE Reel Max GRP'
SPOKES = 'GE Reel Max Spokes GRP'
CHEVRONS = 'GE Reel Max Chevrons GRP'
KITES = 'GE Reel Max Kites GRP'
CIRCLES = 'GE Reel Max Circles Outer GRP'
OWNED = [WHOLE, SPOKES, CHEVRONS, KITES, CIRCLES]

SAPPHIRE = '#2864FF'
ICE = '#8080FF'
GOLD = '#FFD89A'
WHITE = '#FFFFFF'

GRADIENT = ('Active=TRUE|Id=ID_BUTTON_Palette1|'
            'Values=x=0.000^c=#2864ff;x=0.400^c=#ffd89a;'
            'x=0.700^c=#ffffff;x=1.000^c=#2864ff|')
GRADIENT_PAL = f'C_BUTTON_Palette1={GRADIENT},C_CHECKBOX_Palette1=1'


def flat_pal(c1, c2=None):
    p = f'C_BUTTON_Palette1={c1},C_CHECKBOX_Palette1=1'
    if c2:
        p += f',C_BUTTON_Palette2={c2},C_CHECKBOX_Palette2=1'
    return p


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
    'E_SLIDER_Pinwheel_Speed=3,'
    'E_SLIDER_Pinwheel_Thickness=47,'
    'E_SLIDER_Pinwheel_Twist=82,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)
WHOLE_PINWHEEL_FLIP = WHOLE_PINWHEEL.replace(
    'B_CHOICE_PerPreviewCamera=2D,',
    'B_CHOICE_PerPreviewCamera=2D,B_CHOICE_BufferTransform=Flip Horizontal,')

SPOKES_SPIRALS = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'B_CHOICE_BufferTransform=Flip Horizontal,'
    'E_CHECKBOX_Spirals_3D=1,'
    'E_SLIDER_Spirals_Count=2,'
    'E_SLIDER_Spirals_Rotation=85,'
    'E_SLIDER_Spirals_Thickness=10,'
    'E_TEXTCTRL_Spirals_Movement=4,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

CHEVRONS_CHASE = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=Left-Right,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=10,'
    'E_SLIDER_Number_Chases=1,'
    'E_TEXTCTRL_Chase_Rotations=4,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

KITES_BOUNCE = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=Bounce from Left,'
    'E_CHOICE_Fade_Type=None,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=10,'
    'E_SLIDER_Number_Chases=1,'
    'E_TEXTCTRL_Chase_Rotations=3,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

CIRCLES_DRIP = (
    'B_CHOICE_BufferStyle=Vertical Per Model/Strand,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=Left-Right,'
    'E_CHOICE_Fade_Type=From Head,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=1,'
    'E_SLIDER_Number_Chases=1,'
    'E_TEXTCTRL_Chase_Rotations=8,'
    'T_TEXTCTRL_Fadein=2,'
    'T_TEXTCTRL_Fadeout=2'
)

PLAN = [
    (WHOLE, 0, 'Pinwheel', WHOLE_PINWHEEL, GRADIENT_PAL),
    (WHOLE, 1, 'Pinwheel', WHOLE_PINWHEEL_FLIP, GRADIENT_PAL),
    (SPOKES, 0, 'Spirals', SPOKES_SPIRALS, flat_pal(WHITE)),
    (CHEVRONS, 0, 'SingleStrand', CHEVRONS_CHASE, flat_pal(ICE, SAPPHIRE)),
    (KITES, 0, 'SingleStrand', KITES_BOUNCE, flat_pal(SAPPHIRE)),
    (CIRCLES, 0, 'SingleStrand', CIRCLES_DRIP, flat_pal(GOLD)),
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
