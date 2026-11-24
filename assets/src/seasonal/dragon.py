from common import *

N = 8
CW, CH = 164, 52
BY = 50            # feet row (frame coords, before the 1px outline offset)
NPERF = 8
PX0, PDX = 12, 12  # performer x positions
YC, AMP = 14, 4
WAVE_L = 72.0
HEAD_X = 86        # left edge of the head canvas


def outl(img, col):
    o = outline(img, col)
    return o.crop((1, 1, img.width + 1, img.height + 1))


def wave(x, i):
    return YC + AMP * math.sin(2 * math.pi * (i / N) - x * 2 * math.pi / WAVE_L)


def thickness(x):
    return 5 + 6 * min(1.0, x / 70.0)          # tail thin -> head thick


def performer(i, k, cx, lead=False):
    """one adult performer (red tunic / yellow trousers), arms up holding a pole."""
    img = new(CW, CH)
    kd = KINDS["adult"]
    phase = k * 0.07
    hip = legs(img, cx, BY, i, N, "adult", "gold", "orange", "ink", phase=phase, drop=None)
    x0, x1 = cx - 2, cx + 3
    ty = hip - kd["th"]
    rect(img, x0, ty, x1, hip, "red")
    rect(img, x1, ty + 1, x1, hip, "red_d")
    rect(img, x0, ty + 4, x1, ty + 4, "yellow")        # sash
    rect(img, x0, hip, x1, hip, "yellow")
    head(img, cx, ty - 6, "adult", "skin2", "skin3", "ink", "short", blush=False)
    rect(img, cx - 2, ty - 5, cx + 3, ty - 5, "yellow")  # headband
    # both arms raised to the pole
    hx, hy = cx + 4, ty - 5
    thick(img, cx + 1, ty + 2, hx, hy, "red_d", 1)
    thick(img, cx, ty + 2, hx - 1, hy + 2, "red", 1)
    put(img, hx, hy, "skin2"); put(img, hx - 1, hy + 2, "skin2")
    return outl(img, "ink"), (hx, hy), ty


def head_img(open_amt, bob):
    """dragon head facing right, canvas 44x34; mane left, whiskers right"""
    h = new(44, 34)
    # mane (red flames) behind the head
    for k, (x, y) in enumerate(((0, 6), (2, 3), (4, 9), (1, 12), (3, 16), (5, 20), (2, 22))):
        poly(h, [(x + 6, y + 2), (x, y + 4 - (k % 2) * 2), (x + 6, y + 8)], "red" if k % 2 else "red_d")
    ellipse(h, 3, 6, 19, 24, "red")
    # horns (antler-like, pale with gold tips), sweeping back
    line(h, 11, 8, 6, 2, "sand"); line(h, 12, 8, 7, 2, "glow"); put(h, 5, 1, "gold"); put(h, 6, 1, "gold")
    line(h, 15, 7, 12, 1, "sand"); line(h, 16, 7, 13, 1, "glow"); put(h, 11, 0, "gold")
    line(h, 9, 5, 7, 6, "sand"); put(h, 13, 4, "sand")
    # cranium + snout
    ellipse(h, 6, 7, 21, 22, "gold")
    ellipse(h, 6, 7, 20, 21, "gold")
    poly(h, [(14, 9), (33, 9), (37, 12), (36, 15), (16, 16)], "gold")      # upper jaw
    gap = 2 + open_amt
    ly = 16 + gap
    poly(h, [(14, ly), (33, ly), (35, ly + 3), (33, ly + 5), (16, ly + 5)], "gold")  # lower jaw
    # mouth interior
    rect(h, 16, 16, 34, ly, "red_d")
    rect(h, 18, 17, 33, ly - 1, "ink") if gap > 3 else None
    # tongue
    rect(h, 20, ly - 1, 28, ly, "salmon")
    # teeth
    for x in range(17, 36, 3):
        put(h, x, 16, "white"); put(h, x, 17, "white") if gap > 2 else None
        put(h, x + 1, ly, "white"); put(h, x + 1, ly - 1, "white") if gap > 3 else None
    # shading
    poly(h, [(14, 14), (36, 14), (36, 15), (16, 16)], "orange")
    line(h, 7, 20, 20, 22, "orange")
    line(h, 15, 9, 33, 9, "yellow")
    for x in range(8, 20, 2):
        put(h, x, 8, "yellow")
    # nostrils + nose bump
    put(h, 34, 11, "brown_k"); put(h, 35, 12, "brown_k")
    ellipse(h, 33, 8, 37, 11, "gold"); put(h, 34, 9, "yellow")
    # eye: big, white with red ring, ink pupil, red brow
    ellipse(h, 19, 7, 25, 14, "red")
    ellipse(h, 20, 8, 24, 13, "white")
    rect(h, 22, 9, 24, 12, "ink"); put(h, 22, 9, "white")
    line(h, 18, 6, 27, 5, "red_d"); line(h, 19, 5, 26, 4, "red")
    # cheek scale + gill fin
    for (x, y) in ((10, 14), (13, 17), (9, 18)):
        put(h, x, y, "orange")
    poly(h, [(4, 14), (9, 12), (9, 20)], "red_d")
    # whiskers (long, flowing forward then down) in yellow
    for pts in (((36, 12), (39, 10), (42, 12), (43, 17)), ((36, 14), (40, 15), (42, 20), (43, 24))):
        for a, b in zip(pts, pts[1:]):
            line(h, a[0], a[1], b[0], b[1], "yellow")
    # beard under the chin: white fringe
    for x in range(15, 31):
        ln = 4 + (x % 3) + (open_amt // 2)
        for y in range(ly + 5, min(34, ly + 5 + ln)):
            put(h, x, y, "white" if y < ly + 4 + ln else "grey_l")
    return h


def segment(img_body, i):
    """body tube: column-wise, scales + belly fringe + dorsal fins + red hoops"""
    xs = range(2, HEAD_X + 12)
    for x in xs:
        yc = wave(x, i)
        th = thickness(x)
        top = int(round(yc - th / 2))
        bot = int(round(yc + th / 2))
        for y in range(top, bot + 1):
            put(img_body, x, y, "gold")
        # light top, shaded belly side
        put(img_body, x, top, "yellow"); put(img_body, x, top + 1, "yellow") if (x // 2) % 2 == 0 else None
        for y in range(bot - 2, bot + 1):
            put(img_body, x, y, "orange")
        # scale scallops
        sy = (top + bot) // 2
        ph = x % 6
        put(img_body, x, sy - 1 + [0, 1, 2, 2, 1, 0][ph] - 1, "orange") if th > 6 else None
        # white belly fringe
        if (x % 2) == 0:
            put(img_body, x, bot + 1, "white"); put(img_body, x, bot + 2, "grey_l") if x % 4 == 0 else None
        else:
            put(img_body, x, bot + 1, "grey_l")
        # red hoop at each segment joint
        if (x - PX0) % PDX in (0, 1):
            for y in range(top, bot + 1):
                put(img_body, x, y, "red" if (x - PX0) % PDX == 0 else "red_d")
        # dorsal fins (green) every 4px, triangles
        if x % 4 == 0:
            fh = 3 if th > 6 else 2
            for k in range(1, fh + 1):
                put(img_body, x, top - k, "green_l" if k == fh else "green")
                put(img_body, x - 1, top - k + 1, "green_d") if k < fh else None
    # tail tip flick
    xt = 2
    yt = int(round(wave(xt, i)))
    put(img_body, 0, yt - 1, "red"); put(img_body, 1, yt - 2, "red"); put(img_body, 0, yt - 3, "orange")


def pearl(bob):
    p = new(11, 13)
    ellipse(p, 1, 3, 9, 11, "orange")
    ellipse(p, 2, 4, 8, 10, "gold")
    ellipse(p, 2, 4, 6, 8, "yellow")
    put(p, 3, 5, "white")
    # swirl
    line(p, 5, 6, 8, 9, "red"); put(p, 6, 8, "orange")
    # flame wisps on top
    for (x, y) in ((3, 2), (5, 0), (7, 2), (4, 1), (6, 1)):
        put(p, x, y, "orange" if y else "yellow")
    put(p, 5, 1, "yellow"); put(p, 5, 2, "yellow")
    return outl(p, "brown_k")


def make(i):
    img = new(CW, CH)
    # performers + poles
    perf = new(CW, CH)
    poles = new(CW, CH)
    for k in range(NPERF):
        cx = PX0 + PDX * k
        p, (hx, hy), ty = performer(i, k, cx)
        perf.alpha_composite(p)
        # pole up to the body segment underside
        x = cx + 4
        th = thickness(x)
        ytop = int(round(wave(x, i) + th / 2)) + 1
        line(poles, x, hy, x, ytop, "brown_d")
        put(poles, x - 1, ytop, "brown_d")
    img.alpha_composite(perf)
    img.alpha_composite(poles)
    body = new(CW, CH)
    segment(body, i)
    img.alpha_composite(outl(body, "brown_k"))
    # head, riding on the front of the body, bobbing with the wave
    hy = int(round(wave(HEAD_X + 12, i))) - 14
    head = head_img(open_amt=[0, 1, 2, 3, 3, 2, 1, 0][i], bob=0)
    img.alpha_composite(outl(head, "brown_k"), (HEAD_X + 2, hy))
    # lead performer with the pearl, in front
    cx = 138
    lead, (hx, hy2), ty = performer(i, 9, cx, lead=True)
    img.alpha_composite(lead)
    px_, py_ = cx + 11, 8 + int(round(1.5 * math.sin(2 * math.pi * i / N)))
    line(img, hx, hy2, px_ + 4, py_ + 11, "brown_d")
    img.alpha_composite(pearl(0), (px_ - 1, py_ - 1))
    return img


if __name__ == "__main__":
    fr = [make(i) for i in range(N)]
    save_asset(G, "dragon_dance_R", fr, fps=8, anchor=(CW // 2, BY), notes="Mua rong, faces RIGHT: 8 performers (red/yellow) under a gold dragon, travelling sine wave, lead performer with pearl in front. 8 frames @ 8fps. anchor = feet centre (x=82,y=50 = ground row). Thu/Xuan procession on road or sidewalk.")
    save_asset(G, "dragon_dance_L", [flip(f) for f in fr], fps=8, anchor=(CW // 2 - 1, BY), notes="mirror of _R")
