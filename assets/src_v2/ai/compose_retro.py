"""Style test v4: AI facade band + retro ground + AI sprites -> 640x360 pixel grid, shared 64-colour palette."""
import sys, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
from PIL import Image, ImageDraw, ImageFilter
from rembg import remove, new_session
from tools.pixelize import build_palette, pixelize
O = ROOT / 'assets/out_v2/ai/px'
W, H = 1920, 1080
SPRITES = dict(shelter=('shelter_91_0.png', 'isnet-general-use'), bus=('bus_91_0.png', 'isnet-general-use'),
               moto=('moto3_96_1.png', 'isnet-general-use'), cat=('cat3_95_1.png', 'isnet-general-use'))

plate = Image.open(O / 'bg_ctrl_82_0.png').convert('RGB').resize((1920, 1097), Image.LANCZOS)
frame = Image.new('RGBA', (W, H), (0, 0, 0, 255)); frame.paste(plate.crop((0, 0, 1920, 660)), (0, 0))
d = ImageDraw.Draw(frame); rnd = random.Random(3)
INK=(31,35,38); WALK=(183,164,136); WALK_D=(143,124,100); WALK_L=(206,190,160); CURB=(212,200,172)
ASPH=(58,69,73); ASPH_D=(46,55,59); ASPH_L=(72,84,88); LANE=(232,222,196)
d.rectangle([0,648,W,717], fill=WALK)
for y0 in range(648,717,18):
    off=(y0//18)%2*30
    for x0 in range(-off,W,60): d.rectangle([x0+2,y0+2,x0+58,y0+16], fill=rnd.choice([WALK,WALK,WALK_L,WALK_D]))
d.line([(0,648),(W,648)], fill=INK, width=4)
d.rectangle([0,717,W,735], fill=CURB); d.line([(0,717),(W,717)], fill=INK, width=3); d.line([(0,735),(W,735)], fill=INK, width=4)
for x0 in range(0,W,96): d.line([(x0,718),(x0,734)], fill=WALK_D, width=2)
d.rectangle([0,736,W,948], fill=ASPH)
for _ in range(260):
    x=rnd.randint(0,W); y=rnd.randint(740,945); w=rnd.randint(8,60); h=rnd.randint(3,8)
    d.rectangle([x,y,x+w,y+h], fill=rnd.choice([ASPH_D,ASPH_L]))
for x0 in range(0,W,150): d.rectangle([x0,838,x0+84,844], fill=LANE)
d.rectangle([0,948,W,966], fill=CURB); d.line([(0,948),(W,948)], fill=INK, width=4); d.line([(0,966),(W,966)], fill=INK, width=3)
d.rectangle([0,966,W,H], fill=WALK)
for y0 in range(966,H,40):
    off=(y0//40)%2*60
    for x0 in range(-off,W,120): d.rectangle([x0+3,y0+3,x0+117,y0+37], fill=rnd.choice([WALK,WALK,WALK_L,WALK_D]))
sh = Image.new('L',(W,H),0); sd = ImageDraw.Draw(sh)
for _ in range(90):
    x=rnd.randint(900,1920); y=rnd.randint(650,1075); r=rnd.randint(10,46)
    sd.ellipse([x-r*1.6,y-r*0.5,x+r*1.6,y+r*0.5], fill=110)
frame = Image.composite(Image.new('RGBA',(W,H),(30,40,60,255)), frame, sh.filter(ImageFilter.GaussianBlur(3)).point(lambda v:int(v*0.5)))

def cut(key):
    src, model = SPRITES[key]
    c = remove(Image.open(O / src).convert('RGB'), session=new_session(model), post_process_mask=True)
    c.save(O / f'cut_{key}.png'); return c.crop(c.getbbox())

def place(sp, *, width=None, height=None, cx, bottom, shadow=0.45):
    global frame
    sp = sp.resize((width, round(sp.height*width/sp.width)), Image.LANCZOS) if width else sp.resize((round(sp.width*height/sp.height), height), Image.LANCZOS)
    m = Image.new('L',(W,H),0); ImageDraw.Draw(m).ellipse([cx-sp.width*0.46,bottom-12,cx+sp.width*0.46,bottom+10], fill=int(255*shadow))
    frame = Image.composite(Image.new('RGBA',(W,H),(22,28,40,255)), frame, m.filter(ImageFilter.GaussianBlur(8)))
    frame.alpha_composite(sp, (round(cx-sp.width/2), bottom-sp.height))

place(cut('shelter'), width=560, cx=876, bottom=700)
place(cut('bus'), width=700, cx=1660, bottom=828)
place(cut('moto'), height=175, cx=980, bottom=940)
place(cut('cat'), height=185, cx=360, bottom=1066)
hi = frame.convert('RGB'); hi.save(O / 'styleframe_retro_hi.png')
px = pixelize(hi, (640, 360), build_palette([hi], n=64))
px.save(O / 'styleframe_retro_640.png')
px.resize((W, H), Image.NEAREST).convert('RGB').save(O / 'styleframe_retro.png')
print('ok')
