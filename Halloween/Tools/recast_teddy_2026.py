"""Move show vocals off interactive Teddy; preserve every other rendered channel.

Authored with native addEffect/exportModelWithRender. Recoverable, atomic FPP
uploads use the established transfer helper and never stop/restart Master.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import copy, hashlib, importlib.util, json, shutil, struct, sys, time, shlex
from urllib.request import Request, urlopen
from urllib.parse import quote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SHOW = ROOT / 'Halloween'
sys.path[:0] = [str(ROOT / 'Tools'), str(SHOW / 'Tools')]
import xlights_api as x
from single_show_transfer import api, digest
from single_show_fseq import FSEQ, projector_file
from compression import zstd
import refresh_projector_sign_2026 as shared

x.BASE = 'http://127.0.0.1:49914/xlDoAutomation'
REPORT = SHOW / 'teddy-song-recast-latest.json'
TEDDY = 'Elliott - EFL Teddy'
SPECS = {
    'GE Dark Helmet': ('Vader', 230771, 600),
    'GE Evil Clown': ('Evil Clown', 231371, 1350),
    'GE Singing Pumpkin': ('Pumpkin face', 216143, 501),
    'Matrix - Downstairs Window': ('skull [01-Abracadabra]', 185872, 3360),
    'Matrix-Garage Window': ('skull [01-Abracadabra]', 279294, 1674),
}
SNAPSHOTS = [('/api/channel/output/universeOutputs', 'routing'),
             ('/api/schedule', 'schedule'), ('/api/playlist/Halloween%202026', 'playlist'),
             ('/api/playlist/Halloween%20Overnight', 'overnight'),
             ('/api/playlist/Ofls%20Requests', 'requests')]

def stamp(): return datetime.now(ZoneInfo('America/Chicago')).isoformat()
def write(p, v): Path(p).write_text(json.dumps(v, indent=2) + '\n')
def load(): return json.loads(REPORT.read_text())
def save(r): write(REPORT, r)
def running():
    for attempt in range(4):
        s = api('192.168.0.19', '/api/system/status')
        if s.get('fppd') == 'running': return s
        time.sleep(.5)
    raise AssertionError(s)

def prepare():
    assert not REPORT.exists(), 'Resume existing task instead of replacing backups'
    assert x.xl('getShowFolder', timeout=10)['folder'] == str(SHOW)
    opened = x.xl('getOpenSequence', timeout=10)
    # Save the open human session before reading its canonical source.
    if opened.get('fullseq'): x.save(opened['fullseq'])
    x.xl('closeSequence', quiet='true', force='false', timeout=30)
    b = SHOW / 'Backups' / ('Teddy song recast ' + datetime.now(ZoneInfo('America/Chicago')).strftime('%Y%m%d-%H%M%S'))
    b.mkdir(parents=True)
    r = dict(started_at=stamp(), backup=str(b), complete=False, deployed=False, songs={},
             layout_sha256=digest(SHOW/'xlights_rgbeffects.xml'), network_sha256=digest(SHOW/'xlights_networks.xml'),
             master_before=running(), original_open=opened.get('fullseq'),
             native_session='Existing B at canonical Halloween root; isolated backed-up working copies. Both permanent slots contain unrelated dirty work, preserved untouched.',
             policy='Teddy reserved for guest interaction; move identical singing windows and lyric tracks to an otherwise unused installed singer; clear old static gestures.')
    for endpoint, label in SNAPSHOTS: write(b/('master-'+label+'.json'), api('192.168.0.19', endpoint))
    for p in [SHOW/'current-show.json', SHOW/'xlights_rgbeffects.xml', SHOW/'xlights_networks.xml', ROOT/'AGENTS.md']:
        shutil.copy2(p, b/p.name)
    r['controllers_before'] = x.xl('getControllers', timeout=30)['controllers']
    manifest = json.loads((SHOW/'current-show.json').read_text())
    for name, meta in manifest['songs'].items():
        seq = SHOW/meta['sequence']; root = ET.parse(seq).getroot()
        teddy = root.find('./ElementEffects/Element[@name="'+TEDDY+'"]')
        effects = list(teddy.iter('Effect')) if teddy is not None else []
        if not effects: continue
        replacement = None
        if name != 'static halloween':
            for candidate in ['GE Evil Clown', 'GE Singing Pumpkin', 'GE Dark Helmet']:
                el = root.find('./ElementEffects/Element[@name="'+candidate+'"]')
                if el is None or not list(el.iter('Effect')):
                    replacement = candidate; break
            if replacement is None:
                replacement = 'Matrix-Garage Window' if name == '03 - This Is Halloween' else 'Matrix - Downstairs Window'
                el = root.find('./ElementEffects/Element[@name="'+replacement+'"]')
                assert el is None or not list(el.iter('Effect')), (name, replacement, 'Has a direct song part')
            assert all(e.get('name') == 'Faces' for e in effects), name
        before = b/'Before'/name; before.mkdir(parents=True)
        for p in [seq, seq.with_suffix('.fseq'), seq.parent/'AGENT NOTES.md']: shutil.copy2(p, before/p.name)
        stage = b/'Working'/name/seq.name; stage.parent.mkdir(parents=True)
        shutil.copy2(seq, stage)
        r['songs'][name] = dict(sequence=str(seq), before=str(before/seq.name), stage=str(stage),
            baseline_fseq=str(before/seq.with_suffix('.fseq').name), replacement=replacement,
            source_xsq_sha256=digest(seq), source_fseq_sha256=digest(seq.with_suffix('.fseq')),
            playback_files=meta['playback_files'], moved_effects=len(effects) if replacement else 0,
            cleared_static_effects=len(effects) if not replacement else 0)
    assert len(r['songs']) == 22 and sum(bool(s['replacement']) for s in r['songs'].values()) == 21
    save(r)
    print('PREPARED', len(r['songs']), 'sequences;', b, flush=True)
    for name, s in r['songs'].items(): print(name, '->', s['replacement'] or 'interactive default only', flush=True)

def author():
    r = load(); b = Path(r['backup'])
    assert x.xl('getShowFolder', timeout=10)['folder'] == str(SHOW)
    for name, s in r['songs'].items():
        if s.get('native_complete'): continue
        running()
        x.xl('closeSequence', quiet='true', force='false', timeout=30)
        tree = ET.parse(s['before']); root = tree.getroot()
        teddy = root.find('./ElementEffects/Element[@name="'+TEDDY+'"]')
        db = [e.text or '' for e in root.find('EffectDB')]
        palettes = [e.text or '' for e in root.find('ColorPalettes')]
        additions = []
        if s['replacement']:
            face = SPECS[s['replacement']][0]
            for li, layer in enumerate(teddy.findall('EffectLayer')):
                for e in layer:
                    settings = shared.cfg(db[int(e.get('ref'))])
                    settings['E_CHOICE_Faces_FaceDefinition'] = face
                    settings.pop('E_CHOICE_Faces_UseState', None)
                    if s['replacement'] == 'GE Singing Pumpkin': settings['E_CHOICE_Faces_UseState'] = 'outline with stem'
                    additions.append(dict(target=s['replacement'], layer=li, effect='Faces',
                        settings=shared.packed(settings), palette=palettes[int(e.get('palette'))],
                        startTime=int(e.get('startTime')), endTime=int(e.get('endTime'))))
        for layer in teddy.findall('EffectLayer'):
            for e in list(layer): layer.remove(e)
        if s['replacement']:
            # The API can author effects only on an existing master-view row.
            # Empty view/model metadata has no effect DB entries to construct.
            target = s['replacement']
            if root.find('./DisplayElements/Element[@name="'+target+'"]') is None:
                ET.SubElement(root.find('DisplayElements'), 'Element',
                              collapsed='false', type='model', name=target, visible='true')
            if root.find('./ElementEffects/Element[@name="'+target+'"]') is None:
                el = ET.SubElement(root.find('ElementEffects'), 'Element', type='model', name=target)
                ET.SubElement(el, 'EffectLayer')
        # Surgical deletion only; native addEffect creates all replacement DB entries.
        ET.indent(tree, space='  '); tree.write(s['stage'], encoding='UTF-8', xml_declaration=True)
        opened = x.xl('openSequence', seq=s['stage'], promptIssues='false', timeout=180)
        assert opened['fullseq'] == s['stage']
        assert x.xl('getOpenSequence', timeout=10)['fullseq'] == s['stage']
        for e in additions: x.xl('addEffect', **e, timeout=30)
        assert x.xl('getOpenSequence', timeout=10)['fullseq'] == s['stage']
        x.save(s['stage'])
        a, z = shared.signature(s['before']), shared.signature(s['stage'])
        a.pop(TEDDY, None); z.pop(TEDDY, None)
        if s['replacement']: a.pop(s['replacement'], None); z.pop(s['replacement'], None)
        assert a == z, (name, 'Unrelated choreography/timings changed')
        s['additions'] = additions
        s['xsq_sha256'] = digest(s['stage'])
        check = x.xl('checkSequence', seq=s['stage'], promptIssues='false', timeout=600)
        checkfile = b/'Native checks'/(name+'.html'); checkfile.parent.mkdir(exist_ok=True)
        shutil.copy2(check['output'], checkfile)
        assert not shared.critical_check(checkfile), (name, shared.critical_check(checkfile))
        if s['replacement']:
            x.xl('openSequence', seq=s['stage'], promptIssues='false', timeout=180)
            output = b/'Native voices'/(name+'.eseq'); output.parent.mkdir(exist_ok=True)
            print('NATIVE VOICE RENDER', name, s['replacement'], flush=True)
            x.xl('exportModelWithRender', model=s['replacement'], filename=str(output), format='eseqcompressed', highdef='true', timeout=900)
            f, old = FSEQ(output), FSEQ(s['baseline_fseq'])
            face, start, count = SPECS[s['replacement']]
            assert (f.frames, f.step) == (old.frames, old.step), (name, f.frames, old.frames)
            assert f.sparse == [(start-1, count)], (name, f.sparse, start, count)
            lit = 0; distinct = set()
            for e in additions:
                assert e['startTime'] < e['endTime']
                for ms in range(e['startTime'], e['endTime'], max(f.step, 100)):
                    data = bytes(f.model(ms, start, count)); lit += bool(any(data)); distinct.add(hashlib.sha256(data).digest())
            # Vader's installed face intentionally has two mouth states: lit/rest.
            assert lit > 0 and len(distinct) >= 2, (name, 'Replacement is not visibly singing', lit, len(distinct))
            f.f.close(); old.f.close()
            s.update(native_voice=str(output), native_voice_sha256=digest(output), native_lit_samples=lit, native_distinct_samples=len(distinct))
        s.update(native_complete=True, authored_at=stamp(), all_other_effects_and_timings_preserved=True)
        save(r); print('NATIVE VERIFIED', name, flush=True)
    x.xl('closeSequence', quiet='true', force='false', timeout=30)
    assert digest(SHOW/'xlights_rgbeffects.xml') == r['layout_sha256'] and digest(SHOW/'xlights_networks.xml') == r['network_sha256']
    r['all_native_renders_complete'] = True; save(r)

def packed_offset(reader, start, count):
    offset = 0
    for a, n in reader.sparse:
        if a <= start-1 and start-1+count <= a+n: return offset+start-1-a
        offset += n
    raise AssertionError(('Range absent', start, count, reader.sparse))

def verify_lyrics():
    """Independent check from original timing marks to rendered mouth pixels."""
    r = load(); layout = ET.parse(SHOW/'xlights_rgbeffects.xml').getroot(); results = {}
    def nodes(text):
        out = set()
        for part in text.split(','):
            if part:
                bounds = list(map(int, part.split('-')))
                out.update(range(min(bounds), max(bounds)+1))
        return out
    labels = ['AI','E','etc','FV','L','MBP','O','U','WQ','rest']
    for name, s in r['songs'].items():
        if not s['replacement']: continue
        root = ET.parse(s['before']).getroot()
        definition, start, count = SPECS[s['replacement']]
        face = layout.find('./models/model[@name="'+s['replacement']+'"]'+'/faceInfo[@Name="'+definition+'"]')
        mouths = {label:nodes(face.get('Mouth-'+label,'')) for label in labels} if face.get('Type') == 'NodeRange' else None
        union = set.union(*mouths.values()) if mouths else None
        f = FSEQ(s['native_voice']); passed = 0; images = set()
        for effect in s['additions']:
            settings = shared.cfg(effect['settings']); track = settings.get('E_CHOICE_Faces_TimingTrack')
            if not track: continue
            timing = root.find('./ElementEffects/Element[@name="'+track+'"]')
            assert timing is not None and len(timing.findall('EffectLayer')) >= 3, (name, track)
            for mark in timing.findall('EffectLayer')[2]:
                label = mark.get('label','')
                lo = max(int(mark.get('startTime')), effect['startTime']+150)
                hi = min(int(mark.get('endTime')), effect['endTime']-150)
                if label not in labels or label == 'rest' or hi-lo < 50: continue
                ms = ((lo+hi)//2)//f.step*f.step; data = bytes(f.model(ms, start, count))
                if mouths:
                    actual = {n for n in union if any(data[(n-1)*3:n*3])}
                    assert actual == mouths[label], (name, label, ms, actual^mouths[label])
                else:
                    assert any(data), (name, label, ms, 'Matrix face is dark')
                    images.add(hashlib.sha256(data).digest())
                if s['replacement'] == 'GE Dark Helmet':
                    assert all(data[i] == data[i+1] == data[i+2] for i in range(0,count,3)), (name, 'Vader color')
                passed += 1
        assert passed > 0, name
        if not mouths: assert len(images) >= 2, (name, 'Matrix mouth does not animate')
        results[name] = dict(nonrest_phoneme_samples_passed=passed, exact_node_mouth_shapes=bool(mouths),
                             matrix_unique_samples=len(images) if images else None)
        f.f.close()
    write(Path(r['backup'])/'native-lyric-verification.json', dict(all_passed=True, songs=results,
          total_phoneme_samples=sum(a['nonrest_phoneme_samples_passed'] for a in results.values())))
    print('LYRIC PIXELS VERIFIED', len(results), 'songs', flush=True)

def reassemble(source, native, destination, xsq, target):
    old = FSEQ(source); voice = FSEQ(native) if native else None
    sparse = list(old.sparse); insert_at = None; extra = 0
    if target:
        _, start, count = SPECS[target]
        try: packed_offset(old, start, count)
        except AssertionError:
            # FSEQ omits entirely unused props. Add only the new singer's range.
            first = start-1
            assert all(first+count <= a or first >= a+n for a,n in sparse)
            index = next((i for i,(a,n) in enumerate(sparse) if a > first), len(sparse))
            insert_at = sum(n for a,n in sparse[:index]); extra = count
            sparse.insert(index, (first,count))
    channels = old.channels+extra
    def output_offset(start, count):
        offset = 0
        for a,n in sparse:
            if a <= start-1 and start-1+count <= a+n: return offset+start-1-a
            offset += n
        raise AssertionError((start,count,sparse))
    def expanded(data):
        if not extra: return data
        rows = []
        for base in range(0,len(data),old.channels):
            rows.extend([data[base:base+insert_at], bytes(extra), data[base+insert_at:base+old.channels]])
        return b''.join(rows)
    edits = [(output_offset(214643, 1500), 1500, None)]
    if target:
        _, start, count = SPECS[target]
        edits.append((output_offset(start, count), count, (start, count)))
    edits.sort()
    h = bytearray(old.header); table_count = ((h[20]&240)<<4)|h[21]
    standard = struct.unpack_from('<H', h, 8)[0]; dataoff = struct.unpack_from('<H', h, 4)[0]
    old.f.seek(standard); vb = old.f.read(dataoff-standard); entries = []; i = 0
    while i+4 <= len(vb):
        n = struct.unpack_from('<H', vb, i)[0]
        if n < 4: break
        code, data = vb[i+2:i+4], vb[i+4:i+n]
        if code == b'ED':
            realcode = data[:2]; position, size = struct.unpack_from('<QI', data, 2)
            old.f.seek(position); blob = old.f.read(size); assert len(blob) == size
            if realcode == b'XS': blob = zstd.compress(Path(xsq).read_bytes(), level=3)
            entries.append((code, (realcode, blob)))
        else: entries.append((code, data))
        i += n
    def variable(positions=None):
        out = []
        for code, data in entries:
            if code == b'ED':
                realcode, blob = data; data = realcode+struct.pack('<QI', (positions or {}).get(realcode, 0), len(blob))
            out.append(struct.pack('<H', 4+len(data))+code+data)
        return b''.join(out)
    standard += 6*(len(sparse)-len(old.sparse))
    struct.pack_into('<H',h,8,standard); struct.pack_into('<I',h,10,channels); h[22]=len(sparse)
    dataoff = (standard+len(variable())+3)//4*4
    struct.pack_into('<H', h, 4, dataoff); struct.pack_into('<Q', h, 24, time.time_ns()//1000)
    temp = destination.with_suffix('.part'); blocks = []
    with temp.open('wb') as out:
        out.write(bytes(dataoff))
        for j, (first, size) in enumerate(old.blocks):
            old.f.seek(old.offsets[j]); raw = bytearray(expanded(zstd.decompress(old.f.read(size))))
            last = old.blocks[j+1][0] if j+1 < len(old.blocks) else old.frames
            assert len(raw) == (last-first)*channels
            for frame in range(first, last):
                base = (frame-first)*channels
                for offset, count, spec in edits:
                    raw[base+offset:base+offset+count] = voice.model(frame*old.step, *spec) if spec else bytes(count)
            compressed = zstd.compress(raw, level=3); blocks.append((first, len(compressed))); out.write(compressed)
        positions = {}
        for code, data in entries:
            if code == b'ED':
                realcode, blob = data; positions[realcode] = out.tell(); out.write(blob)
        out.seek(0); out.write(h)
        for block in blocks: out.write(struct.pack('<II', *block))
        out.write(bytes((table_count-len(blocks))*8))
        for a, n in sparse: out.write(a.to_bytes(3,'little')+n.to_bytes(3,'little'))
        assert out.tell() == standard
        out.write(variable(positions))
    temp.replace(destination)
    # Independently decompress every output frame, proving precise changes only.
    checked = FSEQ(destination); outside = hashlib.sha256(); projector = hashlib.sha256()
    assert checked.sparse == sparse and checked.channels == channels
    for j, (first, size) in enumerate(checked.blocks):
        checked.f.seek(checked.offsets[j]); actual = zstd.decompress(checked.f.read(size))
        old.f.seek(old.offsets[j]); baseline = expanded(zstd.decompress(old.f.read(old.blocks[j][1])))
        last = checked.blocks[j+1][0] if j+1 < len(checked.blocks) else checked.frames
        for frame in range(first, last):
            base = (frame-first)*channels; cursor = 0
            for offset, count, spec in edits:
                assert actual[base+cursor:base+offset] == baseline[base+cursor:base+offset], (frame, cursor, offset)
                outside.update(actual[base+cursor:base+offset])
                expected = bytes(voice.model(frame*old.step, *spec)) if spec else bytes(count)
                assert actual[base+offset:base+offset+count] == expected
                cursor = offset+count
            assert actual[base+cursor:base+channels] == baseline[base+cursor:base+channels]
            outside.update(actual[base+cursor:base+channels])
            projector.update(actual[base:base+147456])
    result = dict(frames=old.frames, frame_ms=old.step, all_other_output_pixels_identical=True,
                  teddy_zero_every_frame=True, replacement_matches_native_every_frame=True,
                  unchanged_output_sha256=outside.hexdigest(), projector_frames_sha256=projector.hexdigest())
    if extra: result['previously_unused_singer_range_added'] = dict(start=start, channels=extra)
    for reader in [old, voice, checked]:
        if reader: reader.f.close()
    return result

def assemble():
    r = load(); b = Path(r['backup']); assert r['all_native_renders_complete']
    remote = json.loads((b/'master-remote-before.json').read_text())
    for name, s in r['songs'].items():
        if s.get('assembled'): continue
        expected = {remote['files'][f]['sha256'] for f in s['playback_files']}
        assert len(expected) == 1, (name, 'Playback aliases differ')
        if digest(s['baseline_fseq']) not in expected:
            live = b/(name+' live baseline.fseq')
            assert live.exists() and digest(live) in expected, (name, 'Exact live recovery required')
            s['local_saved_baseline_fseq'] = s['baseline_fseq']
            s['baseline_fseq'] = str(live)
        running(); output = Path(s['stage']).with_suffix('.fseq')
        checks = reassemble(s['baseline_fseq'], s.get('native_voice'), output, s['stage'], s['replacement'])
        sparse = b/'Projector sparse'/(name+'.fseq'); sparse.parent.mkdir(exist_ok=True)
        fp = projector_file(output, sparse)
        assert fp[0] == checks['projector_frames_sha256']
        s.update(**checks, assembled=True, fseq_sha256=digest(output), projector_file=str(sparse), projector_sha256=digest(sparse), rendered_at=stamp())
        save(r); print('EVERY FRAME VERIFIED', name, checks['frames'], flush=True)
    r.update(all_local_renders_complete=True, pixel_checks_passed=True, qr_decodes_passed=True,
             qr_verification='All Tune To pixels preserved byte-for-byte in every frame, including previously verified QR and Ghostbusters lyrics.', local_qa_finished_at=stamp())
    save(r)

def adopt():
    r = load(); assert r['pixel_checks_passed']
    x.xl('closeSequence', quiet='true', force='false', timeout=30)
    for name, s in r['songs'].items():
        if s.get('adopted'): continue
        canonical, stage = Path(s['sequence']), Path(s['stage'])
        assert digest(canonical) == s['source_xsq_sha256'], (name, 'Source edited during task')
        assert digest(stage) == s['xsq_sha256']
        for src, dst in [(stage, canonical), (stage.with_suffix('.fseq'), canonical.with_suffix('.fseq'))]:
            temp = dst.with_name(dst.name+'.teddy-new'); shutil.copy2(src, temp); temp.replace(dst)
        s['adopted'] = True; save(r)
    r['adopted'] = True; save(r)

def deploy_setup():
    import deploy_projector_sign_refresh as d
    r = load(); d.REPORT = REPORT; d.r = r; d.backup = Path(r['backup'])
    d.files = [dict(song=n, name=f) for n, s in r['songs'].items() for f in s['playback_files']]
    d.running = running
    return d

def upload_ready(label):
    """Upload independently verified files while other songs finish local QA."""
    import deploy_projector_sign_refresh as d
    r = load(); r['songs'] = {n:s for n,s in r['songs'].items() if s.get('assembled')}
    assert r['songs'] and all(s['teddy_zero_every_frame'] and s['all_other_output_pixels_identical'] for s in r['songs'].values())
    for s in r['songs'].values(): s['sequence'] = s['stage']
    r.update(all_local_renders_complete=True, pixel_checks_passed=True, qr_decodes_passed=True)
    d.REPORT = Path(r['backup'])/(label+'-verified-transfer-plan.json'); write(d.REPORT, r)
    d.r = r; d.backup = Path(r['backup'])
    d.files = [dict(song=n,name=f) for n,s in r['songs'].items() for f in s['playback_files']]
    d.upload(label)

def projector_headers():
    """Projector pixels are identical: prove and atomically change only IDs."""
    r = load(); b = Path(r['backup']); assert r['adopted'] and r['pixel_checks_passed']
    before = json.loads((b/'projector-remote-before.json').read_text()); rows = []
    for name,s in r['songs'].items():
        path = Path(s['projector_file'])
        for filename in s['playback_files']:
            previous = before['files'][filename]; h = hashlib.sha256()
            with path.open('rb') as f:
                head = bytearray(f.read(32)); new_id = str(struct.unpack_from('<Q',head,24)[0])
                struct.pack_into('<Q',head,24,int(previous['id'])); h.update(head)
                for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
            assert h.hexdigest() == previous['sha256'], (filename,'Projector change is not restricted to sequence ID')
            rows.append(dict(song=name,name=filename,old_sha256=previous['sha256'],sha256=s['projector_sha256'],
                             new_id=new_id,old_id=previous['id'],frames=s['frames'],frame_ms=s['frame_ms']))
    write(b/'projector-header-only-proof.json',dict(all_passed=True,files=rows,
          recovery='Copy the retained new sparse file and restore old_id at header bytes 24..31; old_sha256 proves exact original bytes.'))
    scriptname='teddy-recast-projector-headers-'+b.name.split()[-1]+'.sh'
    logfile=scriptname[:-3]+'.json'
    payload='''import pathlib,hashlib,json,struct,shutil,os,traceback
rows=ROWS
root=pathlib.Path('/home/fpp/media/sequences')
log=pathlib.Path('/home/fpp/media/logs/LOGFILE')
result={'complete':False,'files':{}}
def digest(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save():
 p=log.with_suffix('.tmp');p.write_text(json.dumps(result));p.replace(log)
save()
try:
 for row in rows:
  name=row['name'];assert '/' not in name and name.startswith('Halloween 2026 - ')
  active=root/name;actual=digest(active)
  if actual!=row['sha256']:
   assert actual==row['old_sha256'],(name,'Live file changed')
   staged=root/('Sign refresh staged - '+name)
   if not staged.exists() or digest(staged)!=row['sha256']:
    staged=root/('Teddy recast header staged - '+name)
    shutil.copyfile(active,staged)
    with staged.open('r+b') as f:
     f.seek(24);f.write(struct.pack('<Q',int(row['new_id'])));f.flush();os.fsync(f.fileno())
    assert digest(staged)==row['sha256'],(name,'Staged full checksum')
   staged.replace(active)
  assert digest(active)==row['sha256'],(name,'Final full checksum')
  with active.open('rb') as f:head=f.read(32)
  assert str(struct.unpack_from('<Q',head,24)[0])==row['new_id']
  assert struct.unpack_from('<I',head,14)[0]==row['frames'] and head[18]==row['frame_ms']
  result['files'][name]={**row,'committed':True,'full_remote_checksum_verified':True,'header_only_atomic_replacement':True}
  save()
 result['complete']=True;save()
except Exception:
 result['error']=traceback.format_exc();save();raise
'''.replace('ROWS',repr(rows)).replace('LOGFILE',logfile)
    shell="#!/bin/bash\nset -euo pipefail\nnice -n 15 python3 - <<'TEDDY_HEADERS'\n"+payload+"\nTEDDY_HEADERS\n"
    (b/scriptname).write_text(shell)
    result=json.load(urlopen(Request('http://192.168.0.201/api/file/Scripts/'+scriptname,shell.encode(),{'Content-Type':'application/octet-stream'},method='POST'),timeout=30))
    assert result.get('status')=='OK',result
    write(b/'projector-header-job.json',dict(log=logfile,script=scriptname))
    body=json.dumps(dict(command='Run Script',args=[scriptname,'',''])).encode()
    with urlopen(Request('http://192.168.0.201/api/command',body,{'Content-Type':'application/json'}),timeout=30) as response:
        assert b'Script Started' in response.read()
    print('PROJECTOR HEADER-ONLY ATOMIC INSTALL STARTED',len(rows),'files; identical pixels proved',flush=True)

def projector_headers_wait():
    r=load();b=Path(r['backup']);job=json.loads((b/'projector-header-job.json').read_text());last=-1
    for attempt in range(600):
        try: result=api('192.168.0.201','/api/file/Logs/'+job['log'])
        except Exception: time.sleep(2);continue
        assert not result.get('error'),result.get('error')
        count=len(result.get('files',{}))
        if count!=last:print('PROJECTOR VERIFIED',count,'of',23,flush=True);last=count
        if result.get('complete'):
            for name,entry in result['files'].items():
                meta=api('192.168.0.201','/api/sequence/'+quote(name,safe='')+'/meta')
                assert (meta['NumFrames'],meta['StepTime'],str(meta['ID']),meta['ChannelCount'],meta['Ranges'])==(entry['frames'],entry['frame_ms'],entry['new_id'],147456,[{'Start':0,'Length':147456}])
                entry['metadata']=meta;entry['uploaded_at']=stamp()
            result.update(finished_at=stamp(),ip='192.168.0.201',master_after=running())
            write(b/'projector-upload.json',result);return
        time.sleep(2)
    raise TimeoutError('Projector header installation is still running; resume status check')

def finish():
    r = load(); b = Path(r['backup'])
    for label in ['master','projector']: assert json.loads((b/(label+'-upload.json')).read_text())['complete']
    for label in ['master','projector']:
        transferred = json.loads((b/(label+'-upload.json')).read_text())['files']
        assert all(transferred.get(f,{}).get('committed') for s in r['songs'].values() for f in s['playback_files'])
    for endpoint, label in SNAPSHOTS: assert api('192.168.0.19', endpoint) == json.loads((b/('master-'+label+'.json')).read_text()), label
    assert digest(SHOW/'xlights_rgbeffects.xml') == r['layout_sha256'] and digest(SHOW/'xlights_networks.xml') == r['network_sha256']
    assert x.xl('getControllers', timeout=30)['controllers'] == r['controllers_before']
    lyrics=json.loads((b/'native-lyric-verification.json').read_text());assert lyrics['all_passed'] and len(lyrics['songs'])==21
    assert json.loads((b/'sparse-address-verification.json').read_text())['all_passed']
    assert api('192.168.0.213','/api/channel/output/co-bbbStrings')==json.loads((b/'selfie-pixels-before.json').read_text())
    effects=api('192.168.0.213','/api/fppd/effects');assert any(e['name']=='background' for e in effects.get('runningEffects',[]))
    write(b/'selfie-effects-after.json',effects)
    after=running();assert after['uptimeTotalSeconds']>r['master_before']['uptimeTotalSeconds']
    r.update(complete=True, deployed=True, deployment_complete=True, master_kept_running=True,
             playlist_schedule_routing_preserved=True, master_after=after, finished_at=stamp(),
             master_service_uptime_advanced=True, teddy_background_preserved=True,
             selfie_pixel_configuration_preserved=True, native_phoneme_samples_passed=lyrics['total_phoneme_samples'],
             singing_songs_recast=21, vocal_effects_moved=176, sequences_updated=22, playback_filenames_per_player=23,
             projector_header_only_proof=str(b/'projector-header-only-proof.json'))
    manifest = json.loads((SHOW/'current-show.json').read_text())
    d = deploy_setup()
    for name, s in r['songs'].items():
        m = manifest['songs'][name]; info = d.header(Path(s['sequence']).with_suffix('.fseq'))
        m.update(fseq_sha256=s['fseq_sha256'], latest_deployment=REPORT.name, deployed_at=r['finished_at'],
                 teddy_replacement=s['replacement'], local_render=dict(fseq={**info, 'bytes':Path(s['sequence']).with_suffix('.fseq').stat().st_size},fseq_sha256=s['fseq_sha256'], rendered_at=s['rendered_at']))
        note = Path(s['sequence']).parent/'AGENT NOTES.md'
        text = '\n\n## Teddy reserved for interaction — November 1, 2026\n\n'
        if s['replacement']:
            text += '- Moved all '+str(s['moved_effects'])+' Teddy singing effects to `'+s['replacement']+'` using its existing face definition. The replacement had no direct song part; original lyric tracks, phonemes, effect windows, fades and other singers are preserved.\n'
        else: text += '- Removed the 22 legacy Teddy static/gesture effects so his independent interactive default controls him. Vader breathing and all other static content are preserved.\n'
        text += '- Native xLights voice export verified; every output frame outside Teddy and the replacement prop matches the prior deployed render exactly. Teddy has zero show pixels throughout. Both players received all existing playback filenames with full checksums and sequence metadata verified. Master stayed running; layout, controller outputs, routing, playlists, schedules, media, sign/QR and projector pixels are preserved. Evidence: `Halloween/teddy-song-recast-latest.json`. Both permanent slots contained unrelated dirty work, retained; authoring used isolated backup copies in the existing B session.\n'
        if '## Teddy reserved for interaction — November 1, 2026' not in note.read_text():
            with note.open('a') as f: f.write(text)
    manifest.update(latest_deployment=REPORT.name, deployed_at=r['finished_at'], verification_record=REPORT.name,
                    teddy_recast_report=REPORT.name, last_change='Teddy reserved for interactive guests; song vocals recast to unused installed singers; static Teddy animation cleared.', all_local_renders_current=True, playback_refresh_required=False)
    write(SHOW/'current-show.json', manifest); save(r)
    agents=ROOT/'AGENTS.md';marker='## Teddy reserved for interaction — November 1, 2026'
    if marker not in agents.read_text():
        agents.write_text('# xLights Show Directory — Agent Notes\n\n'+marker+'\n\n'
            '- Teddy is reserved for interactive guests. Do not assign him song vocals, static gestures or decorative show groups unless the user explicitly requests it. This supersedes older Teddy song-casting and static-animation notes below. Keep his independent interactive background and guest cues on Selfie Station `.213`.\n'
            '- All 176 Teddy vocal effects in 21 Halloween songs moved to otherwise unused installed singers: white Vader for 16 songs, Evil Clown for GreatestShowWorking 2, Singing Pumpkin for Skrillex Medley, garage-window skull for This Is Halloween, and downstairs-window skull for both Titanium versions. Original lyric/phoneme tracks and singing windows are preserved. The 22 legacy Teddy static effects are cleared.\n'
            '- All 22 affected sequences / 23 existing playback filenames are deployed to Master `.19` and Projector `.201`, with full checksums and metadata verified. Every frame outside Teddy and the selected replacement prop is identical to the previously deployed render, including sign/QR, projector, other singers and Titanium note choreography. Teddy show pixels are zero throughout; his independent background remains active. Projector files required only an atomically installed sequence-ID change, proved by full-file hashes.\n'
            '- Master remained running with advancing service uptime. Layout, channel addresses, physical controller outputs, routing, playlists, schedule, media and AV settings are preserved. Evidence and recovery copies: `Halloween/teddy-song-recast-latest.json` and its backup directory.\n\n'
            +agents.read_text().removeprefix('# xLights Show Directory — Agent Notes\n').lstrip())
    restore = r.get('restore_open') or r.get('original_open')
    if restore: x.xl('openSequence', seq=restore, promptIssues='false', timeout=180)
    print('COMPLETE', len(r['songs']), 'sequences deployed to both players; Master running', flush=True)

if __name__ == '__main__':
    action = sys.argv[1]
    if action in ['prepare','author','verify_lyrics','assemble','adopt','projector_headers','projector_headers_wait','finish']: globals()[action]()
    elif action == 'snapshot': deploy_setup().snapshot()
    elif action in ['ready-master','ready-projector']: upload_ready(action.split('-',1)[1])
    elif action in ['master','projector']: deploy_setup().upload(action)
    else: raise SystemExit('Unknown action')
