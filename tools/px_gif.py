"""Pixel toolkit for the GIF-style styleframe (style v4, 23/11/2026).

Same API as tools/px.py (new, rect, line, poly, outline, text, save_asset, validate, ...) but with the
v4 palette (pastel, derived from refs/pinterest_pixel_shop.gif) and output in assets/out_gif/.

    import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
    from tools.px_gif import *
    from tools.layout_gif import *
"""
from __future__ import annotations

import tools.px as _px
from tools.px import *  # noqa: F401,F403  (functions; palette dicts are mutated below)

# name -> hex. Ramps run light -> dark. Colours sampled from the reference GIF where it has them.
PALETTE_GIF: dict[str, str] = {
    # sky + distance (GIF sky b6dafc, haze blues)
    "sky_hl": "#d7e9fb", "sky": "#b6dafc", "sky_m": "#9bc1e7", "sky_d": "#82b0de",
    "haze_l": "#c6d6e6", "haze": "#a9bfd4", "haze_d": "#8fa7bf",
    "cloud": "#ffffff", "cloud_s": "#e6edf5", "cloud_d": "#c9d6e4",
    # neutrals: concrete / metal / glass (GIF greys)
    "white": "#ffffff", "paper": "#eeeae3", "grey_hl": "#e1e1e1", "grey_l": "#b5c0c9",
    "grey": "#919ca3", "grey_m": "#748189", "grey_d": "#5d646b", "grey_k": "#3f4449", "ink": "#202931",
    "glass_l": "#d7e8f3", "glass": "#9fc3dc", "glass_d": "#6f97b5",
    # wood / dark trim (GIF browns: outlines of buildings use wood_k / ink)
    "wood_hl": "#a89e92", "wood_l": "#8a7b71", "wood": "#695a4c", "wood_d": "#4a4238",
    "wood_k": "#342e26", "trunk_l": "#8e7b68", "trunk": "#6e5a47", "trunk_d": "#4e3f31",
    # Hanoi wall paints (pastel, each with light / base / shade)
    "wy_l": "#f7e2a8", "wy": "#ecc978", "wy_d": "#c9a058",           # yellow ochre (classic Hanoi)
    "wp_l": "#f3d6cc", "wp": "#e3b3a6", "wp_d": "#bf8a80",           # dusty pink
    "wb_l": "#d6e6ea", "wb": "#aecbd3", "wb_d": "#86a7b1",           # pale blue
    "wc_l": "#f1ece1", "wc": "#dcd3c2", "wc_d": "#b5aa96",           # cream / weathered plaster
    # shutters / painted wood
    "sh_l": "#79b893", "sh": "#4f9370", "sh_d": "#356b52",           # green louvered shutters
    "sb_l": "#6f9fd0", "sb": "#4a78ad", "sb_d": "#33557d",           # blue shutters / doors
    # terracotta + sidewalk tiles
    "tc_l": "#d99a7c", "tc": "#b8705a", "tc_d": "#8d5043",
    "pave_l": "#c9c1b5", "pave": "#a99f92", "pave_d": "#857b70",
    # road
    "road_l": "#6b7076", "road": "#55595f", "road_d": "#42454a", "lane": "#e9e4d4",
    # foliage (pastel greens)
    "leaf_hl": "#b5dc8c", "leaf_l": "#7fbf6a", "leaf": "#4f9e5f", "leaf_d": "#2e794d", "leaf_k": "#1d4e33",
    # bougainvillea (hero) — magenta ramp, a touch more saturated than the GIF cherry
    "bl_hl": "#f9c3dc", "bl_l": "#ee8fbf", "bl": "#dc5f9d", "bl_d": "#b23f7d", "bl_k": "#7a2a5a",
    # GIF cherry pinks (Tết peach blossom, signs)
    "pk_l": "#dc7f99", "pk": "#c5627b", "pk_d": "#a34460",
    # reds / oranges / yellows (signs, stools, bus, lanterns)
    "red_l": "#e5614f", "red": "#cb3432", "red_d": "#94271f",
    "or_l": "#f6b26b", "or": "#e8913f", "or_d": "#b8662e",
    "yl_l": "#ffe08a", "yl": "#f2c14e", "yl_d": "#c79231",
    # blues (plastic seats, bus-stop sign)
    "pb_l": "#68a6e2", "pb": "#3e7fc4", "pb_d": "#2d5f99", "navy": "#1d3c64",
    "teal": "#3e9aac", "teal_d": "#2a6f7d",
    # skin + hair
    "sk_l": "#f6d2b3", "sk": "#e8b48e", "sk_d": "#c48663", "hair": "#2b241d", "hair_l": "#4a3c30",
    # cat (orange tabby) — or_* ramp + these
    "cat_hl": "#fbd59b",
    # light
    "glow": "#fff3c9", "lamp": "#ffd77e",
    # ---- seasons (added 24/11/2026). Only for season skies, lights and FX; scenery stays on the ramps above.
    # dusk sky (Trung Thu evening): top violet -> horizon gold
    "du_1": "#4b4a86", "du_2": "#6f5c9a", "du_3": "#a56a9e", "du_4": "#d9799a", "du_5": "#f39c8c", "du_6": "#ffc58f",
    # night sky (winter): deep navy ramp + star / moon
    "nt_k": "#0f1530", "nt_d": "#18214a", "nt": "#223060", "nt_m": "#2f4177", "nt_l": "#43588f",
    "moon": "#fff6d6", "moon_d": "#efdca6", "moon_k": "#d8c18a",
    # overcast / rain sky
    "ov_l": "#c3cbd3", "ov": "#a2adb8", "ov_d": "#858f9c", "ov_k": "#6b7482",
    # flag / Tết gold
    "gold": "#ffd23f",
    # park scene (bản 6): pale sage far tree line
    "fg_l": "#d3e3c8", "fg": "#b6cdb0", "fg_d": "#98b39c",
    # far high-rises: barely darker / greyer than the sky (faint, "mờ")
    "far_l": "#c6dbee", "far": "#b0c7dd", "far_d": "#9db5cc",
}

_px.PALETTE.clear(); _px.PALETTE.update(PALETTE_GIF)
_px.RGB.clear(); _px.RGB.update({k: _px._hex(v) for k, v in PALETTE_GIF.items()})
_px._ALLOWED.clear(); _px._ALLOWED.update(_px.RGB.values())
_px.OUT = _px.ROOT / "assets" / "out_gif"
_px.PREVIEW_SCALE = 5
PALETTE, RGB = _px.PALETTE, _px.RGB
