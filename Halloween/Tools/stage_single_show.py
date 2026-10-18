"""Stage final native addressing while preserving verified physical wiring."""
from pathlib import Path
import copy, json, re
import xml.etree.ElementTree as ET

SHOW = Path(__file__).resolve().parents[1]
record = json.loads((SHOW / 'single-show-consolidation-latest.json').read_text())
backup = Path(record['backup'])
before = backup / 'Hardware before'
stage = backup / 'Staged deployment'
stage.mkdir(exist_ok=True)
ref = json.loads((backup / 'physical output reference.json').read_text())
controllers = {c['name']: c for c in ref['controllers']}
models = {m.get('name'): m for m in ET.parse(SHOW / 'xlights_rgbeffects.xml').getroot().find('models')}
def read(name): return json.loads((before / name).read_text())
def write(name, value):
    path = stage / name
    path.write_text(json.dumps(value, indent=2))
    return str(path)
plan = {'fpp': {}, 'genius': {}, 'backup': str(backup)}
for name in ['FPP-KULP08-FrontPorch', 'FPP-KULP16-02', 'FPP-KULP32-01', 'FPP-LEFT-YARD', 'FPP-KULP16-01']:
    c = controllers[name]; ip = c['ip']; config = read(ip + '-pixels.json'); config.pop('status', None)
    ports = ref['portmaps'][name]['pixelports']
    native = {m['name']: m for p in ports for m in p['models']}
    old = {s['description']: s for o in config['channelOutputs'] for p in o.get('outputs', []) for s in p.get('virtualStrings', []) if s.get('pixelCount', 0)}
    assigned = set()
    for module in config['channelOutputs']:
        for port in module.get('outputs', []):
            number = port['portNumber'] + 1
            expected = next((p['models'] for p in ports if p['port'] == number), [])
            if ip == '192.168.0.253' and number in (11, 12):
                # Hardware-confirmed four/two tombstone split; layout's bank is contiguous.
                expected = [native[s['description']] for s in port.get('virtualStrings', []) if s.get('pixelCount', 0)]
            new = []
            for m in expected:
                desc = m['name']
                base = re.sub(r'-str-\d+$', '', desc)
                connection = models[base].find('ControllerConnection')
                s = copy.deepcopy(old.get(desc, old.get('Lantana 07')))
                assert s is not None, (ip, desc)
                s.update(description=desc, pixelCount=m['pixels'], startChannel=m['startchannel'] - 1)
                if connection is not None:
                    for source, target in [('Brightness', 'brightness'), ('nullNodes', 'nullNodes'), ('endNullNodes', 'endNulls'), ('reverse', 'reverse')]:
                        if source in connection.attrib: s[target] = int(connection.get(source))
                if desc.startswith('Lantana '): s['nullNodes'] = 0 if desc in ('Lantana 01', 'Lantana 09') else 20
                assert m['pixels'] * 3 == m['channels']
                new.append(s); assert desc not in assigned; assigned.add(desc)
            if new:
                port['protocol'] = 'ws2811'; port['virtualStrings'] = new
            elif port.get('virtualStrings') and any(s.get('pixelCount', 0) for s in port['virtualStrings']):
                raise AssertionError(('Unexpected physical output', ip, number))
        assert assigned == set(native), (ip, assigned ^ set(native))
    plan['fpp'][ip] = write(ip + '-pixels.json', config)
for name in ['GENIUS-PORCH', 'Genius Roof']:
    c = controllers[name]; ip = c['ip']; config = read(ip + '-genius.json')
    for p in ref['portmaps'][name]['pixelports']:
        if not p['models']: continue
        output = config['outputs'][p['port'] - 1]
        assert len(output['virtual_strings']) == len(p['models'])
        for s, m in zip(output['virtual_strings'], p['models']):
            # Names are occasionally truncated by firmware; physical port/order is verified.
            assert s.get('ec') == m['pixels'], (ip, p['port'], s, m)
            s['sc'] = m['startchannel'] - c['startchannel'] + 1
    plan['genius'][ip] = write(ip + '-genius.json', config)
c = controllers['Falcon_F16V4_621D']; strings = read(c['ip'] + '-SP.json')['P']['A']
for p in ref['portmaps'][c['name']]['pixelports']:
    expected = p['models']
    current = [s for s in strings if s['p'] == p['port'] - 1 and s['n'] > 0]
    remaining = list(expected)
    for s in current:
        assert remaining, (p, current)
        first = remaining[0]; covered = 0
        while covered < s['n']:
            m = remaining.pop(0)
            assert m['startchannel'] == first['startchannel'] + covered * 3
            covered += m['pixels']
        assert covered == s['n'], (p, s)
        s['sc'] = first['startchannel'] - 1
    assert not remaining, (p, current)
plan['falcon'] = {'ip': c['ip'], 'strings': write('falcon-strings.json', strings), 'start': c['startchannel'], 'board': read(c['ip'] + '-ST.json')['P']['B'], 'addressing': read(c['ip'] + '-ST.json')['P']['A']}
panels = read('tuneto-panels.json'); panels.pop('status', None)
for output in panels['channelOutputs']:
    if output['type'] == 'LEDPanelMatrix': output['startChannel'] = controllers['FPP-TUNETO']['startchannel']
plan['panels'] = write('tuneto-panels.json', panels)
routing = read('master-routing.json'); routing.pop('status', None)
by_ip = {c['ip']: c for c in controllers.values()}
for module in routing['channelOutputs']:
    for route in module.get('universes', []):
        if route['address'] == '192.168.0.249': continue
        c = by_ip[route['address']]; route['startChannel'] = c['startchannel']; route['channelCount'] = c['channels']
plan['routing'] = write('master-routing.json', routing)
old = json.loads((SHOW / 'Backups/Full render deployment 20261017-163501/progress.json').read_text())
plan['files'] = [{'song': Path(s['xsq']).parent.name, 'destination': s['remote']} for s in old['songs'].values()]
plan['files'].append({'song': 'I Knew It I Knew You', 'destination': 'Halloween 2026 - I Knew It I Knew You.fseq'})
assert len(plan['files']) == len({f['destination'] for f in plan['files']}) == 25
write('plan.json', plan)
print('Staged five FPP controllers, two Genius controllers, roof Falcon, Tune To panels, routing and 25 playback files.')
