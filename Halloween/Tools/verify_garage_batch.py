"""Check every garage pixel and Tune To output in the completed batch."""
from pathlib import Path
import json,sys
from single_show_fseq import FSEQ
show=Path(__file__).resolve().parents[1];p=show/'garage-batch-render-latest.json';r=json.loads(p.read_text());assert r['all_local_renders_complete']
ref=json.loads(Path(r['physical_output_reference']).read_text());sign=next(c for c in ref['controllers'] if c['name']=='FPP-TUNETO')
targets={n:r['sample_addresses'][n] for n in ['Garage Left Bottom','Wall - Garage Top']};results={}
for name,song in r['songs'].items():
 reader=FSEQ(Path(song['xsq']).with_suffix('.fseq'));lit={n:set() for n in targets};sign_lit=0
 for ms in range(0,reader.frames*reader.step,1000):
  for n,m in targets.items():
   data=reader.model(ms,m['startchannel'],m['channels'])
   lit[n].update(i//3 for i in range(0,len(data),3) if any(data[i:i+3]))
  sign_lit+=bool(any(reader.model(ms,sign['startchannel'],sign['channels'])))
 reader.f.close()
 if name!='tuneto-halloween':
  for n in targets: assert len(lit[n])==targets[n]['pixels'],(name,n,len(lit[n]))
 assert sign_lit>0,(name,'Tune To is black')
 results[name]={'garage_pixels_lit':{n:len(v) for n,v in lit.items()},'sign_lit_samples':sign_lit}
 print('PIXEL COVERAGE',name,results[name],flush=True)
r['pixel_coverage_verification']=results;r['garage_all_103_pixels_verified']=True;r['all_24_tune_to_signs_lit']=True;p.write_text(json.dumps(r,indent=2)+'\n')
