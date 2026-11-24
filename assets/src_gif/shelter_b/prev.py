import sys
from _c import *
from PIL import Image
k = int(sys.argv[1]); box = tuple(map(int, sys.argv[2:6])); names = sys.argv[6:]
base = Image.open(ROOT/"assets/out_gif/_mock/mock3.png").convert("RGBA")
bp = base.load()
for y in range(H):
    for x in range(W):
        if bp[x, y][:3] in ((217,95,155),(176,61,125),(220,95,157),(178,63,125)) or (bp[x,y][0]>150 and bp[x,y][1]<110 and bp[x,y][2]>90 and x<200 and y<175): bp[x, y] = c("sky")
for n in names:
    base.alpha_composite(Image.open(ROOT/f"assets/out_gif/shelter/{n}.png").convert("RGBA").crop((0,0,W,H)))
base.crop(box).resize(((box[2]-box[0])*k,(box[3]-box[1])*k),0).save("/tmp/p.png")
