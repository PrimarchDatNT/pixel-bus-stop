from common import *
import numpy as np
from layout_v2 import *

W, H = 640, 360
L = default_lib()
L.add('puddle', '#6fa0c8', n=8, gloss=80, spec=1.0, refl=0.5, env='sky', rim=0.0, amb=0.3, hi=0.8,
      ramp_kw=dict(l0=0.25))
for nm, hx in (('concrete_warm', '#cdb99c'), ('concrete_cool', '#a7adbb'), ('concrete_rose', '#c4a9a4')):
    L.add(nm, hx, n=8, gloss=6, spec=0.1, rim=0.4, bounce=0.6, wrap=0.3, tex=0.05, ramp_kw=dict(cfloor_d=0.03))
L.add('asphalt2', '#5b5a74', n=9, gloss=25, spec=0.4, refl=0.10, env='wet', rim=0.0, wrap=0.3, tex=0.05, tex_sx=1.6,
      tex_sy=1.6, ramp_kw=dict(l0=0.2, cfloor_d=0.05, cfloor_l=0.02, dk=0.5))
b = Buf(W, H, L)
rng = np.random.RandomState(4)
YS, XS = np.mgrid[0:H, 0:W]


def pavers(y0, y1, th, tw, tilt, bev=1.0, z=0.0, accent=True):
    nrows = max(1, int(round((y1 - y0) / th)))
    ys = np.linspace(y0, y1, nrows + 1).round().astype(int)
    b.box(0, y0, W, y1, 'concrete_dark', z=z - 1.5, bevel=0, tilt=tilt)
    for r in range(nrows):
        ya, yb = ys[r], ys[r + 1]
        off = (r % 2) * tw // 2 + rng.randint(0, 3)
        x = -off
        while x < W:
            w = tw + rng.randint(-1, 2)
            mt = ['concrete', 'concrete', 'concrete_warm', 'concrete_warm', 'concrete_cool', 'concrete_rose', 'concrete_dark'][rng.randint(7)]
            bias = rng.uniform(-0.05, 0.05) + (0.10 if (accent and rng.rand() < 0.06) else 0)
            b.box(x + 1, ya + 1, x + w, yb, mt, z=z, bevel=bev, tilt=tilt, bias=bias, pid=b.newpid())
            x += w + 1
    # cracks / chips
    for i in range(10):
        cx, cy = rng.randint(0, W), rng.randint(y0 + 2, y1 - 2)
        b.decal(b.mask_line([(cx, cy), (cx + rng.randint(3, 7), cy + rng.randint(-1, 2))]), 'concrete_dark', bias=-0.18)


# far sidewalk
pavers(FAR_SIDEWALK_Y0, FAR_SIDEWALK_Y1 + 1, 5.8, 13, (0, 0.38), 0.9)
b.tone(b.mask_rect(0, FAR_SIDEWALK_Y0, W, FAR_SIDEWALK_Y0 + 3), -0.12)       # contact AO under the facades
# far curb: top face + visible road-facing front
b.box(0, FAR_CURB_Y0, W, FAR_CURB_Y0 + 2, 'concrete', z=3, bevel=(0, 0, 1, 0), tilt=(0, 0.6), pid=b.newpid(), bias=0.10)
b.box(0, FAR_CURB_Y0 + 2, W, FAR_CURB_Y1 + 1, 'concrete', z=3, bevel=(0, 0, 0, 1.5), tilt=(0, -0.25), pid=b.newpid(), bias=-0.04)
for x in range(30, W, 47):
    b.set_line(b.mask_line([(x, FAR_CURB_Y0 + 2), (x, FAR_CURB_Y1)]), 1)
b.hot(120, FAR_CURB_Y0, 6, 1, 'concrete', shoulder=False)
b.hot(402, FAR_CURB_Y0, 5, 1, 'concrete', shoulder=False)
# road
b.box(0, ROAD_Y0, W, ROAD_Y1 + 1, 'asphalt2', z=0, bevel=0, tilt=(0, 0.12))
big = vnoise(H, W, 46, 14, 8)
b.tone(b.mask_rect(0, ROAD_Y0, W, ROAD_Y1 + 1), (big - 0.5) * 0.10 + 0.10 * (1 - np.clip((YS - ROAD_Y0) / 70.0, 0, 1)) - 0.04 + 0.06 * (np.abs(YS - 262) < 5) * 0)
# gutter shadow beside the far curb
b.tone(b.mask_rect(0, ROAD_Y0, W, ROAD_Y0 + 3), -0.12)
# patches, cracks
for i in range(4):
    px, py = rng.randint(20, 380), rng.randint(ROAD_Y0 + 10, ROAD_Y1 - 14)
    pw, ph = rng.randint(22, 44), rng.randint(6, 11)
    b.decal(b.mask_rect(px, py, px + pw, py + ph), 'asphalt2', bias=-0.09)
for i in range(3):
    px, py = rng.randint(10, 620), rng.randint(ROAD_Y0 + 4, ROAD_Y1 - 4)
    pts = [(px, py)]
    for k in range(4):
        pts.append((pts[-1][0] + rng.randint(2, 6), pts[-1][1] + rng.randint(-2, 3)))
    b.decal(b.mask_line(pts), 'asphalt', bias=-0.22)
# manhole + drain
for (mx, my) in ((88, 296), (468, 262)):
    b.ellipsoid(mx, my, 11, 4.2, 'metal_dark', z=0.3, rz=1.5, pid=b.newpid())
    b.decal(b.mask_ellipse(mx, my, 7.5, 2.7), 'metal_dark', bias=-0.12)
    for k in range(-3, 4):
        b.set_line(b.mask_line([(mx + k * 2, my - 2), (mx + k * 2, my + 2)]), 1)
    b.hot(mx - 6, int(my - 3), 3, 1, 'metal_dark')
for gx in (210, 350):
    b.box(gx, ROAD_Y1 - 3, gx + 26, ROAD_Y1, 'metal_dark', z=0.5, bevel=0.8, pid=b.newpid())
    for k in range(gx + 3, gx + 25, 3):
        b.set_line(b.mask_line([(k, ROAD_Y1 - 2), (k, ROAD_Y1 - 1)]), 2)
# puddles (glossy sky reflections)
for (px, py, rx, ry) in ((228, 300, 16, 3.4), (426, 306, 11, 2.6), (60, 266, 9, 2.2)):
    pm = b.mask_ellipse(px, py, rx, ry)
    b.decal(pm, 'puddle', bias=0.0)
    b.tone(pm & (YS < py), 0.10)
    b.hot(px - rx // 2, int(py - 1), 3, 1, 'puddle')
# lane dashes (white paint, glossy)
for x in range(-6, W, 44):
    b.box(x, LANE_DIVIDER_Y - 1, x + 26, LANE_DIVIDER_Y + 1, 'sign_white', z=0.8, bevel=0.7, pid=b.newpid(), tilt=(0, 0.1))
    b.hot(x + 3, LANE_DIVIDER_Y - 1, 2, 1, 'sign_white', shoulder=False)
# road edge lines
# near curb: top face only, rounded lip
b.box(0, NEAR_CURB_Y0, W, NEAR_CURB_Y0 + 3, 'concrete', z=3, bevel=(0, 0, 1.2, 0), tilt=(0, 0.55), pid=b.newpid(), bias=0.12)
b.box(0, NEAR_CURB_Y0 + 3, W, NEAR_CURB_Y1 + 1, 'concrete', z=3, bevel=(0, 0, 0, 1.4), tilt=(0, 0.3), pid=b.newpid())
for x in range(60, W, 52):
    b.set_line(b.mask_line([(x, NEAR_CURB_Y0 + 1), (x, NEAR_CURB_Y1)]), 1)
# near sidewalk (bigger pavers)
pavers(NEAR_SIDEWALK_Y0, NEAR_SIDEWALK_Y1 + 1, 9.5, 25, (0, 0.38), 1.3)
# a few fallen bougainvillea petals near the shelter
pet = []
for i in range(46):
    pet.append((int(rng.normal(236, 22)), int(rng.uniform(212, 238))))

img = harden_alpha(b.image(shadow_k=12))
a = np.array(img)
a[:FAR_SIDEWALK_Y0] = 0
img = Image.fromarray(a, 'RGBA')
img.save(OUT + 'ground.png')
print(img.size, count_colors(img))
zoom(img, 2, name='ground.png', box=(0, 205, 640, 360))
