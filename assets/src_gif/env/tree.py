from parts import *
import math

X = TREE_TRUNK_X


def disk(cx, cy, r):
    return blob_mask([(cx, cy, r)])


def top_edge(x):
    """Flat, uneven crown top (wider than tall)."""
    t = [10, 6, 9, 5, 8, 11, 7, 4, 8, 12, 9, 14, 12, 17, 15, 22]
    return t[min(len(t) - 1, x // 7)]


def bot_edge(x):
    b = [92, 98, 94, 103, 99, 108, 104, 100, 107, 112, 108, 114, 110, 106, 100, 96]
    return b[min(len(b) - 1, x // 7)]


def right_edge(y):
    r = [88, 96, 103, 99, 106, 108, 101, 95, 100, 92, 86, 84, 80]
    return r[max(0, min(len(r) - 1, y // 10))]


def inside(x, y):
    return -2 <= x <= right_edge(y) and top_edge(max(x, 0)) <= y <= bot_edge(max(x, 0))


def make_clumps():
    rnd = random.Random(21)
    out = []
    # tiers top -> bottom; lower tiers overlap upper ones
    y = 6
    tier = 0
    while y < 122:
        x = -4 + rnd.randint(0, 5)
        while x < 112:
            r = rnd.choice([5, 6, 7, 8, 9, 10, 7, 8])
            cx = x + r // 2
            cy = y + rnd.randint(-2, 3)
            if inside(cx, cy) and rnd.random() > .2 and not (16 <= cx <= 54 and cy >= 88 and rnd.random() < .8):
                out.append(dict(x=cx, y=cy, r=r))
            x += r + rnd.choice([-2, -1, 0, 1, 2, 4])
        y += rnd.choice([7, 8, 9])
        tier += 1
    # small edge clumps (3-5 px) for the ragged silhouette
    for _ in range(130):
        x = rnd.randint(-2, 108)
        e = rnd.choice(["t", "b", "r"])
        if e == "t":
            y = top_edge(max(x, 0)) + rnd.randint(-1, 2)
        elif e == "b":
            y = bot_edge(max(x, 0)) - rnd.randint(0, 3)
            if 14 <= x <= 56 and y >= 88: continue
        else:
            y = rnd.randint(24, 100); x = right_edge(y) - rnd.randint(0, 3)
        out.append(dict(x=x, y=y, r=rnd.choice([3, 4, 4, 5]), small=True))
    out.sort(key=lambda c: (c["y"] + c["r"] // 2, c["x"]))
    return out


def clump_draw(img, cx, cy, r, ramp):
    d, b, l, hl = ramp
    D = disk(cx, cy, r)
    B = disk(cx - 1, cy - 1, max(1, r - 1)) if r >= 4 else D
    sp(img, D, d)
    sp(img, B, b if r >= 4 else d)
    if r >= 4:
        for (x, y) in B:
            s_ = (x - cx) + (y - cy)
            if (x + 1, y + 1) not in B and s_ <= -r * .45:
                put(img, x, y, hl if r >= 6 else l)
            elif r >= 6 and (x + 3, y + 3) not in B and s_ <= -r * .5:
                put(img, x, y, l)
            elif r >= 8 and (x + 4, y + 4) not in B and s_ <= -r * .8:
                put(img, x, y, l)
        if r >= 6:   # lit patch upper-left
            P = disk(cx - r // 3 - 1, cy - r // 3 - 1, r // 2 + 1) & B
            sp(img, P, l)
            for (x, y) in P:
                if (x + 1, y + 1) not in P and (x - cx) + (y - cy) < -r * .5:
                    put(img, x, y, hl)
        if r >= 7:   # shade notch lower right
            put(img, cx + r // 3, cy + r // 3, d); put(img, cx + r // 3 + 1, cy + r // 3, d)
            put(img, cx + r // 3, cy + r // 3 + 1, d)


def ramp_for(x, y, r):
    t = (y - 6) / 116 * .85 + x / 106 * .15
    if t < .30: return ("leaf_d", "leaf", "leaf_l", "leaf_hl")
    if t < .62: return ("leaf_d", "leaf", "leaf_l", "leaf_l")
    return ("leaf_k", "leaf_d", "leaf", "leaf_l")


def trunk_geom():
    pts = []
    for y in range(196, 96, -1):
        t = (196 - y) / 100
        hw = 6.2 - 3.0 * min(1, t * 1.1)
        if y > 190:
            hw += (y - 190) * 0.45
        cx = X
        pts.append((y, cx, hw))
    return pts


def draw_trunk(img):
    for y, cx, hw in trunk_geom():
        xa, xb = int(round(cx - hw)), int(round(cx + hw))
        rect(img, xa, y, xb, y, "trunk")
        rect(img, xa, y, xa + 1, y, "trunk_l")
        rect(img, xb - 1, y, xb, y, "trunk_d")
        if (y // 7) % 2 == 0:
            put(img, xa + 3, y, "trunk_d")
        if (y // 9) % 2 == 1:
            put(img, xa + 2, y, "trunk_l")
        put(img, xa - 1, y, "trunk_d") if False else None
    # dark outline on both sides
    for y, cx, hw in trunk_geom():
        xa, xb = int(round(cx - hw)), int(round(cx + hw))
        put(img, xa - 1, y, "trunk_d"); put(img, xb + 1, y, "trunk_d")
    # whitewashed lower trunk (Hanoi street trees)
    for y, cx, hw in trunk_geom():
        if y >= 176 - ((y * 7) % 3 == 0 and 0):
            xa, xb = int(round(cx - hw)), int(round(cx + hw))
            rect(img, xa, y, xb, y, "paper")
            rect(img, xa, y, xa + 1, y, "white")
            rect(img, xb - 2, y, xb, y, "grey_l")
            put(img, xa - 1, y, "grey"); put(img, xb + 1, y, "grey_m")
    # white band edge ragged
    for y, cx, hw in trunk_geom():
        if y == 181:
            xa = int(round(cx - hw))
            rect(img, xa + 3, y, xa + 5, y, "paper")
    # root flare shadow row
    rect(img, X - 8, 196, X + 9, 196, "trunk_d")
    rect(img, X - 6, 195, X - 5, 195, "trunk_d"); rect(img, X + 6, 195, X + 7, 195, "trunk_d")


def draw_branch(img, pts, w0, w1):
    n = len(pts) - 1
    for i in range(n):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        steps = max(abs(xb - xa), abs(yb - ya), 1)
        for s in range(steps + 1):
            t = (i + s / steps) / n
            x = round(xa + (xb - xa) * s / steps); y = round(ya + (yb - ya) * s / steps)
            w = max(1, round(w0 + (w1 - w0) * t))
            rect(img, x - w // 2, y, x - w // 2 + w - 1, y, "trunk")
            put(img, x - w // 2, y, "trunk_l") if w >= 2 else None
            put(img, x - w // 2 + w - 1, y, "trunk_d")
    return


BRANCHES = [
    [(32, 116), (28, 104), (18, 92), (8, 78)],
    [(32, 112), (28, 94), (24, 72), (16, 52)],
    [(35, 112), (38, 92), (46, 66), (52, 44)],
    [(36, 114), (50, 104), (68, 98), (90, 90)],
    [(36, 108), (56, 92), (74, 76), (88, 60)],
]




def make_frame(f, cl):
    img = canvas()
    draw_trunk(img)
    M = set((x, y) for x in range(-2, 107) for y in range(0, 122) if inside(x, y))
    # deep shadow fill (leaf_k) inside the crown, set back from the edge
    for (x, y) in M:
        if inside(x - 4, y) and inside(x + 4, y) and inside(x, y - 4) and inside(x, y + 4):
            put(img, x, y, "leaf_k")
    for br in BRANCHES:
        draw_branch(img, br, 7, 2)
    seq = [(0, 0), (1, 0), (0, 1)]
    for k, c in enumerate(cl):
        x, y, r = c["x"], c["y"], c["r"]
        near_edge = c.get("small") or not (inside(x - 12, y) and inside(x + 12, y) and inside(x, y - 12) and inside(x, y + 12))
        if near_edge and f:
            dx, dy = seq[(f + k) % 3] if k % 2 else seq[(2 * f + k) % 3]
            x += dx; y += dy
        clump_draw(img, x, y, r, ramp_for(x, y, r))
    # see-through gaps showing sky/branches near the lower rim
    for (hx, hy, hr) in [(52, 99, 2), (74, 106, 2), (12, 90, 2), (88, 80, 1), (30, 88, 1)]:
        for p in disk(hx, hy, hr):
            if 0 <= p[0] < W and 0 <= p[1] < H and img.getpixel(p)[3] and p[1] > 70:
                if f == 0 or True:
                    img.putpixel(p, (0, 0, 0, 0))
    # loose single leaves around the silhouette
    rnd = random.Random(4)
    for _ in range(300):
        x, y = rnd.randint(0, 112), rnd.randint(0, 122)
        if img.getpixel((x, y))[3] == 0:
            nb = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if any(0 <= a < W and 0 <= b < H and img.getpixel((a, b))[3] and img.getpixel((a, b))[:3] != RGB["trunk"] for a, b in nb) and rnd.random() < .28:
                put(img, x, y, rnd.choice(["leaf", "leaf_l", "leaf_d"]))
    return img


if __name__ == "__main__":
    cl = make_clumps()
    frames = [make_frame(f, cl) for f in range(3)]
    save_asset("env", "tree", frames, fps=3, anchor=(0, 0), notes="3-frame sway, edge clumps +-1px, trunk fixed")
