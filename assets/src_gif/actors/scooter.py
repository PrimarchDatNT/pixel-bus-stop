from _common import *
from walker import seg
SC='review/gif_style/_sheets/'

def wheel(im,x0,y0,f):
    ellipse(im,x0,y0,x0+7,y0+7,'grey_k'); ellipse(im,x0+2,y0+2,x0+5,y0+5,'grey_l')
    rect(im,x0+3,y0+3,x0+4,y0+4,'grey_d')
    if f: put(im,x0+2,y0+3,'white'); put(im,x0+5,y0+4,'white')
    else: put(im,x0+3,y0+2,'white'); put(im,x0+4,y0+5,'white')

def scooter(f):
    im=new(40,32)
    wheel(im,4,24,f); wheel(im,28,24,f)
    d = 1 if f else 0   # upper body bob
    # rear body (pink)
    poly(im,[(3,26),(4,21),(8,18),(17,18),(19,22),(18,26),(13,26),(11,24),(7,26)],'pk_l')
    rect(im,6,19,16,19,'bl_hl') if False else None
    poly(im,[(5,22),(8,19),(16,19),(17,22)],'pk_l')
    rect(im,5,23,12,23,'pk'); rect(im,9,25,18,26,'pk_d'); rect(im,4,26,8,26,'pk_d')
    rect(im,13,22,17,24,'pk'); 
    # floorboard
    rect(im,17,25,28,25,'pk'); rect(im,18,26,27,26,'pk_d')
    # seat
    poly(im,[(7,17-0),(9,15),(19,15),(21,17)],'grey_k'); rect(im,9,15,18,15,'grey_m')
    # tail light
    put(im,3,21,'red'); put(im,3,22,'red')
    # leg shield + fork + fender
    poly(im,[(27,12),(31,12),(30,25),(26,25)],'pk_l'); rect(im,27,13,27,24,'white'); rect(im,30,13,30,25,'pk_d')
    for i in range(8): put(im,31+i//6,17+i,'grey_m')
    poly(im,[(28,24),(30,22),(34,22),(36,25)],'pk'); rect(im,29,25,35,25,'pk_d') if False else None
    # handlebar/headlight/mirror
    rect(im,27,11,31,11,'grey_k'); rect(im,29,8,29,10,'grey_d'); rect(im,28,7,30,7,'grey_l')
    ellipse(im,31,12,34,15,'yl_l'); put(im,31,13,'white'); put(im,34,15,'yl_d')
    # ---- rider (everything shifted by d upward) 
    r=new(40,32)
    # legs: thigh from hip to knee, shin down to floorboard
    seg(r,14,16,23,17,('navy','pb_d'),w=1) if False else None
    for x in range(14,24): put(r,x,16,'pb'); put(r,x,17,'pb_d')
    for x in range(14,24): put(r,x,15,'pb_l') if x<19 else None
    seg(r,23,17,25,24,('pb','pb_d'),w=2)
    put(r,25,24,'pb_d')
    rect(r,24,25,27,25,'white'); rect(r,24,24,24,24,'white')  # shoe
    # torso: sun-protection coat (mint) + flutter tail
    for i,y in enumerate(range(7,17)):
        x0=13+(0 if i>3 else 1); x1=19-(1 if i>6 else 0)
        for x in range(x0,x1+1):
            put(r,x,y,'sh_l' if x==x0 else ('sh_d' if x>=x1-1 else 'sh'))
    # coat tail flapping behind
    tail=[(12,15),(11,16),(10,16),(9,17)] if not f else [(12,16),(11,17),(10,17),(9,18)]
    for x,y in tail: put(r,x,y,'sh'); put(r,x,y+1,'sh_d')
    rect(r,12,12,12,14,'sh_d')
    # arm to handlebar
    seg(r,18,10,24,13,('sh','sh_d'),w=2)
    seg(r,25,13,28,11,('sh','sh_d'),w=1)
    put(r,28,10,'white'); put(r,29,10,'white')       # glove on grip
    # neck + head + helmet
    rect(r,16,6,17,6,'sk_d')
    rect(r,14,1,20,6,'sk')
    # face: sunglasses + white mask
    rect(r,18,3,21,3,'ink'); put(r,21,4,'sk_l')
    rect(r,17,4,21,6,'paper'); put(r,21,4,'paper') if False else None
    put(r,21,5,'white'); put(r,21,6,'white'); rect(r,17,4,20,4,'sk')
    # helmet shell
    poly(r,[(13,4),(13,2),(15,0),(19,0),(21,2),(21,3),(13,3)],'white')
    rect(r,13,1,20,1,'white'); rect(r,13,2,21,2,'white')
    rect(r,13,3,16,5,'white')
    put(r,15,1,'glass_l'); put(r,16,1,'glass_l'); rect(r,14,3,14,5,'grey_hl')
    rect(r,17,3,21,3,'grey_hl') if False else None
    # shadows: helmet lower edge
    rect(r,18,2,21,2,'grey_hl'); rect(r,13,5,16,5,'grey_l')
    # hair under helmet at back
    put(r,13,6,'hair'); put(r,14,6,'hair')
    # hair strand under
    # shift upper body by -d
    up=new(40,32); up.alpha_composite(r,(0,-d))
    im.alpha_composite(up)
    return im
if __name__=='__main__':
    fr=[sout(scooter(i)) for i in (0,1)]
    sheet(fr,scale=12).save(SC+'scooter.png')
    save_c('scooter_rider',fr,20,max(f.getbbox()[3] for f in fr)-1,fps=8,notes='faces right (flip for left). anchor = lowest wheel pixel row, wheelbase centre. y = WHEEL_Y')
