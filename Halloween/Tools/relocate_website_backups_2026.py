"""Relocate only this task's Master recovery links after full local verification."""
from pathlib import Path
import hashlib,json,shlex,subprocess,sys
ROOT=Path('/Users/elliott.ohara/xlights');SHOW=ROOT/'Halloween'
r=json.loads((SHOW/'website-promotion-latest.json').read_text());backup=Path(r['backup'])
progress_path=backup/'master-website-upload.json';p=json.loads(progress_path.read_text())
originals=p['backup_verified']['files'];out=backup/'Verified Master originals';out.mkdir(exist_ok=True)
if '--status' in sys.argv:
 program='import os,pathlib,json\np=pathlib.Path('+repr(p['remote_backup'])+')\ns=os.statvfs(p)\nprint(json.dumps({"free_bytes":s.f_bavail*s.f_frsize,"remaining_task_backup_links":len(list(p.glob("*.fseq")))}))\n'
 subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','fpp@192.168.0.19','python3 -'],input=program,text=True,check=True)
 sys.exit()
def digest(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
locations={f:SHOW/Path(s['sequence']).relative_to(r['source_show']).with_suffix('.fseq') for s in r['songs'].values() for f in s['playback_files']}
verified={}
for name,entry in originals.items():
 assert Path(name).name==name and name.endswith('.fseq')
 local=out/name
 if not local.exists():
  source=locations[name]
  if digest(source)==entry['sha256']:
   local.hardlink_to(source)
  else:
   temporary=local.with_suffix('.part')
   with temporary.open('wb') as f:subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','fpp@192.168.0.19','cat -- '+shlex.quote(p['remote_backup']+'/'+name)],stdout=f,check=True)
   assert digest(temporary)==entry['sha256'];temporary.replace(local)
 assert digest(local)==entry['sha256'],name
 verified[name]={'local':str(local),'sha256':entry['sha256'],'bytes':entry['bytes']}
 print('RECOVERY COPY VERIFIED',name,flush=True)
(backup/'master-recovery-copies-local.json').write_text(json.dumps(verified,indent=2)+'\n')
program='''from pathlib import Path
import hashlib,json,os
directory=Path(DIRECTORY)
expected=EXPECTED
assert directory.name.startswith('website-promotion-20261018-')
freed=0
for name,checksum in expected.items():
 assert Path(name).name==name and name.endswith('.fseq')
 path=directory/name
 if not path.exists():continue
 assert not path.is_symlink()
 with path.open('rb') as f:
  h=hashlib.sha256()
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 assert h.hexdigest()==checksum,name
 if path.stat().st_nlink==1:freed+=path.stat().st_size
 path.unlink()
print(json.dumps({'task_backup_links_removed':len(expected),'bytes_released':freed}))
'''.replace('DIRECTORY',repr(p['remote_backup'])).replace('EXPECTED',repr({n:v['sha256'] for n,v in verified.items()}))
result=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','fpp@192.168.0.19','sudo -n python3 -'],input=program,capture_output=True,text=True)
assert result.returncode==0,result.stderr
print(result.stdout,flush=True)
p['recovery_copies_relocated_to_mac']=str(out);p['remote_backup_links_removed_after_full_checksum_verification']=True
progress_path.write_text(json.dumps(p,indent=2)+'\n')
subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','fpp@192.168.0.19','df -h /home/fpp/media'],check=True)
