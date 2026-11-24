"""Compositor for the v4 GIF-style loop, four seasons.

    .venv/bin/python compose/gif_frame.py --season thu             # still   -> review/gif_style/thu/frame@5x.png
    .venv/bin/python compose/gif_frame.py --season thu --anim 24   # + 24 s seamless loop -> review/gif_style/thu/loop.mp4
    .venv/bin/python compose/gif_frame.py --all --anim 24          # every season + review/gif_style/bon_mua.mp4
    .venv/bin/python compose/gif_frame.py --scene cafe --season ha # park scene (bản 6): kiosk café | taphoa
                                                                   #   -> review/gif_style/v6_cafe/<season>/

Seasons (compose/seasons.py): xuan (Tết morning), ha (summer noon, the approved styleframe), mua (summer shower),
thu (Trung Thu dusk), dong (New Year's Eve night, fog, fireworks). Layers come from assets/out_gif/<group>/<name>.png
(+ .json written by save_asset). Scenery layers are full-canvas (anchor 0,0); actors are placed by PLACE.
Lighting is a per-colour grade (flat areas stay flat), with emissive pixels (lit windows, lanterns, cat eyes) that
skip the grade, then flat stepped light pools, fog, rain and fireworks from compose/fx_gif.py.
"""
from __future__ import annotations

import json
import math
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "compose"))
from tools.layout_gif import *  # noqa: E402,F403
from tools.px_gif import RGB as PRGB  # noqa: E402
import fx_gif as fx  # noqa: E402
import sky_soft  # noqa: E402
from seasons import SEASONS, ORDER_OF_SEASONS, season_for, SKY_GRAD  # noqa: E402

A = ROOT / "assets/out_gif"
OUT = ROOT / "review/gif_style"
FPS = 12
LOOP = 24.0        # seconds; every cycle below divides this so the clip loops seamlessly

# z-order, back to front. (group, name, placement key or None for full-canvas)
BASE_ORDER = [
    ("env", "sky", None), ("env", "distance", None),
    ("env", "house", None),
    ("actors", "shopkeeper", "shopkeeper"),
    ("actors", "grandma_water", "grandma_water"),
    ("env", "house_front", None),
    ("actors", "pigeon_perch", "pigeon_perch"),
    ("actors", "sparrow_perch", "sparrow_perch"),
    ("env", "ground", None),
    ("shelter", "shelter_back", None), ("shelter", "seats", None),
    ("actors", "woman_wait", "woman_wait"),
    ("shelter", "shelter_front", None),
    ("shelter", "bougainvillea", None),
    ("actors", "cat_black", "cat_black"),
    ("shelter", "stop_sign", None),
    ("actors", "dog_lie", "dog_lie"),
    ("actors", "pigeon_walk", "pigeon_peck"),
    ("actors", "tea_table", "tea_table"), ("actors", "stool_red", "stool_red"), ("actors", "stool_blue", "stool_blue"),
    ("actors", "oldman_tea", "oldman_tea"), ("actors", "steam", "steam"),
    ("actors", "sparrow_perch", "sparrow_stool"),
]
BASE_PLACE: dict[str, list[tuple]] = {
    "shopkeeper": [SHOPKEEPER_SPOT],
    "grandma_water": [BALCONY_SPOT],
    "pigeon_perch": [(244, ROOF_RIDGE_Y + 1), (284, ROOF_RIDGE_Y + 1, True)],
    "sparrow_perch": [(STOP_SIGN_X, 131, True)],
    "sparrow_stool": [(377, STAND_Y - 8)],
    "woman_wait": [WAITER_SPOT],
    "cat_black": [CAT_SPOT],
    "dog_lie": [DOG_SPOT],
    "pigeon_peck": [(244, STAND_Y + 1, False, "peck"), (261, STAND_Y + 2, True, "peck")],
    "tea_table": [(337, STAND_Y)],
    "stool_red": [(376, STAND_Y)],
    "stool_blue": [(364, STAND_Y)],
    "oldman_tea": [(362, STAND_Y)],
    "steam": [(329, 177)],
}
SEMI = {"steam": 0.7}                             # drawn with partial opacity

# Park scene (bản 6): a one-storey kiosk (café or tạp hóa) with a park behind instead of the shophouse + city.
PARK_RIDGE_Y = 92


def park_order(shop: str):
    order = []
    for g, n, p in BASE_ORDER:
        if (g, n) == ("env", "distance"):
            order += [("env", "park_far", None), ("env", "park_lawn", None), ("env", "park_xacu", None),
                      ("env", "park_bang", None), ("env", "park_front", None)]   # (6c: grandma_ex replaced by the flower bike)
        elif (g, n) == ("env", "house"):
            order.append(("env", f"kiosk_{shop}", None))
        elif (g, n) == ("actors", "shopkeeper"):
            order += [(g, n, p), ("actors", "cat_tabby", "cat_tabby")]       # mèo mướp on the café counter
        elif (g, n) == ("actors", "cat_black"):
            order.append(("actors", "cat_black_lie", "cat_black"))           # 6c: mèo mun lies on the bench
        elif n in ("grandma_water", "house_front"):
            continue
        else:
            order.append((g, n, p))
            if (g, n) == ("env", "ground"):
                order.append(("env", f"kiosk_props_{shop}", None))
    return order


PARK_PLACE = dict(BASE_PLACE, pigeon_perch=[(244, PARK_RIDGE_Y + 1), (272, PARK_RIDGE_Y + 1, True)],
                  grandma_ex=[(340, 170, False, "ex")], cat_tabby=[(273, 175, False, "idle")],
                  cat_black=[(148, SEAT_Y - 1)])                       # right end of bench B, clear of the parked bus
SCENES = {"house": (BASE_ORDER, BASE_PLACE, ""),
          "cafe": (park_order("cafe"), PARK_PLACE, "v6_cafe"),
          "taphoa": (park_order("taphoa"), PARK_PLACE, "v6_taphoa")}

# scripted states over the loop: name -> [(t0, t1, state)] (the black cat reacts to the bus)
TIMELINES = {
    "cat_black": [(0, 3, "sit"), (3, 7, "lick"), (7, 8.5, "wash"), (8.5, 13.5, "look"), (13.5, 17, "watch"),
                  (17, 21, "lick"), (21, 24, "sit")],
    # park scene: asleep on the bench, lifts its head when the bus comes, watches it leave, dozes off again
    "cat_black_lie": [(0, 4, "sleep"), (4, 13.5, "look"), (13.5, 17, "watch"), (17, 20, "look"), (20, 24, "sleep")],
}

# the bus: arrives (ease-out), idles at the stop, leaves (ease-in). Times in the loop, x = bus front (left edge).
BUS_T_IN, BUS_T_STOP, BUS_T_GO, BUS_T_OUT = 4.0, 8.5, 13.5, 18.5
EASTER_BUS = {"ha": 0}     # easter egg: in the summer clip the iKame bus replaces bus 32 on lap 0 of 5 (the lap the
                           # montage shows), i.e. once per 2 minutes; park scenes only
BUS_X_STOP = 0                                         # 6c: the 148 px bus parks with its rear at x147, so the cat
                                                       # lying on the bench (x148-167) stays in view
STUDENT_T, STUDENT_X0, STUDENT_V = 14.0, 132, 26.0     # kid revealed behind the leaving bus, walks right
MOTO_T0, MOTO_T1 = 18.7, 23.9                          # Tết: motorbike with a peach tree, after the bus has gone
BIKE_T0, BIKE_DUR = 18.7, 9.1                          # park scene: xe đạp hoa rides left -> right while the road is
                                                       # free of the bus (18.7 -> 27.8 = 3.8 of the next loop)
BIKE_LOAD = {"xuan": "xuan", "ha": "ha", "mua": "ha", "thu": "thu", "dong": "dong"}   # flowers of the season

SHADOW = {"tea_table": 34, "stool_red": 11, "stool_blue": 11, "oldman_tea": 0, "moto_parked": 34, "dog_lie": 22,
          "pigeon_walk": 9, "walker": 16, "scooter": 30, "kumquat": 14}  # sprite -> shadow width (0 = none)


def bus_x(t: float, bw: int) -> float | None:
    x_in, x_out = W + 4, -bw - 12
    if BUS_T_IN <= t < BUS_T_STOP:
        u = (t - BUS_T_IN) / (BUS_T_STOP - BUS_T_IN)
        return BUS_X_STOP + (x_in - BUS_X_STOP) * (1 - u) ** 2
    if BUS_T_STOP <= t < BUS_T_GO:
        return BUS_X_STOP
    if BUS_T_GO <= t < BUS_T_OUT:
        u = (t - BUS_T_GO) / (BUS_T_OUT - BUS_T_GO)
        return BUS_X_STOP - (BUS_X_STOP - x_out) * u ** 2
    return None


class Sprite:
    def __init__(self, group: str, name: str):
        p = A / group / f"{name}.png"
        meta = json.loads((A / group / f"{name}.json").read_text())
        strip = Image.open(p).convert("RGBA")
        fw, fh, n = meta["frameW"], meta["frameH"], meta["frames"]
        self.name = name
        self.frames = [strip.crop((i * fw, 0, (i + 1) * fw, fh)) for i in range(n)]
        self.fps = meta.get("fps") or 0
        self.anchor = tuple(meta.get("anchor") or (0, 0))
        self.states = meta.get("states") or {}

    def frame(self, t: float, offset: float = 0.0, state: str | None = None) -> Image.Image:
        idx = self.states.get(state) if state else None
        idx = idx or list(range(len(self.frames)))
        if not self.fps or len(idx) == 1:
            return self.frames[idx[0]]
        return self.frames[idx[int((t + offset) * self.fps) % len(idx)]]


def load(group, name):
    try:
        return Sprite(group, name)
    except FileNotFoundError:
        return None


# ------------------------------------------------------------------------------------------------ season look
def _c(name):
    return np.array(PRGB[name], dtype=np.float32)


GRADES = {   # per-colour light grades (rgb float arrays). Same input colour -> same output colour: stays pixel-flat.
    "night": lambda c: c * np.array([0.30, 0.36, 0.56], np.float32) + np.array([12, 16, 40], np.float32),
    "dusk": lambda c: c * np.array([0.80, 0.60, 0.72], np.float32) + np.array([22, 8, 26], np.float32),
    "overcast": lambda c: ((c * 0.55 + (c @ np.array([0.3, 0.59, 0.11], np.float32))[..., None] * 0.45)
                           * np.array([0.78, 0.81, 0.86], np.float32)),
}
SOFT = {     # lit interiors (the shop) under each grade
    "night": lambda c: c * np.array([0.90, 0.80, 0.62], np.float32) + np.array([18, 10, 0], np.float32),
    "dusk": lambda c: c * np.array([0.98, 0.86, 0.74], np.float32) + np.array([12, 6, 0], np.float32),
    "overcast": lambda c: c * np.array([0.92, 0.90, 0.86], np.float32),
}
FAR_MIX = {"night": ("nt_m", 0.40), "dusk": ("du_5", 0.30), "overcast": ("ov_l", 0.35)}
BLOOM_TO_LEAF = {"bl_hl": "leaf_hl", "bl_l": "leaf_l", "bl": "leaf", "bl_d": "leaf_d", "bl_k": "leaf_k"}


class Look:
    """Applies a season to sprite frames (recolour, bougainvillea leafing, grade, emissive), cached per frame."""

    def __init__(self, key: str, scene: str = "house"):
        self.key = key
        self.scene = scene
        self.base_order, self.base_place, self.tag = SCENES[scene]
        self.S = season_for(key, scene)
        self.grade = self.S.get("grade")
        self.cache: dict = {}

    def get(self, k, default=None):
        return self.S.get(k, default)

    def proc(self, img: Image.Image, *names: str) -> Image.Image:
        ck = (id(img), names)
        hit = self.cache.get(ck)
        if hit is not None:
            return hit[1]
        S = self.S
        a = np.array(img, dtype=np.float32)
        rgb = a[..., :3]
        rules = lambda field: [r for n in names for r in (S.get(field, {}).get(n) or [])]  # noqa: E731
        # 1. recolour (clothes, park trees). Masks come from the original colours, so chains (a->b, b->c) don't cascade.
        for n in names:
            pairs = [(np.all(rgb == _c(src), axis=-1), _c(dst)) for src, dst in (S.get("recolor", {}).get(n) or {}).items()]
            for m, dst in pairs:
                rgb[m] = dst
        # 2. bougainvillea: fewer flowers out of season (shade tones become leaves)
        if "bougainvillea" in names and S.get("bloom_leaf"):
            for src in S["bloom_leaf"]:                      # shaded tones of the clumps turn to foliage
                m = np.all(rgb == _c(src), axis=-1)
                rgb[m] = _c(BLOOM_TO_LEAF[src])
        cur = rgb.copy()
        # 3. light grade
        if self.grade and "sky" not in names:
            out = GRADES[self.grade](cur)
            if ("distance" in names or "park_far" in names) and self.grade in FAR_MIX:
                col, k = FAR_MIX[self.grade]
                out = out + (_c(col) - out) * k
            soft = SOFT[self.grade](cur)
            if any(n in S.get("soft_all", ()) for n in names):
                out = soft
            for x0, y0, x1, y1 in rules("soft"):
                out[y0:y1 + 1, x0:x1 + 1] = soft[y0:y1 + 1, x0:x1 + 1]
            for rect, mapping in rules("emit"):
                box = np.zeros(rgb.shape[:2], bool)
                if rect is None:
                    box[:] = True
                else:
                    x0, y0, x1, y1 = rect
                    box[y0:y1 + 1, x0:x1 + 1] = True
                for src, dst in mapping.items():
                    m = np.all(cur == _c(src), axis=-1) & box
                    out[m] = _c(dst)
            rgb = out
        a[..., :3] = np.clip(np.rint(rgb), 0, 255)
        res = Image.fromarray(a.astype(np.uint8), "RGBA")
        self.cache[ck] = (img, res)          # keep img alive so its id stays unique
        return res


def season_order(look: Look):
    order = []
    adds = look.get("add", [])
    sky = look.get("sky")
    for g, n, p in look.base_order:
        if (g, n) == ("env", "sky") and sky:
            g, n = sky
        order.append((g, n, p))
        for after, item in adds:
            if after == n or after == p:
                order.append(item)
    return order


def season_place(look: Look):
    pl = dict(look.base_place)
    pl.update(look.get("place", {}))
    return pl


# ------------------------------------------------------------------------------------------------ drawing helpers
def shadow(cv: Image.Image, x: int, y: int, w: int, h: int = 3, k: float = 0.78):
    """Flat pixel shadow: darken an ellipse-ish band centred on (x, y) by k (stays crisp, no blur)."""
    px = cv.load()
    for dy in range(h):
        half = int(w / 2 * (1 - (abs(dy - (h - 1) / 2) / h) ** 2 * 1.2))
        for dx in range(-half, half + 1):
            X, Y = x + dx, y - h + 2 + dy
            if 0 <= X < W and 0 <= Y < H:
                r, g, b, a = px[X, Y]
                px[X, Y] = (int(r * k), int(g * k), int(b * k), a)


def put_img(cv, img, anchor, x, y, flip=False):
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        cv.alpha_composite(img, (x - (img.width - 1 - anchor[0]), y - anchor[1]))
    else:
        cv.alpha_composite(img, (x - anchor[0], y - anchor[1]))


def is_sky(g, n):
    return n == "sky" or (g == "season" and n.startswith("sky_"))


def render(t: float, sprites: dict, movers: dict, look: Look, mask_out: list | None = None) -> Image.Image:
    """One logical 384x216 frame. With mask_out, also appends the bool HxW mask of pixels where the (soft) sky is
    still visible, for sky_soft.to_hi()."""
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    sky_snap = None
    hide = look.get("hide", set())
    place_map = season_place(look)
    lights = []
    for i, (g, n, place) in enumerate(season_order(look)):
        s = sprites.get((g, n))
        if not s or n in hide or (place and place in hide):
            continue
        if place is None and is_sky(g, n) and look.key in SKY_GRAD:
            cv.paste(sky_lo(look.key, t))                        # 6c: soft sky (gradient, moon, drifting soft clouds;
            after_sky(cv, t, look)                               # box-averaged), then stars / fireworks
            sky_snap = np.asarray(cv)[..., :3].copy()
            continue
        if place is None:
            names = ("sky",) if is_sky(g, n) else ((n, ALIAS[n]) if n in ALIAS else (n,))
            cv.alpha_composite(look.proc(s.frame(t, offset=i * 0.37), *names))
        else:
            for k, pl in enumerate(place_map.get(place, [])):
                x, y = pl[0], pl[1]
                flipped = len(pl) > 2 and pl[2]
                state = pl[3] if len(pl) > 3 else None
                if n in TIMELINES:
                    tl = t % LOOP
                    t0, _, state = next(seg for seg in TIMELINES[n] if seg[0] <= tl < seg[1])
                    img = s.frame(tl - t0, state=state)
                else:
                    if not state and "sway" in s.states:
                        state = "sway"
                    img = s.frame(t, offset=k * 0.61 + i * 0.29, state=state)
                img = look.proc(img, n, place)
                if SHADOW.get(n):
                    shadow(cv, x, y, SHADOW[n])
                if n in SEMI:
                    al = img.getchannel("A").point(lambda v, f=SEMI[n]: int(v * f)); img = img.copy(); img.putalpha(al)
                put_img(cv, img, s.anchor, x, y, flipped)
                gp = look.get("glow_place", {}).get(place)
                if gp:
                    dy, r, col, kk = gp
                    lights.append((x, y + dy, r, r, col, kk))
        if is_sky(g, n):
            after_sky(cv, t, look)                               # (house scene / seasons without a gradient)
        if (g, n) in (("env", "distance"), ("env", "park_far")):
            after_distance(cv, t, look)
    draw_movers(cv, t, movers, look, lights)
    if mask_out is not None:                                     # sky pixels nothing was drawn over (before glows/rain)
        mask_out.append(None if sky_snap is None else np.all(np.asarray(cv)[..., :3] == sky_snap, axis=-1))
    post(cv, t, look, lights)
    return cv


def sky_lo(key: str, t: float) -> Image.Image:
    """The soft sky at time t at the logical size (box average of the 1920x1080 one); not palette-locked on purpose."""
    lo = sky_soft.sky(key).at(t)[0]
    return Image.fromarray(np.dstack([lo, np.full(lo.shape[:2], 255, np.uint8)]), "RGBA")


ALIAS = {"kiosk_cafe": "kiosk", "kiosk_taphoa": "kiosk", "kiosk_props_cafe": "kiosk_props",
         "kiosk_props_taphoa": "kiosk_props"}


def after_sky(cv, t, look):
    f = look.get("fx", {})
    if f.get("stars"):
        sky_cols = None if look.key in SKY_GRAD else {PRGB[c] for c in ("nt_k", "nt_d", "nt")}
        fx.stars(cv, t, LOOP, region=(0, 0, W, 130), n=60, sky_colors=sky_cols)
    if f.get("fireworks"):
        probe = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        region = look.get("fw_region", (262, 10, 380, 112))
        flash, col = fx.fireworks(probe, t, LOOP, region=region)
        if flash > 0.05:                                     # the whole sky lights up a touch (flat, no shape)
            k = round(0.10 * flash, 2)
            a = np.array(cv, dtype=np.float32)
            a[..., :3] += (np.array(col, np.float32) - a[..., :3]) * k
            cv.paste(Image.fromarray(np.rint(a).astype(np.uint8), "RGBA"))
        fx.fireworks(cv, t, LOOP, region=region)


DISTANT_BLOCKS = [(296, 312, 152), (312, 323, 142), (323, 339, 155), (339, 351, 146), (351, 366, 153), (366, 384, 144)]


def after_distance(cv, t, look):
    f = look.get("fx", {})
    if f.get("city_lights"):
        rnd = random.Random(21)
        px = cv.load()
        for a, b, top in look.get("far_blocks", DISTANT_BLOCKS):  # lit windows on the far blocks (same grid as env)
            for yy in range(top + 4, look.get("far_rows_end", 168), 5):
                for xx in range(a + 2, b - 3, 4):
                    if rnd.random() < 0.45 * f["city_lights"]:
                        col = PRGB["lamp" if rnd.random() < 0.7 else "yl_l"] + (255,)
                        px[xx, yy] = col; px[xx + 1, yy] = col
        if look.get("deck_lamps", True):
            for x in range(300, W, 7):                           # Long Biên deck lamps
                px[x, 159] = PRGB["yl_l"] + (255,)
    if f.get("fog"):
        fx.fog(cv, t, LOOP, bands=[(150, 9, 0.38, 1), (168, 6, 0.30, -1)], color=PRGB["nt_l"])


def post(cv, t, look, lights):
    f = look.get("fx", {})
    if f.get("fairy"):                                           # fairy lights under the balcony slab, blinking
        px = cv.load()
        cols = ["red_l", "yl_l", "leaf_hl", "pb_l"]
        fx0, fx1, fy = look.get("fairy_row", (160, 298, 127))
        for j, x in enumerate(range(fx0, fx1, 4)):
            y = fy + (1 if (x // 4) % 5 in (2, 3) else 0)
            on = (j + int(t * 2)) % 2 == 0
            col = cols[j % 4]
            px[x, y] = PRGB[col if on else "grey_k"] + (255,)
            if on:
                lights.append((x, y, 2, 2, col, 0.22))
    for cx, cy, rx, ry, col, k in look.get("glows", []) + lights:
        fx.glow(cv, cx, cy, rx, ry, PRGB[col] if isinstance(col, str) else col, k=k)
    if f.get("fog"):
        fx.fog(cv, t, LOOP, bands=[(182, 10, 0.20, 1), (60, 24, 0.06, -1)], color=PRGB["nt_l"])
    if f.get("rain"):
        r = f["rain"]
        fx.rain(cv, t, LOOP, density=r.get("density", 1.0), exclude=tuple(r.get("exclude", ())))


def draw_movers(cv, t, movers, look, lights):
    """Things that travel. Every period divides LOOP so the clip loops seamlessly."""
    lap = int(t // LOOP) % 5                                 # which 24 s lap of the 120 s clip (easter egg bus)
    t = t % LOOP
    hide = look.get("hide", set())
    lit = look.grade in ("dusk", "night")
    wkey = look.get("walker", "walker")
    w = movers.get(wkey)
    if w and "walker" not in hide:                           # vendor (or the lion dance): one crossing per loop
        lion = wkey == "lion_dance"
        span = W + (110 if lion else 60)
        ph = 4.95 if lion else 0.0                           # lion troupe is past the shop when the kids get off
        x = int((-50 if lion else -30) + ((t + ph) * span / LOOP) % span)
        shadow(cv, x, STAND_Y + 2, 40 if lion else SHADOW["walker"])
        put_img(cv, look.proc(w.frame(t), "walker", w.name), w.anchor, x, STAND_Y + 2)
    for skey, dt, dx in look.get("students", [("student", 0.0, 0)]):
        kid = movers.get(skey)
        if kid and t >= STUDENT_T + dt:
            x = int(STUDENT_X0 + dx + (t - STUDENT_T - dt) * STUDENT_V)
            if x < W + 30:
                shadow(cv, x, STAND_Y + 3, 10)
                put_img(cv, look.proc(kid.frame(t), "student", kid.name), kid.anchor, x, STAND_Y + 3)
                if lit and skey.startswith("lantern_kid"):
                    lights.append((x + 12, STAND_Y + 3 - 8, 9, 9, "or_l", 0.30))
    pw = movers.get("pigeon_walker")
    if pw and "pigeon_walker" not in hide:                   # one pigeon strolling to and fro in front of the shop
        period, span = 12.0, 22
        u = (t % period) / period
        going_left = u < 0.5
        x = int(304 - span * (u * 2 if going_left else 2 - u * 2))
        pause = abs(u - 0.5) < 0.06 or u > 0.94
        img = look.proc(pw.frame(t, state="peck" if pause else "walk"), "pigeon_walk")
        shadow(cv, x, STAND_Y + 1, SHADOW["pigeon_walk"])
        put_img(cv, img, pw.anchor, x, STAND_Y + 1, flip=not going_left)
    bus = movers.get("bus")
    if look.scene != "house" and EASTER_BUS.get(look.key) == lap and movers.get("bus_ikame"):
        bus = movers["bus_ikame"]
    if bus:
        bw = bus.frames[0].width
        bx = bus_x(t, bw)
        if bx is not None:
            X = int(round(bx))
            if BUS_T_STOP <= t < BUS_T_GO:
                img = bus.frame(t - BUS_T_STOP, state="idle")
            else:
                img = bus.frames[bus.states["drive"][int(abs(bx) / 4) % 3]]
            for dx in range(0, bw, 30):                      # long flat shadow on the road
                shadow(cv, X + dx + 15, WHEEL_Y + 2, 30, h=3, k=0.72)
            cv.alpha_composite(look.proc(img, "bus32"), (X - bus.anchor[0], WHEEL_Y - bus.anchor[1]))
            if look.grade:                                   # headlight
                lights.append((X + 1, WHEEL_Y - 18, 7, 5, "glow", 0.45))
                lights.append((X - 16, WHEEL_Y - 1, 22, 3, "lamp", 0.22))
            puff = movers.get("puff")
            if puff and BUS_T_GO - 0.3 <= t < BUS_T_GO + 2.5:   # exhaust when pulling away
                for j in range(4):
                    age = t - (BUS_T_GO - 0.3) - j * 0.35
                    if 0 <= age < 1.4:
                        px_ = X + bw + 2 + int(age * 10); py_ = WHEEL_Y - 9 - int(age * 6)
                        cv.alpha_composite(look.proc(puff.frames[min(3, int(age / 0.35))], "bus_puff"),
                                           (px_ - 3, py_ - 3))
    mo = movers.get(look.get("moto") or "")
    if mo and MOTO_T0 <= t < MOTO_T1:                        # Tết: peach tree on a motorbike, right -> left
        v = (W + 70) / (MOTO_T1 - MOTO_T0)
        x = int(W + 8 - (t - MOTO_T0) * v)
        shadow(cv, x + 18, WHEEL_Y + 1, 30)
        img = look.proc(mo.frames[int(x / 3) % 3], "moto_dao")
        put_img(cv, img, mo.anchor, x, WHEEL_Y)
    fb = movers.get("bike_flowers_" + look.get("bike", BIKE_LOAD.get(look.key, "ha")))
    if fb and look.scene != "house" and "bike_flowers" not in hide:   # flower vendor's bicycle, near lane
        u = (t - BIKE_T0) % LOOP
        if u < BIKE_DUR:
            x = int(-30 + u * (W + 60) / BIKE_DUR)
            shadow(cv, x, WHEEL_Y + 2, 34)
            img = look.proc(fb.frame(t), "bike_flowers")
            put_img(cv, img, fb.anchor, x, WHEEL_Y + 1)
            if look.grade in ("dusk", "night"):
                lights.append((x + 10, WHEEL_Y - 18, 5, 4, "glow", 0.35))
    birds = look.get("birds", "sparrow")
    b = movers.get("bird")
    if birds == "sparrow" and b and "bird" not in hide:      # sparrow crossing, twice per loop
        x = int(W + 20 - ((t - 1.0) * (W + 200) / 12.0) % (W + 200))
        y = int(40 + 6 * math.sin(t * 2 * math.pi / 4))
        cv.alpha_composite(look.proc(b.frame(t), "sparrow_fly"), (x - b.anchor[0], y - b.anchor[1]))
    sw = movers.get("swallow")
    if birds == "swallow" and sw:                            # Tết swallows (én báo xuân): swooping
        for k in range(3):
            per = 8.0
            u = ((t + k * 2.9) % per) / per
            x = int(W + 20 - u * (W + 60))
            y = int(58 + k * 9 + 18 * math.sin(2 * math.pi * u * 2 + k))
            cv.alpha_composite(sw.frame(t, offset=k * 0.21), (x - sw.anchor[0], y - sw.anchor[1]))
    pf = movers.get("pigeon_fly")
    if pf and "pigeon_fly" not in hide:                      # a small flock crossing high, twice per loop
        for k, (dx, dy) in enumerate(((0, 0), (14, -5), (26, 3))):
            x = int(W + 30 + dx - ((t - 4.0) * (W + 260) / 12.0) % (W + 260))
            y = int(22 + dy + 3 * math.sin(t * 2 * math.pi / 3 + k))
            cv.alpha_composite(look.proc(pf.frame(t, offset=k * 0.13), "pigeon_fly"),
                               (x - pf.anchor[0], y - pf.anchor[1]))
    for pkey, count, seed, style in look.get("particles", [("petal", 14, 7, "fall")]):
        p = movers.get(pkey)
        if p:
            particles(cv, t, p, look, count, seed, style)


def particles(cv, t, p, look, count, seed, style):
    rnd = random.Random(seed)
    for k in range(count):
        if style == "blow":                                  # autumn leaves blown in from the left
            x0 = rnd.uniform(-30, 220); y0 = rnd.uniform(30, 150)
            vx = rnd.uniform(14, 26); vy = rnd.uniform(6, 11); drift = vx
        else:
            x0 = rnd.uniform(CANOPY_BOX[0], CANOPY_BOX[2]); y0 = rnd.uniform(CANOPY_BOX[1] + 20, CANOPY_BOX[3])
            vy = rnd.uniform(9, 16) * (2.2 if style == "rain" else 1.0); drift = rnd.uniform(6, 14); vx = drift
        phase = rnd.uniform(0, 20)
        life = (STAND_Y - y0) / vy
        if style == "blow":
            life = min(life, (W + 5 - x0) / vx)
        period = LOOP / max(1, round(LOOP / (life + rnd.uniform(0.5, 3))))
        if period < life:
            period = LOOP / max(1, int(LOOP / life))
        tt = (t + phase) % period
        if tt > life:
            continue
        x = int(x0 + drift * tt + 3 * math.sin(tt * 2 + k))
        y = int(y0 + vy * tt + (2 * math.sin(tt * 3 + k) if style == "blow" else 0))
        if 0 <= x < W:
            img = look.proc(p.frame(tt, offset=k), "petal")
            cv.alpha_composite(img, (x - p.anchor[0], y - p.anchor[1]))


def check_loop(sprites: dict):
    """Warn about frame cycles that don't divide LOOP (they would jump at the loop seam)."""
    for key, s in sprites.items():
        if not s.fps:
            continue
        for st, idx in (s.states or {"all": list(range(len(s.frames)))}).items():
            n = len(idx)
            if n > 1 and abs((LOOP * s.fps) % n) > 1e-6:
                print(f"  loop warning: {key} state {st}: {n} frames @ {s.fps} fps")


def load_all(look: Look):
    sprites = {(g, n): s for g, n, _ in season_order(look) if (s := load(g, n))}
    movers = {k: load("actors", n) for k, n in
              (("walker", "walker_nonla"), ("lion_dance", "lion_dance"), ("bird", "sparrow_fly"),
               ("swallow", "swallow"), ("pigeon_walker", "pigeon_walk"), ("pigeon_fly", "pigeon_fly"),
               ("bus", "bus32"), ("bus_ikame", "bus_ikame"), ("puff", "bus_puff"), ("student", "student_walk"),
               ("lantern_kid_a", "lantern_kid_a"), ("lantern_kid_b", "lantern_kid_b"), ("moto_dao", "moto_dao"),
               ("petal_peach", "petal_peach"), ("leaf_yellow", "leaf_yellow"))}
    for kind in ("xuan", "ha", "thu", "dong"):
        movers[f"bike_flowers_{kind}"] = load("actors", f"bike_flowers_{kind}")
    movers["petal"] = load("shelter", "petals")
    return sprites, {k: v for k, v in movers.items() if v}


def scene_dir(scene: str) -> Path:
    tag = SCENES[scene][2]
    return OUT / tag if tag else OUT


def encoder(path: Path, crf: int):
    """ffmpeg reading raw 1920x1080 RGB frames on stdin (the x5 upscale now happens in Python, see sky_soft)."""
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W * 5}x{H * 5}", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264",
                             "-pix_fmt", "yuv420p", "-crf", str(crf), "-r", "30", str(path)], stdin=subprocess.PIPE)


def finish(p):
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg failed")


def hi_frame(season_dir: Path, i: int, key: str | None = None) -> np.ndarray:
    """Logical frame i of a rendered season (+ its sky mask) -> 1920x1080 RGB array."""
    key = key or season_dir.name
    f = np.asarray(Image.open(season_dir / "_frames" / f"{i:05d}.png").convert("RGB"))
    mp = season_dir / "_mask" / f"{i:05d}.png"
    m = np.asarray(Image.open(mp)) > 0 if mp.exists() else None
    return sky_soft.to_hi(f, m, key, i / FPS)


def render_season(key: str, anim: float | None, still_t: float = 5.0, scene: str = "house"):
    look = Look(key, scene)
    sprites, movers = load_all(look)
    out = scene_dir(scene) / key
    out.mkdir(parents=True, exist_ok=True)
    check_loop({**sprites, **{("mover", k): v for k, v in movers.items()}})
    ms: list = []
    still = render(still_t, sprites, movers, look, ms).convert("RGB")
    still.save(out / "frame.png")
    Image.fromarray(sky_soft.to_hi(np.asarray(still), ms[0], key, still_t)).save(out / "frame@5x.png")
    print(key, "layers:", len(sprites), "movers:", len(movers), "->", out / "frame@5x.png")
    if anim:
        fdir, mdir = out / "_frames", out / "_mask"
        for d in (fdir, mdir):
            d.mkdir(exist_ok=True)
            for f in d.glob("*.png"):
                f.unlink()
        enc = encoder(out / "loop.mp4", 16)
        for i in range(int(anim * FPS)):
            ms = []
            im = render(i / FPS, sprites, movers, look, ms).convert("RGB")
            im.save(fdir / f"{i:05d}.png")                                       # logical size
            if ms[0] is not None:
                Image.fromarray(ms[0]).save(mdir / f"{i:05d}.png")               # 1-bit: soft sky visible here
            enc.stdin.write(sky_soft.to_hi(np.asarray(im), ms[0], key, i / FPS).tobytes())
        finish(enc)
        print("anim:", out / "loop.mp4")


MONTAGE_TRANS = 2.0      # seconds of the wind-gust season change (compose/transition.py; audio_gif follows it)


def montage(keys, loops=1, trans=MONTAGE_TRANS, scene: str = "house"):
    """All seasons back to back (each `loops` x 24 s); a gust of wind sweeps each next season in.

    Season k plays its local frames tf .. tf + total - 1 (its first tf frames were already shown inside the gust that
    brought it in), so nothing jumps back in time after a transition, and the end wraps cleanly into the start."""
    import transition
    base = scene_dir(scene)
    n_loop = int(LOOP * FPS)
    tf = int(trans * FPS)
    enc = encoder(base / "bon_mua.mp4", 18)
    for si, k in enumerate(keys):
        nxt = keys[(si + 1) % len(keys)]
        total = n_loop * loops
        for i in range(total):
            im = hi_frame(base / k, i + tf)
            j = i - (total - tf)
            if j >= 0:                                       # last tf frames: the gust blows the next season in
                nb = hi_frame(base / nxt, j)
                im = transition.sweep(im, nb, j, tf, k, nxt, seed=si)
            enc.stdin.write(np.ascontiguousarray(im).tobytes())
    finish(enc)
    print("montage:", base / "bon_mua.mp4")


def main():
    anim = float(sys.argv[sys.argv.index("--anim") + 1]) if "--anim" in sys.argv else None
    still_t = float(sys.argv[sys.argv.index("--t") + 1]) if "--t" in sys.argv else 5.0
    scene = sys.argv[sys.argv.index("--scene") + 1] if "--scene" in sys.argv else "house"
    if "--montage" in sys.argv:                                  # only re-join the already rendered seasons
        montage(ORDER_OF_SEASONS, scene=scene)
        return
    if "--all" in sys.argv:
        # the five seasons render side by side (one process each); --jobs 1 for the old one-at-a-time behaviour
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else len(ORDER_OF_SEASONS)
        if jobs > 1:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(max_workers=jobs) as ex:
                for f in [ex.submit(render_season, k, anim, still_t, scene) for k in ORDER_OF_SEASONS]:
                    f.result()
        else:
            for k in ORDER_OF_SEASONS:
                render_season(k, anim, still_t, scene)
        if anim:
            montage(ORDER_OF_SEASONS, scene=scene)
        return
    key = sys.argv[sys.argv.index("--season") + 1] if "--season" in sys.argv else "ha"
    render_season(key, anim, still_t, scene)


if __name__ == "__main__":
    main()
