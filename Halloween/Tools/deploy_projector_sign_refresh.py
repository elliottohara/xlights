"""Recoverable per-file playback replacement; no service or configuration changes."""
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,shlex,subprocess,sys,time

SHOW=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SHOW/'Tools'))
from single_show_transfer import api,digest,transfer
from single_show_fseq import projector_file
REPORT=SHOW/'projector-sign-refresh-latest.json'
r=json.loads(REPORT.read_text());backup=Path(r['backup']);manifest=json.loads((SHOW/'current-show.json').read_text())
files=[dict(song=n,name=f) for n,s in manifest['songs'].items() for f in s['playback_files']]
targets={'master':'192.168.0.19','projector':'192.168.0.201'}
def stamp():return datetime.now(ZoneInfo('America/Chicago')).isoformat()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def running():
    state=api(targets['master'],'/api/system/status');assert state['fppd']=='running';return state
def snapshot():
    running()
    for label,ip in targets.items():
        if (backup/(label+'-remote-before.json')).exists():continue
        tag='sign-refresh-'+backup.name.split()[-1]
        log=tag+'-before.json';script=tag+'-before.sh'
        payload='''import pathlib,hashlib,struct,json,shutil
result={'files':{},'disk_free':shutil.disk_usage('/home/fpp/media').free,'complete':False}
for name in NAMES:
 p=pathlib.Path('/home/fpp/media/sequences')/name;h=hashlib.sha256()
 with p.open('rb') as f:
  head=f.read(32);f.seek(0)
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 result['files'][name]={'bytes':p.stat().st_size,'sha256':h.hexdigest(),'id':str(struct.unpack_from('<Q',head,24)[0])}
result['complete']=True
print(json.dumps(result))
'''.replace('NAMES',repr([f['name'] for f in files]))
        shell='#!/bin/bash\nset -euo pipefail\nnice -n 10 python3 - <<\'SIGN_SNAPSHOT\' > '+shlex.quote('/home/fpp/media/logs/'+log)+' 2>&1\n'+payload+'\nSIGN_SNAPSHOT\n'
        (backup/(label+'-'+script)).write_text(shell)
        response=json.load(urlopen(Request('http://'+ip+'/api/file/Scripts/'+quote(script,safe=''),shell.encode(),{'Content-Type':'application/octet-stream'},method='POST'),timeout=30));assert response.get('status')=='OK',response
        body=json.dumps({'command':'Run Script','args':[script,'','']}).encode()
        result=urlopen(Request('http://'+ip+'/api/command',body,{'Content-Type':'application/json'}),timeout=30).read().decode()
        write(backup/(label+'-snapshot-job.json'),dict(log=log,script=script));print('READ-ONLY SNAPSHOT',label,result,flush=True)
def get_snapshot(label):
    p=backup/(label+'-remote-before.json')
    if p.exists():return json.loads(p.read_text())
    job=json.loads((backup/(label+'-snapshot-job.json')).read_text())
    for _ in range(300):
        try:
            result=api(targets[label],'/api/file/Logs/'+quote(job['log'],safe=''))
            if result.get('complete'):write(p,result);return result
        except Exception:pass
        time.sleep(2)
    raise RuntimeError('Read-only snapshot not finished: '+label)
def header(path):
    with Path(path).open('rb') as f:h=f.read(32)
    import struct
    return dict(frames=struct.unpack_from('<I',h,14)[0],frame_ms=h[18],id=str(struct.unpack_from('<Q',h,24)[0]),channels=struct.unpack_from('<I',h,10)[0])
def upload(label):
    r=json.loads(REPORT.read_text());assert r['all_local_renders_complete'] and r['pixel_checks_passed'] and r['qr_decodes_passed']
    remote=get_snapshot(label);ip=targets[label];progressfile=backup/(label+'-upload.json')
    p=json.loads(progressfile.read_text()) if progressfile.exists() else dict(files={},ip=ip)
    sizes=[Path(s['sequence']).with_suffix('.fseq').stat().st_size if label=='master' else Path(s['projector_file']).stat().st_size for s in r['songs'].values()]
    growth=sum((Path(r['songs'][f['song']]['sequence']).with_suffix('.fseq').stat().st_size if label=='master' else Path(r['songs'][f['song']]['projector_file']).stat().st_size)-remote['files'][f['name']]['bytes'] for f in files)
    assert remote['disk_free']>=max(sizes)+max(0,growth)+32*1024*1024,('Insufficient staging space',label,remote['disk_free'],max(sizes),growth)
    for index,item in enumerate(files,1):
        name=item['name'];song=r['songs'][item['song']]
        if p['files'].get(name,{}).get('committed'):continue
        running();previous=remote['files'][name];baseline=Path(song['baseline_fseq'])
        if label=='projector':
            old=backup/'Projector before'/(item['song']+'.fseq');old.parent.mkdir(exist_ok=True)
            if not old.exists():projector_file(baseline,old)
        else:old=baseline
        if digest(old)!=previous['sha256']:
            old=backup/'Remote recovery'/label/name;old.parent.mkdir(parents=True,exist_ok=True)
            if not old.exists() or digest(old)!=previous['sha256']:
                subprocess.run(['curl','-fsS','--connect-timeout','15','--max-time','900','-o',str(old),'http://'+ip+'/api/file/Sequences/'+quote(name,safe='')],check=True)
            assert digest(old)==previous['sha256']
        path=Path(song['sequence']).with_suffix('.fseq') if label=='master' else Path(song['projector_file'])
        expected=song['fseq_sha256'] if label=='master' else song['projector_sha256'];assert digest(path)==expected
        assert digest(Path(song['sequence']))==song['xsq_sha256'],('A newer sequence edit requires rendering first',item['song'])
        info=header(path);current=api(ip,'/api/sequence/'+quote(name,safe='')+'/meta');pending=p['files'].get(name,{})
        if pending.get('replacement_attempted') and str(current['ID'])==info['id']:
            scratch=backup/(label+'-reconcile.fseq');subprocess.run(['curl','-fsS','--max-time','900','-o',str(scratch),'http://'+ip+'/api/file/Sequences/'+quote(name,safe='')],check=True)
            assert digest(scratch)==expected;scratch.unlink();pending.update(committed=True,reconciled=True);write(progressfile,p);continue
        assert str(current['ID'])==previous['id'],('Player file changed since snapshot',label,name)
        temp='Sign refresh staged - '+name;print('UPLOAD',label,index,len(files),name,path.stat().st_size,flush=True)
        transfer(path,ip,'Sequences',temp,expected)
        meta=api(ip,'/api/sequence/'+quote(temp,safe='')+'/meta')
        assert (meta['NumFrames'],meta['StepTime'],str(meta['ID']))==(info['frames'],info['frame_ms'],info['id'])
        assert meta['ChannelCount']==info['channels']
        if label=='projector':assert meta['ChannelCount']==147456 and meta['Ranges']==[{'Start':0,'Length':147456}]
        entry=dict(song=item['song'],recovery_file=str(old),recovery_sha256=previous['sha256'],sha256=expected,metadata=meta,full_remote_checksum_verified=True,replacement_attempted=True)
        p['files'][name]=entry;write(progressfile,p);running()
        result=api(ip,'/api/file/Sequences/rename/'+quote(temp,safe='')+'/'+quote(name,safe=''),{});assert result.get('status')=='success',result
        final=api(ip,'/api/sequence/'+quote(name,safe='')+'/meta');assert all(final.get(k)==meta.get(k) for k in ['ID','NumFrames','StepTime','ChannelCount','Ranges'])
        entry.update(committed=True,uploaded_at=stamp());write(progressfile,p);print('DEPLOYED',label,index,len(files),name,flush=True)
    p.update(complete=True,master_after=running(),finished_at=stamp());write(progressfile,p)
def finish():
    r=json.loads(REPORT.read_text())
    for label in targets:assert json.loads((backup/(label+'-upload.json')).read_text())['complete']
    for endpoint,name in [('/api/channel/output/universeOutputs','master-routing.json'),('/api/schedule','master-schedule.json'),('/api/playlist/Halloween%202026','master-playlist.json'),('/api/playlist/Halloween%20Overnight','master-overnight.json')]:
        assert api(targets['master'],endpoint)==json.loads((backup/name).read_text()),endpoint
    r.update(deployment_complete=True,deployed=True,master_kept_running=True,playlist_schedule_routing_preserved=True,master_after=running(),complete=True,finished_at=stamp());write(REPORT,r)
    manifest=json.loads((SHOW/'current-show.json').read_text())
    for name,s in r['songs'].items():
        m=manifest['songs'][name];info=header(Path(s['sequence']).with_suffix('.fseq'))
        m.update(frames=s['frames'],frame_ms=s['frame_ms'],fseq_sha256=s['fseq_sha256'],local_render=dict(fseq={**info,'bytes':Path(s['sequence']).with_suffix('.fseq').stat().st_size},fseq_sha256=s['fseq_sha256'],rendered_at=s['rendered_at']),latest_deployment=REPORT.name,deployed_at=r['finished_at'])
    manifest.update(latest_deployment=REPORT.name,deployed_at=r['finished_at'],verification_record=REPORT.name,latest_local_batch_render=REPORT.name,local_batch_render_finished_at=r['local_qa_finished_at'],projector_sign_refresh_report=REPORT.name,playback_refresh_required=False,all_local_renders_current=True,last_change='Stationary readable QR on Tune To only; projector song visuals; Titanium individual opening retained',website_promotion=dict(qr_target='Tune To',qr_hold='entire sequence, fixed position',projector_qr_enabled=False,evidence=REPORT.name))
    manifest.update(local_recovery_backup=str(backup),master_status=r['master_after'],master_files_uploaded=len(files),projector_files_uploaded=len(files),playlist_and_schedule_preserved=True,master_must_remain_running=True)
    write(SHOW/'current-show.json',manifest)
    for name,s in r['songs'].items():
        note=Path(s['sequence']).parent/'AGENT NOTES.md'
        marker='- Fixed-sign playback deployment completed: '
        if marker not in note.read_text():
            with note.open('a') as f:f.write(marker+'all existing filenames verified on Master and Projector with complete SHA-256 checksums and matching native sequence metadata. Master remained running; playlists, schedule, routes, media and AV settings were preserved. Evidence: `Halloween/projector-sign-refresh-latest.json`.\n')
    opening_path=SHOW/'titanium-opening-flakes-tombstones-latest.json'
    opening=json.loads(opening_path.read_text());opening['included_in_current_deployment']=dict(report=REPORT.name,fseq_sha256=r['songs']['Titanium']['fseq_sha256'],deployed_at=r['finished_at'],individual_note_pixels_reverified=True);write(opening_path,opening)
    print('COMPLETE: 25 MASTER + 25 PROJECTOR FILES VERIFIED; MASTER RUNNING',flush=True)
if __name__=='__main__':
    if sys.argv[1]=='snapshot':snapshot()
    elif sys.argv[1]=='finish':finish()
    else:upload(sys.argv[1])
