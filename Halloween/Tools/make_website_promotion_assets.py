from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from reportlab.graphics.barcode.qrencoder import QRCode,QRErrorCorrectLevel
import json
OUT=Path(__file__).resolve().parents[1]/'WebsitePromotion';OUT.mkdir(exist_ok=True)
URL='https://oharafamilylightshow.com/'
DOMAIN='oharafamilylightshow.com'
FONTS=Path('/System/Library/Fonts/Supplemental')
def centered(draw,text,y,width,size,bold=False,fill='white'):
 font=ImageFont.truetype(str(FONTS/('Arial Bold.ttf' if bold else 'Arial.ttf')),size)
 box=draw.textbbox((0,0),text,font=font)
 assert box[2]-box[0]<=width-4,(text,size,box)
 draw.text(((width-box[2]+box[0])//2,y-box[1]),text,font=font,fill=fill)
im=Image.new('RGBA',(192,64));d=ImageDraw.Draw(im)
d.rectangle((0,0,191,18),fill='black');d.rectangle((0,43,191,63),fill='black')
centered(d,DOMAIN,3,192,14,True)
centered(d,'TUNE TO 87.9 FM',46,192,18,True)
im.save(OUT/'tune-to-website.png')
qr=QRCode(None,QRErrorCorrectLevel.M);qr.addData(URL);qr.make()
matrix=qr.modules;modules=len(matrix);scale=4;size=(modules+8)*scale
assert size<=152,(modules,size)
code=Image.new('RGB',(size,size),'white');d=ImageDraw.Draw(code)
for y,row in enumerate(matrix):
 for x,dark in enumerate(row):
  if dark:d.rectangle(((x+4)*scale,(y+4)*scale,(x+5)*scale-1,(y+5)*scale-1),fill='black')
im=Image.new('RGB',(256,192),'black');d=ImageDraw.Draw(im)
centered(d,'SCAN TO VISIT OUR WEBSITE',3,256,14,True)
im.paste(code,((256-size)//2,20))
centered(d,DOMAIN,176,256,15,True)
im.save(OUT/'projector-website-qr.png')
code.save(OUT/'qr.png')
(OUT/'asset-info.json').write_text(json.dumps(dict(url=URL,modules=modules,scale=scale,quiet_zone_modules=4,qr_bounds=[(256-size)//2,20,size,size],projector_dimensions=[256,192],sign_dimensions=[192,64]),indent=2))
preview=Image.new('RGB',(768,816),'#16171a')
preview.paste(im.resize((768,576),Image.Resampling.NEAREST),(0,0))
sign=Image.open(OUT/'tune-to-website.png');back=Image.new('RGBA',sign.size,'#432065');back.alpha_composite(sign)
preview.paste(back.convert('RGB').resize((576,192),Image.Resampling.NEAREST),(96,600))
preview.save(OUT/'preview.png')
print((OUT/'asset-info.json').read_text())
