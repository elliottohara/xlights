"""Resumable verified master uploads; keep playback stopped until completion."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from datetime import datetime
import hashlib, json, subprocess, time
import xml.etree.ElementTree as ET
from verify_single_show_saved import verify

SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'single-show-consolidation-latest.json'
def read(path): return json.loads(Path(path).read_text())
record = read(REPORT); backup = Path(record['backup'])
plan = read(backup / 'Staged deployment/plan.json')
progress_path = backup / 'sequence upload progress.json'
progress = read(progress_path) if progress_path.exists() else {'files': {}, 'media': {}}
def save(): progress_path.write_text(json.dumps(progress, indent=2))
def api(ip, endpoint, body=None):
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request('http://' + ip + endpoint, data, {'Content-Type': 'application/json'} if data else {}), timeout=60) as response: return json.load(response)
def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
def url(ip, kind, name): return 'http://' + ip + '/api/file/' + kind + '/' + quote(name, safe='')
def transfer(path, ip, kind, name, expected):
    scratch = Path('/private/tmp/single-show-remote-check.bin')
    chunk_path = Path('/private/tmp/single-show-upload-chunk.bin')
    def check():
        subprocess.run(['curl', '-fsS', '--connect-timeout', '15', '--max-time', '900', '--speed-time', '60', '--speed-limit', '1024', '-o', str(scratch), url(ip, kind, name)], check=True)
        equal = digest(scratch) == expected
        scratch.unlink(missing_ok=True)
        return equal
    listing = {f['name']: f for f in api(ip, '/api/files/' + kind)['files']}
    if listing.get(name, {}).get('sizeBytes') == path.stat().st_size and check(): return
    for attempt in range(4):
        try:
            with path.open('rb') as source:
                offset = 0
                while chunk := source.read(16 * 1024 * 1024):
                    chunk_path.write_bytes(chunk)
                    endpoint = url(ip, kind, name) + ('?sb=' + str(offset) + '&bs=1' if offset else '')
                    result = json.loads(subprocess.check_output(['curl', '-fsS', '--connect-timeout', '15', '--max-time', '300', '--speed-time', '60', '--speed-limit', '1024', '-X', 'POST', '-H', 'Content-Type: application/octet-stream', '--data-binary', '@' + str(chunk_path), endpoint]))
                    assert result.get('status') == 'OK' and int(result.get('written', -1)) == len(chunk) and int(result.get('offset', -1)) == offset, result
                    offset += len(chunk)
            chunk_path.unlink(missing_ok=True)
            assert check(), ('Remote checksum differs', name)
            return
        except Exception as error:
            scratch.unlink(missing_ok=True)
            if attempt == 3: raise
            print('RETRY TRANSFER', name, attempt + 1, str(error), flush=True); time.sleep(3)
assert api('192.168.0.19', '/api/system/status').get('status') == 'stopped'
assert read(backup / 'output upload progress.json')['complete']
# Complete original playback recovery already exists locally; validate it once.
if not progress.get('recovery_verified'):
    old = read(SHOW / 'house-left-porch-port3-latest.json')
    recovery = read(Path(old['backup']) / 'Live playback recovery/progress.json')
    assert len(recovery) == 24
    for item in recovery.values(): assert digest(item['path']) == item['sha256']
    progress['recovery_verified'] = True; save()
for index, item in enumerate(plan['files'], 1):
    name, song_name = item['destination'], item['song']
    if progress['files'].get(name, {}).get('committed'): continue
    while True:
        record = read(REPORT); song = record['songs'][song_name]
        if song.get('rendered'): break
        time.sleep(5)
    verify(song_name, record)
    path = Path(song['xsq']).with_suffix('.fseq'); expected = song['fseq_sha256']
    assert digest(path) == expected
    print('UPLOAD MASTER', index, len(plan['files']), name, flush=True)
    temporary = 'Single show staged - ' + name
    transfer(path, '192.168.0.19', 'Sequences', temporary, expected)
    progress['files'][name] = {'replacement_attempted': True, 'sha256': expected, 'bytes': path.stat().st_size}; save()
    result = api('192.168.0.19', '/api/file/Sequences/rename/' + quote(temporary, safe='') + '/' + quote(name, safe=''), {})
    assert result.get('status') == 'success', result
    progress['files'][name]['committed'] = True; save()
    print('MASTER FILE VERIFIED', index, len(plan['files']), name, flush=True)
media_name = 'Halloween 2026 - I Knew It I Knew You.mp3'
if not progress['media'].get(media_name):
    root = ET.parse(record['songs']['I Knew It I Knew You']['xsq']).getroot()
    media = Path(root.findtext('./head/mediaFile'))
    if not media.is_absolute(): media = SHOW / media
    assert media.exists()
    transfer(media, '192.168.0.19', 'Music', media_name, digest(media))
    progress['media'][media_name] = {'verified': True, 'sha256': digest(media)}; save()
assert api('192.168.0.19', '/api/schedule') == read(backup / 'Hardware before/schedule.json')
assert api('192.168.0.19', '/api/playlist/Halloween%202026') == read(backup / 'Hardware before/playlist.json')
progress['master_complete'] = True; progress['finished_at'] = datetime.now().isoformat(); save()
print('ALL 25 MASTER PLAYBACK FILES AND NEW AUDIO UPLOADED AND VERIFIED.', flush=True)
