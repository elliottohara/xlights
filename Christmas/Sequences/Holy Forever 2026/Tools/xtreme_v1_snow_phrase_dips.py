"""Xtreme V1 (5/5): Whole Scene snow dips in the vocal rests.

Rebuild of intro_snow_inverse.py with one addition — the Xtreme "go dark
between phrases" rule. Within V1 the verse hold (≈28/400) now dips toward
16/400 during gaps ≥500 ms in the `Lyrics Lead` WORD layer (the phrase
layer is contiguous by construction, so words are the honest rest signal).
Everything else (intro Holy-swell inverse curve, ease to PC1) is identical
to the approved baseline.

Owns `Whole Scene` L0.

Run:
    python3 .../Tools/xtreme_v1_snow_phrase_dips.py [--dry-run]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/xtremeify/Tools')
import xlights_api as x


OUT = ('/Users/elliott.ohara/xlights-worktrees/xtremeify/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
EMPTY_SOURCE = 'House'
TARGET = 'Whole Scene'
LYRICS = 'Lyrics Lead'
START, END = 0, 41850
V1_START, V1_END = 15275, 39975

BASE = 55
DIP = 18
START_B = 50
VERSE_B = 28
REST_B = 16      # during vocal rests
END_B = 12
MIN_GAP_MS = 500
RAMP_MS = 300


def word_gaps():
    """Gaps >= MIN_GAP_MS between labeled marks on the words layer within V1."""
    ids = x.xl('getEffectIDs', model=LYRICS)['effects'][1]
    words = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=LYRICS, layer=1, id=eid)
        if s.get('name', '').strip():
            words.append((int(s['startTime']), int(s['endTime'])))
    words.sort()
    gaps = []
    for (s1, e1), (s2, e2) in zip(words, words[1:]):
        if e1 >= V1_END:
            break
        if s2 - e1 >= MIN_GAP_MS and e1 >= V1_START:
            gaps.append((e1, min(s2, END)))
    return gaps


def brightness_vc(gaps):
    pts = [
        (0, START_B), (1500, BASE), (3900, BASE), (4400, DIP), (5100, DIP),
        (6400, BASE), (9000, BASE), (10550, BASE), (11000, DIP), (11600, DIP),
        (13300, BASE), (14500, BASE), (15520, VERSE_B),
    ]
    for gs, ge in gaps:
        pts.append((gs + RAMP_MS, REST_B))
        pts.append((max(gs + RAMP_MS, ge - RAMP_MS), REST_B))
        pts.append((ge + RAMP_MS, VERSE_B))
    pts.append((39000, VERSE_B))
    pts.append((END, END_B))
    pts = sorted(set(pts))
    # drop any point that landed out of order after ramps
    clean = []
    for ms, b in pts:
        if clean and ms <= clean[-1][0]:
            continue
        clean.append((ms, b))
    values = ';'.join(f'{ms / float(END):.4f}:{b / 400.0:.4f}' for ms, b in clean)
    return ('Active=TRUE|Id=ID_VALUECURVE_Brightness|Type=Custom|'
            f'Min=0.00|Max=400.00|RV=TRUE|Values={values}|')


SETTINGS = (
    'E_CHOICE_Falling=Driving,'
    'E_SLIDER_Snowflakes_Count=90,'
    'E_SLIDER_Snowflakes_Speed=4,'
    'E_SLIDER_Snowflakes_Type=1,'
    'T_TEXTCTRL_Fadein=2.0,'
    'T_TEXTCTRL_Fadeout=2.00'
)


def main():
    dry = '--dry-run' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    gaps = word_gaps()
    print(f'{len(gaps)} vocal rests >= {MIN_GAP_MS}ms in V1:')
    for gs, ge in gaps:
        print(f'  {gs}-{ge} ({ge - gs}ms)')
    vc = brightness_vc(gaps)
    palette = (f'C_BUTTON_Palette1=#eeeae2,C_CHECKBOX_Palette1=1,'
               f'C_VALUECURVE_Brightness={vc}')

    if dry:
        print('dry-run: no writes')
        print(vc)
        return

    x.xl('cloneModelEffects', target=TARGET, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=TARGET)['effects']
    assert not left[0], f'L0 still has effects after wipe: {left[0]}'

    x.add_effect(TARGET, 0, 'Snowflakes', SETTINGS, palette, START, END)
    verify = x.xl('getEffectSettings', model=TARGET, layer=0, id=0)
    assert verify['name'] == 'Snowflakes'
    assert verify.get('palette', {}).get('C_VALUECURVE_Brightness'), 'VC missing'
    print(f'added: Snowflakes {verify["startTime"]}-{verify["endTime"]} with rest dips')

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
