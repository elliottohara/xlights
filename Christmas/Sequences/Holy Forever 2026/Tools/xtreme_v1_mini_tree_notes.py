"""Xtreme V1 (3/5): mini trees keyed to the real `Piano Notes` onsets.

Replaces the hand-curated intimate_mini_tree_piano.py pulses. Xtreme rule:
100% of starts quantized to note-onset marks, density follows the onsets.
Every labeled `Piano Notes` mark inside V1 gets one warm-gold On pulse on
one of `Mini Tree - 1..4` — EXCEPT marks that coincide with a `Piano
Chords` `P` mark (those are the wide chords already answered by the arch
reveal + rotating banks; the mini trees stay the between-chord voice).

Tree choice follows the melodic contour: the top MIDI note of each mark is
rank-mapped across the verse (lowest top note → Tree 1, highest → Tree 4),
so the trees literally step with the piano line. Same-tree collisions are
clamped to the next pulse start.

Layer 0 of each `Mini Tree - N` is owned by this script.

Run:
    python3 .../Tools/xtreme_v1_mini_tree_notes.py [--dry-run] [--clear-only]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/xtremeify/Tools')
import xlights_api as x


OUT = ('/Users/elliott.ohara/xlights-worktrees/xtremeify/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
EMPTY_SOURCE = 'House'
TREES = [f'Mini Tree - {i}' for i in range(1, 5)]
NOTES_TRACK = 'Piano Notes'
CHORDS_TRACK = 'Piano Chords'
V1_START, V1_END = 15275, 39975   # sung V1 span
PULSE_MS = 425
CHORD_EXCLUDE_MS = 50

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
    notes = []
    for t, lab in labeled_marks(NOTES_TRACK):
        if not (V1_START <= t <= V1_END):
            continue
        if any(abs(t - c) <= CHORD_EXCLUDE_MS for c in chords):
            continue
        midis = [int(n) for n in lab.split()]
        notes.append((t, max(midis)))

    # rank-map top notes to trees 1..4 (melodic contour, even spread)
    order = sorted(set(top for _, top in notes))
    def tree_for(top):
        r = order.index(top) / max(len(order) - 1, 1)
        return 1 + min(3, int(r * 4))

    pulses = []   # (tree name, start, end, top)
    for t, top in notes:
        pulses.append([f'Mini Tree - {tree_for(top)}', t, t + PULSE_MS, top])

    # clamp same-tree collisions
    by_tree = {}
    for p in pulses:
        by_tree.setdefault(p[0], []).append(p)
    for tree, ps in by_tree.items():
        ps.sort(key=lambda p: p[1])
        for cur, nxt in zip(ps, ps[1:]):
            if cur[2] > nxt[1] - 25:
                cur[2] = nxt[1] - 25
            assert cur[2] - cur[1] >= 150, f'{tree} pulse too short after clamp: {cur}'

    return pulses


def wipe(model):
    x.xl('cloneModelEffects', target=model, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=model)['effects']
    assert not left[0], f'{model} layer 0 not empty after wipe'


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    pulses = plan()
    print(f'{len(pulses)} note pulses (from labeled {NOTES_TRACK} marks in V1, '
          f'chord marks excluded)')
    for tree, s, e, top in pulses:
        print(f'  {s}-{e}  top={top}  {tree}')

    if dry:
        print('dry-run: no writes')
        return

    for tree in TREES:
        wipe(tree)

    if not clear_only:
        for tree, s, e, _top in pulses:
            x.add_effect(tree, 0, 'On', SETTINGS, PALETTE, s, e)

    total = 0
    for tree in TREES:
        n = len(x.xl('getEffectIDs', model=tree)['effects'][0])
        total += n
        print(f'  {tree}: {n} effects on L0')
    expected = 0 if clear_only else len(pulses)
    assert total == expected, f'expected {expected}, found {total}'

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
