import sys, pathlib, random, math; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *; from tools.layout import *; from tools.mockbg import mock_scene, place, save_mock

def mask_cloud(w, h, seed, nbumps, rmin, rmax, flat=True, hump=1.0):
    rr = random.Random(seed)
    m = [[False] * w for _ in range(h)]
    base = h - 1 - (2 if flat else 0)
    x = rmin
    i = 0
    while x < w - rmin:
        f = x / w
        prof = (math.sin(math.pi * f) ** .7) * hump
        r = int(rmin + (rmax - rmin) * prof * (0.2 + 0.8 * rr.random() ** 0.7))
        r = max(rmin, min(r, int(base * 0.68)))
        cy = base - int(r * .45)
        for yy in range(h):
            for xx in range(w):
                if ((xx - x) / (r * 1.05)) ** 2 + ((yy - cy) / r) ** 2 <= 1 and yy <= base: m[yy][xx] = True
        x += max(4, int(r * (0.9 + .5 * rr.random())))
    # solid flat base strip between bumps
    for xx in range(w):
        col = [yy for yy in range(h) if m[yy][xx]]
        if col:
            for yy in range(base - 3, base + 1): m[yy][xx] = True
    tops = [min([yy for yy in range(h) if m[yy][xx]] or [h]) for xx in range(w)]
    for xx in range(1, w - 1):
        if tops[xx] < h and tops[xx] < tops[xx - 1] and tops[xx] < tops[xx + 1]: m[tops[xx]][xx] = False
    return m, base

def shade(m, w, h, base, pal, ragged_bottom=False, seed=0):
    hi, mid, lo, deep = pal
    img = new(w, h)
    rr = random.Random(seed)
    for x in range(w):
        col = [y for y in range(h) if m[y][x]]
        if not col: continue
        top, bot = min(col), max(col)
        span = max(1, bot - top)
        for y in col:
            t = (y - top) / span
            # left-side lighter
            side = 0
            if x > 0 and not m[y][x - 1]: side = -1
            nbr_ul = (y > 0 and x > 0 and not m[y - 1][x - 1])
            if t < .45: col_ = hi
            elif t < .6: col_ = hi if (x + y) % 2 == 0 else mid
            elif t < .78: col_ = mid
            elif t < .9: col_ = mid if (x + y) % 2 == 0 else lo
            else: col_ = lo
            # lower-right edge falls into shade
            if (x + 1 < w and not m[y][x + 1] and t > .3) or (x + 2 < w and not m[y][x + 2] and t > .55): col_ = lo if col_ in (hi, mid) else deep
            if y == bot: col_ = deep
            if y == bot - 1 and col_ == lo: col_ = lo
            put(img, x, y, col_)
    if ragged_bottom:
        for x in range(w):
            col = [y for y in range(h) if img.getpixel((x, y))[3]]
            if col and rr.random() < .35:
                b = max(col)
                put(img, x, b + 1, "slate") if b + 1 < h and False else None
    return img

FAIR = ("white", "grey_l", "sky_l", "sky")
RAIN = ("grey", "slate", "slate_d", "navy")

def fair(name, w, h, seed, nb, rmin, rmax):
    m, base = mask_cloud(w, h, seed, nb, rmin, rmax)
    return shade(m, w, h, base, FAIR, seed=seed)

def rain(name, w, h, seed, nb, rmin, rmax):
    m, base = mask_cloud(w, h, seed, nb, rmin, rmax, hump=.9)
    img = shade(m, w, h, base, RAIN, seed=seed)
    # tattered underside: dithered strip of slate_d/navy below the flat base
    rr = random.Random(seed + 1)
    for x in range(w):
        for k in range(1, 3 + rr.randrange(0, 2)):
            y = base + k
            if y < h and BAYER4[y % 4][x % 4] < (9 - k * 4) + 0 and img.getpixel((x, base))[3]:
                put(img, x, y, "slate_d" if k == 1 else "navy")
    # light streak highlights on upper-left
    return img

if __name__ == "__main__":
    items = [
        ("cloud_l1", fair("cloud_l1", 120, 48, 3, 9, 6, 24), "large fair-weather cloud"),
        ("cloud_l2", fair("cloud_l2", 94, 38, 8, 7, 5, 18), "large fair-weather cloud, variant"),
        ("cloud_s1", fair("cloud_s1", 52, 22, 5, 5, 4, 10), "small fair-weather cloud"),
        ("cloud_s2", fair("cloud_s2", 40, 18, 12, 4, 4, 8), "small fair-weather cloud, variant"),
        ("cloud_rain1", rain("cloud_rain1", 230, 62, 4, 13, 8, 30), "wide storm cloud for the summer downpour"),
        ("cloud_rain2", rain("cloud_rain2", 190, 54, 9, 11, 8, 26), "wide storm cloud, variant"),
    ]
    for n, im, note in items:
        save_asset("env", n, im, anchor=(0, 0), notes=f"{note}. Top-left anchor; compositor scrolls horizontally in the sky layer. No opacity baked.")
    sheet = new(W, 150); rect(sheet, 0, 0, W - 1, 149, "sky"); rect(sheet, 0, 90, W - 1, 149, "sky_l")
    x = 4
    for n, im, _ in items:
        sheet.alpha_composite(im, (x if "rain" not in n else 4 + (0 if n.endswith("1") else 236), 4 if "rain" not in n else (64 if n.endswith("1") else 70))); x += im.width + 6 if "rain" not in n else 0
    save_mock(sheet, "env", "clouds_check", 3)
