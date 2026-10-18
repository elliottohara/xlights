"""Restore the verified Selfie Station setup after an OS upgrade.

Master is read-only. Only Selfie Station is configured and rebooted. The
physical pixel driver and incoming DDP are checked separately from network
forwarding, which stays disabled on this receiver.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
import json,copy,time
SHOW=Path('/Users/elliott.ohara/xlights/Halloween');IP='192.168.0.213';MASTER='192.168.0.19'
B=SHOW/'Backups'/('Selfie station post-upgrade setup '+datetime.now(ZoneInfo('America/Chicago')).strftime('%Y%m%d-%H%M%S'));B.mkdir()
def api(ip,path,body=None,method=None):
 assert not(ip==MASTER and (body is not None or method or any(x in path for x in ['/restart','/reboot','/stop'])))
 data=body.encode() if isinstance(body,str) else json.dumps(body).encode() if body is not None else None
 with urlopen(Request('http://'+ip+path,data,{'Content-Type':'text/plain' if isinstance(body,str) else 'application/json'} if data is not None else {},method=method),timeout=25) as r:
  raw=r.read().decode()
  try:return json.loads(raw)
  except json.JSONDecodeError:return raw
def save(n,d):(B/n).write_text(json.dumps(d,indent=2)+'\n')
def clean(d):d=copy.deepcopy(d);d.pop('status',None);return d
before={}
for path,label in [('/api/system/status','status'),('/api/cape','cape'),('/api/channel/output/co-bbbStrings','pixels'),('/api/channel/output/universeInputs','inputs'),('/api/channel/output/universeOutputs','network-outputs'),('/api/channel/output/co-other','other-outputs'),('/api/commandPresets','presets'),('/api/schedule','schedule'),('/api/fppd/effects','effects'),('/api/testmode','test')]:
 before[label]=api(IP,path);save('before-'+label+'.json',before[label])
assert before['cape']['serialNumber']=='D221112092829' and before['cape']['name']=='K8-B'
master_before=api(MASTER,'/api/system/status');save('master-status-before.json',master_before);assert master_before['fppd']=='running'
for path,label in [('/api/channel/output/universeOutputs','routing'),('/api/schedule','schedule'),('/api/playlist/Halloween%202026','playlist')]:save('master-'+label+'-before.json',api(MASTER,path))
keys=['Locale','TimeZone','Latitude','Longitude','WifiRegulatoryDomain','LegalJurisdiction','temperatureInF','DateFormat','TimeFormat','ntpServer','UseNTPFromDHCP','ShareCrashData','FetchVendorLogos','SendVendorSerial','statsPublish','initialSetup-02','HostName','HostDescription','fppMode']
def setting(job):
 ip,k=job;d=api(ip,'/api/settings/'+k);return ip,k,d.get('value') if isinstance(d,dict) else None
state={IP:{},MASTER:{}}
with ThreadPoolExecutor(max_workers=6) as ex:
 for ip,k,v in ex.map(setting,[(ip,k) for ip in state for k in keys]):state[ip][k]=v
save('settings-before.json',state)
common=['Locale','Latitude','Longitude','WifiRegulatoryDomain','DateFormat','TimeFormat','UseNTPFromDHCP','ShareCrashData','FetchVendorLogos','SendVendorSerial','statsPublish']
desired={k:str(state[MASTER][k]) for k in common if state[MASTER][k] is not None}
desired.update(TimeZone='America/Chicago',LegalJurisdiction='US',temperatureInF='1',HostName='FPP-Selfie-Station',HostDescription='Selfie Station',fppMode='player')
if state[MASTER].get('ntpServer') is not None:desired['ntpServer']=str(state[MASTER]['ntpServer'])
changed=[]
for k,v in desired.items():
 if str(state[IP].get(k))!=v:
  api(IP,'/api/settings/'+k+'?skipBackup=1',v,'PUT');changed.append(k)
 actual=api(IP,'/api/settings/'+k).get('value');assert str(actual)==v,(k,actual,v)
print('REGIONAL/INITIAL SETTINGS RESTORED',changed,flush=True)
old=SHOW/'Backups/Left yard Kulp replacement 20261018-162520/replacement-pixels-after.json'
pixels=clean(json.loads(old.read_text()));assert [(s['pixelCount'],s['startChannel'],s['brightness']) for o in pixels['channelOutputs'] for p in o.get('outputs',[]) for s in p.get('virtualStrings',[]) if s.get('pixelCount')]==[(500,214642,20),(167,216142,20)]
api(IP,'/api/command',{'command':'Effects Stop','args':[]})
api(IP,'/api/channel/output/co-bbbStrings',pixels);assert clean(api(IP,'/api/channel/output/co-bbbStrings'))==pixels
inputs={'channelInputs':[{'startChannel':1,'timeout':1000,'universes':[],'channelCount':-1,'enabled':1,'type':'universes'}]}
api(IP,'/api/channel/output/universeInputs',inputs);assert clean(api(IP,'/api/channel/output/universeInputs'))==inputs
api(IP,'/api/settings/initialSetup-02','1','PUT')
save('desired-pixels.json',pixels);save('desired-inputs.json',inputs);save('desired-settings.json',desired)
record={'backup':str(B),'ip':IP,'name':'FPP-KULP-SELFIE-STATION','version':before['status']['version'],'cape_serial_verified':True,'ports':[{'port':1,'model':'Elliott - EFL Teddy','pixels':500,'start_channel':214643,'brightness':20},{'port':2,'model':'GE Singing Pumpkin','pixels':167,'start_channel':216143,'brightness':20}],'master_must_remain_running':True,'settings_changed':changed,'complete':False}
(SHOW/'selfie-station-setup-latest.json').write_text(json.dumps(record,indent=2)+'\n')
print('PORTS AND DDP INPUT RESTORED. REBOOTING ONLY SELFIE STATION TO FINISH THE UPGRADE.',flush=True)
print(api(IP,'/api/system/reboot'),flush=True)

import socket,struct
record=json.loads((SHOW/'selfie-station-setup-latest.json').read_text())
for i in range(100):
 try:
  status=api(IP,'/api/system/status')
  if status.get('fppd')=='running' and status.get('uptime') not in ('00:00','00:01'):break
 except Exception:pass
 time.sleep(2)
else:raise RuntimeError('Selfie Station did not return after reboot')
print('SELFIE STATION RETURNED',{k:status.get(k) for k in ['fppd','host_name','mode_name','uptime','channelInputsEnabled','channelOutputsEnabled','warnings','rebootFlag']},flush=True)
assert clean(api(IP,'/api/channel/output/co-bbbStrings'))==json.loads((B/'desired-pixels.json').read_text())
assert clean(api(IP,'/api/channel/output/universeInputs'))==json.loads((B/'desired-inputs.json').read_text())
for k,v in json.loads((B/'desired-settings.json').read_text()).items():
 assert str(api(IP,'/api/settings/'+k).get('value'))==v,k
assert api(IP,'/api/settings/initialSetup-02').get('value')=='1'
assert not api(IP,'/api/fppd/effects')['runningEffects'],'Unexpected overlay effects after reboot'
print('OUTPUTS ON',api(IP,'/api/command',{'command':'Outputs On','args':[]}),flush=True)
status=api(IP,'/api/system/status');assert status['channelInputsEnabled'],status
# channelOutputsEnabled is HasUniverseOutputs() in this FPP build: it reports
# network forwarding, not physical BBB pixel outputs. Verify the driver log.
with urlopen('http://'+IP+'/api/file/Logs/fppd.log',timeout=20) as response:log=response.read().decode(errors='replace')
last_init=log.split('Loading output plugin: type=BBB48String')[-1]
assert 'Init succeeded, adding to channel outputs' in last_init
for expected in ['214642 - 216141','216142 - 216642']:
 assert 'Determined range needed '+expected in last_init,expected
(B/'pixel-driver-after.log').write_text(last_init)
# Clear only receive counters after the diagnostic probe, then confirm normal
# incoming DDP continues without errors. No light-test pattern is started.
api(IP,'/api/fppd/e131stats',method='DELETE');time.sleep(2)
after_stats=api(IP,'/api/fppd/e131stats');save('live-ddp-after.json',after_stats)
ddp=[u for u in after_stats.get('universes',[]) if u.get('id')=='DDP']
assert ddp and sum(int(u['packetsReceived']) for u in ddp)>0,after_stats
assert sum(int(u['errors']) for u in ddp)==0,after_stats
assert not api(IP,'/api/testmode')['enabled']
assert api(IP,'/api/schedule')==json.loads((B/'before-schedule.json').read_text())
for path,label in [('/api/channel/output/universeOutputs','routing'),('/api/schedule','schedule'),('/api/playlist/Halloween%202026','playlist')]:
 assert api(MASTER,path)==json.loads((B/('master-'+label+'-before.json')).read_text())
master_after=api(MASTER,'/api/system/status');assert master_after['fppd']=='running'
save('status-after.json',status);save('master-status-after.json',master_after)
record.update(complete=True,hostname_verified=True,regional_settings_verified=True,initial_setup_complete=True,pixel_outputs_readback_verified=True,ddp_input_verified=True,channel_inputs_enabled=True,pixel_output_module_enabled=True,pixel_driver_initialized=True,network_forwarding_enabled=False,old_grinch_effects_stopped=True,local_reboot_complete=True,master_kept_running=True,master_configuration_preserved=True,finished_at=datetime.now(ZoneInfo('America/Chicago')).isoformat(),warnings=status.get('warnings',[]))
(SHOW/'selfie-station-setup-latest.json').write_text(json.dumps(record,indent=2)+'\n')
print('COMPLETE: TEDDY 500 ON PORT 1, PUMPKIN 167 ON PORT 2, BOTH 20%; DDP RECEIVED; PIXEL DRIVER INITIALIZED; MASTER REMAINS RUNNING.',flush=True)
