import importlib.util,os,sys,tempfile,fcntl,subprocess,json
from pathlib import Path
p=Path(__file__).with_name('teddy_control.py')
spec=importlib.util.spec_from_file_location('worker',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as d:
 lock=Path(d)/'interaction.lock'
 a=lock.open('a');b=lock.open('a')
 assert m.acquire_interaction(a)
 assert not m.acquire_interaction(b)
 m.release_interaction(a)
 assert m.acquire_interaction(b)
 m.release_interaction(b)
 proc=subprocess.Popen([sys.executable,'-c','import fcntl,sys; f=open(sys.argv[1],"a");fcntl.flock(f,fcntl.LOCK_EX);print("locked",flush=True);sys.stdin.read()',str(lock)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
 assert proc.stdout.readline().strip()=='locked'
 assert not m.acquire_interaction(a)
 proc.stdin.close();assert proc.wait(timeout=3)==0
 assert m.acquire_interaction(a)
 m.release_interaction(a)
 # A crashed lock owner must leave no stale blocker.
 proc=subprocess.Popen([sys.executable,'-c','import fcntl,sys,time;f=open(sys.argv[1],"a");fcntl.flock(f,fcntl.LOCK_EX);print("locked",flush=True);time.sleep(60)',str(lock)],stdout=subprocess.PIPE,text=True)
 assert proc.stdout.readline().strip()=='locked';assert not m.acquire_interaction(a)
 proc.kill();proc.wait(timeout=3);assert m.acquire_interaction(a);m.release_interaction(a)
print('PASS: mutual exclusion, independent process contention, normal release, crash release')
