"""Keep a fixed readable QR on Tune To and restore the projector to song visuals.

Native xLights authoring/rendering only. FPP Master is read-only and stays running.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import urlopen
import copy, hashlib, html, json, re, shutil, struct, sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]; SHOW=ROOT/'Halloween'
sys.path.insert(0,str(ROOT/'Tools'));sys.path.insert(0,str(SHOW/'Tools'))
import xlights_api as x
x.BASE='http://127.0.0.1:49914/xlDoAutomation'
from single_show_fseq import FSEQ,projector_file
REPORT=SHOW/'projector-sign-refresh-latest.json'
ASSETS=SHOW/'WebsitePromotion/TuneToReadable-v2'

def stamp():return datetime.now(ZoneInfo('America/Chicago')).isoformat()
def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def master(path='/api/system/status'):
    return json.load(urlopen('http://192.168.0.19'+path,timeout=30))
def save(r):REPORT.write_text(json.dumps(r,indent=2)+'\n')
def cfg(text):return dict(t.split('=',1) for t in (text or '').split(',') if '=' in t)
def packed(d):return ','.join(k+'='+str(v) for k,v in d.items())

def signature(path):
    r=ET.parse(path).getroot();db=[e.text or '' for e in r.find('EffectDB')];pal=[e.text or '' for e in r.find('ColorPalettes')]
    result={}
    def settings(text):
        out=cfg(text)
        for k,v in list(out.items()):
            if not v:out.pop(k);continue
            out[k]=html.unescape(v).replace(str(SHOW)+'/', '')
        if out.get('B_CHOICE_PerPreviewCamera')=='2D':out.pop('B_CHOICE_PerPreviewCamera')
        return tuple(sorted(out.items()))
    for el in r.find('ElementEffects'):
        layers=[]
        for layer in el.findall('EffectLayer'):
            out=[]
            for e in layer:
                attrs=tuple(sorted((k,v) for k,v in e.attrib.items() if k not in ['ref','palette','id','selected']))
                out.append((attrs,settings(db[int(e.get('ref'))]),settings(pal[int(e.get('palette'))])) if e.get('ref') is not None else attrs)
            layers.append(out)
        if any(layers) or el.get('type')=='timing':result[el.get('name')]=layers
    return result

def effects(r,name):
    db=[e.text or '' for e in r.find('EffectDB')];pal=[e.text or '' for e in r.find('ColorPalettes')]
    el=next((e for e in r.find('ElementEffects') if e.get('name')==name),None)
    if el is None:return []
    return [dict(target='Projector',layer=i,effect=e.get('name'),startTime=int(e.get('startTime')),endTime=int(e.get('endTime')),settings=db[int(e.get('ref'))],palette=pal[int(e.get('palette'))])
            for i,layer in enumerate(el.findall('EffectLayer')) for e in layer]

def titanium_visuals(r):
    result=[]
    note_plan=json.loads((SHOW/'titanium-opening-flakes-tombstones-latest.json').read_text())
    layer_ends=[0,0]
    for note in note_plan['note_assignments']:
        n=note['target'];start=note['start_ms'];end=note['end_ms']
        source=next(e for e in note_plan['additions'] if e['target']==n and e['layer']==0 and e['startTime']==start and e['endTime']==end)
        d=cfg(source['settings']);is_flake=n in note_plan['flakes'];bank=note_plan['flakes'] if is_flake else note_plan['tombstones']
        d.update(E_CHECKBOX_Shockwave_Scale='1',E_SLIDER_Shockwave_CenterX=str(round(15+70*bank.index(n)/max(1,len(bank)-1))),E_SLIDER_Shockwave_CenterY='65' if is_flake else '25',E_SLIDER_Shockwave_End_Radius='110',E_SLIDER_Shockwave_Start_Width='4',E_SLIDER_Shockwave_End_Width='10',T_TEXTCTRL_Fadeout='0.1')
        layer=next(i for i,last in enumerate(layer_ends) if last<=start);layer_ends[layer]=end
        result.append(dict(target='Projector',layer=layer,effect='Shockwave',startTime=start,endTime=end,settings=packed(d),palette=source['palette']))
    for e in effects(r,'Matrix-Garage Window'):
        d=cfg(e['settings']);d.update(E_CHECKBOX_Shockwave_Scale='1',E_SLIDER_Shockwave_End_Radius='145',E_SLIDER_Shockwave_Start_Width='3',E_SLIDER_Shockwave_End_Width='8')
        d.pop('B_CHOICE_BufferStyle',None);e['settings']=packed(d);result.append(e)
    for e in effects(r,'Whole Scene w Matrixes [01-Abracadabra]'):
        if e['effect']=='On':continue # The source's masking fills depend on another model's stack.
        e['layer']+=4;d=cfg(e['settings']);d.pop('B_CHOICE_BufferStyle',None);d['T_CHOICE_LayerMethod']='Normal';e['settings']=packed(d);result.append(e)
    shaders=effects(r,'Titanium - Whole Scene with Snowflakes');cursor=0
    calm=next(e for e in shaders if 'Vortex V2.fs' in e['settings'])
    for e in sorted(shaders,key=lambda e:e['startTime']):
        if cursor<e['startTime']:result.append(calm_visual(calm,cursor,e['startTime']))
        e['layer']=8;d=cfg(e['settings']);d.pop('T_CHECKBOX_Canvas',None);d['T_CHOICE_LayerMethod']='Normal';e['settings']=packed(d);result.append(e);cursor=e['endTime']
    if cursor<245050:result.append(calm_visual(calm,cursor,245050))
    return result

def calm_visual(source,start,end):
    d=cfg(source['settings'])
    for k in list(d):
        if k.startswith('T_') or k=='E_VALUECURVE_Shader_Speed':d.pop(k)
    d.update(E_SLIDER_Shader_Speed='15',E_SLIDER_SHADERXYZZY_ColorG='5',E_SLIDER_SHADERXYZZY_ColorB='100',T_TEXTCTRL_Fadein='0.5',T_TEXTCTRL_Fadeout='2' if end==245050 else '0.5',T_CHOICE_LayerMethod='Normal')
    return dict(target='Projector',layer=8,effect='Shader',settings=packed(d),palette='C_BUTTON_Palette1=#1554CC,C_CHECKBOX_Palette1=1,C_SLIDER_Brightness=20',startTime=start,endTime=end)

def new_visuals(name,r):
    if name in ['Titanium','Titanium 2']:return titanium_visuals(r)
    if name=='01 - Abracadabra':
        result=effects(r,'Matrix - Downstairs Window')
        offset=1+max(e['layer'] for e in result)
        for e in effects(r,'Whole Scene w Matrixes [01-Abracadabra]'):
            e['layer']+=offset;result.append(e)
        return result
    return []

def critical_check(path):
    t=Path(path).read_text();a=t.index('id="section-sequence"');z=t.find('id="section-',a+20);t=t[a:z if z>=0 else None];issues={}
    for title,ok in [('Models Not Found in Layout','No missing model issues found'),('Impossible Effect Overlaps','No impossible effect overlaps found'),('Effects Extending Beyond Sequence End','No effects extending beyond sequence end found')]:
        m=re.search(r'<h3[^>]*>\s*'+title+r'\s*</h3>(.*?)(?=<h3|$)',t,re.S)
        if not m or ok not in m.group(1):issues[title]=re.sub('<[^>]+>',' ',m.group(1))[:600] if m else 'missing'
    return issues

def prepare():
    assert x.xl('getShowFolder',timeout=15)['folder']==str(SHOW)
    opened=x.xl('getOpenSequence',timeout=15);x.xl('saveSequence',seq=opened['fullseq'],timeout=180)
    prior=json.loads(Path('/tmp/titanium-projector-sign-task.json').read_text())
    backup=Path(prior['backup']);manifest=json.loads((SHOW/'current-show.json').read_text())
    record=dict(started_at=stamp(),backup=str(backup),policy='Stationary QR exclusively on Tune To throughout every sequence; projector carries only show visuals',original_open=opened['fullseq'],layout_sha256=digest(SHOW/'xlights_rgbeffects.xml'),network_sha256=digest(SHOW/'xlights_networks.xml'),songs={},complete=False,deployed=False)
    record['master_before']=master();assert record['master_before']['fppd']=='running'
    for endpoint,file in [('/api/schedule','master-schedule'),('/api/playlist/Halloween%202026','master-playlist'),('/api/playlist/Halloween%20Overnight','master-overnight'),('/api/channel/output/universeOutputs','master-routing')]:
        (backup/(file+'.json')).write_text(json.dumps(master(endpoint),indent=2)+'\n')
    shutil.copy2(SHOW/'current-show.json',backup/'current-show-before.json')
    save(record)
    for name,item in manifest['songs'].items():
        seq=SHOW/item['sequence'];before=backup/'Before'/item['sequence'];before.parent.mkdir(parents=True,exist_ok=True)
        for p in [seq,seq.with_suffix('.fseq'),seq.parent/'AGENT NOTES.md']:
            shutil.copy2(p,before.parent/p.name)
        r=ET.parse(seq).getroot();db=[e.text or '' for e in r.find('EffectDB')]
        votes=[];removed=[]
        for el in r.find('ElementEffects'):
            for li,layer in enumerate(el.findall('EffectLayer')):
                for e in layer:
                    if e.get('ref') is None:continue
                    text=db[int(e.get('ref'))]
                    if el.get('name')=='Tune To' and 'occasional-voting.gif' in text:votes.append([int(e.get('startTime')),int(e.get('endTime'))])
                    if 'projector-website-qr.png' in text:removed.append(dict(target=el.get('name'),layer=li,attributes=e.attrib))
        assert removed,(name,'No old projector QR found')
        visuals=new_visuals(name,r)
        if visuals:assert all(e['endTime']>e['startTime'] for e in visuals)
        record['songs'][name]=dict(sequence=str(seq),before=str(before),baseline_fseq=str(before.with_suffix('.fseq')),playback_files=item['playback_files'],votes=votes,removed_projector_qr=removed,new_visuals=visuals,authored=False,rendered=False)
        save(record)
    print('BACKED UP',len(record['songs']),'sequences and full prior renders',flush=True)

def author(name,item,record):
    seq=Path(item['sequence']);x.xl('closeSequence',quiet='true',force='false',timeout=30)
    before=signature(seq);tree=ET.parse(seq);r=tree.getroot();db=[e.text or '' for e in r.find('EffectDB')];els=r.find('ElementEffects')
    for el in els:
        for layer in el.findall('EffectLayer'):
            for e in list(layer):
                if e.get('ref') is not None and 'projector-website-qr.png' in db[int(e.get('ref'))]:layer.remove(e)
    target=next(e for e in els if e.get('name')=='Tune To')
    for layer in list(target):target.remove(layer)
    ET.SubElement(target,'EffectLayer');ET.SubElement(target,'EffectLayer')
    if item['new_visuals']:
        target=next(e for e in els if e.get('name')=='Projector')
        assert not list(target.iter('Effect')),(name,'Unrelated original projector effects would be removed')
        for layer in list(target):target.remove(layer)
        for _ in range(1+max(e['layer'] for e in item['new_visuals'])):ET.SubElement(target,'EffectLayer')
    ET.indent(tree,space='  ');tree.write(seq,encoding='UTF-8',xml_declaration=True)
    retained=signature(seq);opened=x.xl('openSequence',seq=str(seq),promptIssues='false',timeout=180);assert opened['fullseq']==str(seq)
    duration=int(opened['len'])//int(opened['framems'])*int(opened['framems'])
    common='E_CHECKBOX_LoopGIF=0,E_CHECKBOX_Pictures_PixelOffsets=0,E_CHECKBOX_Pictures_Shimmer=0,E_CHECKBOX_Pictures_TransparentBlack=0,E_CHECKBOX_Pictures_WrapX=0,E_CHECKBOX_SuppressGIFBackground=0,E_CHOICE_Pictures_Direction=none,E_CHOICE_Scaling=Scale To Fit,E_SLIDER_PicturesXC=0,E_SLIDER_PicturesYC=0,E_SLIDER_Pictures_EndScale=100,E_SLIDER_Pictures_StartScale=100,T_CHOICE_LayerMethod=Normal,T_TEXTCTRL_Fadein=0,T_TEXTCTRL_Fadeout=0'
    palette='C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'
    x.xl('addEffect',target='Tune To',effect='Pictures',layer=1,startTime=0,endTime=duration,settings=common+',E_TEXTCTRL_Pictures_Filename='+str(ASSETS/'stationary-qr.png'),palette=palette,timeout=30)
    for a,b in item['votes']:
        x.xl('addEffect',target='Tune To',effect='Pictures',layer=0,startTime=a,endTime=b,settings=common+',E_TEXTCTRL_Pictures_Filename='+str(ASSETS/'stationary-vote.png'),palette=palette,timeout=30)
    for e in item['new_visuals']:x.xl('addEffect',timeout=30,**e)
    x.xl('saveSequence',seq=str(seq),timeout=180)
    after=signature(seq);after.pop('Tune To');retained.pop('Tune To',None)
    if item['new_visuals']:after.pop('Projector');retained.pop('Projector',None)
    assert after==retained,(name,'Unrelated effects changed')
    assert digest(SHOW/'xlights_rgbeffects.xml')==record['layout_sha256']
    assert digest(SHOW/'xlights_networks.xml')==record['network_sha256']
    item.update(authored=True,duration_ms=duration,unrelated_choreography_preserved=True,authored_at=stamp());save(record)

def run():
    record=json.loads(REPORT.read_text());backup=Path(record['backup'])
    names=['Titanium','Titanium 2','01 - Abracadabra']+[n for n in record['songs'] if n not in ['Titanium','Titanium 2','01 - Abracadabra']]
    for i,name in enumerate(names,1):
        item=record['songs'][name]
        if item['rendered']:continue
        assert master()['fppd']=='running'
        if not item['authored']:author(name,item,record)
        seq=Path(item['sequence']);before=signature(seq)
        checked=x.xl('checkSequence',seq=str(seq),promptIssues='false',timeout=600)
        out=backup/'Native checks'/(name+'.html');out.parent.mkdir(exist_ok=True);shutil.copy2(checked['output'],out)
        item['native_check_issues']=critical_check(out);save(record);assert not item['native_check_issues'],(name,item['native_check_issues'])
        opened=x.xl('openSequence',seq=str(seq),promptIssues='false',timeout=180);assert opened['fullseq']==str(seq)
        print('RENDER',i,len(names),name,flush=True)
        x.xl('renderAll',highdef='true',timeout=3600);x.xl('saveSequence',seq=str(seq),timeout=180)
        assert signature(seq)==before,(name,'Authored effects changed while rendering')
        reader=FSEQ(seq.with_suffix('.fseq'));old=FSEQ(item['baseline_fseq']);assert (reader.frames,reader.step)==(old.frames,old.step);reader.f.close();old.f.close()
        sparse=backup/'Projector sparse'/(name+'.fseq');sparse.parent.mkdir(exist_ok=True)
        frames=projector_file(seq.with_suffix('.fseq'),sparse)
        item.update(rendered=True,fseq_sha256=digest(seq.with_suffix('.fseq')),projector_file=str(sparse),projector_sha256=digest(sparse),projector_frames_sha256=frames[0],frames=frames[1],frame_ms=frames[2],rendered_at=stamp());save(record)
        print('VERIFIED',i,len(names),name,flush=True)
    x.xl('closeSequence',quiet='true',force='false',timeout=30)
    x.xl('openSequence',seq=record['original_open'],promptIssues='false',timeout=180)
    record.update(all_local_renders_complete=True,master_after_render=master());assert record['master_after_render']['fppd']=='running';save(record)
    print('ALL 24 SEQUENCES RENDERED; TITANIUM REOPENED; MASTER RUNNING',flush=True)

if __name__=='__main__':
    {'prepare':prepare,'run':run}[sys.argv[1]]()
