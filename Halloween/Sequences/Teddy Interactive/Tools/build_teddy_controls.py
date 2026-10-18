"""Author five-second button routines through the native xLights API."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'Tools'))
import xlights_api as x
SONG=ROOT/'Halloween/Sequences/Teddy Interactive'
MODEL='Elliott - EFL Teddy'
COLORS={'White':'#FFFFFF','Green':'#00FF00','Blue':'#0000FF','Yellow':'#FFFF00','Red':'#FF0000'}
PATTERNS={
 'White':['arms','mid','up','mid'],
 'Green':['arms','leftmid','leftup','leftmid'],
 'Blue':['arms','rightmid','rightup','rightmid'],
 'Yellow':['mid','up'],
 'Red':['leanleft','leanright'],
}

def palette(color):return 'C_BUTTON_Palette1='+color+',C_CHECKBOX_Palette1=1'
def effect(target,name,layer,settings,start,end,color='#FFFFFF'):
 x.add_effect(target,layer,name,settings,palette(color),start,end)
def state(definition,value,start,end,layer=0):
 effect(MODEL,'State',layer,','.join(['E_CHOICE_State_Color=Graduate','E_CHOICE_State_Mode=Default',
  'E_CHOICE_State_StateDefinition='+definition,'E_CHOICE_State_State='+value,'E_SLIDER_State_Fade_Time=0']),start,end)
def base(duration):
 effect(MODEL,'Faces',3,','.join(['E_CHECKBOX_Faces_Outline=1','E_CHOICE_Faces_EyeBlinkFrequency=Normal',
  'E_CHOICE_Faces_Eyes=Auto','E_CHOICE_Faces_FaceDefinition=Teddy ',
  'E_CHOICE_Faces_Phoneme=rest','E_CHOICE_Faces_UseState=Teddy RedBow']),0,duration)
def new(duration):
 x.xl('closeSequence',force='true',quiet='true')
 x.xl('newSequence',force='true',mediaFile='',durationSecs=duration//1000,frameMS=25,view='Faces')
 base(duration)
def export(name,duration,**details):
 sequence=SONG/(name+'.xsq');output=SONG/'Effects'/(name+'.eseq')
 x.save(str(sequence))
 result=x.xl('exportModelWithRender',model=MODEL,filename=str(output),format='eseqcompressed',highdef='false',timeout=240)
 assert output.exists() and output.stat().st_size>100,result
 x.xl('exportModel',model=MODEL,filename=str(SONG/'Preview'/(name+'.mp4')),format='mp4compressed',timeout=240)
 print(name,output.stat().st_size,flush=True)
 return dict(name=name,duration_ms=duration,xsq=str(sequence.relative_to(ROOT)),eseq=str(output.relative_to(ROOT)),bytes=output.stat().st_size,**details)
def main():
 assert Path(x.xl('getShowFolder',timeout=10)['folder']).resolve()==(ROOT/'Halloween').resolve()
 for folder in ['Effects','Preview','Tools']:(SONG/folder).mkdir(parents=True,exist_ok=True)
 rows=[]
 for color,pattern in PATTERNS.items():
  new(5000)
  # Quarter-second poses make the movement repeat clearly for the full routine.
  for i,start in enumerate(range(0,5000,250)):state('arms',pattern[i%len(pattern)],start,start+250)
  if color=='White':
   effect(MODEL+'/Bow Tie','On',1,'',0,5000,'#101010')
   settings=','.join(['E_CHECKBOX_Marquee_PixelOffsets=1','E_CHECKBOX_Marquee_Reverse=0',
    'E_CHECKBOX_Marquee_WrapX=1','E_CHECKBOX_Marquee_WrapY=1',
    'E_SLIDER_MarqueeXC=0','E_SLIDER_MarqueeYC=0','E_SLIDER_Marquee_Band_Size=2',
    'E_SLIDER_Marquee_Skip_Size=3','E_SLIDER_Marquee_Speed=4','E_SLIDER_Marquee_Stagger=1',
    'E_SLIDER_Marquee_ScaleX=100','E_SLIDER_Marquee_ScaleY=100',
    'E_SLIDER_Marquee_Start=0','E_SLIDER_Marquee_Thickness=100'])
   effect(MODEL+'/Bow Tie','Marquee',0,settings,0,5000)
  else:effect(MODEL+'/Bow Tie','On',0,'',0,5000,COLORS[color])
  if color=='Red':state('Brows','highbrows',0,5000,2)
  rows.append(export('Teddy '+color+' Routine',5000,button=color.lower(),arm_pattern=pattern,scarf='white marquee' if color=='White' else COLORS[color]))
 # Neutral idle poses remain available for a quiet station outside show playback.
 for pose,value in [('Down','arms'),('Up','up')]:
  new(6000);state('arms',value,0,6000)
  rows.append(export('Teddy Hold '+pose,6000,arms=pose.lower()))
 (SONG/'Tools/library.json').write_text(json.dumps(rows,indent=2)+'\n')
 x.xl('closeSequence',force='true',quiet='true')
 print('COMPLETE',len(rows),'native model effect sequences',flush=True)
if __name__=='__main__':main()
