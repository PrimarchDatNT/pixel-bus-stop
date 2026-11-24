from parts import *

WALL = ["wb", "wy", "wp", "wc", "wy"]
GH = [36, 36, 36, 46, 36]   # ground-floor heights


def floors_of(i):
    x0, x1, top, n = HOUSES[i]
    gy = FACADE_BASE_Y - GH[i]
    y0 = top + 8
    u = n - 1
    ys = [y0 + round(k * (gy - y0) / u) for k in range(u + 1)]
    return gy, [(ys[k], ys[k + 1]) for k in range(u)]


# floor specs: wins=(xrel,w,mode,shutter,curtain) ; bal=(xr0,xr1) ; pots=[(xrel,kind)] ; hangs=[xrel]
SPECS = {
 0: [dict(wins=[(12, 11, "open", "sb", False), (40, 11, "open", "sb", True)], bal=(3, 60),
          pots=[(5, 0), (30, 1), (55, 2)], hangs=[26, 36], vent=(32, 108))],
 1: [dict(wins=[(12, 10, "open", "sb", False), (42, 10, "closed", "sh", False)], bal=(5, 60),
          pots=[(7, 2), (29, 0), (53, 1)], hangs=[21], vent=None),
     dict(wins=[(8, 9, "closed", "sh", False), (32, 16, "open", "sh", True)], bal=(2, 63),
          pots=[(4, 0), (22, 1), (56, 2), (60, 0)], hangs=[16], vent=None)],
 2: [dict(wins=[(21, 12, "open", "sb", False)], bal=(3, 50), pots=[(5, 0), (43, 2)], hangs=[], vent=None),
     dict(wins=[(9, 10, "open", "sh", True), (35, 10, "closed", "sb", False)], bal=(2, 51),
          pots=[(5, 1), (24, 0), (47, 2)], hangs=[], vent=None, laundry=(5, 49)),
     dict(wins=[(21, 12, "open", "sh", False)], bal=(3, 50), pots=[(6, 2), (42, 0)], hangs=[], vent=None),
     dict(wins=[(9, 10, "closed", "sb", False), (35, 10, "open", "sb", True)], bal=(2, 51),
          pots=[(4, 0), (24, 1), (46, 0)], hangs=[], vent=None)],
 3: [dict(wins=[(9, 9, "open", "sb", False), (31, 9, "closed", "sh", False)], bal=None,
          pots=[], hangs=[], vent=None, ac=(55, 6)),
     dict(wins=[(9, 9, "open", "sh", True), (31, 9, "open", "sb", False), (53, 9, "closed", "sh", False)],
          bal=(2, 69), pots=[(3, 2), (22, 0), (45, 1), (64, 0)], hangs=[], vent=None)],
 4: [dict(wins=[(12, 12, "open", "sb", False), (42, 12, "open", "sb", True)], bal=(3, 66),
          pots=[(5, 0), (30, 2), (59, 1)], hangs=[27, 37], vent=None, flag=True),
     dict(wins=[(10, 12, "closed", "sh", False), (42, 12, "half", "sh", False)], bal=None,
          pots=[], hangs=[], vent=None),
     dict(wins=[(12, 12, "open", "sh", True), (41, 14, "open", "sb", False)], bal=(3, 66),
          pots=[(6, 1), (28, 0), (58, 2)], hangs=[], vent=None)],
}


def base_wall(img, i):
    x0, x1, top, n = HOUSES[i]
    k = WALL[i]
    L, B, D = k + "_l", k, k + "_d"
    rect(img, x0, top, x1 - 1, FACADE_BASE_Y - 1, B)
    # parapet + cornice
    rect(img, x0, top, x1 - 1, top, D)
    rect(img, x0, top + 1, x1 - 1, top + 2, L)
    for x in range(x0 + 2, x1 - 4, 8):
        rect(img, x, top + 4, x + 5, top + 5, D)
        rect(img, x, top + 4, x + 5, top + 4, B)
        rect(img, x, top + 5, x, top + 5, B)
    rect(img, x0, top + 6, x1 - 1, top + 6, L)
    rect(img, x0, top + 7, x1 - 1, top + 7, D)
    # side shading
    rect(img, x0, top + 1, x0, FACADE_BASE_Y - 1, L)
    rect(img, x1 - 2, top + 3, x1 - 1, FACADE_BASE_Y - 1, D)
    rect(img, x1 - 1, top, x1 - 1, top + 2, D)


def upper_floors(img, i):
    x0, x1, top, n = HOUSES[i]
    k = WALL[i]
    L, B, D = k + "_l", k, k + "_d"
    gy, fl = floors_of(i)
    for fi, (ft, fe) in enumerate(fl):
        sp_ = SPECS[i][fi]
        # slab
        rect(img, x0, fe - 4, x1 - 1, fe - 4, L)
        rect(img, x0, fe - 3, x1 - 1, fe - 2, B)
        rect(img, x0, fe - 1, x1 - 1, fe - 1, D)
        if x0 == 0:
            pass
        rect(img, x0, fe - 4, x0, fe - 1, L)
        rect(img, x1 - 2, fe - 4, x1 - 1, fe - 1, D)
        yb = fe - 6
        hmax = 34 if i != 3 else 26
        yt = max(ft + 4, yb - hmax)
        if i == 3: yt = max(ft + 4, yb - 22)
        if sp_.get("vent"):
            vx, vy = sp_["vent"]
            sp(img, blob_mask([(x0 + vx, vy, 3)]), "wood_k")
            sp(img, blob_mask([(x0 + vx, vy, 2)]), D)
            put(img, x0 + vx - 1, vy - 1, L)
            rect(img, x0 + vx - 2, vy, x0 + vx + 2, vy, "wood_d")
        bal = sp_["bal"]
        if bal:
            bx0, bx1 = x0 + bal[0] - 1, x0 + bal[1] + 1
            rect(img, bx0, fe - 4, bx1, fe - 4, L)
            rect(img, bx0, fe, bx1, fe, D)
        for (xr, w, mode, s, cur) in sp_["wins"]:
            window(img, x0 + xr, yt, yb, w, mode, s, cur, k)
        if sp_.get("ac"):
            xr, dy = sp_["ac"]
            aircon(img, x0 + 54, yt + 10)
        if sp_.get("laundry"):
            a, b = sp_["laundry"]
            laundry(img, x0 + a, x0 + b, fe - 18)
        if bal:
            railing(img, x0 + bal[0], x0 + bal[1], fe - 4)
            for (xr, kind) in sp_["pots"]:
                pot(img, x0 + xr, fe - 5, kind)
            for xr in sp_["hangs"]:
                hang(img, x0 + xr, fe + 1, 5) if fi < len(fl) - 1 else None


def roof_clutter(img, i):
    x0, x1, top, n = HOUSES[i]
    if i == 0:
        antenna(img, x0 + 12, top, 15, 4)
        antenna(img, x0 + 52, top, 11, 3)
    if i == 1:
        tank(img, x0 + 44, top, 15, 11)
        antenna(img, x0 + 14, top, 13, 4)
    if i == 2:
        tank(img, x0 + 12, top, 16, 12)
        antenna(img, x0 + 40, top, 14, 4)
    if i == 3:
        antenna(img, x0 + 20, top, 12, 4)
        antenna(img, x0 + 58, top, 9, 3)
    if i == 4:
        tank(img, x0 + 8, top, 15, 11)
        antenna(img, x0 + 50, top, 12, 4)


def pipe(img, x, y0, y1):
    rect(img, x, y0, x + 1, y1, "grey_l")
    rect(img, x, y0, x, y1, "grey_hl")
    rect(img, x + 1, y0, x + 1, y1, "grey")
    for y in range(y0 + 6, y1, 18):
        rect(img, x - 1, y, x + 2, y, "grey_m")


def frame_opening(img, x0, y0, x1, y1, fill):
    rect(img, x0 - 1, y0 - 1, x1 + 1, y1 + 1, "wood_k")
    rect(img, x0, y0, x1, y1, fill)


# ------------------------------------------------------------------ ground floors
def ground_0(img):
    x0, gy = 60, FACADE_BASE_Y - 36
    # rolled-down shutter (grey slats), door
    frame_opening(img, x0 + 8, gy + 6, x0 + 40, FACADE_BASE_Y - 1, "grey_l")
    for y in range(gy + 7, FACADE_BASE_Y - 1, 2):
        rect(img, x0 + 8, y, x0 + 40, y, "grey")
    rect(img, x0 + 8, gy + 6, x0 + 40, gy + 9, "grey_hl")
    rect(img, x0 + 8, gy + 9, x0 + 40, gy + 9, "grey_m")
    rect(img, x0 + 8, gy + 7, x0 + 8, FACADE_BASE_Y - 1, "grey_hl")
    # door
    frame_opening(img, x0 + 46, gy + 8, x0 + 57, FACADE_BASE_Y - 1, "sb")
    for y in range(gy + 10, FACADE_BASE_Y - 1, 3):
        rect(img, x0 + 47, y, x0 + 56, y, "sb_d")
    rect(img, x0 + 46, gy + 8, x0 + 46, FACADE_BASE_Y - 1, "sb_l")
    put(img, x0 + 55, gy + 22, "yl")
    sign(img, x0 + 47, gy + 1, x0 + 56, gy + 5, "paper", "red", "12", "grey_l") if False else None
    rect(img, x0 + 46, gy + 2, x0 + 57, gy + 5, "paper")
    rect(img, x0 + 46, gy + 5, x0 + 57, gy + 5, "grey_l")
    text(img, x0 + 48, gy + 2, "12", "red_d")


def ground_1(img):
    x0 = 124
    gy = FACADE_BASE_Y - 36
    # signboard CÀ PHÊ
    sx0, sx1 = x0 + 10, x0 + 52
    sign(img, sx0, gy + 2, sx1, gy + 13, "wood_d", "yl_l", "CÀ PHÊ", "wood_k", "wood")
    # little coffee cup icon
    cx = sx1 - 8
    rect(img, cx, gy + 7, cx + 3, gy + 10, "white"); put(img, cx + 4, gy + 8, "white")
    put(img, cx + 4, gy + 9, "grey_hl"); rect(img, cx, gy + 10, cx + 3, gy + 10, "grey_l")
    put(img, cx + 1, gy + 5, "grey_hl"); put(img, cx + 2, gy + 4, "grey_hl") if False else None
    # opening
    ox0, ox1 = x0 + 9, x0 + 56
    oy0 = gy + 16
    frame_opening(img, ox0, oy0, ox1, FACADE_BASE_Y - 1, "wood")
    rect(img, ox0, oy0, ox1, oy0 + 1, "wood_d")
    # back wall boards
    for x in range(ox0 + 3, ox1, 7):
        rect(img, x, oy0 + 2, x, FACADE_BASE_Y - 1, "wood_l")
    # shelf with jars
    rect(img, ox0 + 2, oy0 + 6, ox0 + 18, oy0 + 6, "wood_d")
    for k, cc in enumerate(["red_l", "yl", "paper", "or", "teal", "paper"]):
        rect(img, ox0 + 3 + k * 3, oy0 + 2, ox0 + 4 + k * 3, oy0 + 5, cc)
    # hanging lamps
    for lx in (ox0 + 22, ox0 + 32, ox0 + 42):
        line(img, lx, oy0 + 2, lx, oy0 + 5, "wood_k")
        rect(img, lx - 1, oy0 + 6, lx + 1, oy0 + 7, "lamp")
        put(img, lx, oy0 + 8, "glow")
    # counter
    rect(img, ox0 + 2, FACADE_BASE_Y - 11, ox1 - 2, FACADE_BASE_Y - 11, "wc_l")
    rect(img, ox0 + 2, FACADE_BASE_Y - 10, ox1 - 2, FACADE_BASE_Y - 1, "wc_d")
    rect(img, ox0 + 2, FACADE_BASE_Y - 10, ox1 - 2, FACADE_BASE_Y - 10, "wc")
    # coffee machine
    rect(img, ox0 + 28, FACADE_BASE_Y - 17, ox0 + 36, FACADE_BASE_Y - 12, "grey")
    rect(img, ox0 + 28, FACADE_BASE_Y - 17, ox0 + 36, FACADE_BASE_Y - 17, "grey_hl")
    rect(img, ox0 + 30, FACADE_BASE_Y - 14, ox0 + 31, FACADE_BASE_Y - 12, "red")
    rect(img, ox0 + 38, FACADE_BASE_Y - 15, ox0 + 40, FACADE_BASE_Y - 12, "white")
    # side window + plaque
    window(img, x0 + 62, gy + 18, gy + 28, 4, "none", "sb", False, "wy")
    rect(img, x0 + 4, gy + 18, x0 + 6, gy + 23, "pb"); rect(img, x0 + 4, gy + 18, x0 + 6, gy + 18, "pb_l")


def ground_2(img):
    x0 = 190
    gy = FACADE_BASE_Y - 36
    # shop shutter
    frame_opening(img, x0 + 6, gy + 4, x0 + 36, FACADE_BASE_Y - 1, "grey_l")
    for y in range(gy + 5, FACADE_BASE_Y - 1, 2):
        rect(img, x0 + 6, y, x0 + 36, y, "grey")
    rect(img, x0 + 6, gy + 4, x0 + 36, gy + 8, "grey_hl")
    rect(img, x0 + 6, gy + 8, x0 + 36, gy + 8, "grey_m")
    rect(img, x0 + 6, gy + 5, x0 + 6, FACADE_BASE_Y - 1, "grey_hl")
    rect(img, x0 + 36, gy + 5, x0 + 36, FACADE_BASE_Y - 1, "grey_m")
    rect(img, x0 + 14, gy + 24, x0 + 16, gy + 25, "grey_d")      # shutter handle
    # side door
    frame_opening(img, x0 + 40, gy + 6, x0 + 51, FACADE_BASE_Y - 1, "sh")
    rect(img, x0 + 40, gy + 6, x0 + 40, FACADE_BASE_Y - 1, "sh_l")
    for y in range(gy + 8, FACADE_BASE_Y - 1, 3):
        rect(img, x0 + 41, y, x0 + 50, y, "sh_d")
    put(img, x0 + 49, gy + 20, "yl")
    rect(img, x0 + 41, gy + 1, x0 + 50, gy + 3, "paper"); text(img, x0 + 42, gy - 2, "") if False else None
    text(img, x0 + 43, gy, "") if False else None
    rect(img, x0 + 40, gy + 1, x0 + 51, gy + 3, "red"); rect(img, x0 + 41, gy + 2, x0 + 50, gy + 2, "yl_l")
    rect(img, x0 + 38, gy + 12, x0 + 38, gy + 14, "grey_d")


def ground_3(img):
    x0 = 244
    gy = FACADE_BASE_Y - 46
    by = FACADE_BASE_Y
    ox0, ox1 = 250, 309
    # signboard
    sign(img, ox0 + 2, gy + 1, ox1 - 2, gy + 12, "pb", "white", "TẠP HÓA", "pb_d", "pb_l")
    # interior
    oy0 = gy + 14
    frame_opening(img, ox0, oy0, ox1, by - 1, "wood_d")
    rect(img, ox0, oy0, ox1, oy0 + 1, "wood_k")
    # back wall in the middle: lighter, flat (shopkeeper gap)
    rect(img, 273, oy0 + 2, 288, 179, "wood")
    rect(img, 273, oy0 + 2, 288, oy0 + 2, "wood_l")
    # calendar on the back wall
    rect(img, 288, oy0 + 4, 291, oy0 + 10, "paper"); rect(img, 288, oy0 + 4, 291, oy0 + 5, "red"); put(img, 290, oy0 + 8, "grey")
    # shelves left x251..273, right 288..308
    goods = ["red_l", "yl", "pb_l", "sh_l", "or", "white", "pk_l", "teal", "yl_l", "bl_l"]
    rnd = random.Random(11)
    def shelf(xa, xb, rows):
        for r, py in enumerate(rows):
            rect(img, xa, py, xb, py, "wood_l")
            rect(img, xa, py + 1, xb, py + 1, "wood_k")
            x = xa + 1
            while x < xb - 1:
                w = rnd.choice([2, 2, 3]); h = rnd.choice([4, 5, 5, 6]) if r != 0 else rnd.choice([3, 4])
                cc = goods[rnd.randrange(len(goods))]
                rect(img, x, py - h, x + w - 1, py - 1, cc)
                rect(img, x, py - h, x, py - 1, "white") if cc not in ("white", "yl_l") else None
                put(img, x + w - 1, py - 1, "wood_k") if False else None
                if h >= 5 and w == 2:
                    rect(img, x, py - h, x + w - 1, py - h, "grey_l")
                x += w + 1 if rnd.random() < .8 else w + 2
    shelf(ox0 + 2, 272, [oy0 + 8, oy0 + 15, oy0 + 22])
    shelf(289, ox1 - 2, [oy0 + 8, oy0 + 15, oy0 + 22])
    # awning: striped, scalloped
    ay0, ay1 = oy0 - 1, oy0 + 3
    for x in range(ox0 - 2, ox1 + 3):
        s = ((x - (ox0 - 2)) // 4) % 2
        cl = "red_l" if s == 0 else "white"
        cd = "red" if s == 0 else "grey_hl"
        rect(img, x, ay0, x, ay1, cl)
        rect(img, x, ay1 - 1, x, ay1 - 1, cd)
        if ((x - (ox0 - 2)) % 4) in (1, 2):
            rect(img, x, ay1 + 1, x, ay1 + 1, cl)
            rect(img, x, ay1 + 1, x, ay1 + 1, cd) if False else None
    rect(img, ox0 - 2, ay0, ox1 + 2, ay0, "red")
    # hanging snack strips under the awning
    for sx in range(ox1 - 20, ox1 - 2, 4):
        line(img, sx, ay1 + 2, sx, ay1 + 9, "wood_k")
        for k in range(3):
            rect(img, sx - 1, ay1 + 3 + k * 3, sx + 1, ay1 + 4 + k * 3, goods[(sx + k) % len(goods)])
    for sx in range(ox0 + 6, ox0 + 22, 4):
        line(img, sx, ay1 + 2, sx, ay1 + 6, "wood_k")
        rect(img, sx - 1, ay1 + 3, sx + 1, ay1 + 5, goods[(sx * 3) % len(goods)])
    # counter (glass case + wood front)
    cy = 180
    rect(img, ox0 + 1, cy, ox1 - 1, cy, "wood_l")
    rect(img, ox0 + 1, cy + 1, ox1 - 1, by - 1, "tc")
    rect(img, ox0 + 1, cy + 1, ox1 - 1, cy + 1, "tc_l")
    rect(img, ox0 + 1, by - 1, ox1 - 1, by - 1, "tc_d")
    for x in range(ox0 + 4, ox1 - 2, 10):
        rect(img, x, cy + 3, x, by - 3, "tc_d")
    # goods on the counter (not in gap x274..287): left case, right jars
    rect(img, ox0 + 3, cy - 6, ox0 + 20, cy - 1, "glass_l")
    rect(img, ox0 + 3, cy - 6, ox0 + 20, cy - 6, "white")
    for k, cc in enumerate(["or_l", "yl", "pk_l", "sh_l", "red_l", "yl_l"]):
        rect(img, ox0 + 4 + k * 3, cy - 4, ox0 + 5 + k * 3, cy - 1, cc)
    line(img, ox0 + 4, cy - 5, ox0 + 6, cy - 5, "white")
    for k, cc in enumerate(["red_l", "pb_l", "yl", "paper"]):
        rect(img, 290 + k * 4, cy - 5, 292 + k * 4, cy - 1, cc)
        rect(img, 290 + k * 4, cy - 6, 292 + k * 4, cy - 6, "grey_l")
    # drinks cooler on far right
    rect(img, ox1 - 9, oy0 + 24, ox1 - 2, cy - 1, "wc_l") if False else None
    # iron grille pillar
    rect(img, ox1 + 1, oy0, ox1 + 1, by - 1, "wood_k")


def ground_4(img):
    x0 = 316
    gy = FACADE_BASE_Y - 36
    sign(img, x0 + 6, gy + 2, x0 + 62, gy + 13, "red", "white", "PHỞ BÒ", "red_d", "red_l")
    rect(img, x0 + 8, gy + 4, x0 + 8, gy + 4, "yl_l")
    # lanterns
    for lx in (x0 + 3, x0 + 65):
        line(img, lx, gy + 2, lx, gy + 5, "wood_k")
        sp(img, blob_mask([(lx, gy + 8, 2, 3)]), "red")
        put(img, lx - 1, gy + 7, "red_l"); put(img, lx, gy + 11, "yl")
    ox0, ox1 = x0 + 6, x0 + 62
    oy0 = gy + 15
    frame_opening(img, ox0, oy0, ox1, FACADE_BASE_Y - 1, "wood_d")
    # rolled-up shutter box
    rect(img, ox0, oy0, ox1, oy0 + 4, "grey_l")
    rect(img, ox0, oy0, ox1, oy0, "white")
    rect(img, ox0, oy0 + 3, ox1, oy0 + 3, "grey")
    rect(img, ox0, oy0 + 4, ox1, oy0 + 4, "grey_m")
    for x in range(ox0 + 4, ox1, 6):
        rect(img, x, oy0 + 1, x, oy0 + 2, "grey_hl")
    # back wall with menu boards
    rect(img, ox0 + 22, oy0 + 7, ox0 + 34, oy0 + 15, "paper")
    rect(img, ox0 + 22, oy0 + 7, ox0 + 34, oy0 + 7, "red")
    for k in range(3):
        rect(img, ox0 + 24, oy0 + 10 + k * 2, ox0 + 31 - k, oy0 + 10 + k * 2, "grey")
    rect(img, ox0 + 40, oy0 + 7, ox0 + 50, oy0 + 12, "yl_l"); rect(img, ox0 + 40, oy0 + 7, ox0 + 50, oy0 + 7, "or")
    # stainless broth pot on the counter + counter
    cy = FACADE_BASE_Y - 11
    rect(img, ox0 + 2, cy, ox0 + 54, cy, "grey_hl")
    rect(img, ox0 + 2, cy + 1, ox0 + 54, FACADE_BASE_Y - 1, "grey_l")
    rect(img, ox0 + 2, cy + 1, ox0 + 54, cy + 1, "white")
    rect(img, ox0 + 2, FACADE_BASE_Y - 1, ox0 + 54, FACADE_BASE_Y - 1, "grey")
    rect(img, ox0 + 6, cy - 7, ox0 + 15, cy - 1, "grey_l")
    rect(img, ox0 + 6, cy - 8, ox0 + 15, cy - 8, "white")
    rect(img, ox0 + 6, cy - 7, ox0 + 7, cy - 1, "grey_hl")
    rect(img, ox0 + 14, cy - 7, ox0 + 15, cy - 1, "grey")
    for k in range(3):
        put(img, ox0 + 8 + k * 2, cy - 10 - (k % 2), "grey_hl")
        put(img, ox0 + 9 + k * 2, cy - 12 - (k % 2), "white")
    # bowls
    for bx in (ox0 + 24, ox0 + 31, ox0 + 38):
        rect(img, bx, cy - 3, bx + 4, cy - 2, "white")
        rect(img, bx + 1, cy - 1, bx + 3, cy - 1, "white")
        rect(img, bx, cy - 4, bx + 4, cy - 4, "or_l")
    # hanging roast / herb baskets: skip. side pillars
    rect(img, x0 + 2, gy + 16, x0 + 3, FACADE_BASE_Y - 1, "wy_d")


def make_house(i):
    img = canvas()
    base_wall(img, i)
    upper_floors(img, i)
    gy, fl = floors_of(i)
    # ground
    [ground_0, ground_1, ground_2, ground_3, ground_4][i](img)
    x0, x1, top, n = HOUSES[i]
    if i == 2:
        pass
    if i == 4:
        pipe(img, x0 + 66, top + 8, FACADE_BASE_Y - 1) if False else None
    roof_clutter(img, i)
    # clip to house box
    out = canvas()
    out.paste(img.crop((x0, 0, min(x1, W), H)), (x0, 0))
    return out


if __name__ == "__main__":
    allh = canvas()
    for i in range(5):
        im = make_house(i)
        save_asset("env", f"house_{i}", im, anchor=(0, 0))
        allh.alpha_composite(im)
    save_asset("env", "houses", allh, anchor=(0, 0), notes="all five houses, one layer")
