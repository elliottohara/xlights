"""Whole Scene snowflakes: intro + intimate verse, inverse of the cross.

Continuous Snowflakes on `Whole Scene` L0 from 0 → 41850 (PC1 section
boundary). Brightness is the inverse of the Mega Tree cross curve during
the intro Holy swells, then holds a dimmed (not zero) presence through
the intimate acoustic verse so the "choir"/atmosphere stays around under
the Snowman lead.

Cross (of 400): intro baseline ≈30 / peak 100; verse hold ≈22
Snow  (of 400): intro baseline ≈55 / dip ≈18; verse hold ≈28 (dimmed)

Run: python3 Christmas/Sequences/Holy Forever 2026/Tools/intro_snow_inverse.py [--dry-run]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x


EMPTY_SOURCE = 'House'
TARGET = 'Whole Scene'
START = 0
END = 41850  # match cross / PC1 boundary; covers full intimate V1

# Cross curve absolutes (of 400) — kept for documentation / inverse math
CROSS_DIM = 30
CROSS_PEAK = 100

# Snow absolutes (of 400)
BASE = 55       # quiet pad between Holys
DIP = 18        # under each Holy swell (inverse of cross peak)
START_B = 50
VERSE_B = 28    # dimmed presence through intimate V1 (not zero)
END_B = 12      # ease toward PC1


def tfrac(ms: int) -> float:
    return ms / float(END - START)


def inv(cross_abs: float) -> float:
    """Map a cross brightness (0–400 scale) to snow brightness."""
    # linear: CROSS_DIM → BASE, CROSS_PEAK → DIP
    t = (cross_abs - CROSS_DIM) / float(CROSS_PEAK - CROSS_DIM)
    return BASE - t * (BASE - DIP)


def brightness_vc() -> str:
    """Inverse of continuous_cross_intro at intro keypoints; verse hold after."""
    pts = [
        (0, START_B / 400.0),
        (1500, BASE / 400.0),
        (3900, BASE / 400.0),          # swell 1 begins — still baseline
        (4400, DIP / 400.0),           # cross peak → snow dip
        (5100, DIP / 400.0),
        (6400, BASE / 400.0),
        (9000, BASE / 400.0),
        (10550, BASE / 400.0),         # swell 2 begins
        (11000, DIP / 400.0),
        (11600, DIP / 400.0),
        (13300, BASE / 400.0),
        (14500, BASE / 400.0),
        (15520, VERSE_B / 400.0),      # dim into intimate V1
        (30000, VERSE_B / 400.0),      # hold dimmed choir presence
        (39000, VERSE_B / 400.0),
        (END, END_B / 400.0),
    ]
    # sanity: keypoints match inverse of cross DIM/PEAK
    assert abs(inv(CROSS_DIM) - BASE) < 0.01
    assert abs(inv(CROSS_PEAK) - DIP) < 0.01
    values = ';'.join(f'{tfrac(ms):.4f}:{b:.4f}' for ms, b in pts)
    return (
        'Active=TRUE|Id=ID_VALUECURVE_Brightness|Type=Custom|'
        f'Min=0.00|Max=400.00|RV=TRUE|Values={values}|'
    )


SETTINGS = (
    'E_CHOICE_Falling=Driving,'
    'E_SLIDER_Snowflakes_Count=90,'
    'E_SLIDER_Snowflakes_Speed=4,'
    'E_SLIDER_Snowflakes_Type=1,'
    'T_TEXTCTRL_Fadein=2.0,'
    'T_TEXTCTRL_Fadeout=2.00'
)

PALETTE = (
    'C_BUTTON_Palette1=#eeeae2,'
    'C_CHECKBOX_Palette1=1,'
    f'C_VALUECURVE_Brightness={brightness_vc()}'
)


def main():
    dry = '--dry-run' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    ids = x.xl('getEffectIDs', model=TARGET)['effects']
    l0 = ids[0] if ids else []
    print(f'{TARGET}: L0={len(l0)} effects')
    for eid in l0:
        s = x.xl('getEffectSettings', model=TARGET, layer=0, id=eid)
        print(f'  existing: {s["name"]} {s["startTime"]}-{s["endTime"]}')
    print(f'plan: wipe L0, add Snowflakes {START}-{END} '
          f'base={BASE} dip={DIP} verse={VERSE_B} (of 400)')
    print(f'  sample inv(cross {CROSS_DIM})={inv(CROSS_DIM):.0f} '
          f'inv(cross {CROSS_PEAK})={inv(CROSS_PEAK):.0f}')

    if dry:
        print('dry-run: no writes')
        return

    x.xl('cloneModelEffects', target=TARGET, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=TARGET)['effects']
    assert not left[0], f'L0 still has effects after wipe: {left[0]}'

    x.add_effect(TARGET, 0, 'Snowflakes', SETTINGS, PALETTE, START, END)
    verify = x.xl('getEffectSettings', model=TARGET, layer=0, id=0)
    print(f'added: {verify["name"]} {verify["startTime"]}-{verify["endTime"]}')
    vc = verify.get('palette', {}).get('C_VALUECURVE_Brightness', '')
    print(f'brightness VC present: {bool(vc)}')
    assert verify['name'] == 'Snowflakes'
    assert vc, 'brightness value curve missing after addEffect'
    assert verify['startTime'] == START and verify['endTime'] == END

    out = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq'
    x.save(out)
    print(f'saved {out}')


if __name__ == '__main__':
    main()
