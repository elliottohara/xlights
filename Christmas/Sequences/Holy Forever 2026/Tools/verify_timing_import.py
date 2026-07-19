"""Verify the imported drum/mood timing tracks match the template exactly."""
import re
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x

XSQ = ('/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Timing Templates/'
       'Holy Forever Drums and Mood.xsq')
TRACKS = ['Song Sections', 'Mood', 'Beat Count', 'Kick', 'Snare', 'Cymbals']

text = open(XSQ).read()


def template_marks(track):
    m = re.search(rf'name="{re.escape(track)}">\s*<EffectLayer>(.*?)'
                  r'</EffectLayer>', text, re.S)
    return [(int(a), int(b), lab) for lab, a, b in
            re.findall(r'label="([^"]*)" startTime="(\d+)" endTime="(\d+)"',
                       m.group(1))]


bad = 0
for track in TRACKS:
    want = template_marks(track)
    ids = x.xl('getEffectIDs', model=track)['effects'][0]
    got = []
    for eid in ids:
        e = x.xl('getEffectSettings', model=track, layer='0', id=str(eid))
        got.append((int(e['startTime']), int(e['endTime']), e['name']))
    got.sort()
    if got == want:
        n_hits = sum(1 for *_, lab in want if lab not in ('',))
        print(f'OK   {track}: {len(got)} marks ({n_hits} labeled)')
    else:
        bad += 1
        print(f'FAIL {track}: live {len(got)} vs template {len(want)}')
        for i, (g, w) in enumerate(zip(got, want)):
            if g != w:
                print(f'  first diff at {i}: live={g} want={w}')
                break

sys.exit(1 if bad else 0)
