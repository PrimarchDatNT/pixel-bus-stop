from _common import *
SC='review/gif_style/_sheets/'

def stool(col):
    rows = [
     ".RRRRR.",
     "RrrrrrQ",
     "RrrrrqQ",
     ".qqqqq.",
     ".r...q.",
     ".r...q.",
     "r.....q",
     "Rr...qQ",
    ]
    im = G(rows, {'R':'red_l','r':'red','q':'red_d','Q':'red_d'})
    if col=='blue':
        im = recolor(im, {'red_l':'pb_l','red':'pb','red_d':'pb_d'})
    return im
def stool_out(col): return sout(stool(col))

def table():
    im = new(30, 24)
    # table top + legs (front elevation)
    rect(im,0,13,29,13,'wood_hl'); rect(im,0,14,29,15,'wood_l'); rect(im,0,16,29,16,'wood')
    rect(im,1,17,29-1,17,'wood_d')
    for x in (2,26):
        rect(im,x,17,x+1,22,'wood_l'); rect(im,x+1,17,x+1,22,'wood')
    rect(im,4,20,25,20,'wood'); rect(im,4,21,25,21,'wood_d')
    # thermos (big, red & white) x 2..9
    th = G([
     "..GG...",
     ".GggG..",
     "MMMMMM.",
     "RrrrrqQ",
     "RrrrrqQ",
     "RwwwwgQ",
     "RwwwwgQ",
     "RwwwwgQ",
     "RrrrrqQ",
     "RrrrrqQ",
     "RrrrrqQ",
     ".qqqqq.",
    ],{'R':'red_l','r':'red','q':'red_d','Q':'red_d'})
    im.alpha_composite(sout(th), (1,0))   # 9 x 14 -> bottom at row 13? th 12 rows +2 outline = 14 => rows 0..13 overlaps table top row 13 (ok: sits on it)
    # jar x 13..18
    jar = G([
     ".rrrr.",
     ".qqqq.",
     "IiiiiI",
     "IYyyyi",
     "IYyzyi",
     "IyyyzI",
     "IyzyyI",
     "iiiiii",
    ],{'i':'glass','I':'glass_l'})
    im.alpha_composite(sout(jar), (12,3))   # 8x10 -> rows 3-12
    # tray + glasses x 21..28
    rect(im,20,12,28,12,'pb_d')
    for gx in (21,24,27):
        gl = G(["Iw.I","IOOi","IooI","iooi"] if False else ["IwI","iOi","ioi","ioi"],{'o':'or','O':'or_l'})
        im.alpha_composite(sout(gl,fixed='glass_d'), (gx-1,6))
    return im

def steam_frames():
    # 4 wisps rising, 8x12
    out=[]
    paths = [
      [(3,10),(4,9),(4,8),(3,7),(3,6),(4,5),(4,4),(3,3)],
      [(4,10),(3,9),(3,8),(4,7),(4,6),(3,5),(3,4),(4,3)],
      [(3,9),(4,8),(4,7),(3,6),(3,5),(4,4),(4,3),(3,2)],
      [(4,9),(3,8),(3,7),(4,6),(4,5),(3,4),(3,3),(4,2)],
    ]
    for i,p in enumerate(paths):
        im=new(8,12)
        for j,(x,y) in enumerate(p):
            put(im,x,y,'white' if j<6 else 'cloud_s')
        # second thinner wisp
        for j,(x,y) in enumerate(p[2:7]):
            put(im,x+2,y+1,'cloud_s' if j%2 else 'white')
        out.append(im)
    return out

HEAD_O = [
 "..gSS..",
 ".SSSSg.",
 ".SSSSSg",
 ".SkSSsG",
 "ssSSsss",
 ".SgdgSs",
 "..sgGs.",
]
def oldman(f):
    im = new(14,24)
    stamp(im, HEAD_O, 2, 0)
    # neck + tank top
    rows = [
     "....sss.....",
     "..swwwwwws..",
     "..swwwwwwwG.",
     "..wwwwwwwwG.",
     "..wwwgwwwwG.",
     "..wwwwwwwwG.",
     "..wwwwwwwGG.",
     "..awwwwwwGx.",
    ]
    stamp(im, rows, 1, 7)
    # trousers: hips + thigh to knee, rows 14-16 (thigh bottom row 16)
    rect(im,6,14,13,16,'wc_d'); rect(im,2,14,6,16,'wc_d')
    for x in range(2,14): put(im,x,14,'wc')
    for x in range(2,14): put(im,x,16,'wood_hl')
    put(im,13,15,'wood_hl'); put(im,13,14,'wood_hl'); put(im,12,15,'wood_hl')
    # shin (khaki to calf) rows 17-21, ankle skin 22, dep row 23
    for y in range(17,22):
        put(im,2,y,'wc'); put(im,3,y,'wc_d'); put(im,4,y,'wood_hl')
    for y in (22,):
        put(im,2,y,'sk_l'); put(im,3,y,'sk'); put(im,4,y,'sk_d')
    for x in range(0,6): put(im,x,23,'sh')
    put(im,0,23,'sh_l'); put(im,1,23,'sh_l'); put(im,5,23,'sh_d')
    # right arm (resting hand on knee) skip; drinking arm
    hand = [(3,12),(3,10),(2,7),(3,10)][f]
    hx,hy = hand
    # forearm from elbow (5,13) to hand
    ex,ey = 6,13
    for t in range(0,9):
        x = round(ex + (hx-ex)*t/8); y = round(ey + (hy-ey)*t/8)
        put(im,x,y,'sk'); put(im,x,y+1,'sk_d')
    for p in [(4,9),(4,10),(5,11),(5,12)]: put(im,*p,'sk')
    for p in [(5,9),(5,10),(6,11),(6,12)]: put(im,*p,'sk_d')
    # glass in hand (3x4), glass sits above/at hand
    gx,gy = hx-2, hy-3
    gl = G(["IwI","iOi","ioi","ioi"],{'o':'or','O':'or_l'})
    im.alpha_composite(gl,(gx,gy))
    put(im,hx,hy,'sk_l')   # fingers wrap
    if f==2: put(im,hx+1,hy,'sk_l')
    return im

if __name__=='__main__':
    t=sout(table())
    st=[stool_out('red'),stool_out('blue')]
    om=[sout(oldman(i)) for i in range(4)]
    sheet([t]+st+om+steam_frames(),scale=8,cols=5).save(SC+'tra.png')
    save_c('tea_stall',[t],16,24,notes='anchor = bottom of legs, centre. place x=TRA_DA_X+16 (sprite left=262), y=196. thermos top ~24px above')
    save_c('stool_red',[st[0]],4,9,notes='anchor = bottom centre')
    save_c('stool_blue',[st[1]],4,9,notes='anchor = bottom centre')
    save_c('oldman_tea',om,3,25,fps=3,notes='seated, faces left; anchor=sandal bottom row; sits on a stool (stool top row ~ thigh bottom row)')
    save_c('steam',steam_frames(),4,11,fps=4,notes='anchor bottom centre; place above thermos cap')
