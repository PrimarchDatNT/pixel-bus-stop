"""Xe đạp hoa v2 (bản 6c, 24/11/2026): a flower vendor in a nón lá riding an old step-through bicycle that is
OVERLOADED with flowers — a round bamboo thúng on the rear rack with a big fan of flowers rising above her hat, and
a front basket with a second bunch. Faces RIGHT (rides left -> right along the road).

One sprite per season, each with the flowers Hanoi vendors actually carry at that time of year:
    bike_flowers_xuan : Tết peach branches (đào)            + red roses in front
    bike_flowers_ha   : lotus buds + open lotus + leaves (sen) + sunflowers in front (also used in the rain)
    bike_flowers_thu  : yellow chrysanthemums (cúc vàng)     + purple thạch thảo in front
    bike_flowers_dong : white daisies (cúc họa mi)           + red roses in front
4 frames @ 8 fps each (crank 0/90/180/270 deg, spokes turning). Anchor = centre-bottom (tyre contact row).

    .venv/bin/python assets/src_gif/park/bike.py [preview.png]
"""
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.px_gif import *  # noqa: E402,F403

BW, BH = 64, 44
GROUND = BH - 1
WR = 7
RW, FW_ = (14, GROUND - WR), (47, GROUND - WR)          # wheel centres
BB = (29, GROUND - 6)                                  # bottom bracket
HIP = (25, 24)
FRAME, FRAME_L = "teal_d", "teal"
SHIRT, SHIRT_D = "wb_l", "wb"
PANTS, PANTS_D = "sb_d", "navy"


def P(im, x, y, col):
    if 0 <= x < BW and 0 <= y < BH:
        put(im, x, y, col)


def thick(im, a, b, col, w=2):
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
        for dx in range(w):
            for dy in range(w):
                P(im, x + dx, y + dy, col)


# ------------------------------------------------------------------------------------------ flower stamps
def rose(im, x, y, l, m, d):
    for dx, dy, c in ((1, 0, l), (0, 1, l), (1, 1, d), (2, 1, m), (1, 2, m), (0, 0, m), (2, 2, d), (2, 0, m), (0, 2, m)):
        P(im, x + dx, y + dy, c)
    P(im, x, y, l)


def daisy(im, x, y):
    for dx, dy, c in ((1, 0, "white"), (0, 1, "white"), (2, 1, "paper"), (1, 2, "paper"), (1, 1, "yl")):
        P(im, x + dx, y + dy, c)


def mum(im, x, y):
    for dx, dy, c in ((0, 0, "yl_l"), (1, 0, "yl_l"), (2, 0, "yl"), (0, 1, "yl_l"), (1, 1, "yl"), (2, 1, "or_l"),
                      (0, 2, "yl"), (1, 2, "or_l"), (2, 2, "or")):
        P(im, x + dx, y + dy, c)


def sunflower(im, x, y):
    ring = [(1, 0), (2, 0), (3, 0), (0, 1), (4, 1), (0, 2), (4, 2), (0, 3), (4, 3), (1, 4), (2, 4), (3, 4)]
    for (dx, dy) in ring:
        P(im, x + dx, y + dy, "yl_l" if dy < 2 or dx == 0 else "yl")
    for dx, dy, c in ((1, 1, "trunk"), (2, 1, "trunk_d"), (3, 1, "trunk_d"), (1, 2, "trunk_d"), (2, 2, "trunk_d"),
                      (3, 2, "wood_k"), (1, 3, "trunk_d"), (2, 3, "wood_k"), (3, 3, "wood_k")):
        P(im, x + dx, y + dy, c)


def lotus_bud(im, x, y):
    rows = [(1, ["pk_l"]), (0, ["pk_l", "pk", "pk"]), (0, ["pk_l", "pk", "pk_d"]), (0, ["pk", "pk", "pk_d"]),
            (0, ["leaf", "leaf_d", "leaf_d"])]
    for j, (x0, cs) in enumerate(rows):
        for i, c in enumerate(cs):
            P(im, x + x0 + i, y + j, c)
    if (x + y) % 3 == 0:
        P(im, x + 1, y, "white")


def lotus_open(im, x, y):
    for dx, dy, c in ((0, 1, "pk_l"), (1, 0, "white"), (2, 1, "yl"), (3, 0, "white"), (4, 1, "pk_l"), (1, 1, "wp_l"),
                      (3, 1, "wp_l"), (0, 2, "pk"), (1, 2, "pk_l"), (2, 2, "yl_d"), (3, 2, "pk_l"), (4, 2, "pk"),
                      (1, 3, "pk"), (2, 3, "pk_d"), (3, 3, "pk")):
        P(im, x + dx, y + dy, c)


def lotus_leaf(im, cx, cy, r):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r - 1, cx + r + 2):
            if ((x - cx) / (r + 1.5)) ** 2 + ((y - cy) / (r + .5)) ** 2 <= 1:
                s = (x - cx) * 0.5 + (y - cy) * 0.9
                P(im, x, y, "leaf_l" if s < -1.5 else ("leaf_d" if s > 1.8 else "leaf"))
    P(im, cx, cy, "leaf_d")


def fan(cx, base, top, w_top, w_base, lean=0.0):
    """Points of a fan-shaped bouquet: narrow at the basket, wide and rounded at the top, leaning back by `lean`."""
    S = set()
    for y in range(top, base + 1):
        v = (y - top) / max(1, base - top)
        w = w_top * (1 - v) + w_base * v
        if v < 0.4:                                          # dome-shaped top, not a box
            w *= math.sqrt(max(0.0, 1 - ((0.4 - v) / 0.4) ** 2))
        c = cx - lean * (1 - v)
        for x in range(round(c - w), round(c + w) + 1):
            edge = abs(x - c) > w - 1.2
            if not (edge and (x * 5 + y * 3) % 4 == 0):      # ragged rim
                S.add((x, y))
    return S


def packed(S, rnd, step):
    """Jittered grid of stamp positions inside S."""
    xs = [p[0] for p in S]; ys = [p[1] for p in S]
    out = []
    for y in range(min(ys), max(ys) + 1, step):
        for x in range(min(xs) + (y // step) % 2 * (step // 2), max(xs) + 1, step):
            jx, jy = x + rnd.randint(-1, 1), y + rnd.randint(-1, 1)
            if (jx + 1, jy + 1) in S:
                out.append((jx, jy))
    return out


# ------------------------------------------------------------------------------------------ the loads
def load_ha(im, rnd):            # lotus (sen): buds on long stems fanning up, open flowers, big round leaves
    for i in range(16):                                      # stems
        a = -1.2 + 2.4 * i / 15
        thick(im, (12 + round(a * 2), 21), (12 + round(a * 11) - 2, 3 + abs(round(a * 4))), "leaf_d", 1)
    for (cx, cy, r) in ((4, 17, 3), (20, 17, 3), (11, 19, 3), (2, 10, 3), (21, 9, 2), (13, 12, 3)):
        lotus_leaf(im, cx, cy, r)
    for (x, y) in [(1, 2), (5, 0), (9, 1), (13, 0), (17, 1), (21, 3), (-1, 6), (3, 5), (8, 6), (15, 5), (19, 7),
                   (23, 9), (6, 10), (11, 8), (17, 11), (0, 13)]:
        lotus_bud(im, x, y)
    for (x, y) in ((8, 13), (15, 15), (2, 15)):
        lotus_open(im, x, y)


def load_xuan(im, rnd):          # peach branches (đào): dark twigs fanning up, crowded with pink blossoms
    twigs = [[(12, 21), (9, 13), (4, 6), (1, 1)], [(12, 21), (11, 11), (10, 3), (8, 0)],
             [(12, 21), (14, 12), (17, 4), (19, 0)], [(12, 21), (16, 14), (22, 8), (25, 5)], [(12, 21), (7, 15), (1, 11)],
             [(10, 11), (5, 9)], [(14, 12), (13, 6)], [(17, 5), (21, 2)], [(9, 13), (13, 9)]]
    blossoms = []
    for tw in twigs:
        for a, b in zip(tw, tw[1:]):
            thick(im, a, b, "trunk_d", 1)
            n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
            for i in range(0, n + 1, 1):                    # a blossom cluster at every pixel of every twig
                blossoms.append((round(a[0] + (b[0] - a[0]) * i / n), round(a[1] + (b[1] - a[1]) * i / n)))
    for (x, y) in blossoms:
        if y > 18:
            continue
        for dx, dy in ((rnd.randint(-2, 1), rnd.randint(-2, 1)), (rnd.randint(-1, 2), rnd.randint(-1, 2)),
                       (rnd.randint(-3, 2), rnd.randint(-2, 2))):
            X, Y = x + dx, y + dy
            P(im, X, Y, "wp_l"); P(im, X + 1, Y, "pk_l"); P(im, X, Y + 1, "pk_l"); P(im, X + 1, Y + 1, "pk")
            if rnd.random() < 0.3:
                P(im, X, Y, "white")
        if rnd.random() < 0.25:
            P(im, x + 2, y - 1, "leaf_l")
    for tw in twigs:                                         # twig tips poking out of the blossom cloud
        (ax, ay), (bx, by) = tw[-2], tw[-1]
        for i in range(3):
            P(im, round(bx + (ax - bx) * i / 6), round(by + (ay - by) * i / 6), "trunk_d")
    for tw in twigs[:5]:                                     # and the main branches near the basket
        (ax, ay), (bx, by) = tw[0], tw[1]
        thick(im, (ax, ay - 2), (round(ax + (bx - ax) * 0.5), round(ay + (by - ay) * 0.5)), "trunk", 1)


def load_thu(im, rnd):           # yellow chrysanthemums (cúc vàng), densely packed pompoms
    S = fan(12, 21, 0, 13, 8, lean=2)
    for (x, y) in S:
        P(im, x, y, "leaf_d")
    for (x, y) in packed(S, rnd, 3):
        mum(im, x, y)


def load_dong(im, rnd):          # white daisies (cúc họa mi): a cloud of small white heads with yellow eyes
    S = fan(12, 21, 0, 13, 8, lean=2)
    for (x, y) in S:
        P(im, x, y, "leaf_d" if rnd.random() < 0.6 else "leaf")
    for (x, y) in packed(S, rnd, 3):
        daisy(im, x, y)
    for (x, y) in sorted(S):
        if rnd.random() < 0.06:
            P(im, x, y, "white")


def front_ha(im, rnd):
    thick(im, (49, 20), (47, 14), "leaf_d", 1); thick(im, (51, 20), (52, 12), "leaf_d", 1)
    thick(im, (53, 20), (56, 15), "leaf_d", 1)
    for (x, y) in ((44, 12), (50, 8), (55, 12)):
        sunflower(im, x, y)
    for (x, y) in ((48, 17), (54, 17), (50, 14)):
        P(im, x, y, "leaf"); P(im, x + 1, y, "leaf_l")


def front_roses(im, rnd):
    S = fan(51, 19, 10, 6, 5)
    for (x, y) in S:
        P(im, x, y, "leaf_d" if rnd.random() < 0.6 else "leaf")
    for (x, y) in packed(S, rnd, 3):
        rose(im, x, y, "red_l", "red", "red_d")
    for (x, y) in sorted(S)[::5]:
        if rnd.random() < 0.4:
            P(im, x, y, "white")


def front_thachthao(im, rnd):
    S = fan(51, 19, 9, 7, 5)
    for (x, y) in sorted(S):
        r = rnd.random()
        P(im, x, y, "du_2" if r < 0.35 else ("du_3" if r < 0.75 else ("white" if r < 0.85 else "leaf_d")))


LOADS = {"xuan": (load_xuan, front_roses), "ha": (load_ha, front_ha), "thu": (load_thu, front_thachthao),
         "dong": (load_dong, front_roses)}


# ------------------------------------------------------------------------------------------ bike + rider
def wheel(im, c, k):
    cx, cy = c
    ellipse(im, cx - WR, cy - WR, cx + WR, cy + WR, "ink")
    for y in range(cy - WR + 2, cy + WR - 1):                 # see-through spoked wheel
        for x in range(cx - WR + 2, cx + WR - 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= (WR - 1.6) ** 2:
                im.putpixel((x, y), (0, 0, 0, 0))
    a0 = k * math.pi / 8
    for j in range(3):
        a = a0 + j * math.pi / 3
        for r in range(-(WR - 2), WR - 1):
            if r:
                P(im, round(cx + math.cos(a) * r), round(cy + math.sin(a) * r), "grey_l")
    P(im, cx, cy, "grey"); P(im, cx - 2, cy - WR, "grey_k"); P(im, cx - 3, cy - WR + 1, "grey_k")


def leg(im, hip, pedal, col, shoe):
    L1, L2 = 10.0, 10.0
    hx, hy = hip; px, py = pedal
    d = min(math.hypot(px - hx, py - hy), L1 + L2 - 0.01)
    a = math.atan2(py - hy, px - hx)
    b = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    kx = hx + L1 * math.cos(a - b); ky = hy + L1 * math.sin(a - b)
    thick(im, (hx, hy), (round(kx), round(ky)), col)
    thick(im, (round(kx), round(ky)), (px, py - 1), col)
    rect(im, px, py, px + 2, py, shoe)


def basket_rear(im):
    """Round bamboo thúng on the rear rack, woven."""
    x0, x1, y0, y1 = 1, 23, 20, 27
    for y in range(y0, y1 + 1):
        inset = 0 if y < y1 - 1 else (1 if y == y1 - 1 else 3)
        for x in range(x0 + inset, x1 - inset + 1):
            c = "trunk_l" if (x + y) % 3 else "trunk"
            if y == y0:
                c = "wy"
            elif y == y0 + 1:
                c = "wy_d"
            elif x == x1 - inset:
                c = "trunk"
            P(im, x, y, c)
    rect(im, 0, 28, 24, 28, "grey_k"); thick(im, (6, 28), RW, "grey_k", 1)


def basket_front(im):
    rect(im, 45, 19, 56, 25, "trunk_l"); rect(im, 45, 19, 56, 19, "wy"); rect(im, 45, 20, 56, 20, "wy_d")
    for x in (47, 50, 53):
        line(im, x, 21, x, 25, "trunk")
    rect(im, 46, 26, 55, 26, "trunk")
    thick(im, (45, 25), (43, 27), "grey_k", 1)


def frame(kind, k):
    im = new(BW, BH)
    th = k * math.pi / 2
    pn = (round(BB[0] + 4 * math.cos(th)), round(BB[1] + 4 * math.sin(th)))
    pf = (round(BB[0] + 4 * math.cos(th + math.pi)), round(BB[1] + 4 * math.sin(th + math.pi)))
    load, front = LOADS[kind]
    load(im, random.Random(5))                             # the big rear bouquet, behind everything
    basket_rear(im)
    leg(im, (HIP[0] + 1, HIP[1]), pf, PANTS_D, "sk")         # far leg
    wheel(im, RW, k); wheel(im, FW_, k)
    # step-through frame (curved down tube), like the old women's bikes
    thick(im, RW, BB, FRAME, 1); thick(im, RW, (23, 26), FRAME, 1)
    thick(im, BB, (23, 25), FRAME, 2)
    for a, b in (((41, 25), (35, 29)), ((35, 29), (31, 33)), ((31, 33), BB)):
        thick(im, a, b, FRAME, 2)
    P(im, 40, 25, FRAME_L); P(im, 36, 28, FRAME_L)
    thick(im, (41, 22), (42, 27), FRAME, 2); thick(im, (42, 27), FW_, FRAME, 1)      # head tube + fork
    rect(im, 39, 21, 44, 21, "grey_k"); P(im, 45, 22, "grey_k")                       # handlebar
    rect(im, 21, 24, 26, 24, "ink"); P(im, 21, 23, "ink")                              # saddle
    ellipse(im, BB[0] - 2, BB[1] - 2, BB[0] + 2, BB[1] + 2, "grey"); P(im, BB[0] - 1, BB[1] - 1, "grey_l")
    P(im, 44, 24, "lamp"); P(im, 44, 25, "glow")                                       # bike lamp
    basket_front(im)
    front(im, random.Random(9))
    # rider: torso, arm, head under the nón lá
    for y in range(12, 24):
        lean = (23 - y) // 4
        rect(im, 22 + lean, y, 27 + lean, y, SHIRT); P(im, 27 + lean, y, SHIRT_D); P(im, 26 + lean, y, SHIRT_D)
    thick(im, (28, 14), (40, 20), SHIRT_D)                                             # arm
    rect(im, 40, 20, 41, 21, "sk")
    rect(im, 27, 6, 32, 11, "sk"); rect(im, 27, 6, 28, 11, "sk_d")                     # face
    P(im, 31, 8, "hair"); P(im, 26, 8, "hair"); P(im, 26, 9, "hair"); P(im, 26, 10, "hair"); P(im, 25, 10, "hair")
    rect(im, 28, 12, 30, 12, "sk_d")                                                   # neck
    for y, (a, b) in enumerate(((29, 31), (27, 33), (25, 35), (23, 37))):              # nón lá
        rect(im, a, y + 1, b, y + 1, "wy_l" if y < 2 else "wy")
    rect(im, 22, 5, 38, 5, "wy_d"); P(im, 28, 2, "white"); P(im, 27, 3, "wy_l")
    leg(im, HIP, pn, PANTS, "sk")                                                      # near leg
    return im


def build():
    out = {}
    for kind in LOADS:
        frames = [frame(kind, k) for k in range(4)]
        save_asset("actors", f"bike_flowers_{kind}", frames, fps=8, anchor=(BW // 2, GROUND),
                   notes=f"xe đạp hoa ({kind}): faces right; anchor = centre-bottom (tyre row)")
        out[kind] = frames
    return out


if __name__ == "__main__":
    out = build()
    from PIL import Image
    k = 8; bg = (85, 89, 95)
    S = Image.new("RGB", (4 * (BW * k + 10), BH * k), bg)
    for i, kind in enumerate(LOADS):
        f = out[kind][0]
        b = Image.new("RGBA", f.size, bg + (255,)); b.alpha_composite(f)
        S.paste(b.convert("RGB").resize((BW * k, BH * k), Image.NEAREST), (i * (BW * k + 10), 0))
    S.save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/bike.png")
    print("ok")
