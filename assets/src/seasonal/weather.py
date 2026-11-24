from common import *


# ------------------------------------------------------------- rain tiles (seamless, wrap in x and y)
def rain_tile(frames, count, lens, slope, cols, seed):
    T = 120
    out = []
    for f in range(frames):
        rng = random.Random(seed * 100 + f)
        img = new(T, T)
        px = img.load()
        # stratified positions so streaks spread evenly (no big gaps / clumps)
        cells = int(math.ceil(math.sqrt(count)))
        cs = T / cells
        pts = []
        for gy in range(cells):
            for gx in range(cells):
                pts.append((int(gx * cs + rng.random() * cs), int(gy * cs + rng.random() * cs)))
        rng.shuffle(pts)
        for (x, y) in pts[:count]:
            L = rng.randint(*lens)
            col = rng.choice(cols)
            for k in range(L):
                xx = (x + int(k * slope)) % T
                yy = (y + k) % T
                # fade tail: first third uses darker/fainter colour
                cc = col if k > L // 3 else cols[-1]
                px[xx, yy] = c(cc)
        out.append(img)
    return out


# ------------------------------------------------------------- splash / ripple
def splash(f):
    img = new(13, 8)
    cx, by = 6, 7
    col = ["white", "white", "grey_l", "grey_l", "grey"][f]
    # ring
    rx = [1, 2, 3, 5, 6][f]
    if f <= 3:
        line(img, cx - rx, by, cx + rx, by, col)
    else:
        for x in range(cx - rx, cx + rx + 1):
            if (x + f) % 2 == 0:
                put(img, x, by, col)
    # droplets
    drops = {
        0: [(0, 4)],
        1: [(-1, 4), (1, 5), (0, 3)],
        2: [(-3, 3), (3, 3), (-1, 2), (1, 2)],
        3: [(-4, 4), (4, 4), (-2, 3), (2, 3)],
        4: [(-5, 6), (5, 6)],
    }[f]
    for dx, dy in drops:
        put(img, cx + dx, by - dy, "white" if f < 3 else "sky_l")
    if f == 1:
        put(img, cx, by - 1, "white"); put(img, cx, by - 2, "grey_l")
    return img


def ripple(f):
    img = new(18, 7)
    cx, cy = 9, 3
    rx, ry = [(2, 1), (4, 1.4), (6.5, 2.2), (8.5, 3)][f]
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=c("white" if f < 2 else "grey_l"))
    if f >= 2:
        # break the ring up with a dither mask
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                if px[x, y][3] and BAYER4[y % 4][x % 4] >= (14 if f == 2 else 8):
                    px[x, y] = CLEAR
    if f == 3:
        d.ellipse([cx - 4, cy - 1.2, cx + 4, cy + 1.2], outline=c("white"))
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                if px[x, y] == c("white") and (x + y) % 2:
                    px[x, y] = CLEAR
    return img


# ------------------------------------------------------------- petals / leaves / glint
def sprite_frames(shapes, legend):
    return [grid(s, legend) for s in shapes]


def petals():
    shapes = [["#a.", "###", ".#."], ["a#.", ".##", ".a."], ["...", "a##", ".#a"], [".#.", "##a", "#.."]]
    A = sprite_frames(shapes, dict(a="bloom", **{"#": "bloom_l"}))
    B = sprite_frames(shapes, dict(a="bloom_d", **{"#": "bloom"}))
    return A + B


def leaf(light, mid, dark):
    shapes = [
        ["..a..", ".abb.", "abbbb", ".bbd.", "..d.."],
        ["a....", "abb..", ".bbb.", "..bbd", "...dd"],
        [".....", "..a..", ".abd.", "..d..", "....."],
        ["....a", "..bba", ".bbb.", "dbb..", "dd..."],
    ]
    return sprite_frames(shapes, dict(a=light, b=mid, d=dark))


def sun(f):
    S = 19
    img = new(S, S)
    cx = cy = 9
    long_, short_ = ("yellow", "gold")
    # rays: frame 0 -> cardinals long, diagonals short; frame 1 -> swapped
    for k in range(8):
        a = k * math.pi / 4
        cardinal = (k % 2 == 0)
        ln = 8 if (cardinal == (f == 0)) else 7
        r0 = 6.5
        for r in range(int(r0 * 2), int(ln * 2 + 1)):
            rr = r / 2
            x = round(cx + rr * math.cos(a)); y = round(cy + rr * math.sin(a))
            put(img, x, y, "yellow" if rr < ln - 1 else "gold")
            if cardinal == (f == 0) and rr < ln - 1.5:
                px_ = round(cx + rr * math.cos(a) - math.sin(a)) if abs(math.cos(a)) < .1 else x
                py_ = round(cy + rr * math.sin(a) + math.cos(a)) if abs(math.sin(a)) < .1 else y
                put(img, px_, py_, "gold")
    ellipse(img, cx - 5, cy - 5, cx + 5, cy + 5, "orange")
    ellipse(img, cx - 5, cy - 5, cx + 4, cy + 4, "gold")
    ellipse(img, cx - 5, cy - 5, cx + 3, cy + 3, "yellow")
    ellipse(img, cx - 4, cy - 4, cx - 1, cy - 1, "glow")
    return img


def rainbow():
    Wd, Hd = 220, 70
    img = new(Wd, Hd)
    px = img.load()
    bands = ["red", "orange", "yellow", "green_l", "blue", "plum"]
    a, b = 110.0, 69.0
    cx, cy = 110, 69.5
    wd = 0.20  # radial thickness fraction
    for y in range(Hd):
        for x in range(Wd):
            r = math.hypot((x + 0.5 - cx) / a, (y + 0.5 - cy) / b)
            u = (1.0 - r) / wd * 6.0   # 0 at outer edge .. 6 at inner
            thr = (BAYER4[y % 4][x % 4] + 0.5) / 16 - 0.5   # -0.5..0.5
            ui = u + thr * 1.6
            k = math.floor(ui)
            if 0 <= k < 6:
                px[x, y] = c(bands[k])
    return img


def glint(f):
    img = new(7, 7)
    cx = cy = 3
    if f == 0:
        put(img, cx, cy, "white")
    elif f == 1:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            put(img, cx + dx, cy + dy, "white" if (dx, dy) == (0, 0) else "sky_l")
        put(img, cx, cy, "white")
    else:
        for r in (1, 2, 3):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                put(img, cx + dx * r, cy + dy * r, "white" if r == 1 else "sky_l")
        put(img, cx, cy, "white")
        for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
            put(img, cx + dx, cy + dy, "cyan")
    return img


if __name__ == "__main__":
    save_asset(G, "rain_drizzle_tile", rain_tile(3, 70, (3, 5), 0.15, ["grey_l", "sky_l", "white"], 1), fps=12, anchor=(0, 0),
               notes="120x120 seamless tile (wraps both axes), 3 frames; compositor tiles + scrolls down. Xuan mua bui / Dong mua phun. Set opacity at render.")
    save_asset(G, "rain_heavy_tile", rain_tile(3, 190, (8, 13), 0.35, ["white", "sky_l", "grey_l"], 2), fps=12, anchor=(0, 0),
               notes="120x120 seamless tile, slanted dense streaks, 3 frames. Ha mua rao.")
    save_asset(G, "splash", [splash(f) for f in range(5)], fps=15, anchor=(6, 7), loop=False,
               notes="Rain splash on ground, 5 frames; anchor = impact point (bottom-centre). Spawn randomly on road/sidewalk.")
    save_asset(G, "ripple", [ripple(f) for f in range(4)], fps=6, anchor=(9, 3), loop=False,
               notes="Puddle ring, 4 frames; anchor = centre. Use on puddles on road.")
    save_asset(G, "petal_bloom", petals(), fps=8, anchor=(1, 1), states={"a": [0, 1, 2, 3], "b": [4, 5, 6, 7]},
               notes="Bougainvillea petal 3x3, tumbling; two shades as states a (bloom_l) / b (bloom). Thu wind.")
    save_asset(G, "leaf_yellow", leaf("glow", "yellow", "gold"), fps=8, anchor=(2, 2), notes="Tumbling bang leaf 5x5, 4 frames. Thu.")
    save_asset(G, "leaf_orange", leaf("gold", "orange", "rust"), fps=8, anchor=(2, 2), notes="Tumbling leaf, orange. Thu.")
    save_asset(G, "leaf_red", leaf("salmon", "red", "red_d"), fps=8, anchor=(2, 2), notes="Tumbling leaf, red (bang red leaves; also Dong sparse). Thu/Dong.")
    save_asset(G, "sun", [sun(0), sun(1)], fps=3, anchor=(9, 9), notes="Sun disc with 2-frame ray shimmer; layer celestial. Ha.")
    save_asset(G, "rainbow", rainbow(), anchor=(110, 69), notes="Dithered elliptical rainbow arc 220x70, hard-alpha dither edges; anchor bottom-centre; compositor can apply opacity ~0.5. Ha after rain.")
    save_asset(G, "glint", [glint(f) for f in range(3)], fps=6, anchor=(3, 3), notes="Sparkle for wet surfaces, 3 frames; sprinkle randomly with offsets. Ha after rain / Xuan.")
