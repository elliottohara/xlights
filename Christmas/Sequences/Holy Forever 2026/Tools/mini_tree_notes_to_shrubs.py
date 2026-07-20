"""Intimate V1 piano melody stepping across the `All Shrubs GRP` members
(user requests 2026-07-20: "assign each ... value to a prop ... lowest note
farthest left"; then "tons of rose bushes lighting up at the same time" ->
"one prop per hit, driven by the top/melody note; a single light steps
across the row").

For each V1 `Piano Notes` mark we take its TOP (melody) note. The distinct
top notes are rank-mapped across the 14 group members ordered left-to-right
by layout X (lowest top note -> leftmost prop `Shrub Left`, highest -> the
rightmost prop `Rose Bush 9`), so the melody uses the whole row. Exactly
ONE prop lights per mark. Chord-coincident marks (within 50 ms of a
`Piano Chords` `P` mark) are excluded — those wide chords are already
answered by the arch reveal + rotating banks.

Requires all 14 members to be in the sequence master view. The 9
`Rose Bush N` models were added to the .xsq DisplayElements/ElementEffects
on 2026-07-20 (see AGENT NOTES); before that only the 5 shrub/door-tree
props were addressable.

Same visual treatment as the mini-tree original this supersedes: warm gold
On, 425 ms, brightness 55, .04 attack / .30 fadeout.

Run:
    python3 .../Tools/mini_tree_notes_to_shrubs.py [--dry-run] [--clear-only]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-a/Tools')
import xlights_api as x

OUT = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
EMPTY_SOURCE = 'House'

# All 14 `All Shrubs GRP` members, ordered left-to-right by layout WorldPosX
# (verified in xlights_rgbeffects.xml 2026-07-20), most-negative (west) first.
PROPS = [
    'Shrub Left', 'Rose Bush 1', 'Rose Bush 2', 'Door Tree Left',
    'Rose Bush 3', 'Rose Bush 4', 'Door Tree Right', 'Shrub Center',
    'Rose Bush 5', 'Rose Bush 6', 'Rose Bush 7', 'Rose Bush 8',
    'Shrub Right', 'Rose Bush 9',
]
# Also wipe these so a rerun leaves no stale duplicates from earlier passes.
LEGACY_TARGETS = ['All Shrubs GRP'] + [f'Mini Tree - {i}' for i in range(1, 5)]

NOTES_TRACK = 'Piano Notes'
CHORDS_TRACK = 'Piano Chords'
V1_START, V1_END = 15275, 39975
CHORD_EXCLUDE_MS = 50
PULSE_MS = 425

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


def labeled_marks(track):
    ids = x.xl('getEffectIDs', model=track)['effects'][0]
    out = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=track, layer=0, id=eid)
        label = s.get('name', '').strip()
        if label:
            out.append((int(s['startTime']), label))
    return sorted(out)


def plan():
    chords = [t for t, lab in labeled_marks(CHORDS_TRACK) if lab == 'P']
    marks = []
    for t, lab in labeled_marks(NOTES_TRACK):
        if not (V1_START <= t <= V1_END):
            continue
        if any(abs(t - c) <= CHORD_EXCLUDE_MS for c in chords):
            continue
        marks.append((t, [int(n) for n in lab.split()]))

    # one melody note per mark = its top (highest) note
    tops = [(t, max(notes)) for t, notes in marks]

    unique = sorted(set(top for _, top in tops))
    n_unique = len(unique)
    n_props = len(PROPS)

    # rank the distinct melody notes across the whole row: lowest -> leftmost
    note_prop = {}
    for r, note in enumerate(unique):
        frac = r / max(n_unique - 1, 1)
        note_prop[note] = min(n_props - 1, int(round(frac * (n_props - 1))))
    print('melody note -> prop map (low=left):')
    for note in unique:
        print(f'  MIDI {note:>3} -> {PROPS[note_prop[note]]}')

    raw = []   # (prop_idx, start, end) — exactly one per mark
    for t, top in tops:
        raw.append([note_prop[top], t, t + PULSE_MS])

    # clamp per-prop overlaps onto extra layers
    by_prop = {}
    for p in raw:
        by_prop.setdefault(p[0], []).append(p)
    layered = []   # (prop_idx, layer, start, end)
    for pidx, ps in by_prop.items():
        ps.sort(key=lambda p: p[1])
        layer_ends = []
        for _, s, e in ps:
            for i, last_end in enumerate(layer_ends):
                if s >= last_end:
                    layer_ends[i] = e
                    layered.append((pidx, i, s, e))
                    break
            else:
                layer_ends.append(e)
                layered.append((pidx, len(layer_ends) - 1, s, e))

    layered.sort(key=lambda p: (p[2], p[0]))
    return layered


def wipe(model, max_layer):
    for _ in range(max_layer + 1):
        x.xl('cloneModelEffects', target=model, source=EMPTY_SOURCE,
             eraseModel='true')
    for layer_ids in x.xl('getEffectIDs', model=model)['effects']:
        assert not layer_ids, f'{model} not fully empty after wipe'


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    layered = plan()
    max_layer = {}
    for pidx, layer, _, _ in layered:
        max_layer[pidx] = max(max_layer.get(pidx, 0), layer)

    print(f'\n{len(layered)} note pulses across {len(max_layer)} props')
    for pidx, layer, s, e in layered:
        print(f'  L{layer}  {s}-{e}  {PROPS[pidx]}')

    if dry:
        print('dry-run: no writes')
        return

    for t in LEGACY_TARGETS:
        wipe(t, 3)
    for i in range(len(PROPS)):
        wipe(PROPS[i], max_layer.get(i, 0))

    if not clear_only:
        for pidx, layer, s, e in layered:
            x.add_effect(PROPS[pidx], layer, 'On', SETTINGS, PALETTE, s, e)

    total = sum(
        sum(len(l) for l in x.xl('getEffectIDs', model=p)['effects'])
        for p in PROPS
    )
    expected = 0 if clear_only else len(layered)
    assert total == expected, f'expected {expected}, found {total}'

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
