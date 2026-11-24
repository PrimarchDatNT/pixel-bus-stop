from common import *

BW, BH = 170, 52
WIN_Y0, WIN_Y1 = 17, 30
TOP = 6                              # roof line (curved corners)
COMMON = [(30, 44), (47, 70), (89, 109), (112, 120)]
MIDDOOR, FRONTDOOR = 73, 123         # x0 of 14px doors (right-facing coords, doors side only)
WHEELS = [36, 152]
CY, R = 45, 6
PAX = {30: [(4, 0)], 47: [(5, 0), (14, 1)], 89: [(4, 0), (13, 0), (17, 1)], 112: [(3, 1)], 73: [(6, 1)], 123: [(5, 0)]}
FRONT_LED = (127, 147)
SIDE_LED = (92, 107)


def wins(doors_side):
    w = list(COMMON)
    if not doors_side:
        w += [(73, 86), (123, 136)]
    return sorted(w)


def slope_x(y):
    return int(148 + (y - TOP) * 0.68)


def glass(im, x0, y0, x1, y1, n=0):
    rect(im, x0, y0, x1, y1, "slate")
    rect(im, x0, y0, x1, y0 + 1, "grey")
    rect(im, x0, y1, x1, y1, "slate_d")
    line(im, x0 + 8, y0, x0 + 4, y0 + 4, "grey_l")
    line(im, x0 + 11, y0, x0 + 9, y0 + 2, "grey_l")


def passengers(im, wi, x0, y1=WIN_Y1):
    for ox, stand in PAX.get(x0, []):
        top = 19 if stand else 22
        col = "navy" if (ox % 2) else "slate_d"
        rect(im, x0 + ox, top, x0 + ox + 2, top + 2, col)          # head
        rect(im, x0 + ox - 1, top + 3, x0 + ox + 3, y1 - 1, col)   # shoulders/torso
        if stand:
            put(im, x0 + ox + 4, top + 3, "slate_d")               # arm to strap
            put(im, x0 + ox + 4, top + 2, "grey")


def door(im, x0, state):
    x1 = x0 + 13
    if state == 0:
        rect(im, x0, 16, x1, 45, "orange")
        for lx0, lx1 in ((x0 + 1, x0 + 6), (x0 + 8, x0 + 12)):
            rect(im, lx0, 17, lx1, 32, "gold")
            glass(im, lx0 + 1, 18, lx1 - 1, 30)
        line(im, x0 + 7, 16, x0 + 7, 45, "brown_d")
        put(im, x0 + 6, 38, "brown_d"); put(im, x0 + 8, 38, "brown_d")
        # lower livery inside door
        rect(im, x0 + 1, 33, x0 + 12, 34, "gold"); rect(im, x0 + 1, 35, x0 + 12, 35, "sand")
        rect(im, x0 + 1, 36, x0 + 12, 41, "red"); rect(im, x0 + 1, 42, x0 + 12, 43, "red_d")
        rect(im, x0 + 1, 44, x0 + 12, 45, "stone_d")
        line(im, x0 + 7, 17, x0 + 7, 45, "brown_d")
        return
    leaf = 3 if state == 1 else 1
    rect(im, x0, 16, x1, 45, "orange")
    rect(im, x0 + 1, 17, x1 - 1, 45, "navy")
    # interior: seat back silhouette + rail + steps
    rect(im, x0 + 1, 17, x1 - 1, 24, "slate_d")
    rect(im, x0 + 2, 31, x0 + 5, 40, "slate_d")
    line(im, x0 + 7, 17, x0 + 7, 42, "grey_l")
    rect(im, x0 + 1, 41, x1 - 1, 41, "stone")
    rect(im, x0 + 1, 42, x1 - 1, 43, "stone_l")
    rect(im, x0 + 1, 44, x1 - 1, 45, "stone_d")
    for lx0, lx1 in ((x0 + 1, x0 + leaf), (x1 - leaf, x1 - 1)):
        rect(im, lx0, 17, lx1, 40, "gold")
        rect(im, lx0, 18, lx1, 28, "slate")
        line(im, lx0, 18, lx0, 20, "grey_l")
        rect(im, lx0, 33, lx1, 40, "red")
        line(im, lx0, 17, lx1, 17, "yellow")


def build(facing="R", doors=0, wf=0, doors_side=True, stop=None):
    """doors: 0 closed/1 half/2 open (doors_side only). stop: None or blink 0/1 (brake + hazards)."""
    im = new(BW, BH)
    X0, X1 = 2, 164
    rect(im, X0, TOP, X1, 46, "gold")
    rect(im, X0, TOP, X1, TOP + 1, "yellow")
    rect(im, X0, 31, X1, 31, "orange")
    rect(im, X0, 35, X1, 35, "sand")
    rect(im, X0, 36, X1, 41, "red")
    rect(im, X0, 42, X1, 43, "red_d")
    rect(im, X0, 44, X1, 46, "stone_d")
    rect(im, X0, 44, X1, 44, "stone")
    # curved roof corners
    for y, (xa, xb) in {TOP: (10, 145), TOP + 1: (5, 149), TOP + 2: (3, 153)}.items():
        for x in range(X0, X1 + 1):
            if x < xa or x > xb:
                im.putpixel((x, y), CLEAR)
    # raked windscreen: clear everything ahead of the slope above the beltline
    for y in range(TOP, 32):
        for x in range(slope_x(y) + 1, X1 + 1):
            im.putpixel((x, y), CLEAR)
    # AC unit on the roof + antenna
    rect(im, 58, 1, 110, 5, "grey")
    rect(im, 59, 1, 109, 1, "grey_l")
    rect(im, 58, 5, 110, 5, "slate")
    for x in range(63, 108, 5):
        rect(im, x, 3, x, 4, "slate")
    for p in [(58, 1), (110, 1)]:
        im.putpixel(p, CLEAR)
    rect(im, 118, 3, 127, 5, "grey"); rect(im, 118, 3, 127, 3, "grey_l")
    line(im, 16, 0, 16, 5, "slate_d"); put(im, 16, 0, "red")
    # LED panels (text after flip)
    rect(im, FRONT_LED[0], 9, FRONT_LED[1], 15, "ink")
    rect(im, SIDE_LED[0], 9, SIDE_LED[1], 15, "ink")
    # rear engine louvres (replace the rear-most window)
    rect(im, 5, 17, 26, 30, "gold"); rect(im, 5, 17, 26, 17, "orange")
    rect(im, 6, 18, 25, 29, "brown_d")
    for y in range(19, 30, 2):
        line(im, 6, y, 25, y, "orange"); line(im, 6, y + 1, 25, y + 1, "rust") if y + 1 <= 29 else None
    for y in range(19, 30, 2):
        put(im, 6, y, "yellow")
    # windows
    for (a, b) in wins(doors_side):
        glass(im, a, WIN_Y0, b, WIN_Y1)
        passengers(im, 0, a)
        line(im, a + 8, WIN_Y0, a + 4, WIN_Y0 + 4, "grey_l") if b - a > 12 else None
        line(im, a + 11, WIN_Y0, a + 9, WIN_Y0 + 2, "grey_l") if b - a > 14 else None
    # big driver window, raked front edge, driver silhouette + wheel
    for y in range(WIN_Y0, WIN_Y1 + 1):
        xr = slope_x(y) - 2
        if y == WIN_Y0:
            line(im, 136, y, xr, y, "grey")
        else:
            line(im, 136, y, xr, y, "slate" if y < 29 else "slate_d")
        if y < WIN_Y0 + 3:
            line(im, 136, y, xr, y, "grey")
    rect(im, 144, 21, 146, 23, "navy"); rect(im, 143, 24, 147, 30, "navy"); put(im, 147, 22, "slate_d"); put(im, 143, 20, "navy")
    line(im, 149, 29, 153, 25, "ink"); line(im, 149, 30, 153, 26, "slate_d")        # steering wheel
    line(im, 147, 26, 150, 27, "navy")
    line(im, 148, 17, 141, 24, "grey_l"); line(im, 152, 17, 148, 21, "grey_l"); line(im, 143, 17, 140, 20, "grey_l")
    for y in range(WIN_Y0, WIN_Y1 + 1):
        put(im, slope_x(y) - 1, y, "gold") if y > 0 else None            # front pillar frame
    # mirror on stalk
    rect(im, 162, 22, 163, 28, "slate_d"); put(im, 162, 22, "grey"); line(im, 159, 23, 161, 23, "slate_d")
    # front: headlights, indicators, bumper
    hz = (stop is not None)
    rect(im, 161, 36, 164, 40, "glow"); put(im, 164, 40, "yellow"); line(im, 161, 41, 164, 41, "gold")
    rect(im, 162, 33, 164, 34, ("yellow" if (hz and stop == 0) else "orange"))
    rect(im, 160, 43, 166, 46, "stone_d"); rect(im, 160, 43, 166, 43, "stone")
    # rear: tail lights stacked + bumper
    if hz:
        rect(im, 2, 35, 4, 42, "red_hot"); put(im, 2, 35, "salmon"); rect(im, 2, 21, 3, 23, "red_hot")
        rect(im, 2, 31, 3, 32, "yellow" if stop == 0 else "orange")
    else:
        rect(im, 2, 37, 3, 41, "red_d"); rect(im, 2, 37, 3, 38, "red"); rect(im, 2, 21, 3, 23, "red_d")
        rect(im, 2, 31, 3, 32, "orange")
    rect(im, 2, 43, 4, 46, "stone_d"); rect(im, 2, 43, 4, 43, "stone")
    # doors
    if doors_side:
        door(im, MIDDOOR, doors)
        door(im, FRONTDOOR, doors)
    # arches + wheels
    for cx in WHEELS:
        disc(im, cx, CY, 8, "ink", clip=lambda x, y: y <= 46)
    outl(im, "brown_k")
    for cx in WHEELS:
        wheel(im, cx, CY, R, wf)
    if facing == "L":
        im = flip(im)
    fx = txt_x(facing, BW, *FRONT_LED); sx = txt_x(facing, BW, *SIDE_LED)
    text(im, fx + 3, 10, "32", "gold")
    for k in range(5):
        put(im, fx + 13 + k * 2, 12, "orange")
    text(im, sx + 4, 10, "32", "gold")
    edge = BW - 6
    remap_cols(im, edge, BW - 1, {"gold": "orange", "yellow": "gold", "red": "red_d", "sand": "gold"}, TOP, 47)
    return im


def lights(facing, doors_side):
    base = build(facing, 0, 0, doors_side)
    ov = new(BW, BH)
    flipf = (lambda a, b: (BW - 1 - b, BW - 1 - a)) if facing == "L" else (lambda a, b: (a, b))
    # interior window glow, dithered, skipping silhouettes
    sil = {RGB["slate_d"], RGB["navy"]}
    bp = base.load(); op = ov.load()
    for (a, b) in wins(doors_side) + [(138, 154)]:
        a2, b2 = flipf(a, b)
        for y in range(WIN_Y0, WIN_Y1 + 1):
            for x in range(a2, b2 + 1):
                if bp[x, y][3] == 0 or bp[x, y][:3] not in {RGB["slate"], RGB["grey"], RGB["grey_l"]}:
                    continue
                if BAYER4[y % 4][x % 4] < 7:
                    op[x, y] = c("glow") if y % 2 == 0 else c("yellow")
    for dx0, dx1 in (FRONT_LED, SIDE_LED):
        a2, b2 = flipf(dx0, dx1)
        rect(ov, a2, 9, b2, 15, "ink")
        text(ov, a2 + (3 if dx0 == FRONT_LED[0] else 4), 10, "32", "yellow")
        if dx0 == FRONT_LED[0]:
            for k in range(5):
                put(ov, a2 + 13 + k * 2, 12, "gold")
    # headlight + halo, taillight + halo
    hx0, hx1 = flipf(162, 164); tx0, tx1 = flipf(2, 3)
    rect(ov, hx0, 37, hx1, 40, "white")
    fwd = -1 if facing == "L" else 1
    hxo = hx0 if facing == "L" else hx1
    for k in range(1, 4):
        for y in range(36 - k, 42 + k):
            x = hxo + fwd * k
            if 0 <= x < BW and BAYER4[y % 4][x % 4] < 9 - 2 * k:
                op[x, y] = c("glow")
    rect(ov, tx0, 37, tx1, 41, "red_hot")
    bk = -fwd
    txo = tx0 if facing == "R" else tx1
    for k in range(1, 3):
        for y in range(37 - k, 42 + k):
            x = txo + bk * k
            if 0 <= x < BW and BAYER4[y % 4][x % 4] < 8 - 2 * k:
                op[x, y] = c("red")
    # ground-ish light spill under the front, dithered
    return ov


if __name__ == "__main__":
    for f in "LR":
        ds = (f == "R")
        if ds:
            fr = [build(f, 0, 0), build(f, 0, 1), build(f, 1, 0), build(f, 2, 0), build(f, 0, 0, True, 0), build(f, 0, 1, True, 1)]
            st = {"drive": [0, 1], "doors_open": [2, 3], "stop": [4, 5]}
            extra = "Frames 2-3 doors_open: 2=half, 3=full (play 2 then hold 3; reverse to close). Doors on this (right) side. Front door centre x=%d, mid door centre x=%d. " % (FRONTDOOR + 7, MIDDOOR + 7)
        else:
            fr = [build(f, 0, 0, False), build(f, 0, 1, False), build(f, 0, 0, False, 0), build(f, 0, 1, False, 1)]
            st = {"drive": [0, 1], "stop": [2, 3]}
            extra = "No doors (camera sees driver's side). Front-left end: raked windscreen with driver, LED sign above, headlights; rear: louvres + small window + taillights. "
        extra += "stop = brake lights on + hazard blink (alternates each frame; use ~3fps). Frames 0-1 drive (wheel spin 12fps). Facing %s." % ("left" if f == "L" else "right")
        save_asset(G, f"bus_{f}", fr, fps=12, states=st, notes=extra)
        save_asset(G, f"bus_lights_{f}", lights(f, ds), notes="Overlay, same frame size as bus_%s: window glow (dithered), lit LED, head/tail lights" % f)
