from _common import *
import tools.px as _px
import json
names=['woman_wait','shopkeeper','tea_stall','stool_red','stool_blue','oldman_tea','steam','cat_sleep','cat_tail','cat_sit','sparrow_perch','sparrow_fly','moto_parked','walker_nonla','scooter_rider']
K=4; PAD=6; W=1500
cells=[]
for n in names:
    fr,m=strip_frames(n)
    w=sum(f.width+3 for f in fr); h=max(f.height for f in fr)
    c1=Image.new('RGBA',(w,h),(0,0,0,0)); x=0
    for f in fr: c1.alpha_composite(f,(x,0)); x+=f.width+3
    cells.append((n,c1.resize((c1.width*K,c1.height*K),Image.NEAREST),m))
rows=[];cur=[];cw=0
for c_ in cells:
    if cw+c_[1].width+PAD>W and cur: rows.append(cur);cur=[];cw=0
    cur.append(c_);cw+=c_[1].width+PAD
rows.append(cur)
Hh=sum(max(c_[1].height for c_ in r)+20+PAD for r in rows)+PAD
sh=Image.new('RGBA',(W,Hh),(*RGB['sky'],255)); y=PAD
for r in rows:
    x=PAD; rh=max(c_[1].height for c_ in r)
    for n,im,m in r:
        lab=new(len(n)*5+4,8); text(lab,1,2,n.upper().replace('_','-'),'ink'); 
        # text doesn't draw underscore; use dash
        sh.alpha_composite(lab.resize((lab.width*2,lab.height*2),Image.NEAREST),(x,y))
        sh.alpha_composite(im,(x,y+20+rh-im.height)); x+=im.width+PAD
    y+=rh+20+PAD
import os
os.makedirs(str(_px.OUT/'actors'/'_preview'),exist_ok=True)
sh.convert('RGB').save(_px.OUT/'actors'/'_preview'/'_sheet@4x.png')
