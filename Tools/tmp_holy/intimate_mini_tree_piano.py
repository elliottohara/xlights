"""Intimate V1: short piano-note runs across the four mini trees.

The wide piano chords remain on `Arches - All`.  These are the smaller tonal
attacks between those chords, curated from the audio onset analysis and kept
deliberately sparse.  Each run steps across individual mini trees with a short
warm-gold On pulse; the stars remain dark.

Layer 0 of each `Mini Tree - N` is owned by this script.  The group-level
`Mini Trees` element and `Mini Tree Stars` are not touched.

Run:
    python3 Tools/tmp_holy/intimate_mini_tree_piano.py [--dry-run]
    python3 Tools/tmp_holy/intimate_mini_tree_piano.py --clear-only
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x


OUT = '/Users/elliott.ohara/xlights/Christmas/Holy Forever 2026.xsq'
EMPTY_SOURCE = 'House'
TREES = [f'Mini Tree - {i}' for i in range(1, 5)]
PULSE_MS = 425

# Actual between-chord onset peaks, snapped to the 25 ms sequence frame.
# Tree orders give each phrase a visible melodic contour instead of a beat
# counter.  The final two fills become slightly more active as V1 opens into
# the pre-chorus.
RUNS = [
    ([16375, 16800, 17250], [1, 2, 3]),
    ([23900, 24350, 24700], [1, 2, 3]),
    ([26175, 26400, 26600], [4, 3, 2]),
    ([30100, 30600, 31400], [1, 2, 3]),
    ([33475, 34725, 35275], [4, 2, 1]),
    ([36775, 37200, 38050, 38900], [1, 2, 3, 4]),
]

SETTINGS = (
    'E_CHECKBOX_On_Shimmer=0,'
    'T_TEXTCTRL_Fadein=.04,'
    'T_TEXTCTRL_Fadeout=.30'
)

PALETTE = (
    'C_BUTTON_Palette1=#FFD89A,'
    'C_CHECKBOX_Palette1=1,'
    'C_SLIDER_Brightness=55'
)


def plan():
    effects = []
    for run_number, (times, tree_order) in enumerate(RUNS, start=1):
        assert len(times) == len(tree_order), f'run {run_number} is malformed'
        assert times == sorted(times), f'run {run_number} is not chronological'
        for start, tree_number in zip(times, tree_order):
            assert start % 25 == 0, f'{start} is off the 25 ms frame grid'
            assert 1 <= tree_number <= 4
            effects.append(
                (f'Mini Tree - {tree_number}', start, start + PULSE_MS, run_number)
            )

    by_tree = {tree: [] for tree in TREES}
    for tree, start, end, run_number in effects:
        by_tree[tree].append((start, end, run_number))
    for tree, spans in by_tree.items():
        spans.sort()
        for current, following in zip(spans, spans[1:]):
            assert current[1] <= following[0], (
                f'overlap on {tree}: {current} vs {following}'
            )
    return effects


def wipe(tree):
    x.xl(
        'cloneModelEffects',
        target=tree,
        source=EMPTY_SOURCE,
        eraseModel='true',
    )
    layers = x.xl('getEffectIDs', model=tree)['effects']
    assert not layers[0], f'{tree} layer 0 not empty after wipe'


def main():
    dry_run = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    effects = plan()
    print(f'{len(RUNS)} piano fills, {len(effects)} note pulses')
    for run_number, (times, tree_order) in enumerate(RUNS, start=1):
        notes = ', '.join(
            f'{time / 1000:.3f}s→T{tree}'
            for time, tree in zip(times, tree_order)
        )
        print(f'  run {run_number}: {notes}')

    if dry_run:
        print('dry-run: no writes')
        return

    for tree in TREES:
        wipe(tree)

    if not clear_only:
        for tree, start, end, _run_number in effects:
            x.add_effect(tree, 0, 'On', SETTINGS, PALETTE, start, end)

    expected = 0 if clear_only else len(effects)
    actual = 0
    for tree in TREES:
        layers = x.xl('getEffectIDs', model=tree)['effects']
        count = len(layers[0])
        actual += count
        print(f'  {tree}: {count} effects on layer 0')
    assert actual == expected, f'expected {expected} effects, found {actual}'

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
