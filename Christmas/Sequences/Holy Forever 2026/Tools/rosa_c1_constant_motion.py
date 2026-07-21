"""Chorus 1 Rosa Grande — constant detailed movement (Xtreme style).

First Rosa Grande feature for this sequence. Window = Chorus 1 / Anthemic
mood block: 67275 (Beat Count downbeat at the Mood 'Anthemic' boundary) to
93925 (Groove/V2 downbeat). All effect starts land ON live timing marks.

Six part banks (Xtreme rule: 3-6 banks per prop per song), recipes lifted
from the pros' Imperial March HD mapping of this exact layout:

Continuous bases (the "constant movement"):
  - GE Rosa Grande Ribbon GRP  L0: Fan, slow rotating blades, full chorus.
  - GE Rosa Grande Spoke GRP   L0: 3D Pinwheel, speed ramps 10->26 across
    the chorus so the arms visibly accelerate as it builds.
  - GE Rosa Grande Ring GRP    L0: Spirals counter-rotating (rotation -6)
    against the pinwheel for opposed-motion depth.

Beat-locked detail (the "detailed"):
  - GE Rosa Grande Snowflake Spoke GRP L0: Shockwave bloom on every
    Beat Count bar downbeat ('1' marks 67275..90600, 8 blooms).
  - GE Rosa Grande Torch Long Even/Odd GRP L0: alternating Shockwave
    stabs on the 12 live Kick 'K' marks in the window (even/odd pair
    alternation - the signature Xtreme move on this bank pair).

Not touched: Web Ring GRP (owns a V1 chord effect), whole-prop group,
everything outside the six banks' L0 in this window.

Run (xLights slot A must have the sequence open):
    python3 rosa_c1_constant_motion.py [--dry-run] [--clear-only]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-a/Tools')
import xlights_api as x

OUT = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')

WIN_START = 67275   # Anthemic downbeat (Mood boundary, Beat Count '1')
WIN_END = 93925     # Groove/V2 downbeat

RIBBON = 'GE Rosa Grande Ribbon GRP'
SPOKE = 'GE Rosa Grande Spoke GRP'
RING = 'GE Rosa Grande Ring GRP'
SNOWFLAKE = 'GE Rosa Grande Snowflake Spoke GRP'
TORCH_EVEN = 'GE Rosa Grande Torch Long Even GRP'
TORCH_ODD = 'GE Rosa Grande Torch Long Odd GRP'
BANKS = [RIBBON, SPOKE, RING, SNOWFLAKE, TORCH_EVEN, TORCH_ODD]

# warm anthemic palette (traditional gold/ivory, house style)
GOLD = '#FFD89A'
IVORY = '#F0E6D0'
WHITE = '#FFFFFF'
AMBER = '#FFC800'


def pal(c1, c2, brightness):
    return (f'C_BUTTON_Palette1={c1},C_BUTTON_Palette2={c2},'
            f'C_CHECKBOX_Palette1=1,C_CHECKBOX_Palette2=1,'
            f'C_SLIDER_Brightness={brightness}')


# --- continuous bases -------------------------------------------------------

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
    'E_SLIDER_Fan_Num_Blades=4,'
    'E_SLIDER_Fan_Num_Elements=1,'
    'E_SLIDER_Fan_Revolutions=720,'
    'E_SLIDER_Fan_Start_Radius=0,'
    'T_TEXTCTRL_Fadein=.4,'
    'T_TEXTCTRL_Fadeout=.5'
)

PINWHEEL_SETTINGS = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Pinwheel_Rotation=1,'
    'E_CHOICE_Pinwheel_3D=3D,'
    'E_CHOICE_Pinwheel_Style=New Render Method,'
    'E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,'
    'E_SLIDER_Pinwheel_ArmSize=100,'
    'E_SLIDER_Pinwheel_Arms=4,'
    'E_SLIDER_Pinwheel_Thickness=25,'
    'E_SLIDER_Pinwheel_Twist=0,'
    'E_VALUECURVE_Pinwheel_Speed=Active=TRUE|Id=ID_VALUECURVE_Pinwheel_Speed'
    '|Type=Ramp|Min=0.00|Max=50.00|P1=10.00|P2=26.00|RV=TRUE|,'
    'T_TEXTCTRL_Fadein=.4,'
    'T_TEXTCTRL_Fadeout=.5'
)

SPIRALS_SETTINGS = (
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Spirals_3D=1,'
    'E_SLIDER_Spirals_Count=4,'
    'E_SLIDER_Spirals_Rotation=-6,'
    'E_SLIDER_Spirals_Thickness=64,'
    'E_TEXTCTRL_Spirals_Movement=2,'
    'T_TEXTCTRL_Fadein=.4,'
    'T_TEXTCTRL_Fadeout=.5'
)

# --- hit recipes (Xtreme Shockwave skeleton) --------------------------------

def shockwave(buffer_style, end_radius, end_width, fadeout):
    return (
        f'B_CHOICE_BufferStyle={buffer_style},'
        'E_CHECKBOX_Shockwave_Blend_Edges=1,'
        'E_NOTEBOOK_Shockwave=Position,'
        'E_SLIDER_Shockwave_Accel=0,'
        'E_SLIDER_Shockwave_CenterX=50,'
        'E_SLIDER_Shockwave_CenterY=50,'
        'E_SLIDER_Shockwave_Start_Radius=1,'
        'E_SLIDER_Shockwave_Start_Width=5,'
        f'E_SLIDER_Shockwave_End_Radius={end_radius},'
        f'E_SLIDER_Shockwave_End_Width={end_width},'
        f'T_TEXTCTRL_Fadeout={fadeout}'
    )

# bar-downbeat blooms: one medium wave across the whole snowflake bank
BLOOM_SETTINGS = shockwave('Overlay - Centered', 28, 65, '.25')
BLOOM_MS = 600

# kick stabs: wave re-renders inside each torch (HD per-part signature)
STAB_SETTINGS = shockwave('Per Model Per Preview', 13, 25, '.25')
STAB_MS = 450

# live timing marks in the window (Beat Count '1' / Kick 'K', verified)
BAR_DOWNBEATS = [67275, 70600, 73925, 77275, 80600, 83925, 87275, 90600]
KICKS = [68075, 68925, 71875, 72250, 73900, 76825,
         82725, 85600, 88925, 89750, 92250, 93075]


def read_marks(track, label):
    """Re-read live marks so the plan always matches the sequence."""
    ids = x.xl('getEffectIDs', model=track)['effects'][0]
    out = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=track, layer=0, id=eid)
        t0 = int(s['startTime'])
        if s.get('name', '') == label and WIN_START <= t0 < WIN_END:
            out.append(t0)
    return sorted(out)


def window_effects(model):
    """IDs of layer-0 effects on `model` that touch the C1 window."""
    layers = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for eid in (layers[0] if layers else []):
        s = x.xl('getEffectSettings', model=model, layer=0, id=eid)
        if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
            hits.append(eid)
    return hits


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'
    assert info.get('len') == 308314, f'unexpected len: {info}'

    bars = read_marks('Beat Count', '1')
    kicks = read_marks('Kick', 'K')
    assert bars == BAR_DOWNBEATS, f'Beat Count drifted: {bars}'
    assert kicks == KICKS, f'Kick drifted: {kicks}'

    # refuse if any bank already has effects in the window (except ours on rerun)
    preexisting = {b: window_effects(b) for b in BANKS}

    plan = []
    plan.append((RIBBON, 'Fan', FAN_SETTINGS, pal(GOLD, IVORY, 70),
                 WIN_START, WIN_END))
    plan.append((SPOKE, 'Pinwheel', PINWHEEL_SETTINGS, pal(IVORY, GOLD, 75),
                 WIN_START, WIN_END))
    plan.append((RING, 'Spirals', SPIRALS_SETTINGS, pal(AMBER, GOLD, 65),
                 WIN_START, WIN_END))
    for t in bars:
        plan.append((SNOWFLAKE, 'Shockwave', BLOOM_SETTINGS,
                     pal(WHITE, GOLD, 90), t, t + BLOOM_MS))
    for i, t in enumerate(kicks):
        bank = TORCH_EVEN if i % 2 == 0 else TORCH_ODD
        plan.append((bank, 'Shockwave', STAB_SETTINGS,
                     pal(GOLD, WHITE, 85), t, t + STAB_MS))

    for item in plan:
        print(f'  {item[0]:44s} {item[1]:10s} {item[4]}-{item[5]}')
    print(f'{len(plan)} effects planned, window {WIN_START}-{WIN_END}')

    if dry:
        print('dry-run: no writes')
        return

    # clear only OUR window on L0 of the six banks (direct per-effect wipe
    # is not available via API; window is empty on first run, and reruns
    # would need clear via .xsq -- so refuse if anything is present)
    dirty = {b: ids for b, ids in preexisting.items() if ids}
    if dirty:
        raise SystemExit(
            f'C1 window not empty on {list(dirty)} - clear via .xsq first '
            f'(no API delete). Nothing written.')

    if not clear_only:
        for model, effect, settings, palette, s, e in plan:
            x.add_effect(model, 0, effect, settings, palette, s, e)

    got = sum(len(window_effects(b)) for b in BANKS)
    expected = 0 if clear_only else len(plan)
    assert got == expected, f'expected {expected} in window, found {got}'

    x.save(OUT)
    print(f'saved {OUT} ({got} effects live in C1 window)')


if __name__ == '__main__':
    main()
