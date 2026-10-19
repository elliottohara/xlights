#!/usr/bin/env python3
"""Build the talking-bear calibration in a free permanent xLights work slot."""
import argparse,json,sys,urllib.error
from pathlib import Path
root=Path(__file__).resolve().parents[4]
import os
if root.name == 'slot-b': os.environ['XLIGHTS_API_PORT']='49914'
sys.path.insert(0,str(root/'Tools'))
import xlights_api as x
show=root/'Halloween';song=show/'Sequences/Teddy Interactive'
assert Path(x.xl('getShowFolder')['folder']).resolve()==show.resolve(), 'Wrong show folder'
try:
 opened=x.xl('getOpenSequence')
except urllib.error.HTTPError as error:
 assert error.code == 503 and json.loads(error.read()).get('msg') == 'Sequence not open.', 'Unexpected xLights error'
 opened={}
assert not opened.get('seq') and not opened.get('fullseq'), 'Slot is occupied; do not close another task'
model='Elliott - EFL Teddy';palette='C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'
x.xl('newSequence',force='true',mediaFile='',durationSecs=10,frameMS=25,view='Faces')
x.add_effect(model,0,'State','E_CHOICE_State_Color=Graduate,E_CHOICE_State_Mode=Default,E_CHOICE_State_StateDefinition=arms,E_CHOICE_State_State=arms,E_SLIDER_State_Fade_Time=0',palette,0,10000)
for n,shape in enumerate(['rest','AI','E','etc','FV','L','MBP','O','U','WQ']):
 settings=','.join(['E_CHECKBOX_Faces_Outline=1','E_CHOICE_Faces_Eyes=Open','E_CHOICE_Faces_FaceDefinition=Teddy ','E_CHOICE_Faces_Phoneme='+shape,'E_CHOICE_Faces_UseState=Teddy RedBow'])
 x.add_effect(model,3,'Faces',settings,palette,n*1000,(n+1)*1000)
seq=song/'Teddy Speech Calibration.xsq';effect=song/'Effects/bear-calibration.eseq';effect.parent.mkdir(exist_ok=True)
x.save(str(seq));x.xl('exportModelWithRender',model=model,filename=str(effect),format='eseqcompressed',highdef='false',timeout=240)
assert effect.exists() and effect.stat().st_size>100
print(json.dumps({'sequence':str(seq),'effect':str(effect),'expected':{'channels':1500,'sparse_start':214642,'frames':400,'frame_ms':25}}))
x.xl('closeSequence',quiet='true')
