from _c import *
import random, math
from PIL import Image
R = random.Random(7)
NF = 3
RAMP = ["bl_k", "bl_d", "bl", "bl_l", "bl_hl"]
LEAF = ["leaf_k", "leaf_d", "leaf", "leaf_l", "leaf_hl"]

def hsh(x, y, s=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) % 1000 / 1000.0

class Clump:
    def __init__(s, cx, cy, r, sway=None, leaf=False, seed=0, ry=None, depth=1, halo=True):
        s.cx, s.cy, s.r, s.sway, s.leaf, s.seed, s.depth, s.halo = cx, cy, r, sway, leaf, seed, depth, halo
        s.ry = ry or r * 0.85
    def off(s, f):
        if s.sway is None: return 0, 0
        ph, amp = s.sway
        t = (f + ph) % 3
        return ([0, 1, 0][t] * amp, [0, 0, 1][t] if amp else 0)
    def draw(s, im, f):
        dx, dy = s.off(f)
        cx, cy, r, ry = s.cx, s.cy, s.r, s.ry
        ramp = LEAF if s.leaf else RAMP
        px = im.load()
        dark = ramp[0]
        # dark halo on lower/right rim carves a gap against what is already painted
        if s.halo:
            for y in range(int(cy - ry - 2), int(cy + ry + 3)):
                for x in range(int(cx - r - 2), int(cx + r + 3)):
                    u, v = (x - cx) / (r + 1.3), (y - cy) / (ry + 1.3)
                    if u * u + v * v <= 1.0 and (u * .6 + v * .8) > -.15:
                        X, Y = x + dx, y + dy
                        if 0 <= X < W and 0 <= Y < H and px[X, Y][3]:
                            px[X, Y] = c(dark)
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                u, v = (x - cx) / r, (y - cy) / ry
                n = hsh((x + s.seed) // 4, (y + s.seed) // 3, s.seed)
                n2 = hsh(x, y, s.seed + 5)
                d = u * u + v * v + (n - .5) * .5 + (n2 - .5) * .12
                if d > 1.0: continue
                lit = (-u * .62 - v * .78)
                val = lit * .55 + (n - .5) * .5 - d * .5 + .12
                val += (-(s.cx - 170) / 300 - (s.cy - 128) / 40) * .35      # lower / inner -> darker
                val += (s.depth - 1) * .3                                    # back tier darker, front lighter
                if val > .42: t = 3
                elif val > -.08: t = 2
                elif val > -.5: t = 1
                else: t = 0
                if d > .78 and lit < -.1: t = min(t, 1)
                if d > .92 and lit < -.3: t = 0
                if s.leaf: t = max(1, min(t + 1, 3)) if t else 1
                X, Y = x + dx, y + dy
                if 0 <= X < W and 0 <= Y < H:
                    px[X, Y] = c(ramp[t])

def region_top(x):
    pts = [(88,146),(94,134),(102,124),(114,116),(128,109),(142,105),(156,106),(170,109),(184,111),(196,117),(204,128),(207,147),
           (224,147),(226,140),(232,130),(240,126),(248,132),(250,146)]
    for (a,ya),(b,yb) in zip(pts, pts[1:]):
        if a <= x <= b: return ya + (yb-ya)*(x-a)/(b-a)
    return 150

clumps = []
ri = R.randint
# ---- tier 0: dark back mass filling the whole envelope
for y in range(114, 150, 7):
    for xo in range(0, 170, 10):
        x = 90 + xo + (5 if (y // 7) % 2 else 0) + ri(-2, 2)
        yy = y + ri(-2, 2)
        if yy < region_top(x) + 6 or x < 92 or x > 246: continue
        if 207 < x < 224 and yy < 150: continue
        clumps.append(Clump(x, yy, ri(7, 9), None, seed=ri(0, 99), depth=0))
# ---- tier 1: mid clumps
for y in range(112, 146, 6):
    for xo in range(0, 170, 10):
        x = 92 + xo + (5 if (y // 6) % 2 else 0) + ri(-2, 2)
        yy = y + ri(-2, 2)
        if yy < region_top(x) + 4 or x < 93 or x > 246: continue
        if 207 < x < 224 and yy < 152: continue
        clumps.append(Clump(x, yy, ri(5, 7), None, seed=ri(0, 99), depth=1))
# ---- tier 2: bright top-lit clumps along the crown (sway on the outer ones)
for x in range(96, 247, 8):
    if 205 < x < 226: continue
    top = region_top(x)
    sw = ((x // 8) % 3, 1) if (x < 112 or x > 228 or ri(0, 2) == 0) else None
    clumps.append(Clump(x + ri(-1, 1), top + ri(3, 5), ri(4, 6), sw, seed=ri(0, 99), depth=2))
# balcony spill (upper tendrils)
for (x, y, r) in [(138, 103, 5), (151, 101, 4), (164, 104, 5), (177, 108, 4), (128, 107, 4)]:
    clumps.append(Clump(x, y, r, ((x // 5) % 3, 1), seed=ri(0, 99), depth=2))
# ---- leaf clusters between clumps and at the edges
def leafy(x, y, sw=None):
    for (ox, oy, r) in [(0, 0, 3), (3, 1, 2), (-2, 2, 2)]:
        clumps.append(Clump(x + ox, y + oy, r, sw, leaf=True, seed=ri(0, 99), depth=1, halo=True))
for (x, y) in [(110,126),(124,118),(136,122),(148,112),(158,126),(172,116),(186,122),(196,130),(120,138),(134,142),(150,138),(166,136),(182,138),(196,142),(104,140),(230,136),(240,140),(100,132),(142,128),(178,128),(214,132),(160,108),(120,110),(188,114),(232,128)]:
    sw = ((x // 9) % 3, 1) if (x < 112 or x > 228) else None
    leafy(x, y, sw)
# front lip along the roof edge
for x in range(100, 206, 8):
    clumps.append(Clump(x + ri(-1, 1), 146 + ri(-1, 1), ri(5, 6), None, seed=ri(0, 99), depth=1))
for x in (226, 233, 240):
    clumps.append(Clump(x, 148 + ri(-1, 1), 5, None, seed=ri(0, 99), depth=1))
for x in (107, 156, 169, 197):
    leafy(x, 150, None)
# left cascade
for (x, y, r, sw) in [(96, 150, 6, (0,1)), (99, 157, 5, (1,1)), (94, 159, 4, (2,1)), (91, 153, 4, (2,1))]:
    clumps.append(Clump(x, y, r, sw, seed=ri(0, 99), depth=1))

# ---- front drapes: separate hanging strands (thin vine + spaced bract clusters + leaf bits)
strands = []
class Strand:
    sway = True
    def __init__(s, x, L, ph): s.x, s.L, s.ph = x, L, ph
    def draw(s, im, f):
        t = (f + s.ph) % 3
        dx = [0, 1, 0][t]; dy = [0, 0, 1][t]
        for yy in range(150, 150 + s.L):
            put(im, s.x + dx + (1 if (yy // 4) % 2 else 0), yy + (dy if yy > 152 else 0), "leaf_d")
        k = 0
        yy = 151
        while yy < 150 + s.L:
            side = -2 if k % 2 == 0 else 2
            r = 3 if yy < 150 + s.L - 6 else 2
            Clump(s.x + side + (1 if side > 0 else 0), yy + 2, r, ((s.ph) % 3, 1), seed=s.x + k, depth=1).draw(im, f)
            if k % 2 == 1:
                Clump(s.x - side, yy + 5, 2, ((s.ph) % 3, 1), leaf=True, seed=s.x + k, depth=1).draw(im, f)
            yy += 5; k += 1
        # loose tip bract
        t_ = (s.x + dx, 150 + s.L + 1 + dy)
        put(im, t_[0], t_[1], "bl"); put(im, t_[0] + 1, t_[1], "bl_l"); put(im, t_[0], t_[1] + 1, "bl_d")
for i, (x, L) in enumerate([(103,17),(112,9),(152,10),(160,4),(168,4),(176,4),(234,22),(241,12)]):
    strands.append(Strand(x, L, i % 3))

clumps.sort(key=lambda c_: (c_.depth, c_.cy))
def trunk(im):
    pts = []
    for i in range(0, 38):
        y = 184 - i
        x = 114 + round(2.6 * math.sin(i / 4.2)) - (1 if i > 30 else 0)
        pts.append((x, y))
    for (x, y) in pts:
        w = 3
        rect(im, x - 1, y, x - 1 + w - 1, y, "trunk")
        put(im, x - 1, y, "trunk_l"); put(im, x - 1 + w - 1, y, "trunk_d")
    # knots / branch stubs
    for (x, y) in [(112, 178), (117, 170), (112, 163), (118, 157)]:
        rect(im, x, y, x + 1, y, "trunk_d"); put(im, x, y - 1, "trunk")
    # branches into mass
    line(im, 114, 150, 108, 146, "trunk"); line(im, 115, 150, 121, 147, "trunk")

def planter(im):
    x0, x1 = BOUGAINVILLEA_PLANTER
    rect(im, x0 - 1, 184, x1 + 1, 186, "tc_l"); rect(im, x0 - 1, 186, x1 + 1, 186, "tc")
    rect(im, x0, 187, x1, STAND_Y - 1, "tc"); rect(im, x0, 187, x0, STAND_Y - 1, "tc_l")
    rect(im, x1 - 2, 187, x1, STAND_Y - 1, "tc_d"); rect(im, x0, STAND_Y, x1, STAND_Y, "tc_d")
    rect(im, x0 - 1, 184, x1 + 1, 184, "tc_l")
    rect(im, x0, 187, x1, 187, "tc_d")
    # soil + leaf tuft
    rect(im, x0 + 1, 183, x1 - 1, 183, "wood_d")
    for (x, y, r) in [(104, 180, 3), (110, 179, 3), (101, 182, 2), (113, 182, 2)]:
        Clump(x, y, r, None, leaf=True, seed=3).draw(im, 0)
    for (x, y) in [(107, 177), (102, 177), (112, 176)]:
        Clump(x, y, 2, None, seed=x).draw(im, 0)

def post(im):
    """rim light / under-shade passes on the silhouette, hand-feel."""
    px = im.load()
    out = im.copy(); op = out.load()
    pink = {c(n)[:3]: i for i, n in enumerate(RAMP)}
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            p = px[x, y]
            if p[3] == 0 or p[:3] not in pink: continue
            i = pink[p[:3]]
            if px[x, y + 1][3] == 0 and i >= 2:         # underside rim
                op[x, y] = c("bl_d")
            elif px[x, y + 1][3] == 0 and i == 1:
                op[x, y] = c("bl_k")
            elif px[x, y - 1][3] == 0 and px[x - 1, y - 1][3] == 0 and i == 3 and y < 140 and hsh(x // 2, y, 9) < .8 and px[x - 1, y][3] == 0 or (px[x, y - 1][3] == 0 and px[x - 1, y][3] == 0 and i == 3 and y < 138 and x < 200 and hsh(x, y, 2) < .6):
                op[x, y] = c("bl_hl")
    return out

def loose(im, f):
    # single bracts hanging / drifting at the edges
    for k, (x, y) in enumerate([(88, 142), (92, 170), (101, 175), (214, 156), (222, 154), (252, 140), (246, 153), (152, 168), (110, 168), (200, 166)]):
        yy = y + [0, 1, 0][(f + k) % 3]
        put(im, x, yy, "bl_l"); put(im, x + 1, yy, "bl"); put(im, x, yy + 1, "bl"); put(im, x + 1, yy + 1, "bl_d")
        if k % 3 == 0: put(im, x, yy, "bl_hl")

def frame(f):
    im = canvas()
    # trunk goes first so bloom hides its upper end
    trunk(im); planter(im)
    for cl in clumps: cl.draw(im, f)
    for st in strands: st.draw(im, f)
    im = post(im)
    loose(im, f)
    return im

if __name__ == "__main__":
    frames = [frame(f) for f in range(NF)]
    save_asset("shelter", "bougainvillea", frames, fps=3, anchor=(0, 0),
               notes="Trunk + planter static; core mass static; edge clumps/drapes sway 1px over 3 frames.")
