"""Chorus 1 — black out GE Merry Christmas so only Christ shows.

Whole Scene aurora paints the full sign; Christ already has its white
reveal on `GE Merry Christmas/Christ`. Mirror the PC1 Off pattern: Off on
the whole prop L0 for the C1 window (67275–93925). Empty settings/palette
like the existing PC1 Offs. Christ L0/L1 reveal left alone.

Run (Slot A):
    python3 c1_merry_christmas_blackout.py [--dry-run] [--clear-only] [--rework]
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

PROP = 'GE Merry Christmas'
CHRIST = 'GE Merry Christmas/Christ'
OWNED = {PROP: {0}}
CLEAR = OWNED


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
                hits.append((li, eid, s.get('name'), int(s['startTime']),
                             int(s['endTime'])))
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

    dirty = window_effects(PROP)
    # Only treat our owned C1 Off as reworkable; refuse if something else is there.
    non_off = [h for h in dirty if h[2] != 'Off']
    our_off = [h for h in dirty if h[2] == 'Off'
               and h[3] == WIN_START and h[4] == WIN_END]

    print(f'plan: {PROP} L0 Off {WIN_START}-{WIN_END} (Christ reveal untouched)')
    if dirty:
        print(f'  in-window now: {dirty}')

    if dry:
        print('dry-run: no writes')
        return

    if non_off:
        raise SystemExit(f'unexpected non-Off C1 effects on {PROP}: {non_off}')

    if dirty and not (rework or clear_only):
        if our_off and len(dirty) == len(our_off):
            print('already present — nothing to do')
            return
        raise SystemExit(f'C1 window not empty on {PROP} — rerun with --rework.')

    if dirty and (rework or clear_only):
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        removed = clear_window_via_xsq()
        print(f'cleared {removed} window effects via .xsq')
        x.xl('openSequence', seq=XSQ, timeout=120)
        assert int(x.xl('getOpenSequence').get('len', 0)) == SEQ_LEN

    if not clear_only:
        x.add_effect(PROP, 0, 'Off', '', '', WIN_START, WIN_END)
        print(f'  + {PROP} L0 Off')

    got = window_effects(PROP)
    expected = 0 if clear_only else 1
    assert len(got) == expected, got
    if not clear_only:
        assert got[0][2] == 'Off', got

    # Christ C1 reveal must still be there.
    christ = []
    for li, ids in enumerate(x.xl('getEffectIDs', model=CHRIST)['effects']):
        for eid in ids:
            s = x.xl('getEffectSettings', model=CHRIST, layer=str(li), id=str(eid))
            if int(s['endTime']) > WIN_START and int(s['startTime']) < WIN_END:
                christ.append((li, s.get('name')))
    assert any(n == 'Marquee' for _, n in christ), christ
    assert any(n == 'Color Wash' for _, n in christ), christ
    print(f'  Christ C1 intact: {christ}')

    x.save(XSQ)
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
