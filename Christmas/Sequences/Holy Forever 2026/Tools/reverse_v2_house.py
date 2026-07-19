"""Reverse the wall/house marquee direction during verse 2 (user request 2026-07-13).

`House Outline` and `Roof` L0 carry the same Single Line Marquee bed for the
whole song. This flips ONLY the V2 block (95100-127625) to
E_CHECKBOX_Marquee_Reverse=1 so the chase runs the opposite way for the second
verse, then returns to normal at chorus 2. Everything else is re-added
byte-identical to the current EffectDB strings.

Method (the only safe effect edit, per AGENTS.md): wipe L0 with
cloneModelEffects from the 1-layer empty `House` source (deeper layers stay
untouched) and re-add all 12 effects via addEffect. Pre-verifies the live
session matches the expected bed before touching anything; aborts otherwise.

Saving/backup is done by the caller (save session -> cp backup -> run this ->
save again), same pattern as the other tmp_holy scripts.

Run: python3 Christmas/Sequences/Holy Forever 2026/Tools/reverse_v2_house.py [--dry-run]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

ELEMENTS = ['House Outline', 'Roof']
EMPTY_SOURCE = 'House'                 # 1 empty layer -> wipe touches L0 only
V2 = (95100, 127625)

MARQ_A = ('B_CHOICE_BufferStyle=Single Line,E_CHECKBOX_Marquee_PixelOffsets=0,'
          'E_CHECKBOX_Marquee_Reverse={rev},E_CHECKBOX_Marquee_WrapX=0,'
          'E_NOTEBOOK_Marquee=Settings,E_SLIDER_MarqueeXC=0,E_SLIDER_MarqueeYC=0,'
          'E_SLIDER_Marquee_Band_Size=4,E_SLIDER_Marquee_ScaleX=100,'
          'E_SLIDER_Marquee_ScaleY=100,E_SLIDER_Marquee_Skip_Size=7,'
          'E_SLIDER_Marquee_Speed=2,E_SLIDER_Marquee_Stagger=0,'
          'E_SLIDER_Marquee_Start=0,E_SLIDER_Marquee_Thickness=3,'
          'T_TEXTCTRL_Fadein=.45,T_TEXTCTRL_Fadeout=.45')
MARQ_B = ('B_CHOICE_BufferStyle=Single Line,E_CHECKBOX_Marquee_PixelOffsets=0,'
          'E_CHECKBOX_Marquee_Reverse=0,E_CHECKBOX_Marquee_WrapX=0,'
          'E_NOTEBOOK_Marquee=Settings,E_SLIDER_MarqueeXC=0,E_SLIDER_MarqueeYC=0,'
          'E_SLIDER_Marquee_Band_Size=4,E_SLIDER_Marquee_ScaleX=100,'
          'E_SLIDER_Marquee_ScaleY=100,E_SLIDER_Marquee_Skip_Size=4,'
          'E_SLIDER_Marquee_Speed=5,E_SLIDER_Marquee_Stagger=0,'
          'E_SLIDER_Marquee_Start=0,E_SLIDER_Marquee_Thickness=4,'
          'T_TEXTCTRL_Fadein=.25,T_TEXTCTRL_Fadeout=.35')
ON_FINAL = 'E_CHECKBOX_On_Shimmer=1,T_TEXTCTRL_Fadeout=5'

BTNS = ('C_BUTTON_Palette1=#EEEAE2,C_BUTTON_Palette2=#075FCC,'
        'C_BUTTON_Palette3=#13A8FF,C_BUTTON_Palette4=#031C38,'
        'C_BUTTON_Palette5=#143A5A,C_BUTTON_Palette6=#000000,'
        'C_BUTTON_Palette7=#FFFFFF,C_BUTTON_Palette8=#7258B7,')
PAL1 = BTNS + 'C_CHECKBOX_Palette2=1,C_CHECKBOX_Palette3=1'
PAL3 = BTNS + 'C_CHECKBOX_Palette1=1,C_CHECKBOX_Palette2=1,C_CHECKBOX_Palette3=1'
PAL4 = BTNS + 'C_CHECKBOX_Palette1=1,C_CHECKBOX_Palette3=1'
PAL8 = BTNS + 'C_CHECKBOX_Palette2=1,C_CHECKBOX_Palette4=1'
PAL9 = BTNS + 'C_CHECKBOX_Palette2=1'

# The current bed on BOTH elements: (name, settings, palette, start, end).
# rev=0 everywhere today; the rebuild flips the V2 block to rev=1.
BED = [
    ('Marquee', MARQ_A, PAL8, 15525, 41850),
    ('Marquee', MARQ_A, PAL1, 41850, 67575),
    ('Marquee', MARQ_B, PAL3, 67575, 95100),
    ('Marquee', MARQ_A, PAL1, 95100, 127625),      # <- V2, gets Reverse=1
    ('Marquee', MARQ_B, PAL3, 127625, 154150),
    ('Marquee', MARQ_B, PAL3, 154150, 181900),
    ('Marquee', MARQ_B, PAL3, 181900, 207200),
    ('Marquee', MARQ_B, PAL3, 207200, 234225),
    ('Marquee', MARQ_B, PAL4, 234225, 260750),
    ('Marquee', MARQ_B, PAL4, 260750, 287300),
    ('Marquee', MARQ_B, PAL3, 287300, 301500),
    ('On', ON_FINAL, PAL9, 301500, 308275),
]

def kv(s):
    return dict(p.split('=', 1) for p in s.split(',') if p)

def read_l0(el):
    """[(name, start, end, settings-dict, palette-dict)] for layer 0."""
    out = []
    for eid in x.xl('getEffectIDs', model=el)['effects'][0]:
        e = x.xl('getEffectSettings', model=el, layer='0', id=str(eid))
        out.append((e['name'], int(e['startTime']), int(e['endTime']),
                    e['settings'], e['palette']))
    return sorted(out, key=lambda t: t[1])

def check_bed(el, live, want_rev_on_v2):
    """live L0 must equal BED exactly (with the V2 rev flag as specified)."""
    bad = []
    if len(live) != len(BED):
        return [f'{el}: {len(live)} L0 effects, expected {len(BED)}']
    for (name, settings, palette, s, e), (ln, ls, le, lset, lpal) in zip(BED, live):
        rev = '1' if (want_rev_on_v2 and (s, e) == V2) else '0'
        want_s, want_p = kv(settings.format(rev=rev)), kv(palette)
        where = f'{el} {s}-{e}'
        if (ln, ls, le) != (name, s, e):
            bad.append(f'{where}: got {ln} {ls}-{le}')
            continue
        for label, want, got in (('settings', want_s, dict(lset)),
                                 ('palette', want_p, dict(lpal))):
            for k in sorted(set(want) | set(got)):
                if want.get(k) != got.get(k):
                    bad.append(f'{where} {label}: {k} live={got.get(k)!r} '
                               f'expected={want.get(k)!r}')
    return bad

def main():
    dry = '--dry-run' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence open: {info}'

    src = x.xl('getEffectIDs', model=EMPTY_SOURCE)['effects']
    assert len(src) == 1 and not src[0], f'{EMPTY_SOURCE} unusable as wipe source: {src}'

    deep_before = {el: x.xl('getEffectIDs', model=el)['effects'][1:] for el in ELEMENTS}

    # pre-check: live session must match the known bed (rev=0 everywhere)
    problems = []
    for el in ELEMENTS:
        problems += check_bed(el, read_l0(el), want_rev_on_v2=False)
    if problems:
        for p in problems:
            print('  PRECHECK MISMATCH:', p)
        raise SystemExit('live session does not match the expected bed; aborting')
    print(f'precheck OK: {ELEMENTS} each carry the expected {len(BED)}-effect bed')
    if dry:
        print('dry run: no changes made')
        return

    for el in ELEMENTS:
        x.xl('cloneModelEffects', target=el, source=EMPTY_SOURCE, eraseModel='true')
        for name, settings, palette, s, e in BED:
            rev = '1' if (s, e) == V2 else '0'
            x.add_effect(el, 0, name, settings.format(rev=rev), palette, s, e)
        print(f'  {el}: L0 wiped and re-added ({len(BED)} effects, V2 reversed)')

    bad = []
    for el in ELEMENTS:
        bad += check_bed(el, read_l0(el), want_rev_on_v2=True)
        after = x.xl('getEffectIDs', model=el)['effects'][1:]
        if after != deep_before[el]:
            bad.append(f'{el}: deeper layers changed: {deep_before[el]} -> {after}')
    if bad:
        for b in bad:
            print('  MISMATCH:', b)
        raise SystemExit('verification failed - restore from backup')
    print('done: V2 marquee reversed on both elements, deep layers untouched '
          '(not saved)')

if __name__ == '__main__':
    main()
