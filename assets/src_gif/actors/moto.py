from _common import *
SC='review/gif_style/_sheets/'

def wheel(im, x0, y0=10):
    ellipse(im,x0,y0,x0+9,y0+9,'grey_k')
    ellipse(im,x0+2,y0+2,x0+7,y0+7,'grey_l')
    ellipse(im,x0+3,y0+3,x0+6,y0+6,'grey')
    rect(im,x0+4,y0+4,x0+5,y0+5,'grey_d')
    put(im,x0+1,y0+3,'grey_m'); put(im,x0+2,y0+2,'grey_m') if False else None
    put(im,x0+4,y0+2,'grey_hl'); put(im,x0+3,y0+3,'grey_hl')

def moto():
    im = new(36, 22)
    wheel(im,3,12); wheel(im,25,12)
    # muffler (side) in front of rear wheel
    rect(im,5,18,13,19,'grey'); rect(im,5,18,13,18,'grey_l'); put(im,4,19,'grey_d'); put(im,14,18,'grey_d'); put(im,14,19,'grey_d')
    # engine block
    rect(im,14,15,22,20,'grey_m'); rect(im,14,15,22,15,'grey_l'); rect(im,14,20,22,20,'grey_d')
    ellipse(im,16,16,19,19,'grey_l'); rect(im,17,17,18,18,'grey_d')
    # footboard
    rect(im,17,13,26,13,'teal'); rect(im,17,14,25,15,'teal_d')
    # rear fender + side cover
    poly(im,[(2,12),(3,9),(6,8),(11,8),(14,10),(14,12)],'teal')
    poly(im,[(4,9),(6,7),(16,7),(19,9),(18,12),(10,12),(8,11)],'teal')
    rect(im,7,8,16,8,'glass'); rect(im,9,12,17,12,'teal_d'); rect(im,3,12,8,12,'teal_d') if False else None
    put(im,2,12,'teal_d'); put(im,3,12,'teal_d'); put(im,4,12,'teal_d')
    # seat
    poly(im,[(5,6),(8,4),(19,4),(21,6)],'grey_k'); rect(im,8,4,18,4,'grey_m')
    # tail light
    put(im,1,10,'red'); put(im,1,9,'red_l'); put(im,2,10,'red')
    # leg shield
    poly(im,[(25,4),(29,4),(28,13),(24,13)],'teal')
    rect(im,25,5,25,12,'glass'); rect(im,28,5,28,13,'teal_d')
    # fork
    for i in range(9): put(im,29+i//5,9+i,'grey_m'); put(im,30+i//5,9+i,'grey_d')
    # front fender
    poly(im,[(25,13),(27,10),(32,10),(35,13)],'teal'); rect(im,26,13,34,13,'teal_d')
    # handlebar, mirror, headlight
    rect(im,26,3,30,3,'grey_k'); rect(im,27,1,27,2,'grey_d'); rect(im,26,0,28,0,'grey_l')
    ellipse(im,30,3,33,6,'yl_l'); put(im,30,4,'white'); put(im,33,6,'yl_d'); put(im,32,6,'yl_d')
    # helmet (half-shell) hanging from handlebar/mirror
    poly(im,[(20,4),(21,2),(24,2),(25,4),(25,6),(20,6)],'yl_l')
    rect(im,20,6,25,6,'yl_d'); put(im,21,3,'white'); put(im,22,3,'white')
    put(im,24,7,'red'); put(im,23,6,'grey_d') if False else None
    # front basket (wicker) + veg
    rect(im,30,8,35,12,'wood_l'); rect(im,30,8,35,8,'wood_hl')
    for y in (9,11):
        for x in range(30,36): 
            if (x+y)%2==0: put(im,x,y,'wood')
    rect(im,35,9,35,12,'wood_d')
    for x,y in [(31,7),(32,7),(32,6),(33,7),(34,7),(34,6)]: put(im,x,y,'leaf')
    put(im,33,6,'leaf_l'); put(im,31,7,'leaf_l')
    return im
if __name__=='__main__':
    fr=[sout(moto())]
    sheet(fr,scale=14).save(SC+'moto.png')
    save_c('moto_parked',fr,19,fr[0].height-1,notes='side view facing right (flip for left). anchor=bottom of wheels, centre. place at MOTORBIKE_X, y=196 on sidewalk')
