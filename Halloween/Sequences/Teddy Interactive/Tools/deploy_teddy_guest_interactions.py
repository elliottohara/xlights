"""Install Teddy-only effects and a continuous native base; old button Pi is retired."""
from pathlib import Path
from urllib.error import HTTPError
import json
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
            'effects':request(PIXELS,'/api/fppd/effects')}
    assert before['master']['fppd']=='running'
    assert not any(e['name'].startswith('ofls-speech-') for e in before['effects'].get('runningEffects',[])), 'Teddy is speaking; retry after speech ends'
    BACKUP.mkdir(parents=True,exist_ok=True)
    if not (BACKUP/'before.json').exists():(BACKUP/'before.json').write_text(json.dumps(before,indent=2)+'\n')
    names=[r['name'] for r in manifest['effects']]+[manifest['default_background_alias']]
    uploaded=[]
    for name in names:
        uploaded.append(upload(PIXELS,'effects',name+'.eseq',(SONG/'Effects'/(name+'.eseq')).read_bytes()))
    new=(SONG/'Effects/background.eseq').read_bytes();check_teddy_range(new)
    try:old=request(PIXELS,'/api/file/effects/background.eseq')
    except HTTPError as error:
        if error.code!=404:raise
        old=None
    if old is not None:check_teddy_range(old)
    if old is not None and not (BACKUP/'background.eseq').exists():(BACKUP/'background.eseq').write_bytes(old)
    temporary=False
    try:
        if old is not None and old!=new:
            # Keep the new default visible while releasing the old mapped file.
            cmd(PIXELS,'Effect Start',['Teddy Default','','true','false','true',manifest['model']])
            temporary=True
            cmd(PIXELS,'Effect Stop',['background'])
        uploaded.append(upload(PIXELS,'effects','background.eseq',new))
        running={e['name'] for e in request(PIXELS,'/api/fppd/effects').get('runningEffects',[])}
        if 'background' not in running:
            cmd(PIXELS,'Effect Start',['background','','true','false','true',manifest['model']])
    finally:
        if temporary:cmd(PIXELS,'Effect Stop',['Teddy Default'])
    assert request(PIXELS,'/api/channel/output/co-bbbStrings')==before['pixel_outputs']
    assert request(MASTER,'/api/system/status')['fppd']=='running'
    report={'effects_uploaded_and_readback_verified':uploaded,'continuous_native_background':True,
            'boot':'Native FPP InitEffects automatically starts background.eseq',
            'old_button_controller_contacted':False,'master_kept_running':True,
            'pixel_outputs_unchanged':True,'fpp_services_restarted':False}
    (SONG/'Tools/continuous-default-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
