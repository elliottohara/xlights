"""Chorus 1 — amber arch chase, tiled from the user's hand-edited pattern.

v4 (current): user hand-edited two bar-length SingleStrand effects on
`Arches - All` L0 and liked the timing/look — asked to repeat that same
motif across the whole chorus. Read back live from the GUI:

    68975-72275  Left-Right   (period 3300 ms)
    72275-75575  Right-Left

Each is ONE SingleStrand Chase (not per-beat) with `Chase_Rotations=4`
(one back-and-forth cycle per implied beat inside the span) plus a Blink
FX overlay (intensity/speed 128), `Per Model Per Preview` buffer, single
amber palette slot. This script locks that 3300 ms period + L-R/R-L
alternation to the discovered phase (anchor 68975) and tiles it across
the full C1 window (67275-93925), including a clipped lead-in segment
before 68975 and a clipped tail segment past 92075 so the whole chorus
is covered edge to edge. The two original hand-placed spans fall out of
the tiling unchanged (verified by assertion).

L1 stays a single Off across the window (kills the Whole Scene aurora).

History: v1 per-arch On pulses REJECTED; v2 red+amber dual chase per bar
REJECTED; v3 one-sweep-per-beat REJECTED (wrong beat phase, then fixed in
v3.1 to land-on-beat) — superseded entirely by this hand-edited v4 motif.

Run (Slot A):
    python3 c1_arches_beat_chase.py [--dry-run] [--clear-only] [--rework]
"""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-a/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
SEQ_LEN = 308314

WIN_START = 67275
WIN_END = 93925

# Phase/period read back from the user's live hand edit.
ANCHOR = 68975
PERIOD = 3300

TARGET = 'Arches - All'
STALE = ['Arch - 1', 'Arch - 2', 'Arch - 3', 'Arch - 4']
OWNED = {TARGET: {0, 1}}
CLEAR = {**OWNED, **{a: {0, 1} for a in STALE}}

ROSA_AMBER = '#ffd89a'
PALETTE = f'C_BUTTON_Palette1={ROSA_AMBER},C_CHECKBOX_Palette1=1'


def chase_settings(direction):
    # Verbatim template read back from the user's hand-edited GUI effect.
    return (
        'B_CHOICE_BufferStyle=Per Model Per Preview,'
        'E_CHECKBOX_Chase_Group_All=0,'
        f'E_CHOICE_Chase_Type1={direction},'
        'E_CHOICE_Fade_Type=From Head,'
        'E_CHOICE_SingleStrand_Colors=Palette,'
        'E_CHOICE_SingleStrand_FX=Blink,'
        'E_CHOICE_SingleStrand_FX_Palette=Default,'
        'E_CHOICE_Skips_Direction=Left,'
        'E_NOTEBOOK_SSEFFECT_TYPE=Chase,'
        'E_SLIDER_Color_Mix1=20,'
        'E_SLIDER_FX_Intensity=128,'
        'E_SLIDER_FX_Speed=128,'
        'E_SLIDER_Number_Chases=1,'
        'E_SLIDER_Skips_Advance=0,'
        'E_SLIDER_Skips_BandSize=1,'
        'E_SLIDER_Skips_SkipSize=1,'
        'E_SLIDER_Skips_StartPos=1,'
        'E_TEXTCTRL_Chase_Offset=0.0,'
        'E_TEXTCTRL_Chase_Rotations=4'
    )


def direction_for(n):
    return 'Left-Right' if n % 2 == 0 else 'Right-Left'


def plan_segments():
    """Tile PERIOD-length segments phase-locked to ANCHOR across the window,
    clipping the first/last to WIN_START/WIN_END."""
    n = (WIN_START - ANCHOR) // PERIOD
    segs = []
    while ANCHOR + n * PERIOD < WIN_END:
        seg_start = max(WIN_START, ANCHOR + n * PERIOD)
        seg_end = min(WIN_END, ANCHOR + (n + 1) * PERIOD)
        if seg_end > seg_start:
            segs.append((seg_start, seg_end, direction_for(n)))
        n += 1
    return segs


def window_effects(model, layers=None):
    want = layers if layers is not None else CLEAR.get(model)
    layer_list = x.xl('getEffectIDs', model=model)['effects']
    hits = []
    for li, ids in enumerate(layer_list):
        if want is not None and li not in want:
            continue
        for eid in ids:
            s = x.xl('getEffectSettings', model=model, layer=str(li), id=str(eid))
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                hits.append((li, eid, s.get('name')))
    return hits


def clear_window_via_xsq():
    tree = ET.parse(XSQ)
    ee = tree.getroot().find('ElementEffects')
    removed = 0
    for el in ee.findall('Element'):
        name = el.get('name')
        if name not in CLEAR:
            continue
        want = CLEAR[name]
        for li, layer in enumerate(el.findall('EffectLayer')):
            if li not in want:
                continue
            for eff in list(layer.findall('Effect')):
                s, e = int(eff.get('startTime')), int(eff.get('endTime'))
                if e > WIN_START and s < WIN_END:
                    layer.remove(eff)
                    removed += 1
    tree.write(XSQ, encoding='UTF-8', xml_declaration=True)
    return removed


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv
    rework = '--rework' in sys.argv

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info

    segs = plan_segments()
    # Sanity: the user's two live edits must fall out of this tiling exactly.
    assert (68975, 72275, 'Left-Right') in segs, segs
    assert (72275, 75575, 'Right-Left') in segs, segs

    dirty = {m: hits for m in CLEAR if (hits := window_effects(m))}
    print(f'plan: {TARGET} L1 Off + {len(segs)}x SingleStrand '
          f'(period {PERIOD}ms, phase-locked to the hand-edited pair, '
          f'alternating L-R/R-L) {WIN_START}-{WIN_END}')
    for st, et, d in segs:
        print(f'  {st}-{et} {d}')
    if dirty:
        print(f'  will clear in-window: { {m: len(h) for m, h in dirty.items()} }')

    if dry:
        print('dry-run: no writes')
        return

    if dirty:
        if TARGET in dirty and not rework:
            raise SystemExit(
                f'C1 window not empty on {TARGET} — rerun with --rework.')
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} window effects via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        assert int(x.xl('getOpenSequence').get('len', 0)) == SEQ_LEN

    if not clear_only:
        x.add_effect(TARGET, 1, 'Off', '', '', WIN_START, WIN_END)
        print(f'  + {TARGET} L1 Off')
        for st, et, d in segs:
            x.add_effect(TARGET, 0, 'SingleStrand', chase_settings(d),
                         PALETTE, st, et)
        print(f'  + {len(segs)} chase segments')

    got = window_effects(TARGET)
    if clear_only:
        assert not got, got
    else:
        assert len([h for h in got if h[0] == 1]) == 1, got
        assert len([h for h in got if h[0] == 0]) == len(segs), got
    for a in STALE:
        assert not window_effects(a), f'stale left on {a}'

    # V1 chords still on L0 before C1
    pre = [eid for eid in x.xl('getEffectIDs', model=TARGET)['effects'][0]
           if int(x.xl('getEffectSettings', model=TARGET, layer='0',
                       id=str(eid))['endTime']) <= WIN_START]
    assert pre, 'V1 Arches - All L0 chords missing'

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
