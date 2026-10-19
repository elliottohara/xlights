"""Deploy verified website signage atomically, preserving live playback."""
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from datetime import datetime
from zoneinfo import ZoneInfo
import concurrent.futures,hashlib,json,shlex,struct,subprocess,sys,time
ROOT=Path('/Users/elliott.ohara/xlights');SHOW=ROOT/'Halloween'
sys.path.insert(0,str(SHOW/'Tools'))
from single_show_transfer import api,digest,transfer
from single_show_fseq import projector_file
REPORT=SHOW/'website-promotion-latest.json'
r=json.loads(REPORT.read_text());backup=Path(r['backup']);backup_only='--backup-only' in sys.argv
if '--status' in sys.argv:
 print('MASTER', {k:v for k,v in api('192.168.0.19','/api/system/status').items() if k in ['fppd','status_name','current_sequence']})
 for label in ['master','projector']:
  p=json.loads((backup/(label+'-website-upload.json')).read_text());print(label,'committed',sum(bool(v.get('committed')) for v in p['files'].values()))
  staged=[(f['name'],f.get('sizeBytes')) for f in api(p['ip'],'/api/files/Sequences')['files'] if f['name'].startswith('Website QR staged - ')]
  print(label,'staging',staged[-3:])
  for name,entry in p['files'].items():
   if not entry.get('committed'):
    current=api(p['ip'],'/api/sequence/'+quote(name,safe='')+'/meta')
    print(label,'pending metadata',{k:(entry['metadata'].get(k),current.get(k)) for k in ['ID','NumFrames','StepTime','ChannelCount','Ranges']})
  try:
   req='http://'+p['ip']+'/api/file/Logs/'+quote(p['remote_log'],safe='');data=urlopen(req,timeout=15).read().decode();old=json.loads(data);print(label,'backup_complete',old.get('complete'),'files',len(old.get('files',{})))
  except Exception as e:print(label,'backup status',str(e),locals().get('data','')[:300])
 print('\n'.join(row for row in subprocess.check_output(['ps','-axo','pid,etime,state,command'],text=True).splitlines() if 'curl -fsS' in row and 'single-show' in row))
 sys.exit()
if not backup_only:
 assert r['all_local_renders_complete']
 for name,song in r['songs'].items():
  assert (backup/'Pixel checks'/(name+'.json')).exists(),('Missing pixel verification',name)
  assert digest(Path(song['sequence']).with_suffix('.fseq'))==song['fseq_sha256']
 decoded=subprocess.run(['swift',str(SHOW/'Tools/decode_website_qr.swift'),*[str(backup/'Pixel checks'/(n+' - qr.png')) for n in r['songs']]],capture_output=True,text=True)
 (backup/'rendered-qr-decodes.txt').write_text(decoded.stdout+decoded.stderr)
 assert decoded.returncode==0,decoded.stdout+decoded.stderr
manifest=json.loads((SHOW/'current-show.json').read_text())
files=[dict(song=n,filename=f) for n,s in manifest['songs'].items() for f in s['playback_files']]
def master_running():
 for attempt in range(4):
  status=api('192.168.0.19','/api/system/status')
  if status.get('fppd')=='running':return status
  time.sleep(2)
 raise RuntimeError('Master running state could not be verified: '+repr(status))
tag='website-promotion-'+backup.name.replace('Website promotion ','')
for label,ip in [('master','192.168.0.19'),('projector','192.168.0.201')]:
 progress_path=backup/(label+'-website-upload.json')
 if progress_path.exists():
  progress=json.loads(progress_path.read_text())
  if progress.get('backup_dispatched'):continue
 else:progress=dict(ip=ip,files={},remote_backup='/home/fpp/media/backups/'+tag,remote_log=tag+'-backup.json')
 progress_path.write_text(json.dumps(progress,indent=2))
 payload='''import pathlib,os,json,hashlib,struct
names=NAMES
backup=pathlib.Path(BACKUP);backup.mkdir(parents=True,exist_ok=True)
result={"files":{},"complete":False}
for name in names:
 source=pathlib.Path('/home/fpp/media/sequences')/name
 target=backup/name
 if not target.exists():os.link(source,target)
 with target.open('rb') as f:
  head=f.read(32);f.seek(0);checksum=hashlib.file_digest(f,'sha256').hexdigest()
 result['files'][name]={"bytes":target.stat().st_size,"sha256":checksum,"id":str(struct.unpack_from('<Q',head,24)[0])}
result['complete']=True
print(json.dumps(result))
'''.replace('NAMES',repr([f['filename'] for f in files])).replace('BACKUP',repr(progress['remote_backup']))
 # Python 3.9 on the projector lacks hashlib.file_digest.
 payload=payload.replace("checksum=hashlib.file_digest(f,'sha256').hexdigest()","h=hashlib.sha256();\n  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)\n  checksum=h.hexdigest()")
 shell='#!/bin/bash\nset -euo pipefail\npython3 - <<\'WEBSITE_BACKUP\' > '+shlex.quote('/home/fpp/media/logs/'+progress['remote_log'])+' 2>&1\n'+payload+'\nWEBSITE_BACKUP\n'
 name=tag+'-backup.sh';(backup/(label+'-'+name)).write_text(shell)
 req=Request('http://'+ip+'/api/file/Scripts/'+quote(name,safe=''),shell.encode(),{'Content-Type':'application/octet-stream'},method='POST')
 response=json.load(urlopen(req,timeout=30));assert response.get('status')=='OK',response
 try:
  urlopen('http://'+ip+'/api/file/Logs/'+quote(progress['remote_log'],safe=''),timeout=10).read()
  dispatched='Existing backup log found; retaining the original backup job'
 except Exception:
  request=Request('http://'+ip+'/api/command',json.dumps({'command':'Run Script','args':[name,'','']}).encode(),{'Content-Type':'application/json'},method='POST')
  dispatched=urlopen(request,timeout=30).read().decode()
 print('BACKUP STARTED',label,dispatched,flush=True)
 progress['backup_dispatched']=True;progress_path.write_text(json.dumps(progress,indent=2))

if backup_only:
 print('Backup scripts dispatched; playback files have not been replaced.',flush=True)
 sys.exit()

def worker(label,ip):
 progress_path=backup/(label+'-website-upload.json');p=json.loads(progress_path.read_text())
 def save():progress_path.write_text(json.dumps(p,indent=2)+'\n')
 if not p.get('backup_verified'):
  for attempt in range(180):
   try:
    old=api(ip,'/api/file/Logs/'+quote(p['remote_log'],safe=''))
    if old.get('complete'):break
   except Exception:pass
   time.sleep(3)
  else:raise RuntimeError('Remote backup did not finish: '+label)
  p['backup_verified']=old;save();print('BACKUP VERIFIED',label,len(old['files']),flush=True)
 sparse=backup/'Projector QR sparse';sparse.mkdir(exist_ok=True)
 for index,item in enumerate(files,1):
  name=item['filename'];song=r['songs'][item['song']]
  if p['files'].get(name,{}).get('committed'):continue
  source=Path(song['sequence']).with_suffix('.fseq')
  pending=p['files'].get(name,{})
  if pending.get('replacement_attempted'):
   current=api(ip,'/api/sequence/'+quote(name,safe='')+'/meta')
   if all(current.get(k)==pending['metadata'].get(k) for k in ['ID','NumFrames','StepTime','ChannelCount','Ranges']):
    scratch=backup/(label+'-reconcile.fseq')
    subprocess.run(['curl','-fsS','--connect-timeout','15','--max-time','900','-o',str(scratch),'http://'+ip+'/api/file/Sequences/'+quote(name,safe='')],check=True)
    assert digest(scratch)==pending['sha256'];scratch.unlink()
    pending.update(committed=True,reconciled_after_metadata_timeout=True,uploaded_at=datetime.now(ZoneInfo('America/Chicago')).isoformat());save()
    print('RECONCILED',label,index,len(files),name,flush=True);continue
  master_running()
  canonical=SHOW/Path(song['sequence']).relative_to(Path(r['source_show']))
  assert digest(canonical)==digest(Path(song['baseline_xsq'])),('A newer sequence edit requires merging before deployment',item['song'])
  current=api(ip,'/api/sequence/'+quote(name,safe='')+'/meta')
  prior=p['backup_verified']['files'][name]
  assert str(current['ID'])==prior['id'],('Playback file changed after backup',label,name,current['ID'],prior['id'])
  if label=='projector':
   path=sparse/name;pixels=projector_file(source,path);expected=digest(path)
  else:path=source;pixels=None;expected=song['fseq_sha256']
  temp='Website QR staged - '+name
  print('UPLOAD',label,index,len(files),name,path.stat().st_size,flush=True)
  transfer(path,ip,'Sequences',temp,expected)
  meta=api(ip,'/api/sequence/'+quote(temp,safe='')+'/meta')
  assert (meta['NumFrames'],meta['StepTime'],str(meta['ID']))==(song['fseq']['frames'],song['fseq']['frame_ms'],song['fseq']['id']),meta
  if pixels:assert meta['ChannelCount']==147456 and meta['Ranges']==[{'Start':0,'Length':147456}],meta
  p['files'][name]=dict(song=item['song'],sha256=expected,bytes=path.stat().st_size,full_remote_checksum_verified=True,metadata=meta,projector_frames_sha256=pixels[0] if pixels else None,replacement_attempted=True);save()
  result=api(ip,'/api/file/Sequences/rename/'+quote(temp,safe='')+'/'+quote(name,safe=''),{});assert result.get('status')=='success',result
  for attempt in range(4):
   try:final=api(ip,'/api/sequence/'+quote(name,safe='')+'/meta');break
   except Exception:
    if attempt==3:raise
    time.sleep(3)
  assert all(final.get(k)==meta.get(k) for k in ['ID','NumFrames','StepTime','ChannelCount','Ranges'])
  p['files'][name].update(committed=True,uploaded_at=datetime.now(ZoneInfo('America/Chicago')).isoformat());save()
  print('DEPLOYED',label,index,len(files),name,flush=True)
 p.update(complete=True,master_after=master_running());save()

targets=[('master','192.168.0.19'),('projector','192.168.0.201')]
if '--master-only' in sys.argv:targets=targets[:1]
if '--projector-only' in sys.argv:targets=targets[1:]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 tasks=[pool.submit(worker,label,ip) for label,ip in targets]
 for task in tasks:task.result()
if not all(json.loads((backup/(label+'-website-upload.json')).read_text()).get('complete') for label in ['master','projector']):
 print('Selected target complete; the other upload worker is still running.',flush=True);sys.exit()
for endpoint,name in [('/api/schedule','master-schedule.json'),('/api/playlist/Halloween%202026','master-Halloween_2026.json'),('/api/playlist/Halloween%20Overnight','master-Halloween_Overnight.json'),('/api/channel/output/universeOutputs','master-routing.json')]:
 assert api('192.168.0.19',endpoint)==json.loads((backup/name).read_text()),('Unexpected show metadata change',endpoint)
r.update(deployment_complete=True,master_kept_running=True,playlist_schedule_routing_preserved=True,master_uploads=len(files),projector_uploads=len(files),deployed_at=datetime.now(ZoneInfo('America/Chicago')).isoformat())
REPORT.write_text(json.dumps(r,indent=2)+'\n')
print('COMPLETE: 25 MASTER + 25 PROJECTOR FILES VERIFIED; MASTER RUNNING',flush=True)
