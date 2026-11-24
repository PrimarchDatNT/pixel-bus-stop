from common import *


def vendor(f):
    CW, CH = 38, 28
    img = new(CW, CH)
    by = 26
    # ---- stool
    rect(img, 24, 20, 31, 21, "brown_d")
    rect(img, 24, 20, 31, 20, "ochre")
    rect(img, 25, 22, 25, by, "brown_d"); rect(img, 30, 22, 30, by, "brown_d")
    # ---- woman (facing LEFT toward the brazier), seated, hunched
    # legs: thigh forward (left), shin down
    rect(img, 15, 19, 27, 21, "plum")             # thighs
    rect(img, 15, 19, 27, 19, "mauve")
    rect(img, 14, 22, 16, by - 1, "plum")         # shins
    rect(img, 12, by - 1, 16, by, "ink")          # shoe
    rect(img, 22, 22, 24, by - 1, "bloom_k"); rect(img, 21, by - 1, 24, by, "ink")
    # coat torso (padded, dark green) leaning forward
    poly(img, [(23, 20), (30, 20), (31, 12), (27, 9), (23, 10), (21, 15)], "green_d")
    poly(img, [(23, 19), (28, 19), (29, 13), (26, 10), (23, 11), (22, 15)], "green")
    rect(img, 22, 17, 30, 17, "green_d")   # padding seam
    rect(img, 22, 14, 29, 14, "green_d")
    line(img, 29, 12, 30, 19, "teal_k")
    # scarf (mauve) round the neck
    rect(img, 20, 10, 26, 12, "mauve")
    rect(img, 20, 10, 26, 10, "bloom_l")
    rect(img, 25, 13, 27, 16, "mauve")  # tail of scarf hanging back
    put(img, 26, 17, "bloom_d")
    # head (face to left)
    rect(img, 19, 5, 24, 10, "skin2")
    rect(img, 19, 5, 20, 7, "skin1")
    put(img, 20, 7, "ink")                 # eye
    put(img, 18, 8, "skin2")               # nose
    rect(img, 19, 9, 20, 9, "salmon")      # cheek
    rect(img, 24, 5, 25, 9, "ink")         # hair bun / back
    # non la (conical hat), light from upper-left
    poly(img, [(21, 0), (13, 6), (30, 6)], "sand")
    poly(img, [(21, 0), (13, 6), (21, 6)], "glow")
    poly(img, [(24, 2), (30, 6), (23, 6)], "ochre")
    line(img, 13, 6, 30, 6, "ochre")
    for xx in range(15, 29, 3):
        put(img, xx, 5, "ochre")
    line(img, 25, 7, 24, 10, "red")        # chin strap
    # arms reaching to the fire
    thick(img, 24, 13, 17, 16, "green_d", 1)
    thick(img, 23, 14, 16, 17, "green", 1)
    put(img, 15, 17, "skin2"); put(img, 15, 16, "skin1")
    img = outline(img, "ink")
    # ---- brazier (clay stove) in front-left, drawn after so no ink outline between; use brown_k
    br = new(18, 14)
    # bucket body (terracotta)
    poly(br, [(2, 5), (15, 5), (14, 13), (3, 13)], "clay")
    poly(br, [(2, 5), (6, 5), (6, 13), (3, 13)], "orange")
    poly(br, [(11, 5), (15, 5), (14, 13), (11, 13)], "rust")
    rect(br, 1, 4, 16, 5, "rust"); rect(br, 1, 4, 16, 4, "clay")
    rect(br, 6, 9, 10, 11, "brown_k"); rect(br, 6, 9, 10, 9, "red_d")   # draught door
    put(br, 8, 10, "orange") if f != 1 else put(br, 7, 10, "red_hot")
    # glowing coals on top
    coal_sets = [
        {3: "red_hot", 5: "yellow", 7: "orange", 9: "red_hot", 11: "yellow", 13: "orange"},
        {3: "orange", 5: "red_hot", 7: "yellow", 9: "orange", 11: "red_hot", 13: "yellow"},
        {3: "yellow", 5: "orange", 7: "red_hot", 9: "yellow", 11: "orange", 13: "red_hot"},
    ][f]
    rect(br, 2, 3, 15, 3, "brown_k")
    for x, col in coal_sets.items():
        put(br, x, 3, col); put(br, x + 1, 3, "red_d" if col != "yellow" else "orange")
    br = outline(br, "brown_k")
    # grill + food on top: corn cobs and sweet potatoes
    food = new(18, 7)
    # corn cobs (yellow with brown char marks)
    for x0 in (2, 6):
        rect(food, x0, 2, x0 + 3, 4, "yellow")
        rect(food, x0, 2, x0 + 3, 2, "glow")
        put(food, x0 + 1, 3, "gold"); put(food, x0 + 3, 4, "ochre")
        put(food, x0 + 2, 4, "brown_d"); put(food, x0, 3, "ochre")
        rect(food, x0 - 1, 3, x0 - 1, 3, "green")   # husk tip
    # sweet potatoes (purple-brown)
    for x0 in (10, 14):
        ellipse(food, x0, 2, x0 + 3, 4, "brown_d")
        put(food, x0 + 1, 2, "mauve"); put(food, x0 + 1, 3, "rust")
        put(food, x0 + 3, 3, "brown_k")
    # grill wire
    line(food, 1, 5, 16, 5, "slate")
    for x in range(2, 16, 3):
        put(food, x, 6, "slate_d")
    img.alpha_composite(br, (0, CH - 14 - 1 + 1 - 1 + 2 - 2 + 1 - 1 + 1))
    img.alpha_composite(food, (1, CH - 14 - 3))
    # ember sparks
    sp = [(5, 14), (11, 13), (8, 15)][f]
    put(img, sp[0] + 3, CH - 14 - 3 - (f), "yellow")
    if f == 2:
        put(img, 12, CH - 22, "orange")
    return img


def puff_density(img, cx, cy, r, dens):
    px = img.load()
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if not (0 <= x < img.width and 0 <= y < img.height):
                continue
            d = math.hypot(x - cx, y - cy)
            if d > r:
                continue
            e = d / r
            dd = dens * (1 - 0.55 * e)
            if BAYER4[y % 4][x % 4] < dd * 16:
                col = "white" if (e < 0.5 and (x - cx + y - cy) < 1) else ("grey_l" if e < 0.8 else "grey")
                px[x, y] = c(col)


def smoke(f):
    img = new(18, 24)
    t = f / 5
    cx0, cy0 = 8, 19 - f * 3.0
    r = 3.2 + t * 5.0
    dens = 1.5 - t * 1.25
    puff_density(img, cx0 + math.sin(f * 1.1) * 1.5, cy0, r, dens)
    # trailing smaller puffs
    for k in (1, 2):
        ff = max(0, f - k * 1.6)
        if ff <= 0 and f > 0:
            pass
        puff_density(img, cx0 + math.sin((f - k) * 1.1 + 1) * 2, cy0 + k * 4 * (1 - t * 0.2), max(1.6, r * 0.55), dens * 0.8 * (1 - k * 0.2) if f < 5 else 0)
    return img


def breath(f):
    img = new(9, 6)
    r = [1.3, 2.0, 2.6, 3.0][f]
    puff_density(img, 2 + f * 1.4, 3 - f * 0.3, r, [1.1, 0.9, 0.6, 0.35][f])
    return img


def fog(peak, seed, tiles):
    Wd, Hd = 480, 24
    img = new(Wd, Hd)
    px = img.load()
    rng = random.Random(seed)
    comps = [(tiles[0], rng.random() * 6.28, 0.35), (tiles[1], rng.random() * 6.28, 0.25), (tiles[2], rng.random() * 6.28, 0.2),
             (tiles[3], rng.random() * 6.28, 0.12)]
    for y in range(Hd):
        prof = math.sin(math.pi * (y + 0.5) / Hd) ** 1.3
        for x in range(Wd):
            n = 0.55
            for k, ph, amp in comps:
                n += amp * math.sin(2 * math.pi * (k * x / Wd + y / Hd * 0.5) + ph)
            n = max(0.0, min(1.0, n))
            d = peak * prof * n
            b = BAYER4[y % 4][x % 4]
            if b < d * 16:
                px[x, y] = c("grey_l")
            if b < d * 16 * 0.45 - 0.01:
                px[x, y] = c("white")
    return img


if __name__ == "__main__":
    save_asset(G, "vendor_corn_dong", [vendor(f) for f in range(3)], fps=6, anchor=(19, 26),
               notes="Corn/sweet-potato vendor on low stool facing LEFT toward charcoal brazier (coals glow 3 frames). Place at VENDOR_X, VENDOR_BASE_Y; spawn smoke_puff above brazier (~x-13,y-20 from anchor). Dong.")
    save_asset(G, "smoke_puff", [smoke(f) for f in range(6)], fps=6, anchor=(8, 21), loop=False,
               notes="Smoke rising + dissipating 6 frames, dithered; anchor = emission point (bottom). Spawn every ~1s from the brazier. Dong.")
    save_asset(G, "breath_puff", [breath(f) for f in range(4)], fps=6, anchor=(1, 3), loop=False,
               notes="Tiny breath puff, 4 frames; anchor = mouth. Drifts right (flip for left-facing). Dong.")
