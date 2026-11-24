import sys, pathlib, random; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *; from tools.layout import *; from tools.mockbg import mock_scene, place, save_mock

BY = 32                 # scene y of image top
BH = 130
def LY(y): return y - BY
GF_TOP = 88             # local y of ground floor top (scene 120)
VIS_BOT = 125           # last visible local row (sidewalk covers from 126)
R = random.Random(11)

# paint ramps: hl, base, shade, deep   (cooler/desaturated shadows -> atmospheric depth)
PAINT = {
    "ochre": ("sand", "ochre", "stone_l", "stone"),
    "sand":  ("white", "sand", "grey_l", "grey"),
    "mint":  ("grey_l", "mint", "grey", "slate"),
    "grey":  ("white", "grey_l", "grey", "slate"),
    "salmon": ("sand", "skin1", "skin3", "mauve"),
    "yellow": ("white", "ochre", "skin2", "stone"),
    "blue":  ("grey_l", "grey", "slate", "slate_d"),
}
WINDOWS = []   # (x,y,w,h) glass rects for night
SHOPS = []     # (x,y,w,h) shop opening interior
SIGNS = []     # (x,y,w,h)
BALCONIES = [] # (x0,x1,rail_y,slab_y)

def marks_rows(s):
    t = new(80, 24); text(t, 2, 12, s, "white")
    ys = [y for y in range(24) for x in range(80) if t.getpixel((x, y))[3]]
    return 12 - min(ys), max(ys) - 12 - 4   # above caps, below caps (beyond 5 rows)

def sign(img, cx, y, s, bg, fg, border=None, w=None):
    tw = text_size(s)[0]
    up, dn = marks_rows(s)
    up = max(up - 1, 0)
    h = up + 5 + max(dn, 0) + 4
    w = w or tw + 5
    x = cx - w // 2
    rect(img, x, y, x + w - 1, y + h - 1, bg)
    rect(img, x, y + h - 1, x + w - 1, y + h - 1, border or "slate_d")   # lower edge shade
    rect(img, x, y, x + w - 1, y, border or "grey_l") if border != "none" else None
    text(img, x + (w - tw) // 2 + 0, y + 2 + up + 1, s, fg)
    SIGNS.append((x, y, w, h, s, bg, fg, x + (w - tw) // 2, y + 2 + up + 1))
    return h

def window(img, x, y, w, h, P, shutter=True, curtain=None, lit=True):
    hl, base, sh, deep = PAINT[P]
    rect(img, x - 1, y - 1, x + w, y + h, hl if P != "grey" else "white")
    rect(img, x - 1, y + h, x + w, y + h, sh)       # sill shade
    rect(img, x, y, x + w - 1, y + h - 1, "slate_d")
    # sky reflection diagonal top-left
    for i in range(min(w, h) // 2 + 1):
        put(img, x + i, y + (h // 3) - i + 1 if False else y + i, "slate")
    rect(img, x, y, x + 1, y, "slate") 
    put(img, x, y + 1, "slate")
    if w >= 6: put(img, x + w // 2, y, "slate_d"); line(img, x + w // 2, y, x + w // 2, y + h - 1, "navy")  # mullion
    if curtain:
        rect(img, x + w - 3, y, x + w - 1, y + h // 2, curtain)
    # shadow under sill / grime
    for i in range(w): 
        if R.random() < .5: put(img, x + i, y + h + 1, sh)
    if shutter:
        sw = max(2, w // 2)
        for side in (-1, 1):
            sx = x - 1 - sw if side < 0 else x + w + 1
            for yy in range(y - 1, y + h + 1):
                col = "green" if (yy - y) % 2 == 0 else "green_d"
                rect(img, sx, yy, sx + sw - 1, yy, col)
            rect(img, sx, y - 1, sx, y + h, "green_d") if side < 0 else rect(img, sx + sw - 1, y - 1, sx + sw - 1, y + h, "green_d")
            put(img, sx + (1 if side < 0 else sw - 2), y - 1, "mint")
    WINDOWS.append((x, y, w, h))

def ac_unit(img, x, y, drip=True):
    rect(img, x, y, x + 6, y + 3, "white")
    rect(img, x, y + 3, x + 6, y + 3, "grey_l")
    rect(img, x + 1, y + 1, x + 4, y + 2, "grey_l"); 
    for i in range(1, 5): put(img, x + i, y + 2, "grey")
    put(img, x + 6, y, "grey_l"); put(img, x + 6, y + 1, "grey_l")
    rect(img, x, y + 4, x + 6, y + 4, "slate")
    if drip:
        for k in range(R.randrange(3, 7)): put(img, x + 2, y + 5 + k, "grey" if k % 2 else "slate")

def potted(img, x, y, kind=0):
    """pot at (x,y)=bottom-left of 3px pot, plant above."""
    rect(img, x, y - 1, x + 2, y, "clay"); put(img, x + 2, y, "brown_d"); put(img, x, y, "rust") if False else None
    if kind == 0:
        for dx, dy, col in [(1, -2, "green"), (0, -3, "green_l"), (2, -3, "green"), (1, -4, "green_l"), (1, -3, "green_d")]: put(img, x + dx, y + dy, col)
    elif kind == 1:
        for dx, dy, col in [(1, -2, "green_d"), (0, -3, "green"), (2, -3, "green_d"), (1, -3, "green_l"), (0, -4, "green_l"), (2, -4, "green"), (1, -5, "green")]: put(img, x + dx, y + dy, col)
    else:
        for dx, dy, col in [(1, -2, "green"), (1, -3, "green_l"), (0, -4, "green"), (2, -4, "green_l"), (1, -4, "green_d")]: put(img, x + dx, y + dy, col)
        put(img, x + 1, y - 5, "gold")  # a flower

def balcony(img, x0, x1, y0, y1, P, plants=(0, 1), laundry=False, door=True):
    hl, base, sh, deep = PAINT[P]
    # slab
    rect(img, x0 - 1, y1 - 1, x1 + 1, y1 - 1, hl)
    rect(img, x0 - 1, y1, x1 + 1, y1, deep if False else sh)
    # door behind
    if door:
        dw = min(x1 - x0 - 5, 10)
        dx = (x0 + x1) // 2 - dw // 2 - 1
        rect(img, dx, y0 + 3, dx + dw, y1 - 7, "slate_d")
        rect(img, dx, y0 + 3, dx + 1, y0 + 3, "slate"); put(img, dx, y0 + 4, "slate")
        line(img, dx + dw // 2, y0 + 3, dx + dw // 2, y1 - 7, "navy")
        WINDOWS.append((dx, y0 + 3, dw + 1, y1 - 7 - (y0 + 3) + 1))
        rect(img, dx - 1, y0 + 2, dx + dw + 1, y0 + 2, hl)
        # lintel shadow
        for i in range(dw + 1): put(img, dx + i, y0 + 3 + 0, "slate_d") if False else None
    # rail
    ry = y1 - 6
    BALCONIES.append((x0, x1, ry, y1))
    rect(img, x0, ry, x1, ry, "slate_d")
    for x in range(x0, x1 + 1, 2): line(img, x, ry + 1, x, y1 - 2, "slate")
    rect(img, x0, y1 - 2, x1, y1 - 2, "slate_d")
    # plants
    px_ = x0 + 2
    for k, kind in enumerate(plants):
        potted(img, px_ + k * 8, ry - 0 if False else y1 - 2, kind)
    if laundry:
        lx = x1 - 14
        line(img, lx, y0 + 5, lx + 12, y0 + 5, "slate")
        for i, col in enumerate(["white", "sky", "salmon", "white"]):
            rect(img, lx + 1 + i * 3, y0 + 6, lx + 2 + i * 3, y0 + 9, col)

def tank(img, x, y, kind="h"):
    """stainless water tank. (x,y)=top-left"""
    if kind == "h":
        rect(img, x + 1, y, x + 12, y + 5, "grey_l")
        rect(img, x + 1, y, x + 12, y, "white"); rect(img, x + 2, y + 1, x + 8, y + 1, "white")
        rect(img, x + 1, y + 4, x + 12, y + 5, "grey")
        put(img, x, y + 1, "grey_l"); put(img, x, y + 2, "grey_l"); put(img, x, y + 3, "grey"); put(img, x + 13, y + 2, "grey"); put(img, x + 13, y + 3, "slate"); put(img, x + 13, y + 1, "grey")
        put(img, x + 1, y, "grey_l"); put(img, x + 12, y, "grey_l")
        line(img, x + 6, y + 1, x + 6, y + 5, "grey"); line(img, x + 10, y + 1, x + 10, y + 5, "slate")
        rect(img, x + 2, y + 6, x + 3, y + 8, "slate"); rect(img, x + 10, y + 6, x + 11, y + 8, "slate")
    else:  # vertical
        rect(img, x + 1, y + 1, x + 8, y + 12, "grey_l")
        rect(img, x + 2, y, x + 7, y, "grey_l"); put(img, x + 3, y, "white"); put(img, x + 4, y, "white")
        rect(img, x + 1, y + 1, x + 2, y + 11, "white")
        rect(img, x + 7, y + 1, x + 8, y + 12, "grey")
        rect(img, x + 8, y + 6, x + 8, y + 12, "slate")
        line(img, x + 1, y + 4, x + 8, y + 4, "grey"); line(img, x + 1, y + 9, x + 8, y + 9, "grey")
        put(img, x + 1, y + 4, "grey_l"); put(img, x + 1, y + 9, "grey_l")
        rect(img, x + 2, y + 13, x + 3, y + 15, "slate"); rect(img, x + 6, y + 13, x + 7, y + 15, "slate")

def antenna(img, x, y, n=4):
    line(img, x, y, x, y + 12, "slate_d")
    for i in range(n):
        yy = y + 1 + i * 2
        w = 4 - (i // 2)
        line(img, x - w, yy, x + w, yy, "slate" if i % 2 else "slate_d")
    put(img, x, y - 1, "slate_d")
    line(img, x, y + 12, x + 3, y + 14, "slate_d") if False else None

def roof(img, x0, x1, top, P, kind):
    hl, base, sh, deep = PAINT[P]
    if kind == "tin":
        # small sloped tin roof sitting on the parapet
        for i in range(5):
            line(img, x0 + 3 + i, top - 1 - i, x1 - 3 - i, top - 1 - i, "slate" if i % 2 == 0 else "grey")
        line(img, x0 + 3, top - 1, x0 + 3 + 4, top - 5, "grey_l")
        rect(img, x0 + 3, top, x1 - 3, top, "slate_d")
    elif kind == "tile":
        for i in range(6):
            line(img, x0 + 1 + i * 2, top - 1 - i, x1 - 1 - i * 2, top - 1 - i, "brown_d" if i % 2 else "clay")
        for i in range(6):
            put(img, x0 + 1 + i * 2, top - 1 - i, "sand")
        rect(img, x0, top, x1, top, "brown_d")
    elif kind == "tum":
        # rooftop room with small window
        rx0, rx1 = x0 + 6, x0 + (x1 - x0) // 2 + 4
        rect(img, rx0, top - 12, rx1, top - 1, base)
        rect(img, rx0, top - 12, rx0, top - 1, hl); rect(img, rx1, top - 12, rx1, top - 1, sh)
        rect(img, rx0 - 1, top - 13, rx1 + 1, top - 13, "slate"); rect(img, rx0 - 1, top - 14, rx1 + 1, top - 14, "grey")
        rect(img, rx0 + 3, top - 9, rx0 + 6, top - 5, "slate_d"); put(img, rx0 + 3, top - 9, "slate")
        WINDOWS.append((rx0 + 3, top - 9, 4, 5))

def house(img, d):
    x0, w, topS, P = d["x"], d["w"], d["top"], d["paint"]
    x1 = x0 + w - 1
    top = LY(topS)
    hl, base, sh, deep = PAINT[P]
    # wall
    rect(img, x0, top, x1, VIS_BOT + 4, base)
    # party-wall shading: left edge highlight, right 2px shade
    rect(img, x1 - 1, top, x1, VIS_BOT + 4, sh)
    rect(img, x1, top, x1, VIS_BOT + 4, deep)
    rect(img, x0, top, x0, VIS_BOT + 4, hl)
    # parapet band
    rect(img, x0, top, x1, top, hl); rect(img, x0, top + 1, x1, top + 2, base)
    rect(img, x0, top + 3, x1, top + 3, sh)
    dither(img, x0, top + 4, x1 - 2, top + 5, base, sh, .35)
    roof(img, x0, x1, top, P, d.get("roof", "flat"))
    # floors
    n = len(d["floors"])
    fy0 = top + 6
    fh = (GF_TOP - fy0) // n
    for i, kind in enumerate(d["floors"]):
        y0 = fy0 + i * fh
        y1 = y0 + fh - 1
        # slab line
        if kind != "bal":
            rect(img, x0 + 1, y1, x1 - 2, y1, sh); rect(img, x0 + 1, y1 - 1, x1 - 2, y1 - 1, hl)
        cx = x0 + (w - 3) // 2
        if kind == "win":
            ww = 7; wh = min(11, fh - 9)
            window(img, cx - ww - 3, y1 - wh - 4, ww, wh, P, shutter=True)
            if w > 54: window(img, cx + 4, y1 - wh - 4, ww, wh, P, shutter=True, curtain=R.choice([None, "sand", "salmon"]))
            else: window(img, cx + 4, y1 - wh - 4, ww, wh, P, shutter=False)
        elif kind == "win1":
            ww = 9; wh = min(11, fh - 9)
            window(img, cx - 3, y1 - wh - 4, ww, wh, P, shutter=True, curtain=R.choice([None, "sand"]))
        elif kind == "ac":
            ww = 7; wh = min(11, fh - 9)
            window(img, x0 + 6, y1 - wh - 4, ww, wh, P, shutter=False, curtain="sand")
            ac_unit(img, x1 - 12, y1 - 12)
            window(img, x0 + 20, y1 - wh - 4, 6, wh, P, shutter=False) if w > 56 else None
        elif kind == "bal":
            balcony(img, x0 + 4, x1 - 5, y0, y1, P, plants=d.get("plants", (0, 1)), laundry=d.get("laundry", False))
    # ground floor
    gf(img, d, x0, x1, P)
    # roof gear
    for item in d.get("gear", []):
        k, gx = item[0], x0 + item[1]
        if k == "tank_h": tank(img, gx, top - 9 - (item[2] if len(item) > 2 else 0), "h")
        if k == "tank_v": tank(img, gx, top - 16, "v")
        if k == "ant": antenna(img, gx, top - 14)
        if k == "ac": ac_unit(img, gx, top - 5, drip=False)
    # drain pipe on the party wall
    if d.get("pipe", True):
        px_ = x1 - 3
        line(img, px_, top + 7, px_, GF_TOP - 2, "grey_l")
        for yy in range(top + 9, GF_TOP - 2, 9): put(img, px_, yy, "slate"); put(img, px_ + 1, yy, "slate")
    # grime streaks
    for _ in range(w // 6):
        gx = R.randrange(x0 + 2, x1 - 3); gy = R.randrange(top + 8, GF_TOP - 8)
        for k in range(R.randrange(3, 8)):
            if R.random() < .7: put(img, gx, gy + k, sh)

def gf(img, d, x0, x1, P):
    hl, base, sh, deep = PAINT[P]
    kind = d["shop"]
    top = GF_TOP
    # shopfront band (slightly darker base)
    rect(img, x0 + 1, top, x1 - 2, top + 1, sh)
    rect(img, x0 + 1, top - 1, x1 - 2, top - 1, hl)
    sgn = d.get("sign")
    sx0 = x0 + 8 if d.get("door", True) else x0 + 3
    ox0, ox1 = sx0, x1 - 5
    sh_h = 0
    if sgn:
        s, bg, fg = sgn
        sh_h = sign(img, (ox0 + ox1) // 2, top + 3, s, bg, fg, w=min(ox1 - ox0 - 1, text_size(s)[0] + 7))
    oy0 = top + 3 + sh_h + 2
    oy1 = VIS_BOT
    # opening
    rect(img, ox0 - 1, oy0 - 1, ox1 + 1, oy1, sh)
    rect(img, ox0, oy0, ox1, oy1, "navy")
    interior(img, d["shop"], ox0, oy0, ox1, oy1)
    SHOPS.append((ox0, oy0 + d.get("shutter", 10), ox1 - ox0 + 1, oy1 - oy0 + 1 - d.get("shutter", 10)))
    # roll-up shutter (cua cuon)
    drop = d.get("shutter", 10)
    sc1, sc2 = d.get("shcol", ("grey_l", "grey"))
    for y in range(oy0, min(oy1 + 1, oy0 + drop)):
        rect(img, ox0, y, ox1, y, sc1 if (y - oy0) % 2 == 0 else sc2)
    if drop:
        rect(img, ox0, oy0 + drop - 1, ox1, oy0 + drop - 1, "slate")
        rect(img, ox0 + (ox1 - ox0) // 2 - 1, oy0 + drop, ox0 + (ox1 - ox0) // 2 + 1, oy0 + drop, "slate_d")  # handle
        # shutter box above
        rect(img, ox0 - 1, oy0 - 1, ox1 + 1, oy0 - 1, "slate")
        for x in range(ox0, ox1 + 1):
            put(img, x, oy0, "white") if (x - ox0) % 5 == 1 and sc1 == "grey_l" else None
    if d.get("phone"):
        text(img, ox0 + 4, oy0 + 12, d["phone"], "slate")
    # side door of the house
    if d.get("door", True):
        dx0 = x0 + 2
        rect(img, dx0, oy0 + 1, dx0 + 4, oy1, "brown_d")
        rect(img, dx0, oy0 + 1, dx0 + 4, oy0 + 1, "brown_k")
        rect(img, dx0 + 1, oy0 + 3, dx0 + 3, oy1, "brown_d") 
        line(img, dx0 + 2, oy0 + 3, dx0 + 2, oy1, "brown_k")
        put(img, dx0 + 3, oy0 + 12, "gold")
        rect(img, dx0 - 1, oy0, dx0 + 5, oy0, hl)
        # house number plate
        rect(img, dx0 + 1, oy0 - 4, dx0 + 3, oy0 - 3, "blue_d"); put(img, dx0 + 2, oy0 - 4, "white")
    # curb-side items: plants in front of the shopfront wall base
    for px_, k in d.get("pots", []): potted(img, x0 + px_, VIS_BOT, k)
    # hanging awning/dust stains under shop
    for x in range(ox0, ox1 + 1):
        if R.random() < .4: put(img, x, oy1 - 0, "slate_d")

def interior(img, kind, x0, y0, x1, y1):
    w = x1 - x0 + 1
    rect(img, x0, y0 + (y1 - y0) * 2 // 3, x1, y1, "slate_d")  # floor/lower darker lit
    dither(img, x0, y0, x1, y0 + 8, "navy", "teal_k", .25)
    if kind == "tap":   # sundries: shelves with coloured goods, hanging snack strings
        for sy in (y0 + 8, y0 + 13, y0 + 18):
            rect(img, x0 + 1, sy, x1 - 1, sy, "brown_d")
            for x in range(x0 + 2, x1 - 1, 2):
                put(img, x, sy - 1, R.choice(["red_d", "gold", "mint", "blue_d", "sand", "plum", "orange"]))
                if R.random() < .6: put(img, x, sy - 2, R.choice(["red_d", "gold", "mint", "sand"]))
        for x in range(x0 + 2, x1 - 1, 3):
            line(img, x, y0, x, y0 + 3, "slate"); rect(img, x, y0 + 4, x, y0 + 5, R.choice(["red", "gold", "mint", "sky"]))
        rect(img, x0, y1 - 3, x1, y1, "brown_d"); rect(img, x0, y1 - 3, x1, y1 - 3, "brown_k") if False else None
        rect(img, x0 + 2, y1 - 5, x0 + 5, y1 - 4, "sand")
    elif kind == "pho":
        rect(img, x0 + 1, y0 + 8, x1 - 1, y0 + 9, "slate")  # counter back
        ellipse(img, x0 + 3, y1 - 10, x0 + 9, y1 - 6, "grey"); rect(img, x0 + 3, y1 - 8, x0 + 9, y1 - 5, "grey"); rect(img, x0 + 3, y1 - 9, x0 + 9, y1 - 9, "white")
        # stools + tables
        for sx in (x0 + 13, x0 + 22):
            rect(img, sx, y1 - 6, sx + 5, y1 - 6, "grey"); rect(img, sx + 1, y1 - 5, sx + 1, y1, "slate"); rect(img, sx + 4, y1 - 5, sx + 4, y1, "slate")
            rect(img, sx - 1, y1 - 12, sx + 2, y1 - 9, "red_d"); rect(img, sx - 1, y1 - 7, sx + 2, y1 - 7, "red_d") if False else None
        for x in range(x0 + 2, x1 - 2, 3): put(img, x, y0 + 4, "gold")
    elif kind == "hair":
        rect(img, x0 + 1, y0 + 2, x1 - 1, y0 + 14, "slate")      # mirror wall
        rect(img, x0 + 1, y0 + 2, x1 - 1, y0 + 2, "grey"); 
        for k in range(0, w - 4, 8):
            rect(img, x0 + 3 + k, y0 + 4, x0 + 8 + k, y0 + 12, "slate_d"); line(img, x0 + 3 + k, y0 + 4, x0 + 6 + k, y0 + 4, "grey_l"); put(img, x0 + 3 + k, y0 + 5, "grey_l")
            # chair
            rect(img, x0 + 4 + k, y1 - 7, x0 + 7 + k, y1 - 6, "red_d"); rect(img, x0 + 4 + k, y1 - 11, x0 + 4 + k, y1 - 7, "red_d"); rect(img, x0 + 5 + k, y1 - 5, x0 + 6 + k, y1, "slate")
    elif kind == "sua":  # bike repair: tires, tools on wall
        for k, x in enumerate(range(x0 + 3, x1 - 4, 7)):
            ellipse(img, x, y0 + 4, x + 5, y0 + 9, "ink"); ellipse(img, x + 2, y0 + 6, x + 3, y0 + 7, "navy")
        line(img, x0 + 2, y0 + 13, x1 - 2, y0 + 13, "brown_d")
        for x in range(x0 + 3, x1 - 2, 3): put(img, x, y0 + 14, "grey"); put(img, x, y0 + 15, "slate")
        # stacked tyres floor
        for k in range(3):
            rect(img, x1 - 10, y1 - 2 - k * 3, x1 - 3, y1 - k * 3, "ink"); rect(img, x1 - 9, y1 - 1 - k * 3, x1 - 4, y1 - 1 - k * 3, "navy")
        # bicycle wheel
        ellipse(img, x0 + 4, y1 - 9, x0 + 12, y1 - 1, "slate"); ellipse(img, x0 + 5, y1 - 8, x0 + 11, y1 - 2, "navy")
    elif kind == "cafe":
        for x in range(x0 + 3, x1 - 3, 7):  # pendant lamps
            line(img, x, y0, x, y0 + 4, "slate"); rect(img, x - 1, y0 + 5, x + 1, y0 + 5, "gold"); put(img, x, y0 + 6, "glow")
        rect(img, x0 + 1, y0 + 10, x1 - 1, y0 + 11, "brown_d")
        for sx in range(x0 + 4, x1 - 4, 10):
            rect(img, sx, y1 - 8, sx + 4, y1 - 8, "sand"); rect(img, sx + 2, y1 - 7, sx + 2, y1, "slate")
            rect(img, sx - 2, y1 - 6, sx - 1, y1, "slate_d"); rect(img, sx + 6, y1 - 6, sx + 7, y1, "slate_d")
        for x in range(x0 + 2, x1 - 2, 4): put(img, x, y0 + 9, "mint")
    elif kind == "bread":
        rect(img, x0 + 1, y0 + 6, x1 - 1, y0 + 7, "brown_d")
        for x in range(x0 + 2, x1 - 2, 3): rect(img, x, y0 + 4, x + 1, y0 + 5, "clay"); put(img, x, y0 + 4, "sand")
        rect(img, x0 + 2, y1 - 8, x1 - 2, y1 - 6, "slate"); rect(img, x0 + 2, y1 - 8, x1 - 2, y1 - 8, "grey_l")
        rect(img, x0 + 2, y1 - 5, x1 - 2, y1, "slate_d")
    elif kind == "tv":  # electronics
        for k, x in enumerate(range(x0 + 2, x1 - 5, 9)):
            rect(img, x, y0 + 4 + (k % 2) * 4, x + 6, y0 + 9 + (k % 2) * 4, "ink"); rect(img, x + 1, y0 + 5 + (k % 2) * 4, x + 5, y0 + 8 + (k % 2) * 4, "blue_d"); put(img, x + 1, y0 + 5 + (k % 2) * 4, "sky")
        rect(img, x0 + 1, y1 - 5, x1 - 1, y1, "slate_d")
    else:  # closed/generic home: dark, a bike inside
        rect(img, x0 + 2, y1 - 6, x0 + 7, y1 - 5, "slate")
        ellipse(img, x0 + 2, y1 - 5, x0 + 6, y1 - 1, "ink")

def seam(img, x):
    for y in range(0, BH):
        p = img.getpixel((x, y))
        if p[3]: put(img, x, y, "slate_d" if y > 30 else "slate")

HOUSES = [
 dict(x=0, w=52, top=62, paint="ochre", roof="tin", floors=["bal", "win"], shop="tap", sign=("TẠP HÓA", "ochre", "red_d"), shutter=9,
      gear=[("ant", 38)], laundry=True, plants=(1, 0)),
 dict(x=52, w=58, top=40, paint="mint", roof="tum", floors=["win1", "ac", "bal"], shop="pho", sign=("PHỞ BÒ", "red_d", "yellow"), shutter=7,
      gear=[("tank_v", 38), ("ant", 48)], plants=(0, 2, 1), shcol=("grey_l", "grey")),
 dict(x=110, w=56, top=84, paint="salmon", roof="flat", floors=["win"], shop="hair", sign=("CẮT TÓC", "blue_d", "white"), shutter=11,
      gear=[("tank_h", 18)], pots=[(8, 0)]),
 dict(x=166, w=62, top=52, paint="sand", roof="tile", floors=["bal", "win1", "ac"], shop="sua", sign=("SỬA XE", "yellow", "blue_d"), shutter=6,
      gear=[("ant", 6)], plants=(2, 1)),
 dict(x=228, w=60, top=90, paint="grey", roof="flat", floors=["ac", "win1"], shop="cafe", sign=("CÀ PHÊ", "sand", "brown_d"), shutter=6,
      gear=[("tank_h", 30)], door=False),
 dict(x=288, w=56, top=46, paint="yellow", roof="tin", floors=["bal", "win", "bal"], shop="bread", sign=("BÁNH MÌ", "red_d", "sand"), shutter=12,
      gear=[("tank_v", 6), ("ant", 40)], laundry=True, plants=(1, 2, 0), shcol=("sand", "grey_l")),
 dict(x=344, w=64, top=72, paint="blue", roof="flat", floors=["ac", "win"], shop="tv", sign=("ĐIỆN MÁY", "blue_d", "yellow"), shutter=8,
      gear=[("tank_h", 8), ("ant", 44)]),
 dict(x=408, w=72, top=58, paint="ochre", roof="tum", floors=["win", "bal", "win1"], shop="home", sign=("GIẶT LÀ", "mint", "slate_d"), shutter=24, phone="SỬA KHÓA",
      gear=[("tank_v", 46), ("ant", 60)], plants=(0, 1, 2, 1), shcol=("grey", "slate"), laundry=True),
]

def build():
    global WINDOWS, SHOPS, SIGNS
    WINDOWS.clear(); SHOPS.clear(); SIGNS.clear(); BALCONIES.clear()
    img = new(W, BH)
    # draw back-to-front: far-ish taller ones first doesn't matter; houses abut
    for d in HOUSES: house(img, d)
    for d in HOUSES[1:]: seam(img, d["x"])
    return img

LIT = {"red_d": "red", "blue_d": "blue", "yellow": "glow", "sand": "glow", "ochre": "yellow", "mint": "glow",
       "white": "white", "slate_d": "brown_d", "brown_d": "red_d"}

def build_lights():
    L = new(W, BH)
    rr = random.Random(5)
    for (x, y, w, h) in WINDOWS:
        if rr.random() < .55:
            warm = rr.choice(["gold", "yellow", "glow"])
            rect(L, x, y, x + w - 1, y + h - 1, warm)
            rect(L, x, y + h - 2, x + w - 1, y + h - 1, "gold" if warm != "gold" else "orange")
            r = rr.random()
            if w >= 4 and r < .4: rect(L, x + w - 2, y, x + w - 1, y + h // 2, "sand")          # curtain edge
            elif r < .65 and h >= 6:                                                            # hanging lamp
                put(L, x + w // 2, y, "brown_d"); put(L, x + w // 2, y + 1, "brown_d"); put(L, x + w // 2, y + 2, "white")
            elif r < .85 and w >= 4 and h >= 7:                                                 # silhouette
                sx = x + w // 2 - 1
                rect(L, sx, y + h - 6, sx + 1, y + h - 5, "brown_k"); rect(L, sx - 1, y + h - 4, sx + 2, y + h - 1, "brown_k")
    for i, (x, y, w, h) in enumerate(SHOPS):
        if h <= 2: continue
        rect(L, x, y, x + w - 1, y + h - 1, "gold")
        rect(L, x, y, x + w - 1, y + 1, "yellow")
        rect(L, x, y + h - 4, x + w - 1, y + h - 1, "ochre")
        # shelves / stools silhouettes
        for sy in (y + 5, y + 10):
            if sy < y + h - 5: rect(L, x + 1, sy, x + w - 2, sy, "brown_d")
        for sx in range(x + 6, x + w - 8, 20):
            rect(L, sx, y + h - 8, sx + 3, y + h - 7, "brown_d"); rect(L, sx + 1, y + h - 6, sx + 1, y + h - 5, "brown_k"); rect(L, sx + 2, y + h - 6, sx + 2, y + h - 5, "brown_k")
        if i % 2 == 0 and h >= 9:   # a person
            px_ = x + w // 2 + (i % 3) * 2
            rect(L, px_, y + h - 11, px_ + 1, y + h - 10, "brown_k"); rect(L, px_ - 1, y + h - 9, px_ + 2, y + h - 1, "brown_k")
    for (x, y, w, h, s, bg, fg, tx, ty) in SIGNS:
        rect(L, x, y, x + w - 1, y + h - 1, LIT.get(bg, bg))
        text(L, tx, ty, s, LIT.get(fg, fg) if fg not in ("white", "blue_d", "slate_d", "brown_d") else {"white": "white", "blue_d": "blue_d", "slate_d": "slate_d", "brown_d": "brown_d"}[fg])
    return L

if __name__ == "__main__":
    img = build()
    save_asset("env", "buildings", img, anchor=(0, 0), notes="480x130, top-left at (0,32); bottom row 129 = scene y 161 (BUILDING_BASE_Y).")
    lt = build_lights()
    save_asset("env", "buildings_lights", lt, anchor=(0, 0), notes="Night overlay, same size/pos as buildings (0,32).")
    bg = new(W, H); rect(bg, 0, 0, W - 1, H - 1, "sky_l"); bg.alpha_composite(img, (0, BY)); save_mock(bg, "env", "buildings_check", 3)
    bg2 = new(W, H); rect(bg2, 0, 0, W - 1, H - 1, "navy"); bg2.alpha_composite(img, (0, BY)); bg2.alpha_composite(lt, (0, BY)); save_mock(bg2, "env", "buildings_night_check", 3)
