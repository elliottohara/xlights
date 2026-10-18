"""Deploy the rendered library and GPIO actions. Master is read-only."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
import json,hashlib,time,copy

ROOT=Path(__file__).resolve().parents[4]
SONG=ROOT/'Halloween/Sequences/Teddy Interactive'
PI='192.168.0.133'; TEDDY='192.168.0.213'; MASTER='192.168.0.19'

def request(ip,path,value=None,method=None,binary=False):
    assert ip!=MASTER or (value is None and method is None)
    data=value if isinstance(value,bytes) else json.dumps(value).encode() if value is not None else None
    headers={'Content-Type':'application/octet-stream' if binary else 'application/json'} if data is not None else {}
    with urlopen(Request('http://'+ip+path,data,headers,method=method),timeout=30) as response:
        raw=response.read()
    try:return json.loads(raw)
    except (ValueError,UnicodeDecodeError):return raw

def cmd(ip,name,args):return request(ip,'/api/command',{'command':name,'args':args})

def upload(ip,directory,name,data):
    path='/api/file/'+directory+'/'+quote(name,safe='')
    result=request(ip,path,data,'POST',True)
    actual=request(ip,path)
    assert isinstance(actual,bytes) and actual==data,(name,result)
    return {'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

def main():
    before={'master':request(MASTER,'/api/system/status'),
            'pixels':request(TEDDY,'/api/channel/output/co-bbbStrings'),
            'presets':request(PI,'/api/configfile/commandPresets.json'),
            'gpio':request(PI,'/api/configfile/gpio.json')}
    assert before['master']['fppd']=='running'
    (SONG/'Tools/deployment-before.json').write_text(json.dumps(before,indent=2)+'\n')
    uploaded=[]
    for file in sorted((SONG/'Effects').glob('*.eseq')):
        uploaded.append(upload(TEDDY,'effects',file.name,file.read_bytes()))
        print('Uploaded',file.name,flush=True)
    print(upload(PI,'scripts','teddy_control.py',(SONG/'Tools/teddy_control.py').read_bytes()),flush=True)
    wrapper=b'#!/bin/bash\nexec /usr/bin/python3 /home/fpp/media/scripts/teddy_control.py "$@"\n'
    print(upload(PI,'scripts','teddy_controls.sh',wrapper),flush=True)
    presets=copy.deepcopy(before['presets'])
    existing=[c for c in presets.get('commands',[]) if c.get('name')=='FPPD_STARTED']
    assert not existing or all(c.get('command')=='Run Script' and c.get('args',[None])[0]=='teddy_controls.sh' for c in existing)
    presets['commands']=[c for c in presets.get('commands',[]) if c.get('name')!='FPPD_STARTED']
    presets['commands'].append({'name':'FPPD_STARTED','presetSlot':0,
        'command':'Run Script','args':['teddy_controls.sh','startup',''],
        'multisyncCommand':False,'multisyncHosts':''})
    print('Startup preset',request(PI,'/api/configfile/commandPresets.json',presets),flush=True)
    gpio=copy.deepcopy(before['gpio'])
    mapping={
        'P1-11':('White - Teddy arms up','up','gpio_pd','rising'),
        'P1-13':('Green - Teddy arms down','down','gpio_pu','falling'),
        'P1-15':('Blue - Teddy look left','left','gpio_pu','falling'),
        'P1-16':('Red - Teddy surprise + fart','red','gpio_pu','falling'),
        'P1-18':('Yellow - Teddy look right','right','gpio_pu','falling'),
    }
    for t in gpio:
        if t['pin'] in mapping:
            desc,action,mode,edge=mapping[t['pin']]
            t.update(enabled=True,desc=desc,mode=mode,rising=[],falling=[],hold=[],holdTime=0,
                     debounceTime=100,debounceEdge='both',reEnableMode='timed',
                     reEnableDelay=2200 if action=='red' else 1100,ledPin='')
            t[edge]=[{'command':'Run Script','args':['teddy_controls.sh',action,''],
                     'multisyncCommand':False,'multisyncHosts':''}]
        elif t['pin']=='P1-10':
            t.update(enabled=False,desc='Unused legacy wing trigger',rising=[],falling=[],hold=[])
    print('GPIO',request(PI,'/api/configfile/gpio.json',gpio),flush=True)
    assert request(PI,'/api/configfile/gpio.json')==gpio
    assert request(PI,'/api/configfile/commandPresets.json')==presets
    assert request(TEDDY,'/api/channel/output/co-bbbStrings')==before['pixels']
    print('Restarting button Pi only',request(PI,'/api/system/fppd/restart'),flush=True)
    result={'pi':PI,'teddy':TEDDY,'uploaded':uploaded,'gpio':gpio,'startup_preset':True,
            'master_kept_running':True,'controller_pixel_config_unchanged':True}
    (SONG/'Tools/deployment-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    for _ in range(25):
        time.sleep(1)
        try:
            state=request(PI,'/api/configfile/teddy-runtime.json')
            if isinstance(state,dict) and state.get('heartbeat',0)>time.time()-5:
                print('Runtime',json.dumps(state),flush=True);break
        except Exception:pass
    else:raise RuntimeError('Teddy startup worker did not report ready')

if __name__=='__main__':main()
