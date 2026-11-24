from common import *
import numpy as np


def build_bus(L=None, pose=0):
    L = L or default_lib()
    G = '#12526e'
    if 'bg_dark' not in L.by:
        L.add('bg_dark', '#1d5c80', n=9, gloss=40, spec=0.4, rim=0.0, amb=0.08, hi=0.80, ramp_kw=dict(l0=0.10, l1=0.90, dk=0.25, cdark=0.9, lk=0.2))
        for nm, src, k in (('bg_seat', 'plastic_blue', 0.45), ('bg_seat2', 'paint_orange', 0.5),
                           ('bg_skin', 'skin', 0.4), ('bg_hair', 'hair', 0.4), ('bg_shirt', 'cloth_white', 0.45),
                           ('bg_shirt2', 'cloth_red', 0.45), ('bg_shirt3', 'cloth_blue', 0.4), ('bg_pole', 'chrome', 0.4)):
            L.derive(nm, src, mix=G, k=k, hi=0.80, amb=0.08, refl=0.0, rim=0.0, spec=0.25, gloss=20)
    W, H = 226, 70
    b = Buf(W, H, L)

    # ---------------------------------------------------------- body shell
    b.clip = b.mask_rect(0, 0, 226, 59)
    b.box(4, 5, 224, 73, 'paint_yellow', z=10, bevel=(9, 3, 5, 0), bulge_y=0.36, rc=4)
    b.clip = None
    # raked front: cut the corner above the nose
    b.erase(b.mask_poly([(0, 0), (16.5, 0), (3.2, 38.5), (0, 38.5)]))
    # windshield wedge seen at a grazing angle (bright sky reflection)
    ws = b.mask_poly([(4, 38), (16.5, 4.6), (23.2, 4.6), (10.5, 38)])
    b.clip = ws
    b.box(2, 4, 26, 39, 'glass_light', z=14, bevel=0.8, tilt=(-0.15, 0.5), pid=b.newpid())
    b.clip = None
    b.glare(ws, offset=0, period=14, bands=((0, 2, 0.2),), slope=0.5)

    # ---------------------------------------------------------- windows
    wins = [('poly', [(13.5, 31.5), (23, 10), (53, 10), (53, 31.5)])]
    for x0 in (56, 84, 112, 140, 168, 196):
        wins.append(('rect', (x0, 10, x0 + 25, 31.5)))
    wmasks = []
    for kind, g in wins:
        M = b.mask_poly(g) if kind == 'poly' else b.mask_rect(*g)
        ring = ndi.binary_dilation(M, iterations=1) & ~M
        wmasks.append(M)
        b.erase(M)
        b.clip = ring
        b.box(0, 7, 226, 36, 'rubber', z=13, bevel=0, pid=b.newpid())
        b.clip = M
        b.box(0, 7, 226, 36, 'bg_dark', z=4, bevel=0, pid=b.newpid())
        b.clip = None
    # --- interior: driver
    dm = wmasks[0]
    b.clip = dm
    b.box(40, 15, 52, 36, 'bg_seat', z=6, bevel=(4, 2, 5, 1), pid=b.newpid())          # seat back
    b.capsule((33.5, 31), (34.5, 24), 5.3, 4.2, 'bg_shirt3', z=8, rz=4)                  # torso
    b.capsule((32, 26), (27, 27.5), 1.9, 1.6, 'bg_shirt3', z=9, rz=1.8)                  # arm
    b.ellipsoid(27, 27.6, 1.6, 1.6, 'bg_skin', z=9.5)                                    # hand
    b.ellipsoid(34.5, 17.6, 4.3, 4.6, 'bg_skin', z=9)                                    # head
    b.ellipsoid(35.2, 15.6, 4.5, 3.2, 'bg_hair', z=9.6)                                  # hair
    b.ellipsoid(36.5, 20.5, 3.2, 2.0, 'bg_hair', z=8.8)                                  # nape
    b.capsule((24.5, 21), (27.2, 31.5), 1.1, 1.1, 'bg_pole', z=9, rz=1.2)                # steering wheel
    b.decal(b.mask_rect(31, 17, 32, 19), 'black')                                       # eye
    b.clip = None
    # --- interior: passengers + seats
    for wi, kind in ((2, 0), (4, 1), (5, 2), (3, -1)):
        M = wmasks[wi]
        xs_ = np.nonzero(M.any(0))[0]
        x0 = xs_[0]
        b.clip = M
        sx = x0 + 6 + (wi * 5) % 6
        b.box(sx - 1, 17, sx + 11, 36, 'bg_seat2' if wi % 2 else 'bg_seat', z=6, bevel=(4, 4, 5, 1), pid=b.newpid())
        if kind >= 0:
            hx = sx + 5
            b.capsule((hx - 2, 33), (hx + 1, 28), 5.8, 4.8, ['bg_shirt', 'bg_shirt2', 'bg_shirt3'][kind], z=8, rz=4)
            b.ellipsoid(hx - 0.5, 20.8, 3.7, 4.0, 'bg_skin', z=9)
            b.ellipsoid(hx + 0.3, 19.0, 3.9, 2.9, 'bg_hair', z=9.6)
            b.decal(b.mask_rect(hx - 3, 20, hx - 2, 21), 'black')
        b.clip = None
    # standing poles
    for wi in range(1, 7):
        M = wmasks[wi]
        xs_ = np.nonzero(M.any(0))[0]
        b.clip = M
        b.cyl_v(xs_[0] + 2, 10, xs_[0] + 4, 32, 'bg_pole', z=9, cap=0.5)
        b.clip = None
    # window light: sky reflection band, horizon gradient, glare streaks
    ys, xs = np.mgrid[0:H, 0:W]
    for M in wmasks:
        yy = np.nonzero(M.any(1))[0]
        y0, y1 = yy[0], yy[-1]
        u = (ys - y0) + 0.45 * (xs - np.nonzero(M.any(0))[0][0])
        b.tone(M & (u < 0.52 * (y1 - y0)), 0.36)
        b.tone(M, 0.07)
        b.tone(M, 0.14 * (1 - np.clip((ys - y0) / max(1, y1 - y0), 0, 1)))
        b.tone(M & (np.abs(u - 0.52 * (y1 - y0)) < 0.9), 0.14)
    allw = np.zeros((H, W), bool)
    for M in wmasks:
        allw |= M
    b.glare(allw, offset=4, period=34, bands=((0, 5, 0.16), (8, 2, 0.26)), slope=1.0)
    # route display (LED) in window 2
    b.box(59, 11, 80, 21, 'black', z=12, bevel=1.2, pid=b.newpid())
    b.text(62, 6, "32", 'light_warm')
    b.decal(b.mask_poly([(72, 13.5), (72, 18.5), (76, 16)]), 'light_warm')

    # ---------------------------------------------------------- trim, stripes, decals
    b.box(11, 32, 223, 35, 'chrome', z=13, bevel=(0, 0, 1.2, 1.4))
    b.decal(b.mask_rect(4, 42, 224, 46), 'paint_orange')
    b.decal(b.mask_rect(4, 46, 224, 47), 'paint_white')
    b.decal(b.mask_rect(4, 47, 224, 59), 'paint_red')
    # panel seams / hatch lines
    for x in (108, 168):
        b.set_line(b.mask_line([(x, 48), (x, 57)]), 1)
    hx0, hx1, hy0, hy1 = 141, 157, 49, 56
    b.set_line(b.mask_line([(hx0, hy0), (hx1, hy0), (hx1, hy1), (hx0, hy1), (hx0, hy0)]), 1)
    b.hot(hx0 + 2, hy0 + 1, 2, 1, 'paint_red')
    # roundel with route number
    b.decal(b.mask_ellipse(124, 52.5, 7.0, 7.0), 'sign_white')
    b.text(119, 45, "32", 'sign_red')
    # text on red band
    b.text(66, 44, "XE BUÝT", 'sign_white')
    b.text(30, 47, "HÀ NỘI", 'sign_yellow') if False else None
    # wheel arches
    for cx in (42, 186):
        arch = b.mask_ellipse(cx, 59.5, 12.8, 12.8) & b.mask_rect(0, 0, 226, 60)
        lip = b.mask_ellipse(cx, 59.5, 14.2, 14.2) & b.mask_rect(0, 0, 226, 60) & ~arch
        b.decal(arch, 'rubber')
        b.tone(lip & b.mask_rect(0, 0, cx, 70), 0.10)
        b.tone(lip & b.mask_rect(cx, 0, 226, 70), -0.08)
    # underbody / skirt
    b.box(14, 58, 216, 63, 'rubber', z=5, bevel=(1, 1, 0.5, 2))
    # wheels
    for cx in (42, 186):
        c = b.mask_ellipse(cx, 59.0, 9.6, 9.6)
        b.inflate(c, 'rubber', z=11, b=4.5, pid=b.newpid())
        r_ = b.mask_ellipse(cx, 59.0, 5.8, 5.8)
        b.inflate(r_, 'chrome', z=13.5, b=2.6, pid=b.newpid())
        b.ellipsoid(cx, 59.0, 2.2, 2.2, 'metal_light', z=14, rz=1.6)
        for k in range(5):
            a = k * 6.283 / 5 + 0.3
            b.decal(b.mask_ellipse(cx + 3.9 * np.cos(a), 59 + 3.9 * np.sin(a), 0.6, 0.6), 'metal_dark')
        b.hot(cx - 4, 55, 2, 1, 'chrome')
        b.hot(cx - 7, 56, 1, 2, 'rubber', shoulder=False, col=(150, 160, 190))
    # ---------------------------------------------------------- front / rear furniture
    b.box(1, 51, 12, 59, 'chrome', z=15, bevel=3.2, bulge_y=0.5)                       # bumper
    b.ellipsoid(7.5, 46.2, 3.8, 3.2, 'light_warm', z=15, rz=2.5)                       # headlight
    b.hot(5, 44, 2, 1, 'light_warm')
    b.ellipsoid(6.5, 40.2, 2.0, 1.8, 'paint_orange', z=14, rz=1.6)                     # indicator
    b.box(220, 38, 226, 55, 'tail_red', z=13, bevel=(1.5, 0, 2, 2))
    b.hot(221, 40, 1, 2, 'tail_red')
    # mirror (driver side) + arm
    b.cyl_h(5, 22, 15, 24.5, 'chrome', z=17, cap=1)
    b.box(0, 11, 6, 27, 'metal_dark', z=19, bevel=(2.2, 1.4, 2.2, 2.2), bulge_x=0.4, bulge_y=0.3)
    b.box(1, 12, 4.5, 24, 'glass_light', z=20, bevel=1, tilt=(-0.1, 0.5))
    b.hot(1, 13, 1, 3, 'glass_light', shoulder=False)
    # roof pods
    b.box(58, 1, 150, 8, 'paint_white', z=12, bevel=(3, 3, 3, 1), bulge_y=0.55)
    for x in range(72, 150, 13):
        b.set_line(b.mask_line([(x, 3), (x, 6)]), 1)
    b.box(160, 2, 200, 8, 'metal_light', z=12, bevel=(2, 2, 2.5, 1), bulge_y=0.5)
    # ---------------------------------------------------------- hot spots on paint
    b.hot(11, 9, 1, 4, 'paint_yellow', shoulder=False)
    b.hot(22, 5, 4, 1, 'paint_yellow')
    for x in (62, 122, 186):
        b.hot(x, 32, 5, 1, 'chrome', shoulder=False)
    b.hot(30, 48, 5, 1, 'paint_red')
    b.hot(210, 7, 3, 1, 'paint_yellow')
    return b


if __name__ == '__main__':
    b = build_bus()
    img = harden_alpha(b.image(shadow_k=16))
    img.save(OUT + 'bus_L.png')
    print(img.size, count_colors(img))
    zoom(img, 5, name='bus.png')
