"""Chorus 1 Rosa Grande — slow constant motion in traditional colors (v2).

v1 (rejected 2026-07-21: "positively awful... It'll cause seizures") fired
8 Shockwave blooms + 12 kick stabs over fast bases. v2 removes ALL hits and
runs only slow, continuous, counter-rotating movement, each bank in its own
traditional color, full Chorus 1 window: 67275 (Anthemic Mood downbeat) to
93925 (Groove/V2 downbeat).

  - GE Rosa Grande Spoke GRP    L0: 3D Pinwheel, constant slow speed 8,
    red/gold. (No speed ramp.)
  - GE Rosa Grande Ring GRP     L0: Spirals rotation -3, movement 1 --
    slow counter-rotation against the pinwheel, green/gold.
  - GE Rosa Grande Ribbon GRP   L0: Fan, one revolution across the whole
    chorus (Revolutions 360), gold/white.
  - GE Rosa Grande Snowflake Spoke GRP L0: sparse white Twinkle shimmer.

Torch banks are dark this pass (v1's kick stabs were the seizure trigger).

Rework support: if the window already holds effects on these banks (or the
v1 torch banks), pass --rework to clear them via direct .xsq edit (the API
has no delete): closeSequence -> strip our window effects from L0 of the
six banks -> openSequence -> verify len -> re-add.

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

RIBBON = 'GE Rosa Grande Ribbon GRP'
SPOKE = 'GE Rosa Grande Spoke GRP'
RING = 'GE Rosa Grande Ring GRP'
SNOWFLAKE = 'GE Rosa Grande Snowflake Spoke GRP'
TORCH_EVEN = 'GE Rosa Grande Torch Long Even GRP'
TORCH_ODD = 'GE Rosa Grande Torch Long Odd GRP'
# all banks this feature has ever owned in the window (v1 + v2) — cleared on rework
OWNED = [RIBBON, SPOKE, RING, SNOWFLAKE, TORCH_EVEN, TORCH_ODD]

RED = '#B01212'      # deep red, not fire-engine
GREEN = '#0B6B3A'    # muted evergreen (house green)
GOLD = '#FFD89A'
WHITE = '#FFFFFF'


def pal(c1, c2, brightness):
    return (f'C_BUTTON_Palette1={c1},C_BUTTON_Palette2={c2},'
            f'C_CHECKBOX_Palette1=1,C_CHECKBOX_Palette2=1,'
            f'C_SLIDER_Brightness={brightness}')


PINWHEEL_SETTINGS = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Pinwheel_Rotation=1,'
    'E_CHOICE_Pinwheel_3D=3D,'
    'E_CHOICE_Pinwheel_Style=New Render Method,'
    'E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,'
    'E_SLIDER_Pinwheel_ArmSize=100,'
    'E_SLIDER_Pinwheel_Arms=4,'
    'E_SLIDER_Pinwheel_Speed=8,'
    'E_SLIDER_Pinwheel_Thickness=30,'
    'E_SLIDER_Pinwheel_Twist=0,'
    'T_TEXTCTRL_Fadein=1.0,'
    'T_TEXTCTRL_Fadeout=1.0'
)

SPIRALS_SETTINGS = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Spirals_3D=1,'
    'E_SLIDER_Spirals_Count=3,'
    'E_SLIDER_Spirals_Rotation=-3,'
    'E_SLIDER_Spirals_Thickness=64,'
    'E_TEXTCTRL_Spirals_Movement=1.0,'
    'T_TEXTCTRL_Fadein=1.0,'
    'T_TEXTCTRL_Fadeout=1.0'
)

FAN_SETTINGS = (
    'B_CHOICE_BufferStyle=Default,'
    'E_CHECKBOX_Fan_Blend_Edges=1,'
    'E_NOTEBOOK_Fan=Options,'
    'E_SLIDER_Fan_Blade_Angle=90,'
    'E_SLIDER_Fan_Blade_Width=100,'
    'E_SLIDER_Fan_CenterX=50,'
    'E_SLIDER_Fan_CenterY=50,'
    'E_SLIDER_Fan_Duration=100,'
    'E_SLIDER_Fan_End_Radius=70,'
    'E_SLIDER_Fan_Num_Blades=3,'
    'E_SLIDER_Fan_Num_Elements=1,'
    'E_SLIDER_Fan_Revolutions=360,'
    'E_SLIDER_Fan_Start_Radius=0,'
    'T_TEXTCTRL_Fadein=1.0,'
    'T_TEXTCTRL_Fadeout=1.0'
)

TWINKLE_SETTINGS = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_SLIDER_Twinkle_Count=8,'
    'E_SLIDER_Twinkle_Steps=60,'
    'T_TEXTCTRL_Fadein=1.0,'
    'T_TEXTCTRL_Fadeout=1.0'
)

PLAN = [
    (SPOKE, 'Pinwheel', PINWHEEL_SETTINGS, pal(RED, GOLD, 60)),
    (RING, 'Spirals', SPIRALS_SETTINGS, pal(GREEN, GOLD, 55)),
    (RIBBON, 'Fan', FAN_SETTINGS, pal(GOLD, WHITE, 55)),
    (SNOWFLAKE, 'Twinkle', TWINKLE_SETTINGS, pal(WHITE, GOLD, 45)),
]


def window_effects(model):
    layers = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for eid in (layers[0] if layers else []):
        s = x.xl('getEffectSettings', model=model, layer=0, id=eid)
        if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
            hits.append(eid)
    return hits


def clear_window_via_xsq():
    """Direct .xsq edit: drop this feature's window effects from OWNED banks.

    Sequence must be CLOSED in xLights before calling."""
    tree = ET.parse(XSQ)
    root = tree.getroot()
    removed = 0
    for el in root.find('ElementEffects').findall('Element'):
        if el.get('name') not in OWNED:
            continue
        layers = el.findall('EffectLayer')
        if not layers:
            continue
        l0 = layers[0]
        for eff in list(l0.findall('Effect')):
            s, e = int(eff.get('startTime')), int(eff.get('endTime'))
            if e > WIN_START and s < WIN_END:
                l0.remove(eff)
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
    for m, e, _, p in PLAN:
        print(f'  {m:44s} {e:10s} {WIN_START}-{WIN_END}  {p.split(",")[0]}')
    print(f'{len(PLAN)} slow continuous effects planned')

    if dry:
        if dirty:
            print(f'window currently dirty on: {list(dirty)} (use --rework)')
        print('dry-run: no writes')
        return

    if dirty:
        if not rework:
            raise SystemExit(
                f'C1 window not empty on {list(dirty)} — rerun with --rework '
                f'to clear via .xsq. Nothing written.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} window effects via .xsq')
        x.xl('openSequence', seq=XSQ)
        info = x.xl('getOpenSequence')
        assert info.get('len') == SEQ_LEN, f'reopen failed: {info}'

    if not clear_only:
        for model, effect, settings, palette in PLAN:
            x.add_effect(model, 0, effect, settings, palette,
                         WIN_START, WIN_END)

    got = sum(len(window_effects(b)) for b in OWNED)
    expected = 0 if clear_only else len(PLAN)
    assert got == expected, f'expected {expected} in window, found {got}'

    x.save(XSQ)
    print(f'saved {XSQ} ({got} effects live in C1 window)')


if __name__ == '__main__':
    main()
