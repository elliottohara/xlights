"""Run as yardhost on Teddy Pi; hot-load saved cues without restarting voice."""
from pathlib import Path
import hashlib,hmac,json,shlex,shutil,time,urllib.request

PATCH={'effect_wake':'Teddy Wake Hello','effect_thinking':'Teddy Thinking',
       'effect_idle':'Teddy Goodbye','thinking_loop':True,'idle_blink':True,
       'enabled':True,'dry_run':False}

def main():
    home=Path.home();endpoint='http://127.0.0.1:8771/yard/presence/api'
    with urllib.request.urlopen(endpoint,timeout=8) as r:before=json.load(r)
    assert before['fpp_effects']['ok']
    assert all(PATCH[k] in before['fpp_effects']['names'] for k in
               ['effect_wake','effect_thinking','effect_idle'])
    config=Path(before['config_path'])
    backup=home/'ofls-yard-host/backups/teddy-guest-interactions-20261101'
    backup.mkdir(parents=True,exist_ok=True)
    if config.exists() and not (backup/config.name).exists():shutil.copy2(config,backup/config.name)
    secret=None
    for line in (home/'.config/ofls-yard-host/yard-host.env').read_text().splitlines():
        if line.startswith('YARD_SPEAK_CALLBACK_SECRET='):
            values=shlex.split(line.split('=',1)[1]);secret=values[0] if values else None
    assert secret,'Operator credential missing'
    body=json.dumps(PATCH,separators=(',',':'));ts=int(time.time())
    signature=hmac.new(secret.encode(),(str(ts)+'\n'+body).encode(),hashlib.sha256).hexdigest()
    req=urllib.request.Request(endpoint,body.encode(),{'Content-Type':'application/json',
        'X-Ofls-Timestamp':str(ts),'X-Ofls-Signature':signature})
    with urllib.request.urlopen(req,timeout=10) as r:result=json.load(r)
    assert result['ok'] and all(result['effective'][k]==v for k,v in PATCH.items())
    print(json.dumps({'hot_reloaded':True,'effective':result['effective'],'backup':str(backup)}))

if __name__=='__main__':main()
