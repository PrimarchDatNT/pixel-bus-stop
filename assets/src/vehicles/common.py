import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *
from tools.layout import *
from tools.mockbg import mock_scene, place, save_mock

G = "vehicles"


def outl(img, name="ink", diag=False):
    """In-place 1px outline on transparent pixels touching opaque ones (keep a 1px canvas margin)."""
    w, h = img.size
    px = img.load()
    col = c(name)
    nb = [(-1, 0), (1, 0), (0, -1), (0, 1)] + ([(-1, -1), (1, -1), (-1, 1), (1, 1)] if diag else [])
    todo = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                continue
            for dx, dy in nb:
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and px[xx, yy][3]:
                    todo.append((x, y)); break
    for p in todo:
        px[p] = col


def disc(img, cx, cy, r, name, clip=None):
    px = img.load(); col = c(name)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.8 and 0 <= x < img.width and 0 <= y < img.height:
                if clip and not clip(x, y):
                    continue
                px[x, y] = col


def wheel(img, cx, cy, r, frame, rim="grey_l", rim_sh="grey", hubc="slate"):
    """Dark tyre + lighter rim/hub. frame 0: plus-shaped spokes, frame 1: x-shaped (spin read)."""
    disc(img, cx, cy, r, "ink")
    if r >= 5:
        disc(img, cx, cy, r - 1, "navy")      # tyre sidewall tone
    disc(img, cx, cy, r - 2, rim)
    # shade lower-right half of rim
    px = img.load()
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if 0 <= x < img.width and 0 <= y < img.height and px[x, y][:3] == RGB[rim] and (x - cx) + (y - cy) > 1:
                px[x, y] = c(rim_sh)
    if r >= 5:
        disc(img, cx, cy, r - 4, hubc)
    rr = max(1, r - 3)
    if frame % 2 == 0:
        pts = [(cx + rr, cy), (cx - rr, cy), (cx, cy + rr), (cx, cy - rr)]
    else:
        d = max(1, round(rr * 0.75))
        pts = [(cx + d, cy + d), (cx - d, cy - d), (cx + d, cy - d), (cx - d, cy + d)]
    for p in pts:
        put(img, p[0], p[1], "slate_d")
    put(img, cx, cy, "slate_d")
    if frame % 2 == 0:
        put(img, cx - 1, cy - 1, "white")
    else:
        put(img, cx + 1, cy - 1, "white")


def remap_cols(img, x0, x1, mapping, y0=0, y1=None):
    """Replace palette names within a column band (used to re-light flipped sprites)."""
    m = {RGB[k]: c(v) for k, v in mapping.items()}
    px = img.load()
    for y in range(y0, y1 if y1 is not None else img.height):
        for x in range(max(0, x0), min(img.width, x1)):
            p = px[x, y]
            if p[3] and p[:3] in m:
                px[x, y] = m[p[:3]]


def txt_x(facing, W, x0, x1):
    """Left x of a right-facing panel [x0,x1] after optional flip."""
    return x0 if facing == "R" else W - 1 - x1
