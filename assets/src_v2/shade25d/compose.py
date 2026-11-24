from common import *
from layout_v2 import *
import numpy as np

W, H = 640, 360


def sky():
    # hand-placed summer-noon bands (top -> horizon), 2-row chequer seam between bands
    cols = ['#1f7de0', '#2a88e6', '#3592ea', '#429ced', '#50a7f0', '#60b2f2', '#72bdf4', '#86c8f6', '#9bd3f8',
            '#b0defa', '#c4e8fb', '#d5f0fc']
    ys = [0, 26, 50, 72, 92, 112, 132, 152, 170, 188, 202, 212]
    a = np.zeros((H, W, 3), np.uint8)
    for i, c in enumerate(cols):
        y0 = ys[i]
        y1 = ys[i + 1] if i + 1 < len(cols) else H
        a[y0:y1] = hexrgb(c)
        if i + 1 < len(cols):
            nxt = hexrgb(cols[i + 1])
            for k, yy in enumerate((y1 - 2, y1 - 1)):
                if yy < H:
                    xs = np.arange(W)
                    chk = ((xs + yy) % 2 == 0) if k == 1 else ((xs % 4) == 0)
                    a[yy, chk] = nxt
    return Image.fromarray(a, 'RGB').convert('RGBA')


def clouds():
    L = default_lib()
    b = Buf(640, 150, L)
    def cloud(cx, cy, s, seed):
        r = np.random.RandomState(seed)
        m = np.zeros((150, 640), bool)
        for k in range(7):
            ex = cx + (k - 3) * 11 * s + r.uniform(-4, 4)
            ry = (9 + 8 * np.exp(-((k - 3) / 2.0) ** 2)) * s * r.uniform(0.85, 1.1)
            m |= b.mask_ellipse(ex, cy - ry * 0.55, 14 * s * r.uniform(0.9, 1.2), ry)
        m &= b.mask_rect(0, 0, 640, cy + 4 * s)           # flat-ish base
        b.inflate(m, 'sky_cloud', z=0, b=9 * s, noise=1.2, nseed=int(seed), nscale=5, smooth=1.0, base_n=(0, 0.1, 1), pid=b.newpid())
    cloud(430, 60, 1.0, 3)
    cloud(150, 38, 0.8, 7)
    cloud(560, 110, 0.7, 9)
    img = harden_alpha(b.image(shadows=False, ao=False, outline=False))
    return img


def sun(img):
    a = np.array(img).astype(float)
    ys, xs = np.mgrid[0:H, 0:W]
    cx, cy = 96, 30
    d = np.hypot(xs - cx, ys - cy)
    for rr, amt in ((52, 0.06), (36, 0.08), (24, 0.12), (15, 0.22)):
        k = (d < rr)[..., None] * amt
        a[..., :3] = a[..., :3] * (1 - k) + np.array([255, 250, 225]) * k
    out = Image.fromarray(a.astype(np.uint8), 'RGBA')
    L = default_lib()
    b = Buf(40, 40, L)
    b.ellipsoid(20, 20, 7.5, 7.5, 'light_warm', z=0)
    s = harden_alpha(b.image(shadows=False, ao=False, outline=False))
    out.alpha_composite(s, (cx - 20, cy - 20))
    return out


def multiply(img, mask, mul=(0.64, 0.69, 0.86)):
    a = np.array(img).astype(float)
    m = mask[..., None]
    a[..., :3] = np.where(m, a[..., :3] * np.array(mul), a[..., :3])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def ell(cx, cy, rx, ry):
    ys, xs = np.mgrid[0:H, 0:W]
    return ((xs + .5 - cx) / rx) ** 2 + ((ys + .5 - cy) / ry) ** 2 <= 1


def shadows(img, shelter_origin):
    # shelter + blooms (cast to lower-right on far sidewalk)
    m = np.zeros((H, W), bool)
    m[222:240, 214:384] = True
    m[226:240, 384:398] = True
    ys, xs = np.mgrid[0:H, 0:W]
    m &= ~((xs < 214 + (ys - 222) * 0.0))
    img = multiply(img, m)
    # darker core directly under roof/seats
    img = multiply(img, np.zeros((H, W), bool) | ((ys >= 226) & (ys < 236) & (xs >= 252) & (xs < 322)), (0.8, 0.82, 0.92))
    # bus shadow on road (far lane) + step for a hard edge
    bx = 548
    m = ell(bx + 4, 275, 118, 5.5) & (ys > 268)
    img = multiply(img, m, (0.55, 0.60, 0.78))
    m2 = ell(bx + 4, 275, 108, 3.2) & (ys > 270)
    img = multiply(img, m2, (0.8, 0.82, 0.92))
    # cat shadow on near sidewalk
    m = ell(150 + 6, 352, 29, 4.2)
    img = multiply(img, m, (0.62, 0.67, 0.84))
    return img


def petals(img):
    r = np.random.RandomState(31)
    a = np.array(img)
    cols = [(232, 52, 160), (255, 100, 190), (176, 40, 150), (255, 140, 205)]
    for i in range(70):
        x = int(r.normal(222, 26))
        y = int(r.uniform(226, 239)) if r.rand() < 0.8 else int(r.uniform(318, 345))
        if r.rand() < 0.3:
            x = int(r.normal(300, 40))
        if 0 <= x < W and 0 <= y < H and not (y > 318 and abs(x - 150) < 40):
            c = cols[r.randint(4)]
            a[y, x] = (*c, 255)
            if r.rand() < 0.4 and x + 1 < W:
                a[y, x + 1] = (*cols[r.randint(4)], 255)
    return Image.fromarray(a, 'RGBA')


def main():
    img = sky()
    img.alpha_composite(clouds(), (0, 0)) if False else None
    cl = clouds()
    # cloud layer sits behind facades
    img = sun(img)
    img.alpha_composite(cl, (0, 10))
    fac = Image.open(OUT + 'facades.png')
    img.alpha_composite(fac, (0, TEST['buildings_tl'][1]))
    gr = Image.open(OUT + 'ground.png')
    img.alpha_composite(gr, (0, 0))
    ox, oy = map(int, open(OUT + '_shelter_origin.txt').read().split())
    img = shadows(img, (ox, oy))
    img = petals(img)
    sh = Image.open(OUT + 'shelter_ha.png')
    img.alpha_composite(sh, (ox, oy))
    bus = Image.open(OUT + 'bus_L.png')
    img.alpha_composite(bus, (TEST['bus_L_x'] - bus.width // 2, FAR_LANE_BASE_Y - 68))
    cat = Image.open(OUT + 'cat_sit.png')
    img.alpha_composite(cat, (TEST['cat_x'] - cat.width // 2, CAT_BASE_Y - 38))
    img = img.convert('RGBA')
    img.save(OUT + 'styleframe.png')
    upscale(img, 3).save(OUT + 'styleframe@3x.png')
    print(img.size, count_colors(img))


main()
