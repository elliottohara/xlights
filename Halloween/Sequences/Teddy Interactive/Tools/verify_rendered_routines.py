"""Verify the native exports' duration, channel bounds, scarf colors and motion."""
from pathlib import Path
import ctypes,ctypes.util,hashlib,json,struct,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[4];SONG=ROOT/'Halloween/Sequences/Teddy Interactive'
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
z.ZSTD_isError.argtypes=[ctypes.c_size_t];z.ZSTD_isError.restype=ctypes.c_uint

def decode(path):
 b=path.read_bytes();assert b[:4]==b'PSEQ' and b[7]==2 and b[20]&15==1
 channels,frames=struct.unpack_from('<II',b,10);step=b[18]
 count=b[21]|((b[20]>>4)<<8);sparse_count=b[22]
 ranges=[(int.from_bytes(b[i:i+3],'little'),int.from_bytes(b[i+3:i+6],'little')) for i in range(32+8*count,32+8*count+6*sparse_count,6)]
 blocks=[struct.unpack_from('<II',b,32+8*i) for i in range(count)];blocks=[x for x in blocks if x[1]]
 pos=int.from_bytes(b[4:6],'little');raw=bytearray()
 for i,(first,size) in enumerate(blocks):
  end=blocks[i+1][0] if i+1<len(blocks) else frames
  expected=(end-first)*channels;out=ctypes.create_string_buffer(expected);chunk=b[pos:pos+size]
  actual=z.ZSTD_decompress(out,expected,chunk,size);assert not z.ZSTD_isError(actual) and actual==expected
  raw.extend(out.raw);pos+=size
 assert len(raw)==channels*frames
 return [bytes(raw[i*channels:(i+1)*channels]) for i in range(frames)],step,ranges

def nodes(text):
 result=[]
 for part in text.split(','):
  ab=list(map(int,part.split('-')));result.extend(range(ab[0],ab[-1]+(1 if ab[-1]>=ab[0] else -1),1 if ab[-1]>=ab[0] else -1))
 return result
m=next(v for v in E.parse(ROOT/'Halloween/xlights_rgbeffects.xml').iter('model') if v.get('name')=='Elliott - EFL Teddy')
bow=next(v for v in m.findall('subModel') if v.get('name')=='Bow Tie')
bow_nodes=sorted(set(n for key,val in bow.attrib.items() if key.startswith('line') for n in nodes(val)))
arm_nodes=nodes('91-98,101-117,120-136,367-383,386-402,405-412')
def pixels(frame,indices):return b''.join(frame[(n-1)*3:n*3] for n in indices)
colors={'green':bytes.fromhex('00ff00'),'blue':bytes.fromhex('0000ff'),'yellow':bytes.fromhex('ffff00'),'red':bytes.fromhex('ff0000')}
results=[];motion_signatures=set()
for item in json.loads((SONG/'Tools/library.json').read_text()):
 if 'button' not in item:continue
 frames,step,ranges=decode(ROOT/item['eseq']);assert len(frames)==200 and step==25 and ranges==[(214642,1500)]
 button=item['button'];scarf=[pixels(f,bow_nodes) for f in frames]
 if button in colors:assert all(p==colors[button]*len(bow_nodes) for p in scarf),(button,'scarf color mismatch')
 else:
  assert len(set(scarf))>1,'White marquee is static'
  assert any(b'\xff\xff\xff' in p for p in scarf),'No white marquee lights'
  assert all(p[i]==p[i+1]==p[i+2] for p in scarf for i in range(0,len(p),3)),'White scarf contains colored background'
 arm_frames=[pixels(f,arm_nodes) for f in frames];assert len(set(arm_frames))>=2
 # Every requested quarter-second pose is present, including the end of the routine.
 for t in range(0,190,10):assert arm_frames[t]!=arm_frames[t+10],(button,'arm motion stopped',t)
 signature=hashlib.sha256(b''.join(arm_frames)).hexdigest();assert signature not in motion_signatures
 motion_signatures.add(signature)
 results.append({'button':button,'duration_ms':len(frames)*step,'sparse_ranges':ranges,'arm_frames_differ':True,'distinct_arm_pattern':True,'scarf_verified':item['scarf'],'white_marquee_unique_frames':len(set(scarf)) if button=='white' else None})
report={'routines':results,'all_five_passed':len(results)==5}
(SONG/'Tools/rendered-routines-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
