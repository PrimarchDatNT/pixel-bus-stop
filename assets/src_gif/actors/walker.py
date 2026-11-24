import math
from _common import *
SC='review/gif_style/_sheets/'

def seg(im,x0,y0,x1,y1,cols,w=2):
    n=max(abs(x1-x0),abs(y1-y0),1)
    for t in range(n+1):
        x=round(x0+(x1-x0)*t/n); y=round(y0+(y1-y0)*t/n)
        for i in range(w): put(im,x+i,y,cols[i])

def basket(im,cx,top,kind):
    # string handled elsewhere; basket 9 wide: fruit mound rows top..top+2, body top+3..top+5
    x0=cx-4
    rect(im,x0,top+3,x0+8,top+4,'wood_l'); rect(im,x0+1,top+5,x0+7,top+5,'wood'); 
    rect(im,x0,top+3,x0+8,top+3,'wood_hl'); put(im,x0+8,top+4,'wood'); put(im,x0+7,top+4,'wood')
    for x in (x0+2,x0+4,x0+6): put(im,x,top+4,'wood')
    if kind==0:   # oranges / mangoes
        for dx,dy,cl in [(1,2,'or'),(3,1,'or_l'),(5,2,'or'),(7,2,'yl'),(4,2,'yl'),(2,2,'or_l'),(6,1,'yl_l')]:
            rect(im,x0+dx,top+dy-1+0,x0+dx+1,top+dy,cl) if False else None
        ellipse(im,x0+0,top,x0+8,top+3,'or')
        for dx,dy,cl in [(2,0,'or_l'),(3,0,'or_l'),(5,1,'yl'),(6,0,'yl_l'),(1,2,'or_d'),(4,2,'or_d'),(7,2,'or_d'),(6,1,'or_l')]: put(im,x0+dx,top+dy,cl)
    else:         # lychee / dragon-fruit pink & green leaves
        ellipse(im,x0+0,top,x0+8,top+3,'pk')
        for dx,dy,cl in [(2,0,'pk_l'),(3,0,'pk_l'),(5,1,'leaf_l'),(6,0,'leaf'),(1,2,'pk_d'),(4,2,'pk_d'),(7,2,'pk_d'),(6,1,'pk_l'),(4,0,'leaf_l')]: put(im,x0+dx,top+dy,cl)

def walker(p):
    im=new(32,34); S=new(32,34)
    bob = [0,1,0,0,1,0][p]
    hx=16   # torso centre
    # legs
    hip=(hx-1,20+bob)
    for leg,ph,near in ((1,3,False),(0,0,True)):
        a=2*math.pi*((p+ph)%6)/6
        fx=round(4*math.cos(a)); lift = max(0,round(2*math.sin(a)*-1)) if False else (1 if math.sin(a)<-0.3 else 0)+(1 if math.sin(a)<-0.8 else 0)
        kx=hip[0]+fx//2+ (1 if lift else 0); ky=hip[1]+5-lift//1 if False else hip[1]+5-(lift>0)
        fy=hip[1]+10-lift
        cols=('grey','grey_d') if near else ('grey_d','grey_k')
        seg(im,hip[0],hip[1],kx,ky,cols); seg(im,kx,ky,hip[0]+fx,fy,cols)
        # foot
        fcol=('sk','sk_d') if near else ('sk_d','sk_d')
        put(im,hip[0]+fx+1,fy+1,fcol[0]); put(im,hip[0]+fx+2,fy+1,fcol[1]); put(im,hip[0]+fx,fy+1,fcol[0])
    # torso (cream ao ba ba), leaning slightly forward
    for i,y in enumerate(range(11+bob,20+bob)):
        x0=hx-3+(1 if i<3 else 0); x1=hx+2+(1 if i<4 else 0)
        for x in range(x0,x1+1):
            col='wc_l' if x==x0 else ('wc_d' if x>=x1-1 else 'wc')
            put(im,x,y,col)
    for x in range(hx-3,hx+3): put(im,x,19+bob,'grey_d'); 
    # head under hat, facing right
    hy=4+bob
    rect(im,hx-2,hy,hx+2,hy+5,'sk'); rect(im,hx-2,hy,hx-2,hy+5,'sk_l')
    rect(im,hx-2,hy,hx+1,hy+1,'hair'); put(im,hx-3,hy+2,'hair'); put(im,hx-3,hy+3,'hair')
    put(im,hx+2,hy+2,'sk_l'); put(im,hx+3,hy+3,'sk'); # nose
    put(im,hx+1,hy+2,'ink'); put(im,hx+1,hy+4,'sk_d')
    rect(im,hx,hy+6,hx+1,hy+6,'sk_d')   # neck
    # nón lá: cone
    cy=1+bob
    for i,(w) in enumerate([3,7,11,15]):
        y=cy+i
        x0=hx-w//2+1
        for x in range(x0,x0+w):
            col='yl_l' if x<x0+w//2 else 'yl'
            if x>=x0+w-2: col='yl_d' if i>1 else 'yl'
            put(im,x,y,col)
    for x in range(hx-6,hx+9): put(im,x,cy+3,'yl_d') if (x-hx)%2==0 else put(im,x,cy+3,'yl')
    put(im,hx+1,cy+4,'red_d'); put(im,hx+2,cy+5,'red_d') if False else None   # chin strap
    # pole + baskets
    py=11+bob
    for x in range(1,31):
        y=py+ (1 if (x<5 or x>27) else 0)
        put(im,x,y,'wood_l')
    for x in range(1,31):
        y=py+(1 if (x<5 or x>27) else 0); put(im,x,y+1,'wood') if False else None
    lb=[0,1,0,0,1,0][(p+3)%6]*0
    for cx_,k in ((4,0),(27,1)):
        top=py+10+(1 if p%3==1 else 0)
        # strings
        for y in range(py+2,top+1): put(im,cx_-3,y,'wood_d') if False else None
        for y in range(py+2,top+3): put(im,cx_-3 if k==0 else cx_-3,y,'wood_d') if False else None
        sx=2 if k==0 else 29
        seg(S,sx,py+1,cx_-3,top+3,('wood_hl',),w=1); seg(S,sx,py+1,cx_+3,top+3,('wood_hl',),w=1)
        basket(im,cx_,top,k)
    # arms: hands on pole
    seg(im,hx-2,13+bob,hx+1,py,('sk_l','sk'),w=1)
    seg(im,hx,13+bob,hx+2,py,('sk','sk_d'),w=1)
    put(im,hx-2,12+bob,'wc'); put(im,hx-1,12+bob,'wc')
    return im,S
def full(p):
    im,S=walker(p); o=sout(im); S2=new(o.width,o.height); S2.alpha_composite(S,(1,1))
    # strings go behind the sprite
    out=new(o.width,o.height); out.alpha_composite(S2); out.alpha_composite(o); return out
if __name__=='__main__':
    fr=[full(i) for i in range(6)]
    sheet(fr,scale=10,cols=3).save(SC+'walker.png')

    save_c('walker_nonla',fr,17,max(f.getbbox()[3] for f in fr)-1,fps=8,notes='faces right (flip for left). anchor=feet row (support foot), torso centre; ~32 wide incl. pole and baskets')
