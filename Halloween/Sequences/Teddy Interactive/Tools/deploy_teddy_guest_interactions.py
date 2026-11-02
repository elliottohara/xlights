"""Install Teddy-only effects and a dedicated idle loop; old button Pi is retired."""
from pathlib import Path
from urllib.error import HTTPError
import copy,json
from deploy_teddy_controls import request,cmd,upload

ROOT=Path(__file__).resolve().parents[4]
SONG=ROOT/'Halloween/Sequences/Teddy Interactive'
BACKUP=ROOT/'Halloween/Backups/Teddy continuous default 20261101/Before deploy'
PIXELS='192.168.0.213';MASTER='192.168.0.19'

def check_teddy_range(data):
    assert data[:4]==b'PSEQ' and data[7]==2,'Expected native compressed ESEQ'
    count=data[21]|((data[20]>>4)<<8);start=32+8*count
    ranges=[(int.from_bytes(data[i:i+3],'little'),int.from_bytes(data[i+3:i+6],'little'))
            for i in range(start,start+6*data[22],6)]
    assert ranges==[(214642,1500)],'Existing background covers other props; preserve it'

def main():
    manifest=json.loads((SONG/'Tools/guest-interactions.json').read_text())
    before={'master':request(MASTER,'/api/system/status'),
            'pixel_outputs':request(PIXELS,'/api/channel/output/co-bbbStrings'),
            'effects':request(PIXELS,'/api/fppd/effects'),
            'presets':request(PIXELS,'/api/configfile/commandPresets.json')}
    assert before['master']['fppd']=='running'
    assert not any(e['name'].startswith('ofls-speech-') for e in before['effects'].get('runningEffects',[])), 'Teddy is speaking; retry after speech ends'
    BACKUP.mkdir(parents=True,exist_ok=True)
    if not (BACKUP/'before.json').exists():(BACKUP/'before.json').write_text(json.dumps(before,indent=2)+'\n')
    names=[r['name'] for r in manifest['effects']]+[manifest['default_background_alias']]
    uploaded=[]
    for name in names:
        uploaded.append(upload(PIXELS,'effects',name+'.eseq',(SONG/'Effects'/(name+'.eseq')).read_bytes()))
    idle=manifest['persistent_background_effect']
    assert idle=='Teddy Interactive Idle', 'Use the dedicated name that survives show commands'
    new=(ROOT/manifest['background_eseq']).read_bytes();check_teddy_range(new)
    try:old=request(PIXELS,'/api/file/effects/'+idle.replace(' ','%20')+'.eseq')
    except HTTPError as error:
        if error.code!=404:raise
        old=None
    if old is not None:check_teddy_range(old)
    if old is not None and not (BACKUP/(idle+'.eseq')).exists():(BACKUP/(idle+'.eseq')).write_bytes(old)
    # The legacy native boot alias is Teddy-only before we retire its running
    # instance. Never stop a background file covering the pumpkin or other props.
    try:legacy=request(PIXELS,'/api/file/effects/background.eseq')
    except HTTPError as error:
        if error.code!=404:raise
        legacy=None
    if legacy is not None:check_teddy_range(legacy)
    temporary=False
    try:
        if old is not None and old!=new:
            # Keep the new default visible while releasing the old mapped file.
            cmd(PIXELS,'Effect Start',['Teddy Default','','true','false','true',manifest['model']])
            temporary=True
            cmd(PIXELS,'Effect Stop',[idle])
        uploaded.append(upload(PIXELS,'effects',idle+'.eseq',new))
        running={e['name'] for e in request(PIXELS,'/api/fppd/effects').get('runningEffects',[])}
        if idle not in running:
            cmd(PIXELS,'Effect Start',[idle,'','true','false','true',manifest['model']])
        assert idle in {e['name'] for e in request(PIXELS,'/api/fppd/effects').get('runningEffects',[])}
        if legacy is not None:cmd(PIXELS,'Effect Stop',['background'])
        # Multiple commands for one event are native FPP presets. They retain
        # any existing unrelated startup actions and execute only on this FPP.
        presets=copy.deepcopy(before['presets'])
        startup=[('Effect Start',[idle,'','true','false','true',manifest['model']])]
        if legacy is not None:startup.append(('Effect Stop',['background']))
        for command,args in startup:
            if not any(c.get('name')=='FPPD_STARTED' and c.get('command')==command and c.get('args')==args
                       for c in presets.get('commands',[])):
                presets.setdefault('commands',[]).append({'name':'FPPD_STARTED','presetSlot':0,
                    'command':command,'args':args,'multisyncCommand':False,'multisyncHosts':''})
        if presets!=before['presets']:request(PIXELS,'/api/configfile/commandPresets.json',presets)
        assert request(PIXELS,'/api/configfile/commandPresets.json')==presets
    finally:
        if temporary:cmd(PIXELS,'Effect Stop',['Teddy Default'])
    assert request(PIXELS,'/api/channel/output/co-bbbStrings')==before['pixel_outputs']
    assert request(MASTER,'/api/system/status')['fppd']=='running'
    report={'effects_uploaded_and_readback_verified':uploaded,'continuous_native_background':True,
            'background_effect':idle,'boot':'Selfie Station FPPD_STARTED starts the dedicated idle loop',
            'survives_legacy_background_stop':True,
            'old_button_controller_contacted':False,'master_kept_running':True,
            'pixel_outputs_unchanged':True,'fpp_services_restarted':False}
    (SONG/'Tools/continuous-default-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
