"""Check the actual native-rendered pixels, including smooth boundary poses."""
from pathlib import Path
import ast, ctypes, ctypes.util, hashlib, json, struct
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[4]
SONG=ROOT/'Halloween/Sequences/Teddy Interactive'
tree=ast.parse((SONG/'Tools/verify_rendered_routines.py').read_text())
helpers=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)
                        and n.name in ['decode','nodes','pixels']],type_ignores=[])
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
z.ZSTD_decompress.restype=ctypes.c_size_t
z.ZSTD_isError.argtypes=[ctypes.c_size_t];z.ZSTD_isError.restype=ctypes.c_uint
exec(compile(helpers,'native-eseq-decoder','exec'))

def main():
    manifest=json.loads((SONG/'Tools/guest-interactions.json').read_text())
    decoded={}
    for row in manifest['effects']:
        path=ROOT/row['eseq'];frames,step,ranges=decode(path)
        assert step==25 and ranges==[(214642,1500)]
        assert len(frames)*step==row['duration_ms']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        decoded[row['event']]=frames
    default=decoded['idle'][0]
    model=next(m for m in E.parse(ROOT/'Halloween/xlights_rgbeffects.xml').iter('model')
               if m.get('name')==manifest['model'])
    bow=next(m for m in model.findall('subModel') if m.get('name')=='Bow Tie')
    bow_nodes=set(n for k,v in bow.attrib.items() if k.startswith('line') for n in nodes(v))
    left=nodes('91-98,101-117,120-136')
    right=nodes('367-383,386-402,405-412')
    face=next(f for f in model.findall('faceInfo') if f.get('Name')=='Teddy ')
    eyes=set(n for k,v in face.attrib.items() if k.startswith('Eyes-') and v
             and not k.endswith('Color') for n in nodes(v))
    results=[]
    for event,frames in decoded.items():
        assert all(f==default for f in frames[:10]),(event,'start hold mismatch')
        assert all(f==default for f in frames[-10:]),(event,'end hold mismatch')
        assert frames[0]==frames[-1]==default,(event,'handoff mismatch')
        minimum_lit=min(sum(any(f[i:i+3]) for i in range(0,len(f),3)) for f in frames)
        assert minimum_lit>=300,(event,'body must stay illuminated')
        left_poses=len({pixels(f,left) for f in frames})
        right_poses=len({pixels(f,right) for f in frames})
        if event=='wake':assert left_poses==3 and right_poses==1
        if event=='farewell':assert left_poses==1 and right_poses==3
        if event in ('idle','thinking'):assert left_poses==right_poses==1
        if event=='thinking':
            changed={i//3+1 for f in frames for i,(a,b) in enumerate(zip(f,default)) if a!=b}
            assert changed <= bow_nodes|eyes,(changed-bow_nodes-eyes)
            marquee=len({pixels(f,sorted(bow_nodes)) for f in frames})
            assert marquee>10
        else:marquee=None
        results.append(dict(event=event,frames=len(frames),duration_ms=len(frames)*25,
                            exact_default_boundaries=True,neutral_holds_ms=250,
                            minimum_lit_pixels=minimum_lit,
                            left_arm_poses=left_poses,right_arm_poses=right_poses,
                            marquee_unique_frames=marquee))
    assert (SONG/'Effects/Teddy Hold Down.eseq').read_bytes()==(SONG/'Effects/Teddy Default.eseq').read_bytes()
    assert (SONG/'Effects/background.eseq').read_bytes()==(SONG/'Effects/Teddy Default.eseq').read_bytes()
    report=dict(all_passed=True,model=manifest['model'],channels=1500,
                sparse_offset=214642,frame_ms=25,background_alias_matches=True,clips=results)
    (SONG/'Tools/guest-interactions-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
