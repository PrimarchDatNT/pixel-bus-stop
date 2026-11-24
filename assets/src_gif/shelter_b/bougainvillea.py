from bloom import *
import math

def stamp(im, cx, cy, w, shade=True):
    px = im.load(); r = w / 2
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            dx = x - cx
            if dx * dx + (y - cy) ** 2 > (r + .4) ** 2: continue
            nm = "trunk_l" if dx < -r * .35 else "trunk_d" if dx > r * .3 else "trunk"
            px[x, y] = c(nm)

def stroke(im, pts, w0, w1, wig=0.0):
    n = len(pts) - 1
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = max(abs(x1 - x0), abs(y1 - y0)) * 2
        for k in range(int(L) + 1):
            t = k / max(L, 1); g = (i + t) / n
            stamp(im, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, w0 + (w1 - w0) * g)

TRUNK = [(29, 187), (25, 179), (30, 171), (34, 163), (29, 155), (24, 148), (26, 141)]
LIMBS = [[(26, 143), (22, 139), (16, 131), (13, 123), (13, 115), (16, 107), (14, 98)],
         [(27, 143), (33, 140), (38, 132), (44, 124), (49, 115), (55, 106), (60, 98)],
         [(46, 120), (40, 112), (36, 104)], [(14, 118), (6, 112), (3, 105)],
         [(52, 110), (60, 112), (66, 108)]]

def windows_back(im):
    px = im.load()
    for (cx, cy, rx, ry) in WINDOWS:
        for y in range(cy - ry - 3, cy + ry + 4):
            for x in range(cx - rx - 3, cx + rx + 4):
                u = ((x - cx) / (rx + 2.5)) ** 2 + ((y - cy) / (ry + 2.5)) ** 2
                if u <= 1: px[x, y] = c("bl_k" if hsh(x, y, 3) < .6 or u > .6 else "bl_d")

def hsh(x, y, s=0): return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) % 1000 / 1000.0

def trunk(im):
    stroke(im, TRUNK, 11, 8)
    # root flare
    for dx, w in ((-5, 3), (5, 3)):
        stamp(im, 29 + dx, 183, w + 1)
    for L, (a, b) in zip(LIMBS, [(7, 5), (7, 5), (4, 3), (4, 3), (4, 3)]): stroke(im, L, a, b)
    px = im.load()
    # bark: dark knots + highlight flecks
    for (x, y) in [(28, 176), (31, 170), (29, 163), (27, 157), (30, 182), (27, 150), (24, 142), (36, 136), (15, 126), (41, 128)]:
        put(im, x, y, "trunk_d"); put(im, x + 1, y, "trunk_d"); put(im, x, y + 1, "trunk_d")
    for (x, y) in [(26, 178), (29, 168), (27, 160), (26, 148)]:
        put(im, x, y, "wood_hl")
    # a twig stub
    line(im, 33, 168, 37, 165, "trunk_d"); line(im, 25, 160, 21, 157, "trunk_d")

def planter(im):
    x0, x1 = BOUGAINVILLEA_PLANTER
    rect(im, x0 - 1, 185, x1 + 1, 186, "tc"); rect(im, x0 - 1, 185, x1 + 1, 185, "tc_l")
    rect(im, x0, 187, x1, STAND_Y - 1, "tc"); rect(im, x0, 187, x0 + 1, STAND_Y - 1, "tc_l")
    rect(im, x1 - 2, 187, x1, STAND_Y - 1, "tc_d"); rect(im, x0, 187, x1, 187, "tc_d")
    rect(im, x0, STAND_Y, x1, STAND_Y, "tc_d"); rect(im, x0 + 2, 190, x1 - 3, 190, "tc_l")
    rect(im, x0, 184, x1, 184, "wood_d")
    for (x, y, r) in [(24, 182, 2), (35, 182, 2), (19, 180, 2)]:
        leaf_clump(im, x, y, r)
    bract(im, 21, 178, 2); bract(im, 37, 178, 2)

STRANDS = [  # x, y0, L
    (40, 151, 22), (45, 151, 14), (53, 151, 6), (60, 151, 5), (67, 151, 7), (74, 151, 4), (81, 151, 10),
    (113, 151, 4), (123, 151, 5), (133, 151, 3), (141, 151, 5), (174, 151, 11), (168, 151, 5),
    (7, 134, 22), (14, 137, 12), (20, 137, 28), (181, 138, 14), (189, 134, 22), (196, 132, 10), (88, 151, 3), (106, 151, 3)]

def strand(im, x, y0, L, ph, f):
    t = (f + ph) % 3
    sdx = [0, 1, 0][t]; sdy = [0, 0, 1][t]
    px = im.load()
    for yy in range(y0, y0 + L):
        k = yy - y0
        ox = sdx if k > 3 else 0
        put(im, x + ox + (1 if (yy // 5) % 2 else 0), yy + (sdy if k > 5 else 0), "leaf_d")
    k = 0; yy = y0 + 2
    while yy < y0 + L - 1:
        side = -2 if k % 2 == 0 else 2
        r = 3 if yy < y0 + L - 7 else 2
        ox = sdx if yy - y0 > 3 else 0
        bract(im, x + side + ox + (1 if side > 0 else 0), yy + 2 + (sdy if yy - y0 > 5 else 0), r)
        if k % 2 == 1: leaf_clump(im, x - side + ox, yy + 5 + sdy, 2)
        yy += 5; k += 1
    tx, ty = x + sdx, y0 + L + 1 + sdy
    put(im, tx, ty, "bl_l"); put(im, tx + 1, ty, "bl"); put(im, tx, ty + 1, "bl_d")

LOOSE = [(2, 112), (4, 146), (9, 160), (44, 36), (60, 34), (110, 54), (140, 74), (150, 66), (196, 82), (200, 112), (198, 140), (88, 156), (30, 190), (36, 186), (178, 156), (120, 156)]

def loose(im, f):
    for k, (x, y) in enumerate(LOOSE):
        yy = y + [0, 1, 0][(f + k) % 3]
        put(im, x, yy, "bl_l"); put(im, x + 1, yy, "bl"); put(im, x, yy + 1, "bl"); put(im, x + 1, yy + 1, "bl_d")
        if k % 3 == 0: put(im, x, yy, "bl_hl")

_cache = {}
def frames():
    base, m, d = bloom_layer()
    out = []
    for f in range(NF):
        im = new(W, H)
        windows_back(im); trunk(im); planter(im)
        im.alpha_composite(sway(base, m, d, f))
        for i, (x, y0, L) in enumerate(STRANDS): strand(im, x, y0, L, i % 3, f)
        loose(im, f)
        out.append(im)
    return out

if __name__ == "__main__":
    fr = frames()
    save_asset("shelter", "bougainvillea", fr, fps=3, anchor=(0, 0),
               notes="HERO. Trunk/planter/core static; edge blocks + drapes sway 1px over 3 frames.")
