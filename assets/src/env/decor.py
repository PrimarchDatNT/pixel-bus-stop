import sys, pathlib, random; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *; from tools.layout import *; from tools.mockbg import mock_scene, place, save_mock
import buildings as B

def flag(img, x, y):
    """pole top-left at (x,y): diagonal pole going down-left, flag flying right."""
    for k in range(6): put(img, x - k // 2 + 0, y + 5 - k if False else y + k, "slate_d")
    rect(img, x + 1, y, x + 7, y + 4, "red"); rect(img, x + 1, y + 4, x + 7, y + 4, "red_d")
    put(img, x + 4, y + 1, "yellow"); put(img, x + 3, y + 2, "yellow"); put(img, x + 4, y + 2, "yellow"); put(img, x + 5, y + 2, "yellow"); put(img, x + 4, y + 3, "yellow")
    put(img, x + 7, y + 1, "red_d"); put(img, x + 7, y + 3, "red_d")

def lantern(img, x, y, cols=("red", "red_d", "gold")):
    """hanging lantern, x = centre, y = top of string."""
    body, shade, trim = cols
    put(img, x, y, "brown_d")
    rect(img, x - 1, y + 1, x + 1, y + 1, trim)
    rect(img, x - 2, y + 2, x + 2, y + 5, body); rect(img, x + 1, y + 2, x + 2, y + 5, shade)
    put(img, x - 1, y + 3, "bloom_hl") if body == "red" else None
    rect(img, x - 1, y + 6, x + 1, y + 6, trim)
    put(img, x, y + 7, "gold"); put(img, x, y + 8, "gold")

def star(img, x, y, col, hl):
    for dx, dy in [(0, -2), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)]:
        put(img, x + dx, y + dy, col)
    put(img, x, y, hl); put(img, x - 1, y - 1, hl)

def xuan():
    B.build()
    img = new(W, B.BH)
    for i, (x0, x1, ry, y1) in enumerate(B.BALCONIES):
        flag(img, x1 - 3, ry - 7 if False else ry - 9)
        if i % 2 == 0: flag(img, x0 + 4, ry - 9)
    for (x, y, w, h, *_r) in B.SIGNS:
        lantern(img, x - 4, y - 1); lantern(img, x + w + 3, y - 1)
    # rows of small lanterns hanging from the shutter boxes between shops
    return img

def thu():
    B.build()
    img = new(W, B.BH)
    rr = random.Random(4)
    cols = [("red", "red_d", "gold"), ("gold", "orange", "red_d"), ("yellow", "gold", "red_d"), ("orange", "rust", "yellow")]
    for d in B.HOUSES:
        x0, x1 = d["x"] + 2, d["x"] + d["w"] - 3
        y0 = B.GF_TOP - 1
        pts = []
        for x in range(x0, x1 + 1):
            t = (x - x0) / (x1 - x0)
            y = round(y0 + 5 * 4 * t * (1 - t) * .55)
            put(img, x, y, "brown_d"); pts.append((x, y))
        for k, x in enumerate(range(x0 + 4, x1 - 2, 7)):
            y = pts[x - x0][1]
            body, shade, trim = cols[(k + d["x"] // 7) % 4]
            put(img, x, y + 1, trim); rect(img, x - 1, y + 2, x + 1, y + 4, body); put(img, x + 1, y + 3, shade); put(img, x + 1, y + 4, shade); put(img, x, y + 5, "gold")
    # star lanterns hanging from balconies
    for (x0, x1, ry, y1) in B.BALCONIES[::2]:
        line(img, x0 + 8, ry, x0 + 8, ry + 4, "brown_d"); star(img, x0 + 8, ry + 7, "red", "bloom_hl")
    return img

if __name__ == "__main__":
    a = xuan(); b = thu()
    save_asset("env", "buildings_decor_xuan", a, anchor=(0, 0), notes="Tet overlay on buildings (same size/pos (0,32)): flags on balconies + red lanterns beside shop signs.")
    save_asset("env", "buildings_decor_thu", b, anchor=(0, 0), notes="Mid-Autumn overlay (same size/pos (0,32)): lantern strings across shop fronts + star lanterns on balconies.")
    bg = new(W, H); rect(bg, 0, 0, W - 1, H - 1, "sky_l"); B.build(); bg.alpha_composite(Image.open(OUT / "env/buildings.png"), (0, 32)) if False else None
    from PIL import Image
    bg.alpha_composite(Image.open(OUT / "env/buildings.png").convert("RGBA"), (0, 32))
    s1 = bg.copy(); s1.alpha_composite(a, (0, 32)); s2 = bg.copy(); s2.alpha_composite(b, (0, 32))
    save_mock(s1.crop((0, 100, 480, 170)), "env", "decor_xuan_check", 3); save_mock(s2.crop((0, 100, 480, 170)), "env", "decor_thu_check", 3)
