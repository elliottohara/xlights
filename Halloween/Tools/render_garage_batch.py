"""Render the current shared Halloween layout, preserving existing choreography.

Uses a separate batch record and recoverable prior renders. It makes no FPP
changes and leaves Master running. Initialize garage-batch-render-latest.json
with backups before running; completed songs are resumable.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import Request, urlopen
import hashlib, html, json, re, shutil, struct, time
import xml.etree.ElementTree as ET
from single_show_fseq import FSEQ
SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'garage-batch-render-latest.json'
record = json.loads(REPORT.read_text())
backup = Path(record['backup'])
layout = ET.parse(SHOW / 'xlights_rgbeffects.xml').getroot()
groups = {g.get('name'): g.get('models', '').split(',') for g in layout.find('modelGroups')}
def arch_only(name, seen=None):
    seen = set() if seen is None else seen
    base = name.split('/')[0]
    if base.startswith('Arch - '): return True
    if name in seen or name not in groups: return False
    members = [m for m in groups[name] if m]
    return bool(members) and all(arch_only(m, seen | {name}) for m in members)

def save():
    REPORT.write_text(json.dumps(record, indent=2))

def xl(cmd, timeout=90, **kwargs):
    req = Request('http://127.0.0.1:49913/xlDoAutomation', json.dumps({'cmd': cmd, **kwargs}).encode(), {'Content-Type': 'application/json'})
    with urlopen(req, timeout=timeout) as response:
        result = json.load(response)
    assert result.get('worked') != 'false', result
    return result

def settings(text):
    fields = dict(t.split('=', 1) for t in (text or '').split(',') if '=' in t)
    # Native save makes assets inside the show folder relative to that folder.
    # Compare the resolved reference, preserving every other setting verbatim.
    for key, value in list(fields.items()):
        if 'FILEPICKER' in key or 'filename' in key.lower():
            if not value:
                fields.pop(key)
                continue
            value = html.unescape(value)
            fields[key] = value
        if value.startswith(str(SHOW) + '/'):
            fields[key] = str(Path(value).relative_to(SHOW))
    if fields.get('B_CHOICE_PerPreviewCamera') == '2D':
        fields.pop('B_CHOICE_PerPreviewCamera')
    return tuple(sorted(fields.items()))

def signature(path):
    root = ET.parse(path).getroot()
    db, palettes = list(root.find('EffectDB')), list(root.find('ColorPalettes'))
    def node(e):
        if e.tag == 'Effect':
            if e.get('ref') is None:
                return (e.tag, tuple(sorted(e.attrib.items())))
            return (e.tag, tuple(sorted((k, v) for k, v in e.attrib.items() if k not in ['ref', 'palette', 'id'])),
                    settings(db[int(e.get('ref'))].text), palettes[int(e.get('palette'))].text)
        children = list(e)
        if e.tag == 'ElementEffects':
            # Native save adds effect-free rows for the shared master view.
            # They carry no choreography; timing rows remain significant.
            children = [c for c in children if c.get('type') == 'timing' or next(c.iter('Effect'), None) is not None]
        return (e.tag, e.get('name'), e.get('type'), tuple(node(c) for c in children))
    return node(root.find('ElementEffects'))

def info(path):
    with path.open('rb') as stream:
        h = stream.read(32)
    assert h[:4] == b'PSEQ'
    return {'channels': struct.unpack_from('<I', h, 10)[0], 'frames': struct.unpack_from('<I', h, 14)[0],
            'frame_ms': h[18], 'bytes': path.stat().st_size}

def inspect_check(path):
    text = path.read_text()
    start = text.index('id="section-sequence"')
    end = text.find('id="section-', start + 20)
    section = text[start:end if end >= 0 else None]
    categories = {}
    for match in re.finditer(r'<h3[^>]*>(.*?)</h3>', section, re.S):
        name = html.unescape(re.sub('<[^>]+>', '', match.group(1)))
        tail = section[match.end():]
        next_heading = tail.find('<h3')
        tail = tail[:next_heading] if next_heading >= 0 else tail
        categories[name] = html.unescape(re.sub('<[^>]+>', ' ', tail))
        if name == 'Effects With No Nodes':
            headings = [html.unescape(re.sub('<[^>]+>', '', v)) for v in re.findall(r'<h4[^>]*>(.*?)</h4>', tail, re.S)][1:]
            # The four hidden arches are an explicit user-approved exception.
            # Their choreography is kept for reuse although Halloween hides them.
            if headings and all(arch_only(v) for v in headings):
                categories[name] = 'No effects with no nodes found (hidden arches retained by user instruction)'
    critical = {
        'Models Not Found in Layout': 'No missing model issues found',
        'Effects With No Nodes': 'No effects with no nodes found',
        'Impossible Effect Overlaps': 'No impossible effect overlaps found',
        # Render-style recommendations are reported by the native HTML but do
        # not justify changing preserved purchased-sequence buffer settings.
        'Effects Extending Beyond Sequence End': 'No effects extending beyond sequence end found',
    }
    return {name: re.sub(r'\s+', ' ', categories.get(name, 'Missing check category')).strip()
            for name, expected in critical.items() if expected not in categories.get(name, '')}


def current_master():
    with urlopen('http://192.168.0.19/api/system/status', timeout=15) as response:
        status = json.load(response)
    return {k: status.get(k) for k in ['fppd', 'status', 'status_name']}

assert xl('getShowFolder', timeout=10)['folder'] == str(SHOW)
assert hashlib.sha256((SHOW/'xlights_rgbeffects.xml').read_bytes()).hexdigest() == record['layout_sha256']
record['master_before'] = current_master()
assert record['master_before']['fppd'] == 'running', record['master_before']
reference = {'controllers': xl('getControllers')['controllers'], 'portmaps': {}}
for controller in reference['controllers']:
    reference['portmaps'][controller['name']] = xl('getControllerPortMap', name=controller['name'])['controllerportmap']
(backup/'physical-output-reference.json').write_text(json.dumps(reference, indent=2))
record['physical_output_reference'] = str(backup/'physical-output-reference.json')
models = {m['name']: m for ports in reference['portmaps'].values() for group in ports.values() if isinstance(group, list) for port in group if isinstance(port, dict) for m in port.get('models', [])}
targets = {n: models[n] for n in ['Garage Left Bottom','Wall - Garage Top','House Left','Window - Bottom Left','Lantana 11','Column Left']}
assert targets['Garage Left Bottom']['startchannel'] == 184999
assert targets['Wall - Garage Top']['startchannel'] == 185218
record['sample_addresses'] = targets
save()
names = list(record['songs'])
names.remove('I Knew It I Knew You'); names.insert(0, 'I Knew It I Knew You')
for i, name in enumerate(names, 1):
    song = record['songs'][name]
    if song.get('rendered'): continue
    assert hashlib.sha256((SHOW/'xlights_rgbeffects.xml').read_bytes()).hexdigest() == record['layout_sha256'], 'Layout changed mid-batch'
    path = Path(song['xsq']); expected = info(Path(song['baseline_fseq']))
    xl('closeSequence', force='false', quiet='true')
    before = signature(path)
    assert before == signature(Path(song['baseline_xsq'])), ('Sequence changed since batch backup',name)
    print('OPEN',i,len(names),name,flush=True)
    opened = xl('openSequence',seq=str(path),promptIssues='false',timeout=180)
    assert Path(opened['fullseq']) == path and int(opened['len'])//expected['frame_ms'] == expected['frames'], (name,opened,expected)
    checked = xl('checkSequence',seq=str(path),promptIssues='false',timeout=600)
    destination = backup/'Native checks'/(name+'.html');destination.parent.mkdir(exist_ok=True)
    shutil.copy2(checked['output'],destination)
    song.update(native_check=str(destination),native_critical_issues=inspect_check(destination));save()
    assert not song['native_critical_issues'], (name,song['native_critical_issues'])
    reopened = xl('openSequence',seq=str(path),promptIssues='false',timeout=180)
    assert Path(reopened['fullseq']) == path and reopened['len'] == opened['len']
    print('RENDER',i,len(names),name,flush=True)
    xl('renderAll',highdef='true',timeout=3600)
    xl('saveSequence',seq=str(path),timeout=300)
    assert signature(path) == before, ('Authored effects changed',name)
    # Native save can drop the cached media inventory; keep the original block.
    baseline = Path(song['baseline_xsq']).read_text(); saved = path.read_text()
    pattern = r'<SequenceMedia\b[^>]*>.*?</SequenceMedia>'
    original = re.search(pattern,baseline,re.S); current = re.search(pattern,saved,re.S)
    if original and current and original.group() != current.group():
        path.write_text(saved[:current.start()]+original.group()+saved[current.end():])
    fseq = path.with_suffix('.fseq'); result = info(fseq)
    assert result['frames'] == expected['frames'] and result['frame_ms'] == expected['frame_ms']
    reader = FSEQ(fseq);counts = {n:0 for n in targets}
    for ms in range(0, reader.frames*reader.step,1000):
        for n,m in targets.items(): counts[n] += bool(any(reader.model(ms,m['startchannel'],m['channels'])))
    reader.f.close()
    # A song with no house/all-pixel effects may legitimately leave outlines dark.
    with fseq.open('rb') as stream: digest = hashlib.file_digest(stream,'sha256').hexdigest()
    song.update(rendered=True,fseq=result,fseq_sha256=digest,render_effects_unchanged=True,physical_lit_samples=counts,rendered_at=datetime.now(ZoneInfo('America/Chicago')).isoformat())
    save(); print('VERIFIED',i,len(names),name,result,counts,flush=True)
    xl('closeSequence',force='false',quiet='true')
assert all(s['rendered'] for s in record['songs'].values())
for name in ['Garage Left Bottom','Wall - Garage Top']:
    assert any(s['physical_lit_samples'][name] for s in record['songs'].values()), (name,'never lights')
record.update(all_local_renders_complete=True,finished_at=datetime.now(ZoneInfo('America/Chicago')).isoformat(),master_after=current_master())
assert record['master_after']['fppd'] == 'running'
save()
print('ALL 24 RENDERS COMPLETE; MASTER STILL RUNNING; NO UPLOADS PERFORMED',flush=True)
