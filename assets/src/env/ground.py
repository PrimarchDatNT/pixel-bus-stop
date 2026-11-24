import sys, pathlib, random; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *; from tools.layout import *; from tools.mockbg import mock_scene, place, save_mock

GY = FAR_SIDEWALK_Y0  # 158 : top of the ground image
def L(y): return y - GY
GH = 112
R = random.Random(7)

def sidewalk_far(img, y0, y1):
    """small Hanoi square tiles, 5x4 incl joint, running-bond-ish, warm muted grey-red."""
    tw, th = 6, 4
    for ry, y in enumerate(range(y0, y1 + 1, th)):
        off = (ry % 2) * 3
        for x in range(-6, W + 6, tw):
            x_ = x + off
            r = R.random()
            base = "stone_l" if r < 0.94 else "grey_l"
            for yy in range(y, min(y + th, y1 + 1)):
                for xx in range(x_, x_ + tw):
                    if not (0 <= xx < W): continue
                    jx = (xx == x_ + tw - 1)
                    jy = (yy == y + th - 1)
                    if jx or jy: col = "grey"
                    else:
                        col = base
                    put(img, xx, yy, col)
    # warm "brick" tint tiles (muted red-brown joints stain) as sparse dither
    for _ in range(26):
        x = R.randrange(0, W - 4); y = R.randrange(y0 + 2, y1 - 1)
        pass

def sidewalk_near(img, y0, y1):
    tw, th = 12, 7
    for ry, y in enumerate(range(y0, y1 + 1, th)):
        off = (ry % 2) * 6
        for x in range(-12, W + 12, tw):
            x_ = x + off
            r = R.random()
            base = "stone_l" if r < 0.94 else "grey_l"
            for yy in range(y, min(y + th, y1 + 1)):
                for xx in range(x_, x_ + tw):
                    if not (0 <= xx < W): continue
                    if xx == x_ + tw - 1 or yy == y + th - 1: col = "grey"
                    else: col = base
                    put(img, xx, yy, col)
            # slight tile speckle

    # darker joint cross stays; add stains
    for _ in range(14):
        x = R.randrange(0, W - 6); y = R.randrange(y0 + 1, y1 - 2)
        pass

def curb(img, y0, y1, face_top_light=True):
    """4px granite face. rows: highlight, body, body, shadow."""
    rect(img, 0, y0, W - 1, y0, "grey_l" if False else "stone_l")
    rect(img, 0, y0 + 1, W - 1, y0 + 2, "stone")
    rect(img, 0, y1, W - 1, y1, "stone_d")
    x = R.randrange(4, 14)
    while x < W:
        for yy in range(y0, y1 + 1): put(img, x, yy, "stone_d" if yy > y0 else "stone")
        # slightly lighter block variation
        w = R.randrange(18, 30)
        if R.random() < .5:
            for xx in range(x + 1, min(W, x + w)):
                put(img, xx, y0 + 1, "stone_l") if R.random() < .3 else None
        x += w

def road(img, y0, y1):
    rect(img, 0, y0, W - 1, y1, "stone_d")
    # restrained speckle: lighter aggregate + cooler dark
    for _ in range(330):
        x = R.randrange(W); y = R.randrange(y0, y1 + 1)
        put(img, x, y, "stone" if R.random() < .5 else "slate_d")
    # tyre wear lanes: slightly darker horizontal bands in each lane (rubbed)
    for ly in (FAR_LANE_BASE_Y - 8, NEAR_LANE_BASE_Y - 8):
        for _ in range(160):
            x = R.randrange(W); y = ly + R.randrange(-6, 7)
            put(img, x, y, "navy")
    # gutter dirt row next to curbs
    for x in range(W):
        if R.random() < .6: put(img, x, y0, "stone")
        if R.random() < .6: put(img, x, y1, "stone")
    for x in range(W):
        if (x // 2 + R.randrange(3)) % 3 == 0: put(img, x, y0 + 1, "stone")
    # patched asphalt rectangles (slightly different tone, cooler)
    for (x, y, w, h) in [(300, 190, 40, 8), (40, 222, 34, 7), (400, 226, 24, 5)]:
        dither(img, x, y, x + w - 1, y + h - 1, "stone_d", "navy", .3)
        for xx in range(x, x + w):
            put(img, xx, y, "navy"); put(img, xx, y + h - 1, "stone")
    # cracks
    def crack(x, y, steps, dy_bias):
        for i in range(steps):
            put(img, x, y, "navy"); 
            r = R.random()
            if r < .55: x += 1
            elif r < .8: y += dy_bias
            else: x += 1; y += dy_bias
        return x, y
    crack(130, 193, 28, 1); crack(225, 228, 36, -1); crack(360, 201, 24, 1); crack(15, 215, 20, -1)
    # branch cracks
    crack(150, 198, 8, 1); crack(250, 220, 10, 1)
    # manhole cover (far lane) + sewer drain near curb
    mx, my = 86, 197
    ellipse(img, mx - 9, my - 3, mx + 9, my + 3, "stone_d")
    ellipse(img, mx - 8, my - 3, mx + 8, my + 3, "stone")
    ellipse(img, mx - 7, my - 2, mx + 7, my + 2, "slate_d")
    for i in range(-5, 6, 3): line(img, mx + i, my - 1, mx + i, my + 1, "stone")
    for x in range(mx - 8, mx + 4): put(img, x, my - 3, "stone_l") if x % 2 else None
    # second manhole (near lane, bigger as closer)
    mx, my = 332, 225
    ellipse(img, mx - 10, my - 3, mx + 10, my + 3, "stone")
    ellipse(img, mx - 9, my - 3, mx + 9, my + 3, "slate_d")
    ellipse(img, mx - 7, my - 2, mx + 7, my + 2, "stone_d")
    for i in range(-5, 6, 2): put(img, mx + i, my, "stone")
    put(img, mx - 8, my - 3, "stone_l")
    # storm drain grates on gutter
    for gx in (205, 410):
        rect(img, gx, y0 + 0, gx + 11, y0 + 2, "navy")
        for i in range(0, 12, 2): put(img, gx + i, y0 + 1, "stone_d")
    # lane divider dashes y=210..211, 12 on 10 off, worn
    for x in range(0, W, 22):
        for xx in range(x, min(W, x + 12)):
            for yy in (LANE_DIVIDER_Y, LANE_DIVIDER_Y + 1):
                col = "grey_l"
                if yy == LANE_DIVIDER_Y + 1: col = "grey"
                if R.random() < .1: continue
                put(img, xx, yy, col)
    # zebra-ish stop line? no. a faded bus stop marking "BUS" near the shelter, far lane
    text(img, 188, 193, "BUS", "stone")

def weed_crack(img):
    x, y = 360, 262
    for i, (dx, dy) in enumerate([(0,0),(1,0),(2,1),(3,1),(3,2),(4,2),(5,3),(6,3)]):
        put(img, x + dx, y + dy, "stone")
    put(img, x + 2, y - 1, "green"); put(img, x + 2, y - 2, "green_l"); put(img, x + 1, y - 2, "green_l"); put(img, x + 3, y - 2, "green")
    put(img, x + 2, y - 3, "green_l")
    # far sidewalk crack + weed
    for i, (dx, dy) in enumerate([(0,0),(1,0),(1,1),(2,1),(3,2),(4,2)]): put(img, 100 + dx, 172 + dy, "stone")
    put(img, 101, 171, "green"); put(img, 101, 170, "green_l")
    # leaf litter / gum spots
    for x, y in [(30, 262), (150, 256), (220, 266), (300, 248), (440, 258), (60, 250), (400, 247)]:
        put(img, x, y, "stone_d")

def build():
    img = new(W, 270)  # work in scene coords then crop
    sidewalk_far(img, FAR_SIDEWALK_Y0, FAR_SIDEWALK_Y1)
    # back edge: shadow of building base plinth on sidewalk (2 rows dithered)
    rect(img, 0, FAR_SIDEWALK_Y0, W - 1, FAR_SIDEWALK_Y0, "stone")
    rect(img, 0, FAR_SIDEWALK_Y0 + 1, W - 1, FAR_SIDEWALK_Y0 + 1, "grey")
    # front lip of sidewalk surface (lit edge)
    for x in range(W): put(img, x, FAR_SIDEWALK_Y1, "grey_l")
    curb(img, FAR_CURB_Y0, FAR_CURB_Y1)
    road(img, ROAD_Y0, ROAD_Y1)
    curb(img, NEAR_CURB_Y0, NEAR_CURB_Y1)
    sidewalk_near(img, NEAR_SIDEWALK_Y0, NEAR_SIDEWALK_Y1)
    for x in range(W): put(img, x, NEAR_SIDEWALK_Y0, "grey_l")
    weed_crack(img)
    return img.crop((0, GY, W, GY + GH))

def build_wet():
    img = new(W, 270)
    # wet sheen: short dark horizontal dashes
    for (x0, x1, y0, y1, col, n) in [(0, 479, 188, 205, "navy", 22), (0, 479, 213, 235, "navy", 26),
                                     (0, 479, 245, 268, "slate_d", 26), (0, 479, 160, 177, "stone_d", 20)]:
        for _ in range(n):
            x = R.randrange(x0, x1 - 12); y = R.randrange(y0, y1); w = R.randrange(4, 12)
            for i in range(w): put(img, x + i, y, col)
    # puddles: (cx, cy, rx, ry)
    P = [(120, 198, 22, 4), (270, 222, 30, 5), (400, 196, 16, 3), (80, 168, 12, 2), (350, 172, 14, 3), (200, 258, 28, 5), (430, 252, 22, 4)]
    for cx, cy, rx, ry in P:
        ellipse(img, cx - rx, cy - ry, cx + rx, cy + ry, "slate_d")
        ellipse(img, cx - rx + 1, cy - ry + 1 if ry > 2 else cy - ry, cx + rx - 1, cy + ry - 1 if ry > 2 else cy + ry, "slate")
        # sky reflection: band across upper portion
        for yy in range(cy - ry + 1, cy + 1):
            for xx in range(cx - rx + 2, cx + rx - 1):
                if img.getpixel((xx, yy))[:3] == RGB["slate"]:
                    put(img, xx, yy, "sky" if (xx + yy) % 2 == 0 or yy < cy else "sky_l")
        # highlights
        hy = cy - ry // 2
        for i in range(-rx // 2, rx // 3):
            put(img, cx + i, hy, "sky_l")
        put(img, cx - rx // 3, hy, "white"); put(img, cx - rx // 3 + 1, hy, "white")
        put(img, cx + rx // 3, cy, "white")
    return img.crop((0, GY, W, GY + GH))

if __name__ == "__main__":
    g = build()
    save_asset("env", "ground", g, anchor=(0, 0), notes="480x112 opaque ground plate. Place top-left at (0,158). Local y = scene y - 158. Bands per layout.py.")
    wet = build_wet()
    save_asset("env", "ground_wet", wet, anchor=(0, 0), notes="Overlay, same size/pos as ground (0,158). Puddles + sheen; show during/after rain.")
    bg = mock_scene(); bg.alpha_composite(g, (0, GY)); bg.alpha_composite(wet, (0, GY)); save_mock(bg, "env", "ground_check")
