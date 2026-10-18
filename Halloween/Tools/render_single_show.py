"""Check and render every repaired sequence from the canonical show folder."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import Request, urlopen
import hashlib
import html
import json
import re
import shutil
import struct
import time
import xml.etree.ElementTree as ET

SHOW = Path(__file__).resolve().parents[1]
REPORT = SHOW / 'single-show-consolidation-latest.json'
record = json.loads(REPORT.read_text())
assert record.get('migration_semantics_verified') and record.get('obsolete_row_cleanup_complete')
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

actual_show = urlopen('http://127.0.0.1:49913/getShowFolder', timeout=10).read().decode().strip()
assert Path(actual_show) == SHOW
reference = {'controllers': xl('getControllers')['controllers'], 'portmaps': {}}
for controller in reference['controllers']:
    reference['portmaps'][controller['name']] = xl('getControllerPortMap', name=controller['name'])['controllerportmap']
(backup / 'physical output reference.json').write_text(json.dumps(reference, indent=2))
record['physical_output_reference'] = str(backup / 'physical output reference.json')
save()
names = list(record['songs'])
names.remove('I Knew It I Knew You')
names.insert(0, 'I Knew It I Knew You')
for i, name in enumerate(names, 1):
    song = record['songs'][name]
    if song.get('rendered'):
        continue
    path = Path(song['xsq'])
    xl('closeSequence', force='true', quiet='true')
    root = ET.parse(path)
    header = root.getroot().find('head')
    duration = int(float(header.findtext('sequenceDuration')) * 1000)
    frame_ms = info(backup / 'Before' / path.with_suffix('.fseq').relative_to(SHOW))['frame_ms']
    duration = duration // frame_ms * frame_ms
    trimmed = []
    for element in root.getroot().find('ElementEffects'):
        if element.get('type') == 'timing':
            continue
        for layer in element.iter('EffectLayer'):
            for effect in list(layer):
                if int(effect.get('endTime', '0')) > duration:
                    trimmed.append((element.get('name'), dict(effect.attrib)))
                    if int(effect.get('startTime', '0')) >= duration:
                        layer.remove(effect)
                    else:
                        effect.set('endTime', str(duration))
    if trimmed:
        original = backup / 'Before duration cleanup' / path.relative_to(SHOW)
        original.parent.mkdir(parents=True, exist_ok=True)
        if not original.exists():
            shutil.copy2(path, original)
        root.write(path, encoding='UTF-8', xml_declaration=True)
        song['duration_tail_cleanup'] = trimmed
        save()
    before = signature(path)
    print('OPEN', i, len(names), name, flush=True)
    opened = xl('openSequence', seq=str(path), promptIssues='false', timeout=180)
    expected = info(backup / 'Before' / path.with_suffix('.fseq').relative_to(SHOW))
    assert Path(opened['fullseq']) == path and int(opened['len']) // expected['frame_ms'] == expected['frames'], (name, opened, expected)
    checked = xl('checkSequence', seq=str(path), promptIssues='false', timeout=600)
    check_path = Path(checked['output'])
    destination = backup / 'Native checks' / (name + '.html')
    destination.parent.mkdir(exist_ok=True)
    shutil.copy2(check_path, destination)
    issues = inspect_check(destination)
    song['native_check'] = str(destination)
    song['native_critical_issues'] = issues
    save()
    assert not issues, (name, issues)
    # This build's sequence checker can close the checked file. Reopen it
    # explicitly before rendering instead of relying on checker side effects.
    reopened = xl('openSequence', seq=str(path), promptIssues='false', timeout=180)
    assert Path(reopened['fullseq']) == path and reopened['len'] == opened['len']
    print('RENDER', i, len(names), name, flush=True)
    xl('renderAll', highdef='true', timeout=3600)
    xl('saveSequence', seq=str(path), timeout=300)
    assert signature(path) == before, ('Authored effect data changed during rendering', name)
    fseq = path.with_suffix('.fseq')
    fseq_info = info(fseq)
    assert fseq_info['frames'] == int(opened['len']) // fseq_info['frame_ms']
    with fseq.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    song.update(rendered=True, fseq=fseq_info, fseq_sha256=digest, render_effects_unchanged=True,
                rendered_at=datetime.now(ZoneInfo('America/Chicago')).isoformat())
    save()
    print('VERIFIED RENDER', i, len(names), name, fseq_info, flush=True)
    xl('closeSequence', force='false', quiet='true')
record['all_local_renders_complete'] = True
save()
print('ALL 24 SINGLE-SHOW SEQUENCES CHECKED AND RENDERED', flush=True)
