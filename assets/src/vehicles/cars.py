from common import *
SW, SH = 72, 24
RAMPS = {  # hi, main, shade, deep
    "white": ("white", "white", "grey_l", "grey"),
    "red": ("salmon", "red", "red_d", "bloom_k"),
    "silver": ("white", "grey_l", "grey", "slate"),
}
WC = [(15, 18), (55, 18)]


def sedan(ramp, facing, wf, taxi=False):
    hi, mn, sh, dp = RAMPS[ramp]
    im = new(SW, SH)
    # silhouette
    poly(im, [(2, 19), (2, 12), (3, 10), (6, 9), (20, 9), (26, 2), (45, 2), (55, 8), (64, 9), (68, 11), (69, 13), (69, 19)], mn)
    rect(im, 5, 9, 63, 9, hi)
    line(im, 27, 2, 44, 2, hi)
    # shade lower body
    rect(im, 3, 16, 69, 19, sh)
    rect(im, 3, 19, 69, 19, dp)
    line(im, 3, 15, 69, 15, mn)
    # greenhouse
    poly(im, [(24, 9), (28, 3), (37, 3), (37, 9)], "slate_d")
    poly(im, [(40, 9), (40, 3), (44, 3), (52, 9)], "slate_d")
    poly(im, [(25, 8), (28, 4), (36, 4), (36, 8)], "blue_d")
    poly(im, [(41, 8), (41, 4), (44, 4), (50, 8)], "blue_d")
    rect(im, 25, 4, 26, 4, "sky") if False else None
    line(im, 31, 4, 29, 7, "sky"); line(im, 33, 4, 32, 6, "sky")
    line(im, 43, 4, 42, 6, "sky")
    # door seam, handle, sill
    line(im, 38, 10, 38, 17, sh); line(im, 56, 11, 56, 16, sh)
    rect(im, 34, 11, 35, 11, dp); rect(im, 43, 11, 44, 11, dp)
    # bumpers, lamps
    rect(im, 67, 17, 69, 19, "slate"); rect(im, 2, 17, 4, 19, "slate")
    rect(im, 66, 11, 69, 13, "glow"); put(im, 69, 13, "yellow")
    rect(im, 2, 11, 3, 13, "red_hot")
    rect(im, 63, 14, 64, 14, dp)
    # mirror
    rect(im, 52, 9, 54, 10, dp)
    if taxi:
        rect(im, 3, 14, 69, 14, "green"); rect(im, 3, 15, 69, 15, "green_d")
        rect(im, 4, 14, 8, 14, "green")
    for cx, cy in WC:
        disc(im, cx, cy, 7, "ink", clip=lambda x, y: y <= 19)
    outl(im, "ink")
    for cx, cy in WC:
        wheel(im, cx, cy, 5, wf)
    return im


def make(ramp, facing, wf, taxi=False):
    im = sedan(ramp, facing, wf, taxi)
    if taxi:
        big = new(SW, SH + 7)
        big.alpha_composite(im, (0, 7))
        # roof sign box: 17x7 above roof (x 28..44)
        rect(big, 28, 1, 44, 7, "white"); rect(big, 28, 7, 44, 7, "grey_l")
        rect(big, 29, 0, 43, 0, "white")
        rect(big, 31, 6, 41, 8, "slate_d") if False else None
        outl(big, "ink")
        im = big
    if facing == "L":
        im = flip(im)
    if taxi:
        tx = 28 if facing == "R" else SW - 1 - 44
        text(im, tx + 1, 2, "TAXI", "green_d")
    W = SW
    remap_cols(im, W - 4, W, {"white": "grey_l", "grey_l": "grey", "red": "red_d", "salmon": "red", "grey": "slate"} if not taxi else {"white": "grey_l"}, 0)
    return im


def car_lights(facing):
    ov = new(SW, SH)
    f = (lambda a, b: (SW - 1 - b, SW - 1 - a)) if facing == "L" else (lambda a, b: (a, b))
    hx0, hx1 = f(66, 69); tx0, tx1 = f(2, 3)
    rect(ov, hx0, 11, hx1, 13, "white"); rect(ov, tx0, 11, tx1, 13, "red_hot")
    d = -1 if facing == "L" else 1
    hxo = hx0 if facing == "L" else hx1
    # dithered headlight wedge hugging the ground ahead (stays inside the frame)
    for k in range(1, 3):
        for y in range(10 - k, 15 + k):
            x = hxo + d * k
            if 0 <= x < SW and BAYER4[y % 4][x % 4] < 9 - 2 * k:
                ov.putpixel((x, y), c("glow"))
    txo = tx0 if facing == "R" else tx1
    for k in range(1, 3):
        for y in range(10, 15):
            x = txo - d * k
            if 0 <= x < SW and BAYER4[y % 4][x % 4] < 8 - 2 * k:
                ov.putpixel((x, y), c("red"))
    return ov


if __name__ == "__main__":
    for name, ramp, taxi in [("sedan_white", "white", False), ("sedan_red", "red", False),
                             ("sedan_silver", "silver", False), ("taxi", "white", True)]:
        for f in "LR":
            save_asset(G, f"{name}_{f}", [make(ramp, f, 0, taxi), make(ramp, f, 1, taxi)], fps=12,
                       notes="Sedan, facing %s, 2 wheel frames @12fps%s." % ("left" if f == "L" else "right", "; 72x31 incl. roof sign" if taxi else ""))
    for f in "LR":
        save_asset(G, f"car_lights_{f}", car_lights(f), notes="Overlay 72x24 for sedan_*/ (taxi: paste at y+7); head/tail lights dithered.")
