import math, random
from common import *

# ---------------------------------------------------------------- cau doi (couplets)
def glyph(im, x, y, seed):
    r = random.Random(seed)
    g = [[0] * 4 for _ in range(4)]
    kind = r.randrange(5)
    if kind == 0:   # radical + vertical (like 口 / 木)
        for i in range(4): g[0][i] = 1
        for i in range(4): g[i][r.choice([1, 2])] = 1
        g[3][0] = 1 if r.random() < .5 else 0
    elif kind == 1:  # grid
        for i in range(4): g[0][i] = 1; g[3][i] = 1
        g[1][0] = g[2][0] = g[1][3] = g[2][3] = 1
        g[1][1] = r.randrange(2)
    elif kind == 2:  # cross + dots
        for i in range(4): g[1][i] = 1
        for i in range(4): g[i][2] = 1
        g[3][0] = 1; g[0][0] = r.randrange(2)
    elif kind == 3:  # slanted
        for i in range(4): g[i][3 - i] = 1
        for i in range(4): g[2][i] = 1
        g[0][0] = 1
    else:            # roof + legs
        for i in range(4): g[0][i] = 1
        g[1][1] = g[1][2] = 1
        g[2][0] = g[2][3] = 1; g[3][0] = g[3][3] = 1; g[2][1] = r.randrange(2)
    for j in range(4):
        for i in range(4):
            if g[j][i]:
                P(im, x + i, y + j, "yellow" if (i + j) % 3 else "gold")


def couplet(im, x, y, seed):
    R(im, x, y, x + 5, y, "gold"); P(im, x - 1, y, "ochre"); P(im, x + 6, y, "ochre")
    R(im, x, y + 1, x + 5, y + 27, "red")
    R(im, x, y + 1, x, y + 27, "salmon") if False else None
    R(im, x + 5, y + 1, x + 5, y + 27, "red_d")
    R(im, x, y + 27, x + 5, y + 27, "red_d")
    for i in range(1, 27):
        P(im, x, y + i, "red_hot" if i % 5 == 2 else "red")
    R(im, x, y + 28, x + 5, y + 28, "gold"); P(im, x - 1, y + 28, "ochre"); P(im, x + 6, y + 28, "ochre")
    R(im, x + 2, y + 29, x + 3, y + 29, "red_d")
    for k in range(5):
        glyph(im, x + 1, y + 2 + k * 5, seed * 10 + k)
    R(im, x + 5, y, x + 5, y, "ochre")


def make_cau_doi():
    im = layer()
    couplet(im, 166, 131, 1)
    couplet(im, 269, 131, 2)
    return im


# ---------------------------------------------------------------- red lanterns
LB = [(5, "x"), (7, "x"), (9, "x"), (9, "x"), (9, "x"), (9, "x"), (9, "x"), (7, "x"), (5, "x")]


def lantern(im, cx, y0, dx, tdx):
    """cx centre x; y0 = roof underside row. dx shifts body (swing); tdx shifts tassel."""
    # cord
    P(im, cx, y0, "brown_k"); P(im, cx + dx // 2 if dx else cx, y0 + 1, "brown_k")
    R(im, cx - 2 + dx, y0 + 2, cx + 2 + dx, y0 + 2, "gold"); P(im, cx - 2 + dx, y0 + 2, "yellow"); P(im, cx + 2 + dx, y0 + 2, "ochre")
    top = y0 + 3
    for j, (w, _) in enumerate(LB):
        h = w // 2
        for i in range(-h, h + 1):
            f = (i + h) / max(1, w - 1)
            col = "red"
            if i == -h or (i == -h + 1 and w > 5): col = "salmon" if j in (1, 2, 3, 4) else "red"
            if f > 0.75: col = "red_d"
            if i == h: col = "rust" if j > 3 else "red_d"
            if j >= 7: col = "red_d" if f < 0.6 else "rust"
            if i in (-2, 2) and 1 < j < 7 and w == 9:        # ribs
                col = "red_d" if i == 2 else "red_hot"
            P(im, cx + i + dx, top + j, col)
    P(im, cx - 2 + dx, top + 1, "salmon")
    R(im, cx - 2 + dx, top + 9, cx + 2 + dx, top + 9, "gold"); P(im, cx - 2 + dx, top + 9, "yellow"); P(im, cx + 2 + dx, top + 9, "ochre")
    # tassel
    tx = cx + dx + tdx
    P(im, cx + dx, top + 10, "gold")
    for j in range(5):
        xx = cx + dx + (tdx if j >= 2 else 0)
        P(im, xx, top + 10 + j, "gold" if j % 2 == 0 else "orange")
        if 0 < j < 4:
            P(im, xx - 1, top + 11 + j, "orange"); P(im, xx + 1, top + 11 + j, "gold") if j > 1 else None


def make_lanterns_xuan():
    frames = []
    body = [0, 1, 0]
    tas = [0, -1, 1]
    for f in range(3):
        im = layer()
        for i, cx in enumerate((177, 188, 253, 267)):
            k = (f + i) % 3
            lantern(im, cx, 129, body[k], tas[k])
        frames.append(im)
    return frames


# ---------------------------------------------------------------- Mid-Autumn lantern string
def sag_y(x, x0, period, depth, y0):
    t = ((x - x0) % period) / period
    return y0 + depth * math.sin(math.pi * t)


COLS = [("red", "red_d", "salmon"), ("gold", "orange", "yellow"), ("green_l", "green", "mint"), ("sky", "blue", "sky_l"),
        ("mauve", "plum", "salmon"), ("orange", "rust", "yellow")]


def paper_lantern(im, x, y, cols, lit):
    base, dark, hi = cols
    # 3x4 body w/ little cap
    P(im, x, y, "slate_d")
    R(im, x - 1, y + 1, x + 1, y + 3, base)
    P(im, x + 1, y + 1, dark); P(im, x + 1, y + 2, dark); P(im, x + 1, y + 3, dark); P(im, x, y + 4, dark)
    P(im, x - 1, y + 1, hi)
    if lit:
        P(im, x, y + 2, "glow"); P(im, x, y + 1, hi)
    else:
        P(im, x, y + 2, base)
    P(im, x, y + 5, "gold") if lit else None


def make_lanterns_thu():
    frames = []
    for f in range(2):
        im = layer()
        for (xa, xb) in ((166, 192), (247, 273)):
            period = (xb - xa) / 2.0
            prev = None
            for x in range(xa, xb + 1):
                y = int(round(sag_y(x, xa, period, 4.5, 129)))
                P(im, x, y, "slate_d")
            for k, x in enumerate(range(xa + 3, xb, 4)):
                y = int(round(sag_y(x, xa, period, 4.5, 129)))
                paper_lantern(im, x, y + 1, COLS[(k + (0 if xa < 200 else 3)) % 6], (k + f) % 2 == 0)
        frames.append(im)
    return frames


# ---------------------------------------------------------------- fairy lights (winter)
def bulb(im, x, y, on, col):
    if on:
        P(im, x, y, "white" if col == 0 else {1: "red_hot", 2: "cyan", 3: "yellow"}[col])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            P(im, x + dx, y + dy, "glow" if col == 0 else {1: "salmon", 2: "sky_l", 3: "gold"}[col])
    else:
        P(im, x, y, "ochre" if col == 0 else {1: "red_d", 2: "blue", 3: "orange"}[col])


def catenary(pts, steps_per=40):
    out = []
    for (a, b, sag) in pts:
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for i in range(n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * math.sin(math.pi * t)))
    return out


def make_lights_dong():
    # wire path (static, reproduced each frame)
    segs = []
    # roof edge: hugging the fascia, scallops outside the board span
    segs += [((164, 129), (193, 129), 5), ((193, 130), (246, 130), 1), ((246, 129), (276, 129), 5)]
    # swags through the vine
    segs += [((166, 120), (196, 106), -5), ((196, 106), (226, 114), 4), ((226, 114), (262, 104), 5), ((262, 104), (279, 116), 4)]
    wires = []
    for s in segs:
        pts = catenary([s])
        wires.append(pts)
    frames = []
    for f in range(3):
        im = layer()
        n = 0
        for pts in wires:
            last = None
            for (x, y) in pts:
                P(im, int(round(x)), int(round(y)), "teal_k")
            # bulbs every ~6px along path
            acc = 0.0; px_ = None
            for (x, y) in pts:
                if px_ is not None:
                    acc += math.hypot(x - px_[0], y - px_[1])
                if acc >= 6 or px_ is None:
                    acc = 0.0
                    bx, by = int(round(x)), int(round(y)) + 1
                    col = 0 if n % 4 else (1 + (n // 4) % 3)
                    bulb(im, bx, by, (n + f) % 3 == 0, col)
                    n += 1
                px_ = (x, y)
        frames.append(im)
    return frames


# ---------------------------------------------------------------- P2: night light + wet
def glow_pix(im, x, y, p, col="glow"):
    if p > 0 and BAYER4[y % 4][x % 4] < p * 16:
        P(im, x, y, col)


def make_night_light():
    """Emissive-only: lit tube, lit lightbox poster, lit header board. No halo / pool."""
    import structure
    im = layer()
    # lit lightbox poster (brighter solid colours)
    tmp = layer()
    structure.poster(tmp, 246, 132)
    lit = recolor(tmp, {"sky": "sky_l", "sky_l": "white", "blue": "sky", "blue_d": "blue", "navy": "blue_d",
                        "green_d": "green", "green": "green_l", "teal_k": "green_d", "mint": "white",
                        "rust": "orange", "red_d": "red", "red": "salmon", "brown_k": "brown_d", "brown_d": "rust",
                        "sand": "glow", "gold": "yellow", "yellow": "white"})
    paste(im, lit, 0, 0)
    # lit header board
    bx0, bx1, by0, by1 = 194, 245, 130, 142
    R(im, bx0, by0, bx1, by1, "blue")
    R(im, bx0, by0, bx1, by0, "sky_l"); R(im, bx0, by0, bx0, by1, "sky_l")
    R(im, bx1, by0, bx1, by1, "blue_d"); R(im, bx0, by1, bx1, by1, "blue_d")
    T(im, 196, 134, "TRẠM XE BUÝT", "white")
    # fluorescent tube
    R(im, 190, 131, 240, 131, "white"); R(im, 190, 132, 240, 132, "glow")
    return im


def make_wet():
    im = layer()
    for x in range(161, 279):
        if (x * 5) % 7 < 2:
            P(im, x, 122, "white")
    for x in range(163, 279, 3):
        if (x * 3) % 5 < 2: P(im, x, 123, "sky_l")
    for x in range(164, 279, 9):
        P(im, x, 126, "sky"); P(im, x + 1, 126, "sky_l")
    for x in (172, 183, 201, 220, 236, 258, 269):    # drips under the fascia
        P(im, x, 129, "sky_l"); P(im, x, 130, "white") if x % 2 else None
    for x0 in (190, 202, 214, 226):                    # seat tops / pan lips
        R(im, x0 + 3, 150, x0 + 6, 150, "white"); P(im, x0 + 1, 161, "white"); P(im, x0 + 2, 161, "sky_l")
        P(im, x0 + 7, 162, "sky_l")
    R(im, 190, 165, 232, 165, "sky_l") if False else None
    for x in range(190, 237, 4): P(im, x, 165, "white")
    for x in (191, 211, 231): P(im, x, 172, "sky_l"); P(im, x + 1, 173, "sky_l")
    for (x, y, l) in ((184, 176, 6), (205, 175, 9), (226, 176, 7), (240, 177, 5), (168, 177, 4)):     # puddle glints
        R(im, x, y, x + l - 1, y, "sky_l"); R(im, x + 1, y + 1, x + l - 2, y + 1, "sky")
    for x in (162, 275):
        P(im, x, 135, "white"); P(im, x, 150, "sky_l"); P(im, x, 165, "white")
    return im


if __name__ == "__main__":
    export("decor_cau_doi_xuan", make_cau_doi(), notes="Layer shelter_decor. Two couplets (6x30) hung on inner faces of pillars: left sprite top-left scene (166,131), right (269,131). Single frame.")
    export("decor_lanterns_xuan", make_lanterns_xuan(), fps=3, notes="Layer shelter_decor. 4 red lanterns hung from roof underside y129 at x=177,188,253,267 (centre); 3-frame swing @3fps.")
    export("decor_lanterns_thu", make_lanterns_thu(), fps=2, notes="Layer shelter_decor. Mid-Autumn paper-lantern strings along the roof edge (broken over the header board); 2-frame flicker. fps=2.")
    export("decor_lights_dong", make_lights_dong(), fps=3, notes="Layer shelter_decor. Fairy-light string along roof edge + swags through the bougainvillea; 3-frame blink @3fps.")
    export("shelter_night_light", make_night_light(), notes="Layer shelter_decor (above, at night). Emissive-only (no glow pixels): lit tube y131-132 x190-240, lit lightbox poster, lit header board. Compositor adds bloom.")
    export("shelter_wet", make_wet(), notes="Layer above shelter_front/seats in rain/after rain: wet highlights on roof edge, seats, drips, puddle glints.")
