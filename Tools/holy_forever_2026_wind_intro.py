"""Holy Forever 2026 - intro 'swaying wind' (180ms -> 15520ms, lyrics start).

One lean per bar (3333.33ms, 72bpm grid anchored at 180ms), direction flips on
each downbeat:
  - Whole Scene: Bars gradient gust flowing Left/Right (integer cycles per lean
    so the flip is phase-continuous = pendulum turnaround), Max blend over the
    existing purple wash + shader.
  - Outline/ground groups: Marquee dash streams (Single Line buffer, the proven
    settings from this sequence's own verse marquees) with Reverse flipped per bar.
  - Mega Tree: Spirals swinging movement +1 / -1 per bar.

Does NOT save or render - user reviews in the open editor.
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

START = 180
END = 15520            # first lyric / verse-1 treatments begin here
BARS = [180, 3513, 6847, 10180, 13513, 15520]   # downbeats + final end

BLUE, LTBLUE, DKNAVY, WHITE = '#075FCC', '#13A8FF', '#031C38', '#EEEAE2'

def pal(colors, brightness=None):
    parts = []
    for i, c in enumerate(colors, 1):
        parts.append(f'C_BUTTON_Palette{i}={c}')
        parts.append(f'C_CHECKBOX_Palette{i}=1')
    if brightness is not None:
        parts.append(f'C_SLIDER_Brightness={brightness}')
    return ','.join(sorted(parts))

P_GUST = pal([LTBLUE, DKNAVY], 55)
P_HOUSE = pal([LTBLUE], 75)
P_GROUND = pal([WHITE], 55)
P_TREE = pal([BLUE, LTBLUE], 70)

# element -> free layer during 0-15520 (verified against the .xsq)
MARQUEE_HOUSE = {'House Outline': 1, 'Roof': 1, 'Icicles GRP': 2, 'Arches - All': 0}
MARQUEE_GROUND = {'Yard Borders': 0, 'Driveway': 0, 'Canes': 0,
                  'Colum Shrubs': 0, 'Mini Trees': 2}
WHOLE_SCENE_LAYER = 1
MEGA_TREE_LAYER = 6

def leans():
    """(index, start, end, lean_left, frac_of_full_bar)"""
    for i in range(len(BARS) - 1):
        s, e = BARS[i], BARS[i + 1]
        yield i, s, e, (i % 2 == 0), (e - s) / 3333.333

def fades(i, last, fin='.5', fout='.5'):
    f = []
    if i == 0:
        f.append('T_TEXTCTRL_Fadein=1.5')
    elif fin:
        f.append(f'T_TEXTCTRL_Fadein={fin}')
    if i == last:
        f.append('T_TEXTCTRL_Fadeout=.5')
    elif fout:
        f.append(f'T_TEXTCTRL_Fadeout={fout}')
    return f

def bars_settings(i, last, left, frac):
    cycles = 1.0 if frac > 0.9 else round(frac, 2)
    s = [
        'B_SLIDER_Blur=4',
        'E_CHECKBOX_Bars_3D=0', 'E_CHECKBOX_Bars_Gradient=1', 'E_CHECKBOX_Bars_Highlight=0',
        f'E_CHOICE_Bars_Direction={"Left" if left else "Right"}',
        'E_SLIDER_Bars_BarCount=1',
        f'E_TEXTCTRL_Bars_Cycles={cycles}',
        'T_CHOICE_LayerMethod=Max',
    ]
    # middle flips are phase-continuous (integer cycles) -> no fades needed
    s += fades(i, last, fin=None, fout=None)
    return ','.join(s)

def marquee_settings(i, last, left):
    s = [
        'B_CHOICE_BufferStyle=Single Line',
        'E_CHECKBOX_Marquee_PixelOffsets=0',
        f'E_CHECKBOX_Marquee_Reverse={0 if left else 1}',
        'E_CHECKBOX_Marquee_WrapX=0', 'E_NOTEBOOK_Marquee=Settings',
        'E_SLIDER_MarqueeXC=0', 'E_SLIDER_MarqueeYC=0',
        'E_SLIDER_Marquee_Band_Size=4', 'E_SLIDER_Marquee_ScaleX=100',
        'E_SLIDER_Marquee_ScaleY=100', 'E_SLIDER_Marquee_Skip_Size=7',
        'E_SLIDER_Marquee_Speed=2', 'E_SLIDER_Marquee_Stagger=0',
        'E_SLIDER_Marquee_Start=0', 'E_SLIDER_Marquee_Thickness=3',
    ]
    s += fades(i, last)
    return ','.join(s)

def spirals_settings(i, last, left, frac):
    move = round((1.0 if frac > 0.9 else frac), 2) * (1 if left else -1)
    s = [
        'E_CHECKBOX_Spirals_3D=1', 'E_CHECKBOX_Spirals_Blend=0',
        'E_CHECKBOX_Spirals_Grow=0', 'E_CHECKBOX_Spirals_Shrink=0',
        'E_SLIDER_Spirals_Count=3', 'E_SLIDER_Spirals_Rotation=20',
        'E_SLIDER_Spirals_Thickness=34',
        f'E_TEXTCTRL_Spirals_Movement={move}',
    ]
    s += fades(i, last, fin=None, fout=None)
    return ','.join(s)

def main():
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence open: {info}'

    targets = ['Whole Scene', 'Mega Tree'] + list(MARQUEE_HOUSE) + list(MARQUEE_GROUND)
    missing = [t for t in targets if not x.element_exists(t)]
    if missing:
        raise SystemExit(f'elements not addressable in this sequence: {missing}')

    last = len(BARS) - 2
    n = 0
    for i, s, e, left, frac in leans():
        x.add_effect('Whole Scene', WHOLE_SCENE_LAYER, 'Bars',
                     bars_settings(i, last, left, frac), P_GUST, s, e)
        n += 1
        for el, layer in MARQUEE_HOUSE.items():
            x.add_effect(el, layer, 'Marquee', marquee_settings(i, last, left), P_HOUSE, s, e)
            n += 1
        for el, layer in MARQUEE_GROUND.items():
            x.add_effect(el, layer, 'Marquee', marquee_settings(i, last, left), P_GROUND, s, e)
            n += 1
        x.add_effect('Mega Tree', MEGA_TREE_LAYER, 'Spirals',
                     spirals_settings(i, last, left, frac), P_TREE, s, e)
        n += 1
        print(f'lean {i+1}/5 {"LEFT " if left else "RIGHT"} {s}-{e}  ok')
    print(f'done: {n} effects added (not saved, not rendered)')

if __name__ == '__main__':
    main()
