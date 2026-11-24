from _common import *
SC='review/gif_style/_sheets/'
X={'P':'wb_l','Q':'wb','C':'wb_d'}
HEAD=[
 "....hhhhh....",
 "...hhhhhhh...",
 "...hhhhhhh...",
 "...hSSSSSh...",
 "..SSkSSSkSS..",
 "...SSSsSSS...",
 "...SSdddSS...",
 "....ssSss....",
]
BODY=[
 ".....sss.....",
 ".PPPPsSsPPPP.",
 "PPPPPPSPPPPPQ",
 "PPPPPPPPPPPQQ",
 ".PPPPPPPPPQQ.",
 ".PPPPPPPPQQC.",
 ".PPQPPPPPQQC.",
 ".PPQPPPPPQQC.",
 ".PPPPPPPPQQC.",
 ".PPPPPPPPQQC.",
]
def build(f):
    im=new(21,20)
    stamp(im,HEAD,1,0,X)
    stamp(im,BODY,1,8,X) if False else None
    # body rows start y=8 (neck row is part of HEAD last row; BODY first row neck overlap skip)
    stamp(im,BODY[1:],1,9,X)
    # left arm (viewer left): rests on counter
    for p in [(1,10),(1,11),(2,11)]: put(im,*p,'wb')
    for y in range(12,17): put(im,2,y,'sk'); 
    for y in range(12,17): put(im,3,y,'sk_d')
    put(im,2,17,'sk_l'); put(im,3,17,'sk_l'); put(im,4,17,'sk')
    # right arm raised with fan
    for p in [(12,10),(13,10),(12,11),(13,11)]: put(im,*p,'wb')
    put(im,13,9,'wb'); 
    for p in [(14,9),(14,8),(14,7)]: put(im,*p,'sk')
    put(im,15,8,'sk_d'); put(im,15,7,'sk_d')
    put(im,14,6,'sk_l')
    # fan: handle + head
    cx,cy,rx,ry = [(16,2,3,3),(17,3,2,3),(16,1,3,3)][f]
    # fan handle
    put(im,14,5,'wood_l'); put(im,14,4,'wood_l') if f!=1 else None
    ellipse(im,cx-rx,cy-ry,cx+rx,cy+ry,'yl_l')
    # rim and ribs
    ImageDraw_ = None
    for y in range(cy-ry,cy+ry+1):
        for x in range(cx-rx,cx+rx+1):
            if im.getpixel((x,y))[3] and (x==cx-rx or x==cx+rx or y==cy-ry):
                put(im,x,y,'or_l')
    for y in range(cy-ry+1,cy+ry): put(im,cx,y,'yl')
    put(im,cx-1,cy,'white'); 
    return im
if __name__=='__main__':
    fr=[sout(build(i)) for i in range(3)]
    for f in fr:
        for x in range(f.width): f.putpixel((x,f.height-2),f.getpixel((x,f.height-2)) if False else f.getpixel((x,f.height-2)))
    # drop the bottom outline row (cut line is hidden behind the counter)
    fr=[f.crop((0,0,f.width,f.height-1)) for f in fr]
    for f in fr:
        for x in range(f.width): pass
    sheet(fr,scale=12).save(SC+'shop.png')
    save_c('shopkeeper',fr,9,fr[0].height-2,fps=4,notes='front view, waist-up; anchor = bottom row at waist, centre. waist is hidden behind the counter top')
