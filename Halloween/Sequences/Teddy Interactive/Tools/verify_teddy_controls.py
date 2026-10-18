"""Verify all five routines through the real FPP script command path."""
from pathlib import Path
import importlib.util,json,time
TOOL=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('deploy',TOOL/'deploy_teddy_controls.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def runtime():return d.request(d.PI,'/api/configfile/teddy-runtime.json')
def effects():return d.request(d.TEDDY,'/api/fppd/effects').get('runningEffects',[])
results=[]
for action in ['white','green','blue','yellow','red']:
 before=runtime();sounds=before.get('sound_count',0);name='Teddy '+action.title()+' Routine'
 d.cmd(d.PI,'Run Script',['teddy_controls.sh',action,''])
 deadline=time.monotonic()+8
 while time.monotonic()<deadline:
  state=runtime()
  if state.get('last_request')!=before.get('last_request') and state.get('last_action')==action:break
  time.sleep(.1)
 else:raise AssertionError((action,runtime()))
 start=time.monotonic()
 assert state['effect']==name and state['status']=='gesture',(action,state)
 assert any(e['name']==name for e in effects()),(action,effects())
 time.sleep(max(0,4.35-(time.monotonic()-start)))
 assert runtime()['effect']==name and any(e['name']==name for e in effects()),(action,'did not last five seconds')
 time.sleep(1.05)
 after=runtime()
 assert after['status'] in ('show','idle_pose') and after['effect']!=name,(action,'did not finish',after)
 assert after['sound_count']==sounds+(action=='red'),(action,'unexpected sound count',after)
 results.append({'button':action,'effect':name,'observed_at_start_and_after_4_seconds':True,'finished_after_5_seconds':True,'sound_once':action=='red'})
 print('VERIFIED',action,flush=True)
gpio=d.request(d.PI,'/api/configfile/gpio.json');enabled=[v for v in gpio if v.get('enabled')]
assert len(enabled)==5
for v in enabled:
 assert len(v['rising'])==1 and not v['falling'] and v['reEnableMode']=='timed' and v['reEnableDelay']==5100
 assert v['rising'][0]['args'][1] in ['white','green','blue','yellow','red']
master=d.request(d.MASTER,'/api/system/status');assert master['fppd']=='running'
pixels=d.request(d.TEDDY,'/api/channel/output/co-bbbStrings')
before=json.loads((TOOL/'deployment-before.json').read_text());assert pixels==before['pixels']
audio=d.request(d.PI,'/api/settings/AudioOutput');assert audio['value']=='S3'
report={'command_path_checks':results,'gpio_readback_verified':True,'master_running':True,
 'physical_button_presses_verified':False,'white_physical_input_unconfirmed':True,
 'audio_output':'Sound Blaster Play! 3','sound_audibility_verified':False,
 'controller_pixel_config_unchanged':True,'runtime':runtime()}
(TOOL/'verification-latest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
