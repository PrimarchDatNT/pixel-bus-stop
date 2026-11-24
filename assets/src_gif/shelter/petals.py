from _c import *
f = []
shapes = [
 [(0,1,"bl_l"),(1,0,"bl_hl"),(1,1,"bl"),(2,1,"bl"),(1,2,"bl_d")],
 [(0,0,"bl_l"),(1,1,"bl"),(2,2,"bl_d"),(1,0,"bl"),(0,1,"bl_d")],
 [(1,0,"bl_hl"),(1,1,"bl"),(1,2,"bl_d"),(0,1,"bl_l")],
 [(2,0,"bl_l"),(1,1,"bl"),(0,2,"bl_d"),(2,1,"bl"),(1,2,"bl_d")],
]
for sh in shapes:
    im = new(3, 3)
    for x, y, n in sh: put(im, x, y, n)
    f.append(im)
save_asset("shelter", "petals", f, fps=6, anchor=(1, 1), notes="Tumbling bract, 3x3, centre anchor (1,1); compositor spawns many.")
