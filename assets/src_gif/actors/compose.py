from _common import *
import json
D='review/gif_style/_sheets/'
def spr(n,i=0):
    fr,m=strip_frames(n); return fr[i%len(fr)],tuple(m['anchor'])
# placements: name -> (x,y) anchor on canvas, frame
P=[('tea_stall',262+16,STAND_Y,0),('stool_red',299,STAND_Y,0),('stool_blue',311,STAND_Y,0),('oldman_tea',303,STAND_Y,2),('stool_red',322,STAND_Y,0),
   ('steam',262+7,STAND_Y-24,1),
   ('woman_wait',150,SEAT_Y-1,0),('cat_sleep',CAT_SPOT[0],CAT_SPOT[1]-1,0),('shopkeeper',285,185,0),
   ('sparrow_perch',130,100,0),('sparrow_fly',170,80,1),('moto_parked',MOTORBIKE_X+17,STAND_Y,0),('walker_nonla',100,STAND_Y,0),('scooter_rider',60,WHEEL_Y,0)]
def build(base=MOCK):
    im=base.copy()
    for n,x,y,i in P:
        s,a=spr(n,i); im.alpha_composite(s,(x-a[0],y-a[1]))
    return im
if __name__=='__main__':
    im=build()
    a=im.crop((250,150,350,200)).resize((400*2,200*2),Image.NEAREST)
    b=im.crop((120,150,200,200)).resize((320*2,200*2),Image.NEAREST)
    c_=Image.new('RGB',(a.width+b.width,400),'white'); c_.paste(a.convert('RGB'),(0,0)); c_.paste(b.convert('RGB'),(a.width,0)); c_.save(D+'comp.png')
    im.convert('RGB').save(D+'comp_full.png')
