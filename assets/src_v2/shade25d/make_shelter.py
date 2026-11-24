from common import *
import numpy as np
L = default_lib()
W, H = 420, 250
OX, OY, CW, CH = 180, 104, 225, 136      # crop box in scene coords
b = Buf(W, H, L)
rng = np.random.RandomState(21)

# ---- back wall: glass panels between posts
b.box(216, 172, 370, 225, 'glass', z=2, bevel=1.5, bulge_y=0.25)
g = b.mask_rect(216, 172, 370, 225)
b.glare(g, offset=10, period=26, bands=((0, 5, 0.17), (8, 2, 0.26)), slope=1.0)
# back posts
for x0 in (216, 247, 339, 366):
    b.cyl_v(x0, 172, x0 + 4, 225, 'metal_dark', z=5, cap=1)
# base rail
b.box(216, 218, 370, 225, 'metal_dark', z=4, bevel=1.5, bulge_y=0.3)
# map board (left) and ad light box (right)
b.box(222, 179, 244, 217, 'metal_dark', z=7, bevel=1.5)
b.box(224, 181, 242, 215, 'paper_map', z=8, bevel=1)
for (x0, y0, x1, y1, mt) in ((226, 186, 240, 186, 'sign_red'), (226, 196, 238, 196, 'sign_blue'), (232, 183, 232, 212, 'sign_green'),
                              (226, 206, 241, 206, 'sign_yellow')):
    b.decal(b.mask_line([(x0, y0), (x1, y1)]), mt)
for (x, y) in ((232, 186), (232, 196), (232, 206)):
    b.decal(b.mask_ellipse(x + .5, y + .5, 1.6, 1.6), 'sign_white')
b.box(330, 179, 364, 220, 'metal_dark', z=7, bevel=1.5)
b.box(332, 181, 362, 218, 'sign_blue', z=8, bevel=1, bulge_y=0.2, bias=-0.08)
b.decal(b.mask_ellipse(347, 226, 17, 11) & b.mask_rect(332, 207, 362, 218), 'sign_white', bias=-0.05)
b.decal(b.mask_rect(344, 207, 351, 216), 'sign_red', bias=0.0)
b.hot(335, 184, 2, 1, 'sign_blue')
b.text(337, 183, "SỮA", 'sign_yellow')
b.text(336, 199, "TƯƠI", 'sign_yellow')
# under-roof shade (hand placed)
b.tone(b.mask_rect(216, 172, 370, 180), -0.22)
b.tone(b.mask_rect(216, 180, 370, 186), -0.10)

# ---- seats
for x0 in (256, 276, 296):
    b.box(x0, 203, x0 + 16, 221, 'plastic_blue', z=10, bevel=(4, 4, 6, 3), bulge_x=0.35, bulge_y=0.25)
    b.tone(b.mask_ellipse(x0 + 8, 211, 5.5, 6.5), -0.13)
    b.box(x0 - 1, 219, x0 + 17, 227, 'plastic_blue', z=13, bevel=3.5, bulge_y=0.5, bulge_x=0.2)
    b.hot(x0 + 3, 206, 2, 2, 'plastic_blue')
    b.hot(x0 + 3, 220, 3, 1, 'plastic_blue')
b.cyl_h(252, 227, 316, 231, 'chrome', z=9, cap=1)
for x0 in (255, 307):
    b.cyl_v(x0, 229, x0 + 4, 233, 'chrome', z=9, cap=1)

# ---- bus-stop flag sign on the right
b.cyl_v(383, 186, 386, 233, 'chrome', z=9, cap=1)
b.box(376, 172, 394, 190, 'sign_blue', z=12, bevel=2.5, bulge_y=0.3)
b.text(379, 173, "32", 'sign_white')
b.hot(378, 174, 2, 1, 'sign_blue')

# ---- front pillars, roof, sign
b.cyl_v(213, 170, 220, 233, 'metal_dark', z=14, cap=1.5)
b.cyl_v(366, 170, 373, 233, 'metal_dark', z=14, cap=1.5)
b.box(213, 163, 373, 172, 'plastic_teal', z=14, bevel=(3, 3, 4, 3), bulge_y=0.7)
b.box(213, 170, 373, 173, 'chrome', z=16, bevel=(1, 1, 1, 1.5))
b.glare(b.mask_rect(213, 163, 373, 170), offset=30, period=40, bands=((0, 10, 0.1), (14, 3, 0.15)), slope=0.6)
b.box(258, 172, 332, 190, 'sign_blue', z=18, bevel=2.5, bulge_y=0.35)
b.text(260, 173, "TRẠM XE BUÝT", 'sign_white')
for xx in (262, 328):
    b.cyl_v(xx, 170, xx + 1, 173, 'chrome', z=17, cap=0.5)
b.hot(262, 175, 2, 1, 'sign_blue')

# ---- bougainvillea ------------------------------------------------------------
def n1(n, sc, seed):
    r = np.random.RandomState(seed).rand(n // sc + 3)
    return np.interp(np.arange(n) / sc, np.arange(len(r)), r)

def blob_region(poly_fn):
    return poly_fn

def cluster(cx, cy, zc, rr=5.0, nb=3, mats=None, size=1.0, bias=0.0):
    """One bougainvillea flower head: a triad of papery bracts radiating from a cream bloom."""
    pid = b.newpid()
    mt = mats[rng.choice(len(mats))]
    a0 = rng.uniform(0, 6.28)
    for k in range(3):
        a = a0 + k * 2.094 + rng.uniform(-0.35, 0.35)
        d = 1.9 * size
        m2 = mt if rng.rand() < 0.8 else mats[rng.choice(len(mats))]
        b.ellipsoid(cx + np.cos(a) * d, cy + np.sin(a) * d * 0.9, rng.uniform(3.0, 3.8) * size, rng.uniform(2.2, 2.9) * size, m2,
                    z=zc + rng.uniform(-0.3, 1.2), rz=3.1 * size, pid=pid, bias=bias + rng.uniform(-0.05, 0.05), ang=a)
    if rng.rand() < 0.22:
        b.ellipsoid(cx, cy, 0.9, 0.8, 'sign_white', z=zc + 3.0, pid=pid, bias=-0.1, fat=0.0)


def leaf(cx, cy, zc, r=3.2):
    mt = ['leaf_a', 'leaf_b', 'leaf_b', 'leaf_c', 'leaf_b'][rng.randint(5)]
    a = rng.uniform(-1.2, 1.2) + (0 if rng.rand() < 0.5 else 3.14)
    b.ellipsoid(cx, cy, r * rng.uniform(1.2, 1.7), r * 0.5, mt, z=zc, rz=r * 0.55, ang=a, bias=rng.uniform(-0.05, 0.05))


bm = ['bract_a', 'bract_a', 'bract_b', 'bract_b', 'bract_d', 'bract_c']
# roof mass profile
xs_ = np.arange(W)
dome = lambda x: 0.5 + 0.5 * np.sin(np.pi * np.clip((x - 200) / 185, 0, 1)) ** 0.7
top = 166 - (16 + 24 * dome(xs_)) * (0.78 + 0.45 * n1(W, 9, 3)) + 0 * xs_
top[xs_ < 198] = 175
top[xs_ > 388] = 175
region = np.zeros((H, W), bool)
for x in range(200, 386):
    bot = 168 if (x < 240 or x > 352) else 161
    region[int(top[x]):bot, x] = True
# leaves first (deep layer)
ys, xs = np.nonzero(region)
for i in range(130):
    k = rng.randint(len(xs))
    leaf(xs[k], ys[k], 12 + rng.uniform(0, 3))
# bract clusters, sorted by y-ish so layers pile up
pts = []
for i in range(560):
    k = rng.randint(len(xs))
    x, y = xs[k], ys[k]
    depth = (y - top[x]) / max(1, 168 - top[x])
    pts.append((x, y, 14 + rng.uniform(0, 12) + (1 - depth) * 5))
pts.sort(key=lambda p: p[2])
for (x, y, zc) in pts:
    cluster(x, y, zc, mats=bm, bias=0.07 * (1 - (y - top[min(x, W - 1)]) / max(1, 168 - top[min(x, W - 1)])))

# a few leaves poking out on top
ys, xs = np.nonzero(region)
for i in range(95):
    k = rng.randint(len(xs)); leaf(xs[k], ys[k], 24 + rng.uniform(0, 8), r=3.8)
# left drape over the pillar + hanging strings
drape = np.zeros((H, W), bool)
for y in range(150, 214):
    f = (y - 150) / 64.0
    wl = 14 + 9 * np.sin(y * 0.19) + 4 * n1(H, 5, 8)[y] - f * 5
    cxm = 218 - 4 * np.sin(y * 0.09)
    x0 = int(cxm - wl * 0.5 - 4)
    x1 = int(cxm + wl * 0.5 + 2)
    drape[y, max(0, x0):x1] = True
ys, xs = np.nonzero(drape)
for i in range(60):
    k = rng.randint(len(xs)); leaf(xs[k], ys[k], 15 + rng.uniform(0, 4))
pts = []
for i in range(260):
    k = rng.randint(len(xs))
    x, y = xs[k], ys[k]
    if rng.rand() < (y - 150) / 140.0:
        continue
    pts.append((x, y, 17 + rng.uniform(0, 13)))
pts.sort(key=lambda p: p[2])
for (x, y, zc) in pts:
    cluster(x, y, zc, mats=bm)
# woody vine along the pillar
vine = [(219, 214), (216, 202), (220, 188), (217, 174), (221, 163)]
for a_, b_ in zip(vine[:-1], vine[1:]):
    b.capsule(a_, b_, 1.8, 1.5, 'bark', z=19, rz=1.8)
# ground shrub
shrub = b.mask_ellipse(212, 224, 22, 10) & (np.arange(H)[:, None] < 233)
ys, xs = np.nonzero(shrub)
for i in range(40):
    k = rng.randint(len(xs)); leaf(xs[k], ys[k], 18 + rng.uniform(0, 3))
pts = [(xs[k], ys[k], 19 + rng.uniform(0, 9)) for k in rng.randint(len(xs), size=70)]
pts.sort(key=lambda p: p[2])
for (x, y, zc) in pts:
    cluster(x, y, zc, mats=bm)
# dangling strings along roof edge
for x in [240, 252, 346, 356, 364]:
    ln = rng.randint(1, 3)
    for j in range(ln):
        cluster(x + rng.uniform(-3, 3), 172 + j * 5 + rng.uniform(-1, 1), 17 + j * 0.5, mats=bm)
        if j == 0:
            leaf(x + rng.uniform(-4, 4), 171, 16)

# sparkle: glossy hot spots on sunlit bract tops
bract_ids = {L[n_] for n_ in ('bract_a', 'bract_b', 'bract_c', 'bract_d')}
cand = np.argwhere(b.mask & np.isin(b.mat, list(bract_ids)) & (b.ny > 0.35) & (b.nx < 0.1) & (b.z > 20))
sel = rng.choice(len(cand), size=min(70, len(cand)), replace=False) if len(cand) else []
for i in sel:
    y, x = cand[i]
    b.hot(int(x), int(y), 1, 1, 'bract_d', shoulder=False)
img = b.image(shadow_k=24)
img = harden_alpha(img.crop((OX, OY, OX + CW, OY + CH)))
img.save(OUT + 'shelter_ha.png')
open(OUT + '_shelter_origin.txt', 'w').write(f'{OX} {OY}\n')
print(img.size, count_colors(img))
zoom(img, 4, name='shelter.png')
