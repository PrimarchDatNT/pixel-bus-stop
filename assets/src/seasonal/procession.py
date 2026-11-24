from common import *


def ong_dia(i):
    CW, CH = 28, 26
    img = new(CW, CH)
    bob = [0, -1, 0, -1][i]
    sway = [0, 1, 0, -1][i]
    cx, by = 12, 25
    bx = cx + sway
    for who, col, fx in (("far", "red_d", -1 if i in (0, 1) else 1), ("near", "red", 1 if i in (0, 1) else -1)):
        lift = 1 if (who == "near" and i == 2) or (who == "far" and i == 0) else 0
        rect(img, cx + fx * 2 - 1 + sway, by - 4 - lift, cx + fx * 2 + 1 + sway, by - 1 - lift, col)
        rect(img, cx + fx * 2 - 1 + sway, by - lift, cx + fx * 2 + 2 + sway, by - lift, "ink")
        put(img, cx + fx * 2 + sway, by - 1 - lift, "white")
    # belly + vest
    ellipse(img, bx - 5, 10 + bob, bx + 5, 21 + bob, "skin3")
    ellipse(img, bx - 5, 10 + bob, bx + 4, 20 + bob, "skin2")
    ellipse(img, bx - 4, 11 + bob, bx - 1, 14 + bob, "skin1")
    put(img, bx + 1, 16 + bob, "skin4")
    rect(img, bx - 5, 19 + bob, bx + 5, 21 + bob, "red")
    rect(img, bx - 5, 19 + bob, bx + 5, 19 + bob, "gold")
    rect(img, bx - 6, 10 + bob, bx - 4, 18 + bob, "yellow")
    rect(img, bx + 4, 10 + bob, bx + 6, 18 + bob, "gold")
    rect(img, bx - 4, 10 + bob, bx - 4, 18 + bob, "green")
    rect(img, bx + 4, 10 + bob, bx + 4, 18 + bob, "green_d")
    thick(img, bx - 5, 11 + bob, bx - 7, 15 + bob, "gold", 2)
    put(img, bx - 7, 16 + bob, "skin1")
    # head mask (smaller)
    hx, hy = bx + 1, 2 + bob
    ellipse(img, hx - 5, hy, hx + 5, hy + 9, "salmon")
    ellipse(img, hx - 5, hy, hx + 4, hy + 8, "skin1")
    ellipse(img, hx - 4, hy + 1, hx - 1, hy + 3, "glow")
    rect(img, hx - 4, hy + 5, hx - 3, hy + 5, "salmon"); rect(img, hx + 3, hy + 5, hx + 4, hy + 5, "salmon")
    for ex in (hx - 3, hx + 2):
        put(img, ex, hy + 3, "ink"); put(img, ex + 1, hy + 2, "ink"); put(img, ex + 2, hy + 3, "ink")
    rect(img, hx, hy + 4, hx + 1, hy + 5, "skin4")
    rect(img, hx - 3, hy + 6, hx + 4, hy + 6, "ink")
    rect(img, hx - 2, hy + 7, hx + 3, hy + 7, "white")
    rect(img, hx - 2, hy + 8, hx + 3, hy + 8, "ink")
    put(img, hx - 4, hy + 5, "ink"); put(img, hx + 5, hy + 5, "ink")
    for (x, y) in ((hx - 5, hy + 1), (hx - 6, hy + 3), (hx + 5, hy + 1), (hx + 6, hy + 3)):
        put(img, x, y, "ink")
    rect(img, hx - 3, hy - 1, hx + 3, hy, "green")
    rect(img, hx - 3, hy - 1, hx + 3, hy - 1, "green_l")
    put(img, hx, hy - 2, "yellow") if hy - 2 >= 0 else None
    img = outline(img, "ink")
    fx0, fy0 = bx + 8, 11 + bob
    ang = [0, 1, 0, -1][i]
    thick(img, bx + 5, 17 + bob, fx0 + 1, fy0 + 5, "brown_d", 1)
    fan = new(10, 8)
    poly(fan, [(5, 7), (0, 3), (2, 0), (7, 0), (9, 3)], "ochre")
    poly(fan, [(5, 6), (2, 3), (3, 1), (6, 1), (8, 3)], "sand")
    for k in range(0, 10, 2):
        line(fan, 5, 7, k, 2, "ochre")
    rect(fan, 2, 0, 7, 0, "gold")
    rect(fan, 4, 6, 6, 7, "brown_d")
    img.alpha_composite(fan, (fx0 - 3 + ang, fy0 - 3))
    put(img, bx + 6, 18 + bob, "skin1")
    return img


def drummer(i):
    N = 6
    CW, CH = 36, 32
    img = new(CW, CH)
    cx, by = 12, 30
    k = KINDS["adult"]
    hip = legs(img, cx, by, i, N, "adult", "navy", "ink", "ink")
    # broad adult torso (7 wide) with gold buttons
    x0, x1 = cx - 2, cx + 4
    ty = hip - k["th"]
    rect(img, x0, ty, x1, hip, "red_d")
    rect(img, x0, ty, x0 + 1, hip, "red")
    rect(img, x1, ty + 1, x1, hip, "bloom_k")
    rect(img, x0, hip, x1, hip, "gold")
    rect(img, x0 - 0, ty, x1, ty, "sand")
    for yy in (ty + 3, ty + 6):
        put(img, x1 - 2, yy, "gold")
    head(img, cx + 1, ty - 7, "adult", "skin2", "skin3", "ink", "short", blush=False)
    rect(img, cx - 2, ty - 5, cx + 4, ty - 5, "red")   # headband
    rect(img, cx - 2, ty - 6, cx + 1, ty - 6, "red")
    # beat sequence: U up / M mid / D hit
    seq = ["U", "U", "M", "D", "M", "U"]
    near_s, far_s = seq[i], seq[(i + 3) % 6]
    pos = {"U": (cx + 8, ty + 2), "M": (cx + 9, ty + 2), "D": (cx + 9, ty + 3)}
    sx, sy = cx + 2, ty + 2
    hands = {}
    for who, st, sl, sk in (("far", far_s, "red", "skin2"), ("near", near_s, "red_d", "skin2")):
        hx, hy = pos[st]
        if who == "far":
            hx -= 1
        thick(img, sx, sy, hx, hy, sl, 1)
        thick(img, sx, sy + 1, hx, hy + 1, sl, 1) if False else None
        put(img, hx, hy, sk)
        hands[who] = (hx, hy, st)
    img = outline(img, "ink")
    # drum worn at the belly: side-on barrel + pale drumhead on the right end
    d = new(14, 12)
    rect(d, 0, 1, 9, 10, "red")
    rect(d, 0, 1, 9, 1, "red_hot")
    rect(d, 0, 9, 9, 10, "red_d")
    rect(d, 6, 2, 9, 8, "red_d") if False else None
    for yy in range(2, 9):
        put(d, 9, yy, "red_d")
    rect(d, 0, 3, 9, 3, "gold"); rect(d, 0, 8, 9, 8, "gold")
    for xx in (1, 3, 5, 7):
        put(d, xx, 3, "yellow"); put(d, xx, 8, "yellow")
    ellipse(d, 8, 0, 13, 11, "ochre")
    ellipse(d, 8, 0, 12, 10, "sand")
    ellipse(d, 9, 2, 12, 9, "glow")
    d = outline(d, "brown_k")
    dx, dy = cx + 1, hip - 8
    img.alpha_composite(d, (dx, dy))
    # strap over the shoulder
    line(img, cx + 1, ty + 1, cx + 3, dy + 1, "brown_d")
    # sticks: 2px light wood
    drum_top = dy + 2
    for who in ("far", "near"):
        hx, hy, st = hands[who]
        hx += 1; hy += 1
        if st == "D":
            ex, ey = hx + 4, hy + 0
        elif st == "M":
            ex, ey = hx + 4, hy - 3
        else:
            ex, ey = hx + 3, hy - 6
        line(img, hx, hy, ex, ey, "ochre")
        line(img, hx, hy - 1, ex, ey - 1, "sand")
        put(img, ex, ey - (0 if st != "D" else 0), "white")
        put(img, hx, hy, "skin2")
    return img


if __name__ == "__main__":
    fr = [ong_dia(i) for i in range(4)]
    fw = fr[0].width
    save_asset(G, "ong_dia_R", fr, fps=6, anchor=(13, fr[0].height - 2), notes="Ong Dia, 4-frame waddle, faces RIGHT. Thu procession. anchor=feet.")
    save_asset(G, "ong_dia_L", [flip(f) for f in fr], fps=6, anchor=(fw - 1 - 13, fr[0].height - 2), notes="mirror of _R")
    fr = [drummer(i) for i in range(6)]
    fw = fr[0].width
    save_asset(G, "drummer_R", fr, fps=8, anchor=(13, fr[0].height - 2), notes="Drummer, red trong worn at belly with pale drumhead, 2px sticks alternate, 6-frame walk RIGHT. Thu procession.")
    save_asset(G, "drummer_L", [flip(f) for f in fr], fps=8, anchor=(fw - 1 - 13, fr[0].height - 2), notes="mirror of _R")
