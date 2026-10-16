"""Refined 30-second Halloween ambient loop, authored through xLights slot A.

--prepare backs up the existing file, removes decorative effects (Tune To and
timings are retained), and exposes the planned elements in the master view.
--build adds the plan through addEffect, saves, and renders. No hardware output.
Reference recipes: approved Holy Forever C1 and locally mapped Xtreme sequences.
"""
from pathlib import Path
import argparse, collections, copy, json, re, runpy, shutil, sys
import xml.etree.ElementTree as ET

SONG = Path(__file__).resolve().parents[1]
ROOT = SONG.parents[2]
sys.path.insert(0, str(ROOT/'Tools'))
import xlights_api as x
XSQ = SONG/'static halloween.xsq'
BACKUP = SONG/'Backups'/'Before ambient refinement 20261016'
END = 30000
REF = ROOT/'Christmas/Sequences/Holy Forever 2026/Tools'
rosa = runpy.run_path(str(REF/'rosa_c1_constant_motion.py'))
star = runpy.run_path(str(REF/'starlord_c1_constant_motion.py'))
reel = runpy.run_path(str(REF/'reelmax_c1_constant_motion.py'))
ORANGE, AMBER, VIOLET, LAVENDER, GREEN = '#FF6508','#FFB34D','#7300FF','#A45AFF','#76C82B'
PLAN=[]

def settings(base='', **changes):
    d=dict(v.split('=',1) for v in base.split(',') if '=' in v)
    for k,v in changes.items():
        if v is None: d.pop(k,None)
        else: d[k]=str(v)
    return ','.join(f'{k}={v}' for k,v in d.items())

def pal(*colors, brightness=50):
    return ','.join([f'C_BUTTON_Palette{i}={c},C_CHECKBOX_Palette{i}=1' for i,c in enumerate(colors,1)]+[f'C_SLIDER_Brightness={brightness}'])

def add(target,effect,st='',colors=(ORANGE,),brightness=50,layer=0,start=0,end=END,fade=False):
    if fade: st=settings(st,T_TEXTCTRL_Fadein=1.25,T_TEXTCTRL_Fadeout=1.25)
    PLAN.append(dict(target=target,effect=effect,settings=st,palette=pal(*colors,brightness=brightness),layer=layer,startTime=start,endTime=end))

def on(target,color,brightness,layer=0): add(target,'On','',(color,),brightness,layer)

def recipe(target,effect,base,colors,brightness=45,layer=0,**changes):
    add(target,effect,settings(base,**changes),colors,brightness,layer,fade=True)

MARQUEE='B_CHOICE_BufferStyle=Single Line,E_SLIDER_Marquee_Band_Size=4,E_SLIDER_Marquee_Skip_Size=18,E_SLIDER_Marquee_Speed=1,E_SLIDER_Marquee_Thickness=1,E_SLIDER_Marquee_ScaleX=100,E_SLIDER_Marquee_ScaleY=100'
CHASE='B_CHOICE_BufferStyle=Vertical Per Model/Strand,E_CHECKBOX_Chase_Group_All=0,E_CHOICE_Chase_Type1=Left-Right,E_CHOICE_Fade_Type=From Head,E_CHOICE_SingleStrand_Colors=Palette,E_NOTEBOOK_SSEFFECT_TYPE=Chase,E_SLIDER_Color_Mix1=25,E_SLIDER_Number_Chases=1,E_TEXTCTRL_Chase_Rotations=3'
TWINKLE='E_CHECKBOX_Twinkle_Strobe=0,E_SLIDER_Twinkle_Count=8,E_SLIDER_Twinkle_Steps=100'

# Architecture: a quiet frame with widely spaced warm traveling embers.
add('Roof','Marquee',settings(MARQUEE,T_CHOICE_LayerMethod='1 reveals 2'),(AMBER,),42)
on('Roof',ORANGE,18,layer=1)
on('Verts',VIOLET,24)
on('Garage',ORANGE,22)
on('Windows',AMBER,27)
recipe('Colums','SingleStrand',CHASE,(VIOLET,LAVENDER),38,E_TEXTCTRL_Chase_Rotations=2)
on('Floods GRP',VIOLET,9)
add('Garden Borders','Marquee',settings(MARQUEE,E_SLIDER_Marquee_Band_Size=6,E_SLIDER_Marquee_Skip_Size=20),(ORANGE,VIOLET),35)
for driveway in ['Driveway Left','Driveway Right']:
    add(driveway,'Marquee',settings(MARQUEE,E_SLIDER_Marquee_Band_Size=3,E_SLIDER_Marquee_Skip_Size=30),(VIOLET,),25)

# Yard: fine moving points, with different color roles instead of solid shrubs.
for group,color,b in [('Shrubs',VIOLET,42),('Rose Bush GRP',ORANGE,38),('Lantanas',VIOLET,40)]:
    add(group,'Twinkle',settings(TWINKLE,T_CHOICE_LayerMethod='1 reveals 2'),(color,AMBER),b)
    add(group,'Marquee',settings(MARQUEE,E_SLIDER_Marquee_Band_Size=3,E_SLIDER_Marquee_Skip_Size=16),(color,),18,layer=1)
on('Tombstones',LAVENDER,23)
add('Tree - Oak','Twinkle',settings(TWINKLE,E_SLIDER_Twinkle_Count=5,E_SLIDER_Twinkle_Steps=150),(ORANGE,VIOLET),30)

# Dim, counter-rotating foundations. Each family gets its own shape.
for group,source,key,color,b in [
    ('GE Rosa Grande GRP',rosa,'HERO_PINWHEEL',ORANGE,24),
    ('GE Starlord GRP',star,'WHOLE_PINWHEEL',VIOLET,22),
    ('GE Reel Max GRP',reel,'WHOLE_PINWHEEL',VIOLET,20)]:
    base=source[key]
    recipe(group,'Pinwheel',base,(color,),b,T_CHOICE_LayerMethod='1 reveals 2')
    recipe(group,'Pinwheel',base,(color,),b,layer=1,B_CHOICE_BufferTransform='Flip Horizontal')

# The detailed submodel voices are the dominant spinner layers.
recipe('GE Rosa Grande Torch Long Even GRP','Pinwheel',rosa['TORCH_PINWHEEL'],(ORANGE,),48)
recipe('GE Rosa Grande Feather Long Odd GRP','Spirals',rosa['FEATHER_SPIRALS'],(VIOLET,),46,E_TEXTCTRL_Spirals_Movement=2)
recipe('GE Rosa Grande Spoke GRP','Fan',rosa['SPOKE_FAN'],(AMBER,),25,E_SLIDER_Fan_Revolutions=360)
recipe('GE Rosa Grande Outer Ball GRP','SingleStrand',rosa['BALL_CHASE'],(AMBER,),45,E_TEXTCTRL_Chase_Rotations=3)
recipe('GE Starlord Plunger All GRP','Spirals',star['PLUNGER_SPIRALS'],(VIOLET,LAVENDER),42,E_TEXTCTRL_Spirals_Movement=2)
recipe('GE Starlord Spoke GRP','SingleStrand',star['SPOKE_CHASE'],(ORANGE,),45,E_SLIDER_Number_Chases=1,E_TEXTCTRL_Chase_Rotations=3)
recipe('GE Starlord Cross GRP','SingleStrand',star['CROSS_DRIP'],(AMBER,),28,E_TEXTCTRL_Chase_Rotations=2)
recipe('GE Reel Max Spokes GRP','Spirals',reel['SPOKE_SPIRALS'] if 'SPOKE_SPIRALS' in reel else reel['SPOKES_SPIRALS'],(ORANGE,),40,E_TEXTCTRL_Spirals_Movement=2)
recipe('GE Reel Max Chevrons GRP','SingleStrand',reel['CHEVRON_CHASE'] if 'CHEVRON_CHASE' in reel else reel['CHEVRONS_CHASE'],(ORANGE,),40,E_TEXTCTRL_Chase_Rotations=3)
recipe('GE Reel Max Circles Outer GRP','SingleStrand',reel['CIRCLE_DRIP'] if 'CIRCLE_DRIP' in reel else reel['CIRCLES_DRIP'],(LAVENDER,),35,E_TEXTCTRL_Chase_Rotations=3)

# Smaller fixtures use their own part banks rather than a shared spinner wash.
recipe('GE Baby Grand Illusion Hook CW GRP','Fan',rosa['SPOKE_FAN'],(ORANGE,),42,B_CHOICE_BufferStyle='Per Model Per Preview',B_CHOICE_PerPreviewCamera='2D',E_SLIDER_Fan_End_Radius=60,E_SLIDER_Fan_Revolutions=360)
recipe('GE Baby Grand Illusion Spokes GRP','Spirals',star['PLUNGER_SPIRALS'],(VIOLET,),40,E_SLIDER_Spirals_Thickness=35,E_TEXTCTRL_Spirals_Movement=2)
recipe('GE MOAW Spokes GRP','SingleStrand',CHASE,(ORANGE,AMBER),40,B_CHOICE_BufferStyle='Single Line',E_CHECKBOX_Chase_Group_All=1,E_CHOICE_Chase_Type1='Bounce from Left',E_SLIDER_Color_Mix1=28,E_TEXTCTRL_Chase_Rotations=2)
add('GE MOAW Diamonds GRP','Color Wash','B_CHOICE_BufferStyle=Single Line,E_CHECKBOX_ColorWash_HFade=1,E_CHECKBOX_ColorWash_VFade=0,E_TEXTCTRL_ColorWash_Cycles=2',(VIOLET,LAVENDER),30,fade=True)
add('GE MOAW Swag GRP','Bars','B_CHOICE_BufferStyle=Overlay - Scaled,E_CHECKBOX_Bars_3D=1,E_CHOICE_Bars_Direction=Right,E_SLIDER_Bars_BarCount=3,E_TEXTCTRL_Bars_Cycles=2',(VIOLET,),30,fade=True)

# Halloween-specific parts: readable spiders, warm eyes, slower bat wing motion.
on('GE Preying Spider Body GRP',VIOLET,35)
recipe('GE Preying Spider 150 Leg GRP','SingleStrand',CHASE,(ORANGE,),45,E_TEXTCTRL_Chase_Rotations=2)
on('GE Preying Spider Eye GRP',AMBER,65)
on('GE Preying Spider 150 Mouth GRP',AMBER,35)
on('GE Flying Bats Jr Eyes GRP',AMBER,65)
for t in range(0,END,4000):
    for target,offset in [('GE Flying Bats Wings Up GRP',0),('GE Flying Bats Wings Down GRP',2000)]:
        a=t+offset
        if a<END: add(target,'On','T_TEXTCTRL_Fadein=.6,T_TEXTCTRL_Fadeout=.6',(VIOLET,),45,start=a,end=min(a+2000,END))

# Character detail through existing physical submodels and face definitions.
add('GE Evil Clown','Faces','E_CHECKBOX_Faces_Outline=1,E_CHOICE_Faces_EyeBlinkFrequency=Slow,E_CHOICE_Faces_Eyes=Auto,E_CHOICE_Faces_FaceDefinition=Evil Clown,E_CHOICE_Faces_Phoneme=rest',('#FFFFFF',),42)
on('GE Evil Clown/Hair',GREEN,40)
add('GE Singing Pumpkin','Faces','E_CHECKBOX_Faces_Outline=1,E_CHOICE_Faces_EyeBlinkFrequency=Slow,E_CHOICE_Faces_Eyes=Auto,E_CHOICE_Faces_FaceDefinition=Pumpkin face,E_CHOICE_Faces_Phoneme=rest,E_CHOICE_Faces_UseState=outline with stem',('#FFFFFF',),55)
on('GE Singing Pumpkin/Stem',GREEN,40)
on('GE Dark Helmet/Helmet Outside',VIOLET,38)
on('GE Dark Helmet/Helmet Inside',VIOLET,22)
on('GE Dark Helmet/Eyes','#FFFFFF',45)
on('GE Dark Helmet/Mouth','#FFFFFF',30)
on('GE Dark Helmet/Nose',VIOLET,25)

# Teddy keeps his hand-authored colors, red bow, and gently blinking resting face.
add('Elliott - EFL Teddy','Faces','E_CHECKBOX_Faces_Outline=1,E_CHOICE_Faces_EyeBlinkFrequency=Slow,E_CHOICE_Faces_Eyes=Auto,E_CHOICE_Faces_FaceDefinition=Teddy ,E_CHOICE_Faces_Phoneme=rest,E_CHOICE_Faces_UseState=Teddy RedBow static',('#FFFFFF',),55)

# Final visual balance after reviewing the rendered house: stronger detail,
# subdued bases, and very low floods for overnight use.
for item in PLAN:
    values=dict(v.split('=',1) for v in item['palette'].split(',') if '=' in v)
    old=int(values['C_SLIDER_Brightness'])
    level=min(90,round(old*1.8))
    if item['target']=='Floods GRP': level=12
    if item['target']=='Roof' and item['layer']==1: level=40
    if item['target']=='Verts': level=55
    if item['target']=='Windows': level=55
    values['C_SLIDER_Brightness']=str(level)
    item['palette']=','.join(f'{k}={v}' for k,v in values.items())

def prepare():
    BACKUP.mkdir(parents=True,exist_ok=True)
    backup=BACKUP/XSQ.name
    if not backup.exists(): shutil.copy2(XSQ,backup)
    tree=ET.parse(backup);root=tree.getroot()
    layout=ET.parse(SONG/'xlights_rgbeffects.xml').getroot()
    models={m.get('name'):m for m in layout.findall('./models/model')}
    groups={m.get('name'):m for m in layout.findall('./modelGroups/modelGroup')}
    for item in PLAN:
        parent,sep,part=item['target'].partition('/')
        assert parent in models or parent in groups,parent
        if sep: assert part in [s.get('name') for s in models[parent].findall('subModel')],item['target']
    de,ee=root.find('DisplayElements'),root.find('ElementEffects')
    for e in list(de):
        if e.get('type')!='timing': de.remove(e)
    utility=copy.deepcopy(ee.find('./Element[@name="Tune To"]'))
    removed=sum(len(list(e.iter('Effect'))) for e in ee if e.get('type')!='timing' and e.get('name')!='Tune To')
    for e in list(ee):
        if e.get('type')!='timing': ee.remove(e)
    targets=list(dict.fromkeys(i['target'].split('/')[0] for i in PLAN))+['Tune To']
    for name in targets:
        ET.SubElement(de,'Element',{'collapsed':'true','type':'model','name':name,'visible':'true'})
        if name=='Tune To': ee.append(utility)
        else:
            el=ET.SubElement(ee,'Element',{'type':'model','name':name})
            ET.SubElement(el,'EffectLayer')
            for part in dict.fromkeys(i['target'].split('/',1)[1] for i in PLAN if i['target'].startswith(name+'/')):
                ET.SubElement(el,'SubModelEffectLayer',{'name':part})
    root.find('lastView').text='0'
    ET.indent(tree,space='  ');tree.write(XSQ,encoding='UTF-8',xml_declaration=True)
    (SONG/'Tools'/'ambient-plan.json').write_text(json.dumps(PLAN,indent=2)+'\n')
    print(f'Backed up original; removed {removed} decorative effects; retained timings and Tune To; prepared {len(PLAN)} effects across {len(targets)} elements.')

def build():
    try: info=x.xl('getOpenSequence',timeout=10,retries=1)
    except Exception: info={}
    if info.get('fullseq'):
        assert Path(info['fullseq'])==XSQ,info
        x.xl('closeSequence',quiet='true')
    x.xl('openSequence',seq=str(XSQ))
    assert x.xl('getOpenSequence')['len']==END
    for n,item in enumerate(PLAN,1):
        x.xl('addEffect',**item)
        if n%20==0:print(f'Added {n}/{len(PLAN)} effects',flush=True)
    x.save(str(XSQ));print('Saved; rendering',flush=True);x.render_all();x.save(str(XSQ));print('Render complete and FSEQ saved',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--build',action='store_true');args=ap.parse_args()
    if args.prepare:prepare()
    if args.build:build()
    if not(args.prepare or args.build):print(json.dumps(PLAN,indent=2))
