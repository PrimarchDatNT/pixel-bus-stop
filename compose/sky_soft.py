"""Soft (non-pixel) sky, bản 6c: gradient + painted soft clouds at the OUTPUT size (x5 = 1920x1080).

The scene stays pixel art at 384x216. A soft cloud drawn at 384x216 and blown up x5 with nearest-neighbour would still
show 5x5 steps on its edge, so the sky is built at full size instead:

    hi  = gradient + moon glow + soft clouds, 1920x1080 (static, cached per season)
    lo  = hi box-averaged to 384x216; the compositor paints this as the sky layer and draws everything on top
    res = hi - up(lo)

`to_hi(frame, mask, key)` blows a finished 384x216 frame up x5 and adds `res` back only where the sky is still
visible (mask = logical pixels no sprite covered), so the scene keeps its hard pixels and the sky behind it is smooth.
Effects drawn after the mask (lamp glows, fog, rain) act on top of the sky, as before.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "compose"))
from tools.px_gif import RGB as PRGB  # noqa: E402
from seasons import SKY_GRAD, MOON_GLOW  # noqa: E402

W, H, K = 384, 216, 5
WH, HH = W * K, H * K


def col(c):
    if c.startswith("#"):
        return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], np.float64)
    return np.array(PRGB[c], np.float64)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# --------------------------------------------------------------------------------------------------- the clouds
# Same shapes and places as the old pixel skies (logical coords: centre x, centre y, radius x, radius y).
PUFF = ("cloud", "cloud_s", "cloud_d")
CLOUDS = {
    "ha": [("puff", [(318, 36, 9, 6), (331, 31, 10, 8), (346, 34, 9, 6), (358, 37, 7, 4), (326, 40, 20, 3), (344, 40, 18, 3)], PUFF),
           ("puff", [(106, 17, 6, 3), (116, 14, 6, 4), (126, 17, 5, 3), (114, 19, 14, 2)], PUFF),
           ("puff", [(262, 11, 4, 2), (270, 9, 4, 3), (278, 11, 4, 2), (270, 13, 9, 1)], PUFF),
           ("puff", [(40, 24, 4, 2), (46, 22, 4, 3), (53, 24, 3, 2), (47, 26, 8, 1)], PUFF)],
    "xuan": [("puff", [(40, 30, 10, 6), (55, 25, 11, 9), (72, 29, 10, 7), (86, 33, 8, 4), (60, 35, 26, 3)], PUFF),
             ("puff", [(300, 40, 9, 6), (316, 33, 12, 10), (333, 37, 10, 7), (349, 41, 8, 4), (322, 44, 26, 3)], PUFF),
             ("puff", [(176, 16, 6, 3), (186, 13, 6, 4), (196, 16, 5, 3), (186, 18, 14, 2)], PUFF),
             ("puff", [(360, 12, 4, 2), (367, 10, 4, 3), (374, 12, 4, 2)], PUFF)],
    "mua": [("rain", [(30, 30, 18, 9), (60, 24, 20, 12), (95, 32, 16, 8), (64, 38, 40, 5)], ("ov", "ov_d", "ov_k")),
            ("rain", [(170, 20, 16, 8), (200, 14, 20, 10), (232, 22, 16, 8), (204, 28, 40, 5)], ("ov", "ov_d", "ov_k")),
            ("rain", [(300, 34, 18, 10), (334, 26, 22, 13), (366, 36, 16, 8), (336, 44, 44, 5)], ("ov", "ov_d", "ov_k")),
            # a 4th one waiting just off the left edge at t = 0, so the drifting rain sky never thins out
            ("rain", [(-74, 22, 14, 7), (-50, 16, 17, 10), (-24, 24, 12, 6), (-48, 30, 34, 4)], ("ov", "ov_d", "ov_k"))],
    # streaks: (x, y, length, lit top colour, body colour), as skies.streak() drew them
    "thu": [("streak", (20, 64, 34), ("du_5", "du_3")), ("streak", (66, 58, 22), ("du_5", "du_3")),
            ("streak", (238, 96, 30), ("du_6", "du_4")), ("streak", (300, 104, 40), ("du_6", "du_4")),
            ("streak", (150, 40, 18), ("du_4", "du_2"))],
    "dong": [("streak", (30, 52, 30), ("nt", "nt_d")), ("streak", (140, 30, 22), ("nt", "nt_d")),
             ("streak", (250, 84, 36), ("nt_m", "nt"))],
}


def sd_ellipse(X, Y, cx, cy, rx, ry):
    """Approximate signed distance (logical px) to an ellipse: negative inside."""
    u = (X - cx) / rx
    v = (Y - cy) / ry
    d = np.sqrt(u * u + v * v)
    g = np.sqrt((u / rx) ** 2 + (v / ry) ** 2)
    ratio = np.where(g > 1e-9, d / np.maximum(g, 1e-9), min(rx, ry))
    return (d - 1.0) * ratio


def region(blobs, pad):
    """Output-pixel window around the blobs (NOT clipped to the canvas: clouds drift in and out of view).
    Gaussian tails reach about one radius past the rim, so pad by that."""
    px = pad + max(rx for cx, cy, rx, ry in blobs)
    py = pad + max(ry for cx, cy, rx, ry in blobs)
    x0 = min(cx - rx for cx, cy, rx, ry in blobs) - px
    x1 = max(cx + rx for cx, cy, rx, ry in blobs) + px
    y0 = min(cy - ry for cx, cy, rx, ry in blobs) - py
    y1 = max(cy + ry for cx, cy, rx, ry in blobs) + py
    X0, X1, Y0, Y1 = int(np.floor(x0 * K)), int(np.ceil(x1 * K)), int(np.floor(y0 * K)), int(np.ceil(y1 * K))
    ys = (np.arange(Y0, Y1) + 0.5) / K - 0.5          # output pixel centres in logical coordinates
    xs = (np.arange(X0, X1) + 0.5) / K - 0.5
    X, Y = np.meshgrid(xs, ys)
    return (Y0, X0), X, Y


def noise(shape, seed, cells=(6, 14, 30), amps=(0.6, 0.3, 0.15)):
    """Smooth value noise in [-1, 1] (a few octaves of upsampled random grids)."""
    from PIL import Image
    rng = np.random.default_rng(seed)
    h, w = shape
    out = np.zeros(shape)
    for c, a in zip(cells, amps):
        gh, gw = max(2, h * c // max(h, w) + 2), max(2, w * c // max(h, w) + 2)
        g = Image.fromarray((rng.random((gh, gw)) * 255).astype(np.uint8))
        out += a * (np.asarray(g.resize((w, h), Image.BICUBIC), np.float64) / 127.5 - 1)
    return out / sum(amps)


def bumps(blobs, seed):
    """The given ellipses + small round puffs along their upper rims, so the tops look fluffy (cumulus)."""
    rng = np.random.default_rng(seed)
    out = list(blobs)
    for cx, cy, rx, ry in blobs:
        if ry < 3:
            continue
        for _ in range(int(rx // 3)):
            a = rng.uniform(np.pi * 1.05, np.pi * 1.95)            # upper half of the ellipse
            r = rng.uniform(0.32, 0.5) * ry
            out.append((cx + np.cos(a) * rx * 0.78, cy + np.sin(a) * ry * 0.72, r * 1.1, r))
    return out


def density(X, Y, blobs):
    D = np.zeros_like(X)
    for cx, cy, rx, ry in blobs:                                 # gaussian blobs: D = 0.5 on the ellipse rim
        D += np.exp(-0.693 * (((X - cx) / (rx + 0.5)) ** 2 + ((Y - cy) / (ry + 0.5)) ** 2))
    return D


class Patch:
    """One cloud as a premultiplied RGBA patch at output size, placed at (y0, x0) at t = 0."""

    def __init__(self, y0, x0, rgb, a):
        rows, cols = np.nonzero(a > 1 / 1024)                      # trim the invisible gaussian tails
        r0, r1, c0, c1 = rows.min(), rows.max() + 1, cols.min(), cols.max() + 1
        self.a = a[r0:r1, c0:c1]
        self.prem = rgb[r0:r1, c0:c1] * self.a[..., None]
        self.y0, self.x0 = y0 + r0, x0 + c0
        self.h, self.w = self.a.shape


def puff(blobs, cols, seed, soft=(0.38, 0.6), rough=0.10, light=(1.3, 2.6), shade_k=0.75, base_k=0.55, haze=0.0):
    """A soft cumulus built from gaussian puffs: bright where it faces the sun (upper left), cooler in its own
    shadow and along the flat base, with a slightly ragged soft rim."""
    top, mid, bot = (col(c) for c in cols)
    blobs = bumps(blobs, seed)
    (y0, x0), X, Y = region(blobs, 6)
    n = noise(X.shape, seed)
    D = density(X, Y, blobs)
    Dn = D + rough * n * np.clip(1.4 - D, 0, 1)                  # roughen the rim only, not the core
    a = smoothstep(soft[0], soft[1], Dn)
    if haze:
        a = np.maximum(a, haze * smoothstep(0.06, soft[0], Dn))
    lx, ly = light
    occ = density(X - lx, Y - ly, blobs)                         # how much cloud sits between the pixel and the sun
    shade = smoothstep(0.35, 1.5, occ) * shade_k
    ytop = min(cy - ry for cx, cy, rx, ry in blobs)
    ybot = max(cy + ry for cx, cy, rx, ry in blobs)
    v = smoothstep(0.45, 1.0, np.clip((Y - ytop) / max(ybot - ytop, 1), 0, 1)) * base_k
    c = top + (mid - top) * shade[..., None]
    c = c + (bot - c) * v[..., None]
    return Patch(y0, x0, c, a)


def streak(x, y, n, cols, seed, soft=(0.3, 0.7)):
    """A thin lit cloud streak: a darker body with a brighter top edge, tapering and a little wispy at the ends."""
    top, body = col(cols[0]), col(cols[1])
    parts = [((x + 3 + (n + 1) / 2, y + 1.7, (n + 3) / 2 + 1, 1.15), body, 0.9),
             ((x + n / 2, y + 0.6, n / 2 + 1.5, 0.8), top, 0.95)]
    (y0, x0), X, Y = region([p[0] for p in parts], 5)               # one shared window for both parts
    prem, A = np.zeros(X.shape + (3,)), np.zeros(X.shape)
    for (cx, cy, rx, ry), c, al in parts:                           # body first, the lit top edge over it
        D = density(X, Y, [(cx, cy, rx, ry)]) + 0.12 * noise(X.shape, seed, cells=(4, 10, 24))
        a = smoothstep(soft[0], soft[1], D) * al
        prem = c * a[..., None] + prem * (1 - a[..., None])
        A = a + A * (1 - a)
        seed += 1
    return Patch(y0, x0, prem / np.maximum(A, 1e-9)[..., None], A)


def gradient(key):
    stops = SKY_GRAD[key]
    ys = np.array([p for p, _ in stops]) * (H - 1)
    cs = np.array([col(h) for _, h in stops])
    y = (np.arange(HH) + 0.5) / K - 0.5
    c = np.stack([np.interp(y, ys, cs[:, i]) for i in range(3)], axis=-1)
    a = np.repeat(c[:, None, :], WH, axis=1)
    if key in MOON_GLOW:
        cx, cy, r, hx, k = MOON_GLOW[key]
        yy, xx = np.mgrid[0:HH, 0:WH]
        d = np.hypot((xx + 0.5) / K - 0.5 - cx, (yy + 0.5) / K - 0.5 - cy)
        w = k * np.exp(-((d / r) ** 2) * 2.2)
        a += (col(hx) - a) * w[..., None]
    if key == "thu":                                          # the pixel full moon sits IN the sky (clouds pass in front)
        from PIL import Image
        m = np.asarray(Image.open(ROOT / "assets/out_gif/season/sky_thu_fg.png").convert("RGBA"), np.float64)
        m = up(m)
        al = m[..., 3:] / 255
        a = a * (1 - al) + m[..., :3] * al
    return a


# --------------------------------------------------------------------------- 6c (3): pixel "puff-cluster" clouds
# Client reference (opengameart 4_87): each cloud is a heap of overlapping round puffs drawn in hard pixels, shaded in
# 6-8 flat tones (sunlit caps on top, deeper tones toward the base), lower puffs overlapping the upper ones, and long
# thin stratus bars with stepped ends. Drawn at 384x216, blown up x5, and they drift over the smooth gradient sky.
CLOUD_STYLE = "pixel"            # "pixel" (reference style) or "soft" (painted soft clouds, CLOUDS above)

RAMPS = {   # bright cap -> shaded base
    "ha": ["#ffffff", "#f3f7fc", "#e2ebf6", "#cbdaec", "#b3c6de", "#9cb1cf"],
    "xuan": ["#fffcf2", "#fdf0dc", "#f7e0d0", "#ebcdc9", "#d6b9c6", "#bba6c0"],
    "mua": ["#bcc4cc", "#a9b2bc", "#96a0ac", "#848e9b", "#727c8a", "#626b79"],
    "thu": ["#f6f0d2", "#fde09c", "#fbc07a", "#f59c78", "#e07670", "#b25d74", "#7e526b", "#563f5c"],
    "dong": ["#3e4f84", "#36467a", "#2f3d6d", "#283460", "#212b53", "#1b2347"],
}
PIXEL_CLOUDS = {
    "ha": [("heap", [(318, 36, 9, 6), (331, 31, 10, 8), (346, 34, 9, 6), (358, 37, 7, 4), (326, 40, 20, 3), (344, 40, 18, 3)], {}),
           ("heap", [(106, 17, 6, 3), (116, 14, 6, 4), (126, 17, 5, 3), (114, 19, 14, 2)], {"rmax": 3.5}),
           ("heap", [(262, 11, 4, 2), (270, 9, 4, 3), (278, 11, 4, 2), (270, 13, 9, 1)], {"rmax": 3.0}),
           ("heap", [(40, 24, 4, 2), (46, 22, 4, 3), (53, 24, 3, 2), (47, 26, 8, 1)], {"rmax": 3.0})],
    "xuan": [("heap", [(40, 30, 10, 6), (55, 25, 11, 9), (72, 29, 10, 7), (86, 33, 8, 4), (60, 35, 26, 3)], {}),
             ("heap", [(300, 40, 9, 6), (316, 33, 12, 10), (333, 37, 10, 7), (349, 41, 8, 4), (322, 44, 26, 3)], {}),
             ("heap", [(176, 16, 6, 3), (186, 13, 6, 4), (196, 16, 5, 3), (186, 18, 14, 2)], {"rmax": 3.5}),
             ("heap", [(360, 12, 4, 2), (367, 10, 4, 3), (374, 12, 4, 2)], {"rmax": 3.0}),
             ("bar", (120, 52, 40), ("#ffffff", 0.35)), ("bar", (230, 60, 30), ("#ffffff", 0.3))],
    "mua": [("heap", [(30, 30, 18, 9), (60, 24, 20, 12), (95, 32, 16, 8), (64, 38, 40, 5)], {"rmax": 7.0}),
            ("heap", [(170, 20, 16, 8), (200, 14, 20, 10), (232, 22, 16, 8), (204, 28, 40, 5)], {"rmax": 7.0}),
            ("heap", [(300, 34, 18, 10), (334, 26, 22, 13), (366, 36, 16, 8), (336, 44, 44, 5)], {"rmax": 7.0}),
            ("heap", [(-74, 22, 14, 7), (-50, 16, 17, 10), (-24, 24, 12, 6), (-48, 30, 34, 4)], {"rmax": 6.0}),
            ("bar", (120, 58, 60), ("#5c6573", 0.45)), ("bar", (260, 66, 44), ("#5c6573", 0.4))],
    # Trung Thu: a sunset cumulus straight out of the reference, left of the moon, plus the stratus bars
    "thu": [("heap", [(34, 30, 12, 7), (52, 22, 13, 11), (72, 18, 11, 9), (90, 26, 11, 8), (62, 34, 34, 5)], {"rmax": 6.0}),
            ("heap", [(200, 30, 7, 4), (210, 26, 7, 5), (220, 30, 6, 4), (210, 33, 16, 2)], {"rmax": 4.0}),
            ("bar", (20, 64, 34), ("#f39c8c", 0.5)), ("bar", (66, 58, 22), ("#f39c8c", 0.45)),
            ("bar", (238, 96, 30), ("#ffc58f", 0.5)), ("bar", (300, 104, 40), ("#ffc58f", 0.5)),
            ("bar", (130, 46, 28), ("#d9799a", 0.45))],
    "dong": [("bar", (30, 52, 30), ("#43588f", 0.45)), ("bar", (140, 30, 22), ("#43588f", 0.4)),
             ("bar", (250, 84, 36), ("#43588f", 0.45))],
}


def sky_col_at(key, y):
    stops = SKY_GRAD[key]
    ys = np.array([p for p, _ in stops]) * (H - 1)
    cs = np.array([col(h) for _, h in stops])
    return np.array([np.interp(y, ys, cs[:, i]) for i in range(3)])


def heap(blobs, ramp, seed, rmin=3.0, rmax=6.5, light=1.6, jitter=0.25):
    """Pixel cumulus: round puffs inside the given ellipses (+ bumps along the top rim), drawn top to bottom so the
    lower, darker puffs overlap the sunlit ones. Each puff is one flat tone (set by its height in the cloud) with a
    round lit cap toward the upper left; a filled core underneath so the heap has no holes."""
    rng = np.random.default_rng(seed)
    ramp = np.array([col(c) for c in ramp])
    n_t = len(ramp)
    puffs = []
    for cx, cy, rx, ry in blobs:
        hi_r = min(rmax, max(rmin, ry + 1.5))
        for _ in range(max(2, int(np.pi * rx * ry / 26))):
            r = rng.uniform(rmin, hi_r)
            a, d = rng.uniform(0, 2 * np.pi), np.sqrt(rng.uniform(0, 1))
            puffs.append((cx + np.cos(a) * d * max(rx - r * 0.7, 0.5), cy + np.sin(a) * d * max(ry - r * 0.7, 0.5), r,
                          rng.uniform(-jitter, jitter)))
        if ry >= 2:
            for _ in range(max(2, int(rx / 4.5))):
                a = rng.uniform(np.pi * 1.1, np.pi * 1.9)
                r = rng.uniform(rmin, hi_r)
                puffs.append((cx + np.cos(a) * rx * 0.75, cy + np.sin(a) * ry * 0.75, r, rng.uniform(-jitter, jitter)))
    top = min(py - r for px, py, r, o in puffs)
    bot = max(py + r for px, py, r, o in puffs)
    x0 = int(np.floor(min(min(px - r for px, py, r, o in puffs), min(cx - rx for cx, cy, rx, ry in blobs)))) - 1
    x1 = int(np.ceil(max(max(px + r for px, py, r, o in puffs), max(cx + rx for cx, cy, rx, ry in blobs)))) + 2
    y0, y1 = int(np.floor(top)) - 1, int(np.ceil(bot)) + 2
    Y, X = np.mgrid[y0:y1, x0:x1].astype(np.float64)
    span = max(bot - top, 1)
    tone = np.full(X.shape, -1)
    core = np.zeros(X.shape, bool)
    for cx, cy, rx, ry in blobs:                                   # filled core, shaded by height only
        core |= ((X - cx) / (rx * 0.85 + 0.3)) ** 2 + ((Y - cy) / (ry * 0.85 + 0.3)) ** 2 <= 1
    tone[core] = np.clip(np.rint(np.clip((Y - top) / span, 0, 1) * (n_t - 1) + 0.3), 0, n_t - 1)[core]
    for px, py, r, off in sorted(puffs, key=lambda p: p[1]):
        inside = (X - px) ** 2 + (Y - py) ** 2 <= r * r
        base = np.clip((py - top) / span, 0, 1) * (n_t - 1)           # flat tone from the puff's height
        cap = np.hypot(X - (px - 0.3 * r), Y - (py - 0.45 * r)) / r - 0.6   # < 0 in the round lit cap
        t = base + np.clip(cap, -1, 0.5) * light + off
        tone[inside] = np.clip(np.rint(t), 0, n_t - 1)[inside]
    vt = np.clip(np.rint(np.clip((Y - top) / span, 0, 1) * (n_t - 1) + 0.3), 0, n_t - 1)
    for c in range(tone.shape[1]):                                 # close holes: fill each column between its ends
        rows = np.nonzero(tone[:, c] >= 0)[0]
        if len(rows):
            seg = tone[rows[0]:rows[-1] + 1, c]
            gap = seg < 0
            seg[gap] = vt[rows[0]:rows[-1] + 1, c][gap]
    tone = clean_orphans(tone)
    a = (tone >= 0).astype(np.float64)
    rgb = ramp[np.clip(tone, 0, n_t - 1)]
    return Patch(y0 * K, x0 * K, up(rgb), up(a))


def clean_orphans(tone, passes=2):
    """Pixel-art cleanup: a pixel whose tone matches none of its 4 neighbours takes the most common neighbour tone."""
    t = tone.copy()
    for _ in range(passes):
        p = np.pad(t, 1, constant_values=-1)
        nb = np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
        lone = (t >= 0) & np.all(nb != t, axis=0) & np.all(nb >= 0, axis=0)
        if not lone.any():
            break
        ys, xs = np.nonzero(lone)
        for y, x in zip(ys, xs):
            vals, cnt = np.unique(nb[:, y, x], return_counts=True)
            t[y, x] = vals[np.argmax(cnt)]
    return t


def bar(key, x, y, n, tint):
    """Thin stratus bar with stepped ends (2 rows, the lower one shifted right), flat colour: sky mixed with a tint."""
    c, k = tint
    rows = [(0, 0, n), (1, 5, n + 7)]
    w = n + 8
    a = np.zeros((2, w)); rgb = np.zeros((2, w, 3))
    for r, s0, s1 in rows:
        a[r, s0:s1] = 1
        rgb[r, s0:s1] = sky_col_at(key, y + r) * (1 - k) + col(c) * k
    return Patch(y * K, x * K, up(rgb), up(a))


def clouds(key):
    out = []
    if CLOUD_STYLE == "pixel":
        for i, (kind, spec, opt) in enumerate(PIXEL_CLOUDS.get(key, [])):
            if kind == "heap":
                out.append(heap(spec, RAMPS[key], seed=101 + i, **opt))
            else:
                out.append(bar(key, *spec, opt))
        return out
    for i, (kind, spec, cols) in enumerate(CLOUDS.get(key, [])):
        if kind == "puff":
            out.append(puff(spec, cols, seed=11 + i))
        elif kind == "rain":                                   # heavy grey rain clouds: softer, ragged, a little haze
            out.append(puff(spec, cols, seed=31 + i, soft=(0.28, 0.75), rough=0.22, light=(1.5, 3.5), shade_k=0.6,
                            base_k=0.7, haze=0.10))
        else:
            out.append(streak(*spec, cols, seed=51 + 2 * i))
    return out


def up(a):
    return np.repeat(np.repeat(a, K, axis=0), K, axis=1)


# ------------------------------------------------------------------------------------------------ drifting clouds
# The clouds drift slowly to the right and wrap around: each one leaves the right edge completely before it comes
# back in from the left. One full lap takes CLOUD_PERIOD seconds (5 x the 24 s loop), so a season clip is a seamless
# 120 s loop: everything else still repeats every 24 s, the clouds every 120 s. About 20 px/s at 1920x1080.
CLOUD_PERIOD = 120.0
FPS = 12
N_STEPS = int(CLOUD_PERIOD * FPS)


class Sky:
    def __init__(self, key):
        self.key = key
        self.grad = gradient(key)
        self.dither = np.random.default_rng(7).random(self.grad.shape)   # static dither so dark skies don't band
        self.patches = clouds(key)
        hi = np.clip(np.floor(self.grad + self.dither), 0, 255).astype(np.uint8)
        self.lo0 = self._lo(hi)
        self.res0 = hi.astype(np.int16) - up(self.lo0).astype(np.int16)
        if self.patches:                                          # rows the clouds can touch, on whole logical px
            b0 = max(0, min(p.y0 for p in self.patches) // K)
            b1 = min(H, -(-max(p.y0 + p.h for p in self.patches) // K))
            self.band = (b0, b1)
        self._last = (None, None)

    @staticmethod
    def _lo(hi):
        h = hi.shape[0] // K
        return np.rint(hi.reshape(h, K, W, K, 3).mean(axis=(1, 3))).astype(np.uint8)

    def place(self, p: Patch, step: int) -> int:
        """Left edge (output px) of patch p at a given frame step: a slow wrap-around drift to the right."""
        ring = WH + p.w
        shift = (step % N_STEPS) * ring // N_STEPS
        return (p.x0 + p.w + shift) % ring - p.w

    def at(self, t: float):
        """(lo uint8 HxWx3, res int16 HHxWHx3) of the sky at time t (cached for the last frame asked for)."""
        step = int(round(t * FPS)) % N_STEPS
        if self._last[0] == step:
            return self._last[1]
        if not self.patches:
            out = (self.lo0, self.res0)
        else:
            b0, b1 = self.band
            Y0, Y1 = b0 * K, b1 * K
            band = self.grad[Y0:Y1].copy()
            for p in self.patches:
                x = self.place(p, step)
                xa, xb = max(0, x), min(WH, x + p.w)
                ya, yb = max(Y0, p.y0), min(Y1, p.y0 + p.h)
                if xa >= xb or ya >= yb:
                    continue
                pa = p.a[ya - p.y0:yb - p.y0, xa - x:xb - x, None]
                pp = p.prem[ya - p.y0:yb - p.y0, xa - x:xb - x]
                dst = band[ya - Y0:yb - Y0, xa:xb]
                band[ya - Y0:yb - Y0, xa:xb] = dst * (1 - pa) + pp
            hb = np.clip(np.floor(band + self.dither[Y0:Y1]), 0, 255).astype(np.uint8)
            lo = self.lo0.copy(); lo[b0:b1] = self._lo(hb)
            res = self.res0.copy()
            res[Y0:Y1] = hb.astype(np.int16) - up(lo[b0:b1]).astype(np.int16)
            out = (lo, res)
        self._last = (step, out)
        return out

    def hi(self, t: float) -> np.ndarray:
        lo, res = self.at(t)
        return np.clip(up(lo).astype(np.int16) + res, 0, 255).astype(np.uint8)


_CACHE: dict = {}


def sky(key) -> Sky:
    if key not in _CACHE:
        _CACHE[key] = Sky(key)
    return _CACHE[key]


def to_hi(frame: np.ndarray, mask: np.ndarray | None, key: str, t: float) -> np.ndarray:
    """384x216 RGB frame at time t (+ sky-visible mask) -> 1920x1080 RGB with the smooth sky restored behind the pixels."""
    out = up(frame[..., :3])
    if mask is None or key not in SKY_GRAD:
        return out
    res = sky(key).at(t)[1]
    m = up(mask)
    o = out.astype(np.int16)
    o[m] += res[m]
    return np.clip(o, 0, 255).astype(np.uint8)


if __name__ == "__main__":                                    # preview: review/gif_style/_sky_soft/<key>.png
    from PIL import Image
    d = ROOT / "review/gif_style/_sky_soft"; d.mkdir(parents=True, exist_ok=True)
    for key in (sys.argv[1:] or list(SKY_GRAD)):
        for t in (0.0, 30.0, 60.0):
            Image.fromarray(sky(key).hi(t)).save(d / f"{key}_{int(t):03d}.png")
        print(d / f"{key}_000.png")
