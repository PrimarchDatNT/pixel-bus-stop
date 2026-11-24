from common import *


def clump(img, cx, cy, r, d="leaf_d", m="leaf", l="leaf_l", hl="leaf_hl"):
    sp(img, blob_mask([(cx, cy, r)]), d)
    if r >= 2:
        sp(img, blob_mask([(cx - 1, cy - 1, max(1, r - 1))]), m)
    if r >= 3:
        sp(img, blob_mask([(cx - 1, cy - 2, r - 2)]), l)
    put(img, cx - r + 1, cy - r + 1, hl) if r >= 3 else None


def pot(img, x, yb, kind=0, w=5):
    """Potted plant standing with pot bottom at yb, pot left at x."""
    rect(img, x, yb - 3, x + w - 1, yb - 3, "tc_l")
    rect(img, x + 1, yb - 2, x + w - 2, yb, "tc")
    rect(img, x + w - 2, yb - 2, x + w - 2, yb, "tc_d")
    rect(img, x + 1, yb, x + w - 2, yb, "tc_d")
    cx = x + w // 2
    if kind == 0:   # bushy
        clump(img, cx, yb - 7, 3)
        clump(img, cx - 3, yb - 5, 2)
        clump(img, cx + 3, yb - 5, 2)
    elif kind == 1:  # tall palm-like
        for dx, dy in [(-3, -6), (3, -6), (-2, -9), (2, -9), (0, -11)]:
            line(img, cx, yb - 4, cx + dx, yb + dy, "leaf_d")
        for dx, dy in [(-3, -6), (3, -6), (-2, -9), (2, -9), (0, -11)]:
            put(img, cx + dx, yb + dy, "leaf_l")
            put(img, cx + dx // 2, yb + dy // 2 - 1, "leaf")
    else:           # flowering
        clump(img, cx, yb - 6, 3)
        clump(img, cx - 3, yb - 5, 2)
        for dx, dy, cc in [(-1, -9, "bl_l"), (2, -7, "yl_l"), (-4, -6, "bl_hl"), (3, -9, "bl_l")]:
            put(img, cx + dx, yb + dy, cc)


def hang(img, x, y, n=6):
    """Hanging pot from y (string top) with trailing leaves."""
    line(img, x, y, x, y + 2, "wood_d")
    rect(img, x - 2, y + 3, x + 2, y + 3, "tc_l")
    rect(img, x - 1, y + 4, x + 1, y + 5, "tc")
    put(img, x + 1, y + 5, "tc_d")
    sp(img, blob_mask([(x, y + 2, 3, 1)]), "leaf")
    for dx, ln in [(-3, n - 1), (-1, n), (1, n - 2), (3, n - 1)]:
        for k in range(ln):
            put(img, x + dx, y + 4 + k, "leaf_d" if k % 2 else "leaf")
        put(img, x + dx, y + 3 + ln, "leaf_l")
    put(img, x - 2, y + 2, "leaf_l")


def railing(img, x0, x1, ybase, hgt=8):
    """1px iron railing standing on ybase (the y of the slab top - 1)."""
    yt = ybase - hgt
    rect(img, x0, yt, x1, yt, "grey_k")
    rect(img, x0, ybase - 1, x1, ybase - 1, "grey_d")
    for x in range(x0, x1 + 1, 3):
        line(img, x, yt + 1, x, ybase - 2, "grey_d")
    rect(img, x0, yt, x0, ybase - 1, "grey_k")
    rect(img, x1, yt, x1, ybase - 1, "grey_k")
    # a small scroll every 4th bay
    for x in range(x0 + 3, x1 - 3, 12):
        put(img, x + 1, yt + 3, "grey_m")
        put(img, x + 2, yt + 4, "grey_m")


def shutter(img, x0, x1, yt, yb, s):
    rect(img, x0, yt, x1, yb, s)
    for y in range(yt + 1, yb, 3):
        rect(img, x0, y + 1, x1, y + 1, s + "_d")
    rect(img, x0, yt, x0, yb, s + "_l")
    for y in range(yt + 1, yb, 3):
        put(img, x0, y + 1, s)
    rect(img, x1, yt, x1, yb, s + "_d")
    rect(img, x0, yt, x1, yt, s + "_l" if x1 - x0 > 3 else s)
    rect(img, x0, yb, x1, yb, s + "_d")


def window(img, x, yt, yb, w, mode="open", s="sh", curtain=False, wall="wy"):
    """Tall window; frame outer = (x-1..x+w, yt-1..yb+1). s = 'sh' | 'sb'."""
    rect(img, x - 1, yt - 1, x + w, yb + 1, "wood_k")
    rect(img, x, yt, x + w - 1, yb, "glass")
    rect(img, x, yt, x + w - 1, yt + 1, "glass_d")
    if curtain:
        rect(img, x, yt + 2, x + 1, yb, "paper")
        rect(img, x + w - 2, yt + 2, x + w - 1, yb, "paper")
        rect(img, x + 1, yt + 2, x + 1, yb, "grey_hl")
    # panes
    if w >= 11:
        mx = x + w // 2
        rect(img, mx, yt, mx, yb, "wood_d")
    th = yt + (yb - yt) * 2 // 5
    rect(img, x, th, x + w - 1, th, "wood_d")
    # glare strokes, per pane
    panes = [(x, x + w // 2 - 1), (x + w // 2 + 1, x + w - 1)] if w >= 11 else [(x, x + w - 1)]
    for (a, b) in panes:
        if b - a >= 3:
            ya = yb - 3
            line(img, a + 1, ya, a + 4, ya - 3, "white")
            line(img, a + 1, ya - 3, a + 2, ya - 4, "glass_l")
            if yb - th > 14:
                line(img, a + 1, th - 3, a + 3, th - 5, "glass_l")
        else:
            put(img, a, yb - 2, "white"); put(img, a + 1, yb - 3, "white")
    # lintel + sill
    rect(img, x - 2, yt - 2, x + w + 1, yt - 2, wall + "_l")
    rect(img, x - 2, yt - 1, x - 2, yb + 1, wall + "_d") if False else None
    # shutters
    sw = 5
    top, bot = yt - 1, yb + 1
    if mode == "open":
        shutter(img, x - 1 - sw, x - 2, top, bot, s)
        shutter(img, x + w + 1, x + w + sw, top, bot, s)
    elif mode == "open_l":
        shutter(img, x - 1 - sw, x - 2, top, bot, s)
    elif mode == "closed":
        mid = x + w // 2
        shutter(img, x, mid - 1, top + 1, bot - 1, s)
        shutter(img, mid, x + w - 1, top + 1, bot - 1, s)
        rect(img, x - 1, top, x + w, top, "wood_k"); rect(img, x - 1, bot, x + w, bot, "wood_k")
        rect(img, x - 1, top, x - 1, bot, "wood_k"); rect(img, x + w, top, x + w, bot, "wood_k")
    elif mode == "half":  # left leaf closed, right leaf open outwards
        shutter(img, x, x + w // 2 - 1, top + 1, bot - 1, s)
        shutter(img, x + w + 1, x + w + sw, top, bot, s)


def tank(img, x, yb, h=15, w=11):
    """Stainless roof water tank standing on legs; x left, yb = roof y it stands on."""
    rect(img, x + 1, yb - 3, x + 2, yb - 1, "grey_d")
    rect(img, x + w - 3, yb - 3, x + w - 2, yb - 1, "grey_d")
    rect(img, x, yb - 4, x + w - 1, yb - 4, "grey_m")
    top = yb - 4 - h
    rect(img, x, top + 3, x + w - 1, yb - 5, "grey_l")
    rect(img, x + 1, top + 1, x + w - 2, top + 2, "grey_l")
    rect(img, x + 3, top, x + w - 4, top, "grey_l")
    rect(img, x + w - 4, top + 1, x + w - 3, yb - 5, "grey")      # shade side
    rect(img, x + w - 1, top + 3, x + w - 1, yb - 5, "grey")
    rect(img, x + 1, top + 3, x + 2, yb - 5, "grey_hl")
    rect(img, x + 1, top + 3, x + 1, yb - 5, "white")             # highlight
    rect(img, x + 3, top, x + 4, top, "grey_hl")
    put(img, x + 1, top + 1, "grey_hl")
    for yy in (top + h // 3 + 2, top + 2 * h // 3 + 1):             # weld bands
        rect(img, x, yy, x + w - 1, yy, "grey")
    rect(img, x, yb - 5, x + w - 1, yb - 5, "grey_m")
    put(img, x + w // 2, top - 1, "grey_d")                         # cap


def antenna(img, x, yb, h=14, bars=4):
    line(img, x, yb, x, yb - h, "grey_d")
    for i in range(bars):
        yy = yb - h + 2 + i * 3
        ln = 5 - (i % 2) * 2 + (1 if i == 0 else 0)
        rect(img, x - ln, yy, x + ln, yy, "grey_m")
        put(img, x - ln, yy, "grey_l")
    put(img, x, yb - h - 1, "grey_k")
    line(img, x, yb - 4, x - 3, yb, "grey_m")
    line(img, x, yb - 4, x + 3, yb, "grey_m")


def aircon(img, x, y):
    """12x7 split-AC outdoor unit with fan + vent slats, bracket + pipe."""
    rect(img, x, y, x + 11, y + 6, "white")
    rect(img, x, y, x + 11, y, "grey_hl")
    rect(img, x + 11, y, x + 11, y + 6, "grey_l")
    rect(img, x, y + 6, x + 11, y + 6, "grey_l")
    rect(img, x, y, x, y + 6, "grey_hl")
    sp(img, blob_mask([(x + 3, y + 3, 2)]), "grey_l")
    sp(img, blob_mask([(x + 3, y + 3, 1)]), "grey_d")
    put(img, x + 3, y + 3, "grey_k")
    put(img, x + 2, y + 2, "white")
    for k in range(3):
        rect(img, x + 7, y + 1 + k * 2, x + 10, y + 1 + k * 2, "grey")
    rect(img, x + 1, y + 7, x + 3, y + 7, "grey_d")
    rect(img, x + 8, y + 7, x + 10, y + 7, "grey_d")
    line(img, x + 12, y + 3, x + 13, y + 3, "grey_l")
    line(img, x + 13, y + 3, x + 13, y + 12, "grey_l")


def shirt(img, x, y, cl, cd):
    rect(img, x, y, x + 5, y + 1, cl)
    rect(img, x + 1, y + 2, x + 4, y + 5, cl)
    rect(img, x + 4, y + 2, x + 4, y + 5, cd)
    rect(img, x + 5, y + 1, x + 5, y + 1, cd)
    put(img, x + 2, y, cd); put(img, x + 3, y, cd)


def trousers(img, x, y, cl, cd):
    rect(img, x, y, x + 3, y + 1, cl)
    rect(img, x, y + 2, x + 1, y + 6, cl)
    rect(img, x + 3, y + 2, x + 3, y + 6, cd)
    rect(img, x + 2, y + 2, x + 2, y + 2, cd)


def laundry(img, xa, xb, y):
    line(img, xa, y, xb, y, "grey_m")
    put(img, xa, y + 1, "grey_d"); put(img, xb, y + 1, "grey_d")
    pal = [("pb_l", "pb"), ("white", "grey_l"), ("or_l", "or"), ("pk_l", "pk"), ("yl_l", "yl")]
    x = xa + 2
    i = 0
    while x + 6 < xb:
        cl, cd = pal[i % len(pal)]
        if i % 3 == 1:
            trousers(img, x, y + 1, cl, cd); x += 6
        else:
            shirt(img, x, y + 1, cl, cd); x += 8
        i += 1


def sign(img, x0, y0, x1, y1, bg, fg, txt, frame, hl=None):
    rect(img, x0, y0, x1, y1, bg)
    rect(img, x0, y0, x1, y0, hl or bg)
    rect(img, x0, y0, x0, y1, hl or bg)
    rect(img, x0, y1, x1, y1, frame)
    rect(img, x1, y0, x1, y1, frame)
    rect(img, x0, y0, x1, y0, hl or bg)
    w, _ = text_size(txt)
    text(img, (x0 + x1 + 1 - w) // 2, y0 + 4, txt, fg)
