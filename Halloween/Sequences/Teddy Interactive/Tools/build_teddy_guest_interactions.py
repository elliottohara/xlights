"""Build deterministic, seamless guest interactions using native xLights effects."""
from pathlib import Path
import hashlib, json, sys, shutil

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'Tools'))
import xlights_api as x

SONG = ROOT / 'Halloween/Sequences/Teddy Interactive'
MODEL = 'Elliott - EFL Teddy'
WHITE = 'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'

def add(target, layer, effect, settings, start, end, palette=WHITE):
    x.add_effect(target, layer, effect, settings, palette, start, end)

def arms(pose, start, end):
    add(MODEL, 0, 'State', ','.join([
        'E_CHOICE_State_Color=Graduate', 'E_CHOICE_State_Mode=Default',
        'E_CHOICE_State_StateDefinition=arms', 'E_CHOICE_State_State='+pose,
        'E_SLIDER_State_Fade_Time=0']), start, end)

def face(start, end, eyes='Open'):
    add(MODEL, 3, 'Faces', ','.join([
        'E_CHECKBOX_Faces_Outline=1', 'E_CHOICE_Faces_Eyes='+eyes,
        'E_CHOICE_Faces_FaceDefinition=Teddy ', 'E_CHOICE_Faces_Phoneme=rest',
        'E_CHOICE_Faces_UseState=Teddy RedBow']), start, end)

def begin(duration, blinks=()):
    x.xl('closeSequence', quiet='true', force='false')
    x.xl('newSequence', force='true', mediaFile='', durationSecs=duration//1000,
         frameMS=25, view='Faces')
    cursor=0
    for start in blinks:
        face(cursor,start);face(start,start+150,'Closed');cursor=start+150
    face(cursor,duration)

def export(name, duration, event, **details):
    seq=SONG/(name+'.xsq'); eseq=SONG/'Effects'/(name+'.eseq')
    preview=SONG/'Preview'/(name+'.mp4')
    x.save(str(seq))
    x.xl('exportModelWithRender', model=MODEL, filename=str(eseq),
         format='eseqcompressed', highdef='false', timeout=240)
    x.xl('exportModel', model=MODEL, filename=str(preview),
         format='mp4compressed', timeout=240)
    assert eseq.stat().st_size>100
    print(name,eseq.stat().st_size,flush=True)
    return dict(name=name,event=event,duration_ms=duration,
                xsq=str(seq.relative_to(ROOT)),eseq=str(eseq.relative_to(ROOT)),
                preview=str(preview.relative_to(ROOT)),
                sha256=hashlib.sha256(eseq.read_bytes()).hexdigest(),**details)

def wave(side, duration):
    if duration==2000:
        return [(0,250,'arms'),(250,450,side+'mid'),(450,700,side+'up'),
                (700,900,side+'mid'),(900,1150,side+'up'),
                (1150,1350,side+'mid'),(1350,2000,'arms')]
    # Ease through the middle pose, wave three times, lower through the middle.
    return [(0,500,'arms'),(500,850,side+'mid'),(850,1250,side+'up'),
            (1250,1600,side+'mid'),(1600,2000,side+'up'),
            (2000,2350,side+'mid'),(2350,2750,side+'up'),
            (2750,3100,side+'mid'),(3100,5000,'arms')]

def main():
    assert Path(x.xl('getShowFolder')['folder']).resolve()==ROOT/'Halloween'
    try:
        opened=x.xl('getOpenSequence',retries=1)
    except Exception as e:
        import urllib.error
        if not isinstance(e,urllib.error.HTTPError) or e.code!=503:raise
        opened={}
    assert not opened.get('fullseq'), 'The authoring slot is occupied'
    for folder in ['Effects','Preview','Tools']:(SONG/folder).mkdir(exist_ok=True)
    rows=[]
    begin(8000,[2500,6000]);arms('arms',0,8000)
    rows.append(export('Teddy Default',8000,'idle',loop=True,
                       description='Brown Teddy, red bow, resting mouth, arms down and two gentle blinks.'))
    for event,name,side,duration,blinks in [('wake','Teddy Wake Hello','left',5000,[3500]),
                            ('farewell','Teddy Goodbye','right',2000,[])]:
        begin(duration,blinks)
        for start,end,pose in wave(side,duration):arms(pose,start,end)
        rows.append(export(name,duration,event,loop=False,arm=side,
                           return_to='Teddy Default',neutral_hold_ms=250 if event=='farewell' else 500))
    begin(6000,[2500]);arms('arms',0,6000)
    # Overlays live only on the existing Bow Tie submodel. Fade them into and
    # out of the exact shaded red bow used by the default pose.
    transition='T_TEXTCTRL_Fadein=.5,T_TEXTCTRL_Fadeout=.5'
    add(MODEL+'/Bow Tie',1,'On',transition,500,5500,
        'C_BUTTON_Palette1=#300000,C_CHECKBOX_Palette1=1')
    settings=','.join([
        'E_CHECKBOX_Marquee_PixelOffsets=1','E_CHECKBOX_Marquee_Reverse=0',
        'E_CHECKBOX_Marquee_WrapX=1','E_CHECKBOX_Marquee_WrapY=1',
        'E_SLIDER_MarqueeXC=0','E_SLIDER_MarqueeYC=0',
        'E_SLIDER_Marquee_Band_Size=2','E_SLIDER_Marquee_Skip_Size=3',
        'E_SLIDER_Marquee_Speed=4','E_SLIDER_Marquee_Stagger=1',
        'E_SLIDER_Marquee_ScaleX=100','E_SLIDER_Marquee_ScaleY=100',
        'E_SLIDER_Marquee_Start=0','E_SLIDER_Marquee_Thickness=100',transition])
    add(MODEL+'/Bow Tie',0,'Marquee',settings,500,5500)
    rows.append(export('Teddy Thinking',6000,'thinking',loop=True,
                       return_to='Teddy Default',neutral_hold_ms=500,
                       description='Moving white marquee over a deep-red bow; default face and arms.'))
    manifest={'schema_version':1,'model':MODEL,'start_channel':214643,
              'channels':1500,'frame_ms':25,'default_effect':'Teddy Default',
              'default_background_alias':'Teddy Hold Down',
              'persistent_background_effect':'Teddy Interactive Idle',
              'background_eseq':str((SONG/'Effects/Teddy Interactive Idle.eseq').relative_to(ROOT)),
              'events':{r['event']:r['name'] for r in rows},'effects':rows}
    (SONG/'Tools/guest-interactions.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Preserve the historical Hold Down filename for compatibility; its old
    # button worker remains retired and does not own the persistent idle loop.
    alias=SONG/'Effects/Teddy Hold Down.eseq'
    shutil.copy2(SONG/'Effects/Teddy Default.eseq',alias)
    # Keep the native boot alias for compatibility. The dedicated idle name
    # survives the show's existing multisync Effect Stop(background) commands.
    shutil.copy2(SONG/'Effects/Teddy Default.eseq',SONG/'Effects/background.eseq')
    shutil.copy2(SONG/'Effects/Teddy Default.eseq',SONG/'Effects/Teddy Interactive Idle.eseq')
    library=SONG/'Tools/library.json'
    if library.exists():
        entries=json.loads(library.read_text())
        for row in entries:
            if row['name']=='Teddy Hold Down':
                row.update(duration_ms=8000,bytes=alias.stat().st_size,
                           xsq=rows[0]['xsq'],exported_from='Teddy Default',
                           sha256=rows[0]['sha256'])
        library.write_text(json.dumps(entries,indent=2)+'\n')
    x.xl('closeSequence',quiet='true')
    print('COMPLETE',flush=True)

if __name__=='__main__':main()
