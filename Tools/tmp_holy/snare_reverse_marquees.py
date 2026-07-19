"""From verse 2 onward, flip House Outline + Roof marquee direction on every snare.

Snares = 72 BPM backbeat (beats 2 & 4) on the verified grid (anchor 180 ms,
bar = 3333.333 ms), snapped to 25 ms frames. Starts at V2 (95100); pre-V2
bed is unchanged. Replaces the earlier whole-V2 Reverse=1 block.

Method: wipe L0 via cloneModelEffects from empty `House`, re-add via addEffect.
Supports --dry-run (prints the planned split, no writes).

Run: python3 Tools/tmp_holy/snare_reverse_marquees.py [--dry-run]
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

ELEMENTS = ['House Outline', 'Roof']
EMPTY_SOURCE = 'House'
V2_START = 95100
BED_END = 301500          # last marquee end; On finale follows
FRAME = 25
BAR = 3333.333333
ANCHOR = 180.0
BEAT = BAR / 4

MARQ_A = ('B_CHOICE_BufferStyle=Single Line,E_CHECKBOX_Marquee_PixelOffsets=0,'
          'E_CHECKBOX_Marquee_Reverse={rev},E_CHECKBOX_Marquee_WrapX=0,'
          'E_NOTEBOOK_Marquee=Settings,E_SLIDER_MarqueeXC=0,E_SLIDER_MarqueeYC=0,'
          'E_SLIDER_Marquee_Band_Size=4,E_SLIDER_Marquee_ScaleX=100,'
          'E_SLIDER_Marquee_ScaleY=100,E_SLIDER_Marquee_Skip_Size=7,'
          'E_SLIDER_Marquee_Speed=2,E_SLIDER_Marquee_Stagger=0,'
          'E_SLIDER_Marquee_Start=0,E_SLIDER_Marquee_Thickness=3,'
          'T_TEXTCTRL_Fadein=.45,T_TEXTCTRL_Fadeout=.45')
MARQ_B = ('B_CHOICE_BufferStyle=Single Line,E_CHECKBOX_Marquee_PixelOffsets=0,'
          'E_CHECKBOX_Marquee_Reverse={rev},E_CHECKBOX_Marquee_WrapX=0,'
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

# Original section bed (settings template, palette, start, end).
# Marquee sections from V2_START on get split at snares; Reverse alternates.
SECTIONS = [
    ('Marquee', MARQ_A, PAL8, 15525, 41850),
    ('Marquee', MARQ_A, PAL1, 41850, 67575),
    ('Marquee', MARQ_B, PAL3, 67575, 95100),
    ('Marquee', MARQ_A, PAL1, 95100, 127625),
    ('Marquee', MARQ_B, PAL3, 127625, 154150),
    ('Marquee', MARQ_B, PAL3, 154150, 181900),
    ('Marquee', MARQ_B, PAL3, 181900, 207200),
    ('Marquee', MARQ_B, PAL3, 207200, 234225),
    ('Marquee', MARQ_B, PAL4, 234225, 260750),
    ('Marquee', MARQ_B, PAL4, 260750, 287300),
    ('Marquee', MARQ_B, PAL3, 287300, 301500),
    ('On', ON_FINAL, PAL9, 301500, 308275),
]


def snap(t):
    return int(round(t / FRAME) * FRAME)


def snare_times():
    out = []
    t = ANCHOR
    while t < BED_END + BAR:
        for i in (1, 3):
            s = snap(t + i * BEAT)
            if V2_START <= s < BED_END:
                out.append(s)
        t += BAR
    return sorted(set(out))


def rev_at(start, snares):
    """Direction for a segment starting at `start`: flips at each snare."""
    return sum(1 for s in snares if s <= start) % 2


def build_effects(snares):
    """Full L0 effect list after snare-splitting."""
    out = []
    for name, tmpl, palette, s, e in SECTIONS:
        if name != 'Marquee' or e <= V2_START:
            # pre-V2 (and the On finale): always Reverse=0 / no flip
            settings = tmpl if name == 'On' else tmpl.format(rev=0)
            out.append((name, settings, palette, s, e))
            continue
        cuts = [s] + [sn for sn in snares if s < sn < e] + [e]
        for a, b in zip(cuts, cuts[1:]):
            if b <= a:
                continue
            out.append((name, tmpl.format(rev=rev_at(a, snares)), palette, a, b))
    return out


def kv(s):
    return dict(p.split('=', 1) for p in s.split(',') if p)


def read_l0(el):
    out = []
    for eid in x.xl('getEffectIDs', model=el)['effects'][0]:
        e = x.xl('getEffectSettings', model=el, layer='0', id=str(eid))
        out.append((e['name'], int(e['startTime']), int(e['endTime']),
                    e['settings'], e['palette']))
    return sorted(out, key=lambda t: t[1])


def check(el, live, want):
    bad = []
    if len(live) != len(want):
        return [f'{el}: {len(live)} L0 effects, expected {len(want)}']
    for (name, settings, palette, s, e), (ln, ls, le, lset, lpal) in zip(want, live):
        where = f'{el} {s}-{e}'
        if (ln, ls, le) != (name, s, e):
            bad.append(f'{where}: got {ln} {ls}-{le}')
            continue
        want_s, want_p = kv(settings), kv(palette)
        for label, w, g in (('settings', want_s, dict(lset)),
                            ('palette', want_p, dict(lpal))):
            for k in sorted(set(w) | set(g)):
                if w.get(k) != g.get(k):
                    bad.append(f'{where} {label}: {k} live={g.get(k)!r} '
                               f'expected={w.get(k)!r}')
    return bad


def main():
    dry = '--dry-run' in sys.argv
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), f'wrong sequence open: {info}'

    snares = snare_times()
    want = build_effects(snares)
    print(f'{len(snares)} snares from {snares[0]}→{snares[-1]}; '
          f'{len(want)} L0 effects planned '
          f'(was {sum(1 for *_, s, e in SECTIONS)} sections)')
    if dry:
        # show first few V2 flips
        print('first V2 segments:')
        for name, settings, _, s, e in want:
            if s < V2_START or name != 'Marquee':
                continue
            if s > snares[5]:
                break
            rev = kv(settings)['E_CHECKBOX_Marquee_Reverse']
            print(f'  {s}-{e} Reverse={rev}')
        print('dry run: no changes made')
        return

    src = x.xl('getEffectIDs', model=EMPTY_SOURCE)['effects']
    assert len(src) == 1 and not src[0], f'{EMPTY_SOURCE} unusable as wipe source: {src}'
    deep_before = {el: x.xl('getEffectIDs', model=el)['effects'][1:] for el in ELEMENTS}

    for el in ELEMENTS:
        x.xl('cloneModelEffects', target=el, source=EMPTY_SOURCE, eraseModel='true')
        for name, settings, palette, s, e in want:
            x.add_effect(el, 0, name, settings, palette, s, e)
        print(f'  {el}: L0 wiped and re-added ({len(want)} effects)')

    bad = []
    for el in ELEMENTS:
        bad += check(el, read_l0(el), want)
        after = x.xl('getEffectIDs', model=el)['effects'][1:]
        if after != deep_before[el]:
            bad.append(f'{el}: deeper layers changed')
    if bad:
        for b in bad[:40]:
            print('  MISMATCH:', b)
        if len(bad) > 40:
            print(f'  ... +{len(bad) - 40} more')
        raise SystemExit('verification failed — restore from backup')
    print('done: snare-flipped marquees from V2 on (not saved)')


if __name__ == '__main__':
    main()
