from common import *


def cloud(im, blobs):
    S = blob_mask(blobs)
    for (x, y) in S:
        col = 'cloud'
        if (x, y + 1) not in S:
            col = 'cloud_d'
        elif (x, y + 2) not in S:
            col = 'cloud_s'
        put(im, x, y, col)


def sky():
    im = canvas()
    rect(im, 0, 0, W - 1, 12, 'sky_m')
    rect(im, 0, 13, W - 1, 140, 'sky')
    rect(im, 0, 141, W - 1, H - 1, 'sky_hl')
    # upper-right hero cloud
    cloud(im, [(318, 36, 9, 6), (331, 31, 10, 8), (346, 34, 9, 6), (358, 37, 7, 4), (326, 40, 20, 3), (344, 40, 18, 3)])
    # small upper-middle clouds
    cloud(im, [(106, 17, 6, 3), (116, 14, 6, 4), (126, 17, 5, 3), (114, 19, 14, 2)])
    cloud(im, [(262, 11, 4, 2), (270, 9, 4, 3), (278, 11, 4, 2), (270, 13, 9, 1)])
    cloud(im, [(40, 24, 4, 2), (46, 22, 4, 3), (53, 24, 3, 2), (47, 26, 8, 1)])
    return im


def distance():
    im = canvas()
    hl, h, hd = 'haze_l', 'haze', 'haze_d'
    # skyline x>=296
    blds = [(296, 312, 152), (312, 323, 142), (323, 339, 155), (339, 351, 146), (351, 366, 153), (366, 384, 144)]
    for (a, b, top) in blds:
        rect(im, a, top, b - 1, 171, hl)
        line(im, b - 1, top, b - 1, 171, 'haze')       # soft shade side
        for yy in range(top + 4, 168, 5):
            for xx in range(a + 2, b - 3, 4):
                put(im, xx, yy, 'haze'); put(im, xx + 1, yy, 'haze')
    # rooftop water tanks
    def tank(x, y):
        rect(im, x, y + 4, x + 1, y + 6, hd); rect(im, x + 5, y + 4, x + 6, y + 6, hd)
        ellipse(im, x, y, x + 6, y + 4, 'haze')
        line(im, x + 1, y + 1, x + 3, y + 1, 'haze_l')
    tank(315, 135); tank(355, 146); tank(371, 137)
    put(im, 330, 153, 'haze'); line(im, 330, 149, 330, 154, 'haze')   # antenna
    # river
    rect(im, 296, 163, W - 1, 172, 'haze_l')
    for (x, y, n) in [(305, 166, 6), (322, 169, 8), (340, 165, 5), (357, 168, 7), (375, 166, 6), (333, 171, 4)]:
        line(im, x, y, x + n, y, 'sky_hl')
    # Long Bien truss: deck y160-161, piers, humped top chord with zig-zag lattice
    piers = [304, 344, 384]
    rect(im, 296, 160, W - 1, 160, 'haze')
    rect(im, 296, 161, W - 1, 161, 'haze_d')
    def top_y(x):  # humps over piers, sags mid-span
        d = min(abs(x - p) for p in piers)
        return 145 + int((d / 20.0) ** 1.6 * 7)
    prev = None
    for x in range(296, W):
        ty = top_y(x)
        put(im, x, ty, 'haze_d')
        if prev is not None and abs(ty - prev) > 1:
            for yy in range(min(ty, prev), max(ty, prev)):
                put(im, x, yy, 'haze_d')
        prev = ty
    # posts + diagonals every 5 px
    for x in range(296, W, 5):
        ty = top_y(x)
        line(im, x, ty, x, 159, 'haze')
    k = 0
    for x in range(296, W - 5, 5):
        ty1, ty2 = top_y(x), top_y(x + 5)
        if k % 2 == 0:
            line(im, x, 159, x + 5, ty2, 'haze')
        else:
            line(im, x, ty1, x + 5, 159, 'haze')
        k += 1
    # piers and reflections
    for p in (320, 362):
        rect(im, p - 1, 162, p + 1, 172, 'haze_d')
    for p in (320, 362):
        line(im, p - 1, 173, p + 1, 173, 'haze')
    # far street band, full width
    rect(im, 0, 172, W - 1, 186, 'haze_l')
    line(im, 0, 172, W - 1, 172, 'haze')
    for x in range(4, W, 22):
        line(im, x, 180, x + 9, 180, 'sky_hl')
    # far low roofs/trees silhouettes along the band (left + mid), no outlines
    for (a, b, top) in [(0, 14, 163), (14, 30, 167), (200, 216, 166), (216, 236, 164), (236, 254, 167), (254, 274, 165)]:
        rect(im, a, top, b - 1, 171, 'haze_l')
    for cx, cy, r in [(36, 165, 5), (44, 167, 4), (186, 167, 5), (284, 166, 4), (292, 168, 4)]:
        for (x, y) in blob_mask([(cx, cy, r)]):
            if y <= 171:
                put(im, x, y, 'haze')
    return im


def ground():
    im = canvas()
    # sidewalk: running-bond tiles 12x4 (+1 joint), alternating two warm greys, lit top edge
    rect(im, 0, SIDEWALK_Y0, W - 1, SIDEWALK_Y1, 'pave')
    rows = [(187, 190), (192, 195), (197, 198)]
    for r, (a, b) in enumerate(rows):
        off = (r % 2) * 6
        for i, x in enumerate(range(-12 + off, W, 12)):
            x0, x1 = max(0, x), min(W - 1, x + 10)
            if x1 < x0: continue
            if (i + r) % 2: rect(im, x0, a, x1, b, 'pave_l')
            if 0 <= x + 11 < W: line(im, x + 11, a, x + 11, b + 1, 'pave_d')
        line(im, 0, b + 1, W - 1, b + 1, 'pave_d')
    line(im, 0, SIDEWALK_Y0, W - 1, SIDEWALK_Y0, 'pave_l')
    # curb
    rect(im, 0, 200, W - 1, 200, 'grey_hl')
    rect(im, 0, 201, W - 1, 201, 'grey_l')
    rect(im, 0, 202, W - 1, 202, 'grey_m')
    for x in range(14, W, 48):
        line(im, x, 200, x, 202, 'grey')     # curb stone joints
    # road
    rect(im, 0, ROAD_Y0, W - 1, ROAD_Y1, 'road')
    line(im, 0, ROAD_Y0, W - 1, ROAD_Y0, 'road_d')
    for x in range(6, W, 40):
        rect(im, x, 209, x + 17, 210, 'lane')
    return im
