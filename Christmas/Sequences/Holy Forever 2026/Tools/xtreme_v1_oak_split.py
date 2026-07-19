"""Xtreme V1 (4/5): oak cymbal blooms alternate left/right halves.

Cheapest Xtreme trick (odd/even split): instead of every cymbal Twinkle
covering the whole `Tree - Oak`, successive V1 hits alternate between the
left and right half of the buffer (`B_CUSTOM_SubBuffer`), so consecutive
crashes visibly answer each other — especially the tight 39750/40575 pair
heading into PC1. The two PC1 hits (43075, 54750) stay full-tree, matching
the approved intimate_oak_cymbals.py look outside V1.

Same Twinkle recipe as the baseline (Count 10 / Steps 50, ivory, b35).
Layer 0 of `Tree - Oak` is owned by this script; member `Tree` kept empty.

Run:
    python3 .../Tools/xtreme_v1_oak_split.py [--dry-run] [--clear-only]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/xtremeify/Tools')
import xlights_api as x


OUT = ('/Users/elliott.ohara/xlights-worktrees/xtremeify/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
EMPTY_SOURCE = 'House'
TARGET = 'Tree - Oak'
MEMBER = 'Tree'
TRACK = 'Cymbals'
RANGE_START = 15520
RANGE_END = 67570
V1_END = 41850
DURATION_MS = 2500

LEFT = '0.00x0.00x50.00x100.00'
RIGHT = '50.00x0.00x100.00x100.00'

BASE_SETTINGS = (
    'E_CHECKBOX_Twinkle_ReRandom=0,'
    'E_CHECKBOX_Twinkle_Strobe=0,'
    'E_CHOICE_Twinkle_Style=New Render Method,'
    'E_SLIDER_Twinkle_Count=10,'
    'E_SLIDER_Twinkle_Steps=50,'
    'T_TEXTCTRL_Fadein=.20,'
    'T_TEXTCTRL_Fadeout=1.40'
)
PALETTE = (
    'C_BUTTON_Palette1=#F0E6D0,'
    'C_CHECKBOX_Palette1=1,'
    'C_SLIDER_Brightness=35'
)


def cymbal_hits():
    ids = x.xl('getEffectIDs', model=TRACK)['effects'][0]
    out = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=TRACK, layer=0, id=eid)
        if s.get('name', '') != 'C':
            continue
        t = int(s['startTime'])
        if RANGE_START <= t < RANGE_END:
            out.append(t)
    return sorted(out)


def plan(hits):
    effects = []
    side = 0
    for i, start in enumerate(hits):
        end = start + DURATION_MS
        if i + 1 < len(hits):
            end = min(end, hits[i + 1] - 25)
        end = min(end, RANGE_END)
        if end - start < 600:
            print(f'  skip {start}: too short after clamping')
            continue
        if start < V1_END:
            sub = LEFT if side % 2 == 0 else RIGHT
            side += 1
        else:
            sub = None   # PC1: full tree
        effects.append((start, end, sub))
    for (s, e, _), (s2, e2, _) in zip(effects, effects[1:]):
        assert e <= s2, f'overlap {s}-{e} vs {s2}-{e2}'
    return effects


def wipe(model):
    x.xl('cloneModelEffects', target=model, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=model)['effects']
    assert not left[0], f'{model} layer 0 not empty after wipe'


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    effects = plan(cymbal_hits())
    print(f'{len(effects)} oak twinkles (V1 halves alternate, PC1 full)')
    for s, e, sub in effects:
        where = {LEFT: 'LEFT half', RIGHT: 'RIGHT half', None: 'full'}[sub]
        print(f'  {s}-{e} ({e - s}ms)  {where}')

    if dry:
        print('dry-run: no writes')
        return

    for model in (TARGET, MEMBER):
        wipe(model)

    if not clear_only:
        for s, e, sub in effects:
            settings = BASE_SETTINGS
            if sub:
                settings = f'B_CUSTOM_SubBuffer={sub},' + settings
            x.add_effect(TARGET, 0, 'Twinkle', settings, PALETTE, s, e)

    actual = len(x.xl('getEffectIDs', model=TARGET)['effects'][0])
    expected = 0 if clear_only else len(effects)
    assert actual == expected, f'expected {expected}, found {actual}'
    print(f'{TARGET}: {actual} effects on layer 0')

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
