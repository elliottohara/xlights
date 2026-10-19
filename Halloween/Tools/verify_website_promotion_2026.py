from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
ROOT=Path('/Users/elliott.ohara/xlights')
sys.path.insert(0,str(ROOT/'Halloween/Tools'))
from verify_voting_overlays_2026 import FSEQ
report=json.loads((ROOT/'Halloween/website-promotion-latest.json').read_text());backup=Path(report['backup']);out=backup/'Pixel checks';out.mkdir(exist_ok=True)
sign=np.array(Image.open(str(Path(report['source_show'])/'WebsitePromotion/tune-to-website.png')).convert('RGBA'));mask=sign[:,:,3]==255
qr=np.array(Image.open(str(Path(report['source_show'])/'WebsitePromotion/projector-website-qr.png')).convert('RGB'))
start=next(c['startchannel'] for c in report['controllers'] if c['name']=='FPP-TUNETO')
names=sys.argv[1:] or list(report['songs'])
for name in names:
 song=report['songs'][name]
 if not song.get('rendered'):continue
 result_path=out/(name+'.json')
 if result_path.exists():continue
 reader=FSEQ(Path(song['sequence']).with_suffix('.fseq'));results={'song':name,'sign_checks':[],'qr_checks':[]}
 for ms in range(0,reader.frames*reader.step,1000):
  data=np.frombuffer(reader.model(ms,start,192*64*3),dtype=np.uint8).reshape((64,192,3))
  match=float(np.mean(np.all(np.abs(data.astype(np.int16)-sign[:,:,:3].astype(np.int16))<=2,axis=2)[mask]))
  assert match>.999,(name,ms,'sign mismatch',match)
  results['sign_checks'].append([ms,match])
  if ms==12000:Image.fromarray(data).save(out/(name+' - sign.png'))
 for first,last in song['qr_windows_ms']:
  for ms in [first+reader.step,(first+last)//2,last-reader.step]:
   data=np.frombuffer(reader.model(ms,1,256*192*3),dtype=np.uint8).reshape((192,256,3))
   match=float(np.mean(np.all(np.abs(data.astype(np.int16)-qr.astype(np.int16))<=2,axis=2)))
   if match<=.999:Image.fromarray(data).save(out/(name+' - mismatch.png'))
   assert match>.999,(name,ms,'QR mismatch',match)
   results['qr_checks'].append([ms,match])
   if ms==(first+last)//2:Image.fromarray(data).save(out/(name+' - qr.png'))
 reader.file.close();result_path.write_text(json.dumps(results,indent=2))
 print('PIXELS VERIFIED',name,len(results['sign_checks']),len(results['qr_checks']),flush=True)
