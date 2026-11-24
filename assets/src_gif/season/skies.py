"""Season skies (full-canvas 384x216, anchor 0,0), flat bands like the GIF sky.

    .venv/bin/python assets/src_gif/season/skies.py      # -> assets/out_gif/season/sky_{xuan,thu,dong,mua}.png

xuan: pale Tết morning, big soft clouds, warm cream horizon.
thu:  Trung Thu dusk, violet -> gold bands, full moon upper right, lit cloud streaks.
dong: winter night, navy bands, faint cloud streaks (stars + fireworks are drawn live by compose/fx_gif.py).
mua:  summer shower, heavy grey clouds.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.px_gif import *  # noqa: E402,F403
from tools.layout_gif import W, H  # noqa: E402


def blob_mask(blobs):
    S = set()
    for b in blobs:
        cx, cy, rx, ry = b
        for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
            for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
                if ((x - cx) / (rx + .5)) ** 2 + ((y - cy) / (ry + .5)) ** 2 <= 1.0:
                    S.add((x, y))
    return S


def cloud(im, blobs, top="cloud", mid="cloud_s", bot="cloud_d"):
    S = blob_mask(blobs)
    for (x, y) in S:
        if not (0 <= x < W and 0 <= y < H):
            continue
        col = top
        if (x, y + 1) not in S:
            col = bot
        elif (x, y + 2) not in S:
            col = mid
        put(im, x, y, col)


def bands(im, spec):
    for y0, y1, col in spec:
        rect(im, 0, y0, W - 1, y1, col)


def streak(im, x, y, n, top, body):
    rect(im, x, y, x + n, y, top); rect(im, x + 3, y + 1, x + n + 4, y + 1, body)


def sky_xuan():
    im = new(W, H)
    bands(im, [(0, 14, "sky"), (15, 100, "sky_hl"), (101, H - 1, "wc_l")])
    cloud(im, [(40, 30, 10, 6), (55, 25, 11, 9), (72, 29, 10, 7), (86, 33, 8, 4), (60, 35, 26, 3)])
    cloud(im, [(300, 40, 9, 6), (316, 33, 12, 10), (333, 37, 10, 7), (349, 41, 8, 4), (322, 44, 26, 3)])
    cloud(im, [(176, 16, 6, 3), (186, 13, 6, 4), (196, 16, 5, 3), (186, 18, 14, 2)])
    cloud(im, [(360, 12, 4, 2), (367, 10, 4, 3), (374, 12, 4, 2)])
    return im


def sky_thu():
    im = new(W, H)
    bands(im, [(0, 22, "du_1"), (23, 50, "du_2"), (51, 82, "du_3"), (83, 112, "du_4"), (113, 140, "du_5"),
               (141, H - 1, "du_6")])
    # full moon with a soft halo ring
    cx, cy, r = 336, 34, 11
    ellipse(im, cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4, "du_3" if cy > 40 else "du_2")
    ellipse(im, cx - r, cy - r, cx + r, cy + r, "moon")
    for x, y, w_, h_ in [(-5, -4, 3, 2), (2, -6, 2, 1), (3, 1, 4, 3), (-4, 4, 2, 2), (-1, -1, 1, 1)]:
        rect(im, cx + x, cy + y, cx + x + w_ - 1, cy + y + h_ - 1, "moon_d")
    for i in range(r - 1):                                   # shaded lower-right rim
        put(im, cx + i // 2 + 4, cy + r - i // 3, "moon_d")
    # lit cloud streaks
    streak(im, 20, 64, 34, "du_5", "du_3"); streak(im, 66, 58, 22, "du_5", "du_3")
    streak(im, 238, 96, 30, "du_6", "du_4"); streak(im, 300, 104, 40, "du_6", "du_4")
    streak(im, 150, 40, 18, "du_4", "du_2")
    return im


def sky_dong():
    im = new(W, H)
    bands(im, [(0, 26, "nt_k"), (27, 72, "nt_d"), (73, 122, "nt"), (123, H - 1, "nt_m")])
    streak(im, 30, 52, 30, "nt", "nt_d"); streak(im, 140, 30, 22, "nt", "nt_d"); streak(im, 250, 84, 36, "nt_m", "nt")
    return im


def sky_mua():
    im = new(W, H)
    bands(im, [(0, 22, "ov_k"), (23, 70, "ov_d"), (71, 128, "ov"), (129, H - 1, "ov_l")])
    for blobs in ([(30, 30, 18, 9), (60, 24, 20, 12), (95, 32, 16, 8), (64, 38, 40, 5)],
                  [(170, 20, 16, 8), (200, 14, 20, 10), (232, 22, 16, 8), (204, 28, 40, 5)],
                  [(300, 34, 18, 10), (334, 26, 22, 13), (366, 36, 16, 8), (336, 44, 44, 5)]):
        cloud(im, blobs, top="ov", mid="ov_d", bot="ov_k")
    return im


if __name__ == "__main__":
    for name, fn in (("sky_xuan", sky_xuan), ("sky_thu", sky_thu), ("sky_dong", sky_dong), ("sky_mua", sky_mua)):
        save_asset("season", name, [fn()], anchor=(0, 0), notes="season sky, full canvas")
    print("ok")


# ---------------------------------------------------------------------------------------------- 6c: gradient skies
# The client wants the sky background as a smooth gradient (not pixel bands). The compositor now paints the gradient
# (seasons.SKY_GRAD) and lays these "_fg" overlays on top: only the clouds / moon / streaks, transparent elsewhere.
def _fg(fn):
    global bands
    keep = bands
    bands = lambda im, spec: None            # noqa: E731  (skip the flat bands)
    try:
        return fn()
    finally:
        bands = keep


def sky_thu_fg():
    im = new(W, H)
    cx, cy, r = 336, 34, 11                  # moon disc + craters (the halo is a soft glow in the compositor)
    ellipse(im, cx - r, cy - r, cx + r, cy + r, "moon")
    for x, y, w_, h_ in [(-5, -4, 3, 2), (2, -6, 2, 1), (3, 1, 4, 3), (-4, 4, 2, 2), (-1, -1, 1, 1)]:
        rect(im, cx + x, cy + y, cx + x + w_ - 1, cy + y + h_ - 1, "moon_d")
    for i in range(r - 1):
        put(im, cx + i // 2 + 4, cy + r - i // 3, "moon_d")
    return im                                # (the cloud streaks are soft now: compose/sky_soft.py)


def sky_ha_fg():
    """Clouds of the summer sky (same as env/sky, without its bands)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sg", ROOT / "assets/src_gif/env_b/sky_ground.py")
    sys.path.insert(0, str(ROOT / "assets/src_gif/env_b"))
    sg = importlib.util.module_from_spec(spec); spec.loader.exec_module(sg)
    im = new(W, H)
    sg.cloud(im, [(318, 36, 9, 6), (331, 31, 10, 8), (346, 34, 9, 6), (358, 37, 7, 4), (326, 40, 20, 3), (344, 40, 18, 3)])
    sg.cloud(im, [(106, 17, 6, 3), (116, 14, 6, 4), (126, 17, 5, 3), (114, 19, 14, 2)])
    sg.cloud(im, [(262, 11, 4, 2), (270, 9, 4, 3), (278, 11, 4, 2), (270, 13, 9, 1)])
    sg.cloud(im, [(40, 24, 4, 2), (46, 22, 4, 3), (53, 24, 3, 2), (47, 26, 8, 1)])
    return im


def export_fg():
    # 6c (2): the clouds are drawn soft at full resolution by compose/sky_soft.py, so the only pixel overlay left
    # on the gradient skies is the Trung Thu moon.
    save_asset("season", "sky_thu_fg", [sky_thu_fg()], anchor=(0, 0), notes="pixel moon only (soft sky)")


if __name__ == "__main__":
    export_fg()
    print("fg ok")
