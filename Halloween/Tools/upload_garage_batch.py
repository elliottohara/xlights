"""Deploy the verified Halloween batch without stopping any player service.

Each worker stages one file, verifies its complete remote checksum, then
renames it over the existing destination. Master and projector workers keep
separate resumable progress files. Playlists, schedules and outputs are read
only. Projector files contain exactly the rendered projector channels.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote
import argparse,json,struct,time,xml.etree.ElementTree as ET
from single_show_transfer import api as raw_api,digest,transfer
from single_show_fseq import projector_file

SHOW=Path(__file__).resolve().parents[1]
def api(ip, endpoint, body=None):
    # Reads may time out briefly while a controller is busy. Mutations are not
    # blindly retried: the per-file checkpoint handles an unknown outcome.
    for attempt in range(4):
        try: return raw_api(ip, endpoint, body)
        except Exception:
            if body is not None or attempt == 3: raise
            time.sleep(2 * (attempt + 1))

def read(p):return json.loads(Path(p).read_text())
parser=argparse.ArgumentParser();parser.add_argument('target',choices=['master','projector']);args=parser.parse_args()
upload=read(SHOW/'garage-batch-upload-latest.json');backup=Path(upload['backup']);batch=read(upload['batch_render_report']);manifest=read(SHOW/'current-show.json')
assert batch['all_local_renders_complete'] and batch['garage_all_103_pixels_verified']
assert digest(SHOW/'xlights_rgbeffects.xml')==batch['layout_sha256']
assert digest(SHOW/'xlights_networks.xml')==batch['network_sha256']
MASTER='192.168.0.19';ip=MASTER if args.target=='master' else upload['remotes'][0]
progress_path=backup/(args.target+'-upload-progress.json')
progress=read(progress_path) if progress_path.exists() else {'files':{},'media':{},'target':ip}
def save():progress_path.write_text(json.dumps(progress,indent=2)+'\n')
def master_running():
 status=api(MASTER,'/api/system/status');assert status['fppd']=='running',status
 return {k:status.get(k) for k in ['fppd','status_name','current_sequence']}
progress['master_before']=master_running();save()
files=[{'song':n,'destination':d} for n,s in manifest['songs'].items() for d in s['playback_files']]
assert len(files)==25
staging=backup/'Projector sparse';staging.mkdir(exist_ok=True)
for index,item in enumerate(files,1):
 name=item['destination'];song=batch['songs'][item['song']]
 if progress['files'].get(name,{}).get('committed'):continue
 source=Path(song['xsq']).with_suffix('.fseq');assert digest(source)==song['fseq_sha256'],('Render changed',source)
 if args.target=='projector':
  path=staging/name
  print('PREPARE PROJECTOR',index,len(files),name,flush=True)
  pixels=projector_file(source,path);expected=digest(path)
 else:path=source;expected=song['fseq_sha256'];pixels=None
 temp='Garage batch staged - '+name
 print('UPLOAD',args.target.upper(),index,len(files),name,path.stat().st_size,flush=True)
 transfer(path,ip,'Sequences',temp,expected)
 meta=api(ip,'/api/sequence/'+quote(temp,safe='')+'/meta')
 assert meta['NumFrames']==song['fseq']['frames'] and meta['StepTime']==song['fseq']['frame_ms'],meta
 with source.open('rb') as stream:header=stream.read(32)
 assert str(meta['ID'])==str(struct.unpack_from('<Q',header,24)[0]),('Sequence ID mismatch',meta)
 if pixels:
  assert meta['ChannelCount']==147456 and meta['Ranges']==[{'Start':0,'Length':147456}],meta
 master_running()
 entry={'song':item['song'],'bytes':path.stat().st_size,'sha256':expected,'full_remote_checksum_verified':True,'fpp_metadata':meta,'replacement_attempted':True}
 if pixels:entry['rendered_projector_frame_sha256']=pixels[0]
 progress['files'][name]=entry;save()
 result=api(ip,'/api/file/Sequences/rename/'+quote(temp,safe='')+'/'+quote(name,safe=''),{})
 assert result.get('status')=='success',result
 final=api(ip,'/api/sequence/'+quote(name,safe='')+'/meta')
 assert all(final.get(k)==meta.get(k) for k in ['ID','NumFrames','StepTime','ChannelCount','Ranges']),final
 entry.update(committed=True,uploaded_at=datetime.now(ZoneInfo('America/Chicago')).isoformat());save()
 print('VERIFIED',args.target.upper(),index,len(files),name,flush=True)
# Match the existing playback media names, including the new song not in the old manifest.
media={s['fpp_media']:Path(s['media']) for s in read(SHOW/'show-2026-manifest.json')['sequences'] if s.get('media')}
xsq=ET.parse(batch['songs']['I Knew It I Knew You']['xsq']).getroot();new_audio=Path(xsq.findtext('./head/mediaFile'))
if not new_audio.is_absolute():new_audio=SHOW/new_audio
media['Halloween 2026 - I Knew It I Knew You.mp3']=new_audio
for name,path in media.items():
 if progress['media'].get(name,{}).get('verified'):continue
 assert path.exists(),path
 kind='Videos' if path.suffix.lower()=='.mp4' else 'Music';expected=digest(path)
 # transfer verifies already-present files too, avoiding unnecessary writes.
 print('VERIFY MEDIA',args.target.upper(),name,flush=True)
 listing={f['name']:f for f in api(ip,'/api/files/'+kind)['files']}
 if name in listing and int(listing[name]['sizeBytes'])==path.stat().st_size:
  transfer(path,ip,kind,name,expected)
 else:
  temp='Garage batch staged - '+name;transfer(path,ip,kind,temp,expected)
  result=api(ip,'/api/file/'+kind+'/rename/'+quote(temp,safe='')+'/'+quote(name,safe=''),{});assert result.get('status')=='success',result
 progress['media'][name]={'verified':True,'sha256':expected,'bytes':path.stat().st_size,'kind':kind};save()
assert api(MASTER,'/api/schedule')==read(backup/'master-schedule.json')
for playlist in ['Halloween_2026','Halloween_Overnight']:
 assert api(MASTER,'/api/playlist/'+playlist.replace('_','%20'))==read(backup/('master-'+playlist+'.json'))
progress.update(complete=True,master_after=master_running(),finished_at=datetime.now(ZoneInfo('America/Chicago')).isoformat());save()
print('COMPLETE',args.target.upper(),len(progress['files']),'SEQUENCES',len(progress['media']),'MEDIA FILES; MASTER REMAINS RUNNING',flush=True)
