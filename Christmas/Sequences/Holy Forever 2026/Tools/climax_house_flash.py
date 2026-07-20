"""8-hit Climax drum riff as dramatic white flashes on `House Outline`.

Third attempt at the climax riff request. History:
  1. Roof-line Marquee ("changes direction with each hit") -- disliked.
  2. Individual roof-snowflake Shockwave pops -- disliked ("too subtle" per
     user follow-up "No. Don't like it.").
  3. THIS: "Let's use house outline instead. Just flash it, fairly
     dramatically." -- whole-model bright white strobe flashes, one per hit.

Timing correction after user review: the original evenly spaced eighth-note
guess was wrong. A targeted 1024-point STFT (128-sample hop) on the source
audio found the actual fast fill as 8 consecutive transient peaks at
233287.9, 233494.0, 233697.1, 233909.0, 234112.2, 234321.2, 234536.0, and
234742.0 ms. The live starts below are those peaks snapped to 25 ms frames.
The fill is roughly 16th notes and straddles the 233925 ms Climax downbeat.

Each flash is short (FLASH_MS) relative to the ~400-425 ms hit spacing, so
there's a dark gap between hits -- reads as 8 distinct strobes, not one
continuous glow. Instant attack / short decay for a "snap" flash look.

`House Outline` currently carries no effects on any of its 4 layers -- this
uses L0 only and does not touch L1-3.

Run: python3 "Christmas/Sequences/Holy Forever 2026/Tools/climax_house_flash.py" [--dry-run] [--clear-only]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

ELEMENT = 'House Outline'
EMPTY_SOURCE = 'House'  # 1-layer empty source -> cloneModelEffects wipe touches L0 only

HITS = [233300, 233500, 233700, 233900, 234100, 234325, 234525, 234750]
FLASH_MS = 175  # preserves the approved shape on the 25 ms frame grid

FLASH = 'E_CHECKBOX_On_Shimmer=0,T_TEXTCTRL_Fadein=0,T_TEXTCTRL_Fadeout=.15'
PALETTE = 'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'


def windows():
    return [(t, t + FLASH_MS) for t in HITS]


def read_l0():
    out = []
    for eid in x.xl('getEffectIDs', model=ELEMENT)['effects'][0]:
        e = x.xl('getEffectSettings', model=ELEMENT, layer='0', id=str(eid))
        out.append((e['name'], int(e['startTime']), int(e['endTime'])))
    return sorted(out, key=lambda t: t[1])


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence open: {info}'

    plan = windows()
    for s, e in plan:
        print(f'  {s}-{e}  ({e - s} ms)')
    if dry:
        print('dry run: no changes made')
        return

    src = x.xl('getEffectIDs', model=EMPTY_SOURCE)['effects']
    assert len(src) == 1 and not src[0], f'{EMPTY_SOURCE} unusable as wipe source: {src}'
    x.xl('cloneModelEffects', target=ELEMENT, source=EMPTY_SOURCE, eraseModel='true')

    if not clear_only:
        for s, e in plan:
            x.add_effect(ELEMENT, 0, 'On', FLASH, PALETTE, s, e)

    after = read_l0()
    expected_n = 0 if clear_only else len(plan)
    if len(after) != expected_n:
        raise SystemExit(f'VERIFY FAILED: expected {expected_n} L0 effects, got {len(after)}: {after}')
    print(f'done: {ELEMENT} L0 rebuilt ({len(after)} effects; not saved).')


if __name__ == '__main__':
    main()
