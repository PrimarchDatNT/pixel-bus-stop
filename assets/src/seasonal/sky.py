from common import *


def moon():
    S = 34
    img = new(S, S)
    cx = cy = S // 2
    px = img.load()
    R = 16
    ellipse(img, cx - R, cy - R, cx + R - 1, cy + R - 1, "ochre")
    ellipse(img, cx - R, cy - R, cx + R - 2, cy + R - 2, "glow")
    for y in range(S):
        for x in range(S):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if d <= R - 1.2:
                t = ((x - cx) + (y - cy)) / 22.0
                if t > 0.2 and BAYER4[y % 4][x % 4] < (t - 0.2) * 14:
                    px[x, y] = c("sand")
    # soft maria / craters
    for (x, y, r) in ((cx + 5, cy - 7, 3), (cx + 8, cy + 3, 2), (cx - 2, cy - 11, 2), (cx + 2, cy + 9, 2)):
        ellipse(img, x - r, y - r, x + r, y + r, "sand")
        ellipse(img, x - r + 1, y - r + 1, x + r, y + r, "ochre") if r > 2 else None
        put(img, x - r, y - r, "glow")
    # Chu Cuoi banyan: canopy + trunk with roots, ochre silhouette lower-left
    tx, ty = cx - 7, cy + 11
    ellipse(img, tx - 5, ty - 14, tx + 5, ty - 6, "ochre")
    ellipse(img, tx - 3, ty - 16, tx + 2, ty - 10, "ochre")
    ellipse(img, tx + 2, ty - 13, tx + 7, ty - 8, "ochre")
    put(img, tx - 3, ty - 12, "sand"); put(img, tx - 2, ty - 15, "sand")
    rect(img, tx - 1, ty - 6, tx + 1, ty, "skin3")      # trunk
    line(img, tx - 1, ty - 6, tx - 4, ty - 9, "skin3")  # branch
    line(img, tx + 1, ty - 6, tx + 3, ty - 9, "skin3")
    line(img, tx - 2, ty, tx - 3, ty + 1, "skin3"); line(img, tx + 2, ty, tx + 3, ty + 1, "skin3")
    # clip to the disc
    for y in range(S):
        for x in range(S):
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) > R - 0.4 and px[x, y][3] and px[x, y] in (c("skin3"), ):
                px[x, y] = CLEAR
    return img


LCOLS = {
    "red": ("red", "red_d", "salmon"), "gold": ("gold", "orange", "yellow"),
    "green": ("green_l", "green", "glow"), "blue": ("blue", "blue_d", "sky_l"),
    "pink": ("bloom_l", "bloom_d", "bloom_hl"), "orange": ("orange", "rust", "gold"),
}


def paper_lantern(img, x, y, kind, f, shape="round", glow=False):
    """x = centre, y = top of cap. ~7x9"""
    mid, dark, light = LCOLS[kind]
    # cap + hook
    rect(img, x - 1, y, x + 1, y, "brown_k")
    rect(img, x - 1, y + 1, x + 1, y + 1, "gold")
    # body
    if shape == "round":
        ellipse(img, x - 3, y + 2, x + 3, y + 8, dark)
        ellipse(img, x - 3, y + 2, x + 2, y + 7, mid)
        # ribs
        line(img, x, y + 2, x, y + 8, dark)
        # glow spot flicker
        put(img, x - 2, y + 3, light)
        put(img, x - 1 + (f if glow else 0), y + 4, light)
        if glow:
            put(img, x - 1, y + 5, light)
    else:  # tall barrel
        rect(img, x - 2, y + 2, x + 2, y + 9, mid)
        rect(img, x + 2, y + 2, x + 2, y + 9, dark)
        rect(img, x - 1, y + 3, x - 1, y + 4 + f, light)
        rect(img, x - 2, y + 5, x + 1, y + 5, dark) if False else None
        rect(img, x - 2, y + 6, x + 2, y + 6, dark)
    yb = y + (9 if shape == "round" else 10)
    rect(img, x - 1, yb, x + 1, yb, "gold")
    # tassel
    line(img, x, yb + 1, x, yb + 3, dark)
    put(img, x, yb + 3, "gold")


def lantern_string():
    Wd, Hd = 160, 24
    frames = []
    kinds = ["red", "gold", "green", "pink", "blue", "orange"]
    for f in range(2):
        img = new(Wd, Hd)
        sag = 6

        def wy(x):
            u = 2 * x / (Wd - 1) - 1
            return int(round(1 + sag * (1 - u * u)))
        for x in range(Wd):
            put(img, x, wy(x), "slate_d")
        # little bunting flags between lanterns? keep clean. lanterns every 11px
        k = 0
        for x in range(8, Wd - 4, 12):
            kind = kinds[k % len(kinds)]
            shape = "round" if k % 3 != 2 else "tall"
            glow = ((k + f) % 2 == 0)
            paper_lantern(img, x, wy(x) + 1, kind, f, shape, glow)
            k += 1
        # a fairy-light dot every few px along the wire, flickering
        for x in range(3, Wd, 6):
            if ((x // 6) + f) % 3 == 0:
                put(img, x, wy(x) + 1, "yellow")
        frames.append(img)
    return frames


if __name__ == "__main__":
    save_asset(G, "moon_full", moon(), anchor=(17, 17),
               notes="Clean full moon disc 33px (34x34), soft crater shading, Chu Cuoi banyan lower-left; NO halo (compositor blooms). anchor=centre. Thu night.")
    save_asset(G, "lantern_string_trungthu", lantern_string(), fps=3, anchor=(0, 0),
               notes="Multi-colour paper lanterns on sagging wire 160x24, 2-frame flicker, anchor TOP-LEFT (wire endpoints at x=0 and x=159, y=1). Between pole (x=52) / lamp (x=296) etc. Thu dusk/night; layer shelter_decor/lamp.")
