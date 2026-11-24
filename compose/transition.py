"""Season-change transition for the montage (bản 6c): a gust of wind sweeps the next season in, left -> right.

    out = sweep(a, b, j, n, key_out, key_in)     # a, b: 1920x1080 RGB frames of the two seasons, j-th of n frames

* The front of the gust is a wavy vertical edge, computed per logical pixel (384x216) and blown up x5, so it stays a
  stepped pixel edge. Left of it (behind the gust) is already the new season.
* White wind streaks (1 logical px tall, head bright, tail fading in 4-px steps) ride on and just ahead of the front.
* Leaves / petals of the incoming season (actors/gust_leaf, gust_petal, recoloured) tumble along with the gust,
  bobbing up and down, and all of them have left the frame by the last transition frame.
Everything is deterministic in (j, n, key_in), so the montage renders the same every time.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.px_gif import RGB as PRGB  # noqa: E402

W, H, K = 384, 216, 5

# incoming season -> [(sprite, {neutral tone: season tone}, share)]
NEUTRAL = {"gust_leaf": ("leaf_l", "leaf", "leaf_d"), "gust_petal": ("bl_hl", "bl_l", "bl")}
GUST = {
    "xuan": [("gust_petal", ("bl_hl", "bl_l", "pk_l"), 0.75), ("gust_leaf", ("leaf_hl", "leaf_l", "leaf"), 0.25)],
    "ha": [("gust_petal", ("bl_l", "bl", "bl_d"), 0.55), ("gust_leaf", ("leaf_hl", "leaf_l", "leaf"), 0.45)],
    "mua": [("gust_leaf", ("leaf_l", "leaf", "leaf_d"), 0.8), ("gust_petal", ("bl_l", "bl", "bl_d"), 0.2)],
    "thu": [("gust_leaf", ("yl_l", "yl", "yl_d"), 0.55), ("gust_leaf", ("or_l", "or", "or_d"), 0.45)],
    "dong": [("gust_leaf", ("red_l", "red", "red_d"), 0.7), ("gust_leaf", ("or_l", "or", "or_d"), 0.3)],
}
NIGHT = {"dong": 0.72, "thu": 0.9}             # particles in a dark scene are dimmed a little


def _sprite(name):
    j = json.loads((ROOT / f"assets/out_gif/actors/{name}.json").read_text())
    strip = Image.open(ROOT / f"assets/out_gif/actors/{name}.png").convert("RGBA")
    fw, fh = j["frameW"], j["frameH"]
    return [np.asarray(strip.crop((i * fw, 0, (i + 1) * fw, fh))) for i in range(j["frames"])]


_CACHE: dict = {}


def particles_for(key_in):
    """Recoloured frames (blown up x5) for each particle kind of the incoming season."""
    if key_in not in _CACHE:
        kinds = []
        dim = NIGHT.get(key_in, 1.0)
        for name, tones, share in GUST[key_in]:
            frames = []
            for f in _sprite(name):
                f = f.copy()
                rgb = f[..., :3]
                for src, dst in zip(NEUTRAL[name], tones):
                    m = np.all(rgb == PRGB[src], axis=-1)
                    rgb[m] = np.array(PRGB[dst]) * dim
                frames.append(np.repeat(np.repeat(f, K, 0), K, 1))
            kinds.append((frames, share))
        _CACHE[key_in] = kinds
    return _CACHE[key_in]


def ease(u):
    return u * u * (3 - 2 * u)


def front_x(u):
    """Logical x of the gust front: from just off the left edge to just off the right edge."""
    return -34 + (W + 68) * ease(u)


def edge(u):
    """Per-row x of the wavy front (logical px), shape drifting as it moves."""
    y = np.arange(H)
    return (front_x(u) + 9 * np.sin(2 * np.pi * y / 64 + 2.1 + 4 * u) + 5 * np.sin(2 * np.pi * y / 21 + 0.7 - 7 * u)
            + 2.5 * np.sin(2 * np.pi * y / 9 + 11 * u))


def _blend(dst, x0, y0, img, alpha):
    """Alpha-blend img (h, w, 3) onto dst at output pixel (x0, y0), clipped."""
    h, w = img.shape[:2]
    xa, xb, ya, yb = max(0, x0), min(dst.shape[1], x0 + w), max(0, y0), min(dst.shape[0], y0 + h)
    if xa >= xb or ya >= yb:
        return
    sub = img[ya - y0:yb - y0, xa - x0:xb - x0]
    al = alpha[ya - y0:yb - y0, xa - x0:xb - x0, None] if np.ndim(alpha) else alpha
    d = dst[ya:yb, xa:xb].astype(np.float32)
    dst[ya:yb, xa:xb] = np.rint(d + (sub - d) * al).astype(np.uint8)


def sweep(a: np.ndarray, b: np.ndarray, j: int, n: int, key_out: str, key_in: str, seed: int = 0) -> np.ndarray:
    u = (j + 0.5) / n
    rng = np.random.default_rng(1000 + seed)
    # 1. the wipe: new season behind (left of) the wavy front
    xb = np.floor(edge(u)).astype(int)
    m = np.arange(W)[None, :] < xb[:, None]
    M = np.repeat(np.repeat(m, K, 0), K, 1)
    out = np.where(M[..., None], b, a).copy()
    # 2. a faint bright band riding on the front (the gust itself), 2 pixel steps
    for dx, k in ((6, 0.10), (2, 0.16)):
        band = (np.arange(W)[None, :] >= xb[:, None] - dx) & (np.arange(W)[None, :] < xb[:, None])
        B = np.repeat(np.repeat(band, K, 0), K, 1)
        o = out[B].astype(np.float32)
        out[B] = np.rint(o + (255 - o) * k * (0.7 if "dong" in (key_in, key_out) else 1.0)).astype(np.uint8)
    # 3. wind streaks
    env = np.sin(np.pi * u) ** 0.6
    night = 0.6 if "dong" in (key_in, key_out) else 1.0
    fx = front_x(u)
    for _ in range(36):
        y = int(rng.uniform(4, H - 12))
        d0, L = rng.uniform(-70, 14), int(rng.uniform(10, 36))
        v, al = rng.uniform(0, 50), rng.uniform(0.35, 0.7) * env * night
        head = fx + d0 + v * u
        step = 4
        for s in range(0, L, step):                      # fade from the head back to the tail, 4 px per step
            k = al * (1 - s / L)
            x1 = head - s
            x0 = x1 - step
            X0, X1 = int(round(x0 * K)), int(round(x1 * K))
            if X1 <= 0 or X0 >= W * K:
                continue
            seg = np.full((K, max(1, X1 - X0), 3), 255, np.float32)
            _blend(out, X0, y * K, seg, k)
    # 4. leaves / petals of the new season, carried by the gust
    kinds = particles_for(key_in)
    shares = np.array([s for _, s in kinds]); shares = shares / shares.sum()
    for _ in range(52):
        kind = rng.choice(len(kinds), p=shares)
        frames = kinds[kind][0]
        d = rng.uniform(-130, 20)
        v = rng.uniform(max(25.0, -10 - d), 150)              # every particle is off the right edge by u = 1
        y0 = rng.uniform(6, H - 18)
        amp, fq, ph = rng.uniform(2, 9), rng.uniform(0.6, 1.8), rng.uniform(0, 1)
        lift = rng.uniform(-6, 14)
        x = front_x(u) + d + v * u
        y = y0 + amp * np.sin(2 * np.pi * (fq * u + ph)) - lift * u
        fr = frames[(int(rng.integers(0, 4)) + j // 2) % len(frames)]      # tumbles at 6 fps
        X, Y = int(round(x * K)) - fr.shape[1] // 2, int(round(y * K)) - fr.shape[0] // 2
        _blend(out, X, Y, fr[..., :3].astype(np.float32), fr[..., 3].astype(np.float32) / 255)
    return out
