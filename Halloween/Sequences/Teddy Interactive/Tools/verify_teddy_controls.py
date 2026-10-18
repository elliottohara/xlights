"""Live command-path checks for Teddy's GPIO actions, without toggling pins."""
from pathlib import Path
import importlib.util,json,time

TOOL=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('deploy',TOOL/'deploy_teddy_controls.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)

def runtime():return d.request(d.PI,'/api/configfile/teddy-runtime.json')
def trigger(action):return d.cmd(d.PI,'Run Script',['teddy_controls.sh',action,''])
def effects():return d.request(d.TEDDY,'/api/fppd/effects').get('runningEffects',[])

results=[]
for action,arms,label in [('up','up','Arms Up'),('left','up','Look Left Up'),
                         ('right','up','Look Right Up'),('red','up','Surprised Up'),
                         ('down','down','Arms Down'),('red','down','Surprised Down')]:
    before=runtime();sounds=before.get('sound_count',0)
    print('Trigger',action,trigger(action),flush=True)
    deadline=time.monotonic()+8
    seen=None
    while time.monotonic()<deadline:
        state=runtime()
        if state.get('last_request')!=before.get('last_request') and state.get('last_action')==action:
            seen=state;break
        time.sleep(.1)
    assert seen is not None,(action,runtime())
    assert seen['arms']==arms,(action,seen)
    playing=effects()
    assert any(e['name']=='Teddy '+label for e in playing),(action,playing)
    assert len([e for e in playing if e['name'].startswith('Teddy ')])==1,(action,playing)
    time.sleep(2.2)
    after=runtime()
    assert after['arms']==arms and after['status'] in ('show','idle_pose'),(action,after)
    assert after.get('sound_count',0)==sounds+(action=='red'),(action,sounds,after)
    results.append({'action':action,'arms':arms,'effect_verified':'Teddy '+label,
                    'sound_once_verified':action=='red','after':after['status']})
    print('VERIFIED',action,arms,after['status'],'sound count',after['sound_count'],flush=True)

# Verify GPIO configuration and input levels, without claiming physical presses.
gpio=d.request(d.PI,'/api/configfile/gpio.json')
enabled=[t for t in gpio if t.get('enabled')]
assert len(enabled)==5
for t in enabled:
    commands=t.get('rising',[])+t.get('falling',[])
    assert len(commands)==1 and commands[0]['command']=='Run Script'
    assert t['reEnableMode']=='timed'
levels={}
for t in enabled:
    try:levels[t['pin']]=d.request(d.PI,'/api/gpio/'+t['pin'])
    except Exception:levels[t['pin']]={'available':False,'reason':'This FPP GET route exposes only manually set output values; input levels require a physical-button check.'}
master=d.request(d.MASTER,'/api/system/status');assert master['fppd']=='running'
pixels=d.request(d.TEDDY,'/api/channel/output/co-bbbStrings')
before=json.loads((TOOL/'deployment-before.json').read_text())
assert pixels==before['pixels'],'Physical controller configuration changed'
report={'command_path_checks':results,'gpio_readback_verified':True,
        'input_levels':levels,'master_running':True,
        'physical_button_presses_verified':False,'sound_audibility_verified':False,
        'controller_pixel_config_unchanged':True,'runtime':runtime()}
(TOOL/'verification-latest.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
