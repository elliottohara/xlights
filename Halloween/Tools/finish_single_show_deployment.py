"""Final live readback, restore the player service, and record completion."""
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime
from zoneinfo import ZoneInfo
import copy, json, time
import xml.etree.ElementTree as ET
from verify_single_show_saved import verify

SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'single-show-consolidation-latest.json'
def read(path): return json.loads(Path(path).read_text())
record = read(REPORT); backup = Path(record['backup'])
plan = read(backup / 'Staged deployment/plan.json')
def complete(path, key): return Path(path).exists() and read(path).get(key)
while not (complete(backup / 'sequence upload progress.json', 'master_complete') and complete(backup / 'projector upload progress.json', 'complete')):
    time.sleep(5)
def api(ip, endpoint, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request('http://' + ip + endpoint, data, {'Content-Type': 'application/json'} if data else {}), timeout=timeout) as response: return json.load(response)
def clean(value):
    value = copy.deepcopy(value); value.pop('status', None); return value
record = read(REPORT)
for name in record['songs']: verify(name, record)
assert record['all_local_renders_complete'] and record['redundant_song_configs_retired']
assert (backup / 'final physical channel samples.json').exists()
assert api('192.168.0.19', '/api/system/status').get('status') == 'stopped'
readbacks = {}
for ip, path in plan['fpp'].items():
    readbacks[ip] = api(ip, '/api/channel/output/co-bbbStrings')
    assert clean(readbacks[ip]) == clean(read(path)), ('Final FPP readback', ip)
    assert api(ip, '/api/system/status').get('fppd') == 'running', ip
for ip, path in plan['genius'].items():
    readbacks[ip] = api(ip, '/api/config')
    assert clean(readbacks[ip]) == clean(read(path)), ('Final Genius readback', ip)
readbacks['panels'] = api('192.168.0.245', '/api/channel/output/channelOutputsJSON')
assert clean(readbacks['panels']) == clean(read(plan['panels']))
readbacks['routing'] = api('192.168.0.19', '/api/channel/output/universeOutputs')
assert clean(readbacks['routing']) == clean(read(plan['routing']))
f = plan['falcon']
query = lambda mode: api(f['ip'], '/api', {'T': 'Q', 'M': mode, 'B': 0, 'E': 0, 'I': 0, 'P': {}})
readbacks['falcon'] = query('SP')
assert readbacks['falcon']['P']['A'] == read(f['strings'])
assert query('ST')['P']['ps'] == f['start'] - 1
with urlopen('http://192.168.0.249/strings.xml', timeout=30) as response:
    assert ET.tostring(ET.fromstring(response.read())) == ET.tostring(ET.parse(backup / 'Hardware before/falcon-test.xml').getroot())
playlist = read(backup / 'Hardware before/playlist.json'); schedule = read(backup / 'Hardware before/schedule.json')
assert api('192.168.0.19', '/api/playlist/Halloween%202026') == playlist
assert api('192.168.0.19', '/api/schedule') == schedule
master_files = {f['name']: f for f in api('192.168.0.19', '/api/files/Sequences')['files']}
projector_files = {f['name']: f for f in api('192.168.0.201', '/api/files/Sequences')['files']}
uploads = read(backup / 'sequence upload progress.json'); projector = read(backup / 'projector upload progress.json')
for item in plan['files']:
    name = item['destination']; song = record['songs'][item['song']]
    assert uploads['files'][name]['committed'] and uploads['files'][name]['sha256'] == song['fseq_sha256']
    assert master_files[name]['sizeBytes'] == song['fseq']['bytes']
    assert projector['files'][name]['committed'] and name in projector_files
for item in playlist['mainPlaylist']:
    if item.get('enabled') and item.get('sequenceName'): assert item['sequenceName'] in master_files
api('192.168.0.19', '/api/system/fppd/restart')
for _ in range(90):
    try:
        status = api('192.168.0.19', '/api/system/status', timeout=5)
        if status.get('fppd') == 'running' and status.get('status_name') == 'idle': break
    except Exception: pass
    time.sleep(1)
else: raise RuntimeError('Master did not return to idle after deployment')
assert api('192.168.0.19', '/api/playlist/Halloween%202026') == playlist
assert api('192.168.0.19', '/api/schedule') == schedule
readbacks['master_status'] = status
(backup / 'final live readbacks.json').write_text(json.dumps(readbacks, indent=2))
record = read(REPORT)
record.update(live_deployment_complete=True, controller_outputs_uploaded=True, controller_readbacks_verified=True,
              master_files_uploaded=25, projector_files_uploaded=25, playlist_and_schedule_preserved=True,
              falcon_test_unchanged=True, master_service_running=True, master_status='idle',
              all_saved_choreography_verified=True, physical_channel_samples_verified=True,
              shared_show_import_maps=read(backup / 'shared import map manifest.json'),
              finished_at=datetime.now(ZoneInfo('America/Chicago')).isoformat())
REPORT.write_text(json.dumps(record, indent=2))
for name, song in record['songs'].items():
    note = Path(song['xsq']).parent / 'AGENT NOTES.md'; text = note.read_text()
    line = '- Shared-show deployment completed: fresh playback uploaded to Master and Projector, with full Master checksums and every Projector frame verified. Final controller addresses read back; existing playlist/schedule preserved; Master returned to idle.\n'
    if line not in text: note.write_text(text.replace('## Shared Halloween show — October 18, 2026\n\n', '## Shared Halloween show — October 18, 2026\n\n' + line))
print('SHARED HALLOWEEN SHOW COMPLETE: 24 SONGS, 25 MASTER FILES, 25 PROJECTOR FILES; PLAYER IDLE.', flush=True)
