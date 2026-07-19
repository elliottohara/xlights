"""Xtreme V1 (2/5): arch piano-chord chase becomes a reveal pair.

Same approved From-Middle SingleStrand motion on `Arches - All`, but Xtreme
style: the chase no longer carries color directly. L0 = white SingleStrand
with `T_CHOICE_LayerMethod=1 reveals 2` (motion draws the shape), L1 = warm
ivory→gold Color Wash field (partner supplies the color). Net look: the
expanding chase picks up a subtle warm shift instead of flat ivory.

Timing identical to intimate_arch_chords.py: one pair per `Piano Chords`
`P` mark, span = gap to next chord (last clamped to 41850).

Run:
    python3 .../Tools/xtreme_v1_arch_reveal.py [--dry-run] [--restore-flat]
    (--restore-flat rebuilds the original single-layer flat-color chase)
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/xtremeify/Tools')
import xlights_api as x


OUT = ('/Users/elliott.ohara/xlights-worktrees/xtremeify/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
EMPTY_SOURCE = 'House'
TARGET = 'Arches - All'
TRACK = 'Piano Chords'
RANGE_END = 41850

CHASE_BASE = (
    'B_CHOICE_BufferStyle=Per Model Per Preview,'
    'E_CHECKBOX_Chase_Group_All=0,'
    'E_CHOICE_Chase_Type1=From Middle,'
    'E_CHOICE_Fade_Type=From Head,'
    'E_CHOICE_SingleStrand_Colors=Palette,'
    'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
    'E_SLIDER_Color_Mix1=16,'
    'E_SLIDER_Number_Chases=1,'
    'E_TEXTCTRL_Chase_Rotations=1.0,'
    'T_TEXTCTRL_Fadein=0.15,'
    'T_TEXTCTRL_Fadeout=0.35'
)
CHASE_SETTINGS = CHASE_BASE + ',T_CHOICE_LayerMethod=1 reveals 2'
CHASE_PALETTE = (
    'C_BUTTON_Palette1=#FFFFFF,'
    'C_CHECKBOX_Palette1=1,'
    'C_SLIDER_Brightness=100'
)

WASH_SETTINGS = (
    'E_CHECKBOX_ColorWash_HFade=1,'
    'E_CHECKBOX_ColorWash_VFade=0,'
    'E_TEXTCTRL_ColorWash_Cycles=1.0'
)
WASH_PALETTE = (
    'C_BUTTON_Palette1=#F0E6D0,'
    'C_BUTTON_Palette2=#FFD89A,'
    'C_CHECKBOX_Palette1=1,'
    'C_CHECKBOX_Palette2=1,'
    'C_SLIDER_Brightness=70'
)

# original flat look, for --restore-flat
FLAT_SETTINGS = CHASE_BASE
FLAT_PALETTE = (
    'C_BUTTON_Palette1=#F0E6D0,'
    'C_CHECKBOX_Palette1=1,'
    'C_SLIDER_Brightness=70'
)


def piano_chords():
    ids = x.xl('getEffectIDs', model=TRACK)['effects'][0]
    out = []
    for eid in ids:
        s = x.xl('getEffectSettings', model=TRACK, layer=0, id=eid)
        if s.get('name', '') == 'P':
            out.append(int(s['startTime']))
    return sorted(out)


def spans(chords):
    plan = []
    for i, t in enumerate(chords):
        end = chords[i + 1] - 25 if i + 1 < len(chords) else min(t + 3200, RANGE_END)
        end = min(end, RANGE_END)
        if end - t >= 800:
            plan.append((t, end))
    return plan


def main():
    dry = '--dry-run' in sys.argv
    restore = '--restore-flat' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence: {info}'

    plan = spans(piano_chords())
    mode = 'flat single-layer' if restore else 'reveal pair (L0 chase reveals L1 wash)'
    print(f'{len(plan)} chord spans on {TARGET} — {mode}')
    for s, e in plan:
        print(f'  {s}-{e} ({e - s}ms)')

    if dry:
        print('dry-run: no writes')
        return

    # wipe L0 and L1 (House has 1 layer, so clone-wipe only clears L0;
    # off-park is not needed because L1 is entirely ours — clone from a
    # 2-layer empty source instead: use two successive wipes via House after
    # ensuring L1 has no foreign effects)
    ids = x.xl('getEffectIDs', model=TARGET)['effects']
    x.xl('cloneModelEffects', target=TARGET, source=EMPTY_SOURCE, eraseModel='true')
    ids = x.xl('getEffectIDs', model=TARGET)['effects']
    assert not ids[0], 'L0 not empty after wipe'
    # L1 was empty in the baseline; assert rather than wipe
    assert len(ids) < 2 or not ids[1], f'unexpected L1 effects: {ids[1]}'

    for s, e in plan:
        if restore:
            x.add_effect(TARGET, 0, 'SingleStrand', FLAT_SETTINGS, FLAT_PALETTE, s, e)
        else:
            x.add_effect(TARGET, 0, 'SingleStrand', CHASE_SETTINGS, CHASE_PALETTE, s, e)
            x.add_effect(TARGET, 1, 'Color Wash', WASH_SETTINGS, WASH_PALETTE, s, e)

    ids = x.xl('getEffectIDs', model=TARGET)['effects']
    print(f'{TARGET}: L0={len(ids[0])} L1={len(ids[1]) if len(ids) > 1 else 0}')
    s0 = x.xl('getEffectSettings', model=TARGET, layer=0, id=ids[0][0])
    print(f'  L0 first: {s0["name"]} {s0["startTime"]}-{s0["endTime"]} '
          f'method={s0["settings"].get("T_CHOICE_LayerMethod")}')

    x.save(OUT)
    print(f'saved {OUT}')


if __name__ == '__main__':
    main()
