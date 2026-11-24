from _c import *
import numpy as np
from scipy import ndimage as ndi
NF = 3
RAMP = ["bl_k", "bl_d", "bl", "bl_l", "bl_hl"]
YY, XX = np.mgrid[0:H, 0:W].astype(float)

def vn(seed, period):
    r = np.random.RandomState(seed)
    g = r.rand(int(H / period) + 4, int(W / period) + 4)
    v = ndi.map_coordinates(g, [YY / period + 1, XX / period + 1], order=3, mode="reflect")
    return (v - .5) * 2

# (cx, cy, rx, ry)
BLOBS = [(34, 90, 31, 46), (30, 60, 21, 22), (62, 70, 24, 22), (68, 100, 28, 26), (100, 86, 22, 23),
         (82, 128, 46, 24), (52, 134, 19, 16), (128, 104, 25, 21), (130, 130, 34, 22), (164, 90, 25, 38),
         (176, 64, 14, 17), (188, 116, 15, 24), (148, 108, 14, 14), (48, 48, 14, 11)]
SEG = [  # trunk + limbs (x,y) polylines, widths set in trunk()
]

def build_mask():
    F = np.full((H, W), -9.0); F2 = np.full((H, W), -9.0); sub = np.zeros((H, W), int)
    for i, (cx, cy, rx, ry) in enumerate(BLOBS):
        f = 1 - (((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2)
        m = f > F; F2 = np.where(m, F, np.maximum(F2, f)); F = np.where(m, f, F); sub = np.where(m, i, sub)
    global VALLEY
    VALLEY = np.clip(1 - (F - F2) / .22, 0, 1) * (F2 > .05)
    n2, n3, n1 = vn(1, 9), vn(2, 3.2), vn(3, 17)
    m0 = F > 0
    # scalloped lobes along the outline
    R = np.random.RandomState(5)
    d0 = ndi.distance_transform_edt(m0)
    edge = np.argwhere((d0 > 0) & (d0 <= 1.5))
    R.shuffle(edge)
    taken = []
    for (y, x) in edge:
        if y > 138 and x < 34: continue
        if y > 140: continue
        if any((x - a) ** 2 + (y - b) ** 2 < 100 for a, b in taken): continue
        taken.append((x, y))
        r = R.randint(6, 12)
        # push lobe centre slightly outward (away from the nearest interior)
        F = np.maximum(F, 1 - (((XX - x) / r) ** 2 + ((YY - y) / (r * .9)) ** 2) - .12)
    m = (F + .16 * n2 + .08 * n3 + .08 * n1) > 0.03
    # roof pour: flat-ish scalloped lower lip on the shelter
    lip = 151 + np.round(1.6 * vn(4, 6))
    m &= ~((XX >= 34) & (XX <= 177) & (YY > lip))
    # cat clearing
    cut = 137 + np.round(1.2 * vn(5, 5))
    m &= ~((XX >= 146) & (XX <= 170) & (YY > cut))
    # left of shelter the crown ends higher so the trunk shows
    low = 137 + np.round(2 * vn(6, 6))
    m &= ~((XX < 34) & (YY > low))
    m &= ~((XX > 177) & (YY > 140 + np.round(2 * vn(7, 5))))
    # branch windows
    for (cx, cy, rx, ry) in WINDOWS:
        m &= ~((((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2) < 1 + .25 * n3)
    # tiny sky/gaps holes near the rim
    d = ndi.distance_transform_edt(m)
    hn = vn(8, 4)
    m &= ~((hn > .84) & (d > 3) & (d < 11))
    # cleanup
    for _ in range(2):
        nb = ndi.convolve(m.astype(int), np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]), mode="constant")
        m = np.where(m & (nb <= 1), False, m); m = np.where(~m & (nb >= 3), True, m)
    lab, n = ndi.label(m)
    sz = ndi.sum(m, lab, range(1, n + 1))
    for i, s in enumerate(sz):
        if s < 30: m[lab == i + 1] = False
    return m, sub

WINDOWS = [(34, 136, 7, 6), (15, 122, 6, 7), (46, 114, 7, 6), (15, 104, 5, 5), (58, 100, 6, 5), (22, 131, 5, 4)]

def tones(m, sub):
    R = np.random.RandomState(21)
    # jittered-grid cluster centres
    SP = 7.2
    cs = []
    for gy in np.arange(-4, H + 8, SP):
        for gx in np.arange(-4, W + 8, SP):
            off = SP * .5 if int(gy / SP) % 2 else 0
            cs.append((gx + off + R.uniform(-2.2, 2.2), gy + R.uniform(-2.2, 2.2), R.uniform(-.4, .4), R.uniform(4.6, 6.2)))
    cs = np.array(cs)
    wx = XX + 2.2 * vn(31, 8); wy = YY + 2.2 * vn(32, 8)
    best = np.full((H, W), 1e9); cid = np.zeros((H, W), int)
    for i, (cx, cy, b_, r) in enumerate(cs):
        dd = (wx - cx) ** 2 + (wy - cy) ** 2
        mk = dd < best; best = np.where(mk, dd, best); cid = np.where(mk, i, cid)
    cx = cs[cid, 0]; cy = cs[cid, 1]; cb = cs[cid, 2]; cr = cs[cid, 3]
    u = (wx - cx) / cr; v_ = (wy - cy) / cr
    lit = -(u * .62 + v_ * .78)
    ml = np.zeros((H, W))
    for i, (bx, by, rx, ry) in enumerate(BLOBS):
        l = -((XX - bx) / rx) * .6 - ((YY - by) / ry) * .8
        ml = np.where(sub == i, l, ml)
    ml = ml * .8 - (YY - 100) / 120 * .55 - (XX - 90) / 250 * .25
    fine = vn(41, 2.5)
    R2 = np.random.RandomState(77); SP2 = 3.8
    c2 = np.array([(gx + (SP2 / 2 if int(gy / SP2) % 2 else 0) + R2.uniform(-1, 1), gy + R2.uniform(-1, 1)) for gy in np.arange(-4, H + 8, SP2) for gx in np.arange(-4, W + 8, SP2)])
    b2 = np.full((H, W), 1e9); id2 = np.zeros((H, W), int)
    for i, (qx, qy) in enumerate(c2):
        dd = (wx - qx) ** 2 + (wy - qy) ** 2
        mk = dd < b2; b2 = np.where(mk, dd, b2); id2 = np.where(mk, i, id2)
    lit2 = -((wx - c2[id2, 0]) * .62 + (wy - c2[id2, 1]) * .78) / 2.6
    v = lit * .62 + cb + ml * .75 + fine * .1 + lit2 * .26 - .02 - VALLEY * .55
    T = np.where(v > .46, 3, np.where(v > -.30, 2, 1))
    T = np.where(v < -.95, 0, T)
    T = np.where(v > 1.12, 4, T)
    T = np.where(m, T, -1)
    d = ndi.distance_transform_edt(m)
    ext = ndi.binary_dilation(~ndi.binary_fill_holes(m) , iterations=1) | (~m & (ndi.label(~m)[0] == ndi.label(~m)[0][0, 0]))
    ext = ndi.label(~m)[0] == ndi.label(~m)[0][0, 0]
    def run(dx, dy, tgt):
        r = np.full((H, W), 9)
        for k in range(6, 0, -1):
            sh = np.roll(tgt, (dy * k, dx * k), (0, 1))
            r = np.where(sh, k, r)
        return r
    ul = np.minimum(np.minimum(run(1, 1, ext), run(1, 0, ext)), run(0, 1, ext))
    dn = run(0, -1, ~m)
    hn = vn(21, 3)
    T = np.where(m & (ul <= 1) & (v > -.15) & (hn > -.3) & (YY < 138), 4, T)
    T = np.where(m & (ul <= 3) & (ul > 1) & (T < 3) & (v > -.45), 3, T)
    T = np.where(m & (dn <= 2) & (T > 1), 1, T)
    T = np.where(m & (dn <= 1) & (hn > -.3), 0, T)
    T = np.where(m & (T == 0) & (d > 3) & (v > -.95), 1, T)
    for _ in range(2):
        out = T.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if T[y, x] < 0: continue
                nb = [a for i, a in enumerate(T[y - 1:y + 2, x - 1:x + 2].ravel()) if i != 4 and a >= 0]
                if len(nb) >= 5:
                    vals, cnt = np.unique(nb, return_counts=True)
                    if cnt.max() >= len(nb) - 1 and vals[cnt.argmax()] != T[y, x] and T[y, x] != 0:
                        out[y, x] = vals[cnt.argmax()]
        T = out
    return T, d

def disc(T, cx, cy, r, ry=None, ramp="leaf"):
    pass

def leaf_clump(im, cx, cy, r, f=0):
    px = im.load()
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            u, v = (x - cx) / (r + .3), (y - cy) / (r * .85 + .3)
            if u * u + v * v > 1: continue
            lit = -u * .6 - v * .8
            nm = "leaf_hl" if lit > .75 and r >= 3 else "leaf_l" if lit > .25 else "leaf" if lit > -.4 else "leaf_d"
            if u * u + v * v > .72 and lit < -.5: nm = "leaf_k"
            if 0 <= x < W and 0 <= y < H: px[x, y] = c(nm)

def bract(im, cx, cy, r, f=0):
    px = im.load()
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            u, v = (x - cx) / (r + .3), (y - cy) / (r * .9 + .3)
            if u * u + v * v > 1: continue
            lit = -u * .6 - v * .8
            nm = "bl_hl" if lit > .8 and r >= 3 else "bl_l" if lit > .3 else "bl" if lit > -.35 else "bl_d"
            if u * u + v * v > .75 and lit < -.45: nm = "bl_k"
            if 0 <= x < W and 0 <= y < H: px[x, y] = c(nm)

LEAFPOS0 = [(18,108),(8,96),(26,86),(14,70),(30,50),(48,44),(60,40),(82,46),(98,56),(120,62),(130,76),(142,86),(152,92),(160,74),(176,70),
           (186,92),(194,104),(196,118),(182,132),(176,106),(150,130),(132,118),(118,134),(100,120),(104,146),(86,138),(70,142),(58,146),
           (44,126),(36,112),(70,112),(88,98),(110,100),(140,108),(66,84),(20,128),(40,146),(124,146),(170,128),(164,60),(90,140)]

def bloom_layer():
    m, sub = build_mask()
    T, d = tones(m, sub)
    im = new(W, H); px = im.load()
    for y in range(H):
        for x in range(W):
            if T[y, x] >= 0: px[x, y] = c(RAMP[T[y, x]])
    # leaf clusters: tucked at edges and in shaded gaps
    for i, (x, y) in enumerate(LEAFPOS):
        if not (0 <= y < H and 0 <= x < W and m[y, x]): continue
        if d[y, x] < 3: continue
        if i % 2: continue
        leaf_clump(im, x, y, 2); leaf_clump(im, x + 3, y + 1, 1 if i % 4 else 2); leaf_clump(im, x - 2, y + 2, 1)
    # keep silhouette: erase anything outside mask+? leaf near edge may spill out, ok, then re-clip
    a = np.array(im)[:, :, 3] > 0
    return im, m, d

def sway(base, m, d, f):
    """frame f: static core (eroded 3) + edge blocks shifted by 1 px in a travelling wave."""
    if f == 0: return base.copy()
    out = new(W, H); op = out.load(); bp = base.load()
    core = d >= 4
    under = d >= 2
    for y in range(H):
        for x in range(W):
            if under[y, x]: op[x, y] = bp[x, y]
    # edge pixels: shift by block phase
    BS = 11
    for y in range(H):
        for x in range(W):
            if core[y, x]: continue
            p = bp[x, y]
            if not p[3]: continue
            ph = ((x // BS) + (y // (BS + 2))) % 3
            t = (f + ph) % 3
            dx, dy = [(0, 0), (1, 0), (0, 1)][t]
            X, Y = x + dx, y + dy
            if 0 <= X < W and 0 <= Y < H and not core[Y, X]:
                op[X, Y] = p
            elif 0 <= X < W and 0 <= Y < H:
                pass
    return out

LEAFPOS = LEAFPOS0[::1]
