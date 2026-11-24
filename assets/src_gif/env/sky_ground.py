from common import *


def make_sky():
    img = canvas()
    rect(img, 0, 0, W - 1, 5, "sky_m")
    rect(img, 0, 6, W - 1, 20, "sky")
    rect(img, 0, 9, W - 1, 20, "sky")
    rect(img, 0, 21, W - 1, 95, "sky")
    rect(img, 0, 96, W - 1, FACADE_BASE_Y - 1, "sky_hl")
    # band edges: a slightly lighter transitional row (flat, no dither)
    rect(img, 0, 9, W - 1, 9, "sky")
    # clouds: (cx, base_y, blobs relative)
    def cloud(cx, by, blobs, flat=True):
        S = blob_mask([(cx + dx, by + dy, *r) for dx, dy, *r in blobs])
        S = {(x, y) for x, y in S if y <= by}
        for x, y in S:
            if (x, y + 1) not in S:
                col = "cloud_d"
            elif (x, y + 2) not in S or (x, y + 3) not in S:
                col = "cloud_s"
            elif (x - 2, y) not in S and (x, y + 4) not in S:
                col = "cloud_s"
            else:
                col = "cloud"
            put(img, x, y, col)
    # cloud over H1 (x124-190, free above y58)
    cloud(150, 40, [(-22, -3, 6), (-12, -9, 8), (2, -13, 10), (16, -8, 8), (26, -3, 6), (0, -3, 9, 5)])
    # cloud over H3 (x244-316, free above y80)
    cloud(282, 62, [(-20, -2, 5), (-10, -6, 7), (3, -10, 9), (15, -6, 7), (23, -2, 5), (0, -2, 9, 4)])
    # small cloud above H4 (x316-384, free above y44)
    cloud(345, 28, [(-12, -2, 4), (-3, -6, 6), (8, -4, 5), (15, -1, 3), (0, -1, 8, 3)])
    return img


def make_skyline():
    img = canvas()
    rnd = random.Random(7)
    # far row: tube houses, haze_l
    x = -4
    rows = []
    while x < W:
        w = rnd.choice([9, 11, 13, 15])
        top = rnd.choice([64, 70, 76, 84, 92, 100])
        rows.append((x, w, top))
        x += w
    for (x, w, top) in rows:
        rect(img, x, top, x + w - 1, 150, "haze_l")
    # roofs: small parapet notch and tanks/antennas on the far row
    for i, (x, w, top) in enumerate(rows):
        if i % 4 == 1:  # water tank
            tx = x + w // 2 - 2
            rect(img, tx, top - 5, tx + 4, top - 1, "haze")
            rect(img, tx + 1, top - 6, tx + 3, top - 6, "haze")
            rect(img, tx + 1, top - 1, tx + 1, top - 1, "haze_d")
            rect(img, tx + 3, top - 1, tx + 3, top - 1, "haze_d")
        if i % 4 == 3:  # antenna
            ax = x + 3
            line(img, ax, top - 8, ax, top - 1, "haze")
            line(img, ax - 2, top - 7, ax + 2, top - 7, "haze")
            line(img, ax - 1, top - 5, ax + 1, top - 5, "haze")
        if i % 3 == 0:  # slight lighter-darker side
            rect(img, x + w - 2, top, x + w - 1, 150, "haze")
    # window dashes on far row (low contrast)
    for (x, w, top) in rows:
        for yy in range(top + 5, 140, 9):
            for xx in range(x + 2, x + w - 3, 5):
                rect(img, xx, yy, xx + 1, yy + 2, "haze")
    # near row: lower, a bit darker haze
    x = -6
    near = []
    while x < W:
        w = rnd.choice([12, 14, 17, 20])
        top = rnd.choice([112, 118, 124, 130])
        near.append((x, w, top))
        x += w
    for (x, w, top) in near:
        rect(img, x, top, x + w - 1, 150, "haze")
        rect(img, x, top, x + w - 1, top, "haze_l")
        for yy in range(top + 4, 150, 8):
            rect(img, x + 2, yy, x + 3, yy + 3, "haze_d" if (x // 3) % 3 == 0 else "haze_l")
    # far tree line: clumps along y ~ 126-142
    for cx in range(-6, W + 8, 7):
        r = 4 + (cx * 7 % 3)
        cy = 142 - (cx * 5 % 4)
        sp(img, blob_mask([(cx, cy, r + 1, r)]), "haze_d")
        sp(img, blob_mask([(cx - 1, cy - 1, r - 1, r - 1)]), "haze")
    rect(img, 0, 146, W - 1, 156, "haze_d")
    rect(img, 0, 157, W - 1, FACADE_BASE_Y - 1, "haze")
    rect(img, 0, 157, W - 1, 157, "haze_d")
    for x in range(4, W, 23):
        rect(img, x, 164, x + 9, 164, "haze_l"); rect(img, x + 3, 175, x + 14, 175, "haze_l")
    return img


def make_ground():
    img = canvas()
    y0, y1 = SIDEWALK_Y0, SIDEWALK_Y1
    rect(img, 0, y0, W - 1, y1, "pave")
    rect(img, 0, y0, W - 1, y0, "pave_l")            # lit top edge
    rect(img, 0, y0 + 1, W - 1, y0 + 1, "pave_l")
    rows = [(y0 + 2, y0 + 7), (y0 + 8, y1 - 1)]
    for ri, (ya, yb) in enumerate(rows):
        off = 0 if ri == 0 else 8
        for x in range(-16 + off, W, 16):
            # tile: lit top-left, joint right + bottom
            rect(img, x + 1, ya, x + 14, yb - 1, "pave" if (x // 16 + ri) % 2 == 0 else "pave_l")
            rect(img, x + 15, ya, x + 15, yb, "pave_d")
            rect(img, x, yb, x + 15, yb, "pave_d")
    # redo top rows lit band and bottom shade
    rect(img, 0, y0, W - 1, y0, "pave_l")
    rect(img, 0, y1, W - 1, y1, "pave_d")
    # curb
    rect(img, 0, CURB_Y0, W - 1, CURB_Y0, "grey_hl")
    rect(img, 0, CURB_Y0 + 1, W - 1, CURB_Y0 + 1, "grey_l")
    rect(img, 0, CURB_Y1, W - 1, CURB_Y1, "grey")
    for x in range(10, W, 40):
        rect(img, x, CURB_Y0 + 1, x, CURB_Y1, "grey")
    # road
    rect(img, 0, ROAD_Y0, W - 1, ROAD_Y1, "road")
    rect(img, 0, ROAD_Y0, W - 1, ROAD_Y0 + 1, "road_d")      # gutter shade under the curb
    rect(img, 0, ROAD_Y1 - 1, W - 1, ROAD_Y1, "road_d")
    for x in range(6, W, 36):
        rect(img, x, 209, x + 17, 209, "lane")
    for x in range(30, W, 90):  # drain grate
        rect(img, x, ROAD_Y0 + 2, x + 9, ROAD_Y0 + 3, "road_l")
    return img


if __name__ == "__main__":
    save_asset("env", "sky", make_sky(), anchor=(0, 0), notes="z0 flat sky bands + 3 clouds")
    save_asset("env", "skyline", make_skyline(), anchor=(0, 0), notes="z1 haze skyline")
    save_asset("env", "ground", make_ground(), anchor=(0, 0), notes="sidewalk+curb+road")
