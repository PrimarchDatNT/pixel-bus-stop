"""Park scene (bản 6, 24/11/2026): the two-storey shophouse is replaced by a low one-storey Hanoi kiosk (nhà cấp 4,
tiled roof) and the city/bridge background by a park: an evergreen xà cừ crown behind the roof, a tiered bàng tree on
the right, an open lawn with a gravel path and a few shrubs (no fence, 6b), a park lamp, a pale far tree line and
faint high-rises beyond it.

    .venv/bin/python assets/src_gif/park/park.py
    -> assets/out_gif/env/{park_far, park_lawn, park_xacu, park_bang, park_front, kiosk_cafe, kiosk_taphoa, kiosk_props_cafe,
                           kiosk_props_taphoa}.png

Two shop variants share one shell: "cafe" (green signboard, red-white awning, bar with espresso machine, phin cups,
chalkboard menu, hanging bulbs) and "taphoa" (red signboard, green-white awning, the old grocery shelves + fridge).
Trees are 3 sway frames at 3 fps (like the bougainvillea). Seasons recolour park_xacu / park_bang by layer name.
"""
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "assets/src_gif/env_b"))
from tools.px_gif import *       # noqa: E402,F403
from tools.layout_gif import *   # noqa: E402,F403
import house as old              # noqa: E402  (grocery interior: shelves, goods, fridge, counter)

# ---------------------------------------------------------------------------------------------- geometry (1x)
K_TOP, K_BOT = 92, 113            # ridge cap top .. eave line
SIGN = (196, 116, 274, 136)       # signboard on the wall above the awning
AWN_Y0, AWN_Y1 = 138, 147         # awning rail .. valance tips
OPEN = (156, 148, 293, 185)       # shop opening (interior)
LAMP_X = 322
BANG_X = 366


def kxl(y): return 166 - round((y - K_TOP) * 20 / (K_BOT - K_TOP))
def kxr(y): return 284 + round((y - K_TOP) * 20 / (K_BOT - K_TOP))


def hsh(*a):
    v = 0
    for x in a:
        v = (v * 1103515245 + int(x) * 2654435761 + 12345) & 0xFFFFFFFF
    return ((v >> 8) & 0xFFFF) / 65536


def blob(cx, cy, rx, ry):
    S = set()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / (rx + .5)) ** 2 + ((y - cy) / (ry + .5)) ** 2 <= 1.0:
                S.add((x, y))
    return S


# ---------------------------------------------------------------------------------------------- canopies
def lobe_mask(cx, cy, rx, ry, phase):
    pts = {}
    seed = cx * 7 + cy * 13
    for y in range(int(cy - ry - 4), int(cy + ry + 5)):
        for x in range(int(cx - rx - 4), int(cx + rx + 5)):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            ang = math.atan2(dy, dx)
            bump = 0.10 * math.sin(ang * 7 + seed) + 0.06 * math.sin(ang * 13 + seed * 0.7 + phase) \
                + 0.05 * math.sin(ang * 19 + seed * 1.3)
            r = math.hypot(dx, dy)
            if r <= 1 + bump:
                pts[(x, y)] = (dx, dy, r, 1 + bump)
    return pts


def canopy(im, lobes, tones, seed, n, phase, sizes=(3, 4, 4, 5, 5, 6), split=(0.38, 0.72), y_cut=None):
    """Clump-stamped crown (same construction as the bougainvillea / GIF cherry). tones = [k, d, base, l, hl]."""
    px = im.load()
    rnd = random.Random(seed)
    top = min(cy - ry for cx, cy, rx, ry in lobes); bot = max(cy + ry for cx, cy, rx, ry in lobes)

    def put_c(x, y, col):
        if 0 <= x < W and 0 <= y < H and (y_cut is None or y <= y_cut):
            px[x, y] = c(col)

    for (cx, cy, rx, ry) in lobes:
        for (x, y), (dx, dy, r, rim) in lobe_mask(cx, cy, rx, ry, phase * 0.5).items():
            v = (y - top) / max(1, bot - top)
            tone = tones[2] if v < 0.62 else tones[1]
            if rim - r < 0.12 and dx * 0.55 + dy * 0.85 > 0.3:
                tone = tones[1] if v < 0.62 else tones[0]
            put_c(x, y, tone)
    stamps = []
    while len(stamps) < n:
        cx, cy, rx, ry = lobes[rnd.randrange(len(lobes))]
        a = rnd.random() * 2 * math.pi; rr = math.sqrt(rnd.random())
        x = cx + math.cos(a) * rx * rr; y = cy + math.sin(a) * ry * rr
        r = rnd.choice(sizes) if rr < 0.8 else rnd.choice(sizes[:3])
        stamps.append((y, x, r, rr))
    stamps.sort()
    for (y, x, r, edge) in stamps:
        if edge > 0.72:
            x += round(math.sin(phase + x * 0.13 + y * 0.07) * 1.0)
        v = (y - top) / max(1, bot - top)
        if v < split[0]:
            hi, body, lo = tones[3], tones[2], tones[1]
        elif v < split[1]:
            hi, body, lo = tones[2], tones[2], tones[1]
        else:
            hi, body, lo = tones[2], tones[1], tones[0]
        X, Y = round(x), round(y)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d2 = dx * dx + dy * dy
                if d2 > r * r + (1 if r > 2 else 0):
                    continue
                if d2 >= r * r - 1 and hsh(X + dx, Y + dy, 5) < 0.25:
                    continue
                if dy <= -r * 0.45 and dx <= r * 0.45:
                    tone = hi
                elif dy >= r * 0.5 or (dy >= r * 0.2 and dx >= r * 0.5):
                    tone = lo
                else:
                    tone = body
                if tone == hi and v < 0.3 and dy <= -r * 0.8 and dx <= 0 and hsh(X, Y, dx) < 0.5:
                    tone = tones[4]
                put_c(X + dx, Y + dy, tone)


def limb(im, pts, w0, w1, tones=("trunk_l", "trunk", "trunk_d")):
    px = im.load()
    n = len(pts) - 1
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = max(abs(x1 - x0), abs(y1 - y0)) * 2
        for k in range(int(L) + 1):
            t = k / max(L, 1); g = (i + t) / n
            cx = x0 + (x1 - x0) * t; cy = y0 + (y1 - y0) * t; r = (w0 + (w1 - w0) * g) / 2
            for y in range(int(cy - r - 1), int(cy + r + 2)):
                for x in range(int(cx - r - 1), int(cx + r + 2)):
                    dx = x - cx
                    if dx * dx + (y - cy) ** 2 > (r + .4) ** 2 or not (0 <= x < W and 0 <= y < H):
                        continue
                    px[x, y] = c(tones[0] if dx < -r * .35 else tones[2] if dx > r * .3 else tones[1])


GREEN = ["leaf_k", "leaf_d", "leaf", "leaf_l", "leaf_hl"]


def xacu(k):
    """Big evergreen xà cừ crown behind the kiosk roof (trunk hidden by the kiosk)."""
    im = new(W, H)
    phase = k * 2 * math.pi / 3
    limb(im, [(236, 128), (234, 108), (226, 92), (214, 80)], 9, 4)
    limb(im, [(234, 104), (250, 90), (262, 78)], 5, 3)
    lobes = [(204, 64, 20, 13), (240, 56, 24, 15), (278, 66, 20, 13),
             (180, 80, 20, 14), (218, 74, 26, 15), (258, 72, 26, 15), (296, 86, 16, 13),
             (168, 102, 18, 12), (204, 98, 26, 13), (246, 96, 28, 13), (288, 104, 20, 11)]
    canopy(im, lobes, GREEN, seed=31, n=360, phase=phase, y_cut=118)
    return im


def bang(k):
    """Bàng tree, right side: trunk + three flat tiers on whorled branches (turns red in winter)."""
    im = new(W, H)
    phase = k * 2 * math.pi / 3
    x = BANG_X
    limb(im, [(x, 177), (x + 1, 150), (x - 1, 124), (x, 100), (x + 1, 76)], 7, 3)
    for dx, col in ((-5, "trunk_d"), (-4, "trunk"), (5, "trunk_d"), (4, "trunk_d")):      # root flare on the lawn
        put(im, x + dx, 177, col)
    rect(im, x - 4, 176, x - 4, 176, "trunk_l")
    line(im, x - 8, 178, x + 9, 178, "leaf_d")
    for (y, L) in ((128, 34), (104, 26), (82, 16)):              # whorls: branches flaring out under each tier
        limb(im, [(x, y + 2), (x - L // 2, y - 1), (x - L, y - 4)], 3, 1)
        limb(im, [(x, y + 2), (x + L // 2, y), (x + L, y - 3)], 3, 1)
    tiers = [(74, 18, 9), (98, 30, 10), (122, 42, 11)]           # (cy, half width, half height)
    for i, (cy, hw, hh) in enumerate(tiers):
        lobes = []
        n_l = max(2, hw // 10)
        for j in range(n_l + 1):
            u = j / n_l
            lx = x - hw + 2 * hw * u
            droop = round(4 * abs(u - 0.5) ** 2 * 2)
            lobes.append((round(lx), cy - 2 + droop, 11, hh - 1))
        lobes.append((x, cy - 4, hw * 0.55, hh))
        canopy(im, lobes, GREEN, seed=50 + i, n=70 + hw * 3, phase=phase + i, sizes=(2, 3, 3, 4, 4), split=(0.45, 0.8))
    return im


# ---------------------------------------------------------------------------------------------- far + front
# far high-rises (x0, x1, top, crown): pale, low contrast, window grid = the city_lights grid in compose/gif_frame
TOWERS = [(0, 12, 74, "flat"), (176, 188, 28, "step"), (262, 273, 36, "spire"), (296, 309, 46, "step"),
          (312, 322, 82, "flat"), (352, 363, 46, "spire"), (372, 384, 62, "flat")]


def tower(im, x0, x1, top, crown):
    rect(im, x0, top, x1 - 1, 150, "far_l")
    line(im, x1 - 1, top, x1 - 1, 150, "far")                  # shaded right side
    for yy in range(top + 4, 148, 5):
        for xx in range(x0 + 2, x1 - 3, 4):
            put(im, xx, yy, "far"); put(im, xx + 1, yy, "far")
    if crown == "step":
        rect(im, x0 + 2, top - 3, x1 - 3, top - 1, "far_l"); line(im, x1 - 3, top - 3, x1 - 3, top - 1, "far")
        rect(im, x0 + 4, top - 5, x1 - 5, top - 4, "far_l")
    elif crown == "spire":
        line(im, (x0 + x1) // 2, top - 8, (x0 + x1) // 2, top - 1, "far")
        rect(im, x0 + 3, top - 2, x1 - 4, top - 1, "far_l")
    else:
        line(im, x0, top, x1 - 1, top, "far")


def far():
    """Pale far tree line of the park + faint high-rises beyond it, full width; seen in the gaps."""
    im = new(W, H)
    for t in TOWERS:
        tower(im, *t)
    rnd = random.Random(3)
    S = set()
    x = -6
    while x < W + 8:
        r = rnd.choice([6, 7, 8, 9, 10])
        S |= blob(x, 140 + rnd.randint(-3, 4), r, r - 2)
        x += r + rnd.randint(2, 6)
    for xx in range(W):
        for yy in range(142, 186):
            S.add((xx, yy))
    for (x, y) in S:
        if 0 <= x < W and 0 <= y < H:
            col = "fg"
            if (x, y - 1) not in S or (x, y - 2) not in S:
                col = "fg_l"
            elif (x + 1, y - 1) not in S:
                col = "fg_d"
            put(im, x, y, col)
    for (x, y) in list(S):                                        # soft vertical trunk hints
        if y == 152 and x % 23 == 5:
            line(im, x, 148, x, 151, "fg_d")
    return im


PATH_Y0, PATH_Y1 = 165, 171        # gravel path across the park (the grandma exercises on it)


def lawn(im):
    """Open park lawn behind the sidewalk (no fence): far grass, a gravel path, near grass, stone edging."""
    px = im.load()
    for y in range(150, 186):
        for x in range(W):
            if y < PATH_Y0:
                col = "leaf_hl" if y < 158 or (x // 9 + y) % 7 else "leaf_l"
            elif y <= PATH_Y1:
                col = "wc_l" if y == PATH_Y0 else ("wc" if y < PATH_Y1 else "wc_d")
                if PATH_Y0 < y < PATH_Y1 and hsh(x, y) < 0.08:
                    col = "pave_l"
            else:
                col = "leaf_l" if (x // 6) % 2 == 0 else "leaf"         # mowing stripes
                if y == PATH_Y1 + 1:
                    col = "leaf"
            px[x, y] = c(col)
    for x in range(0, W, 11):                                      # grass tufts on the far lawn
        if hsh(x, 1) < 0.6:
            put(im, x, 153 + int(hsh(x, 2) * 8), "leaf_l"); put(im, x + 1, 152 + int(hsh(x, 2) * 8), "leaf_l")
    rect(im, 0, 184, W - 1, 184, "wc"); rect(im, 0, 185, W - 1, 185, "wc_d")     # low stone edging
    for x in range(8, W, 16):
        put(im, x, 184, "wc_d")


def shrub(im, cx, base, rx, ry, flowers=None):
    S = blob(cx, base - ry, rx, ry)
    for (x, y) in S:
        if y > base or not (0 <= x < W):
            continue
        dx, dy = (x - cx) / (rx + .5), (y - (base - ry)) / (ry + .5)
        s_ = dx * 0.6 + dy * 0.8
        col = "leaf_l" if s_ < -0.35 else ("leaf_d" if s_ > 0.45 else "leaf")
        if s_ < -0.75:
            col = "leaf_hl"
        put(im, x, y, col)
    if flowers:
        for i, (x, y) in enumerate(sorted(S)):
            if y < base - 1 and hsh(x, y, 4) < 0.10:
                put(im, x, y, flowers)


def shrubs(im):
    for (cx, rx, ry, fl) in [(4, 9, 6, "white"), (46, 8, 5, None), (118, 10, 6, "yl_l"), (166, 7, 5, None),
                             (304, 7, 6, "red_l"), (378, 9, 6, "white")]:
        shrub(im, cx, 183, rx, ry, fl)


def lamp(im, x):
    """Classic park lamp: dark green post, three white globes."""
    rect(im, x, 118, x + 1, 176, "sh_d"); line(im, x, 118, x, 176, "sh")
    rect(im, x - 1, 173, x + 2, 177, "sh_d"); line(im, x - 1, 173, x - 1, 177, "sh")
    rect(im, x - 1, 128, x + 2, 129, "sh_d")
    for (gx, gy) in ((x - 5, 113), (x + 3, 113), (x - 1, 108)):
        rect(im, gx + 1, gy, gx + 3, gy, "glass_l")
        rect(im, gx, gy + 1, gx + 4, gy + 3, "white"); put(im, gx + 4, gy + 3, "glass_l"); put(im, gx + 4, gy + 2, "glass_l")
        rect(im, gx + 1, gy + 4, gx + 3, gy + 4, "sh_d")
        put(im, gx + 1, gy + 1, "glow") if False else None
    line(im, x - 3, 117, x + 4, 117, "sh_d")
    put(im, x - 3, 116, "sh_d"); put(im, x + 4, 116, "sh_d")
    put(im, x, 113, "sh_d"); put(im, x + 1, 113, "sh_d")


def lawn_layer():
    im = new(W, H)
    lawn(im)
    return im


def front():
    im = new(W, H)
    lamp(im, LAMP_X)
    shrubs(im)
    return im


# ---------------------------------------------------------------------------------------------- kiosk shell
def roof(im):
    ramp = ["tc_l", "tc", "tc_d"]
    y0 = K_TOP + 3
    for y in range(y0, K_BOT):
        r, k = (y - y0) // 3, (y - y0) % 3
        for x in range(kxl(y), kxr(y) + 1):
            col = ramp[k]
            seam = (x - 140 + 3 * (r % 2)) % 6 == 0
            if seam and k == 0: col = "tc"
            if seam and k == 1: col = "tc_d"
            t = (x - 140 + 3 * (r % 2)) // 6
            if not seam and hsh(r, t) < 0.12: col = {"tc_l": "tc", "tc": "tc_d", "tc_d": "tc_d"}[col]
            elif not seam and hsh(r, t, 9) < 0.10: col = {"tc": "tc_l", "tc_d": "tc", "tc_l": "tc_l"}[col]
            put(im, x, y, col)
    for x in range(kxl(K_TOP) - 1, kxr(K_TOP) + 2):               # ridge cap
        put(im, x, K_TOP, "tc_l"); put(im, x, K_TOP + 1, "tc"); put(im, x, K_TOP + 2, "wood_d")
    for x in range(kxl(K_TOP) - 1, kxr(K_TOP) + 2, 4):
        put(im, x, K_TOP + 1, "tc_d")
    for sx, d in ((kxl(K_TOP) - 2, -1), (kxr(K_TOP) + 2, 1)):     # small upturned ridge ends
        put(im, sx, K_TOP + 1, "tc"); put(im, sx, K_TOP, "tc_d"); put(im, sx + d, K_TOP - 1, "tc_d")
    for y in range(K_TOP + 3, K_BOT + 1):                          # hip ribs
        put(im, kxl(y) - 1, y, "wood_d"); put(im, kxl(y), y, "tc_l")
        put(im, kxr(y) + 1, y, "wood_k"); put(im, kxr(y), y, "tc_d")
    for x in range(kxl(K_BOT) - 1, kxr(K_BOT) + 2):
        put(im, x, K_BOT, "wood_k")
    for x in range(kxl(K_BOT - 1), kxr(K_BOT - 1) + 1):
        put(im, x, K_BOT - 1, "tc_d" if x % 6 else "wood_d")
    rect(im, 146, K_BOT + 1, 303, K_BOT + 1, "wood_d")


def walls(im):
    rect(im, 150, K_BOT + 2, 299, 185, "wy")
    rect(im, 150, K_BOT + 2, 299, K_BOT + 3, "wy_d")
    for x in range(150, 300):
        if (x - 150) % 4 < 2:
            put(im, x, K_BOT + 2, "wood_d")
    rect(im, 150, K_BOT + 2, 151, 185, "wood_l"); line(im, 150, K_BOT + 2, 150, 185, "wood_hl")
    rect(im, 297, K_BOT + 2, 299, 185, "wood_d"); line(im, 299, K_BOT + 2, 299, 185, "wood_k")
    for x, y, n in [(176, 128, 6), (290, 128, 7), (160, 124, 5), (281, 133, 3)]:   # rain stains
        line(im, x, y, x, y + n, "wy_d")
    for x0 in (150, 294):                                          # pier plinths
        rect(im, x0, 180, x0 + 5, 185, "wc_d"); line(im, x0, 180, x0 + 5, 180, "wc")
    for x in (185, 285):
        sconce(im, x, 119)


def sconce(im, x, y):
    """Small wall lantern on a bracket (lit at night)."""
    line(im, x - 2, y + 2, x, y + 2, "ink"); put(im, x - 2, y + 3, "ink")
    rect(im, x - 1, y, x + 3, y, "ink"); put(im, x + 1, y - 1, "ink")
    rect(im, x, y + 1, x + 2, y + 5, "glass_l"); put(im, x, y + 1, "white"); line(im, x + 2, y + 1, x + 2, y + 5, "glass")
    rect(im, x - 1, y + 6, x + 3, y + 6, "ink"); put(im, x + 1, y + 7, "ink")
    rect(im, 156, 185, 293, 185, "wood_k")


MARKS = {"grave": ["##.", ".##"], "acute": [".##", "##."], "circ": [".####.", "##..##"], "dot": ["##", "##"]}


def sign(im, label, marks, board, frame, ink, shade, cap_y):
    """label: plain caps (no diacritics); marks: [(letter index, mark)] drawn as chunky 2-px marks like the GIF signs."""
    x0, y0, x1, y1 = SIGN
    rect(im, x0, y0, x1, y1, "wood_k")
    rect(im, x0 + 1, y0 + 1, x1 - 1, y1 - 1, shade)
    rect(im, x0 + 2, y0 + 2, x1 - 2, y1 - 2, board)
    line(im, x0 + 2, y0 + 2, x1 - 2, y0 + 2, frame)
    w = text_size(label, 2)[0]
    tx = x0 + (x1 - x0 + 1 - w) // 2 + 1
    text(im, tx, cap_y, label, ink, 2)
    for i, m in marks:
        lx = tx + (text_size(label[:i], 2)[0] + 2 if i else 0)       # left edge of letter i
        lw = text_size(label[i], 2)[0]
        rows = MARKS[m]
        mx = lx + (lw - len(rows[0])) // 2
        my = cap_y + 11 if m == "dot" else cap_y - 3
        for j, r in enumerate(rows):
            for k, ch in enumerate(r):
                if ch == "#":
                    put(im, mx + k, my + j, ink)
    for (x, y) in [(x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)]:
        put(im, x, y, frame)
    for x in (x0 + 10, x1 - 10):                                   # hanging brackets
        line(im, x, K_BOT + 2, x, y0 - 1, "ink")


def awning(im, a, b):
    """Striped fabric awning seen front-on: rail, stripes (a/b alternating), scalloped valance."""
    x0, x1 = 154, 296
    shade = {"red_l": "red", "paper": "wc", "sh_l": "sh", "wc_l": "wc", "sb_l": "sb"}
    rect(im, x0 - 1, AWN_Y0, x1 + 1, AWN_Y0, "wood_k")
    for x in range(x0, x1 + 1):
        s = ((x - x0) // 5) % 2
        col = a if s == 0 else b
        for y in range(AWN_Y0 + 1, AWN_Y1 - 2):
            cc = col
            if y == AWN_Y0 + 1:
                cc = shade[col]
            put(im, x, y, cc)
        j = (x - x0) % 5
        put(im, x, AWN_Y1 - 2, shade[col])
        if j in (1, 2, 3):
            put(im, x, AWN_Y1 - 1, shade[col])
        if j == 2:
            put(im, x, AWN_Y1, shade[col])


def bulb(im, x, y):
    line(im, x, OPEN[1], x, y - 1, "ink")
    rect(im, x - 1, y, x + 1, y, "grey_d")
    rect(im, x - 1, y + 1, x + 1, y + 2, "lamp"); put(im, x - 1, y + 1, "glow"); put(im, x, y + 3, "lamp")


# ---------------------------------------------------------------------------------------------- interiors
def cafe_interior(im):
    x0, y0, x1, y1 = OPEN
    rect(im, x0, y0, x1, y1, "wood_d")
    rect(im, x0, y0, x1, y0 + 2, "wood_k")
    # back wall: lower wainscot of warm tiles
    rect(im, x0, 168, x1, 175, "wood")
    for y in (171, 174):
        line(im, x0, y, x1, y, "wood_d")
    line(im, x0, 168, x1, 168, "wood_l")
    # left shelves: coffee jars, kraft bags, stacked cups
    for y in (157, 166):
        rect(im, x0 + 1, y, 224, y, "wood_l"); rect(im, x0 + 1, y + 1, 224, y + 1, "wood_k")
    x = 170
    for kind in ["jar", "jar", "bag", "bag", "cups", "jar", "bag", "cups", "jar", "jar"]:
        if kind == "jar":
            rect(im, x, 151, x + 3, 156, "glass_l"); rect(im, x, 153, x + 3, 156, "trunk_d"); line(im, x + 3, 151, x + 3, 156, "glass")
            rect(im, x, 150, x + 3, 150, "wood_l"); put(im, x, 153, "trunk")
            x += 5
        elif kind == "bag":
            rect(im, x, 151, x + 4, 156, "wc"); line(im, x + 4, 151, x + 4, 156, "wc_d"); rect(im, x + 1, 153, x + 3, 154, "tc")
            put(im, x, 151, "wc_d"); put(im, x + 2, 151, "wc_d")
            x += 6
        else:
            for k in range(3):
                rect(im, x, 155 - k * 2, x + 3, 156 - k * 2, "paper"); put(im, x + 3, 156 - k * 2, "grey_l")
            x += 5
    x = 168
    for i in range(8):                                             # cups + saucers row, a teapot, a plant
        if i == 3:
            rect(im, x, 162, x + 5, 165, "tc"); rect(im, x + 1, 161, x + 4, 161, "tc_l"); put(im, x + 6, 163, "tc"); put(im, x - 1, 162, "tc_d")
            x += 9; continue
        if i == 6:
            rect(im, x, 163, x + 4, 165, "tc_l"); line(im, x + 4, 163, x + 4, 165, "tc")
            for (dx, dy, col) in ((0, -1, "leaf_l"), (2, -2, "leaf"), (4, -1, "leaf_l"), (1, -3, "leaf_hl"), (3, -3, "leaf"), (2, -4, "leaf_l")):
                put(im, x + dx, 162 + dy, col)
            x += 7; continue
        rect(im, x, 163, x + 3, 165, "paper"); line(im, x + 3, 163, x + 3, 165, "grey_l"); rect(im, x - 1, 165, x + 4, 165, "grey_hl")
        put(im, x + 4, 164, "paper")
        x += 7
    # wall clock above the barista
    for (dx, dy) in [(-2, -3), (-1, -3), (0, -3), (1, -3), (2, -3)]:
        pass
    cx, cy = 236, 155
    for (x, y) in blob(cx, cy, 3, 3):
        put(im, x, y, "paper")
    for (x, y) in blob(cx, cy, 3, 3) - blob(cx, cy, 2, 2):
        put(im, x, y, "wood_l")
    put(im, cx, cy - 1, "ink"); put(im, cx, cy, "ink"); put(im, cx + 1, cy, "ink")
    # right: chalkboard menu
    bx0, by0, bx1, by1 = 268, 151, 291, 171
    rect(im, bx0, by0, bx1, by1, "wood_l"); rect(im, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, "grey_k")
    text(im, bx0 + 3, by0 + 3, "MENU", "paper")
    for i, y in enumerate(range(by0 + 10, by1 - 1, 3)):
        w = [12, 9, 13, 10][i % 4]
        line(im, bx0 + 3, y, bx0 + 3 + w, y, "grey_l"); put(im, bx1 - 3, y, "yl_l"); put(im, bx1 - 4, y, "yl_l")
    # glasses on a small shelf
    rect(im, 249, 159, 265, 159, "wood_l"); rect(im, 249, 160, 265, 160, "wood_k")
    for x in range(250, 264, 4):
        rect(im, x, 155, x + 2, 158, "glass"); put(im, x, 155, "glass_l"); put(im, x, 156, "glass_l")
    # counter
    rect(im, x0, 176, x1, 176, "wood_hl"); rect(im, x0, 177, x1, 177, "wood_l")
    rect(im, x0, 178, x1, 184, "wood")
    for x in range(x0 + 1, x1, 4):
        line(im, x, 178, x, 184, "wood_l"); line(im, x + 2, 178, x + 2, 184, "wood_d")
    rect(im, x0, 184, x1, 184, "wood_d")
    # espresso machine
    mx0, my0 = 252, 163
    rect(im, mx0, my0, mx0 + 13, 175, "grey_l"); rect(im, mx0, my0, mx0 + 13, my0, "grey_hl")
    rect(im, mx0 + 12, my0 + 1, mx0 + 13, 175, "grey"); rect(im, mx0, my0 + 1, mx0, 175, "grey_hl")
    rect(im, mx0 + 1, my0 + 3, mx0 + 11, my0 + 3, "grey")
    put(im, mx0 + 10, my0 + 1, "red_l")
    for gx in (mx0 + 3, mx0 + 8):
        rect(im, gx - 1, my0 + 6, gx + 1, my0 + 7, "grey_k"); put(im, gx, my0 + 8, "grey_k")
        rect(im, gx - 1, 173, gx + 1, 175, "paper"); put(im, gx + 1, 175, "grey_l")
    rect(im, mx0 + 2, my0 - 2, mx0 + 4, my0 - 1, "paper"); rect(im, mx0 + 6, my0 - 2, mx0 + 8, my0 - 1, "paper")
    # phin cups on the counter (Vietnamese drip filter)
    for x in (196, 205, 214):
        rect(im, x - 1, 175, x + 4, 175, "grey_hl")
        rect(im, x, 172, x + 3, 174, "paper"); put(im, x + 3, 173, "grey_l"); put(im, x + 4, 173, "paper")
        rect(im, x, 171, x + 3, 171, "grey_l")
        rect(im, x, 168, x + 3, 170, "grey"); line(im, x, 168, x, 170, "grey_l"); rect(im, x, 167, x + 3, 167, "grey_d")
        put(im, x + 1, 166, "grey_d")
    # flower vase + biscuit jar
    rect(im, 223, 171, 225, 175, "glass_l"); line(im, 225, 171, 225, 175, "glass")
    for (dx, dy, col) in ((0, -1, "leaf"), (1, -2, "leaf_l"), (1, -4, "yl_l"), (-1, -4, "white"), (3, -3, "white"), (2, -5, "yl")):
        put(im, 223 + dx, 171 + dy, col)
    rect(im, 181, 171, 186, 175, "glass_l"); rect(im, 182, 172, 185, 175, "or_l"); rect(im, 181, 170, 186, 170, "red")
    line(im, 186, 171, 186, 175, "glass")
    for x, y in ((186, 151), (210, 152), (262, 151)):
        bulb(im, x, y)


def taphoa_interior(im):
    old.shop(im)
    x0, y0, x1, y1 = OPEN
    rect(im, x0, y0, x1, y0 + 2, "wood_k")


# ---------------------------------------------------------------------------------------------- props on the sidewalk
def plant_pot(im, x, y, tall=False):
    """Glazed pot with a leafy plant, standing on the sidewalk (feet row y)."""
    rect(im, x, y - 7, x + 8, y - 7, "teal")
    rect(im, x + 1, y - 6, x + 7, y, "teal"); line(im, x + 1, y - 6, x + 1, y, "pb_l") if False else None
    line(im, x + 6, y - 6, x + 6, y, "teal_d"); line(im, x + 7, y - 6, x + 7, y, "teal_d"); line(im, x + 2, y, x + 7, y, "teal_d")
    put(im, x + 2, y - 5, "wb_l"); put(im, x + 2, y - 4, "wb_l")
    h = 16 if tall else 10
    for (cx, cy, r) in [(x + 4, y - 8 - h + 6, 4), (x + 1, y - 8 - h // 2 + 1, 3), (x + 7, y - 8 - h // 2 + 2, 3),
                        (x + 4, y - 11, 4)]:
        for (px_, py_) in blob(cx, cy, r, r):
            dx, dy = px_ - cx, py_ - cy
            col = "leaf_l" if dx + dy < -r * 0.6 else ("leaf_d" if dx + dy > r * 0.7 else "leaf")
            if dx + dy < -r * 1.1 and hsh(px_, py_) < 0.6:
                col = "leaf_hl"
            put(im, px_, py_, col)
    line(im, x + 4, y - 8, x + 4, y - 9, "leaf_d")


def a_frame(im, x, y):
    """Chalk A-frame sign on the sidewalk."""
    for yy in range(y - 15, y + 1):
        k = (yy - (y - 15)) // 4
        put(im, x + 1 - k // 2, yy, "wood") if False else None
    rect(im, x, y - 15, x + 10, y - 3, "wood_l")
    rect(im, x + 1, y - 14, x + 9, y - 4, "grey_k")
    line(im, x, y - 2, x, y, "wood"); line(im, x + 10, y - 2, x + 10, y, "wood_d")
    line(im, x + 2, y - 12, x + 8, y - 12, "paper")
    line(im, x + 2, y - 9, x + 6, y - 9, "yl_l"); line(im, x + 2, y - 7, x + 7, y - 7, "grey_l"); line(im, x + 2, y - 5, x + 5, y - 5, "grey_l")
    put(im, x + 7, y - 9, "wp_l")


def props(kind):
    im = new(W, H)
    plant_pot(im, 286, STAND_Y - 1, tall=True)
    if kind == "cafe":
        a_frame(im, 174, STAND_Y)
    else:
        for (x, col) in ((174, "red"), (183, "pb")):              # crates of drinks
            rect(im, x, STAND_Y - 6, x + 7, STAND_Y, col); rect(im, x, STAND_Y - 6, x + 7, STAND_Y - 6, {"red": "red_l", "pb": "pb_l"}[col])
            for bx in range(x + 1, x + 7, 2):
                put(im, bx, STAND_Y - 8, "glass"); put(im, bx, STAND_Y - 7, "glass_d")
            line(im, x + 1, STAND_Y - 3, x + 6, STAND_Y - 3, {"red": "red_d", "pb": "pb_d"}[col])
    return im


def kiosk(kind):
    im = new(W, H)
    (cafe_interior if kind == "cafe" else taphoa_interior)(im)
    walls_keep = im.copy()
    walls(im)
    im.alpha_composite(walls_keep.crop((OPEN[0], OPEN[1], OPEN[2] + 1, OPEN[3])), (OPEN[0], OPEN[1]))
    roof(im)
    if kind == "cafe":
        sign(im, "COFFEE", [], "sh_d", "sh", "paper", "wood_k", cap_y=121)       # 6c: client asked for COFFEE
        awning(im, "red_l", "paper")
    else:
        sign(im, "TAP HOA", [(1, "dot"), (5, "acute")], "red", "red_l", "yl_l", "red_d", cap_y=122)
        awning(im, "sh_l", "paper")
    rect(im, OPEN[0], OPEN[1], OPEN[2], OPEN[1], "wood_k")
    return im


if __name__ == "__main__":
    save_asset("env", "park_far", [far()], anchor=(0, 0), notes="park scene: far tree line + hazy towers")
    save_asset("env", "park_xacu", [xacu(k) for k in range(3)], fps=3, anchor=(0, 0), notes="xà cừ crown behind the kiosk")
    save_asset("env", "park_bang", [bang(k) for k in range(3)], fps=3, anchor=(0, 0), notes="bàng tree right side")
    save_asset("env", "park_lawn", [lawn_layer()], anchor=(0, 0), notes="open lawn + gravel path + stone edging (6b)")
    save_asset("env", "park_front", [front()], anchor=(0, 0), notes="park lamp + shrubs (6b: fence removed)")
    for kind in ("cafe", "taphoa"):
        save_asset("env", f"kiosk_{kind}", [kiosk(kind)], anchor=(0, 0), notes=f"one-storey kiosk ({kind})")
        save_asset("env", f"kiosk_props_{kind}", [props(kind)], anchor=(0, 0), notes="sidewalk props in front of the kiosk")
    print("ok")
