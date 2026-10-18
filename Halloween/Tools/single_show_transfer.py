"""Bounded chunk transfers with complete remote checksums."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
import hashlib,json,subprocess,time


def api(ip, endpoint, body=None):
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request('http://' + ip + endpoint, data, {'Content-Type': 'application/json'} if data else {}), timeout=60) as response: return json.load(response)

def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()

def url(ip, kind, name): return 'http://' + ip + '/api/file/' + kind + '/' + quote(name, safe='')

def transfer(path, ip, kind, name, expected):
    tag = hashlib.sha256((ip + kind + name).encode()).hexdigest()[:12]
    scratch = Path('/private/tmp/single-show-remote-check-' + tag + '.bin')
    chunk_path = Path('/private/tmp/single-show-upload-chunk-' + tag + '.bin')
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
