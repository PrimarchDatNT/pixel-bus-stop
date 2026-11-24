from common import *

N = 6


def star(img, cx, cy, R, flick=0):
    """five-point star lantern (đèn ông sao): yellow frame, red panels, glowing core."""
    def pts(r, rot=-math.pi / 2, inner=None):
        out = []
        ri = inner if inner else r * 0.45
        for k in range(10):
            rr = r if k % 2 == 0 else ri
            a = rot + k * math.pi / 5
            out.append((cx + rr * math.cos(a) + 0.5, cy + rr * math.sin(a) + 0.5))
        return out
    poly(img, [(round(x), round(y)) for x, y in pts(R)], "gold")
    poly(img, [(round(x), round(y)) for x, y in pts(R - 1.3, inner=(R - 1.3) * 0.42)], "red")
    # shade: lower-right darker
    for y in range(cy, cy + R):
        for x in range(cx + 1, cx + R):
            if img.getpixel((x, y)) == c("red"):
                put(img, x, y, "red_d")
    # upper-left panels catch light
    for y in range(cy - R + 2, cy + 1):
        for x in range(cx - R + 2, cx + 1):
            if img.getpixel((x, y)) == c("red"):
                put(img, x, y, "orange")
    # bright glowing core
    rect(img, cx - 2, cy - 2, cx + 1, cy + 1, "yellow")
    rect(img, cx - 1, cy - 1, cx, cy, "glow")
    put(img, cx - 2 + flick * 3, cy - 2, "glow")
    # tip highlights
    put(img, cx, cy - R, "yellow")
    # tassel
    line(img, cx, cy + R, cx, cy + R + 2, "gold")
    put(img, cx, cy + R + 3, "red")


def halo(img, cx, cy, r, col="glow", frame=0):
    """dithered halo, frame-locked. density falls with distance."""
    px = img.load()
    cc = c(col)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if not (0 <= x < img.width and 0 <= y < img.height):
                continue
            d = math.hypot(x - cx, (y - cy) * 1.05)
            if d > r:
                continue
            dens = (1 - d / r) ** 1.6 * 0.6
            if BAYER4[y % 4][x % 4] < dens * 16 and px[x, y][3] == 0:
                px[x, y] = cc


BODY = dict(skin="skin1", skin_d="skin2")


def kid_base(i, canvas, cx, by, shirt, shirt_d, shirt_l, pants, pants_d, hair, style, near_to=None, far_to=None, shoes="brown_k"):
    img = new(*canvas)
    k = KINDS["kid"]
    hip = legs(img, cx, by, i, N, "kid", pants, pants_d, shoes)
    x0, x1, ty = torso(img, cx, hip, "kid", shirt, shirt_d, shirt_l)
    head(img, cx, ty - k["hh"] + 1, "kid", "skin1", "skin2", hair, style)
    hands = arms(img, cx, ty + 1, i, N, "kid", shirt, shirt_d, "skin1", near_to=near_to, far_to=far_to)
    return img, hands, ty


def make_star(i):
    CW, CH = 46, 42
    cx, by = 16, 38
    bobs = [0, 1, 1, 0, 1, 1]
    # hand holding stick in front of the chest (near arm raised)
    hip_y = by - 8 + 1 + (1 if i % 3 == 0 else 0)
    ty = hip_y - 6
    hx, hy = cx + 4, ty + 4
    base, hands, ty = kid_base(i, (CW, CH), cx, by, "yellow", "gold", "glow", "blue_d", "navy", "ink", "short", near_to=(hx, hy))
    base = outline(base, "ink")  # +1 each side
    img = new(CW + 2, CH + 2)
    # lantern (swing 1px)
    sway = [0, 0, 1, 1, 0, -1][i]
    scx, scy = cx + 11 + sway + 1, 9 + (0 if i % 3 else 1) + 1
    img.alpha_composite(base)
    # stick from hand up to the star
    sx, sy = hx + 1, hy + 1
    line(img, sx, sy, scx - sway, scy + 8, "brown_d")
    line(img, sx + 1, sy, scx - sway + 1, scy + 7, "brown_k") if False else None
    star(img, scx, scy, 7, flick=i % 2)
    # hand again over the stick
    put(img, sx, sy, "skin1")
    put(img, sx, sy - 1, "skin2")
    return img


def carp(img, x, y, f):
    """đèn cá chép, head right. canvas 22x13 at (x,y)"""
    t = new(22, 13)
    # tail fan
    poly(t, [(7, 5), (1, 0), (3, 6), (1, 12), (7, 7)], "orange")
    poly(t, [(7, 5), (3, 2), (4, 6), (7, 6)], "gold")
    line(t, 2, 1, 4, 6, "rust")
    line(t, 2, 11, 4, 6, "rust")
    # dorsal fin
    poly(t, [(9, 3), (11, 0), (15, 1), (16, 3)], "gold")
    line(t, 10, 2, 14, 2, "orange")
    # body
    ellipse(t, 6, 2, 20, 11, "red_d")
    ellipse(t, 6, 2, 19, 10, "orange")
    for yy in range(4, 8):
        for xx in range(8, 19):
            if t.getpixel((xx, yy)) == c("orange") and (xx + yy) % 2 == 0:
                put(t, xx, yy, "red")
    # belly (lower, lighter/warmer)
    for yy in range(8, 11):
        for xx in range(8, 19):
            if t.getpixel((xx, yy))[3] and t.getpixel((xx, yy)) != c("red_d"):
                put(t, xx, yy, "gold" if yy == 8 else "yellow")
    # top highlight
    for xx in range(9, 16):
        put(t, xx, 3, "gold")
    # scales (arcs)
    for sx in range(9, 17, 3):
        for sy in (5, 7):
            put(t, sx + (sy % 2), sy, "glow")
            put(t, sx + 1 + (sy % 2), sy + 1 if False else sy, "red_d")
    # head: eye + mouth + whiskers
    rect(t, 17, 5, 18, 6, "white")
    put(t, 18, 6, "ink")
    rect(t, 20, 7, 20, 8, "gold")
    put(t, 21, 8, "yellow"); put(t, 21, 10, "yellow"); put(t, 20, 9, "yellow")
    # gill line
    line(t, 15, 4, 15, 9, "red_d")
    # pectoral fin
    poly(t, [(12, 9), (10, 12), (14, 11)], "orange")
    # tail flutter
    if f % 2:
        put(t, 0, 0, "orange"); put(t, 0, 12, "orange")
    img.alpha_composite(outline_col(t, "brown_k"), (x - 1, y - 1))


def outline_col(img, col):
    return outline(img, col)


def make_carp(i):
    CW, CH = 50, 36
    cx, by = 16, 32
    hip_y = by - 8 + 1 + (1 if i % 3 == 0 else 0)
    ty = hip_y - 6
    hx, hy = cx + 4, ty + 3
    base, hands, ty = kid_base(i, (CW, CH), cx, by, "salmon", "mauve", "bloom_hl", "plum", "bloom_k", "ink", "bob", near_to=(hx, hy))
    base = outline(base, "ink")
    img = new(CW + 2, CH + 2)
    # stick forward-up, then string, then carp hanging in front
    sway = [0, 1, 1, 0, -1, -1][i]
    sx, sy = hx + 1, hy + 1
    tipx, tipy = sx + 5, sy - 8
    cxp, cyp = tipx - 1, tipy + 4 + (1 if i in (1, 4) else 0)
    img.alpha_composite(base)
    line(img, sx, sy, tipx, tipy, "brown_d")
    line(img, tipx, tipy, cxp + 8, cyp + 2, "sand")
    line(img, tipx, tipy, cxp + 16, cyp + 3, "sand")
    carp(img, cxp, cyp, i)
    put(img, sx, sy, "skin1")
    return img


def build(fn):
    frames = [fn(i) for i in range(N)]
    return frames


if __name__ == "__main__":
    fs = build(make_star)
    fl = [flip(f) for f in fs]
    fw = fs[0].width
    save_asset(G, "kid_star_lantern_R", fs, fps=8, anchor=(17, fs[0].height - 3),
               notes="Kid with đèn ông sao, walks RIGHT, dithered glow halo baked into frames (frame-locked). anchor=feet. Thu night; far_walkers at y=WALK_FAR_BASE_Y.")
    save_asset(G, "kid_star_lantern_L", fl, fps=8, anchor=(fw - 1 - 17, fs[0].height - 3), notes="mirror of _R")
    fs = build(make_carp)
    fl = [flip(f) for f in fs]
    fw = fs[0].width
    save_asset(G, "kid_carp_lantern_R", fs, fps=8, anchor=(17, fs[0].height - 3),
               notes="Kid with đèn cá chép, walks RIGHT; anchor=feet. Thu night.")
    save_asset(G, "kid_carp_lantern_L", fl, fps=8, anchor=(fw - 1 - 17, fs[0].height - 3), notes="mirror of _R")
