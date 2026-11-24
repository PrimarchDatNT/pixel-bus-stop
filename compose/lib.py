"""Compositor helpers for still mockups (the Remotion engine will mirror this logic)."""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.layout import *  # noqa: E402,F401
from tools.px import OUT, RGB, dither, new, rect, vgradient  # noqa: E402


@lru_cache(maxsize=None)
def asset(group: str, name: str) -> tuple[Image.Image, dict]:
    meta = json.loads((OUT / group / f"{name}.json").read_text())
    strip = Image.open(OUT / group / f"{name}.png").convert("RGBA")
    return strip, meta


def frame(group: str, name: str, i: int = 0, state: str | None = None) -> tuple[Image.Image, dict]:
    strip, m = asset(group, name)
    if state:
        i = m["states"][state][i % len(m["states"][state])]
    i %= m["frames"]
    fw, fh = m["frameW"], m["frameH"]
    return strip.crop((i * fw, 0, (i + 1) * fw, fh)), m


class Scene:
    def __init__(self) -> None:
        self.img = new(W, H)

    def sky(self, stops: list[str], y1: int = BUILDING_BASE_Y, edges: list[int] | None = None) -> "Scene":
        """Banded pixel-art sky: solid bands with short 4-row Bayer transitions between them."""
        n = len(stops)
        edges = edges or [int(y1 * (k + 1) / n * 0.62) for k in range(n - 1)]  # bands crowd toward the top
        y = 0
        for k, col in enumerate(stops):
            yb = edges[k] if k < n - 1 else y1
            rect(self.img, 0, y, W - 1, yb, col)
            y = yb
        for k, e in enumerate(edges):
            for j, t in enumerate((0.25, 0.5, 0.75)):
                dither(self.img, 0, e - 1 + j, W - 1, e - 1 + j, stops[k], stops[k + 1], t)
        return self

    def fog(self, bands: list[tuple[int, int, float]], rgb=(206, 212, 226), seed: int = 0) -> "Scene":
        """Soft drifting fog: bands of (centre_y, half_height, max_alpha) with horizontal breakup."""
        a = np.asarray(self.img).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        al = np.zeros((H, W), np.float32)
        for k, (cy, hh, mx) in enumerate(bands):
            ph = seed * 1.7 + k * 2.3
            wob = 3 * np.sin(xx / 37 + ph) + 2 * np.sin(xx / 13 + ph * 2)
            dens = 0.65 + 0.35 * np.sin(xx / 53 + ph * 3) * np.sin(xx / 21 + ph)
            prof = np.exp(-(((yy - cy - wob) / hh) ** 2))
            al = np.maximum(al, prof * dens * mx)
        al = (np.round(al * 8) / 8)[..., None]  # quantised alpha keeps a stepped pixel feel
        a[..., :3] = a[..., :3] * (1 - al) + np.array(rgb, np.float32) * al
        self.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
        return self

    def at(self, group: str, name: str, x: int, y: int, i: int = 0, state: str | None = None,
           mode: str = "anchor", flip: bool = False) -> "Scene":
        """mode='anchor': (x,y) is where the asset's anchor lands. mode='tl': (x,y) is top-left."""
        f, m = frame(group, name, i, state)
        if flip:
            f = f.transpose(Image.FLIP_LEFT_RIGHT)
        if mode == "tl":
            ox, oy = x, y
        else:
            ax, ay = m["anchor"]
            if flip:
                ax = m["frameW"] - 1 - ax
            ox, oy = x - ax, y - ay
        self.img.alpha_composite(f, (ox, oy)) if ox >= 0 and oy >= 0 else self._paste_clip(f, ox, oy)
        return self

    def _paste_clip(self, f: Image.Image, ox: int, oy: int) -> None:
        cx, cy = max(0, -ox), max(0, -oy)
        f = f.crop((cx, cy, f.width, f.height))
        self.img.alpha_composite(f, (ox + cx, oy + cy))

    def shadow(self, x: int, y: int, w: int, h: int = 2, strength: float = 0.35) -> "Scene":
        """Soft ground shadow ellipse centred on (x, y)."""
        a = np.asarray(self.img).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        d = ((xx - x) / (w / 2)) ** 2 + ((yy - y) / max(1, h / 2)) ** 2
        m = (d <= 1.0)[..., None]
        a[..., :3] = np.where(m, a[..., :3] * (1 - strength), a[..., :3])
        self.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
        return self

    # --- grading (leaves the palette on purpose; final video does the same in canvas)
    def tint(self, rgb: tuple[int, int, int], mode: str = "multiply", amount: float = 1.0,
             y0: int = 0, y1: int = H) -> "Scene":
        a = np.asarray(self.img).astype(np.float32)
        t = np.array(rgb, np.float32)
        reg = a[y0:y1, :, :3]
        if mode == "multiply":
            out = reg * (t / 255.0)
        elif mode == "screen":
            out = 255 - (255 - reg) * (255 - t) / 255.0
        else:  # overlay-ish soft light
            out = reg + (t - 128) * 0.5
        a[y0:y1, :, :3] = reg * (1 - amount) + out * amount
        self.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
        return self

    def add_light(self, layer: Image.Image, amount: float = 0.8) -> "Scene":
        """Additive light layer (window glow, lamp pool)."""
        a = np.asarray(self.img).astype(np.float32)
        l = np.asarray(layer.convert("RGBA")).astype(np.float32)
        al = l[..., 3:4] / 255.0
        a[..., :3] = a[..., :3] + l[..., :3] * al * amount * 0.6
        self.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
        return self

    def overlay(self, layer: Image.Image, x: int = 0, y: int = 0, opacity: float = 1.0) -> "Scene":
        l = layer.copy()
        if opacity < 1:
            al = np.asarray(l).copy()
            al[..., 3] = (al[..., 3] * opacity).astype(np.uint8)
            l = Image.fromarray(al, "RGBA")
        self._paste_clip(l, x, y) if x < 0 or y < 0 else self.img.alpha_composite(l, (x, y))
        return self

    def tile(self, group: str, name: str, i: int = 0, opacity: float = 1.0, dx: int = 0, dy: int = 0) -> "Scene":
        f, _ = frame(group, name, i)
        layer = new(W, H)
        for yy in range(-f.height + dy % f.height, H, f.height):
            for xx in range(-f.width + dx % f.width, W, f.width):
                layer.alpha_composite(f, (xx, yy)) if xx >= 0 and yy >= 0 else _clip_paste(layer, f, xx, yy)
        return self.overlay(layer, opacity=opacity)

    def save(self, path: Path, scale: int = RENDER_SCALE) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.img.convert("RGB").resize((W * scale, H * scale), Image.NEAREST).save(path)
        return path


def _clip_paste(dst: Image.Image, f: Image.Image, ox: int, oy: int) -> None:
    cx, cy = max(0, -ox), max(0, -oy)
    if cx >= f.width or cy >= f.height:
        return
    dst.alpha_composite(f.crop((cx, cy, f.width, f.height)), (ox + cx, oy + cy))
