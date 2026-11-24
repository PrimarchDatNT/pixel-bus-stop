from _common import *
SC='review/gif_style/_sheets/'

def sleeper(b=0, tail=None):
    im = new(18, 11)
    dy = -1 if b else 0
    # body dome
    ellipse(im, 4, 3+dy, 17, 10, 'or')
    rect(im, 4, 7, 17, 10, 'or')
    # head
    ellipse(im, 0, 4, 7, 10, 'or')
    # ears
    put(im,1,3,'or'); put(im,2,2,'or'); put(im,2,3,'or'); put(im,5,2,'or'); put(im,6,3,'or'); put(im,5,3,'or')
    put(im,2,3,'pk_l'); put(im,5,3,'pk_l')
    # back highlight (upper-left light)
    for x in range(8,14): put(im,x,3+dy,'or_l')
    for x in range(7,10): put(im,x,4+dy,'or_l')
    put(im,14,4+dy,'or_l'); put(im,15,5+dy,'or')
    # stripes on back
    for x in (9,12,15): 
        put(im,x,4+dy+(1 if x>12 else 0),'or_d'); put(im,x,5+dy+(1 if x>12 else 0),'or_d')
    # bottom shade
    for x in range(5,18): put(im,x,10,'or_d')
    # white chest + paws, head under chin
    for x,y in [(0,9),(1,9),(2,9),(3,9),(1,8),(2,8),(3,8),(4,9),(4,10),(0,10),(1,10),(2,10),(3,10)]:
        put(im,x,y,'white')
    put(im,0,10,'white'); 
    for x in range(0,5): put(im,x,10,'grey_hl')
    put(im,4,8,'white')
    # face: closed eye, nose
    put(im,1,6,'or_d'); put(im,2,6,'or_d'); put(im,5,6,'or_d'); put(im,4,6,'or_d')
    put(im,0,7,'pk_l'); 
    # cheek light
    put(im,2,5,'cat_hl'); put(im,3,5,'cat_hl'); put(im,3,4,'or_l')
    put(im,1,4,'or_l')
    # head stripes
    put(im,3,4,'or_d'); put(im,4,5,'or')
    for y in (5,6,7): put(im,7,y,'or_d')
    return im

def tail_curl(im):
    # tail along front-bottom wrapping toward paws, striped
    for x in range(5,17): put(im,x,10,'or')
    for x in (6,9,12,15): put(im,x,10,'or_d')
    put(im,17,10,'or_d')
    return im

def finish(im): return sout(im, fixed='or_d')


def tail_hang(im, pts):
    big = new(26, 18); big.alpha_composite(im,(0,0))
    for i,(x,y) in enumerate(pts):
        col = 'or_d' if (i%3==2 or i==len(pts)-1) else 'or'
        put(big,x,y,col); put(big,x+1,y,col)
    return big

def sitter():
    im = new(10, 9)
    ellipse(im, 2, 3, 9, 8, 'or')          # body
    rect(im, 2, 6, 9, 8, 'or')
    ellipse(im, 0, 1, 6, 6, 'or')          # head
    for p in [(1,0),(1,1),(2,1),(5,0),(5,1),(4,1)]: put(im,*p,'or')
    put(im,2,1,'pk_l'); put(im,5,1,'pk_l') if False else None
    put(im,1,0,'or'); put(im,5,0,'or')
    put(im,2,1,'or'); put(im,4,1,'or')
    # eyes + nose
    put(im,1,3,'ink'); put(im,4,3,'ink'); put(im,0,4,'pk_l') if False else None
    put(im,2,4,'pk_l')
    for p in [(2,5),(3,5),(2,6),(3,6),(3,7),(2,7)]: put(im,*p,'white')   # chest
    put(im,1,2,'or_l'); put(im,2,2,'or_l'); put(im,5,2,'or_d'); put(im,3,2,'or_d')
    # stripes on back
    for p in [(6,4),(7,5),(8,6),(6,7),(7,8)]: put(im,*p,'or_d')
    for p in [(5,3),(6,3)]: put(im,*p,'or_l')
    # front paws
    for p in [(1,8),(2,8),(3,8)]: put(im,*p,'white')
    put(im,1,7,'white')
    # tail curl wrapping front-right
    for p in [(9,8),(8,8),(7,8)]: put(im,*p,'or')
    put(im,9,7,'or_d'); put(im,9,8,'or_d')
    return im

if __name__=='__main__':
    sl=[finish(tail_curl(sleeper(i))) for i in (0,1)]
    P=[[(17,8),(18,9),(19,10),(19,11),(19,12),(19,13),(19,14)],
       [(17,8),(18,9),(19,10),(20,11),(21,12),(21,13),(22,14)],
       [(17,8),(18,8),(19,9),(20,10),(21,10),(22,11),(23,11)]]
    tl=[finish(tail_hang(sleeper(0),P[i])) for i in (0,1,2,1)]
    st=finish(sitter())
    sheet(sl+tl+[st],scale=10,cols=4).save(SC+'cat.png')
    save_asset('actors','cat_sleep',sl,fps=2,anchor=(10,12),notes='anchor=bottom row centre; place at (214,145)')
    save_asset('actors','cat_tail',tl,fps=6,anchor=(10,12),notes='sleeping cat, tail hangs over roof edge and flicks; same body position as cat_sleep')
    save_asset('actors','cat_sit',[st],fps=None,anchor=(6,10),notes='sitting pose facing left')
