"""Upload the preserved 103-pixel garage chain and native address changes."""
from pathlib import Path
from urllib.request import Request, urlopen
import copy, json, time
import xml.etree.ElementTree as ET

SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'garage-left-bottom-port8-latest.json'
record = json.loads(REPORT.read_text()); backup = Path(record['backup'])
ref = json.loads((backup / 'physical-output-reference-after.json').read_text())
controllers = {c['name']: c for c in ref['controllers']}
before_controllers = {c['name']: c for c in json.loads((backup / 'controllers-before.json').read_text())}
hardware = backup / 'Hardware before'; hardware.mkdir(exist_ok=True)
stage = backup / 'Staged hardware'; stage.mkdir(exist_ok=True)
def api(ip, endpoint, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request('http://' + ip + endpoint, data, {'Content-Type': 'application/json'} if data else {}), timeout=timeout) as response: return json.load(response)
def write(path, data): path.write_text(json.dumps(data, indent=2))
def clean(value):
    value = copy.deepcopy(value); value.pop('status', None); return value
def capture(name, ip, endpoint):
    path = hardware / name
    value = api(ip, endpoint)
    if path.exists(): assert clean(json.loads(path.read_text())) == clean(value), ('Changed since snapshot', name)
    else: write(path, value)
    return value
plans = []
for name in ['FPP-KULP08-FrontPorch', 'FPP-KULP16-02', 'FPP-KULP32-01', 'FPP-LEFT-YARD', 'FPP-KULP16-01']:
    c = controllers[name]; ip = c['ip']; old = capture(ip + '-pixels.json', ip, '/api/channel/output/co-bbbStrings'); new = clean(old)
    native = {m['name']: m for p in ref['portmaps'][name]['pixelports'] for m in p['models']}
    for output in new['channelOutputs']:
        for port in output.get('outputs', []):
            for string in port.get('virtualStrings', []):
                if not string.get('pixelCount'): continue
                model = native[string['description']]
                assert model['pixels'] == string['pixelCount']
                string['startChannel'] = model['startchannel'] - 1
    plans.append((ip, '/api/channel/output/co-bbbStrings', new, old)); write(stage / (ip + '-pixels.json'), new)
for name in ['GENIUS-PORCH', 'Genius Roof']:
    c = controllers[name]; ip = c['ip']; old = capture(ip + '-genius.json', ip, '/api/config'); new = copy.deepcopy(old)
    for port in ref['portmaps'][name]['pixelports']:
        if not port['models']: continue
        output = new['outputs'][port['port'] - 1]
        if name == 'GENIUS-PORCH' and port['port'] == 8:
            assert [(m['name'], m['pixels']) for m in port['models']] == [('Garage Left Bottom', 73), ('Wall - Garage Top', 30)]
            output.update(disabled=False, power_enabled=True, virtual_strings=[{'n': m['name'], 'su': 1, 'sc': m['startchannel'] - c['startchannel'] + 1, 'ec': m['pixels'], 'b': 30, 'g': 10, 'st': 'rgb'} for m in port['models']])
        else:
            assert len(output['virtual_strings']) == len(port['models'])
            for string, model in zip(output['virtual_strings'], port['models']):
                assert string.get('ec') == model['pixels']
                string['sc'] = model['startchannel'] - c['startchannel'] + 1
    plans.append((ip, '/api/config', new, old)); write(stage / (ip + '-genius.json'), new)
panels = capture('panels.json', '192.168.0.245', '/api/channel/output/channelOutputsJSON'); new_panels = clean(panels)
for output in new_panels['channelOutputs']:
    if output['type'] == 'LEDPanelMatrix': output['startChannel'] = controllers['FPP-TUNETO']['startchannel']
plans.append(('192.168.0.245', '/api/channel/output/channelOutputsJSON', new_panels, panels))
routing = capture('master-routing.json', '192.168.0.19', '/api/channel/output/universeOutputs'); new_routing = clean(routing); by_ip = {c['ip']: c for c in controllers.values()}
for output in new_routing['channelOutputs']:
    for route in output.get('universes', []):
        if route['address'] == '192.168.0.249': continue
        c = by_ip[route['address']]; route.update(startChannel=c['startchannel'], channelCount=c['channels'])
plans.append(('192.168.0.19', '/api/channel/output/universeOutputs', new_routing, routing))
def falcon(method, mode, params, batch=0, total=0):
    result = api('192.168.0.252', '/api', {'T': method, 'M': mode, 'B': batch, 'E': total, 'I': batch, 'P': params})
    assert result['R'] == 200, result
    return result
old_strings = falcon('Q', 'SP', {})['P']['A']; old_status = falcon('Q', 'ST', {})['P']; write(hardware / 'falcon-strings.json', old_strings); write(hardware / 'falcon-status.json', old_status)
new_strings = copy.deepcopy(old_strings); c = controllers['Falcon_F16V4_621D']; delta = c['startchannel'] - before_controllers[c['name']]['startchannel']
for string in new_strings:
    if string['n']: string['sc'] += delta
with urlopen('http://192.168.0.249/strings.xml', timeout=30) as response: test_before = ET.fromstring(response.read())
ET.ElementTree(test_before).write(hardware / 'falcon-test.xml')
playlist = capture('playlist.json', '192.168.0.19', '/api/playlist/Halloween%202026'); schedule = capture('schedule.json', '192.168.0.19', '/api/schedule')
status = api('192.168.0.19', '/api/system/status')
assert status.get('status_name') in ('idle', 'stopped') or status.get('status') == 'stopped', 'Playback active; retain current playback.'
if status.get('status') != 'stopped': api('192.168.0.19', '/api/system/fppd/stop')
for _ in range(30):
    if api('192.168.0.19', '/api/system/status').get('status') == 'stopped': break
    time.sleep(1)
else: raise RuntimeError('Master did not stop')
for ip, endpoint, new, old in plans:
    if clean(new) != clean(old): api(ip, endpoint, clean(new))
    assert clean(api(ip, endpoint)) == clean(new), ('Readback differs', ip)
    print('CONTROLLER READBACK VERIFIED', ip, flush=True)
result = falcon('S', 'BM', {'B': old_status['B'], 'O': old_status['O'], 'ps': c['startchannel'] - 1})
if result.get('RB'): time.sleep(15)
for index, string in enumerate(new_strings):
    falcon('S', 'SP', {'AD': old_status['A'], 'B': 255, 'ps': -10, 'A': [string]}, index, len(new_strings)); time.sleep(.05)
assert falcon('Q', 'SP', {})['P']['A'] == new_strings
assert falcon('Q', 'ST', {})['P']['ps'] == c['startchannel'] - 1
for ip, endpoint, new, old in plans:
    if ip == '192.168.0.19' or endpoint == '/api/config' or clean(new) == clean(old): continue
    api(ip, '/api/system/fppd/restart')
    for _ in range(90):
        try:
            if api(ip, '/api/system/status', timeout=5).get('fppd') == 'running': break
        except Exception: pass
        time.sleep(1)
    else: raise RuntimeError('Output service restart failed: ' + ip)
    assert clean(api(ip, endpoint)) == clean(new)
with urlopen('http://192.168.0.249/strings.xml', timeout=30) as response: assert ET.tostring(ET.fromstring(response.read())) == ET.tostring(test_before)
assert api('192.168.0.19', '/api/playlist/Halloween%202026') == playlist and api('192.168.0.19', '/api/schedule') == schedule
record.update(complete=True, hardware_readback_verified=True, all_outputs_refreshed=True, playback_refresh_required=True, master_service_stopped_for_layout_testing=True)
write(REPORT, record)
print('COMPLETE: GENIUS PORCH PORT 8 = GARAGE LEFT BOTTOM 73 + WALL - GARAGE TOP 30. 103 PIXELS; CONTROLLER READBACK VERIFIED.', flush=True)
