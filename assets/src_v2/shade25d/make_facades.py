from common import *
import numpy as np

W, H = 640, 176
L = default_lib()
b = Buf(W, H, L)
rng = np.random.RandomState(12)
HAZE = np.array([176, 206, 236], float)


def window(x, y, w, h, frame='wall_white', shutters=False, light=False, curtain=None):
    b.box(x - 1, y - 1, x + w + 1, y + h + 1, frame, z=3, bevel=1.2)
    M = b.mask_rect(x, y, x + w, y + h)
    b.erase(M)
    b.box(x, y, x + w, y + h, 'glass', z=1, bevel=0.8, bulge_y=0.3, bias=0.12 if light else 0.0)
    if curtain:
        b.decal(b.mask_rect(x + 1, y + 1, x + w // 2 + 1, y + h - 1), curtain, bias=-0.08)
    b.glare(M, offset=x * 0.3, period=30, bands=((0, 4, 0.15), (7, 2, 0.24)))
    if w > 12:
        b.cyl_v(x + w // 2 - 1, y, x + w // 2 + 1, y + h, frame, z=4, cap=0.5)
    b.box(x - 2, y + h + 1, x + w + 2, y + h + 4, 'wall_white', z=5, bevel=1.2, bulge_y=0.5)
    if shutters:
        sw = max(4, w // 2 - 1)
        for sx in (x - sw - 2, x + w + 2):
            b.box(sx, y - 1, sx + sw, y + h + 2, 'paint_green', z=4, bevel=1.0, bulge_x=0.1)
            for yy in range(y + 1, y + h + 1, 2):
                b.set_line(b.mask_line([(sx + 1, yy), (sx + sw - 2, yy)]), 1)


def balcony(x0, x1, yf, door=True, plants=True, laundry=False, wall='wall_cream'):
    if door:
        b.erase(b.mask_rect(x0 + 4, yf - 26, x1 - 4, yf))
        b.box(x0 + 4, yf - 26, x1 - 4, yf, 'interior', z=-1, bevel=0, bias=0.1)
        b.box(x0 + 4, yf - 26, x1 - 4, yf - 4, 'glass', z=0.5, bevel=0.5, bulge_y=0.3)
        b.glare(b.mask_rect(x0 + 4, yf - 26, x1 - 4, yf - 4), offset=x0, period=30, bands=((0, 4, 0.15), (7, 2, 0.22)))
        b.cyl_v(x0 + 3, yf - 28, x0 + 5, yf, 'wall_white', z=3, cap=0.5)
        b.cyl_v(x1 - 5, yf - 28, x1 - 3, yf, 'wall_white', z=3, cap=0.5)
        b.cyl_h(x0 + 3, yf - 29, x1 - 3, yf - 27, 'wall_white', z=3, cap=0.5)
    b.box(x0 - 3, yf, x1 + 3, yf + 4, wall, z=7, bevel=(1, 1, 1.5, 1.5), bulge_y=0.4)
    for x in range(x0 - 1, x1 + 1, 3):
        b.cyl_v(x, yf - 10, x + 1.2, yf, 'metal_dark', z=8, cap=0.3)
    b.cyl_h(x0 - 3, yf - 12, x1 + 3, yf - 10, 'metal_dark', z=8.5, cap=0.5)
    if plants:
        for x in range(x0 + 2, x1 - 2, 9):
            if rng.rand() < 0.75:
                b.box(x, yf - 5, x + 6, yf, 'roof_tile', z=9, bevel=1.2)
                b.ellipsoid(x + 3, yf - 8, 4.2, 3.6, ['leaf_a', 'leaf_b', 'leaf_c'][rng.randint(3)], z=9, rz=3)
                if rng.rand() < 0.5:
                    b.ellipsoid(x + 4.5, yf - 10, 1.8, 1.5, ['bract_b', 'sign_yellow', 'bract_a'][rng.randint(3)], z=11)
    if laundry:
        for x in range(x0 + 2, x1 - 4, 5):
            b.box(x, yf - 10, x + 3, yf - 3 - rng.randint(0, 3), ['cloth_red', 'cloth_white', 'cloth_blue', 'sign_yellow'][rng.randint(4)],
                  z=9, bevel=0.6)


def ac_unit(x, y):
    b.box(x, y, x + 13, y + 9, 'paint_white', z=8, bevel=1.8, bulge_y=0.5)
    b.decal(b.mask_ellipse(x + 5, y + 4.5, 3.3, 3.3), 'metal_dark')
    b.decal(b.mask_ellipse(x + 5, y + 4.5, 1.2, 1.2), 'metal_light')
    for k in range(3):
        b.decal(b.mask_rect(x + 9, y + 2 + k * 2, x + 12, y + 3 + k * 2), 'metal_dark')
    b.cyl_v(x + 6, y + 9, x + 7, y + 14, 'metal_dark', z=7, cap=0.2)
    b.hot(x + 2, y + 1, 2, 1, 'paint_white', shoulder=False)


def tank(x, yb, mat='water_tank', h=20, w=12):
    b.cyl_v(x, yb - h, x + w, yb, mat, z=9, cap=3.5)
    b.box(x + 3, yb - h - 3, x + w - 3, yb - h + 1, 'tank_steel', z=9, bevel=(1.5, 1.5, 1.5, 0.5))
    for xx in (x + 1, x + w - 3):
        b.box(xx, yb, xx + 2, yb + 4, 'metal_dark', z=7, bevel=0.4)
    b.hot(x + 3, yb - h + 4, 1, 4, mat, shoulder=False)
    b.set_line(b.mask_line([(x + 1, yb - 7), (x + w - 2, yb - 7)]), 1)


def antenna(x, yb):
    b.capsule((x, yb), (x, yb - 18), 0.8, 0.8, 'metal_dark', z=8)
    for k, wd in enumerate((7, 5, 4)):
        yy = yb - 18 + k * 4
        b.capsule((x - wd, yy), (x + wd, yy), 0.7, 0.7, 'metal_dark', z=8)


def shop(x0, x1, yt, yb, sign_text, board, txt, awning=('sign_red', 'sign_white'), shutter_open=14, goods=True, wall='wall_cream'):
    # opening
    ox0, ox1 = x0 + 8, x1 - 8
    b.erase(b.mask_rect(ox0, yt + 18, ox1, yb))
    b.box(ox0, yt + 18, ox1, yb, 'interior', z=-2, bevel=0, bias=0.12)
    if goods:
        for row, yy in enumerate((yt + 26, yt + 36, yt + 46)):
            b.box(ox0 + 2, yy + 6, ox1 - 2, yy + 8, 'metal_dark', z=-1, bevel=0.5)
            x = ox0 + 3
            while x < ox1 - 6:
                w = rng.randint(4, 8)
                hh = rng.randint(4, 7)
                b.box(x, yy + 6 - hh, x + w, yy + 6, ['sign_red', 'sign_yellow', 'plastic_teal', 'cloth_blue', 'paint_orange', 'sign_white', 'leaf_a'][rng.randint(7)],
                      z=0.0, bevel=0.8, bias=0.05)
                x += w + 1
    b.box(ox0 - 3, yt + 16, ox0, yb, wall, z=4, bevel=1)
    b.box(ox1, yt + 16, ox1 + 3, yb, wall, z=4, bevel=1)
    # roll-down shutter
    sh = yt + 18 + shutter_open
    b.box(ox0, yt + 18, ox1, sh, 'shutter', z=1.5, bevel=(0, 0, 0, 1.5))
    for yy in range(yt + 19, sh, 3):
        b.set_line(b.mask_line([(ox0, yy), (ox1 - 1, yy)]), 1)
    b.cyl_h(ox0 - 2, yt + 15, ox1 + 2, yt + 20, 'metal_light', z=6, cap=1)
    # awning
    b.box(x0 + 2, yt + 6, x1 - 2, yt + 18, awning[0], z=8, bevel=(0, 0, 1.5, 3), bulge_y=0.7)
    for x in range(x0 + 2, x1 - 2, 12):
        b.decal(b.mask_rect(x + 6, yt + 6, x + 12, yt + 18), awning[1])
    # sign board
    tw = len(sign_text.replace(' ', '')) * 6 + sign_text.count(' ') * 6 + 8
    sx0 = (x0 + x1) // 2 - tw // 2
    b.box(sx0, yt - 12, sx0 + tw, yt + 6, board, z=9, bevel=2.5, bulge_y=0.35)
    b.text(sx0 + 4, yt - 10, sign_text, txt)
    b.hot(sx0 + 2, yt - 10, 2, 1, board)
    b.box(x0 + 2, yb - 5, x1 - 2, yb, 'concrete', z=6, bevel=(0, 0, 1.5, 0))


def ledge(x0, x1, y, mat='wall_white', h=4):
    b.box(x0 - 2, y, x1 + 2, y + h, mat, z=5, bevel=(1, 1, 1.8, 1.8), bulge_y=0.5)


def wall(x0, x1, top, mat, parapet=True):
    b.box(x0, top, x1, H, mat, z=0, bevel=(0, 0, 0, 0))
    # grime streaks + vertical tone shift
    ys, xs = np.mgrid[0:H, 0:W]
    m = b.mask_rect(x0, top, x1, H)
    n = vnoise(H, W, 2.5, 22, 5, ox=x0 * 3)
    b.tone(m, (n - 0.5) * 0.12 - 0.05 * np.clip((ys - top) / 140.0, 0, 1))
    if parapet:
        b.box(x0 - 2, top - 5, x1 + 2, top + 2, mat, z=5, bevel=(1, 1, 2.5, 1.5), bulge_y=0.5)
        ledge(x0, x1, top + 2, 'wall_white', 3)


def house(x0, x1, top, wallmat, floors_y, shop_args, kind):
    wall(x0, x1, top, wallmat)
    # side party-wall shade
    b.tone(b.mask_rect(x1 - 4, top, x1, H), -0.18)
    b.tone(b.mask_rect(x0, top + 3, x0 + 2, H), 0.06)
    mid = (x0 + x1) // 2
    for i, yf in enumerate(floors_y):
        ledge(x0 + 2, x1 - 2, yf + 2)
        if kind[i % len(kind)] == 'bal':
            balcony(x0 + 10, mid - 6, yf, laundry=(i == 1))
            window(mid + 8, yf - 24, 14, 20, shutters=True)
            ac_unit(x1 - 26, yf - 14)
        elif kind[i % len(kind)] == 'win':
            window(x0 + 14, yf - 24, 16, 20, shutters=(i % 2 == 0))
            window(mid + 6, yf - 24, 16, 20, shutters=(i % 2 == 1), light=(i == 2))
            ac_unit(x1 - 30, yf - 20)
        else:
            balcony(mid - 4, x1 - 12, yf, laundry=(i == 0))
            window(x0 + 12, yf - 25, 18, 21, curtain='sign_red' if i == 2 else None)
            ac_unit(x0 + 40, yf - 14) if x1 - x0 > 130 else None
    shop(x0 + 2, x1 - 2, 132, H, *shop_args)


# --- houses -------------------------------------------------------------
# H1
house(0, 152, 48, 'wall_yellow', (112, 80), ('TẠP HÓA', 'sign_red', 'sign_yellow', ('sign_red', 'sign_white')), ['bal', 'win'])
tank(18, 48, 'water_tank', 20, 12)
tank(34, 48, 'tank_steel', 16, 10)
antenna(120, 48)
# H2
house(152, 300, 20, 'wall_teal', (112, 80, 48), ('PHỞ BÒ', 'sign_white', 'sign_red', ('paint_green', 'sign_white')), ['win', 'bal2', 'bal'])
b.box(262, 8, 288, 20, 'wall_white', z=6, bevel=1.5)
b.box(270, 11, 278, 20, 'metal_dark', z=7, bevel=1)
# H3
house(300, 465, 48, 'wall_pink', (112, 80), ('CẮT TÓC', 'sign_blue', 'sign_white', ('plastic_blue', 'sign_white')), ['bal2', 'win'])
b.box(298, 38, 467, 52, 'roof_tile', z=3, bevel=(0, 0, 3, 0), bulge_y=0.8)
antenna(330, 38)
# H4
house(465, 640, 22, 'wall_blue', (112, 80, 48), ('ĐIỆN MÁY', 'sign_green', 'sign_white', ('sign_yellow', 'sign_red')), ['bal', 'bal2', 'win'])
tank(560, 22, 'tank_steel', 17, 13)
tank(580, 22, 'water_tank', 17, 12)
antenna(500, 22)

img = harden_alpha(b.image(shadow_k=14))
# lower contrast: haze toward sky
a = np.array(img).astype(float)
k = 0.20
a[..., :3] = a[..., :3] * (1 - k) + HAZE * k
lum = a[..., :3].mean(-1, keepdims=True)
a[..., :3] = a[..., :3] * 0.88 + lum * 0.12
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
img.save(OUT + 'facades.png')
print(img.size, count_colors(img))
zoom(img, 2, name='facades.png')
