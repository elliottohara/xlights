"""Author Teddy's reusable clips through the native xLights API."""
from pathlib import Path
import json, sys, time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'Tools'))
import xlights_api as x

SONG = ROOT / 'Halloween/Sequences/Teddy Interactive'
MODEL = 'Elliott - EFL Teddy'
PALETTE = 'C_BUTTON_Palette1=#FFFFFF,C_CHECKBOX_Palette1=1'

def effect(name, layer, settings, start, end):
    x.add_effect(MODEL, layer, name, settings, PALETTE, start, end)

def state(definition, value, start, end, layer):
    settings = ','.join([
        'E_CHOICE_State_Color=Graduate', 'E_CHOICE_State_Mode=Default',
        'E_CHOICE_State_StateDefinition=' + definition,
        'E_CHOICE_State_State=' + value, 'E_SLIDER_State_Fade_Time=0',
    ])
    effect('State', layer, settings, start, end)

def base(duration, surprised=False):
    effect('Faces', 3, ','.join([
        'E_CHECKBOX_Faces_Outline=1',
        'E_CHOICE_Faces_EyeBlinkFrequency=Normal',
        'E_CHOICE_Faces_Eyes=' + ('Open' if surprised else 'Auto'),
        'E_CHOICE_Faces_FaceDefinition=Teddy ',
        'E_CHOICE_Faces_Phoneme=rest',
        'E_CHOICE_Faces_UseState=Teddy RedBow',
    ]), 0, duration)

def arm(value, start, end):
    state('arms', value, start, end, 0)

def clip(name, duration, arms='down', gesture=None):
    x.xl('closeSequence', force='true', quiet='true')
    x.xl('newSequence', force='true', mediaFile='', durationSecs=duration/1000,
         frameMS=25, view='Faces')
    base(duration, gesture == 'surprised')
    if gesture == 'raise':
        arm('arms', 0, 150); arm('mid', 150, 375); arm('up', 375, duration)
    elif gesture == 'lower':
        arm('up', 0, 150); arm('mid', 150, 375); arm('arms', 375, duration)
    else:
        arm('up' if arms == 'up' else 'arms', 0, duration)
    if gesture in ('left', 'right'):
        state('eye direction', gesture, 125, 1250, 1)
    if gesture == 'surprised':
        state('Brows', 'highbrows', 50, 1350, 2)
    sequence = SONG / (name + '.xsq')
    output = SONG / 'Effects' / (name + '.eseq')
    x.save(str(sequence))
    result = x.xl('exportModelWithRender', model=MODEL, filename=str(output),
                  format='eseqcompressed', highdef='false', timeout=240)
    assert output.exists() and output.stat().st_size > 100, result
    print(name, output.stat().st_size, flush=True)
    return {'name':name,'duration_ms':duration,'arms':arms,'gesture':gesture,
            'xsq':str(sequence.relative_to(ROOT)),
            'eseq':str(output.relative_to(ROOT)),'bytes':output.stat().st_size}

def main():
    assert Path(x.xl('getShowFolder',timeout=10)['folder']).resolve() == (ROOT/'Halloween').resolve(), 'Open this checkout\'s Halloween show before building.'
    (SONG / 'Effects').mkdir(parents=True, exist_ok=True)
    (SONG / 'Preview').mkdir(exist_ok=True)
    (SONG / 'Tools').mkdir(exist_ok=True)
    rows=[]
    rows.append(clip('Teddy Arms Up', 1000, gesture='raise'))
    rows.append(clip('Teddy Arms Down', 1000, gesture='lower'))
    for arms in ['down','up']:
        rows.append(clip('Teddy Hold '+arms.title(), 6000, arms=arms))
        for gesture, label, length in [('left','Look Left',2000),('right','Look Right',2000),('surprised','Surprised',2000)]:
            rows.append(clip('Teddy '+label+' '+arms.title(),length,arms,gesture))
    (SONG / 'Tools/library.json').write_text(json.dumps(rows,indent=2)+'\n')
    x.xl('exportModel',model=MODEL,filename=str(SONG/'Preview/Teddy Surprised Up.mp4'),format='mp4compressed',timeout=240)
    x.xl('closeSequence', force='true', quiet='true')
    print('COMPLETE',len(rows),'native model effect sequences',flush=True)

if __name__ == '__main__': main()
