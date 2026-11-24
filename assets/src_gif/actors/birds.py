from _common import *
SC='review/gif_style/_sheets/'
E={'t':'tc','g':'grey_l','a':'paper','f':'wood_l','W':'wood','D':'wood_d','y':'yl_d','l':'tc_d','k':'ink','T':'tc_d'}
def perch(f):
    if f==0:
        rows=[
         "..ttt.....",
         ".tkgg.....",
         "yggafffff.",
         ".aaaWWWfff",
         ".aaaWWWWDD",
         "..aaWWWDD.",
         "...l.l...",
        ]
    else:
        rows=[
         ".........",
         "..tttf...",
         ".tkggfff.",
         "yggaWfffD",
         ".aaaWWWDD",
         "..aaWWDD.",
         "...l.l...",
        ]
    return G(rows,E)
def fly(f):
    base=[
     "..ttk....",
     ".yggaffff",
     "..aaaWWWD",
     "...aaWDD.",
    ]
    im=new(10,9)
    stamp(im,base,0,4 if f in(0,3) else 3 if f==1 else 4,E)
    # wings
    if f==0: wing=[(4,3),(5,3),(5,2),(6,2),(6,1),(7,2),(7,3)]
    elif f==1: wing=[(4,2),(5,2),(5,1),(6,1),(6,0),(7,1),(7,2),(8,2)]
    elif f==2: wing=[(4,6),(5,6),(5,7),(6,7),(6,8),(7,7),(7,6)]
    else: wing=[(4,3),(5,3),(6,3)]
    for x,y in wing: put(im,x,y+ (0 if f!=1 else 0),'wood')
    if f in (0,1): 
        for x,y in wing[:1]: put(im,x,y,'wood_l')
    if f==2:
        for x,y in wing[:1]: put(im,x,y,'wood_l')
    return im
if __name__=='__main__':
    p=[sout(perch(i)) for i in (0,1)]; fl=[sout(fly(i)) for i in range(4)]
    sheet(p+fl,scale=14,cols=6).save(SC+'birds.png')
    save_c('sparrow_perch',p,5,p[0].height-1,fps=2,notes='perched, faces left (flip for right). anchor = feet row, centre')
    save_c('sparrow_fly',fl,6,5,fps=8,notes='flying, faces left (flip for right). anchor = body centre')
