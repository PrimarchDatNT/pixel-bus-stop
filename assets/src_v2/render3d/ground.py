"""Sidewalks, curbs, road per tools/layout_v2.py bands. Painted pixel textures mapped 1:1 onto planes."""
import random, numpy as np
from PIL import Image
from common import *

HS = 0.21                 # sidewalk height above road
W0, W1 = -40, 680         # ground column extent

def _save(arr, name):
    p = f'{WORK}/{name}.png'; Image.fromarray(arr.astype(np.uint8)).save(p); return p
WORK = None

def paver_tex(w, h, seed, base=(166, 160, 150), tile=(15, 7)):
    rnd = random.Random(seed); a = np.zeros((h, w, 3), float)
    tw, th = tile
    for ry in range(-1, h // th + 2):
        off = (ry % 2) * (tw // 2) + (ry // 3) * 3
        for rx in range(-2, w // tw + 3):
            x0 = rx * tw + off; y0 = ry * th
            v = rnd.uniform(-9, 9); tint = rnd.choice([(0, 0, 0), (0, 0, 0), (4, 2, -4), (-4, 0, 5), (6, 4, 0)])
            if rnd.random() < 0.06: v -= 18; tint = (-4, 2, 8)
            col = np.array(base) + v + np.array(tint)
            for yy in range(th):
                for xx in range(tw):
                    px, py = x0 + xx, y0 + yy
                    if 0 <= px < w and 0 <= py < h:
                        c = col.copy()
                        if xx == 0 or yy == 0: c = c * 0.0 + np.array([96, 92, 100])  # mortar (top/left)
                        elif xx == 1 or yy == 1: c = c + 16 + (6 if (xx == 1 and yy == 1) else 0)   # lit bevel
                        elif xx == tw - 1 or yy == th - 1: c = c - 11
                        else: c = c + (yy * 1.2 - 4) * -0.3 + rnd.uniform(-2.5, 2.5)
                        a[py, px] = c
    return a

def asphalt_tex(w, h, seed):
    rnd = np.random.RandomState(seed)
    base = np.array([66, 70, 84], float)
    a = np.zeros((h, w, 3)) + base
    n = rnd.normal(0, 4.0, (h, w, 1)); a += n * np.array([1, 1, 1.1])
    # large patches
    for _ in range(26):
        x, y = rnd.randint(0, w), rnd.randint(0, h); rw, rh = rnd.randint(18, 70), rnd.randint(3, 11)
        a[y:y + rh, x:x + rw] += rnd.uniform(-9, 9)
    # aggregate speckle
    for _ in range(w * h // 38):
        x, y = rnd.randint(0, w), rnd.randint(0, h); a[y, x] += rnd.choice([-20, 18, 30]) * np.array([1, 1, 1.2])
    # tyre-wear lanes (darker, glossy-ish)
    for ly in (h * 0.18, h * 0.40, h * 0.64, h * 0.86):
        yy = int(ly)
        a[max(0, yy - 3):yy + 3, :] -= 5
    return a

def curb_face_tex(w, h):
    a = np.zeros((h, w, 3)); 
    ramp = [(255, 250, 240), (236, 228, 222), (214, 206, 206), (186, 180, 190), (150, 146, 166)]
    for y in range(h):
        c = ramp[min(len(ramp) - 1, int(y * len(ramp) / h))]; a[y, :] = c
    for x in range(0, w, 66):
        a[:, x] = (84, 82, 100)
        if x + 1 < w: a[:, x + 1] = np.minimum(a[:, x + 1] + 14, 255)
    return a

def curb_top_tex(w, h):
    a = np.zeros((h, w, 3)); 
    for y in range(h):
        t = y / max(1, h - 1)
        a[y, :] = (np.array([226, 220, 208]) * (1 - t) + np.array([186, 180, 178]) * t)
    a[0, :] = (240, 236, 224)
    for x in range(0, w, 66):
        a[:, x] = (112, 108, 122)
    return a

def build(colls, work):
    global WORK; WORK = work
    g = colls['ground']
    wpx = W1 - W0
    x0, x1 = X(W0), X(W1)
    # --- road (Z=0), rows 245..316
    tex = _save(asphalt_tex(wpx, 72, 3), 'tx_road')
    m = tex_mat('road', tex, rough=0.42, spec=0.5)
    hplane('road', x0, x1, Yrow(317, 0), Yrow(245, 0), 0.0, m, g)
    # extra road under sidewalks so the shelter bounce is right
    hplane('under', x0, x1, Yrow(317, 0), Yrow(150, 0), -0.01, mat('under', (0.2, 0.2, 0.2), 0.9), g)
    # --- far sidewalk: top Z=HS rows 200..240; face rows 240..245
    r_top0 = 195
    tex = _save(paver_tex(wpx, 241 - r_top0, 11), 'tx_far')
    m = tex_mat('swfar', tex, rough=0.8, spec=0.25)
    hplane('swfar', x0, x1, Yrow(241, HS), Yrow(r_top0, HS), HS, m, g)
    tex = _save(curb_face_tex(wpx, 5), 'tx_cf')
    vplane('curbface_far', x0, x1, 0, HS, Yrow(245, 0), tex_mat('cf', tex, rough=0.7), g)
    # --- near curb top (granite strip) rows 317..321, near sidewalk 322..362
    tex = _save(curb_top_tex(wpx, 5), 'tx_nc')
    hplane('curb_near', x0, x1, Yrow(322, HS), Yrow(317, HS), HS, tex_mat('nc', tex, rough=0.55, spec=0.4), g)
    tex = _save(paver_tex(wpx, 40, 29, base=(176, 170, 160), tile=(16, 8)), 'tx_near')
    hplane('swnear', x0, x1, Yrow(362, HS), Yrow(322, HS), HS, tex_mat('swn', tex, rough=0.8, spec=0.25), g)
    # near-sidewalk front wall so it has a body for bounce
    box('nearbody', (0, Yrow(340, HS) , HS / 2 - 0.2), (60, 12, 0.2), mat('nb', (0.4, 0.4, 0.4), 0.9), coll=g)
    # --- lane dashes (white paint), row 280
    paint = mat('paint', (0.9, 0.9, 0.86), 0.5, spec=0.5)
    c = 4
    while c < 700:
        box('dash', (X(c + 20), (Yrow(280, 0.01) + Yrow(282, 0.01)) / 2, 0.006), (X(40), Yrow(280, 0.01) - Yrow(282, 0.01), 0.012), paint, coll=g)
        c += 76
    # manhole covers / drain
    iron = mat('iron', (0.10, 0.10, 0.12), 0.45, metal=0.8)
    cyl('manhole', (X(400), Yrow(262, 0.0), 0.012), 0.55, 0.024, iron, coll=g)
    cyl('manhole2', (X(120), Yrow(300, 0.0), 0.012), 0.55, 0.024, iron, coll=g)
    for gx in (X(330), ):
        box('grate', (gx, Yrow(247, 0), 0.01), (1.6, 0.35, 0.02), iron, coll=g)
