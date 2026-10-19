import importlib.util,tempfile,json,fcntl
from pathlib import Path
spec=importlib.util.spec_from_file_location('worker',Path(__file__).with_name('teddy_control.py'));w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
class EndTest(BaseException):pass
with tempfile.TemporaryDirectory() as d:
 root=Path(d);w.HOME=root;w.CONFIG=root;w.QUEUE=root/'queue.json';w.STATE=root/'state.json';w.LOCK=root/'worker.lock';w.INTERACTION_LOCK=root/'interaction.lock'
 now=[0.];events=[];case=[0]
 w.time.monotonic=lambda:now[0];w.time.time=lambda:1000+now[0]
 other=w.INTERACTION_LOCK.open('a');fcntl.flock(other,fcntl.LOCK_EX|fcntl.LOCK_NB)
 w.QUEUE.write_text(json.dumps({'action':'green','id':'press-1','time':1000}))
 def api(ip,path,command=None,args=None):
  assert ip!=w.MASTER or command is None
  if ip==w.MASTER:return {'status_name':'playing','current_sequence':'song.fseq'}
  if path=='/api/fppd/effects':return {'runningEffects':[]}
  events.append((now[0],command,args));return 'OK'
 w.api=api
 def sleep(dt):
  now[0]+=dt
  if case[0]==0 and now[0]>=2:
   assert events==[],events
   assert json.loads(w.STATE.read_text())['status']=='speech'
   fcntl.flock(other,fcntl.LOCK_UN);case[0]=1
  if case[0]==1 and any(e[1]=='Effect Start' for e in events):
   try:fcntl.flock(other,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:pass
   else:raise AssertionError('gesture failed to retain lock')
   assert events[0][2][0]=='Teddy Green Routine'
   case[0]=2
  if case[0]==2 and now[0]>=7.3:
   assert w.acquire_interaction(other),'gesture never released lock'
   assert sum(e[1]=='Effect Start' for e in events)==1,events
   raise EndTest
 w.time.sleep=sleep
 try:w.worker()
 except EndTest:pass
print('PASS: queued button waits during speech, then runs once; gesture owns lock for full duration; no Master commands')
