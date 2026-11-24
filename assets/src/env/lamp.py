import sys, pathlib, random; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *; from tools.layout import *; from tools.mockbg import mock_scene, place, save_mock

# lamp frame: scene x 288..323 (36 wide), y 90..171 (82 tall). pole centre x=LAMP_X
FX, FY, FW, FH = 288, 90, 36, 82
def S(x, y): return x - FX, y - FY

def build():
    img = new(FW, FH)
    px_, base = LAMP_X - FX, LAMP_BASE_Y - FY       # pole left col local; base row local
    top = 98 - FY
    # pole shaft 2px wide (light left), slight flare at the bottom
    for y in range(top, base + 1):
        put(img, px_, y, "slate"); put(img, px_ + 1, y, "slate_d")
    for y in range(base - 20, base + 1):
        put(img, px_ - 1, y, "slate"); put(img, px_ + 2, y, "navy")
    # base plate + collar
    rect(img, px_ - 3, base - 3, px_ + 4, base - 3, "slate_d")
    rect(img, px_ - 2, base - 2, px_ + 3, base, "slate"); rect(img, px_ + 2, base - 2, px_ + 3, base, "slate_d"); rect(img, px_ - 3, base, px_ + 4, base, "navy")
    put(img, px_ - 2, base - 2, "grey")
    # collar rings & a banner clip near the top
    for y in (top + 18, base - 26): rect(img, px_ - 1, y, px_ + 2, y, "slate_d")
    # curved arm: pole top bends to the right (quarter arc) then short horizontal
    arc = [(0, 0), (0, -1), (1, -2), (2, -3), (3, -3), (4, -4), (5, -4), (6, -4), (7, -4), (8, -4)]
    for dx, dy in arc:
        put(img, px_ + dx, top + dy, "slate"); put(img, px_ + dx + (1 if dy == 0 else 0), top + dy + 1 if dx > 1 else top + dy, "slate_d")
    # luminaire (cobra head), hanging at the arm end
    hx, hy = px_ + 8, top - 4
    rect(img, hx, hy, hx + 12, hy, "slate")                    # top cap
    rect(img, hx - 1, hy + 1, hx + 13, hy + 2, "grey")
    rect(img, hx - 1, hy + 1, hx + 6, hy + 1, "grey_l")
    rect(img, hx + 9, hy + 2, hx + 13, hy + 2, "slate")
    rect(img, hx, hy + 3, hx + 12, hy + 3, "slate_d")
    # lens (off state: pale)
    rect(img, hx + 1, hy + 4, hx + 11, hy + 4, "grey_l"); rect(img, hx + 1, hy + 4, hx + 4, hy + 4, "white")
    put(img, hx - 1, hy + 2, "slate"); put(img, hx + 13, hy + 1, "slate_d")
    # small sticker / tag on pole
    rect(img, px_, top + 30, px_ + 1, top + 31, "yellow")
    return img, (hx, hy)

def build_glow(head):
    # glow layer: scene x 262..357 (96), y 78..180 (103) - anchor top-left
    GX, GY, GW, GH = 262, 78, 96, 103
    g = new(GW, GH)
    hx = FX + head[0] + 6 - GX; hy = FY + head[1] + 4 - GY    # lens centre in glow coords
    # halo around head: concentric dithered rings
    for y in range(GH):
        for x in range(GW):
            d = ((x - hx) ** 2 + ((y - hy) * 1.05) ** 2) ** .5
            if d < 7: v = 15
            elif d < 11: v = 11
            elif d < 16: v = 7
            elif d < 22: v = 3
            else: v = 0
            if BAYER4[y % 4][x % 4] < v:
                put(g, x, y, "yellow" if d < 9 else "glow")
    # light cone: sparse dither widening toward the pavement
    pool_y = LAMP_BASE_Y + 4 - GY      # centre of pool on sidewalk
    for y in range(hy + 6, pool_y + 1):
        f = (y - hy - 6) / (pool_y - hy - 6)
        half = 4 + f * 26
        for x in range(int(hx - half), int(hx + half) + 1):
            if 0 <= x < GW:
                edge = abs(x - hx) / half
                v = round(3 * (1 - edge * .6) * (1 - f * .3))
                if BAYER4[y % 4][x % 4] < v and BAYER4[(y + 1) % 4][(x + 2) % 4] < 9: put(g, x, y, "glow")
    # pool on the sidewalk (flat ellipse, dithered 3 rings)
    cx = hx + 2
    for y in range(GH):
        for x in range(GW):
            d = (((x - cx) / 34) ** 2 + ((y - pool_y) / 6.5) ** 2) ** .5
            if d < .35: v = 12
            elif d < .65: v = 8
            elif d < 1.0: v = 4
            else: v = 0
            if v and (SIDE_Y0 - GY) <= y <= (SIDE_Y1 - GY) and BAYER4[y % 4][x % 4] < v:
                put(g, x, y, "yellow" if d < .35 else "glow")
    return g, (GX, GY)

SIDE_Y0, SIDE_Y1 = FAR_SIDEWALK_Y0, FAR_SIDEWALK_Y1

if __name__ == "__main__":
    lamp, head = build()
    save_asset("env", "lamp", lamp, anchor=(LAMP_X - FX, LAMP_BASE_Y - FY), notes=f"36x82. Place top-left at ({FX},{FY}) so pole base lands at ({LAMP_X},{LAMP_BASE_Y}). Lamp head ~y98-103, arm points RIGHT. Draw AFTER ground (ground plate would cover the pole foot).")
    lit = new(FW, FH)
    hx, hy = head
    for x in range(hx + 1, hx + 12): put(lit, x, hy + 4, "glow")
    for x in range(hx + 4, hx + 9): put(lit, x, hy + 4, "yellow")
    put(lit, hx + 6, hy + 4, "white")
    save_asset("env", "lamp_lit", lit, anchor=(LAMP_X - FX, LAMP_BASE_Y - FY), notes=f"36x82, same frame/position as lamp ({FX},{FY}). Emissive lens only (11 px row). Bulb centre scene coord = ({FX+hx+6},{FY+hy+4}). Compositor adds bloom.")
    print("bulb centre", FX + hx + 6, FY + hy + 4)
    bg = mock_scene(); g = pathlib.Path(".")
    bg.alpha_composite(lamp, (FX, FY)); bg.alpha_composite(lit, (FX, FY)); save_mock(bg, "env", "lamp_check")
