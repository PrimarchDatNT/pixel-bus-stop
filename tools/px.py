"""Shared pixel-art toolkit. Every asset script imports this:

    import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
    from tools.px import *
    from tools.layout import *

Rules enforced here: palette-only colors, alpha strictly 0 or 255, 1x logical pixels.
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "out"
PREVIEW_SCALE = 4

# ---------------------------------------------------------------- palette
# Endesga 32 + 13 project extras (bougainvillea ramp, warm stone, sky, lamp glow, wall paints).
PALETTE: dict[str, str] = {
    # skin / browns
    "skin1": "#e8b796", "skin2": "#e4a672", "skin3": "#c28569", "skin4": "#b86f50",
    "brown_d": "#733e39", "brown_k": "#3e2731",
    # warm
    "rust": "#be4a2f", "clay": "#d77643", "sand": "#ead4aa",
    "red_d": "#a22633", "red": "#e43b44", "red_hot": "#ff0044",
    "orange": "#f77622", "gold": "#feae34", "yellow": "#fee761",
    # greens / teal
    "green_l": "#63c74d", "green": "#3e8948", "green_d": "#265c42", "teal_k": "#193c3e",
    "mint": "#7fb7a4",
    # blues / greys
    "blue_d": "#124e89", "blue": "#0099db", "cyan": "#2ce8f5",
    "white": "#ffffff", "grey_l": "#c0cbdc", "grey": "#8b9bb4",
    "slate": "#5a6988", "slate_d": "#3a4466", "navy": "#262b44", "ink": "#181425",
    "sky_l": "#8fd3f4", "sky": "#5bb3e6",
    # purples / pinks
    "plum": "#68386c", "mauve": "#b55088", "salmon": "#f6757a",
    # bougainvillea ramp (dark -> highlight)
    "bloom_k": "#5e1a4a", "bloom_d": "#a3246e", "bloom": "#d93a8c",
    "bloom_l": "#f26db1", "bloom_hl": "#ffb3dc",
    # warm stone (concrete, asphalt, curbs)
    "stone_l": "#a8a29a", "stone": "#77716b", "stone_d": "#4d4945",
    # misc
    "glow": "#ffe9a8", "ochre": "#e8c170",
}


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


RGB: dict[str, tuple[int, int, int]] = {k: _hex(v) for k, v in PALETTE.items()}
_ALLOWED = set(RGB.values())
CLEAR = (0, 0, 0, 0)


def c(name: str) -> tuple[int, int, int, int]:
    """Palette name -> RGBA tuple. Raises KeyError on unknown names (on purpose)."""
    return (*RGB[name], 255)


# ---------------------------------------------------------------- canvas helpers
def new(w: int, h: int) -> Image.Image:
    return Image.new("RGBA", (w, h), CLEAR)


def grid(rows: list[str], legend: dict[str, str]) -> Image.Image:
    """Build a sprite from ASCII rows. '.' and ' ' are transparent; other chars map via legend."""
    h = len(rows)
    w = max(len(r) for r in rows)
    img = new(w, h)
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in ". ":
                continue
            px[x, y] = c(legend[ch])
    return img


def put(img: Image.Image, x: int, y: int, name: str) -> None:
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c(name))


def rect(img: Image.Image, x0: int, y0: int, x1: int, y1: int, name: str) -> None:
    """Filled rectangle, inclusive corners."""
    ImageDraw.Draw(img).rectangle([x0, y0, x1, y1], fill=c(name))


def line(img: Image.Image, x0: int, y0: int, x1: int, y1: int, name: str) -> None:
    ImageDraw.Draw(img).line([x0, y0, x1, y1], fill=c(name), width=1)


def ellipse(img: Image.Image, x0: int, y0: int, x1: int, y1: int, name: str) -> None:
    ImageDraw.Draw(img).ellipse([x0, y0, x1, y1], fill=c(name))


def poly(img: Image.Image, pts: list[tuple[int, int]], name: str) -> None:
    ImageDraw.Draw(img).polygon(pts, fill=c(name))


def paste(dst: Image.Image, src: Image.Image, x: int, y: int) -> None:
    """Alpha-paste (hard alpha, so the result stays palette-clean)."""
    dst.alpha_composite(src, (x, y))


BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def dither(img: Image.Image, x0: int, y0: int, x1: int, y1: int, a: str, b: str, t: float) -> None:
    """Ordered (Bayer 4x4) mix of colors a and b over a rect; t=0 -> all a, t=1 -> all b."""
    pa, pb = c(a), c(b)
    px = img.load()
    for y in range(max(0, y0), min(img.height, y1 + 1)):
        for x in range(max(0, x0), min(img.width, x1 + 1)):
            px[x, y] = pb if BAYER4[y % 4][x % 4] < t * 16 else pa


def vgradient(img: Image.Image, x0: int, y0: int, x1: int, y1: int, stops: list[str]) -> None:
    """Vertical dithered gradient across a list of palette colors (top -> bottom)."""
    n = len(stops) - 1
    hgt = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        f = (y - y0) / hgt * n
        i = min(int(f), n - 1)
        dither(img, x0, y, x1, y, stops[i], stops[i + 1], f - i)


def outline(img: Image.Image, name: str, diagonal: bool = False) -> Image.Image:
    """Return a copy with a 1px outline drawn OUTSIDE opaque pixels (canvas grows by 1px each side)."""
    w, h = img.size
    out = new(w + 2, h + 2)
    src = new(w + 2, h + 2)
    src.paste(img, (1, 1))
    sp, op = src.load(), out.load()
    col = c(name)
    nbrs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonal:
        nbrs += [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for y in range(h + 2):
        for x in range(w + 2):
            if sp[x, y][3]:
                continue
            for dx, dy in nbrs:
                xx, yy = x + dx, y + dy
                if 0 <= xx < w + 2 and 0 <= yy < h + 2 and sp[xx, yy][3]:
                    op[x, y] = col
                    break
    out.alpha_composite(src)
    return out


def flip(img: Image.Image) -> Image.Image:
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def recolor(img: Image.Image, mapping: dict[str, str]) -> Image.Image:
    """Palette swap: {'red': 'blue', ...}."""
    m = {RGB[k]: c(v) for k, v in mapping.items()}
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            p = px[x, y]
            if p[3] and p[:3] in m:
                px[x, y] = m[p[:3]]
    return out


# ---------------------------------------------------------------- tiny pixel font (3x5 caps + Vietnamese marks)
_G = {
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": [".##", "#..", "#..", "#..", ".##"], "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"], "F": ["###", "#..", "##.", "#..", "#.."],
    "G": [".##", "#..", "#.#", "#.#", ".##"], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"], "J": ["..#", "..#", "..#", "#.#", ".#."],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"], "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"], "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."], "P": ["##.", "#.#", "##.", "#..", "#.."],
    "Q": [".#.", "#.#", "#.#", "##.", ".##"], "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."], "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"], "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"], "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."], "Z": ["###", "..#", ".#.", "#..", "###"],
    "Đ": [".##.", ".#.#", "####", ".#.#", ".##."],
    "0": ["###", "#.#", "#.#", "#.#", "###"], "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["##.", "..#", ".#.", "#..", "###"], "3": ["##.", "..#", ".#.", "..#", "##."],
    "4": ["#.#", "#.#", "###", "..#", "..#"], "5": ["###", "#..", "##.", "..#", "##."],
    "6": [".##", "#..", "###", "#.#", "###"], "7": ["###", "..#", ".#.", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"], "9": ["###", "#.#", "###", "..#", "##."],
    " ": ["..", "..", "..", "..", ".."], "-": ["...", "...", "###", "...", "..."],
    ".": [".", ".", ".", ".", "#"], ":": [".", "#", ".", "#", "."], "!": ["#", "#", "#", ".", "#"],
    "/": ["..#", "..#", ".#.", "#..", "#.."],
}
_MARK_ABOVE_VOWEL = {"̂": [".#.", "#.#"], "̆": ["#.#", ".#."]}  # circumflex, breve
_MARK_TONE = {"̀": ["#.", ".#"], "́": [".#", "#."], "̉": ["##", ".#"], "̃": [".#.#", "#.#."]}
_DOT_BELOW, _HORN = "̣", "̛"
FONT_ASC = 5   # rows reserved above caps for marks
FONT_H = 5     # cap height
FONT_DESC = 2  # rows below for dot-below


def _char_parts(ch: str):
    if ch.upper() == "Đ":
        return "Đ", [], False, False
    d = unicodedata.normalize("NFD", ch.upper())
    base, marks = d[0], d[1:]
    vowel = [_MARK_ABOVE_VOWEL[m] for m in marks if m in _MARK_ABOVE_VOWEL]
    tone = [_MARK_TONE[m] for m in marks if m in _MARK_TONE]
    return base, vowel + tone, _DOT_BELOW in marks, _HORN in marks


def text_size(s: str, scale: int = 1) -> tuple[int, int]:
    w = 0
    for ch in s:
        base, _, _, horn = _char_parts(ch)
        w += len(_G.get(base, _G[" "])[0]) + (1 if horn else 0) + 1
    return (max(0, w - 1) * scale, (FONT_ASC + FONT_H + FONT_DESC) * scale)


def text(img: Image.Image, x: int, y: int, s: str, name: str, scale: int = 1) -> int:
    """Draw Vietnamese-capable caps text. (x, y) is the TOP of the cap height (marks go above y).
    Returns drawn width. Use scale=2..3 for titles."""
    col = c(name)
    px = img.load()

    def dot(xx, yy):
        for sy in range(scale):
            for sx in range(scale):
                X, Y = x + (xx) * scale + sx, y + yy * scale + sy
                if 0 <= X < img.width and 0 <= Y < img.height:
                    px[X, Y] = col

    cx = 0
    for ch in s:
        base, marks, dotb, horn = _char_parts(ch)
        g = _G.get(base, _G[" "])
        gw = len(g[0])
        for gy, row in enumerate(g):
            for gx, v in enumerate(row):
                if v == "#":
                    dot(cx + gx, gy)
        top = -1  # leave a 1-row gap above caps
        for m in marks:
            mh, mw = len(m), len(m[0])
            off = (gw - mw) // 2
            for my, row in enumerate(m):
                for mx, v in enumerate(row):
                    if v == "#":
                        dot(cx + off + mx, top - mh + my)
            top -= mh
        if dotb:
            dot(cx + gw // 2, FONT_H + 1)
        if horn:
            dot(cx + gw, -1)
            dot(cx + gw, 0)
            gw += 1
        cx += gw + 1
    return max(0, cx - 1) * scale


# ---------------------------------------------------------------- validation + export
def validate(img: Image.Image, label: str = "") -> None:
    bad_alpha, bad_col = 0, set()
    for r, g, b, a in img.getdata():
        if a not in (0, 255):
            bad_alpha += 1
        elif a == 255 and (r, g, b) not in _ALLOWED:
            bad_col.add("#%02x%02x%02x" % (r, g, b))
    if bad_alpha or bad_col:
        raise ValueError(f"[{label}] palette violation: {bad_alpha} semi-transparent px, "
                         f"off-palette colors {sorted(bad_col)[:10]}")


def _preview_bg(w: int, h: int) -> Image.Image:
    bg = Image.new("RGBA", (w, h), (*RGB["grey_l"], 255))
    return bg


def save_asset(group: str, name: str, frames, *, fps: float | None = None,
               anchor: tuple[int, int] | None = None, states: dict[str, list[int]] | None = None,
               loop: bool = True, notes: str = "") -> Path:
    """Export one asset.

    frames: an Image or list of equally-sized Images (animation frames).
    anchor: (x, y) in frame coords of the ground/attach point; default bottom-centre.
    states: optional named frame ranges, e.g. {"walk": [0,1,2,3,4,5], "idle": [6,7]}.

    Writes assets/out/<group>/<name>.png (horizontal strip, 1x), <name>.json,
    and _preview/<name>@4x.png (+ .gif when animated).
    """
    if isinstance(frames, Image.Image):
        frames = [frames]
    frames = [f.convert("RGBA") for f in frames]
    fw, fh = frames[0].size
    for i, f in enumerate(frames):
        if f.size != (fw, fh):
            raise ValueError(f"[{group}/{name}] frame {i} size {f.size} != {(fw, fh)}")
        validate(f, f"{group}/{name}#{i}")
    d = OUT / group
    (d / "_preview").mkdir(parents=True, exist_ok=True)
    strip = new(fw * len(frames), fh)
    for i, f in enumerate(frames):
        strip.paste(f, (i * fw, 0))
    strip.save(d / f"{name}.png")
    meta = {
        "name": name, "group": group, "frameW": fw, "frameH": fh, "frames": len(frames),
        "fps": fps, "anchor": list(anchor) if anchor else [fw // 2, fh - 1],
        "states": states or {"default": list(range(len(frames)))}, "loop": loop, "notes": notes,
    }
    (d / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    k = PREVIEW_SCALE
    big = strip.resize((strip.width * k, strip.height * k), Image.NEAREST)
    bg = _preview_bg(big.width, big.height)
    bg.alpha_composite(big)
    bg.convert("RGB").save(d / "_preview" / f"{name}@4x.png")
    if len(frames) > 1:
        gif_frames = []
        for f in frames:
            fb = _preview_bg(fw * k, fh * k)
            fb.alpha_composite(f.resize((fw * k, fh * k), Image.NEAREST))
            gif_frames.append(fb.convert("RGB"))
        dur = int(1000 / (fps or 8))
        gif_frames[0].save(d / "_preview" / f"{name}.gif", save_all=True,
                           append_images=gif_frames[1:], duration=dur, loop=0, disposal=2)
    return d / f"{name}.png"
