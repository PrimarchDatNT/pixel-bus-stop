from _c import *
from PIL import Image
import sys
names = sys.argv[2:]; k = int(sys.argv[1])
base = Image.new("RGBA",(W,H),c("sky"))
for n in ["sky","skyline","ground","houses"]:
    base.alpha_composite(Image.open(ROOT/f"assets/out_gif/env/{n}.png").convert("RGBA"))
if 0:
  pass
for n in names:
    s = Image.open(ROOT/f"assets/out_gif/shelter/{n}.png").convert("RGBA")
    j = __import__("json").load(open(ROOT/f"assets/out_gif/shelter/{n}.json"))
    base.alpha_composite(s.crop((0,0,W,H)))
box = (80,95,260,205)
base.crop(box).resize(((box[2]-box[0])*k,(box[3]-box[1])*k),0).save("/tmp/comp.png")

g=Image.open("/tmp/gif0.png").convert("RGB").crop((20,60,230,200))
b2=base.crop(box).resize(((box[2]-box[0])*4,(box[3]-box[1])*4),0).convert("RGB")
g=g.resize((g.width*4//2, g.height*4//2),0) # gif is 2px per logical -> x2 here = 4 per... 
o=Image.new("RGB",(b2.width+g.width,max(b2.height,g.height)),(255,255,255)); o.paste(b2,(0,0)); o.paste(g,(b2.width,0)); o.save("/tmp/cmp.png")
