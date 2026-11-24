from common import *
import math, random

W, H, OX, OY = 50, 36, 15, 6


def ik(h, f, l1=7.0, l2=7.0):
    dx, dy = f[0] - h[0], f[1] - h[1]
    d = min(math.hypot(dx, dy), l1 + l2 - 0.2)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    hh = math.sqrt(max(0, l1 * l1 - a * a))
    ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
    return (round(h[0] + a * ux + hh * uy), round(h[1] + a * uy - hh * ux))   # knee forward (+x)


def thick(im, a, b, col, col2=None):
    line(im, a[0], a[1], b[0], b[1], col)
    line(im, a[0] + 1, a[1], b[0] + 1, b[1], col2 or col)


def bundles(im, kind, t):
    rnd = random.Random(11)
    # three stacked bundles behind the seat: sand wrap bottom, flowers top
    spots = [(-8, 5, 11, 13), (-1, 3, 9, 16), (-4, 0, 8, 7)]
    for (x, y, w, h) in spots[:2]:
        pass
    # wraps
    rect(im, -7 + OX, 14 + OY, 3 + OX, 18 + OY, "sand"); rect(im, -7 + OX, 18 + OY, 3 + OX, 18 + OY, "ochre")
    rect(im, -4 + OX, 9 + OY, 6 + OX, 14 + OY, "green"); rect(im, -4 + OX, 14 + OY, 6 + OX, 14 + OY, "green_d")
    for gx in range(-6, 4, 3):
        line(im, gx + OX, 13 + OY, gx + 1 + OX, 17 + OY, "green_d")
    if kind == "daisy":
        pts = [(-6, 10), (-3, 8), (0, 6), (3, 8), (-8, 13), (-5, 12), (-2, 11), (1, 10), (4, 12), (-4, 5), (-1, 3), (2, 4), (5, 6), (-7, 8)]
        for (x, y) in pts:
            X, Y = x + OX, y + OY
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                put(im, X + dx, Y + dy, "white")
            put(im, X, Y, "yellow")
        for (x, y) in [(-5, 7), (0, 9), (3, 11), (-8, 10), (6, 9)]:
            put(im, x + OX, y + OY, "green_l")
    else:
        for a in [(-2, 14, -4, 2), (1, 14, 4, 4), (-5, 14, -8, 8), (2, 13, 7, 9)]:
            line(im, a[0] + OX, a[1] + OY, a[2] + OX, a[3] + OY, "brown_d")
        for i, (cx, cy, r) in enumerate([(-4, 3, 4), (4, 4, 4), (-8, 8, 3), (7, 9, 3), (0, 8, 4), (-5, 11, 3)]):
            blossoms_(im, cx + OX, cy + OY, r, 20 + i)


def blossoms_(im, cx, cy, r, seed):
    rnd = random.Random(seed)
    cols = ("bloom_l", "salmon", "bloom_hl", "bloom", "bloom_l", "salmon")
    pts = []
    for _ in range(10 + r * 3):
        a = rnd.random() * 6.28; d = rnd.random() ** 0.6
        pts.append((int(cx + math.cos(a) * r * d), int(cy + math.sin(a) * r * d)))
    for x, y in pts: put(im, x + 1, y + 1, "bloom_d")
    for i, (x, y) in enumerate(pts):
        put(im, x, y, cols[(i + x) % 6])
        if i % 3 == 0: put(im, x + 1, y, cols[(i + x) % 6])


def build(kind, phase):
    bike = new(W, H)
    per = new(W, H)
    def P(x, y): return (x + OX, y + OY)
    fw, rw = P(26, 23), P(8, 23)
    for cx, cy in (rw, fw):                       # wheels: thin tyre, hub, alternating spokes
        for dy in range(-7, 8):
            for dx in range(-7, 8):
                if 5.0 < math.hypot(dx, dy) <= 6.45:
                    put(bike, cx + dx, cy + dy, "ink")
        sp = ([(3, 0), (-3, 0), (0, 3), (0, -3), (2, 0), (-2, 0), (0, 2), (0, -2)] if phase % 2 == 0 else
              [(2, 2), (-2, -2), (2, -2), (-2, 2), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        for dx, dy in sp:
            put(bike, cx + dx, cy + dy, "grey")
        put(bike, cx, cy, "grey_l"); put(bike, cx - 1, cy - 1, "white") if phase % 2 == 0 else put(bike, cx + 1, cy - 1, "white")
    # frame
    bb = P(16, 23); seat = P(12, 15); head = P(23, 13); sttop = P(12, 16)
    col = "green_d"
    for a, b in [(bb, seat), (sttop, head), (bb, head), (bb, rw), (seat, rw), (head, fw), (P(23, 11), P(23, 14))]:
        line(bike, a[0], a[1], b[0], b[1], col)
    line(bike, *P(23, 11), *P(26, 10), "ink")                     # handlebar
    rect(bike, *P(9, 14), *P(14, 14), "ink"); put(bike, *P(10, 13), "brown_d")   # saddle
    rect(bike, *P(1, 14), *P(3, 14), "ink") if False else None
    rect(bike, *P(3, 15), *P(11, 15), "slate_d")                  # rear rack
    line(bike, *P(4, 16), *P(7, 22), "slate_d")
    # chainring + pedal cranks
    ang = [0, 90, 180, 270][phase % 4] * math.pi / 180
    cr = 3
    pf = (round(bb[0] + cr * math.cos(ang)), round(bb[1] + cr * math.sin(ang)))
    pb = (round(bb[0] - cr * math.cos(ang)), round(bb[1] - cr * math.sin(ang)))
    line(bike, bb[0], bb[1], pf[0], pf[1], "slate"); line(bike, bb[0], bb[1], pb[0], pb[1], "slate")
    # ---- person layer
    bundles(per, kind, phase)
    hip = P(12, 14)
    far_foot = (pb[0], pb[1]); near_foot = (pf[0], pf[1])
    # far leg (darker)
    kn = ik(hip, far_foot)
    thick(per, hip, kn, "navy"); thick(per, kn, far_foot, "navy")
    rect(per, far_foot[0] - 1, far_foot[1], far_foot[0] + 2, far_foot[1], "ink")
    # torso (upright, leaning a touch forward)
    shirt = {"daisy": ("grey_l", "slate", "slate_d"), "peach": ("salmon", "mauve", "plum")}[kind if kind != "daisy" else "daisy"] if kind in ("daisy", "peach") else None
    hi, mn, sh = shirt
    poly(per, [P(12, 9), P(17, 8), P(18, 9), P(17, 14), P(11, 14), P(10, 12)], mn)
    line(per, *P(11, 9), *P(10, 12), hi); line(per, *P(12, 9), *P(16, 8), hi)
    line(per, *P(17, 10), *P(17, 14), sh); line(per, *P(11, 14), *P(17, 14), sh)
    if kind == "daisy":
        rect(per, *P(14, 8), *P(18, 9), "red"); put(per, *P(12, 9), "red"); put(per, *P(11, 10), "red_d"); put(per, *P(10, 11), "red_d")  # scarf
    # arm to handlebar
    sh_pt = P(15, 10)
    thick(per, sh_pt, P(22, 11), mn, sh); put(per, *P(24, 11), "skin3"); put(per, *P(23, 11), "skin3")
    # near leg
    kn2 = ik(hip, near_foot)
    thick(per, hip, kn2, "slate"); thick(per, kn2, near_foot, "slate")
    rect(per, near_foot[0] - 1, near_foot[1], near_foot[0] + 2, near_foot[1], "ink")
    put(per, kn2[0], kn2[1], "grey")
    # head: face + nón lá
    rect(per, *P(15, 5), *P(18, 8), "skin2"); put(per, *P(18, 7), "skin3"); put(per, *P(17, 6), "brown_k")
    rect(per, *P(14, 9), *P(15, 9), "skin3")
    poly(per, [P(15, 0), P(22, 5), P(9, 5)], "ochre")
    poly(per, [P(15, 1), P(10, 5), P(9, 5)], "sand") if False else None
    line(per, *P(15, 1), *P(9, 5), "sand"); line(per, *P(15, 2), *P(11, 5), "sand")
    line(per, *P(17, 3), *P(22, 5), "clay"); rect(per, *P(18, 5), *P(22, 5), "clay"); rect(per, *P(9, 5), *P(21, 5), "clay") if False else None
    line(per, *P(9, 5), *P(21, 5), "clay") if False else None
    line(per, *P(15, 5), *P(16, 9), "brown_d") if False else None
    outl(per, "ink")
    im = new(W, H)
    im.alpha_composite(bike)
    im.alpha_composite(per)
    # re-draw wheel front spokes over cargo? no. done
    return im


if __name__ == "__main__":
    for kind, name in [("daisy", "bike_daisy_dong"), ("peach", "bike_peach_xuan")]:
        for f in "RL":
            fr = [build(kind, i) for i in range(4)]
            if f == "L": fr = [flip(x) for x in fr]
            ax = OX + 17 if f == "R" else W - 1 - (OX + 17)
            save_asset(G, f"{name}_{f}", fr, fps=8, anchor=(ax, H - 1),
                       notes="Bicycle flower vendor, nón lá; 4-frame pedal loop @8fps; cargo extends %d px behind bike. Facing %s." % (OX, "right" if f == "R" else "left"))
