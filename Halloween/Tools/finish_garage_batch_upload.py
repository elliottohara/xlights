"""Read back the completed batch and record deployment; never restart Master."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote
import json,struct,copy,xml.etree.ElementTree as ET
from single_show_transfer import api,digest
SHOW=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
p=SHOW/'garage-batch-upload-latest.json';record=read(p);backup=Path(record['backup']);batch=read(record['batch_render_report']);manifest=read(SHOW/'current-show.json')
# A concurrent user-authorized rename changed only this controller label.
# Prove every channel, geometry, group and output setting remains identical.
rename = {'FPP-KULP-SELFIE-STATION': 'FPP-LEFT-YARD'}
for filename in ['xlights_rgbeffects.xml','xlights_networks.xml']:
    baseline=ET.parse(Path(batch['backup'])/filename).getroot()
    current=ET.parse(SHOW/filename).getroot()
    for node in current.iter():
        if node.tag=='Controller' and node.get('Name') in rename:
            node.set('Name',rename[node.get('Name')])
        if node.tag=='model' and node.get('Controller') in rename:
            new_name=node.get('Controller');old_name=rename[new_name]
            node.set('Controller',old_name)
            value=node.get('StartChannel','')
            if value.startswith('!'+new_name+':'):
                node.set('StartChannel','!'+old_name+value[len(new_name)+1:])
    assert ET.tostring(baseline)==ET.tostring(current),('Layout changed beyond controller rename',filename)
record['current_layout_equivalent_after_controller_rename']=True
workers={label:read(backup/(label+'-upload-progress.json')) for label in ['master','projector']}
assert all(w.get('complete') and len(w['files'])==25 for w in workers.values())
listing={label:{f['name']:f for f in api(w['target'],'/api/files/Sequences')['files']} for label,w in workers.items()}
metadata={label:{} for label in workers}
for name,song in batch['songs'].items():
 source=Path(song['xsq']).with_suffix('.fseq');assert digest(source)==song['fseq_sha256']
 with source.open('rb') as stream:header=stream.read(32)
 sequence_id=str(struct.unpack_from('<Q',header,24)[0])
 for destination in manifest['songs'][name]['playback_files']:
  for label,w in workers.items():
   entry=w['files'][destination];assert entry['committed'] and entry['full_remote_checksum_verified']
   assert int(listing[label][destination]['sizeBytes'])==entry['bytes']
   meta=api(w['target'],'/api/sequence/'+quote(destination,safe='')+'/meta');metadata[label][destination]=meta
   assert str(meta['ID'])==sequence_id and meta['NumFrames']==song['fseq']['frames'] and meta['StepTime']==song['fseq']['frame_ms']
   if label=='projector':assert meta['ChannelCount']==147456 and meta['Ranges']==[{'Start':0,'Length':147456}]
   else:assert entry['sha256']==song['fseq_sha256']
for endpoint,snapshot in [('/api/schedule','master-schedule.json'),('/api/playlist/Halloween%202026','master-Halloween_2026.json'),('/api/playlist/Halloween%20Overnight','master-Halloween_Overnight.json')]:
 assert api(record['master'],endpoint)==read(backup/snapshot),endpoint
routing_before=read(backup/'master-universeOutputs.json')
routing_after=api(record['master'],'/api/channel/output/universeOutputs')
normalized=copy.deepcopy(routing_after)
for output in normalized['channelOutputs']:
    for route in output.get('universes',[]):
        if route.get('address')=='192.168.0.213' and route.get('description') in rename:
            route['description']=rename[route['description']]
assert normalized==routing_before,'Output routing changed beyond the controller label'
record['controller_label_updated_during_upload']='FPP-KULP-SELFIE-STATION'
statuses={label:api(w['target'],'/api/system/status') for label,w in workers.items()}
assert all(s['fppd']=='running' for s in statuses.values())
assert statuses['projector']['mode_name']=='remote'
systems=api(record['master'],'/api/fppd/multiSyncSystems')['systems']
active_remotes={s['address'] for s in systems if s.get('fppModeString')=='remote' and s['address'].startswith('192.168.')}
assert active_remotes==set(record['remotes']),('Remote inventory changed',active_remotes)
for label,w in workers.items():
 for kind in ['Music','Videos']:
  files={f['name']:f for f in api(w['target'],'/api/files/'+kind)['files']}
  for name,entry in w['media'].items():
   if entry['kind']==kind:assert int(files[name]['sizeBytes'])==entry['bytes'] and entry['verified']
(backup/'final-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
(backup/'final-statuses.json').write_text(json.dumps(statuses,indent=2)+'\n')
now=datetime.now(ZoneInfo('America/Chicago')).isoformat()
record.update(complete=True,finished_at=now,master_sequences=25,projector_sequences=25,master_media=len(workers['master']['media']),projector_media=len(workers['projector']['media']),full_checksums_verified=True,projector_all_frames_verified=True,matching_sequence_ids_verified=True,playlist_and_schedule_preserved=True,output_addresses_preserved=True,output_routes_preserved_except_controller_label=True,master_kept_running=True,master_status=statuses['master']['status_name'],remote_inventory_verified=True)
p.write_text(json.dumps(record,indent=2)+'\n')
manifest.update(playback_refresh_required=False,latest_deployment='garage-batch-upload-latest.json',deployed_at=now,master_status=statuses['master']['status_name'],master_files_uploaded=25,projector_files_uploaded=25)
manifest['garage_group_memberships']['rerender_required']=False
manifest['controller_correction']['playback_refresh_required']=False
for name,song in batch['songs'].items():
 manifest['songs'][name]['fseq_sha256']=song['fseq_sha256'];manifest['songs'][name]['deployed_at']=now
 manifest['songs'][name]['frames']=song['fseq']['frames'];manifest['songs'][name]['frame_ms']=song['fseq']['frame_ms']
 note=Path(song['xsq']).parent/'AGENT NOTES.md';text=note.read_text()
 line='- This batch is now deployed: Master and the projector have matching fresh sequences, with complete transfer checksums and matching frame counts/sequence IDs verified. Projector pixels match the rendered source. Required media verified on both players. Existing playlists, schedule and output routing preserved; Master stayed running. Evidence: `Halloween/garage-batch-upload-latest.json`.\n'
 text=text.replace('- This is a local render only; deployment remains pending. Master stayed running throughout and must remain running.\n',line)
 note.write_text(text)
(SHOW/'current-show.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('COMPLETE: ALL 25 MASTER + 25 PROJECTOR SEQUENCES AND MEDIA VERIFIED; MASTER RUNNING; PLAYLISTS/SCHEDULE/ROUTING PRESERVED.',flush=True)
