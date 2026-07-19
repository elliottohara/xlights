"""Intimate acoustic V1: piano-chord SingleStrand on Arches - All.

Reads labeled 'P' marks from the **Piano Chords** timing track (imported
from Timing Templates/Holy Forever Piano Chords.xsq — audio-detected big
wide piano hits, NOT the beat grid).

One effect per mark on `Arches - All`, BufferStyle = Per Model Per Preview
so every arch gets the same From Middle chase together. Rotations = 1.0
over the full gap to the next chord (slow apex→feet, hit bottom and stop).

Run: python3 Tools/tmp_holy/intimate_arch_chords.py [--dry-run]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x


EMPTY_SOURCE = 'House'
TARGET = 'Arches - All'
TRACK = 'Piano Chords'
ARCHES = ['Arch - 1', 'Arch - 2', 'Arch - 3', 'Arch - 4']
STRANDS = ['Arch 1', 'Arch 2', 'Arch 3']
RANGE_END = 41850
ROTATIONS = '1.0'

SETTINGS = (
    'B_CHOICE_BufferStyle=Per Model Per Preview,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=From Middle,'
    'E_CHOICE_Fade_Type=From Head,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=16,'
    'E_SLIDER_Number_Chases=1,'
    f'E_TEXTCTRL_Chase_Rotations={ROTATIONS},'
    'T_TEXTCTRL_Fadein=0.15,'
    'T_TEXTCTRL_Fadeout=0.35'
)

PALETTE = (
    'C_BUTTON_Palette1=#F0E6D0,'
    'C_CHECKBOX_Palette1=1,'
    'C_SLIDER_Brightness=70'
)


def piano_chords():
    """Labeled 'P' marks from the Piano Chords timing track."""
    try:
        ids = x.xl('getEffectIDs', model=TRACK)['effects'][0]
    except Exception as e:
        raise SystemExit(
            f'timing track {TRACK!r} not in sequence — import '
            f'Timing Templates/Holy Forever Piano Chords.xsq first ({e})')
    out = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=TRACK, layer=0, id=eid)
        label = s.get('name', '')
        if label == 'P':
            out.append(int(s['startTime']))
    return sorted(out)


def wipe(model):
    x.xl('cloneModelEffects', target=model, source=EMPTY_SOURCE, eraseModel='true')
    left = x.xl('getEffectIDs', model=model)['effects']
    assert not left[0], f'{model} not empty after wipe'


def main():
    dry = '--dry-run' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    chords = piano_chords()
    print(f'{len(chords)} Piano Chords marks: {chords}')
    plan = []
    for i, t in enumerate(chords):
        if i + 1 < len(chords):
            end = chords[i + 1] - 25
        else:
            end = min(t + 3200, RANGE_END)
        end = min(end, RANGE_END)
        if end - t < 800:
            print(f'  skip {t}: too short')
            continue
        plan.append((t, end))
        print(f'  {t}-{end} ({end - t}ms) {TARGET}')

    for (s, e), (s2, e2) in zip(plan, plan[1:]):
        assert e <= s2, f'overlap {s}-{e} vs {s2}-{e2}'

    clear = [TARGET] + ARCHES + [f'{a}/{s}' for a in ARCHES for s in STRANDS]
    print(f'plan: wipe {len(clear)}; add {len(plan)} on {TARGET}; '
          f'Per Model Per Preview rot={ROTATIONS}')

    if dry:
        print('dry-run: no writes')
        return

    for m in clear:
        wipe(m)

    for s, e in plan:
        x.add_effect(TARGET, 0, 'SingleStrand', SETTINGS, PALETTE, s, e)

    ids = x.xl('getEffectIDs', model=TARGET)['effects'][0]
    s0 = x.xl('getEffectSettings', model=TARGET, layer=0, id=ids[0])
    print(f'{TARGET}: {len(ids)} effects  '
          f'first={s0["startTime"]}-{s0["endTime"]} '
          f'buf={s0["settings"].get("B_CHOICE_BufferStyle")}')

    out = '/Users/elliott.ohara/xlights/Christmas/Holy Forever 2026.xsq'
    x.save(out)
    print(f'saved {out}')


if __name__ == '__main__':
    main()
