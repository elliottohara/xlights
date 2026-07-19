"""Glowing cross on Mega Tree: intro + intimate acoustic verse.

Continuous Pictures on `Mega Tree` L0 from 0 → 41850 (PC1 section
boundary). Brightens with each intro choir "Holy", then holds a soft
glow through the intimate acoustic verse (Snowman solo) before easing
out as PC1 begins.

Clears any leftover cross on `Matrix - Downstairs Window` L0 if present
(downstairs is empty in the 2026-07-19 baseline). Mega Tree L0 holds only
this cross — safe to House-wipe L0.

Brightness curve:

  swell 1: rises ~3.9 s, peaks ~4.4–5.1, decays through ~6.4 s
  swell 2: rises ~10.55 s, sustains ~10.65–11.6, decays through ~13.3 s
  verse: hold soft glow (~22) through V1; ease out into PC1

Run: python3 Christmas/Sequences/Holy Forever 2026/Tools/continuous_cross_intro.py [--dry-run]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x


EMPTY_SOURCE = 'House'
MATRIX = 'Matrix - Downstairs Window'
TARGET = 'Mega Tree'
TARGET_LAYER = 0
START = 0
END = 41850  # Pre-Chorus 1 section boundary; covers full intimate V1

CROSS = (
    '/Users/elliott.ohara/xlights/Christmas/ImportedMedia/'
    'Holy Forever/Images/Glowing Cross.png'
)

# Brightness scale: C_VALUECURVE_Brightness Custom Values are normalized
# against Min=0 / Max=400. Default (no slider) = 100 → 0.25.
DIM = 30 / 400.0       # always-on glow between Holys
PEAK = 100 / 400.0     # full brightness at choir peaks
START_DIM = 18 / 400.0
VERSE_DIM = 22 / 400.0  # soft hold through intimate acoustic verse
END_DIM = 8 / 400.0     # ease toward PC1 (not hard cut)


def tfrac(ms: int) -> float:
    return ms / float(END - START)


def brightness_vc() -> str:
    """Custom brightness curve: intro Holy swells + verse hold."""
    # (ms, normalized brightness)
    pts = [
        (0, START_DIM),
        (1500, DIM),          # settle into always-on glow
        (3900, DIM),          # swell 1 begins
        (4400, PEAK),         # peak
        (5100, PEAK),         # hold
        (6400, DIM),          # decayed
        (9000, DIM),          # quiet pad between Holys
        (10550, DIM),         # swell 2 begins
        (11000, PEAK),
        (11600, PEAK),        # sustain
        (13300, DIM),         # decayed
        (14500, DIM),
        (15520, VERSE_DIM),   # into intimate V1 (Snowman pickup ~15275)
        (30000, VERSE_DIM),   # hold soft glow through verse
        (39000, VERSE_DIM),
        (END, END_DIM),       # ease toward PC1
    ]
    values = ';'.join(f'{tfrac(ms):.4f}:{b:.4f}' for ms, b in pts)
    return (
        'Active=TRUE|Id=ID_VALUECURVE_Brightness|Type=Custom|'
        f'Min=0.00|Max=400.00|RV=TRUE|Values={values}|'
    )


SETTINGS = (
    'E_CHECKBOX_Pictures_PixelOffsets=0,'
    'E_CHECKBOX_Pictures_Shimmer=0,'
    'E_CHECKBOX_Pictures_TransparentBlack=0,'
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
    'E_TEXTCTRL_Pictures_TransparentBlack=0,'
    'T_TEXTCTRL_Fadein=1.00,'
    'T_TEXTCTRL_Fadeout=2.00'
)

PALETTE = (
    'C_BUTTON_Palette1=#FFFFFF,'
    'C_CHECKBOX_Palette1=1,'
    f'C_VALUECURVE_Brightness={brightness_vc()}'
)


def clear_matrix_cross():
    """Remove any leftover intro Pictures from downstairs window L0."""
    ids = x.xl('getEffectIDs', model=MATRIX)['effects']
    l0 = ids[0] if ids else []
    print(f'{MATRIX}: L0={len(l0)} effects across {len(ids)} layers')
    if not l0:
        print(f'  matrix L0 already empty — nothing to clear')
        return
    x.xl('cloneModelEffects', target=MATRIX, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=MATRIX)['effects']
    assert not left or not left[0], f'matrix L0 still has effects after wipe: {left}'
    print(f'  wiped matrix L0')


def wipe_mega_tree_l0():
    """House-wipe Mega Tree L0 (cross only; deeper layers empty/untouched)."""
    ids = x.xl('getEffectIDs', model=TARGET)['effects']
    l0 = ids[TARGET_LAYER] if len(ids) > TARGET_LAYER else []
    print(f'{TARGET} L{TARGET_LAYER}: {len(l0)} effects before wipe')
    for eid in l0:
        s = x.xl('getEffectSettings', model=TARGET, layer=TARGET_LAYER, id=eid)
        print(f'  existing: {s["name"]} {s["startTime"]}-{s["endTime"]}')
    x.xl('cloneModelEffects', target=TARGET, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=TARGET)['effects']
    assert not left[TARGET_LAYER], f'L0 still has effects after wipe: {left[TARGET_LAYER]}'
    print(f'  wiped {TARGET} L{TARGET_LAYER}')


def main():
    dry = '--dry-run' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    print(f'plan: clear {MATRIX} L0 cross; wipe+add Pictures on {TARGET} '
          f'L{TARGET_LAYER} {START}-{END}')
    print(f'  dim={DIM*400:.0f}  peak={PEAK*400:.0f}  verse={VERSE_DIM*400:.0f}  '
          f'(of 400)')

    if dry:
        print('dry-run: no writes')
        return

    clear_matrix_cross()
    wipe_mega_tree_l0()

    x.add_effect(TARGET, TARGET_LAYER, 'Pictures', SETTINGS, PALETTE, START, END)
    verify = x.xl('getEffectSettings', model=TARGET, layer=TARGET_LAYER, id=0)
    print(f'added: {verify["name"]} {verify["startTime"]}-{verify["endTime"]}')
    vc = verify.get('palette', {}).get('C_VALUECURVE_Brightness', '')
    print(f'brightness VC present: {bool(vc)}')
    assert vc, 'brightness value curve missing from palette after addEffect'
    assert verify['name'] == 'Pictures'
    assert verify['startTime'] == START and verify['endTime'] == END

    out = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq'
    x.save(out)
    print(f'saved {out}')


if __name__ == '__main__':
    main()
