from common import *
import copy

MW, MH = 32, 28
RIDER = [
"..........HHHH.....",
".........HLHHHH....",
".........HHHHHHh...",
".........hhSSESS...",
".........hhSSSSs...",
"..........hSSSs....",
"..........sSSs.....",
"........KJJJJJJ....",
".......KJJJJJJjJ...",
".......KJJJJJjJJJ..",
"......KJJJJJjjjJJGG",
"......KJJJJJj..jJGG",
".....KJJJJJJj......",
".....KJJJJJJ.......",
"....PPPPPPPP.......",
"....pPPPPPPPPPP....",
".....pppPPPPPPPQ...",
"..............QQ...",
"..............QQ...",
".............QQ....",
".............QQ....",
".............qq....",
"............FFFFF..",
]
RLEG = {"P": "slate_d", "p": "navy", "Q": "slate_d", "q": "navy", "F": "ink"}


def rider_img(rows, leg, ox=0, oy=0, W=MW, H=MH, scoot=False):
    rows = list(rows)
    if scoot:  # lower torso 2px, keep feet on the floorboard
        rows = ["." * 19] * 2 + rows[:16] + rows[18:]
    rows = [r.ljust(19, ".") for r in rows]
    im = new(W, H)
    g = grid(rows, leg)
    im.alpha_composite(g, (8 + ox, 1 + oy))
    return im


def legend(helmet="slate_d", jacket="blue_d", pants="navy", skin="skin2", pants_d=None):
    ramp = {  # jacket: highlight, main, shade
        "blue_d": ("blue", "blue_d", "navy"), "red": ("salmon", "red", "red_d"), "green": ("green_l", "green", "green_d"),
        "slate": ("grey", "slate", "slate_d"), "gold": ("yellow", "gold", "orange"), "plum": ("mauve", "plum", "bloom_k"),
        "orange": ("gold", "orange", "rust"), "mint": ("white", "mint", "green"), "salmon": ("white", "salmon", "mauve"),
        "sky_l": ("white", "sky_l", "sky"), "grey_l": ("white", "grey_l", "grey"), "teal_k": ("mint", "green_d", "teal_k"),
        "brown_d": ("clay", "brown_d", "brown_k"),
    }[jacket]
    hr = {"slate_d": ("slate", "slate_d", "navy"), "red": ("salmon", "red", "red_d"), "white": ("white", "grey_l", "grey"),
          "gold": ("yellow", "gold", "orange"), "green": ("green_l", "green", "green_d"), "blue": ("sky_l", "blue", "blue_d"),
          "mint": ("white", "mint", "green"), "salmon": ("white", "salmon", "mauve"), "ochre": ("sand", "ochre", "clay"),
          "plum": ("mauve", "plum", "bloom_k")}[helmet]
    sk = {"skin2": ("skin2", "skin3"), "skin1": ("skin1", "skin2"), "skin3": ("skin3", "skin4")}[skin]
    pd = pants_d or "ink"
    return {"H": hr[1], "L": hr[0], "h": hr[2], "S": sk[0], "s": sk[1], "E": "brown_k",
            "J": ramp[1], "K": ramp[0], "j": ramp[2], "P": pants, "p": pd, "Q": pants, "q": pd, "F": "ink",
            "G": skin if False else sk[1]}


# ---------------------------------------------------------------- bikes
def bike(kind, wf, body="red", W=MW, H=MH, ox=0, oy=0):
    hi, mn, sh = {"red": ("salmon", "red", "red_d"), "blue": ("sky", "blue", "blue_d"), "white": ("white", "grey_l", "grey"),
                  "green": ("green_l", "green", "green_d"), "gold": ("yellow", "gold", "orange"),
                  "plum": ("mauve", "plum", "bloom_k")}[body]
    im = new(W, H)
    def R(x0, y0, x1, y1, n): rect(im, x0 + ox, y0 + oy, x1 + ox, y1 + oy, n)
    def P(x, y, n): put(im, x + ox, y + oy, n)
    def L(x0, y0, x1, y1, n): line(im, x0 + ox, y0 + oy, x1 + ox, y1 + oy, n)
    for cx in (7, 25):
        pass
    wheel(im, 7 + ox, 23 + oy, 4, wf, rim="grey_l")
    wheel(im, 25 + ox, 23 + oy, 4, wf, rim="grey_l")
    if kind == "under":
        R(3, 17, 10, 18, mn); L(3, 17, 10, 17, hi); P(2, 18, "red_hot")
        R(9, 19, 17, 21, mn); L(9, 19, 17, 19, hi); L(9, 21, 17, 21, sh)
        R(8, 16, 19, 16, "slate"); R(8, 17, 19, 17, "navy")
        R(12, 22, 18, 23, "slate"); R(13, 22, 17, 22, "grey"); L(12, 23, 18, 23, "slate_d")
        poly(im, [(20 + ox, 11 + oy), (22 + ox, 11 + oy), (23 + ox, 19 + oy), (20 + ox, 21 + oy)], mn)
        L(20, 11, 20, 20, hi); L(23, 14, 23, 19, sh)
        L(24, 12, 25, 23, "grey_l")
        R(22, 18, 28, 19, mn); L(22, 18, 28, 18, hi); L(22, 19, 28, 19, sh)
        L(22, 11, 26, 11, "slate_d"); P(23, 10, "grey"); P(23, 9, "grey_l")
        R(26, 12, 27, 13, "glow"); P(27, 13, "yellow")
        R(4, 21, 11, 22, "grey"); L(4, 21, 11, 21, "grey_l"); P(3, 22, "slate_d")
    else:  # scooter
        R(3, 16, 14, 20, mn); R(4, 21, 12, 21, mn); R(3, 16, 13, 16, hi); R(5, 20, 13, 21, sh)
        for p_ in [(3, 16), (3, 20)]: im.putpixel((p_[0] + ox, p_[1] + oy), CLEAR)
        R(5, 14, 16, 15, "navy"); L(5, 14, 16, 14, "slate"); P(2, 17, "red_hot"); P(3, 17, "red_hot")
        R(12, 22, 21, 23, "slate_d"); L(12, 22, 21, 22, "slate")
        poly(im, [(20 + ox, 9 + oy), (24 + ox, 9 + oy), (25 + ox, 21 + oy), (20 + ox, 21 + oy)], mn)
        L(20, 10, 20, 20, hi); L(24, 13, 24, 20, sh)
        L(22, 18, 28, 18, mn); R(22, 18, 28, 19, mn); L(22, 18, 28, 18, hi); L(22, 19, 28, 19, sh)
        R(19, 8, 25, 9, "slate_d"); L(19, 8, 25, 8, "slate"); P(22, 7, "grey"); P(22, 6, "grey_l")
        R(26, 10, 27, 12, "glow"); P(27, 12, "yellow")
        R(5, 22, 12, 22, "grey"); L(5, 22, 11, 22, "grey_l")
    return im


def moto(kind="under", outfit=None, wf=0, body="red", extra_back=None, extra_front=None, W=MW, H=MH, ox=0, oy=0,
         leg=None, out="ink", back_rider=None):
    im = new(W, H)
    b = bike(kind, wf, body, W, H, ox, oy)
    sc = kind == "scoot"
    if extra_back: extra_back(im)
    if back_rider:
        im.alpha_composite(rider_img(RIDER, back_rider, ox - 6, oy + 1, W, H, sc))
    r = rider_img(RIDER, leg, ox, oy, W, H, sc)
    # bike under the rider except wheels/front; simply bike first then rider
    im.alpha_composite(b)
    im.alpha_composite(r)
    if extra_front: extra_front(im)
    outl(im, out)
    return im


def finish(im, facing):
    return flip(im) if facing == "L" else im


def save_moto(name, builder, frames, fps=12, W=MW, H=MH, ax=16, states=None, notes=""):
    """builder(facing_unused, i) -> right-facing image; save R and L (L flipped)."""
    for f in "RL":
        fr = [finish(builder(i), f) for i in range(frames)]
        a = ax if f == "R" else W - 1 - ax
        save_asset(G, f"{name}_{f}", fr, fps=fps, anchor=(a, H - 1), states=states,
                   notes=("Facing %s. " % ("right" if f == "R" else "left") + notes))


import random


def blossoms(im, cx, cy, rx, ry, seed=3, n=90, cols=("bloom_l", "salmon", "bloom_hl", "bloom", "bloom_l", "salmon"), shade="bloom_d"):
    rnd = random.Random(seed)
    pts = []
    for _ in range(n):
        a = rnd.random() * 6.28; d = rnd.random() ** 0.6
        import math
        pts.append((int(cx + math.cos(a) * rx * d), int(cy + math.sin(a) * ry * d)))
    for x, y in pts:   # darker underlayer, then lit blobs offset up-left
        put(im, x + 1, y + 1, shade)
    for i, (x, y) in enumerate(pts):
        col = cols[(i + x) % len(cols)]
        put(im, x, y, col)
        if i % 3 == 0: put(im, x + 1, y, col)
        if i % 5 == 0: put(im, x, y - 1, "bloom_hl")


def poncho(im, t):
    tx, ty, by = [(3, 12, 9), (1, 14, 10), (2, 16, 9), (4, 14, 8)][t % 4]   # wing tip + billow height
    cape = [(16, 7), (21, 7), (24, 9), (26, 11), (25, 14), (24, 18), (19, 19), (13, 19), (9, 18),
            (tx + 3, ty + 4), (tx, ty), (tx + 2, by + 2), (9, by), (12, 8)]
    poly(im, cape, "blue")
    poly(im, [(13, 19), (24, 18), (25, 14), (19, 14), (14, 14), (tx + 5, ty + 3), (tx + 3, ty + 4), (9, 18)], "blue_d")
    line(im, 12, 8, 9, by, "sky"); line(im, 9, by, tx + 2, by + 2, "sky"); line(im, 12, 8, 21, 7, "sky")
    line(im, tx + 2, by + 3, tx + 1, ty - 1, "sky") if False else None
    line(im, tx + 3, ty + 1, 13, 12, "blue_d"); line(im, 16, 9, 15, 18, "blue_d"); line(im, 20, 10, 19, 18, "blue_d")
    line(im, 17, 8, 21, 8, "sky")
    rect(im, 26, 11, 27, 12, "skin3")           # hand on the grip
    # hood over the helmet, face open
    rect(im, 17, 1, 21, 2, "blue"); line(im, 17, 1, 20, 1, "sky"); rect(im, 16, 3, 19, 6, "blue"); rect(im, 16, 3, 16, 5, "blue_d")


def build_all():
    A = {}
    # 1 man
    lg = legend("ochre", "teal_k", "blue_d", pants_d="navy")
    A["moto_man"] = (lambda i, lg=lg: moto("under", None, i % 2, "red", leg=lg), 2, {})
    # 2 sun coat
    lg = legend("salmon", "mint", "mint", skin="skin1", pants_d="green"); lg.update({"G": "white", "Q": "slate_d", "q": "navy"})
    def sun_front(im):
        poly(im, [(10, 15), (14, 16), (12, 22), (6, 21), (4, 18)], "mint"); line(im, 5, 18, 11, 22, "green")
        line(im, 10, 16, 5, 19, "white")
        rect(im, 19, 7, 23, 7, "sky_l"); rect(im, 19, 8, 22, 8, "sky_l"); put(im, 19, 7, "white"); put(im, 20, 7, "white")
        line(im, 17, 7, 18, 7, "white"); put(im, 19, 9, "sky")
        put(im, 16, 8, "brown_k"); put(im, 16, 9, "brown_k"); put(im, 15, 10, "brown_k")
    A["moto_sun_ha"] = (lambda i, lg=lg: moto("scoot", None, i % 2, "white", leg=lg, extra_front=sun_front), 2, {})
    # 3 poncho
    lg = legend("blue", "slate", "navy")
    def pon(i, lg=lg):
        im = moto("under", None, i % 2, "blue", leg=lg)
        # re-draw: bike wheels after poncho so tyres stay readable
        im2 = new(MW, MH)
        im2.alpha_composite(im)
        poncho(im2, i)
        outl(im2, "ink")
        for cx in (7, 25):
            wheel(im2, cx, 23, 4, i % 2)
        return im2
    A["moto_poncho_ha"] = (pon, 4, {})
    # 4 peach
    ox, oy, W, H = 8, 14, 42, 42
    lgr = legend("gold", "brown_d", "blue_d", pants_d="navy")
    lgp = legend("salmon", "red", "slate_d", skin="skin1", pants_d="navy")
    def peach_front(im):
        # pillion raised arm + branch
        pass
    def peach(i):
        def back(im):
            # branch rises behind: held by pillion
            for (a, b, c_, d) in [(12, 22, 7, 8), (9, 14, 3, 5), (10, 16, 14, 4), (7, 11, 1, 10), (13, 22, 19, 9)]:
                line(im, a + 8 - 8 + 0, b + 0, c_ + 8, d, "brown_d") if False else line(im, a, b, c_, d, "brown_d")
            blossoms(im, 11, 8, 11, 9, seed=7, n=150)
        return moto("under", None, i % 2, "red", W=W, H=H, ox=ox, oy=oy, leg=lgr, back_rider=lgp, extra_back=None, extra_front=None)
    def peach_full(i, lgr=lgr, lgp=lgp, W=W, H=H, ox=ox, oy=oy):
        im = new(W, H)
        base = moto("under", None, i % 2, "red", W=W, H=H, ox=ox, oy=oy, leg=lgr, back_rider=lgp)
        br = new(W, H)
        for a in [(14, 27, 9, 14), (9, 14, 5, 3), (10, 12, 17, 4), (8, 10, 1, 9), (12, 16, 22, 11), (11, 12, 9, 2), (7, 7, 2, 4)]:
            line(br, a[0], a[1], a[2], a[3], "brown_d")
        for a in [(14, 26, 10, 15), (9, 13, 6, 5)]:
            line(br, a[0], a[1], a[2], a[3], "brown_k")
        for i_, (cx_, cy_, r_) in enumerate([(5, 3, 4), (17, 4, 4), (2, 9, 3), (22, 11, 3), (9, 6, 5), (12, 10, 4), (7, 12, 3), (19, 8, 3)]):
            blossoms(br, cx_, cy_, r_, r_, seed=7 + i_, n=14 + r_ * 3)
        rect(br, 14, 27, 15, 28, "skin1")
        im2 = new(W, H); im2.alpha_composite(br); im2.alpha_composite(base)
        # arm from pillion shoulder to branch
        line(im2, 14, 28, 15, 27, "red")
        return im2
    A["moto_peach"] = (peach_full, 2, dict(W=W, H=H, ax=ox + 16))
    # 5 quat xuan
    ox, oy, W, H = 12, 4, 44, 32
    lg = legend("ochre", "slate", "blue_d", pants_d="navy")
    def quat(i, lg=lg, W=W, H=H, ox=ox, oy=oy):
        base = moto("under", None, i % 2, "blue", W=W, H=H, ox=ox, oy=oy, leg=lg)
        tr = new(W, H)
        # pot on the rear rack + trunk + ball canopy
        rect(tr, 4, 20, 11, 24, "clay"); rect(tr, 4, 20, 11, 20, "gold"); rect(tr, 4, 24, 11, 24, "brown_d"); rect(tr, 9, 21, 11, 24, "rust")
        rect(tr, 7, 14, 8, 20, "brown_d")
        disc(tr, 8, 9, 8, "green_d")
        disc(tr, 7, 8, 7, "green")
        disc(tr, 5, 6, 4, "green_l") if False else None
        rnd = random.Random(5)
        for _ in range(26):
            x, y = rnd.randint(1, 15), rnd.randint(1, 16)
            if (x - 8) ** 2 + (y - 9) ** 2 <= 49:
                put(tr, x, y, "green_l" if (x + y) % 3 == 0 and x < 8 and y < 9 else "green_d" if x > 8 and y > 9 else "green")
        for x, y in [(4, 5), (9, 3), (12, 7), (6, 11), (10, 12), (3, 9), (8, 7), (13, 11), (7, 14), (11, 4), (5, 8), (9, 9)]:
            col = "orange" if (x + y) % 2 else "gold"
            put(tr, x, y, col); put(tr, x + 1, y, "orange" if col == "gold" else "rust")
        line(tr, 3, 21, 12, 23, "brown_k") if False else None
        # strap
        line(tr, 3, 22, 12, 22, "brown_k")
        out = new(W, H)
        out.alpha_composite(tr); out.alpha_composite(base)
        outl(out, "ink")
        return out
    A["moto_quat_xuan"] = (quat, 2, dict(W=W, H=H, ax=ox + 16))
    # 6 puffer
    lg = legend("slate_d", "orange", "blue_d", pants_d="navy"); lg.update({"G": "brown_d"})
    def puff_front(im):
        for y in (10, 13):
            line(im, 14, y, 19, y, "rust") if False else None
        for (x0, x1, y) in [(13, 18, 9), (13, 17, 11), (12, 17, 13)]:
            line(im, x0, y, x1, y, "rust")
        # scarf
        rect(im, 17, 7, 21, 8, "sky_l"); line(im, 17, 8, 21, 8, "sky"); 
        rect(im, 13, 8, 16, 9, "sky_l"); line(im, 12, 10, 13, 11, "sky")
        put(im, 12, 9, "sky"); put(im, 11, 10, "sky_l")
    A["moto_puffer_dong"] = (lambda i, lg=lg: moto("under", None, i % 2, "gold", leg=lg, extra_front=puff_front), 2, {})
    # 7 couple
    ox, W = 6, 38
    lgf = legend("red", "slate", "blue_d", pants_d="navy")
    lgb = legend("salmon", "plum", "slate_d", skin="skin1", pants_d="navy")
    A["scooter_couple"] = (lambda i, lgf=lgf, lgb=lgb, W=W, ox=ox: moto("scoot", None, i % 2, "plum", W=W, ox=ox, leg=lgf, back_rider=lgb), 2, dict(W=W, ax=ox + 16))
    return A


if __name__ == "__main__":
    for name, (bld, n, kw) in build_all().items():
        save_moto(name, bld, n, **kw, notes="12fps wheel spin" + (" + poncho flutter (4 frames)" if n == 4 else ""))
