"""Render website/radio sign bands and recurring projector QR cards natively.

Run in isolated slot A. Master is read-only throughout authoring. Original
renders remain in the canonical tree until verified replacements are adopted.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import Request,urlopen
import hashlib,html,json,re,shutil,struct,sys,time,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
SHOW=ROOT/'Halloween'
CANONICAL=Path('/Users/elliott.ohara/xlights/Halloween')
sys.path.insert(0,str(ROOT/'Tools'))
import xlights_api as x
REPORT=CANONICAL/'website-promotion-latest.json'
ASSETS=SHOW/'WebsitePromotion'
def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def api(endpoint):
 return json.load(urlopen('http://192.168.0.19'+endpoint,timeout=30))
def stamp():return datetime.now(ZoneInfo('America/Chicago')).isoformat()
def save():REPORT.write_text(json.dumps(record,indent=2)+'\n')
def signature(path):
 r=ET.parse(path).getroot();db=list(r.find('EffectDB'));pal=list(r.find('ColorPalettes'));result={}
 for e in r.findall('./ElementEffects/Element'):
  layers=[]
  for layer in e.findall('EffectLayer'):
   effects=[]
   for f in layer:
    attrs={k:v for k,v in f.attrib.items() if k not in ['ref','palette','id','selected']}
    cfg=dict(t.split('=',1) for t in (db[int(f.get('ref'))].text or '').split(',') if '=' in t) if f.get('ref') is not None else {}
    for k,v in list(cfg.items()):
     if 'FILEPICKER' in k or 'filename' in k.lower():
      if not v:cfg.pop(k);continue
      p=Path(html.unescape(v).replace('&comma;',','));cfg[k]=str((p if p.is_absolute() else SHOW/p).resolve())
     elif k=='B_CHOICE_PerPreviewCamera' and v=='2D':cfg.pop(k)
    effects.append((attrs,cfg,pal[int(f.get('palette'))].text if f.get('palette') is not None else None))
   layers.append(effects)
  if e.get('type')=='timing' or any(layers):result[e.get('name')]=layers
 return result
def info(path):
 with Path(path).open('rb') as f:h=f.read(32)
 return dict(channels=struct.unpack_from('<I',h,10)[0],frames=struct.unpack_from('<I',h,14)[0],frame_ms=h[18],id=str(struct.unpack_from('<Q',h,24)[0]),bytes=Path(path).stat().st_size)
def radio_text(root,effect):
 if effect.get('name')!='Text':return False
 cfg=dict(t.split('=',1) for t in (list(root.find('EffectDB'))[int(effect.get('ref'))].text or '').split(',') if '=' in t)
 text=cfg.get('E_TEXTCTRL_Text','')
 filename=cfg.get('E_FILEPICKERCTRL_Text_File')
 if filename:
  p=Path(html.unescape(filename));p=p if p.is_absolute() else SHOW/p
  if p.exists():text+=' '+p.read_text(errors='replace')
 return bool(re.search(r'87[.]9|tune\s*to',text,re.I))
def check_report(path):
 text=Path(path).read_text();start=text.index('id="section-sequence"');end=text.find('id="section-',start+20);section=text[start:end if end>=0 else None]
 issues={}
 for title,ok in [('Models Not Found in Layout','No missing model issues found'),('Impossible Effect Overlaps','No impossible effect overlaps found'),('Effects Extending Beyond Sequence End','No effects extending beyond sequence end found')]:
  m=re.search(r'<h3[^>]*>\s*'+title+r'\s*</h3>(.*?)(?=<h3|$)',section,re.S)
  if not m or ok not in m.group(1):issues[title]=re.sub('<[^>]+>',' ',m.group(1))[:600] if m else 'missing'
 return issues

if not REPORT.exists():
 backup=CANONICAL/'Backups'/('Website promotion '+datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
 record=dict(started_at=stamp(),backup=str(backup),branch='website-radio-projector-promotion',slot='A',source_show=str(SHOW),url='https://oharafamilylightshow.com/',domain='oharafamilylightshow.com',fm='87.9',qr_duration_ms=15000,qr_interval_ms=60000,qr_first_ms=10000,layout_sha256=digest(CANONICAL/'xlights_rgbeffects.xml'),network_sha256=digest(CANONICAL/'xlights_networks.xml'),songs={},complete=False)
 for endpoint,name in [('/api/schedule','master-schedule.json'),('/api/playlist/Halloween%202026','master-Halloween_2026.json'),('/api/playlist/Halloween%20Overnight','master-Halloween_Overnight.json'),('/api/channel/output/universeOutputs','master-routing.json')]:
  (backup/name).write_text(json.dumps(api(endpoint),indent=2))
 record['master_before']=api('/api/system/status');assert record['master_before']['fppd']=='running'
 shutil.copy2(CANONICAL/'current-show.json',backup/'current-show-before.json');save()
else:record=json.loads(REPORT.read_text());backup=Path(record['backup'])
assert x.xl('getShowFolder')['folder']==str(SHOW)
assert digest(SHOW/'xlights_rgbeffects.xml')==record['layout_sha256']
record['controllers']=x.xl('getControllers')['controllers'];save()
manifest=json.loads((CANONICAL/'current-show.json').read_text())
names=['tuneto-halloween','static halloween']+[n for n in manifest['songs'] if n not in ['tuneto-halloween','static halloween']]
for index,name in enumerate(names,1):
 if record['songs'].get(name,{}).get('rendered'):continue
 item=manifest['songs'][name];path=SHOW/item['sequence'];original=CANONICAL/item['sequence']
 baseline=backup/'Before'/item['sequence'];baseline.parent.mkdir(parents=True,exist_ok=True)
 if not baseline.exists():shutil.copy2(original,baseline)
 note=original.parent/'AGENT NOTES.md'
 if note.exists() and not (baseline.parent/note.name).exists():shutil.copy2(note,baseline.parent/note.name)
 expected=info(original.with_suffix('.fseq'))
 x.xl('closeSequence',quiet='true',force='false')
 shutil.copy2(original,path)
 if note.exists():shutil.copy2(note,path.parent/note.name)
 before=signature(path)
 tree=ET.parse(path);r=tree.getroot();duration=expected['frames']*expected['frame_ms']
 parent=r.find('ElementEffects');display=r.find('DisplayElements');removed=[];added_rows=[]
 for target in ['Tune To','Projector']:
  el=next((e for e in parent if e.get('name')==target),None)
  if el is None:
   el=ET.SubElement(parent,'Element',name=target,type='model');added_rows.append(target)
  if not any(e.get('name')==target for e in display):ET.SubElement(display,'Element',name=target,type='model',visible='true',collapsed='false')
  if target=='Tune To':
   for layer_index,layer in enumerate(el.findall('EffectLayer')):
    for f in list(layer):
     if radio_text(r,f):removed.append(dict(layer=layer_index,attributes=dict(f.attrib)));layer.remove(f)
  el.insert(0,ET.Element('EffectLayer'))
 tree.write(path,encoding='utf-8',xml_declaration=True)
 retained=signature(path)
 # Empty new layers are present in retained signature only when originals exist.
 opened=x.xl('openSequence',seq=str(path),promptIssues='false',timeout=180)
 assert Path(opened['fullseq'])==path and int(opened['len'])//expected['frame_ms']==expected['frames'],opened
 common=('E_CHECKBOX_LoopGIF=0,E_CHECKBOX_Pictures_PixelOffsets=0,E_CHECKBOX_Pictures_Shimmer=0,'
 'E_CHECKBOX_Pictures_TransparentBlack=0,E_CHECKBOX_Pictures_WrapX=0,E_CHECKBOX_SuppressGIFBackground=0,'
 'E_CHOICE_Pictures_Direction=none,E_CHOICE_Scaling=Scale To Fit,E_SLIDER_PicturesXC=0,E_SLIDER_PicturesYC=0,'
 'E_SLIDER_Pictures_EndScale=100,E_SLIDER_Pictures_StartScale=100,'
 'T_CHOICE_LayerMethod=Normal,T_TEXTCTRL_Fadein=0,T_TEXTCTRL_Fadeout=0')
 palette='C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'
 x.add_effect('Tune To',0,'Pictures',common+',E_TEXTCTRL_Pictures_Filename='+str(ASSETS/'tune-to-website.png'),palette,0,duration)
 windows=[(s,min(s+15000,duration)) for s in range(10000,duration-14999,60000)]
 if not windows:windows=[(0,min(duration,15000))]
 for start,end in windows:x.add_effect('Projector',0,'Pictures',common+',E_TEXTCTRL_Pictures_Filename='+str(ASSETS/'projector-website-qr.png'),palette,start,end)
 x.save(str(path));after=signature(path)
 for target in ['Tune To','Projector']:
  assert len(after[target][0])==(1 if target=='Tune To' else len(windows)),(name,target)
  after[target]=after[target][1:]
 # Normalize empty rows/new layers for exact original effect preservation.
 def nonempty(sig):return {k:[layer for layer in v if layer] for k,v in sig.items() if any(v)}
 retained_without={k:(v[1:] if k in ['Tune To','Projector'] else v) for k,v in retained.items()}
 assert nonempty(after)==nonempty(retained_without),(name,'Original effects changed during native save')
 song=dict(sequence=str(path),baseline_xsq=str(baseline),baseline_fseq=str(original.with_suffix('.fseq')),playback_files=item['playback_files'],expected=expected,qr_windows_ms=windows,removed_radio_text=removed,added_rows=added_rows,preserved_other_effects=True,authored_at=stamp())
 record['songs'][name]=song;save()
 checked=x.xl('checkSequence',seq=str(path),promptIssues='false',timeout=600)
 destination=backup/'Native checks'/(name+'.html');destination.parent.mkdir(exist_ok=True);shutil.copy2(checked['output'],destination)
 song.update(native_check=str(destination),native_critical_issues=check_report(destination));save();assert not song['native_critical_issues'],(name,song['native_critical_issues'])
 x.xl('openSequence',seq=str(path),promptIssues='false',timeout=180)
 print('RENDER',index,len(names),name,windows,flush=True)
 authored=signature(path);x.xl('renderAll',highdef='true',timeout=3600);x.save(str(path));assert signature(path)==authored
 result=info(path.with_suffix('.fseq'));assert (result['frames'],result['frame_ms'])==(expected['frames'],expected['frame_ms'])
 song.update(rendered=True,fseq=result,fseq_sha256=digest(path.with_suffix('.fseq')),rendered_at=stamp());save()
 assert api('/api/system/status')['fppd']=='running'
 print('RENDERED',index,len(names),name,result['bytes'],flush=True)
 x.xl('closeSequence',quiet='true',force='false')
record['all_local_renders_complete']=True;record['master_after_render']=api('/api/system/status');save()
print('ALL WEBSITE/QR RENDERS COMPLETE; MASTER RUNNING',flush=True)
