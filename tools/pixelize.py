"""Turn AI illustrations into true pixel art on a shared grid + shared palette.

    pal = build_palette([img1, img2], n=48)          # k-means palette shared by every layer
    px  = pixelize(img, (640, 360), pal)             # RGB(A) -> palette-locked pixels
    big = px.resize((1920, 1080), Image.NEAREST)
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter


def _thicken_lines(img: Image.Image, factor: float) -> Image.Image:
    """Darken-dilate thin dark linework so it survives the downscale (k ~ source px per target px)."""
    k = max(3, int(round(factor)) | 1)
    rgb = img.convert("RGB")
    mn = rgb.filter(ImageFilter.MinFilter(k))
    a = np.asarray(rgb).astype(np.float32)
    b = np.asarray(mn).astype(np.float32)
    lum_a = a.mean(-1, keepdims=True)
    lum_b = b.mean(-1, keepdims=True)
    # only pull in pixels that are much darker (outlines), keep fills
    w = np.clip((lum_a - lum_b - 40) / 60, 0, 1) * 0.65
    out = a * (1 - w) + b * w
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def build_palette(images: list[Image.Image], n: int = 48, seed: int = 0) -> Image.Image:
    """K-means (via PIL median-cut + refinement) palette over several images; returns a 'P' palette image."""
    samples = []
    for im in images:
        rgba = im.convert("RGBA")
        a = np.asarray(rgba)
        px = a[a[..., 3] > 128][:, :3]
        if len(px) > 200_000:
            px = px[np.random.default_rng(seed).choice(len(px), 200_000, replace=False)]
        samples.append(px)
    allpx = np.concatenate(samples).astype(np.uint8)
    side = int(np.ceil(np.sqrt(len(allpx))))
    pad = np.zeros((side * side - len(allpx), 3), np.uint8) + allpx[:1]
    tile = Image.fromarray(np.concatenate([allpx, pad]).reshape(side, side, 3), "RGB")
    return tile.quantize(colors=n, method=Image.Quantize.MAXCOVERAGE, kmeans=4)


def pixelize(img: Image.Image, size: tuple[int, int], palette: Image.Image | None = None,
             thicken: bool = True, sharpen: float = 0.6, alpha_cut: int = 128) -> Image.Image:
    """Downscale to `size` with box filtering, optionally line-thicken first, then lock to `palette`."""
    src = img.convert("RGBA")
    factor = src.width / size[0]
    rgb = _thicken_lines(src, factor) if thicken and factor >= 2 else src.convert("RGB")
    small = rgb.resize(size, Image.BOX)
    if sharpen:
        small = Image.blend(small, small.filter(ImageFilter.SHARPEN), sharpen)
    alpha = src.getchannel("A").resize(size, Image.BOX)
    if palette is not None:
        small = small.quantize(palette=palette, dither=Image.Dither.NONE).convert("RGB")
    out = small.convert("RGBA")
    a = np.asarray(alpha)
    o = np.asarray(out).copy()
    o[..., 3] = np.where(a >= alpha_cut, 255, 0)
    return Image.fromarray(o, "RGBA")
