"""Upload verified projector pixels without depending on a running editor."""
from pathlib import Path
from urllib.parse import quote
import json
from single_show_transfer import api, digest, transfer
from single_show_fseq import projector_file, frame_digest

SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'single-show-consolidation-latest.json'
def read(path): return json.loads(Path(path).read_text())
record = read(REPORT); backup = Path(record['backup'])
assert record['all_local_renders_complete']
plan = read(backup / 'Staged deployment/plan.json')
progress_path = backup / 'projector upload progress.json'
progress = read(progress_path) if progress_path.exists() else {'files': {}}
def save(): progress_path.write_text(json.dumps(progress, indent=2))
assert api('192.168.0.19', '/api/system/status').get('status') == 'stopped'
initial = backup / 'Hardware before/projector-files.json'
if not initial.exists(): initial.write_text(json.dumps(api('192.168.0.201', '/api/files/Sequences'), indent=2))
existing = {f['name'] for f in read(initial)['files']}
staging = backup / 'Verified projector sparse'; staging.mkdir(exist_ok=True)
for index, item in enumerate(plan['files'], 1):
    name = item['destination']
    if progress['files'].get(name, {}).get('committed'): continue
    source = Path(record['songs'][item['song']]['xsq']).with_suffix('.fseq')
    local_sparse = staging / name
    print('PREPARE PROJECTOR', index, len(plan['files']), name, flush=True)
    expected = projector_file(source, local_sparse)
    temp_name = 'Shared show verified - ' + name
    print('UPLOAD PROJECTOR', index, len(plan['files']), name, local_sparse.stat().st_size, flush=True)
    transfer(local_sparse, '192.168.0.201', 'Sequences', temp_name, digest(local_sparse))
    metadata = api('192.168.0.201', '/api/sequence/' + quote(temp_name, safe='') + '/meta')
    assert metadata['NumFrames'] == expected[1] and metadata['StepTime'] == expected[2]
    assert metadata['ChannelCount'] == 147456 and metadata['Ranges'] == [{'Start': 0, 'Length': 147456}], metadata
    previous = 'Before single show 20261018 - ' + name
    progress['files'][name] = {'verified_frame_sha256': expected[0], 'frames': expected[1], 'frame_ms': expected[2], 'verified_sparse_copy': str(local_sparse), 'replacement_attempted': True, 'remote_checksum_verified': True, 'fpp_metadata_verified': True}; save()
    listing = {f['name'] for f in api('192.168.0.201', '/api/files/Sequences')['files']}
    if name in existing and previous not in listing:
        result = api('192.168.0.201', '/api/file/Sequences/rename/' + quote(name, safe='') + '/' + quote(previous, safe=''), {})
        assert result.get('status') == 'success', result
    result = api('192.168.0.201', '/api/file/Sequences/rename/' + quote(temp_name, safe='') + '/' + quote(name, safe=''), {})
    assert result.get('status') == 'success', result
    progress['files'][name]['committed'] = True; save()
    print('PROJECTOR ALL FRAMES VERIFIED', index, len(plan['files']), name, flush=True)
progress['complete'] = True; save()
print('ALL PROJECTOR PLAYBACK FILES UPLOADED WITH EVERY FRAME VERIFIED.', flush=True)
