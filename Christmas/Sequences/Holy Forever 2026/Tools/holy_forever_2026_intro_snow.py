"""Holy Forever 2026 — gentle whole-scene snowfall for the ethereal intro.

Snowflakes on `Whole Scene` L0 from 0 → 15520 (verse 1 pickup), with brightness
stepping to the two choir "Holy" swells (same windows as the downstairs glowing
crosses):

  soft pad → abrupt bright on "Holy" → slight darken when the swell ends →
  abrupt bright on the second "Holy" → slight darken → fade into V1.

Wipe+re-add (safe edit). Does NOT save or render — review in the open editor.
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

TARGET = 'Whole Scene'
LAYER = 0
EMPTY_SOURCE = 'House'
END = 15520  # verse-1 treatments begin; Matrixes snow starts at 15525

# Choir "Holy" swell windows (verified mid-channel RMS + glowing-cross effects)
HOLY1 = (3900, 6600)
HOLY2 = (10550, 13550)

# Soft white — ethereal pad, not a blizzard
WHITE = '#EEEAE2'
BRIGHT_SOFT = 28      # before first Holy / quiet pad
BRIGHT_HOLY = 78      # abrupt lift when they sing Holy
BRIGHT_AFTER = 42     # slightly darker once the swell stops (still above pad)

SNOW = (
    'E_CHOICE_Falling=Driving,'
    'E_SLIDER_Snowflakes_Count=60,'
    'E_SLIDER_Snowflakes_Speed=4,'
    'E_SLIDER_Snowflakes_Type=1'
)


def pal(brightness):
    return (
        f'C_BUTTON_Palette1={WHITE},C_CHECKBOX_Palette1=1,'
        f'C_SLIDER_Brightness={brightness}'
    )


def settings(**fades):
    parts = [SNOW]
    for k, v in fades.items():
        if v is not None:
            parts.append(f'T_TEXTCTRL_{k}={v}')
    return ','.join(parts)


# (start, end, brightness, fadein, fadeout)
SEGMENTS = [
    # Soft entrance — snow drifts in before the first Holy
    (0, HOLY1[0], BRIGHT_SOFT, '2.0', None),
    # Abrupt brighten with first Holy; ease slightly as they stop
    (HOLY1[0], HOLY1[1], BRIGHT_HOLY, '0', '.75'),
    # Dimmer between swells
    (HOLY1[1], HOLY2[0], BRIGHT_AFTER, '.25', None),
    # Abrupt brighten with second Holy
    (HOLY2[0], HOLY2[1], BRIGHT_HOLY, '0', '.75'),
    # Hold the afterglow, then fade into verse 1
    (HOLY2[1], END, BRIGHT_AFTER, '.25', '1.5'),
]


def main():
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence open: {info}'
    assert x.element_exists(TARGET), f'{TARGET} not addressable'

    print(f'wiping {TARGET} L0 via {EMPTY_SOURCE}…')
    x.xl('cloneModelEffects', target=TARGET, source=EMPTY_SOURCE, eraseModel='true')

    for s, e, bright, fin, fout in SEGMENTS:
        x.add_effect(TARGET, LAYER, 'Snowflakes',
                     settings(Fadein=fin, Fadeout=fout), pal(bright), s, e)
        print(f'  {s:5d}-{e:5d}  bright={bright:2d}  fadein={fin} fadeout={fout}')

    print(f'done: {len(SEGMENTS)} Snowflakes segments on {TARGET} L0 (not saved)')


if __name__ == '__main__':
    main()
