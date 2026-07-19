"""Strip this session's effects from everything EXCEPT the house outline.

Keeps: wind Marquee on 'House Outline' L1 and 'Roof' L1 (walls + roofline).
Removes: whole-scene gust, ground/arch/icicle/mini-tree/mega-tree wind, all
singing faces.

The API cannot delete effects, so:
  - layers that contain ONLY my effects at layer 0 -> cloneModelEffects wipe
    (true deletion): Arches - All, all 10 singers.
  - everything else -> "Off-parking": setEffectSettings renames each of my
    effects to 'Off' and shrinks it to a 25 ms slot before 180 ms, where the
    display is fully dark (original design starts at 180 ms). Inert +
    invisible; rows can be hand-deleted in the GUI later if wanted.
    (Safe here because setEffectSettings value-mangling doesn't matter for
    an Off effect - it ignores settings entirely.)

Verifies originals are untouched. Not saved; render separately.
"""
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

EMPTY = 'House'
WIND_END = 15520

# element -> (layer, effect name) for my wind effects to Off-park
PARK = {
    'Whole Scene': (1, 'Bars'),
    'Icicles GRP': (2, 'Marquee'),
    'Mini Trees': (2, 'Marquee'),
    'Mega Tree': (6, 'Spirals'),
    'Yard Borders': (0, 'Marquee'),
    'Driveway': (0, 'Marquee'),
    'Canes': (0, 'Marquee'),
    'Colum Shrubs': (0, 'Marquee'),
}
WIPE_L0 = ['Arches - All',
           'GE 8ft Snowman Singing', 'EFL Teddy', 'GE Santa Singing',
           'GE Grinch Talk', 'SingingTree', 'Toni - Penguin 1', 'Toni - Penguin 2',
           'Singing Bulb - Left', 'Singing Bulb - Center', 'Singing Bulb - Right']
KEEP = {'House Outline': (1, 'Marquee', 5), 'Roof': (1, 'Marquee', 5)}

def layer_effects(el, layer):
    ids = x.xl('getEffectIDs', model=el)['effects']
    if layer >= len(ids):
        return []
    out = []
    for eid in ids[layer]:
        e = x.xl('getEffectSettings', model=el, layer=str(layer), id=str(eid))
        out.append((eid, e['name'], int(e['startTime']), int(e['endTime'])))
    return out

def main():
    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info

    # ---- preflight ----
    plan = {}
    for el, (layer, name) in PARK.items():
        effs = layer_effects(el, layer)
        mine = [t for t in effs if t[1] == name and t[2] >= 180 and t[3] <= WIND_END]
        others = [t for t in effs if t not in mine]
        assert len(mine) == 5, (el, layer, mine)
        assert all(o[2] >= WIND_END for o in others), (el, 'unexpected originals', others)
        plan[el] = (layer, mine, len(others))
    for el in WIPE_L0:
        effs = layer_effects(el, 0)
        assert effs and all(n in ('Faces', 'Marquee') and e <= 308264 for _, n, s, e in effs), (el, effs)
        if el == 'Arches - All':
            assert all(n == 'Marquee' and e <= WIND_END for _, n, s, e in effs), (el, effs)
        else:
            assert all(n == 'Faces' for _, n, s, e in effs), (el, effs)
    src = x.xl('getEffectIDs', model=EMPTY)['effects']
    assert all(not l for l in src), f'{EMPTY} not empty: {src}'

    # ---- execute ----
    parked = 0
    for el, (layer, mine, _) in plan.items():
        for slot, (eid, name, s, e) in enumerate(sorted(mine, key=lambda t: t[2])):
            x.xl('setEffectSettings', model=el, layer=str(layer), id=str(eid),
                 name='Off', startTime=str(slot * 25), endTime=str(slot * 25 + 25))
            parked += 1
        print(f'  parked {len(mine)} on {el!r} L{layer}')
    for el in WIPE_L0:
        x.xl('cloneModelEffects', target=el, source=EMPTY, eraseModel='true')
        print(f'  wiped {el!r} L0')
    try:
        x.xl('unselectEffects', timeout=10)
    except Exception:
        pass

    # ---- verify ----
    bad = []
    for el, (layer, name) in PARK.items():
        effs = layer_effects(el, layer)
        live = [t for t in effs if t[3] > 180]
        offs = [t for t in effs if t[1] == 'Off' and t[3] <= 180]
        if len(offs) != 5 or any(t[1] == name and t[3] <= WIND_END and t[3] > 180 for t in live):
            bad.append((el, layer, effs))
        if len(live) != plan[el][2]:
            bad.append((el, 'original count changed', len(live), plan[el][2]))
    for el in WIPE_L0:
        if layer_effects(el, 0):
            bad.append((el, 'L0 not empty'))
    for el, (layer, name, count) in KEEP.items():
        effs = layer_effects(el, layer)
        if len([t for t in effs if t[1] == name]) != count:
            bad.append((el, 'KEEP damaged', effs))
    if bad:
        for b in bad:
            print('  PROBLEM:', b)
        raise SystemExit('verification failed')
    print(f'done: {parked} effects parked as Off stubs, {len(WIPE_L0)} elements wiped; '
          'outline wind (House Outline L1 + Roof L1) intact')

if __name__ == '__main__':
    main()
