from _common import *
SC='review/gif_style/_sheets/'
X={'L':'tc_l'}
HEAD = [
 "...hhhhh.....",
 "..hhlllhh....",
 "..hhhhhhhh...",
 "..SSkShhhhh..",
 ".sSSSShhhhhh.",
 "..SSLShhh.hl.",
 "...sSsshh..h.",
]
BODY = [
 "....ss.......",   # neck r7 (relative to body start)
 "...YYyyyyz...",
 "..SYyyyyyyz..",
 "..sSYyyyyyz..",
 "..ssyyyyyyzz.",
 "..sSyyyyyyzz.",
 "...yyyyyyyz..",
 "...yyyyyyzz..",
 "...bbbbbbbbb.",   # shorts
 "SSsbBbbbbbbbn",
 "SssbbbbbbbbbN",
]
def build(f=0):
    im = new(14, 27)
    hd = 1 if f else 0
    stamp(im, HEAD, 0, hd, X)
    stamp(im, BODY, 0, 7, X)
    # fix ponytail & neck overlap when head dips
    if f:
        put(im,4,7,'sk_d')
    # arm + phone (forearm rising to phone at left)
    for p in [(5,11),(5,12),(4,12),(3,12),(3,11),(2,11),(2,10)]: put(im,*p,'sk')
    for p in [(5,10),(4,11)]: put(im,*p,'sk_l')
    put(im,6,11,'sk_d')
    # phone
    stamp(im, ["DI","DI","DD"], 0, 9)
    if f: put(im,1,10,'white'); put(im,1,11,'glass_l')
    # shins + shoes
    legs = [
     "SSs.......",
     "Sss.......",
     "Ssd.......",
     "Ssd.......",
     "sdd.......",
     "wwg.......",
     "wgG.......",
    ]
    stamp(im, ["...", "..."],0,0)
    for i,r in enumerate([".SS", ".Ss", ".Ss", ".Sd", ".sd", ".sd"]):
        stamp(im,[r],0,19+i) if False else None
    for i in range(6):
        for dx,col in ((1,'sk_l'),(2,'sk'),(3,'sk_d')):
            put(im,dx,19+i,col)
    stamp(im, ["wwwg.","wGGGD"], 0, 25)
    return im

if __name__=='__main__':
    fr=[sout(build(i)) for i in (0,1)]
    save_asset('actors','woman_wait',fr,fps=2,anchor=(9,19),notes='seated, faces left; outline row 19 = thigh bottom, place on SEAT_Y-1. Legs dangle ~6px below seat')
    sheet(fr,scale=14).save(SC+'woman.png')
