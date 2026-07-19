#!/usr/bin/env python3
"""Build "Holy Forever 2026" through the xLights automation API.

The Chris Tomlin lyric video is both the sequence media and a full-length Video
effect on the Projector model. Choreography follows the video's royal-blue,
navy, cyan, charcoal, and warm-white visual language.
"""
from collections import Counter, defaultdict
import math
import sys

sys.path.insert(0, '/Users/elliott.ohara/xlights/Tools')
import xlights_api as x


SHOW = '/Users/elliott.ohara/xlights/Christmas'
MEDIA = '/Users/elliott.ohara/xlights/Christmas/Sequences/Holy Forever 2026/Media/Chris Tomlin - Holy Forever (Lyric Video).mp4'
OUT = f'{SHOW}/Sequences/Holy Forever 2026/Holy Forever 2026.xsq'

x.launch(SHOW)
info = x.new_sequence(MEDIA, frame_ms=25)
DUR = int(info['len'])
END_CAP = DUR - 50


# ---- song map, transcribed from the lyric-video changes -----------------------
INTRO = (0, 15520)
VERSE_1 = (15520, 41850)
PRE_1 = (41850, 67570)
CHORUS_1 = (67570, 95100)
VERSE_2 = (95100, 127630)
CHORUS_1B = (127630, 154150)
CHORUS_2 = (154150, 181900)
PRE_2 = (181900, 207210)
PRE_3 = (207210, 234230)
CHORUS_1C = (234230, 260760)
CHORUS_2B = (260760, 287290)
TAG = (287290, 301500)
OUTRO = (301500, END_CAP)

# 72 BPM in 4/4. The 180 ms phase follows the recurring drum transients.
BEAT_MS = 60000.0 / 72.0
BEAT_PHASE = 180.0


def beats_in(a, b):
    first = math.ceil((a - BEAT_PHASE) / BEAT_MS)
    out = []
    n = first
    while True:
        s = int(round(BEAT_PHASE + n * BEAT_MS))
        if s >= b:
            break
        if s >= a:
            out.append((s, min(int(round(s + BEAT_MS)), b), n % 4))
        n += 1
    return out


def bars_in(a, b):
    return [(s, e) for s, e, pos in beats_in(a, b) if pos == 0]


# ---- palettes sampled from the lyric video -----------------------------------
BASE = {
    1: '#EEEAE2',  # warm ivory lyric text
    2: '#075FCC',  # dominant royal blue
    3: '#13A8FF',  # electric cyan accents
    4: '#031C38',  # deep navy brushwork
    5: '#143A5A',  # blue slate
    6: '#000000',
    7: '#FFFFFF',
    8: '#7258B7',  # restrained violet undertone
}
palettes, pidx = [], {}


def P(*slots, brightness=None):
    values = [f'C_BUTTON_Palette{i}={BASE[i]}' for i in range(1, 9)]
    values += [f'C_CHECKBOX_Palette{i}=1' for i in sorted(slots)]
    if brightness is not None:
        values.append(f'C_SLIDER_Brightness={brightness}')
    value = ','.join(values)
    if value not in pidx:
        pidx[value] = len(palettes)
        palettes.append(value)
    return pidx[value]


def PWIND(*slots, music=False, gradient_slot=None):
    values = [f'C_BUTTON_Palette{i}={BASE[i]}' for i in range(1, 9)]
    if gradient_slot is not None:
        values[gradient_slot - 1] = (
            f'C_BUTTON_Palette{gradient_slot}=Active=TRUE|'
            f'Id=ID_BUTTON_Palette{gradient_slot}|'
            'Values=x=0.150^c=#13a8ff;x=0.475^c=#075fcc;'
            'x=0.825^c=#13a8ff|'
        )
    if music:
        values.append('C_CHECKBOX_MusicSparkles=1')
    values += [f'C_CHECKBOX_Palette{i}=1' for i in sorted(slots)]
    value = ','.join(values)
    if value not in pidx:
        pidx[value] = len(palettes)
        palettes.append(value)
    return pidx[value]


IVORY = P(1)
BLUE = P(2)
CYAN = P(3)
NAVY = P(4)
SLATE = P(5)
WHITE = P(7)
VIOLET = P(8)
BLUE_IVORY = P(1, 2)
BLUE_CYAN = P(2, 3)
CYAN_IVORY = P(1, 3)
NAVY_BLUE = P(2, 4)
BLUE_SLATE = P(2, 5)
TRICOLOR = P(1, 2, 3)
BLUE_VIOLET = P(2, 8)
NAVY_DIM = P(4, brightness=28)
BLUE_DIM = P(2, brightness=38)
SLATE_DIM = P(5, brightness=32)
IVORY_DIM = P(1, brightness=48)
WIND_SHADER_PALETTE = VIOLET
WIND_UNMASK_PALETTE = PWIND(8, music=True)
WIND_GLOW_PALETTE = PWIND(2, music=True, gradient_slot=2)
WIND_PIN_PALETTE = PWIND(8, music=True)
WIND_MUSIC_PALETTE = PWIND(2, 3, music=True)


# ---- effect settings ----------------------------------------------------------
effdb, eidx = [], {}


def E(settings):
    if settings not in eidx:
        eidx[settings] = len(effdb)
        effdb.append(settings)
    return eidx[settings]


ON_PULSE = E('T_TEXTCTRL_Fadeout=.28')
ON_SOFT = E('T_TEXTCTRL_Fadein=.35,T_TEXTCTRL_Fadeout=.45')
ON_SHIMMER = E('E_CHECKBOX_On_Shimmer=1,T_TEXTCTRL_Fadeout=.35')
ON_HOLY = E('E_CHECKBOX_On_Shimmer=1,T_TEXTCTRL_Fadein=.08,T_TEXTCTRL_Fadeout=.75')
ON_LONG_FADE = E('E_CHECKBOX_On_Shimmer=1,T_TEXTCTRL_Fadeout=5')

TWINKLE_SOFT = E(
    'E_CHECKBOX_Twinkle_ReRandom=0,E_CHECKBOX_Twinkle_Strobe=0,'
    'E_CHOICE_Twinkle_Style=New Render Method,E_SLIDER_Twinkle_Count=18,'
    'E_SLIDER_Twinkle_Steps=40,T_TEXTCTRL_Fadein=.6,T_TEXTCTRL_Fadeout=.7'
)
TWINKLE_BRIGHT = E(
    'E_CHECKBOX_Twinkle_ReRandom=0,E_CHECKBOX_Twinkle_Strobe=0,'
    'E_CHOICE_Twinkle_Style=New Render Method,E_SLIDER_Twinkle_Count=42,'
    'E_SLIDER_Twinkle_Steps=24,T_TEXTCTRL_Fadein=.25,T_TEXTCTRL_Fadeout=.4'
)
TWINKLE_FADE = E(
    'E_CHECKBOX_Twinkle_ReRandom=0,E_CHECKBOX_Twinkle_Strobe=0,'
    'E_CHOICE_Twinkle_Style=New Render Method,E_SLIDER_Twinkle_Count=28,'
    'E_SLIDER_Twinkle_Steps=35,T_TEXTCTRL_Fadeout=5'
)
MARQUEE_SLOW = E(
    'B_CHOICE_BufferStyle=Single Line,E_CHECKBOX_Marquee_PixelOffsets=0,'
    'E_CHECKBOX_Marquee_Reverse=0,E_CHECKBOX_Marquee_WrapX=0,'
    'E_NOTEBOOK_Marquee=Settings,E_SLIDER_MarqueeXC=0,E_SLIDER_MarqueeYC=0,'
    'E_SLIDER_Marquee_Band_Size=4,E_SLIDER_Marquee_ScaleX=100,'
    'E_SLIDER_Marquee_ScaleY=100,E_SLIDER_Marquee_Skip_Size=7,'
    'E_SLIDER_Marquee_Speed=2,E_SLIDER_Marquee_Stagger=0,'
    'E_SLIDER_Marquee_Start=0,E_SLIDER_Marquee_Thickness=3,'
    'T_TEXTCTRL_Fadein=.45,T_TEXTCTRL_Fadeout=.45'
)
MARQUEE_BUILD = E(
    'B_CHOICE_BufferStyle=Single Line,E_CHECKBOX_Marquee_PixelOffsets=0,'
    'E_CHECKBOX_Marquee_Reverse=0,E_CHECKBOX_Marquee_WrapX=0,'
    'E_NOTEBOOK_Marquee=Settings,E_SLIDER_MarqueeXC=0,E_SLIDER_MarqueeYC=0,'
    'E_SLIDER_Marquee_Band_Size=4,E_SLIDER_Marquee_ScaleX=100,'
    'E_SLIDER_Marquee_ScaleY=100,E_SLIDER_Marquee_Skip_Size=4,'
    'E_SLIDER_Marquee_Speed=5,E_SLIDER_Marquee_Stagger=0,'
    'E_SLIDER_Marquee_Start=0,E_SLIDER_Marquee_Thickness=4,'
    'T_TEXTCTRL_Fadein=.25,T_TEXTCTRL_Fadeout=.35'
)
SPIRALS_SLOW = E(
    'E_CHECKBOX_Spirals_3D=1,E_CHECKBOX_Spirals_Blend=0,'
    'E_CHECKBOX_Spirals_Grow=0,E_CHECKBOX_Spirals_Shrink=0,'
    'E_SLIDER_Spirals_Count=3,E_SLIDER_Spirals_Rotation=20,'
    'E_SLIDER_Spirals_Thickness=34,E_TEXTCTRL_Spirals_Movement=2,'
    'T_TEXTCTRL_Fadein=.6,T_TEXTCTRL_Fadeout=.6'
)
SPIRALS_GROUP = E(
    'B_CHOICE_BufferStyle=Horizontal Per Model,E_CHECKBOX_Spirals_3D=1,'
    'E_CHECKBOX_Spirals_Blend=0,E_CHECKBOX_Spirals_Grow=0,'
    'E_CHECKBOX_Spirals_Shrink=0,E_SLIDER_Spirals_Count=3,'
    'E_SLIDER_Spirals_Rotation=20,E_SLIDER_Spirals_Thickness=40,'
    'E_TEXTCTRL_Spirals_Movement=2,T_TEXTCTRL_Fadein=.6,T_TEXTCTRL_Fadeout=.6'
)
PINWHEEL_SLOW = E(
    'E_CHECKBOX_Pinwheel_Rotation=1,E_CHOICE_Pinwheel_3D=None,'
    'E_CHOICE_Pinwheel_Style=New Render Method,E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,E_SLIDER_Pinwheel_ArmSize=100,'
    'E_SLIDER_Pinwheel_Arms=5,E_SLIDER_Pinwheel_Speed=4,'
    'E_SLIDER_Pinwheel_Thickness=18,E_SLIDER_Pinwheel_Twist=0,'
    'T_TEXTCTRL_Fadein=.5,T_TEXTCTRL_Fadeout=.5'
)
WAVE_SLOW = E(
    'B_CHOICE_BufferStyle=Horizontal Per Model,E_CHECKBOX_Mirror_Wave=1,'
    'E_CHOICE_Fill_Colors=None,E_CHOICE_Wave_Direction=Right to Left,'
    'E_CHOICE_Wave_Type=Sine,E_SLIDER_Number_Waves=600,'
    'E_SLIDER_Thickness_Percentage=6,E_SLIDER_Wave_Height=45,'
    'E_SLIDER_Wave_YOffset=0,E_TEXTCTRL_Wave_Speed=5,'
    'T_TEXTCTRL_Fadein=.4,T_TEXTCTRL_Fadeout=.4'
)
WIND_SNOW = E(
    'E_CHOICE_Falling=Driving,E_SLIDER_Snowflakes_Count=97,'
    'E_SLIDER_Snowflakes_Speed=6,E_SLIDER_Snowflakes_Type=1,'
    'T_TEXTCTRL_Fadein=2,T_TEXTCTRL_Fadeout=1'
)
WIND_UNMASK = E(
    'T_CHOICE_LayerMethod=2 is Unmask,T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=1'
)
WIND_SHADER = E(
    'E_0FILEPICKERCTRL_IFS=/Users/elliott.ohara/xlights/'
    'Christmas/Shaders/Black Cherry Cosmos.fs,'
    'E_SLIDER_SHADERXYZZY_mouseX=0,E_SLIDER_SHADERXYZZY_mouseY=0,'
    'E_SLIDER_Shader_Speed=4,E_TEXTCTRL_Shader_LeadIn=0,'
    'E_TEXTCTRL_Shader_Offset_X=0,E_TEXTCTRL_Shader_Offset_Y=0,'
    'E_TEXTCTRL_Shader_Zoom=-68,T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=1'
)
WIND_GLOW = E('B_SLIDER_Blur=2,T_TEXTCTRL_Fadein=3,T_TEXTCTRL_Fadeout=2')
WIND_FLOOD = E('T_TEXTCTRL_Fadein=.5,T_TEXTCTRL_Fadeout=.5')
WIND_PIN_PER_MODEL = E(
    'B_CHOICE_BufferStyle=Per Model Per Preview,B_CHOICE_PerPreviewCamera=2D,'
    'E_CHECKBOX_Pinwheel_Rotation=1,E_CHOICE_Pinwheel_3D=3D Inverted,'
    'E_CHOICE_Pinwheel_Style=New Render Method,E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,E_SLIDER_Pinwheel_ArmSize=145,'
    'E_SLIDER_Pinwheel_Arms=1,E_SLIDER_Pinwheel_Offset=0,'
    'E_SLIDER_Pinwheel_Speed=10,E_SLIDER_Pinwheel_Thickness=100,'
    'E_SLIDER_Pinwheel_Twist=0,T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=.5'
)
WIND_SHOCK_PER_MODEL = E(
    'B_CHOICE_BufferStyle=Per Model Per Preview,B_CHOICE_PerPreviewCamera=2D,'
    'E_CHECKBOX_Shockwave_Blend_Edges=1,E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,E_SLIDER_Shockwave_Accel=7,'
    'E_SLIDER_Shockwave_CenterX=50,E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_End_Radius=96,E_SLIDER_Shockwave_End_Width=45,'
    'E_SLIDER_Shockwave_Start_Radius=1,E_SLIDER_Shockwave_Start_Width=40,'
    'T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=.5'
)
WIND_PIN_OVERLAY = E(
    'B_CHOICE_BufferStyle=Overlay - Centered,E_CHECKBOX_Pinwheel_Rotation=1,'
    'E_CHOICE_Pinwheel_3D=3D Inverted,'
    'E_CHOICE_Pinwheel_Style=New Render Method,E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,E_SLIDER_Pinwheel_ArmSize=145,'
    'E_SLIDER_Pinwheel_Arms=1,E_SLIDER_Pinwheel_Offset=0,'
    'E_SLIDER_Pinwheel_Speed=10,E_SLIDER_Pinwheel_Thickness=100,'
    'E_SLIDER_Pinwheel_Twist=0,T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=.5'
)
WIND_SHOCK_OVERLAY = E(
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Shockwave_Blend_Edges=1,E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,E_SLIDER_Shockwave_Accel=7,'
    'E_SLIDER_Shockwave_CenterX=50,E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_End_Radius=96,E_SLIDER_Shockwave_End_Width=45,'
    'E_SLIDER_Shockwave_Start_Radius=1,E_SLIDER_Shockwave_Start_Width=40,'
    'T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=.5'
)
WIND_SHOCK_MINI = E(
    'B_CHOICE_BufferStyle=Horizontal Per Model,'
    'E_CHECKBOX_Shockwave_Blend_Edges=1,E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,E_SLIDER_Shockwave_Accel=0,'
    'E_SLIDER_Shockwave_CenterX=50,E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_End_Radius=85,E_SLIDER_Shockwave_End_Width=85,'
    'E_SLIDER_Shockwave_Start_Radius=21,E_SLIDER_Shockwave_Start_Width=19,'
    'T_TEXTCTRL_Fadein=.75,T_TEXTCTRL_Fadeout=.5'
)
WIND_SHOCK_WIDE = E(
    'E_CHECKBOX_Shockwave_Blend_Edges=1,E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,E_SLIDER_Shockwave_Accel=0,'
    'E_SLIDER_Shockwave_CenterX=45,E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_End_Radius=116,E_SLIDER_Shockwave_End_Width=97,'
    'E_SLIDER_Shockwave_Start_Radius=40,E_SLIDER_Shockwave_Start_Width=34,'
    'T_TEXTCTRL_Fadein=.75,T_TEXTCTRL_Fadeout=.3'
)
WIND_PIN_PER_PREVIEW = E(
    'B_CHOICE_BufferStyle=Per Preview,B_CHOICE_PerPreviewCamera=2D,'
    'E_CHECKBOX_Pinwheel_Rotation=1,E_CHOICE_Pinwheel_3D=3D Inverted,'
    'E_CHOICE_Pinwheel_Style=New Render Method,E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,E_SLIDER_Pinwheel_ArmSize=145,'
    'E_SLIDER_Pinwheel_Arms=1,E_SLIDER_Pinwheel_Offset=0,'
    'E_SLIDER_Pinwheel_Speed=10,E_SLIDER_Pinwheel_Thickness=100,'
    'E_SLIDER_Pinwheel_Twist=0,T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=.5'
)
WIND_SHOCK_DEFAULT = E(
    'E_CHECKBOX_Shockwave_Blend_Edges=1,E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,E_SLIDER_Shockwave_Accel=7,'
    'E_SLIDER_Shockwave_CenterX=50,E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_End_Radius=96,E_SLIDER_Shockwave_End_Width=45,'
    'E_SLIDER_Shockwave_Start_Radius=1,E_SLIDER_Shockwave_Start_Width=40,'
    'T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=.5'
)
WIND_SHOCK_SMALL = E(
    'E_CHECKBOX_Shockwave_Blend_Edges=1,E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,E_SLIDER_Shockwave_Accel=0,'
    'E_SLIDER_Shockwave_CenterX=50,E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_End_Radius=31,E_SLIDER_Shockwave_End_Width=32,'
    'E_SLIDER_Shockwave_Start_Radius=3,E_SLIDER_Shockwave_Start_Width=6,'
    'T_TEXTCTRL_Fadein=.75,T_TEXTCTRL_Fadeout=.5'
)
WIND_SHOCK_FLAKES = E(
    'B_CHOICE_BufferStyle=Overlay - Centered,'
    'E_CHECKBOX_Shockwave_Blend_Edges=1,E_CHECKBOX_Shockwave_Scale=0,'
    'E_NOTEBOOK_Shockwave=Position,E_SLIDER_Shockwave_Accel=0,'
    'E_SLIDER_Shockwave_CenterX=50,E_SLIDER_Shockwave_CenterY=50,'
    'E_SLIDER_Shockwave_End_Radius=61,E_SLIDER_Shockwave_End_Width=54,'
    'E_SLIDER_Shockwave_Start_Radius=1,E_SLIDER_Shockwave_Start_Width=5,'
    'T_TEXTCTRL_Fadeout=.5'
)
WIND_PIN_DEFAULT = E(
    'E_CHECKBOX_Pinwheel_Rotation=1,E_CHOICE_Pinwheel_3D=3D Inverted,'
    'E_CHOICE_Pinwheel_Style=New Render Method,E_SLIDER_PinwheelXC=0,'
    'E_SLIDER_PinwheelYC=0,E_SLIDER_Pinwheel_ArmSize=145,'
    'E_SLIDER_Pinwheel_Arms=1,E_SLIDER_Pinwheel_Offset=0,'
    'E_SLIDER_Pinwheel_Speed=10,E_SLIDER_Pinwheel_Thickness=100,'
    'E_SLIDER_Pinwheel_Twist=0,T_TEXTCTRL_Fadein=1,T_TEXTCTRL_Fadeout=.5'
)
SNOWFALL = E(
    'E_CHOICE_Falling=Driving,E_SLIDER_Snowflakes_Count=12,'
    'E_SLIDER_Snowflakes_Speed=8,E_SLIDER_Snowflakes_Type=1,'
    'T_TEXTCTRL_Fadein=.5,T_TEXTCTRL_Fadeout=.5'
)
COLOR_WASH = E(
    'B_CHOICE_BufferStyle=Single Line,T_TEXTCTRL_Fadein=.65,T_TEXTCTRL_Fadeout=.65'
)
BARS_EXPAND = E(
    'E_CHECKBOX_Bars_3D=1,E_CHECKBOX_Bars_Gradient=0,'
    'E_CHECKBOX_Bars_Highlight=0,E_CHOICE_Bars_Direction=expand,'
    'E_SLIDER_Bars_BarCount=3,E_SLIDER_Bars_Center=0,'
    'E_TEXTCTRL_Bars_Cycles=0.55,T_TEXTCTRL_Fadeout=.3'
)
FAN = E(
    'B_CHOICE_BufferStyle=Overlay - Centered,E_CHECKBOX_Fan_Blend_Edges=1,'
    'E_CHECKBOX_Fan_Reverse=0,E_CHECKBOX_Fan_Scale=0,E_NOTEBOOK_Fan=Options,'
    'E_SLIDER_Fan_Accel=0,E_SLIDER_Fan_Blade_Angle=90,'
    'E_SLIDER_Fan_Blade_Width=100,E_SLIDER_Fan_CenterX=50,'
    'E_SLIDER_Fan_CenterY=50,E_SLIDER_Fan_Duration=95,'
    'E_SLIDER_Fan_Element_Width=100,E_SLIDER_Fan_End_Radius=60,'
    'E_SLIDER_Fan_Num_Blades=2,E_SLIDER_Fan_Num_Elements=1,'
    'E_SLIDER_Fan_Revolutions=540,E_SLIDER_Fan_Start_Angle=0,'
    'E_SLIDER_Fan_Start_Radius=1'
)
SHOCKWAVE = E(
    'B_CHOICE_BufferStyle=Overlay - Scaled,E_CHECKBOX_Shockwave_Blend_Edges=1,'
    'E_CHECKBOX_Shockwave_Scale=0,E_NOTEBOOK_Shockwave=Position,'
    'E_SLIDER_Shockwave_Accel=0,E_SLIDER_Shockwave_CenterX=50,'
    'E_SLIDER_Shockwave_CenterY=50,E_SLIDER_Shockwave_End_Radius=115,'
    'E_SLIDER_Shockwave_End_Width=35,E_SLIDER_Shockwave_Start_Radius=0,'
    'E_SLIDER_Shockwave_Start_Width=5,T_TEXTCTRL_Fadeout=.45'
)
SHOCKWAVE_TIGHT = E(
    'B_CHOICE_BufferStyle=Overlay - Scaled,E_CHECKBOX_Shockwave_Blend_Edges=1,'
    'E_CHECKBOX_Shockwave_Scale=0,E_NOTEBOOK_Shockwave=Position,'
    'E_SLIDER_Shockwave_Accel=0,E_SLIDER_Shockwave_CenterX=50,'
    'E_SLIDER_Shockwave_CenterY=50,E_SLIDER_Shockwave_End_Radius=38,'
    'E_SLIDER_Shockwave_End_Width=28,E_SLIDER_Shockwave_Start_Radius=1,'
    'E_SLIDER_Shockwave_Start_Width=5,T_TEXTCTRL_Fadeout=.3'
)
GALAXY = E(
    'E_CHECKBOX_Galaxy_Blend_Edges=1,E_CHECKBOX_Galaxy_Inward=0,'
    'E_CHECKBOX_Galaxy_Reverse=0,E_CHECKBOX_Galaxy_Scale=0,'
    'E_NOTEBOOK_Galaxy=Start,E_SLIDER_Galaxy_Accel=0,'
    'E_SLIDER_Galaxy_CenterX=50,E_SLIDER_Galaxy_CenterY=50,'
    'E_SLIDER_Galaxy_Duration=22,E_SLIDER_Galaxy_End_Radius=100,'
    'E_SLIDER_Galaxy_End_Width=8,E_SLIDER_Galaxy_Revolutions=1080,'
    'E_SLIDER_Galaxy_Start_Angle=0,E_SLIDER_Galaxy_Start_Radius=1,'
    'E_SLIDER_Galaxy_Start_Width=5,T_TEXTCTRL_Fadein=.3,T_TEXTCTRL_Fadeout=.5'
)
VIDEO = E(
    'E_CHECKBOX_SynchroniseWithAudio=0,E_CHECKBOX_Video_AspectRatio=0,'
    'E_CHECKBOX_Video_TransparentBlack=0,E_CHOICE_Video_DurationTreatment=Normal,'
    f'E_FILEPICKERCTRL_Video_Filename={MEDIA},E_TEXTCTRL_Duration=5:08.315,'
    'E_TEXTCTRL_Video_CropBottom=0,E_TEXTCTRL_Video_CropLeft=0,'
    'E_TEXTCTRL_Video_CropRight=100,E_TEXTCTRL_Video_CropTop=100,'
    'E_TEXTCTRL_Video_Speed=1.00,E_TEXTCTRL_Video_Starttime=0.00,'
    'E_TEXTCTRL_Video_TransparentBlack=0'
)


# ---- effect placement and overlap validation ---------------------------------
seq = defaultdict(lambda: defaultdict(list))

EXPAND = {
    'EFL Wings': ['EFL Wing - Left', 'EFL Wing - Right'],
    'Large Spiral Trees': [f'Large Spiral Tree - {i:02d}' for i in range(1, 13)],
}


def add(element, layer, effect, ref, start, end, palette):
    start, end = int(start), int(min(end, END_CAP))
    if end <= start:
        return
    for model in EXPAND.get(element, [element]):
        seq[model.strip()][layer].append((ref, effect, start, end, palette))


SPINNERS = [
    'GE Rosa Grande 1', 'GE Reel Max 1', 'GE Reel Max 2',
    'GE Starlord 1', 'GE Starlord 2', 'GE Mini Grand Illusion',
    'GE Flake N 1', 'GE Flake N 2',
]
SPOKE_GROUPS = [
    'GE MOAW Spokes GRP', 'GE Reel Max Spokes GRP',
    'GE Baby Grand Illusion Spokes GRP', 'GE Rosa Grande Spoke GRP',
    'GE Starlord Spoke GRP',
]
RING_GROUPS = [
    'GE Reel Max Chevron Rings GRP', 'GE Baby Grand Illusion Rings GRP',
    'GE Rosa Grande Ring GRP', 'GE MOAW Diamonds GRP',
]
HOLY_BANKS = [
    ['GE Reel Max Arrows GRP', 'GE Starlord Plunger All GRP'],
    ['GE Rosa Grande Web Spoke GRP', 'GE MOAW Snowflake Spoke GRP'],
    ['Flakes Spokes All GRP', 'GE Starlord Star GRP'],
]
SLAM_PROPS = [
    'House Outline', 'Roof', 'Icicles GRP', 'Colums', 'Arches - All',
    'Canes', 'Mini Trees', 'Mini Tree Stars', 'Large Spiral Trees',
    'Mega Tree', 'Tree Topper', 'Tree - Oak', 'Toni - Flat Tree',
    'Flakes GRP', 'EFL Wings', 'Matrixes', 'Column Matrixes',
    'Yard Borders', 'Driveway', 'Colum Shrubs',
] + SPINNERS


def slam(start, duration, palette, props=None):
    for model in props or SLAM_PROPS:
        add(model, 3, 'On', ON_PULSE, start, start + duration, palette)


def section_base(a, b, level):
    """Continuous blue visual bed; density and movement rise with level 1..5."""
    main = [NAVY_BLUE, BLUE_CYAN, TRICOLOR, TRICOLOR, CYAN_IVORY][level - 1]
    accent = [SLATE, BLUE, CYAN, IVORY, WHITE][level - 1]
    dim = [NAVY_DIM, BLUE_DIM, BLUE_DIM, IVORY_DIM, IVORY][level - 1]

    add('House Outline', 0, 'Marquee',
        MARQUEE_SLOW if level <= 2 else MARQUEE_BUILD, a, b, main)
    add('Roof', 0, 'Marquee',
        MARQUEE_SLOW if level <= 2 else MARQUEE_BUILD, a, b, main)
    add('Icicles GRP', 0, 'Twinkle',
        TWINKLE_SOFT if level <= 2 else TWINKLE_BRIGHT, a, b, accent)
    add('Canes', 0, 'Marquee', MARQUEE_SLOW, a, b, BLUE_IVORY)
    add('Colum Shrubs', 0, 'Twinkle',
        TWINKLE_SOFT if level <= 3 else TWINKLE_BRIGHT, a, b, main)
    add('Mega Tree', 0, 'Spirals', SPIRALS_SLOW, a, b, main)
    add('Toni - Flat Tree', 0, 'Spirals', SPIRALS_SLOW, a, b, main)
    add('Large Spiral Trees', 0, 'Spirals', SPIRALS_GROUP, a, b, main)
    add('Tree - Oak', 0, 'Twinkle', TWINKLE_SOFT, a, b, accent)
    add('Yard Borders', 0, 'Wave', WAVE_SLOW, a, b, main)
    add('Driveway', 0, 'Wave', WAVE_SLOW, a, b, accent)
    add('Matrixes', 0, 'Snowflakes', SNOWFALL, a, b, main)
    add('Column Matrixes', 0, 'Bars', BARS_EXPAND, a, b, main)
    add('Floods GRP', 0, 'Color Wash', COLOR_WASH, a, b, dim)
    add('Flakes Outline All GRP', 0, 'Twinkle',
        TWINKLE_SOFT if level <= 3 else TWINKLE_BRIGHT, a, b, accent)
    for model in SPOKE_GROUPS:
        add(model, 0, 'Pinwheel', PINWHEEL_SLOW, a, b, main)
    for model in RING_GROUPS:
        add(model, 0, 'Twinkle',
            TWINKLE_SOFT if level <= 3 else TWINKLE_BRIGHT, a, b, accent)


def beat_details(a, b, level):
    colors = [BLUE, IVORY, CYAN, IVORY]
    arch_rows = ['Arches - Bottom', 'Arches - Middle', 'Arches - Top']
    for i, (s, e, pos) in enumerate(beats_in(a, b)):
        tree = pos + 1
        add(f'Mini Tree - {tree}', 1, 'On', ON_PULSE, s, e, colors[pos])
        if level >= 3:
            add(arch_rows[pos % 3], 1, 'On', ON_PULSE, s, e, colors[pos])
        if pos == 0:
            add('Mini Tree Stars', 1, 'On', ON_SHIMMER, s, min(s + 420, e), IVORY)
            add('Tree Topper', 1, 'On', ON_SHIMMER, s, min(s + 500, e), accent_for(level))
        elif level >= 4 and pos == 2:
            add('Mini Tree Stars', 1, 'On', ON_PULSE, s, min(s + 300, e), CYAN)


def accent_for(level):
    return [SLATE, BLUE, CYAN, IVORY, WHITE][level - 1]


def prechorus(a, b, level):
    section_base(a, b, level)
    beat_details(a, b, level)
    for i, (s, e) in enumerate(bars_in(a, b)):
        bank = HOLY_BANKS[i % len(HOLY_BANKS)]
        for model in bank:
            add(model, 1, 'Shockwave', SHOCKWAVE_TIGHT, s, min(s + 700, e), BLUE_CYAN)
        add('EFL Wings', 1, 'Fan', FAN, s, min(s + 1200, e), CYAN_IVORY)


def holy_hit(start, index, strongest=False):
    palette = [IVORY, CYAN, WHITE, CYAN_IVORY][index % 4]
    duration = 1250 if strongest else 950
    for model in HOLY_BANKS[index % len(HOLY_BANKS)]:
        add(model, 2, 'Shockwave', SHOCKWAVE, start, start + duration, palette)
    add('Flakes GRP', 2, 'Shockwave', SHOCKWAVE, start, start + duration, palette)
    add('EFL Wings', 2, 'Shockwave', SHOCKWAVE, start, start + duration, palette)
    add('Tree Topper', 2, 'On', ON_HOLY, start, start + duration, IVORY)
    if strongest:
        slam(start, 700, palette)


def chorus(a, b, level, holy_times, opening_slam=True):
    section_base(a, b, level)
    beat_details(a, b, level)
    if opening_slam:
        slam(a, 700, CYAN_IVORY if level < 5 else WHITE)
    for i, start in enumerate(holy_times):
        holy_hit(start, i, strongest=(i == len(holy_times) - 1 or level == 5 and i == 0))
    for i, (s, e) in enumerate(bars_in(a, b)):
        for model in SPINNERS[i % 2::2]:
            add(model, 1, 'Fan', FAN, s, min(s + 1600, e), BLUE_CYAN)


# Projector: preserve the downloaded lyric video for the complete song.
add('Projector', 0, 'Video', VIDEO, 0, END_CAP, WHITE)

# Rendered comparison identified Let It Go 0:00.5-0:14.4 as the actual target:
# a continuous Black Cherry Cosmos field, sparsely revealed by a music-reactive
# unmask. Its second half adds model-specific pinwheels, shockwaves, and soft
# washes. Settings and buffer styles below match that stack; colors are remapped
# to the Holy Forever video's blue/cyan/ivory/violet palette.
WIND_START = 180
WIND_BUILD = 7710
WIND_SNOW_START = 13970
add(
    'Whole Scene', 3, 'Color Wash', WIND_UNMASK,
    WIND_START, INTRO[1], WIND_UNMASK_PALETTE
)
add(
    'Whole Scene', 4, 'Shader', WIND_SHADER,
    WIND_START, INTRO[1], WIND_SHADER_PALETTE
)
add(
    'Whole Scene', 2, 'Snowflakes', WIND_SNOW,
    WIND_SNOW_START, INTRO[1], IVORY
)

for model, layer in [
    ('Windows', 0), ('Verts', 1), ('Roof', 0),
    ('Arches - All', 1), ('Colums', 1),
]:
    add(
        model, layer, 'Color Wash', WIND_GLOW,
        WIND_BUILD, INTRO[1], WIND_GLOW_PALETTE
    )
add(
    'Floods GRP', 2, 'Color Wash', WIND_FLOOD,
    WIND_BUILD, INTRO[1], BLUE_CYAN
)

for model in ['GE Baby Grand Illusion GRP', 'GE MOAW GRP']:
    add(
        model, 0, 'Pinwheel', WIND_PIN_PER_MODEL,
        WIND_BUILD, INTRO[1], WIND_PIN_PALETTE
    )
    add(
        model, 1, 'Shockwave', WIND_SHOCK_PER_MODEL,
        WIND_BUILD, INTRO[1], BLUE_CYAN
    )

for model, pin_layer, shock_layer in [
    ('GE Starlord GRP', 0, 1),
    ('GE Reel Max GRP', 1, 2),
]:
    add(
        model, pin_layer, 'Pinwheel', WIND_PIN_OVERLAY,
        WIND_BUILD, INTRO[1], WIND_PIN_PALETTE
    )
    add(
        model, shock_layer, 'Shockwave', WIND_SHOCK_OVERLAY,
        WIND_BUILD, INTRO[1], BLUE_CYAN
    )

add(
    'GE Rosa Grande GRP', 0, 'Pinwheel', WIND_PIN_PER_PREVIEW,
    WIND_BUILD, INTRO[1], WIND_PIN_PALETTE
)
add(
    'GE Rosa Grande GRP', 1, 'Shockwave', WIND_SHOCK_DEFAULT,
    WIND_BUILD, INTRO[1], BLUE_CYAN
)
add(
    'Mini Trees', 1, 'Shockwave', WIND_SHOCK_MINI,
    WIND_BUILD, INTRO[1], WIND_MUSIC_PALETTE
)
add(
    'GE Merry Christmas', 1, 'Shockwave', WIND_SHOCK_WIDE,
    WIND_BUILD, INTRO[1], WIND_MUSIC_PALETTE
)
add(
    'Mega Tree', 7, 'Shockwave', WIND_SHOCK_SMALL,
    WIND_BUILD, INTRO[1], WIND_MUSIC_PALETTE
)
add(
    'Tree Topper', 2, 'Shockwave', WIND_SHOCK_SMALL,
    WIND_BUILD, INTRO[1], WIND_MUSIC_PALETTE
)
add(
    'Flakes GRP', 1, 'Shockwave', WIND_SHOCK_FLAKES,
    WIND_BUILD, INTRO[1], BLUE_CYAN
)
add(
    'Icicles GRP', 1, 'Shockwave', WIND_SHOCK_WIDE,
    WIND_BUILD, INTRO[1], WIND_MUSIC_PALETTE
)
for model in ['EFL Wing - Left', 'EFL Wing - Right']:
    add(
        model, 0, 'Pinwheel', WIND_PIN_DEFAULT,
        WIND_BUILD, INTRO[1], WIND_PIN_PALETTE
    )
    add(
        model, 1, 'Shockwave', WIND_SHOCK_DEFAULT,
        WIND_BUILD, INTRO[1], BLUE_CYAN
    )

# Verse 1: restrained blue and ivory.
section_base(*VERSE_1, level=1)
beat_details(*VERSE_1, level=1)

# "Your name..." builds toward the first chorus.
prechorus(*PRE_1, level=2)

# The lyric-video OCR timestamps give exact "Holy" entries.
chorus(*CHORUS_1, level=3, holy_times=[70570, 77580, 83580, 87590])

# Verse 2 drops back, but keeps more motion than verse 1.
section_base(*VERSE_2, level=2)
beat_details(*VERSE_2, level=2)

chorus(*CHORUS_1B, level=3, holy_times=[130630, 137640, 143140, 147650])
chorus(*CHORUS_2, level=4, holy_times=[157160, 164160, 170170, 174170])

# Two passes of "Your name is the highest"; the second rises to full white.
prechorus(*PRE_2, level=3)
prechorus(*PRE_3, level=4)
slam(207210, 850, IVORY)
for model in SPINNERS:
    add(model, 2, 'Galaxy', GALAXY, 207210, 209400, BLUE_CYAN)

# Final choruses: broad, bright, and still in the video's cool palette.
chorus(*CHORUS_1C, level=5, holy_times=[237240, 243740, 249750, 253750])
chorus(*CHORUS_2B, level=5, holy_times=[263760, 270770, 276780, 280780])

# Tag: sustained worshipful finish rather than another busy chase.
section_base(*TAG, level=4)
holy_hit(290290, 0, strongest=True)
holy_hit(293790, 1, strongest=True)
add('House Outline', 2, 'On', ON_LONG_FADE, 293790, TAG[1], IVORY)
add('Roof', 2, 'On', ON_LONG_FADE, 293790, TAG[1], IVORY)
add('Mega Tree', 2, 'Galaxy', GALAXY, 293790, TAG[1], CYAN_IVORY)
for model in SPINNERS:
    add(model, 1, 'Galaxy', GALAXY, 293790, TAG[1], BLUE_CYAN)

# Outro follows the video back to black.
add('Icicles GRP', 0, 'Twinkle', TWINKLE_FADE, OUTRO[0], OUTRO[1], IVORY)
add('Flakes GRP', 0, 'Twinkle', TWINKLE_FADE, OUTRO[0], OUTRO[1], CYAN_IVORY)
add('Mini Trees', 0, 'Twinkle', TWINKLE_FADE, OUTRO[0], OUTRO[1], BLUE_CYAN)
add('House Outline', 0, 'On', ON_LONG_FADE, OUTRO[0], OUTRO[1], BLUE)
add('Roof', 0, 'On', ON_LONG_FADE, OUTRO[0], OUTRO[1], BLUE)
add('Tree Topper', 0, 'On', ON_LONG_FADE, OUTRO[0], OUTRO[1], IVORY)
add('Floods GRP', 0, 'Color Wash', E(
    'B_CHOICE_BufferStyle=Single Line,T_TEXTCTRL_Fadeout=5'
), OUTRO[0], OUTRO[1], NAVY_DIM)


problems = []
for element, layers in seq.items():
    for layer, effects in layers.items():
        effects.sort(key=lambda item: item[2])
        for current, following in zip(effects, effects[1:]):
            if current[3] > following[2]:
                problems.append(
                    f'overlap {element} L{layer}: {current} vs {following}'
                )
if problems:
    for problem in problems[:30]:
        print(problem)
    raise SystemExit(f'OVERLAPS FOUND: {len(problems)}')

total = sum(len(effects) for layers in seq.values() for effects in layers.values())
print(
    f'duration: {DUR} ms  elements: {len(seq)}  effects: {total}  '
    f'palettes: {len(palettes)}  effdb: {len(effdb)}'
)

pushed, failures = 0, []
for element, layers in sorted(seq.items()):
    for layer, effects in sorted(layers.items()):
        for ref, effect, start, end, palette in sorted(effects, key=lambda item: item[2]):
            try:
                x.add_effect(
                    element, layer, effect, effdb[ref], palettes[palette], start, end
                )
                pushed += 1
            except Exception as ex:
                failures.append((element, layer, effect, start, end, str(ex)))

print(f'pushed {pushed} effects, {len(failures)} failures')
if failures:
    for key, count in Counter((f[0], f[2]) for f in failures).most_common():
        print('FAIL', key, 'x', count)
    for failure in failures[:10]:
        print(' ', failure)
    raise SystemExit(1)

x.save(OUT)
print('saved', OUT)
