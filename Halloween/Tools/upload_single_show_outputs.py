"""Apply staged output addressing with readback, keeping master stopped."""
from pathlib import Path
from urllib.request import Request, urlopen
import copy, json, time
import xml.etree.ElementTree as ET

SHOW = Path(__file__).resolve().parents[1]
record_path = SHOW / 'single-show-consolidation-latest.json'
record = json.loads(record_path.read_text()); backup = Path(record['backup'])
plan = json.loads((backup / 'Staged deployment/plan.json').read_text())
progress_path = backup / 'output upload progress.json'
progress = json.loads(progress_path.read_text()) if progress_path.exists() else {}
def save(): progress_path.write_text(json.dumps(progress, indent=2))
def api(ip, path, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request('http://' + ip + path, data, {'Content-Type': 'application/json'} if data else {}), timeout=timeout) as response:
        return json.load(response)
def clean(v):
    v = copy.deepcopy(v); v.pop('status', None); return v
def read(path): return json.loads(Path(path).read_text())
def config(ip, endpoint, staged, before):
    value = clean(read(staged)); now = clean(api(ip, endpoint))
    assert now in (clean(read(before)), value), ('Changed since backup', ip)
    if now != value:
        progress[ip] = {'attempted': True}; save()
        result = api(ip, endpoint, value)
        assert result.get('status') in ('OK', 'ok', 'success') or ip in plan['genius'], (ip, result)
    assert clean(api(ip, endpoint)) == value, ('Readback differs', ip)
    progress[ip] = {'verified': True}; save(); print('OUTPUT READBACK VERIFIED', ip, flush=True)
def restart(ip):
    api(ip, '/api/system/fppd/restart')
    for _ in range(90):
        try:
            if api(ip, '/api/system/status', timeout=5).get('fppd') == 'running': return
        except Exception: pass
        time.sleep(1)
    raise RuntimeError('Service restart failed: ' + ip)
assert api('192.168.0.19', '/api/system/status').get('status') == 'stopped'
with urlopen('http://192.168.0.249/strings.xml', timeout=20) as response:
    assert ET.tostring(ET.fromstring(response.read())) == ET.tostring(ET.parse(backup / 'Hardware before/falcon-test.xml').getroot())
for ip, staged in plan['fpp'].items():
    config(ip, '/api/channel/output/co-bbbStrings', staged, backup / 'Hardware before' / (ip + '-pixels.json'))
for ip, staged in plan['genius'].items():
    config(ip, '/api/config', staged, backup / 'Hardware before' / (ip + '-genius.json'))
f = plan['falcon']; ip = f['ip']
def falcon(method, mode, params, batch=0, total=0):
    result = api(ip, '/api', {'T': method, 'M': mode, 'B': batch, 'E': total, 'I': batch, 'P': params})
    assert result['R'] == 200, result
    return result
target = read(f['strings'])
current = falcon('Q', 'SP', {})['P']['A']
assert current in (read(backup / 'Hardware before' / (ip + '-SP.json'))['P']['A'], target)
status = falcon('Q', 'ST', {})['P']
assert status['O'] == 2 and status['B'] == f['board'] and status['A'] == f['addressing']
progress[ip] = {'attempted': True}; save()
if status['ps'] != f['start'] - 1:
    result = falcon('S', 'BM', {'B': f['board'], 'O': 2, 'ps': f['start'] - 1})
    if result.get('RB'): time.sleep(15)
for index, string in enumerate(target):
    falcon('S', 'SP', {'AD': f['addressing'], 'B': 255, 'ps': -10, 'A': [string]}, index, len(target))
    time.sleep(.05)
assert falcon('Q', 'SP', {})['P']['A'] == target
assert falcon('Q', 'ST', {})['P']['ps'] == f['start'] - 1
progress[ip] = {'verified': True}; save(); print('ROOF FALCON READBACK VERIFIED', flush=True)
config('192.168.0.245', '/api/channel/output/channelOutputsJSON', plan['panels'], backup / 'Hardware before/tuneto-panels.json')
config('192.168.0.19', '/api/channel/output/universeOutputs', plan['routing'], backup / 'Hardware before/master-routing.json')
for ip in [*plan['fpp'], '192.168.0.245']:
    restart(ip); print('OUTPUT SERVICE RUNNING', ip, flush=True)
assert api('192.168.0.19', '/api/system/status').get('status') == 'stopped'
with urlopen('http://192.168.0.249/strings.xml', timeout=20) as response:
    assert ET.tostring(ET.fromstring(response.read())) == ET.tostring(ET.parse(backup / 'Hardware before/falcon-test.xml').getroot())
progress['complete'] = True; progress['falcon_test_unchanged'] = True; save()
record = read(record_path); record['controller_outputs_uploaded'] = True; record['controller_readbacks_verified'] = True
record_path.write_text(json.dumps(record, indent=2))
print('ALL FINAL OUTPUT ADDRESSES UPLOADED; MASTER STAYS STOPPED UNTIL SEQUENCES MATCH.', flush=True)
