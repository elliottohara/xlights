"""V2 house marquees — flip direction every bar, hard reversals, on FELT beat 1.

User ask (2026-08-01): "For verse 2, for each bar, can we just change the
marquee direction. No slowing down or fading, just make them go the opposite
direction." Then, after watching the first build: "That was on beat 3. I want
it on beat 1."

⚠ FELT-BEAT MAPPING (user's ear, 2026-08-01): the Beat Count track's labels
sit a HALF BAR off the felt beat — labeled "1" is felt beat 3. Corroborated
twice: the user's hand-placed Mini Grand rings land on labeled "2" and they
hear those as beat 4 (minigrand_cross_beat_rings.py), and the first build of
this script flipped on labeled "1" and they heard beat 3. **Felt beat 1 =
the marks labeled "3"** (95600, 98925, ..., 125600). (A half-bar shift maps
the 2&4 backbeat onto itself, which is why the snare-flux anchor fit in the
notes couldn't detect it.)

The v2_continue_c1.py pass extended the five C1 marquees (Verts / Roof /
Windows / Yard Borders amber `1 reveals 2` marquees + the white Christ
submodel marquee) as single effects 67275-127275, Reverse=0 the whole way.
This script re-tiles 67275-127275 as:

  - one forward segment 67275-95600 (C1 + the half-bar up to the first felt
    downbeat — NOTHING happens at the labeled-"1" 93925 section line), then
  - one segment per felt bar between the labeled-"3" marks, alternating
    E_CHECKBOX_Marquee_Reverse 1,0,1,0,... (first felt bar runs opposite to
    C1), then
  - a half-bar tail 125600-127275 continuing the alternation, ending hard on
    the Soaring/C2 downbeat.

"No slowing down or fading": Speed/Band/Skip/Thickness untouched, no fades
on any segment after the first — hard reversal at each felt bar line. The
first segment keeps Fadein=2 (approved C1 look). The tail has no fadeout —
ask if the 2 s exit fade should come back.

Run in Slot B (XLIGHTS_API_PORT=49914), sequence open:
    python3 v2_marquee_bar_flip.py [--dry-run] [--clear-only]
Idempotent: whatever Marquees currently tile the window are replaced.
--clear-only removes every Marquee in 67275-127275 on the five targets;
restore the single long marquees via git checkout or a .bak backup.
"""
import shutil
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, '/Users/elliott.ohara/xlights-worktrees/slot-b/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-b/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
SEQ_LEN = 308314

C1_START = 67275
V2_START = 93925          # labeled "1" == felt beat 3 — NOT a flip point
V2_END = 127275           # Mood Soaring downbeat == C2
FELT_ONE_LABEL = '3'      # Beat Count label that lands on felt beat 1

# (owner element in ElementEffects, submodel or None, api target)
TARGETS = [
    ('Verts', None, 'Verts'),
    ('Roof', None, 'Roof'),
    ('Windows', None, 'Windows'),
    ('Yard Borders', None, 'Yard Borders'),
    ('GE Merry Christmas', 'Christ', 'GE Merry Christmas/Christ'),
]


def parse(settings):
    return dict(kv.split('=', 1) for kv in settings.split(',') if '=' in kv)


def fmt(d):
    return ','.join(f'{k}={v}' for k, v in d.items())


def flip_points(root):
    """Beat Count marks on felt beat 1 inside V2 = the flip times."""
    for el in root.find('ElementEffects').findall('Element'):
        if el.get('name') == 'Beat Count' and el.get('type') == 'timing':
            hits = [int(e.get('startTime'))
                    for e in el.find('EffectLayer').findall('Effect')
                    if (e.get('label') or '').strip() == FELT_ONE_LABEL]
            break
    else:
        raise SystemExit('Beat Count track not found')
    flips = [t for t in hits if V2_START < t < V2_END]
    assert len(flips) == 10 and flips[0] == 95600 and flips[-1] == 125600, flips
    return flips


def find_layer(el, sub):
    if sub is None:
        return el.findall('EffectLayer')[0]
    for sml in el.findall('SubModelEffectLayer'):
        if sml.get('name') == sub and int(sml.get('layer') or 0) == 0:
            return sml
    raise SystemExit(f'{el.get("name")}/{sub}: submodel layer 0 not found')


def load():
    """Parse the .xsq; collect each target's window Marquees + a template."""
    tree = ET.parse(XSQ)
    root = tree.getroot()
    db = [t.text or '' for t in root.find('EffectDB').findall('Effect')]
    pals = [t.text or '' for t in root.find('ColorPalettes').findall('ColorPalette')]
    elements = {el.get('name'): el
                for el in root.find('ElementEffects').findall('Element')}
    found = {}
    for owner, sub, api in TARGETS:
        layer = find_layer(elements[owner], sub)
        removals = []
        for e in layer.findall('Effect'):
            es, ee = int(e.get('startTime')), int(e.get('endTime'))
            if ee > C1_START and es < V2_END:
                assert (e.get('name') == 'Marquee' and es >= C1_START
                        and ee <= V2_END), \
                    f'{api} L0 collision: {e.get("name")} {es}-{ee}'
                removals.append(e)
        assert removals, f'{api}: no window marquees found'
        template = min(removals, key=lambda e: int(e.get('startTime')))
        found[api] = (layer, removals, parse(db[int(template.get('ref'))]),
                      pals[int(template.get('palette'))])
    return tree, found


def segments(base_settings, flips):
    """(start, end, settings-dict) plan tiling C1_START..V2_END, flipping at
    each felt beat 1. Segment 0 runs forward with the C1 Fadein; the rest
    alternate Reverse starting at 1 and carry no fades."""
    bounds = [C1_START] + flips + [V2_END]
    segs = []
    for i, (s, e) in enumerate(zip(bounds, bounds[1:])):
        d = dict(base_settings)
        d['E_CHECKBOX_Marquee_Reverse'] = '0' if i % 2 == 0 else '1'
        d.pop('T_TEXTCTRL_Fadeout', None)
        if i:
            d.pop('T_TEXTCTRL_Fadein', None)
        segs.append((s, e, d))
    return segs


def main():
    dry = '--dry-run' in sys.argv
    clear_only = '--clear-only' in sys.argv

    if clear_only:
        tree = ET.parse(XSQ)
        root = tree.getroot()
        elements = {el.get('name'): el
                    for el in root.find('ElementEffects').findall('Element')}
        for owner, sub, api in TARGETS:
            layer = find_layer(elements[owner], sub)
            removed = 0
            for e in list(layer.findall('Effect')):
                es, ee = int(e.get('startTime')), int(e.get('endTime'))
                if (e.get('name') == 'Marquee' and es >= C1_START
                        and ee <= V2_END):
                    layer.remove(e)
                    removed += 1
            print(f'{api}: removed {removed} window marquees')
        if dry:
            print('dry-run: no writes')
            return
        x.save(XSQ)
        x.xl('closeSequence', force='true', quiet='true')
        tree.write(XSQ, encoding='UTF-8', xml_declaration=True)
        x.xl('openSequence', seq=XSQ, timeout=300)
        assert int(x.xl('getOpenSequence').get('len', 0)) == SEQ_LEN
        x.save(XSQ)
        print('clear-only done; restore the long marquees via git checkout '
              'or a .bak-before-v2-marquee-flip backup')
        return

    tree, found = load()
    flips = flip_points(tree.getroot())
    print(f'{len(flips)} flip points (felt beat 1): {flips[0]}..{flips[-1]}')

    plan = {api: segments(sett, flips) for api, (_, _, sett, _) in found.items()}
    for api, segs in plan.items():
        rev = ''.join(d['E_CHECKBOX_Marquee_Reverse'] for _, _, d in segs)
        print(f'{api}: {len(segs)} segments, reverse pattern {rev}')

    if dry:
        print('dry-run: no writes')
        return

    info = x.xl('getOpenSequence')
    assert 'Holy Forever 2026' in info.get('seq', ''), info
    assert int(info.get('len', 0)) == SEQ_LEN, info
    x.save(XSQ)
    x.xl('closeSequence', force='true', quiet='true')
    shutil.copy(XSQ, XSQ + '.bak-before-v2-marquee-flip-beat1')

    # re-parse the freshly saved file so the edit works on live state
    tree, found = load()
    flips = flip_points(tree.getroot())
    plan = {api: segments(found[api][2], flips) for api in found}
    for owner, sub, api in TARGETS:
        layer, removals, _, _ = found[api]
        for e in removals:
            layer.remove(e)
    tree.write(XSQ, encoding='UTF-8', xml_declaration=True)

    x.xl('openSequence', seq=XSQ, timeout=300)
    assert int(x.xl('getOpenSequence').get('len', 0)) == SEQ_LEN

    for owner, sub, api in TARGETS:
        pal = found[api][3]
        for s, e, d in plan[api]:
            x.add_effect(api, 0, 'Marquee', fmt(d), pal, s, e)
        print(f'{api}: added {len(plan[api])} segments')

    x.save(XSQ)

    # verify from the saved file: exact tiling + reverse pattern + no fades
    root2 = ET.parse(XSQ).getroot()
    db2 = [t.text or '' for t in root2.find('EffectDB').findall('Effect')]
    elements2 = {el.get('name'): el
                 for el in root2.find('ElementEffects').findall('Element')}
    want_bounds = [C1_START] + flips + [V2_END]
    for owner, sub, api in TARGETS:
        layer = find_layer(elements2[owner], sub)
        segs = sorted(
            (int(e.get('startTime')), int(e.get('endTime')), e)
            for e in layer.findall('Effect')
            if e.get('name') == 'Marquee'
            and int(e.get('startTime')) >= C1_START
            and int(e.get('endTime')) <= V2_END)
        assert len(segs) == len(want_bounds) - 1, f'{api}: {len(segs)} segments'
        rev = ''
        for i, (s, en, e) in enumerate(segs):
            assert (s, en) == (want_bounds[i], want_bounds[i + 1]), (api, s, en)
            d = parse(db2[int(e.get('ref'))])
            rev += d['E_CHECKBOX_Marquee_Reverse']
            assert 'T_TEXTCTRL_Fadeout' not in d, d
            if i == 0:
                assert d.get('T_TEXTCTRL_Fadein') == '2', d
            else:
                assert 'T_TEXTCTRL_Fadein' not in d, d
        assert rev == '01' * 5 + '0', f'{api}: reverse pattern {rev}'
        print(f'{api}: verified {len(segs)} segments, reverse {rev}')
    print(f'saved {XSQ}')


if __name__ == '__main__':
    main()
