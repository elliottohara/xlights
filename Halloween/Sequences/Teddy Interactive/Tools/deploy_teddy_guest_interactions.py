"""Install only Teddy effects. Never send a command to Master."""
from pathlib import Path
import hashlib, json, shutil, time
from urllib.parse import quote
from deploy_teddy_controls import request, cmd, upload

ROOT=Path(__file__).resolve().parents[4]
SONG=ROOT/'Halloween/Sequences/Teddy Interactive'
BACKUP=ROOT/'Halloween/Backups/Teddy guest interactions 20261101/Controller before'
PIXELS='192.168.0.213'; BUTTONS='192.168.0.133'; MASTER='192.168.0.19'

def main():
    manifest=json.loads((SONG/'Tools/guest-interactions.json').read_text())
    before={'master':request(MASTER,'/api/system/status'),
            'pixel_outputs':request(PIXELS,'/api/channel/output/co-bbbStrings'),
            'gpio':request(BUTTONS,'/api/configfile/gpio.json'),
            'presets':request(BUTTONS,'/api/configfile/commandPresets.json'),
            'effects':request(PIXELS,'/api/fppd/effects')}
    assert before['master']['fppd']=='running'
    assert not any(e['name'].startswith('ofls-speech-') for e in before['effects'].get('runningEffects',[])), 'Teddy is speaking; retry after speech ends'
    BACKUP.mkdir(parents=True,exist_ok=True)
    if not (BACKUP/'before.json').exists():
        (BACKUP/'before.json').write_text(json.dumps(before,indent=2)+'\n')
    names=[r['name'] for r in manifest['effects']]+[manifest['default_background_alias']]
    for name in names:
        if (BACKUP/(name+'.eseq')).exists():continue
        try:raw=request(PIXELS,'/api/file/effects/'+quote(name+'.eseq',safe=''))
        except Exception:continue
        if isinstance(raw,bytes):(BACKUP/(name+'.eseq')).write_bytes(raw)
    # Release only the worker's old mapped hold. The speaking/visit service and
    # all FPP playback services keep running; GPIO and shared flock stay intact.
    cmd(BUTTONS,'Run Script',['teddy_controls.sh','pause',''])
    time.sleep(.5)
    uploaded=[]
    try:
        running=request(PIXELS,'/api/fppd/effects').get('runningEffects',[])
        for effect in running:
            if effect['name']=='Teddy Hold Down':cmd(PIXELS,'Effect Stop',['Teddy Hold Down'])
        for name in names:
            data=(SONG/'Effects'/(name+'.eseq')).read_bytes()
            uploaded.append(upload(PIXELS,'effects',name+'.eseq',data))
        request(BUTTONS,'/api/configfile/teddy-guest-interactions.json',manifest)
        assert request(BUTTONS,'/api/configfile/teddy-guest-interactions.json')==manifest
    finally:
        cmd(BUTTONS,'Run Script',['teddy_controls.sh','startup',''])
    assert request(MASTER,'/api/system/status')['fppd']=='running'
    assert request(PIXELS,'/api/channel/output/co-bbbStrings')==before['pixel_outputs']
    assert request(BUTTONS,'/api/configfile/gpio.json')==before['gpio']
    assert request(BUTTONS,'/api/configfile/commandPresets.json')==before['presets']
    result={'effects_uploaded_and_readback_verified':uploaded,
            'backup':str(BACKUP),'master_running':True,
            'pixel_outputs_unchanged':True,'gpio_and_startup_presets_unchanged':True,
            'fpp_services_restarted':False,'pi_presence_config_updated':False}
    (SONG/'Tools/guest-interactions-deployment.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
