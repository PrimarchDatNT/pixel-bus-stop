from common import *
import numpy as np


SY = 0.945


def Y(y):
    return 1.0 + (y - 1.0) * SY


class P:
    """Vertical-squash proxy so the cat fits the 64x40 frame."""
    def __init__(self, b):
        self.b = b
        self.mask = b.mask

    def __getattr__(self, k):
        return getattr(self.b, k)

    def ellipsoid(self, cx, cy, rx, ry, *a, **k):
        return self.b.ellipsoid(cx, Y(cy), rx, ry * SY, *a, **k)

    def capsule(self, p0, p1, *a, **k):
        return self.b.capsule((p0[0], Y(p0[1])), (p1[0], Y(p1[1])), *a, **k)

    def cone(self, cx, ya, yb, *a, **k):
        return self.b.cone(cx, Y(ya), Y(yb), *a, **k)

    def mask_ellipse(self, cx, cy, rx, ry):
        return self.b.mask_ellipse(cx, Y(cy), rx, ry * SY)

    def mask_poly(self, pts):
        return self.b.mask_poly([(x, Y(y)) for x, y in pts])

    def mask_line(self, pts, width=1):
        return self.b.mask_line([(x, Y(y)) for x, y in pts], width)

    def mask_rect(self, x0, y0, x1, y1):
        return self.b.mask_rect(x0, Y(y0), x1, Y(y1))

    def hot(self, x, y, *a, **k):
        return self.b.hot(x, int(round(Y(y))), *a, **k)


def build_cat(L=None, seed=5):
    L = L or default_lib()
    rng = np.random.RandomState(seed)
    W, H = 64, 40
    raw = Buf(W, H, L)
    b = P(raw)
    # tail first (behind), curling up on the right
    tp = [(46, 36), (53.5, 37.2), (58.5, 33), (58.5, 27)]
    tpid = b.newpid()
    for a_, c_, r0, r1 in zip(tp[:-1], tp[1:], (3.0, 2.9, 2.6), (2.9, 2.6, 2.2)):
        b.capsule(a_, c_, r0, r1, 'fur_orange', z=1, pid=tpid, rz=r0)
    for (cx, cy, rr) in ((50, 37.2, 2.6), (55.8, 35.6, 2.6), (58.7, 31.2, 2.4)):
        b.decal(b.mask_ellipse(cx, cy, 1.1, rr), 'fur_dark')
    b.decal(b.mask_ellipse(58.5, 26.5, 3, 2.0), 'fur_dark')
    # body masses
    b.ellipsoid(38, 29, 14.5, 10.5, 'fur_orange', z=2, rz=10.5, pid=b.newpid())      # haunch
    b.ellipsoid(27, 23, 9.5, 13, 'fur_orange', z=5, rz=9, pid=b.newpid())            # chest / torso
    # fluffy tufts on the back line
    for k in range(9):
        a = rng.uniform(-2.9, -0.6)
        cx, cy = 38 + np.cos(a) * 13.5, 29 + np.sin(a) * 9.5
        b.ellipsoid(cx, cy, 1.9, 2.6, 'fur_orange', z=3, rz=2, pid=b.newpid(), bias=rng.uniform(-0.03, 0.03))
    # legs + paws
    b.capsule((24.2, 27), (23.3, 36), 3.3, 3.0, 'fur_orange', z=8, rz=3.2, pid=b.newpid())
    b.capsule((31.2, 27), (32.3, 36), 3.3, 3.0, 'fur_orange', z=8, rz=3.2, pid=b.newpid())
    b.ellipsoid(22.8, 37.2, 4.0, 2.3, 'fur_orange', z=8, rz=2.6, pid=b.newpid())
    b.ellipsoid(33.4, 37.2, 4.0, 2.3, 'fur_orange', z=8, rz=2.6, pid=b.newpid())
    b.ellipsoid(44, 37.4, 5.2, 2.5, 'fur_orange', z=4, rz=2.6, pid=b.newpid())       # back foot
    # head
    b.cone(18.6, 0.8, 8.5, 4.6, 'fur_orange', z=9, lean=-1.2, pid=b.newpid())
    b.cone(33.6, 0.8, 8.5, 4.6, 'fur_orange', z=9, lean=1.2, pid=b.newpid())
    b.ellipsoid(18.3, 14.8, 3.6, 3.0, 'fur_orange', z=9, rz=2.8, pid=b.newpid())
    b.ellipsoid(34.2, 14.8, 3.6, 3.0, 'fur_orange', z=9, rz=2.8, pid=b.newpid())
    b.ellipsoid(26.3, 11.2, 10.2, 8.4, 'fur_orange', z=10, rz=8.6, pid=b.newpid())
    # --- markings (decals)
    # inner ears
    b.decal(b.mask_poly([(17.8, 3.5), (15.5, 7.5), (20.5, 7.5)]), 'pink', bias=-0.05)
    b.decal(b.mask_poly([(34.4, 3.5), (32, 7.5), (37.2, 7.5)]), 'pink', bias=-0.05)
    # white chest + muzzle + socks
    b.decal(b.mask_ellipse(27.2, 26, 4.8, 9.5), 'fur_cream')
    b.decal(b.mask_ellipse(26.2, 15.6, 5.2, 3.9), 'fur_cream')
    b.decal(b.mask_ellipse(26.2, 12.0, 1.1, 3.0), 'fur_cream')
    for (cx, y0) in ((23, 33.0), (32.5, 33.0)):
        b.decal(b.mask_ellipse(cx, 37, 4.2, 4.0) & b.mask_rect(0, y0, 64, 40) & b.mask_rect(cx - 4.5, 0, cx + 4.5, 40), 'fur_cream')
    # tabby stripes: forehead M, cheeks
    for x in (23.5, 26.5, 29.5):
        b.decal(b.mask_line([(x, 3.2), (x + (x - 26.5) * 0.15, 8.2)]), 'fur_dark')
    for y in (11.0, 13.4):
        b.decal(b.mask_line([(16.2, y), (20.6, y + 0.6)]), 'fur_dark')
        b.decal(b.mask_line([(32.4, y + 0.6), (36.4, y)]), 'fur_dark')
    # body stripes: concentric arcs on the haunch and short bars on torso side
    haunch = b.mask_ellipse(38, 29, 14.5, 10.5)
    for r_ in (10, 14, 18, 22):
        ring = b.mask_ellipse(52, 22, r_, r_ * 0.9) & ~b.mask_ellipse(52, 22, r_ - 2.0, (r_ - 2.0) * 0.9)
        b.decal(ring & haunch & b.mask_rect(0, 18, 64, 36), 'fur_dark')
    for y in (17, 20.5, 24):
        b.decal(b.mask_line([(17.8, y), (21.8, y + 1.2)], width=2) & b.mask_ellipse(27, 23, 9.5, 13) & ~b.mask_ellipse(27.2, 26, 4.8, 9.5), 'fur_dark')
    # legs stripe
    for (cx) in (22.5, 33):
        b.decal(b.mask_line([(cx - 3, 30), (cx + 3, 29)]), 'fur_dark')
    # chest ruff + cheek fluff (cream tufts overlapping the body for soft fur volume)
    for (cx, cy, rx, ry) in ((23.2, 19.8, 2.6, 2.2), (31.4, 19.8, 2.6, 2.2), (27.2, 21.2, 3.0, 2.4), (24.6, 22.8, 2.2, 2.2), (30.0, 22.8, 2.2, 2.2)):
        b.ellipsoid(cx, cy, rx, ry, 'fur_cream', z=11, rz=2.4, pid=b.newpid(), bias=0.0)
    for (cx, cy) in ((16.8, 15.8), (35.8, 15.8)):
        b.ellipsoid(cx, cy, 2.0, 1.6, 'fur_cream', z=10.5, rz=1.8, pid=b.newpid())
    # --- face
    b.decal(b.mask_ellipse(21.2, 10.6, 2.6, 2.9), 'eye')
    b.decal(b.mask_ellipse(30.6, 10.6, 2.4, 2.8), 'eye')
    b.decal(b.mask_ellipse(21.4, 10.8, 0.8, 1.9), 'black')
    b.decal(b.mask_ellipse(30.4, 10.8, 0.8, 1.8), 'black')
    for (x0, x1, y) in ((18, 24, 7.7), (28, 33.5, 7.7)):
        b.decal(b.mask_line([(x0, y), (x1, y)]), 'fur_dark')
    b.decal(b.mask_rect(25, 14, 28, 15), 'pink')
    b.decal(b.mask_rect(25.5, 15, 27.5, 16), 'pink', bias=-0.1)
    b.decal(b.mask_line([(26.5, 16), (26.5, 17.5)]), 'fur_dark')
    b.decal(b.mask_line([(23.5, 18.4), (26.5, 17.5), (29.5, 18.4)]), 'fur_dark')
    # glossy eye + nose highlights, whiskers
    b.hot(20, 9, 1, 1, col=(255, 255, 250), shoulder=False)
    b.hot(29, 9, 1, 1, col=(255, 255, 250), shoulder=False)
    b.hot(23, 12, 1, 1, col=(200, 245, 160), shoulder=False)
    b.hot(32, 12, 1, 1, col=(200, 245, 160), shoulder=False)
    b.hot(25, 14, 1, 1, col=(255, 215, 230), shoulder=False)
    # fur sheen
    for (x, y, w) in ((22, 3, 3), (29, 3, 2), (37, 20, 3), (43, 21, 3), (13, 15, 1)):
        b.hot(x, y, w, 1, col=(255, 216, 150), shoulder=False)
    wh = (246, 240, 232)
    pts = [(x, 16 + (22 - x) // 3) for x in range(13, 21)] + [(x, 18 + (21 - x) // 4) for x in range(12, 19)] \
        + [(x, 16 + (x - 31) // 3) for x in range(32, 40)] + [(x, 18 + (x - 32) // 4) for x in range(33, 41)]
    b.px([(x, int(round(Y(y))), wh) for (x, y) in pts if not raw.mask[int(round(Y(y))), x]])
    return raw


if __name__ == '__main__':
    b = build_cat()
    img = harden_alpha(b.image(shadow_k=10))
    img.save(OUT + 'cat_sit.png')
    print(img.size, count_colors(img))
    zoom(img, 10, name='cat.png')
