from common import *

KINDS["dancer"] = dict(hh=7, hw=6, th=10, tw=6, ll=10, al=8, A=4, lm=2)
KINDS["dancer_tall"] = dict(hh=7, hw=6, th=10, tw=6, ll=17, al=8, A=3, lm=2)
N = 6
CW, CH = 64, 64            # final frame (incl. 1px outline)
BY = CH - 3                # ground row before outline offset (frame ground = BY+1)
HEAD_TOP = 14              # head canvas top y while walking
HW_, HH_ = 32, 38


def lion_head(open_amt, blink=False):
    h = new(HW_, HH_)
    mcx, mcy = 15, 19
    # --- shaggy mane ring (white / grey_l tufts), sweeping top -> back -> chin
    ellipse(h, 1, 7, 24, 31, "grey_l")
    for k in range(19):
        ang = math.radians(92 + k * 10.8)
        r0, r1 = 11.0, 14.0 + (k % 2) * 1.4
        x0, y0 = mcx + r0 * math.cos(ang), mcy + 1.05 * r0 * math.sin(ang)
        x1, y1 = mcx + r1 * math.cos(ang), mcy + 1.05 * r1 * math.sin(ang)
        px_, py_ = -math.sin(ang), math.cos(ang)
        poly(h, [(round(x0 + px_ * 1.8), round(y0 + py_ * 1.8)), (round(x1), round(y1)),
                 (round(x0 - px_ * 1.8), round(y0 - py_ * 1.8))], "white" if k % 2 == 0 else "grey_l")
    for x in range(5, 21):
        put(h, x, 31, "grey")
    # --- face (red), highlight upper-left
    ellipse(h, 6, 8, 29, 28, "red_d")
    ellipse(h, 6, 8, 28, 27, "red")
    ellipse(h, 9, 10, 20, 18, "red_hot")
    ellipse(h, 11, 11, 18, 16, "red")
    # --- horn
    poly(h, [(15, 9), (19, 0), (24, 9)], "gold")
    line(h, 17, 8, 19, 2, "yellow")
    line(h, 22, 8, 20, 4, "orange")
    rect(h, 14, 9, 25, 10, "gold")
    rect(h, 14, 10, 25, 10, "orange")
    # --- forehead mirror (gương)
    ellipse(h, 16, 11, 23, 18, "gold")
    ellipse(h, 17, 12, 22, 17, "sky_l")
    put(h, 18, 13, "white"); put(h, 19, 13, "white"); put(h, 18, 14, "white")
    put(h, 21, 16, "blue"); put(h, 20, 16, "blue")
    put(h, 19, 11, "yellow"); put(h, 20, 18, "orange")
    # --- pom-poms (fur balls with red hearts)
    for (x, y) in ((3, 9), (8, 3), (4, 22)):
        ellipse(h, x, y, x + 4, y + 4, "grey_l")
        ellipse(h, x, y, x + 3, y + 3, "white")
        put(h, x + 2, y + 2, "red")
    # --- brow + big eye with lids
    line(h, 22, 13, 29, 12, "white")
    line(h, 23, 12, 28, 11, "white")
    ellipse(h, 23, 14, 29, 22, "white")
    rect(h, 26, 16, 28, 20, "ink")
    put(h, 26, 16, "white")
    put(h, 25, 18, "grey_l")
    # lids (gold upper lid; closes on blink)
    lid_h = 6 if blink else 1
    for yy in range(14, 14 + lid_h):
        for xx in range(22, 31):
            if h.getpixel((xx, yy)) in (c("white"), c("ink")):
                put(h, xx, yy, "gold")
    line(h, 22, 14 + lid_h - 1 if blink else 15, 29, 14 + lid_h - 1 if blink else 15, "orange")
    # --- cheek pom
    ellipse(h, 12, 21, 16, 25, "salmon")
    put(h, 13, 22, "white")
    # --- nose
    ellipse(h, 28, 21, 31, 25, "gold")
    put(h, 28, 21, "yellow"); put(h, 30, 24, "orange")
    # --- mouth: upper lip fixed, lower jaw drops by open_amt
    jy = 26 + open_amt
    if open_amt:
        rect(h, 17, 26, 30, jy, "ink")
        rect(h, 18, 27 if open_amt > 1 else 26, 29, jy, "red_d") if open_amt > 1 else None
    for x in (18, 20, 22, 24, 26, 28):
        put(h, x, 26, "white")
        if open_amt >= 2:
            put(h, x + 1, jy - 0, "white") if False else None
    ellipse(h, 14, jy, 30, jy + 6, "red_d")
    ellipse(h, 14, jy, 29, jy + 5, "red")
    for x in (19, 22, 25, 28):
        if open_amt:
            put(h, x, jy + 0, "white")
    rect(h, 15, jy + 5, 29, jy + 5, "red_d")
    # --- beard (jagged white fur)
    for x in range(13, 30):
        ln = 3 + (x % 3)
        for yy in range(jy + 6, min(HH_, jy + 6 + ln)):
            put(h, x, yy, "white" if yy < jy + 5 + ln else "grey_l")
    return h


def lion_body(i, mode, hdy):
    """fabric body 40x56 canvas (placed at x=1,y=0). mode 'walk' | 'rear'"""
    b = new(42, 62)
    ph = i / N * 2 * math.pi
    top, bot = {}, {}
    L = 38
    for x in range(L):
        hump = 8.0 * math.sin(math.pi * (x - 1) / 17) if x < 18 else 0
        hump2 = 3.0 * math.sin(math.pi * (x - 18) / 20) if x >= 18 else 0
        t = 33 - hump - hump2 + math.sin(ph + x / 3) * 0.6
        bt = 47 + math.sin(ph - x / 2.2) * 1.2
        if mode == "rear":
            s = (x / (L - 1)) ** 1.3
            t -= 14 * s
            bt -= 7 * s
        top[x], bot[x] = int(round(t)), int(round(bt))
    for x in range(L):
        for y in range(top[x], bot[x] + 1):
            put(b, x, y, "red")
        put(b, x, top[x], "red_hot")
        put(b, x, top[x] + 1, "red_hot") if x % 2 == 0 else None
        for y in range(bot[x] - 4, bot[x] + 1):
            put(b, x, y, "red_d") if y > bot[x] - 3 else None
    # scale pattern: neat scallops in gold over orange
    sc = [0, 1, 2, 2, 1, 0]
    for row, yo in enumerate((4, 11)):
        for x0 in range(1 + (row % 2) * 3, L - 6, 7):
            for dx in range(6):
                xx = x0 + dx
                y = top[min(xx, L - 1)] + yo + sc[dx]
                if y + 1 < bot[xx] - 3:
                    put(b, xx, y, "gold")
                    if 0 < dx < 5:
                        put(b, xx, y + 1, "orange")
    # gold hem band + hanging fringe
    for x in range(L):
        put(b, x, bot[x] - 1, "gold")
        put(b, x, bot[x], "orange")
        fl = 2 + (x % 2)
        for y in range(bot[x] + 1, bot[x] + 1 + fl):
            put(b, x, y, "yellow" if x % 2 == 0 else "gold")
    # tail tuft
    rect(b, 0, top[0] - 1, 2, top[0] + 2, "gold")
    put(b, 0, top[0] - 2, "yellow"); put(b, 1, top[0] - 3, "white"); put(b, 0, top[0] - 4, "grey_l")
    put(b, 2, top[0] - 2, "white")
    return b


def make(i, mode="walk", variant=None):
    img = new(CW - 2, CH - 2)
    by = BY - 1
    if mode == "walk":
        legs(img, 11, by, i, N, "dancer", "gold", "orange", "ink", phase=0.0, w=3)
        legs(img, 46, by, i, N, "dancer", "gold", "orange", "ink", phase=0.5, w=3)
        hdy = [0, -1, -2, -1, 0, 1][i]
        hdx = 0
        open_amt = [0, 1, 3, 5, 3, 1][i]
        blink = (i == 5)
        bdy = [0, -1, -1, 0, -1, -1][i]
    else:
        k = i  # 0..3
        # rear performer stomps, front performer stands tall
        legs(img, 10, by, [1, 2, 4, 5][k], N, "dancer", "gold", "orange", "ink", drop=0, w=3)
        legs(img, 47, by, [2, 4, 1, 5][k], N, "dancer_tall", "gold", "orange", "ink", drop=0, w=3)
        hdy = -14 + [0, -1, 0, 1][k]
        hdx = [-1, 1, -1, 1][k]
        open_amt = [5, 2, 5, 2][k]
        blink = False
        bdy = [0, -1, 0, -1][k]
    body = lion_body(i, mode, hdy)
    img.alpha_composite(body, (1, bdy))
    head = lion_head(open_amt, blink)
    img.alpha_composite(head, (30 + hdx, HEAD_TOP + hdy + (1 if mode == "rear" and False else 0)))
    out = outline(img, "brown_k")
    if variant == "gold":
        out = recolor(out, {"red": "gold", "red_d": "orange", "red_hot": "yellow", "gold": "green", "yellow": "green_l",
                            "orange": "green_d", "salmon": "glow", "grey_l": "mint", "grey": "green",
                            "white": "glow"})
    return out


def export(name, variant):
    fr = [make(i, "walk", variant) for i in range(N)] + [make(i, "rear", variant) for i in range(4)]
    fw, fh = fr[0].size
    st = {"walk": list(range(6)), "rear": [6, 7, 8, 9]}
    ax = 36   # between the two performers' feet
    save_asset(G, f"{name}_R", fr, fps=8, anchor=(ax, fh - 2), states=st,
               notes="Mua lan, faces RIGHT. states: walk(0-5, loop) / rear(6-9, front performer stands tall, head +14px). anchor=feet centre, ground row = fh-2. Thu procession.")
    save_asset(G, f"{name}_L", [flip(f) for f in fr], fps=8, anchor=(fw - 1 - ax, fh - 2), states=st, notes="mirror of _R (head faces left)")


if __name__ == "__main__":
    export("lion_dance", None)
    export("lion_dance_gold", "gold")
