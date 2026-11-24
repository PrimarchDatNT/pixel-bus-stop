from common import *
from bike import ik, thick
import random, math

VW, VH = 76, 32


def kumquat(im, cx, cy, r, seed):
    disc(im, cx, cy, r, "green_d")
    disc(im, cx - 1, cy - 1, r - 1, "green")
    rnd = random.Random(seed)
    for _ in range(r * 5):
        x, y = rnd.randint(cx - r, cx + r), rnd.randint(cy - r, cy + r)
        if (x - cx) ** 2 + (y - cy) ** 2 <= (r - 1) ** 2:
            put(im, x, y, "green_l" if x < cx and y < cy else "green_d" if x > cx and y > cy else "green")
    for _ in range(r * 2 + 2):
        x, y = rnd.randint(cx - r + 1, cx + r - 1), rnd.randint(cy - r + 1, cy + r - 1)
        if (x - cx) ** 2 + (y - cy) ** 2 <= (r - 1) ** 2:
            put(im, x, y, "orange"); put(im, x + 1, y, "gold" if (x + y) % 2 else "orange")


def van(open_bed, facing, wf):
    im = new(VW, VH)
    cy, R = 25, 6
    # chassis
    rect(im, 2, 21, 74, 24, "slate_d"); rect(im, 2, 21, 74, 21, "slate")
    if not open_bed:
        rect(im, 2, 3, 51, 20, "grey_l"); rect(im, 2, 3, 51, 4, "white"); rect(im, 2, 18, 51, 20, "grey")
        rect(im, 2, 13, 51, 15, "blue"); rect(im, 2, 13, 51, 13, "sky")
        for x in (12, 24, 36): line(im, x, 5, x, 12, "grey"); line(im, x, 16, x, 17, "grey")
        rect(im, 2, 3, 3, 20, "grey_l"); line(im, 3, 4, 3, 19, "grey"); im.putpixel((2, 3), CLEAR)
    else:
        rect(im, 2, 18, 51, 20, "brown_d")
        rect(im, 2, 11, 51, 20, "brown_d"); rect(im, 2, 11, 51, 11, "clay")
        for x in range(4, 51, 4): line(im, x, 12, x, 19, "rust")
        rect(im, 2, 17, 51, 17, "brown_k"); rect(im, 2, 20, 51, 20, "brown_k")
    # cab
    poly(im, [(53, 21), (53, 8), (57, 5), (67, 5), (72, 11), (74, 13), (74, 21)], "blue")
    rect(im, 57, 5, 67, 5, "sky"); line(im, 53, 8, 53, 20, "sky")
    rect(im, 53, 17, 74, 21, "blue_d")
    poly(im, [(56, 14), (56, 8), (58, 6), (66, 6), (70, 11), (70, 14)], "slate_d")
    poly(im, [(57, 13), (57, 8), (58, 7), (65, 7), (68, 11), (68, 13)], "blue_d")
    line(im, 60, 7, 58, 11, "sky"); line(im, 62, 7, 61, 9, "sky")
    line(im, 63, 8, 63, 19, "blue_d")
    rect(im, 60, 15, 61, 15, "navy")
    rect(im, 73, 14, 74, 16, "glow"); put(im, 74, 16, "yellow"); rect(im, 73, 18, 74, 18, "orange")
    rect(im, 2, 18, 3, 19, "red_hot")
    rect(im, 72, 21, 75, 22, "slate"); rect(im, 54, 11, 55, 12, "slate_d")
    # wheels
    for cx in (20, 62):
        disc(im, cx, cy, 8, "ink", clip=lambda x, y: y <= 21)
    outl(im, "ink")
    for cx in (20, 62):
        wheel(im, cx, cy, R, wf)
    if open_bed:
        pass
    return im


def van_q(facing, wf):
    base = van(True, "R", wf)
    tr = new(VW, VH)
    for i, cx in enumerate((10, 25, 40)):
        rect(tr, cx - 1, 9, cx, 14, "brown_d")
        kumquat(tr, cx, 7, 6, 10 + i)
    out = new(VW, VH)
    out.alpha_composite(tr)
    ov = new(VW, VH); ov.alpha_composite(base)
    tmp = new(VW, VH); tmp.alpha_composite(tr)
    outl(tmp, "ink")
    out = tmp
    # bed front + rails over the pots
    bedonly = new(VW, VH); bedonly.alpha_composite(base)
    out.alpha_composite(bedonly)
    return out


# ---------------------------------------------------------------- cyclo
CW, CH = 64, 34


def cyclo(phase, facing="R"):
    O = (0, 2)
    def P(x, y): return (x + O[0], y + O[1])
    bike = new(CW, CH); per = new(CW, CH)
    rw, fw = P(10, 25), P(48, 25)
    for cx, cy in (rw, fw):
        for dy in range(-7, 8):
            for dx in range(-7, 8):
                if 5.0 < math.hypot(dx, dy) <= 6.45: put(bike, cx + dx, cy + dy, "ink")
        sp = ([(3, 0), (-3, 0), (0, 3), (0, -3), (2, 0), (-2, 0), (0, 2), (0, -2)] if phase % 2 == 0 else
              [(2, 2), (-2, -2), (2, -2), (-2, 2), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        for dx, dy in sp: put(bike, cx + dx, cy + dy, "grey")
        put(bike, cx, cy, "grey_l")
    bb = P(22, 25); seat = P(17, 15)
    for a, b in [(bb, seat), (seat, rw), (bb, rw), (bb, P(31, 22)), (P(31, 22), fw), (P(31, 22), P(31, 19))]:
        line(bike, a[0], a[1], b[0], b[1], "green_d")
    line(bike, *P(33, 20), *P(48, 20), "green_d"); line(bike, *P(46, 20), *fw, "green_d")
    rect(bike, *P(13, 14), *P(19, 14), "ink")
    ang = [0, 90, 180, 270][phase % 4] * math.pi / 180
    pf = (round(bb[0] + 3 * math.cos(ang)), round(bb[1] + 3 * math.sin(ang)))
    pb = (round(bb[0] - 3 * math.cos(ang)), round(bb[1] - 3 * math.sin(ang)))
    line(bike, *bb, *pf, "slate"); line(bike, *bb, *pb, "slate")
    # passenger carriage: seat, back, folded canopy
    rect(per, *P(32, 15), *P(48, 18), "red_d"); rect(per, *P(32, 14), *P(47, 15), "red"); line(per, *P(33, 14), *P(46, 14), "salmon")
    rect(per, *P(30, 5), *P(34, 15), "red"); line(per, *P(30, 5), *P(30, 15), "salmon")
    poly(per, [P(27, 4), P(36, 2), P(38, 8), P(33, 9), P(27, 9)], "plum"); line(per, *P(28, 4), *P(35, 2), "mauve")
    line(per, *P(29, 6), *P(36, 5), "bloom_k")
    rect(per, *P(48, 11), *P(49, 19), "slate_d")           # front guard
    rect(per, *P(32, 19), *P(46, 19), "slate_d")
    # driver
    hip = P(17, 14)
    kn = ik(hip, pb); thick(per, hip, kn, "navy"); thick(per, kn, pb, "navy"); rect(per, pb[0] - 1, pb[1], pb[0] + 2, pb[1], "ink")
    poly(per, [P(15, 5), P(21, 5), P(22, 8), P(20, 14), P(14, 14), P(13, 9)], "green")
    line(per, *P(14, 6), *P(13, 9), "green_l"); line(per, *P(20, 8), *P(20, 14), "green_d"); line(per, *P(14, 14), *P(20, 14), "green_d")
    thick(per, P(19, 7), P(26, 10), "green", "green_d"); put(per, *P(28, 10), "skin3"); put(per, *P(27, 10), "skin3")
    line(per, *P(27, 9), *P(31, 9), "ink")
    kn2 = ik(hip, pf); thick(per, hip, kn2, "slate"); thick(per, kn2, pf, "slate"); rect(per, pf[0] - 1, pf[1], pf[0] + 2, pf[1], "ink")
    rect(per, *P(17, 0), *P(21, 4), "skin2"); put(per, *P(21, 3), "skin3"); put(per, *P(20, 2), "brown_k")
    poly(per, [P(15, 2), P(17, 0), P(21, 0), P(23, 3), P(15, 3)], "green_l"); line(per, *P(15, 3), *P(23, 3), "green_d")   # nón cối pith helmet
    line(per, *P(17, 0), *P(20, 0), "mint")
    outl(per, "ink")
    im = new(CW, CH); im.alpha_composite(bike); im.alpha_composite(per)
    return im


if __name__ == "__main__":
    for f in "RL":
        fl = (lambda i: flip(i)) if f == "L" else (lambda i: i)
        save_asset(G, f"van_{f}", [fl(van(False, "R", w)) for w in (0, 1)], fps=12,
                   notes="Delivery box van, facing %s; 2 wheel frames @12fps. Light is upper-left only on R; L is a flip." % f)
        save_asset(G, f"van_quat_xuan_{f}", [fl(van_q("R", w)) for w in (0, 1)], fps=12,
                   notes="Open-bed truck loaded with 3 kumquat trees (Tet); facing %s." % f)
        save_asset(G, f"cyclo_{f}", [fl(cyclo(i)) for i in range(4)], fps=8,
                   notes="Xich lo: passenger carriage in front, driver pedalling behind; 4-frame pedal loop @8fps; facing %s." % f)
