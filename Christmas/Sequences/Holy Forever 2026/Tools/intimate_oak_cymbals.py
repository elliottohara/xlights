"""Intimate V1 + PC1: soft oak-tree sparkles on each Cymbals hit.

`Tree - Oak` is a huge poly-line (3600 nodes) behind the Snowman. A hard
chase reads too busy and pulls focus off the singer, so these are sparse
Twinkles that bloom with the cymbal ring and fade — low brightness, low
density, short.

Reads labeled 'C' marks from the live `Cymbals` timing track from Verse 1
through Pre-Chorus 1 (Song Sections: 15520 → 67570). Layer 0 of
`Tree - Oak` is owned by this script; the member model `Tree` is wiped too
so leftovers don't double.

Run:
    python3 Christmas/Sequences/Holy Forever\\ 2026/Tools/intimate_oak_cymbals.py [--dry-run]
    python3 Christmas/Sequences/Holy Forever\\ 2026/Tools/intimate_oak_cymbals.py --clear-only
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x


OUT = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Holy Forever 2026.xsq'
EMPTY_SOURCE = 'House'
TARGET = 'Tree - Oak'
MEMBER = 'Tree'
TRACK = 'Cymbals'
RANGE_START = 15520   # Song Sections: Verse 1
RANGE_END = 67570     # Song Sections: Chorus 1 (exclusive)
DURATION_MS = 2500

SETTINGS = (
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
    """Labeled 'C' marks from V1 through PC1."""
    try:
        ids = x.xl('getEffectIDs', model=TRACK)['effects'][0]
    except Exception as e:
        raise SystemExit(
            f'timing track {TRACK!r} not in sequence — import the drums '
            f'template first ({e})'
        )
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
    for i, start in enumerate(hits):
        end = start + DURATION_MS
        if i + 1 < len(hits):
            end = min(end, hits[i + 1] - 25)
        end = min(end, RANGE_END)
        if end - start < 600:
            print(f'  skip {start}: too short after clamping')
            continue
        effects.append((start, end))
    for (s, e), (s2, e2) in zip(effects, effects[1:]):
        assert e <= s2, f'overlap {s}-{e} vs {s2}-{e2}'
    return effects


def wipe(model):
    x.xl('cloneModelEffects', target=model, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=model)['effects']
    assert not left[0], f'{model} layer 0 not empty after wipe'


def main():
    dry_run = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    hits = cymbal_hits()
    effects = plan(hits)
    print(f'{len(hits)} V1+PC1 Cymbals marks → {len(effects)} oak twinkles on {TARGET}')
    for start, end in effects:
        print(f'  {start}-{end} ({end - start}ms)')

    if dry_run:
        print('dry-run: no writes')
        return

    for model in (TARGET, MEMBER):
        wipe(model)

    if not clear_only:
        for start, end in effects:
            x.add_effect(TARGET, 0, 'Twinkle', SETTINGS, PALETTE, start, end)

    layers = x.xl('getEffectIDs', model=TARGET)['effects']
    actual = len(layers[0])
    expected = 0 if clear_only else len(effects)
    assert actual == expected, f'expected {expected} effects, found {actual}'
    print(f'{TARGET}: {actual} effects on layer 0')

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
