"""Retire every Teddy control on the old button Pi; leave FPP/Master running."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
import copy,json,time

ROOT=Path(__file__).resolve().parents[4]
SONG=ROOT/'Halloween/Sequences/Teddy Interactive'
BACKUP=ROOT/'Halloween/Backups/Teddy button controller retirement 20261101'
OLD='192.168.0.133';LIGHTS='192.168.0.213';MASTER='192.168.0.19'

def api(host,path,value=None):
    assert host!=MASTER or value is None
    data=value if isinstance(value,bytes) else json.dumps(value).encode() if value is not None else None
    req=Request('http://'+host+path,data,{'Content-Type':'application/octet-stream' if isinstance(value,bytes) else 'application/json'} if data is not None else {})
    with urlopen(req,timeout=10) as r:raw=r.read()
    try:return json.loads(raw)
    except (ValueError,UnicodeDecodeError):return raw

def command(host,name,args):return api(host,'/api/command',{'command':name,'args':args})

def upload_script(name,data):
    api(OLD,'/api/file/Scripts/'+quote(name,safe=''),data)
    assert api(OLD,'/api/file/Scripts/'+quote(name,safe=''))==data

def teddy_action(row):
    return isinstance(row,dict) and row.get('command')=='Run Script' and bool(row.get('args')) and row['args'][0] in ['teddy_controls.sh','teddy_control.py']

def main():
    BACKUP.mkdir(parents=True,exist_ok=True)
    before={'gpio':api(OLD,'/api/configfile/gpio.json'),
            'presets':api(OLD,'/api/configfile/commandPresets.json'),
            'worker':api(OLD,'/api/configfile/teddy-runtime.json'),
            'master':api(MASTER,'/api/system/status'),
            'pixel_outputs':api(LIGHTS,'/api/channel/output/co-bbbStrings')}
    assert before['master']['fppd']=='running'
    if not (BACKUP/'before.json').exists():(BACKUP/'before.json').write_text(json.dumps(before,indent=2)+'\n')
    for name in ['teddy_control.py','teddy_controls.sh']:
        dest=BACKUP/name
        if not dest.exists():
            raw=api(OLD,'/api/file/Scripts/'+quote(name,safe=''))
            dest.write_bytes(raw if isinstance(raw,bytes) else raw.encode())
    # Stop its already-loaded worker first, then make all stale trigger paths
    # inert immediately; cached GPIO actions cannot bring it back.
    command(OLD,'Run Script',['teddy_controls.sh','pause',''])
    time.sleep(.5)
    flag={'disabled':True,'reason':'Retired at user request; Teddy is controlled by the new Pi.',
          'new_controller':'192.168.0.30'}
    api(OLD,'/api/configfile/teddy-controls-disabled.json',flag)
    upload_script('teddy_control.py',(SONG/'Tools/teddy_control.py').read_bytes())
    wrapper=b'#!/bin/sh\n# Retired: this controller must not control Teddy.\nexit 0\n'
    upload_script('teddy_controls.sh',wrapper)
    gpio=copy.deepcopy(before['gpio']);disabled=[]
    for row in gpio:
        changed=False
        for edge in ['rising','falling','hold']:
            prior=row.get(edge,[])
            if not isinstance(prior,list):continue
            after=[a for a in prior if not teddy_action(a)]
            if after!=prior:row[edge]=after;changed=True
        if changed:
            if not any(row.get(edge) for edge in ['rising','falling','hold']):row['enabled']=False
            row['desc']='Retired Teddy button; new controller 192.168.0.30'
            disabled.append(row['pin'])
    presets=copy.deepcopy(before['presets'])
    presets['commands']=[c for c in presets.get('commands',[]) if not teddy_action(c)]
    api(OLD,'/api/configfile/gpio.json',gpio)
    api(OLD,'/api/configfile/commandPresets.json',presets)
    assert api(OLD,'/api/configfile/gpio.json')==gpio
    assert api(OLD,'/api/configfile/commandPresets.json')==presets
    # Retire the old dedicated Teddy speech bridge as well. Its configuration
    # is checked on-device without printing or copying any credentials.
    script=b'''#!/usr/bin/python3
from pathlib import Path
import json,shlex,subprocess,os
meta={}
p=Path('/etc/ofls-speech-bridge.env')
if p.exists():
 for line in p.read_text().splitlines():
  if '=' in line:
   k,v=line.split('=',1)
   if k in ['BRIDGE_ROLE','SPEECH_MODEL','FPP_BASE_URL']:
    parts=shlex.split(v);meta[k]=parts[0] if parts else ''
assert meta.get('BRIDGE_ROLE')=='speech' and meta.get('SPEECH_MODEL')=='Elliott - EFL Teddy' and meta.get('FPP_BASE_URL','').rstrip('/')=='http://192.168.0.213', 'Unexpected speech bridge target'
subprocess.run(['systemctl','disable','--now','ofls-speech-bridge.service'],check=True,capture_output=True)
state_path=Path('/home/fpp/media/config/teddy-runtime.json')
state=json.loads(state_path.read_text())
pid=state.get('pid',0)
worker_alive=bool(pid and Path('/proc/'+str(pid)+'/cmdline').exists() and b'teddy_control.py' in Path('/proc/'+str(pid)+'/cmdline').read_bytes())
assert not worker_alive,'Legacy worker is still running'
state.update(status='retired',effect=None,pid=None)
state_path.write_text(json.dumps(state,indent=2)+'\\n')
result={'worker_running':worker_alive}
for action in ['is-active','is-enabled']:
 r=subprocess.run(['systemctl',action,'ofls-speech-bridge.service'],capture_output=True,text=True);result[action]=r.stdout.strip()
assert result['is-active']=='inactive' and result['is-enabled']=='disabled',result
Path('/home/fpp/media/logs/teddy-retirement-result.json').write_text(json.dumps(result))
'''
    upload_script('retire-teddy-services.py',script)
    command(OLD,'Run Script',['retire-teddy-services.py','',''])
    result=None
    for _ in range(15):
        time.sleep(.5)
        try:result=api(OLD,'/api/file/Logs/teddy-retirement-result.json')
        except Exception:continue
        if isinstance(result,dict) and result.get('is-active')=='inactive':break
    assert result and result.get('worker_running') is False and result.get('is-enabled')=='disabled',result
    assert api(MASTER,'/api/system/status')['fppd']=='running'
    assert api(OLD,'/api/system/status')['fppd']=='running'
    assert api(LIGHTS,'/api/channel/output/co-bbbStrings')==before['pixel_outputs']
    record={'old_controller':OLD,'disabled_buttons':disabled,'startup_actions_removed':True,
            'entry_script_is_noop':True,'persistent_disabled_flag':True,
            'dedicated_old_speech_bridge':result,'master_kept_running':True,
            'old_controller_fpp_kept_running':True,'pixel_outputs_unchanged':True,
            'backup':str(BACKUP)}
    (SONG/'Tools/legacy-controller-retirement.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
