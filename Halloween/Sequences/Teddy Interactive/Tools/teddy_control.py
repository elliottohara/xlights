#!/usr/bin/env python3
"""Five-button Teddy controller. Only the named Teddy effects are modified.

Install in FPP's scripts directory on the button Pi. The worker plays five-second arm
routines, prevents overlapping reactions, and yields its idle pose
to the main show. Buttons can still trigger a short reaction during a song.
"""
import fcntl, json, os, signal, subprocess, sys, time, uuid
from pathlib import Path
from urllib.request import Request, urlopen

PI = '127.0.0.1'
TEDDY = '192.168.0.213'
MASTER = '192.168.0.19'  # Read-only: never sends commands to Master.
HOME = Path('/home/fpp/media')
CONFIG = HOME / 'config'
QUEUE = CONFIG / 'teddy-request.json'
STATE = CONFIG / 'teddy-runtime.json'
LOCK = HOME / 'tmp/teddy-worker.lock'
LOG = HOME / 'logs/teddy-controls.log'
ACTIONS = {'white', 'green', 'blue', 'yellow', 'red'}
OWNED = {'Teddy '+color.title()+' Routine' for color in ACTIONS} | {'Teddy Arms Up', 'Teddy Arms Down'} | {
    'Teddy ' + expression + ' ' + pose
    for expression in ['Hold', 'Look Left', 'Look Right', 'Surprised']
    for pose in ['Down', 'Up']}

def api(ip, path, command=None, args=None):
    assert ip != MASTER or (command is None and path == '/api/system/status')
    data = json.dumps({'command':command,'args':args or []}).encode() if command else None
    request = Request('http://' + ip + path, data,
                      {'Content-Type':'application/json'} if data else {})
    with urlopen(request, timeout=2.5) as response:
        raw = response.read().decode()
    try:value=json.loads(raw)
    except ValueError:value=raw
    if isinstance(value, dict) and (value.get('Status') == 'ERROR' or value.get('respCode',200) >= 400):
        raise RuntimeError(str(value))
    return value

def atomic(path, value):
    temp = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)

def read(path, default):
    try:return json.loads(path.read_text())
    except (OSError,ValueError):return default

def log(message):
    print(time.strftime('%Y-%m-%d %H:%M:%S'), message, flush=True)

def running():
    value = api(TEDDY, '/api/fppd/effects')
    return [e['name'] for e in value.get('runningEffects',[]) if e['name'] in OWNED]

def stop_owned(except_name=None):
    for name in set(running()):
        if name != except_name:api(TEDDY, '/api/command', 'Effect Stop', [name])

def start(name, loop=False):
    assert name in OWNED
    api(TEDDY, '/api/command', 'Effect Start',
        [name,'214643',str(loop).lower(),'false','true',''])
    stop_owned(name)

def worker():
    lock = LOCK.open('a')
    try:fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:return
    old = read(STATE,{})
    state = {'arms':old.get('arms','down'),'pid':os.getpid(),'last_request':old.get('last_request',''),
             'status':'starting','last_action':old.get('last_action',''),'sound_count':old.get('sound_count',0)}
    deadline=0; current=''; next_check=0; show_playing=True; last_red=0
    last_saved=0; saved_signature=None
    while True:
        now=time.monotonic()
        try:
            if now >= next_check:
                try:
                    master=api(MASTER,'/api/system/status')
                    show_playing=bool(master.get('current_sequence') or master.get('media_playing') or master.get('status_name') not in ('idle','Idle'))
                except Exception:show_playing=True
                next_check=now+1
            request=read(QUEUE,{})
            action=request.get('action')
            # One short reaction at a time; keep only the most recent queued press.
            if now >= deadline and action in ACTIONS and request.get('id') != state['last_request']:
                state['last_request']=request['id']
                if time.time()-request.get('time',0) < 8:
                    name='Teddy '+action.title()+' Routine';duration=5
                    state['arms']='down'
                    start(name)
                    if action=='red' and now-last_red >= 2:
                        api(PI,'/api/command','Play Media',['dry-fart.mp3','1','0','1'])
                        state['sound_count']+=1;last_red=now
                    current=name;deadline=now+duration
                    state.update(last_action=action,status='gesture',effect=name)
                    log('button='+action+' effect='+name)
            if now >= deadline:
                if show_playing:
                    if current is not None:stop_owned();current=None
                    state.update(status='show',effect=None)
                else:
                    hold='Teddy Hold '+state['arms'].title()
                    if current != hold or now >= state.get('verify_after',0):
                        if current != hold or hold not in running():start(hold,True)
                        current=hold;state['verify_after']=now+4
                    state.update(status='idle_pose',effect=hold)
            state['show_playing']=show_playing
            signature=tuple(state.get(k) for k in ('arms','last_request','status','last_action','sound_count','effect','show_playing'))
            if signature!=saved_signature or now-last_saved>=5:
                state['heartbeat']=time.time()
                atomic(STATE,state)
                saved_signature=signature;last_saved=now
        except Exception as error:
            state.update(status='error',error=str(error),heartbeat=time.time())
            atomic(STATE,state);log('ERROR '+str(error));time.sleep(1)
        time.sleep(.075)

def main():
    action=sys.argv[1] if len(sys.argv)>1 else 'startup'
    if action=='--worker':return worker()
    if action in ('restart','pause'):
        pid=read(STATE,{}).get('pid',0)
        try:
            command=Path('/proc/'+str(pid)+'/cmdline').read_bytes()
            if b'teddy_control.py' in command and b'--worker' in command:
                os.kill(pid,signal.SIGTERM);time.sleep(.2)
        except (OSError,ProcessLookupError):pass
        if action=='pause':return
    elif action in ACTIONS:
        atomic(QUEUE,{'id':uuid.uuid4().hex,'action':action,'time':time.time()})
    elif action!='startup':raise SystemExit('Unknown Teddy action')
    with LOG.open('a') as output:
        subprocess.Popen([sys.executable,__file__,'--worker'],stdin=subprocess.DEVNULL,
                         stdout=output,stderr=output,start_new_session=True)

if __name__=='__main__':main()
