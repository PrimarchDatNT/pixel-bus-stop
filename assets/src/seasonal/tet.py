from common import *
import random


def blossom(img, x, y, rng, big=True):
    """peach blossom: tiny 5-petal flower."""
    cols = ["bloom_l", "bloom_l", "salmon", "bloom_hl"]
    col = rng.choice(cols)
    put(img, x, y, "bloom_d" if col != "bloom_hl" else "salmon")
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        put(img, x + dx, y + dy, col)
    if big and rng.random() < 0.5:
        put(img, x - 1, y - 1, "bloom_hl")


def pot(img, x0, y0, w, h, base, mid, light, band, rim=True):
    """glazed pot, tapered"""
    for j in range(h):
        t = j / (h - 1)
        inset = int(round(t * 2.2))
        rect(img, x0 + inset, y0 + j, x0 + w - 1 - inset, y0 + j, mid)
        put(img, x0 + inset, y0 + j, light)
        put(img, x0 + inset + 1, y0 + j, light) if j < h - 2 else None
        put(img, x0 + w - 1 - inset, y0 + j, base)
        put(img, x0 + w - 2 - inset, y0 + j, base)
    rect(img, x0 - 1, y0, x0 + w, y0 + 1, mid)       # rim
    rect(img, x0 - 1, y0, x0 + w, y0, light)
    rect(img, x0 + w, y0 + 1, x0 + w, y0 + 1, base)
    rect(img, x0 + 1, y0 + 3, x0 + w - 2, y0 + 3, band)
    for xx in range(x0 + 2, x0 + w - 2, 2):
        put(img, xx, y0 + 5, band) if h > 8 else None


def make_pot_dao():
    W_, H_ = 26, 34
    img = new(W_, H_)
    rng = random.Random(7)
    # pot at bottom (blue glaze, gold band)
    pot(img, 7, 25, 12, 9, "blue_d", "blue", "sky_l", "gold")
    # soil
    rect(img, 8, 24, 17, 25, "brown_k")
    # gnarled trunk
    tr = [(13, 24), (13, 22), (12, 19), (13, 16), (14, 13)]
    for a, b in zip(tr, tr[1:]):
        thick(img, a[0], a[1], b[0], b[1], "brown_k", 2)
    line(img, 13, 24, 13, 22, "brown_d")
    # branches (dark)
    br = [
        [(13, 21), (9, 19), (6, 15), (4, 11)], [(12, 19), (8, 14), (7, 9)],
        [(13, 17), (17, 14), (20, 10), (22, 6)], [(14, 14), (14, 9), (12, 5)],
        [(14, 13), (18, 8), (17, 3)], [(7, 15), (3, 16)], [(19, 11), (23, 12)],
        [(10, 17), (11, 12), (10, 8)],
    ]
    pts = []
    for b in br:
        for a, c2 in zip(b, b[1:]):
            line(img, a[0], a[1], c2[0], c2[1], "brown_k")
        pts += b[1:]
        for p in b:
            put(img, p[0] - 0, p[1], "brown_k")
    # highlight on trunk left side
    line(img, 12, 22, 12, 20, "brown_d")
    # blossoms clustered on branch tips + along branches
    for (x, y) in pts:
        for _ in range(2):
            blossom(img, x + rng.randint(-2, 2), y + rng.randint(-2, 2), rng)
    for _ in range(9):
        blossom(img, rng.randint(3, 22), rng.randint(2, 17), rng, big=False)
    # bud dots (darker pink) + a few fallen petals on soil
    for _ in range(6):
        put(img, rng.randint(2, 23), rng.randint(2, 20), "mauve")
    put(img, 9, 25, "bloom_l"); put(img, 16, 25, "bloom_hl")
    return img


def make_pot_quat():
    W_, H_ = 22, 28
    img = new(W_, H_)
    rng = random.Random(11)
    pot(img, 6, 20, 10, 8, "rust", "clay", "sand", "gold")
    rect(img, 6, 19, 15, 20, "brown_k")
    # trunk
    rect(img, 10, 16, 11, 20, "brown_d")
    # canopy: overlapping rounded leaf blobs, light from upper-left
    blobs = [(11, 9, 8), (6, 11, 5), (16, 11, 5), (11, 5, 5), (8, 15, 4), (14, 15, 4)]
    for cx, cy, r in blobs:
        ellipse(img, cx - r, cy - r + 1, cx + r, cy + r - 1, "green_d")
    for cx, cy, r in blobs:
        ellipse(img, cx - r + 1, cy - r + 1, cx + r - 2, cy + r - 2, "green")
    for cx, cy, r in blobs:
        ellipse(img, cx - r + 1, cy - r + 1, cx + 1, cy + 1, "green")
    for cx, cy in ((8, 5), (6, 9), (11, 3), (4, 12), (10, 8)):
        put(img, cx, cy, "green_l"); put(img, cx + 1, cy, "green_l")
    # leaf speckle dark
    for _ in range(14):
        x, y = rng.randint(3, 18), rng.randint(2, 17)
        if img.getpixel((x, y))[3]:
            put(img, x, y, "green_d")
    # kumquats: orange 2x2 with highlight
    fr = [(6, 7), (10, 4), (14, 7), (8, 11), (13, 11), (17, 12), (4, 12), (11, 14), (7, 15), (15, 15), (10, 8)]
    for x, y in fr:
        rect(img, x, y, x + 1, y + 1, "orange")
        put(img, x, y, "yellow")
        put(img, x + 1, y + 1, "rust")
    # li xi tags: red with yellow dot, on strings
    for x, y in ((3, 8), (17, 8), (12, 15)):
        line(img, x, y - 2, x, y, "gold")
        rect(img, x, y + 1, x + 1, y + 3, "red")
        put(img, x, y + 1, "yellow")
    return img


def make_banner():
    Wb, Hb = 100, 16
    base = new(Wb, Hb)
    txt = "CHÚC MỪNG NĂM MỚI"
    tw, _ = text_size(txt)
    # body rows 2..14 (13 tall), x 4..95
    bx0, bx1 = 5, 94
    by0, by1 = 2, 14
    rect(base, bx0, by0, bx1, by1, "red")
    rect(base, bx0, by1 - 1, bx1, by1, "red_d")
    rect(base, bx0, by0, bx1, by0, "rust" if False else "red_hot")
    rect(base, bx0, by0, bx1, by0, "red")
    # gold border: 1px frame inset
    rect(base, bx0 + 1, by0 + 1, bx1 - 1, by0 + 1, "gold")
    rect(base, bx0 + 1, by1 - 1, bx1 - 1, by1 - 1, "gold")
    rect(base, bx0 + 1, by0 + 1, bx0 + 1, by1 - 1, "gold")
    rect(base, bx1 - 1, by0 + 1, bx1 - 1, by1 - 1, "gold")
    # corner dots
    for x, y in ((bx0 + 3, by0 + 3), (bx1 - 3, by0 + 3), (bx0 + 3, by1 - 3), (bx1 - 3, by1 - 3)):
        put(base, x, y, "yellow")
    tx = (Wb - tw) // 2
    ty = by0 + 5
    text(base, tx, ty + 1, txt, "red_d")
    text(base, tx, ty, txt, "yellow")
    frames = []
    for f in range(2):
        out = new(Wb, Hb)
        # wave: step the body at word gaps so glyphs are never cut
        words = txt.split(" ")
        bnds = [0]
        for k in range(1, len(words)):
            bnds.append(tx + text_size(" ".join(words[:k]) + " ")[0] - 2)
        bnds.append(Wb)
        offs = [0, 1, 1, 0] if f == 0 else [1, 0, 0, 1]
        for seg in range(4):
            col = base.crop((bnds[seg], 0, bnds[seg + 1], Hb))
            out.paste(col, (bnds[seg], offs[seg]))
        # fix ties after wave: ropes from top corners to the poles
        for x0s, sgn in ((0, 1), (Wb - 1, -1)):
            pass
        # ties: little rope loops at both ends (anchored at top)
        for sx, dx in ((bx0, -1), (bx1, 1)):
            put(out, sx - dx * 0, 1, "sand")
        line(out, 1, 0, bx0 + 1, 3, "sand")
        line(out, Wb - 2, 0, bx1 - 1, 3, "sand")
        put(out, 0, 0, "sand"); put(out, Wb - 1, 0, "sand")
        # knots
        rect(out, bx0 - 1, 3, bx0, 4, "gold"); rect(out, bx1, 3, bx1 + 1, 4, "gold")
        # tassel ends hanging
        for sx in (bx0 - 1, bx1 + 1):
            put(out, sx, 5, "red"); put(out, sx, 6, "red_d")
        frames.append(out)
    return frames


def make_flag():
    frames = []
    for f in range(2):
        img = new(8, 10)
        rect(img, 0, 0, 0, 9, "brown_d")
        put(img, 0, 0, "gold")
        for x in range(1, 8):
            off = 0
            if f == 1:
                off = 1 if x in (3, 4, 5) else 0
            else:
                off = 1 if x in (5, 6, 7) else 0
            for y in range(0, 5):
                col = "red" if y < 4 else "red_d"
                put(img, x, y + off, col)
        # star (yellow plus) in flag
        cx = 4
        cy = 2 + (1 if (f == 1) else 0) + (0)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            put(img, cx + dx, cy + dy, "yellow")
        frames.append(img)
    return frames


def make_firecracker():
    img = new(6, 24)
    rect(img, 2, 0, 3, 1, "gold")           # rope tie
    put(img, 2, 0, "yellow")
    line(img, 2, 2, 2, 22, "sand") if False else None
    y = 2
    k = 0
    while y < 21:
        xoff = 0
        # tied rope segment
        put(img, 2, y, "gold"); put(img, 3, y, "gold")
        y += 1
        # cracker body 2x3
        for j in range(4):
            put(img, 1, y + j, "red_hot" if j < 2 else "red")
            put(img, 2, y + j, "red")
            put(img, 3, y + j, "red_d")
            put(img, 4, y + j, "red_d") if False else None
        put(img, 1, y, "salmon")
        put(img, 2, y, "yellow") if k % 2 == 0 else None
        y += 4
        k += 1
    # last big one bottom + sparks
    put(img, 2, 22, "gold"); put(img, 3, 22, "yellow")
    put(img, 1, 23, "gold"); put(img, 4, 23, "gold"); put(img, 2, 23, "orange")
    return img


if __name__ == "__main__":
    save_asset(G, "pot_dao", make_pot_dao(), anchor=(13, 33), notes="Potted peach-blossom tree; bottom-centre = ground contact. Place beside the shelter (e.g. x=148 or x=290, y=FAR_SIDEWALK_Y1). Xuan.")
    save_asset(G, "pot_quat", make_pot_quat(), anchor=(11, 27), notes="Potted kumquat with li xi tags; bottom-centre. Xuan.")
    save_asset(G, "banner_tet", make_banner(), fps=2, anchor=(50, 0), notes="2-frame gentle wave; anchor top-centre (hang across the street / between pole+lamp, y~96). Xuan.")
    save_asset(G, "flag_vn", make_flag(), fps=3, anchor=(0, 9), notes="Vietnamese flag on stick, 2-frame wave; anchor = stick foot (left). Xuan.")
    save_asset(G, "firecracker_deco", make_firecracker(), anchor=(2, 0), notes="Decorative string of firecrackers (dây pháo), anchor top (hanging point). Xuan.")
