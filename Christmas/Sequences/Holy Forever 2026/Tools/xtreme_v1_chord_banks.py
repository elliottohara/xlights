"""Xtreme V1 (1/5): rotating dim part-bank responders on the 7 piano chords.

Xtreme signature move: rotate WHICH bank answers each accent instead of
hitting the same element every time. The `Arches - All` SingleStrand stays
the constant wide-chord voice (see xtreme_v1_arch_reveal.py); this script
adds a second, dim responder that rotates through part-bank groups, one per
`Piano Chords` `P` mark, using the Xtreme Shockwave skeleton
(Blend_Edges=1, start 1/5, accel 0, Per Model Per Preview so every cane /
ring / plunger pulses individually) at verse brightness (~30).

Bank rotation (chord 1 → 7, final chord doubles up as a small build):
  Canes → Rosa Web Ring → Starlord Plungers → Baby GI Rings →
  Reel Max Circles Outer → Flakes Outline → Mini Tree Stars + Canes

Layer 0 of each bank element is owned by this script (all were empty in
the 2026-07-19 baseline).

Run:
    python3 .../Tools/xtreme_v1_chord_banks.py [--dry-run] [--clear-only]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/xtremeify/Tools')
import xlights_api as x


OUT = ('/Users/elliott.ohara/xlights-worktrees/xtremeify/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
EMPTY_SOURCE = 'House'
TRACK = 'Piano Chords'

BANKS = [
    'Canes',
    'GE Rosa Grande Web Ring GRP',
    'GE Starlord Plunger All GRP',
    'GE Baby Grand Illusion Rings GRP',
    'GE Reel Max Circles Outer GRP',
    'Flakes Outline All GRP',
    'Mini Tree Stars',
]
# chord index -> list of banks that answer it (last chord doubles up)
ROTATION = [[0], [1], [2], [3], [4], [5], [6, 0]]

DUR_MS = 1100        # gentle ballad bloom, not an EDM stab
LAST_DUR_MS = 1400

SETTINGS = (
    'B_CHOICE_BufferStyle=Per Model Per Preview,'
    'E_CHECKBOX_Shockwave_Blend_Edges=1,'
    'E_SLIDER_Shockwave_Accel=0,'
    'E_SLIDER_Shockwave_CenterX=50,'
    'E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_End_Radius=18,'
    'E_SLIDER_Shockwave_End_Width=35,'
    'E_SLIDER_Shockwave_Start_Radius=1,'
    'E_SLIDER_Shockwave_Start_Width=5,'
    'T_TEXTCTRL_Fadein=0.10,'
    'T_TEXTCTRL_Fadeout=0.50'
)

PALETTE = (
    'C_BUTTON_Palette1=#F0E6D0,'
    'C_BUTTON_Palette2=#FFD89A,'
    'C_CHECKBOX_Palette1=1,'
    'C_CHECKBOX_Palette2=1,'
    'C_SLIDER_Brightness=30'
)


def piano_chords():
    ids = x.xl('getEffectIDs', model=TRACK)['effects'][0]
    out = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=TRACK, layer=0, id=eid)
        if s.get('name', '') == 'P':
            out.append(int(s['startTime']))
    return sorted(out)


def wipe(model):
    x.xl('cloneModelEffects', target=model, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=model)['effects']
    assert not left[0], f'{model} layer 0 not empty after wipe'


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    chords = piano_chords()
    assert len(chords) == len(ROTATION), f'{len(chords)} chords vs {len(ROTATION)} rotation slots'

    plan = []
    for i, t in enumerate(chords):
        dur = LAST_DUR_MS if i == len(chords) - 1 else DUR_MS
        for b in ROTATION[i]:
            plan.append((BANKS[b], t, t + dur))
            print(f'  chord {i + 1} @ {t}: {BANKS[b]} ({dur}ms)')

    if dry:
        print('dry-run: no writes')
        return

    for bank in BANKS:
        wipe(bank)

    if not clear_only:
        for bank, s, e in plan:
            x.add_effect(bank, 0, 'Shockwave', SETTINGS, PALETTE, s, e)

    total = 0
    for bank in BANKS:
        n = len(x.xl('getEffectIDs', model=bank)['effects'][0])
        total += n
        print(f'  {bank}: {n} effects on L0')
    expected = 0 if clear_only else len(plan)
    assert total == expected, f'expected {expected}, found {total}'

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
