"""Compose the review stills (one per season beat) from the real asset layers.

    .venv/bin/python compose/stills.py            # all
    .venv/bin/python compose/stills.py xuan thu_dem
"""
from __future__ import annotations

import random
import sys

import numpy as np
from PIL import Image, ImageFilter

from lib import ROOT, OUT, Scene, frame
from tools.layout import *

STILLS = ROOT / "review" / "stills"
SH = (136, 84)  # every shelter layer's top-left


def has(group: str, name: str) -> bool:
    return (OUT / group / f"{name}.json").exists()


# ------------------------------------------------------------------ shared builders
def backdrop(s: Scene, season: str, sky: list[str], clouds: list[tuple[str, int, int]] = (),
             celestial: tuple[str, int, int] | None = None, decor: str | None = None) -> None:
    s.sky(sky)
    if celestial:
        n, x, y = celestial
        s.at("seasonal", n, x, y)
    for n, x, y in clouds:
        s.at("env", n, x, y, mode="tl")
    s.at("env", "buildings", 0, 32, mode="tl")
    if decor:
        s.at("env", decor, 0, 32, mode="tl")
    s.at("env", "ground", 0, 158, mode="tl")
    s.at("env", "tree_trunk", 350, 30, mode="tl")
    s.at("env", f"tree_canopy_{season}", 350, 30, mode="tl")
    s.at("env", "lamp", 288, 90, mode="tl")


def shelter(s: Scene, season: str, waiting: list[tuple[str, int, int]] = (), decor: list[str] = (),
            bloom_frame: int = 0, stool: bool = True) -> None:
    s.at("shelter", "shelter_back", *SH, mode="tl")
    s.at("shelter", "seats", *SH, mode="tl")
    for n, x, y in waiting:
        if has("characters", n):
            s.at("characters", n, x, y)
    s.at("shelter", "shelter_front", *SH, mode="tl")
    s.at("shelter", f"bougainvillea_{season}", *SH, i=bloom_frame, mode="tl")
    for d in decor:
        s.at("shelter", d, *SH, mode="tl")
    if stool:
        s.at("shelter", "stool_red", 282, 177)


def actor(s: Scene, group: str, name: str, x: int, y: int, i: int = 0, shadow: int = 0, state: str | None = None) -> None:
    if not has(group, name):
        print("  (missing)", group, name)
        return
    if shadow:
        s.shadow(x, y + 1, shadow, 3, 0.28)
    s.at(group, name, x, y, i=i, state=state)


def particles(s: Scene, names: list[str], n: int, box: tuple[int, int, int, int], seed: int) -> None:
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        nm = rnd.choice(names)
        s.at("seasonal", nm, rnd.randint(x0, x1), rnd.randint(y0, y1), i=rnd.randint(0, 3))


def lamp_on(s: Scene, amount: float = 0.55) -> None:
    if has("env", "lamp_lit"):
        bloom(s, full("env", "lamp_lit", 288, 90), 2, 0.9)
    glow(s, 310, 99, 46, (255, 220, 140), amount)


def glow(s: Scene, x: int, y: int, r: float, rgb: tuple[int, int, int], amount: float = 0.6) -> None:
    a = np.asarray(s.img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2) / r
    f = np.clip(1 - d, 0, 1) ** 2 * amount
    a[..., :3] += f[..., None] * np.array(rgb, np.float32)
    s.img = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def bloom(s: Scene, layer: Image.Image, radius: float = 4, amount: float = 0.9, opacity: float = 1.0) -> None:
    """Crisp emissive layer + soft blurred halo on top (additive)."""
    s.overlay(layer, opacity=opacity)
    b = layer.filter(ImageFilter.GaussianBlur(radius))
    s.add_light(b, amount)


def full(group: str, name: str, x: int, y: int, i: int = 0) -> Image.Image:
    f, _ = frame(group, name, i)
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    l.alpha_composite(f, (x, y)) if x >= 0 and y >= 0 else None
    return l


def full_anchor(group: str, name: str, x: int, y: int, i: int = 0) -> Image.Image:
    f, m = frame(group, name, i)
    ax, ay = m["anchor"]
    l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, oy = x - ax, y - ay
    cx, cy = max(0, -ox), max(0, -oy)
    l.alpha_composite(f.crop((cx, cy, f.width, f.height)), (ox + cx, oy + cy))
    return l


def cat(s: Scene, state: str, x: int, i: int = 0, coat: str = "") -> None:
    name = f"cat_{coat}_R" if coat and has("characters", f"cat_{coat}_R") else "cat_R"
    if has("characters", name):
        s.shadow(x, CAT_BASE_Y + 1, 26, 4, 0.3)
        s.at("characters", name, x, CAT_BASE_Y, i=i, state=state)


def first(group: str, *names: str) -> str:
    """First existing asset name (lets stills use new art as soon as it lands)."""
    for n in names:
        if has(group, n):
            return n
    return names[-1]


def birds(s: Scene, name: str, pts: list[tuple[int, int, int]]) -> None:
    for x, y, i in pts:
        if has("characters", name):
            s.at("characters", name, x, y, i=i, state="fly" if "sparrow" in name else None)


# ------------------------------------------------------------------ the stills
def xuan() -> Scene:
    s = Scene()
    backdrop(s, "xuan", ["sky", "sky_l", "sky_l", "grey_l", "sand"],
             clouds=[("cloud_l1", 150, 4), ("cloud_s1", 330, 18), ("cloud_s2", 18, 30)], decor="buildings_decor_xuan")
    s.at("seasonal", "banner_tet", 357, 104)
    s.at("seasonal", "pot_dao", 128, 177)
    s.at("seasonal", "pot_quat", 312, 177)
    s.at("seasonal", "pot_quat", 336, 176)
    shelter(s, "xuan", waiting=[("sit_elder_R", 205, SEAT_BASE_Y + 1)],
            decor=["decor_cau_doi_xuan", "decor_lanterns_xuan"])
    actor(s, "characters", "walk_aodai_xuan_R", 96, WALK_FAR_BASE_Y, 2, shadow=10)
    actor(s, "characters", "walk_man_xuan_L", 300, WALK_FAR_BASE_Y, 4, shadow=10)
    actor(s, "vehicles", "moto_quat_xuan_L", 404, FAR_LANE_BASE_Y, shadow=26)
    actor(s, "vehicles", "sedan_red_L", 70, FAR_LANE_BASE_Y, shadow=62)
    actor(s, "vehicles", "moto_peach_R", 200, NEAR_LANE_BASE_Y, shadow=26)
    actor(s, "vehicles", "bike_peach_xuan_R", 330, NEAR_LANE_BASE_Y, shadow=26)
    birds(s, "swallow_R", [(60, 22, 0), (78, 30, 2), (96, 18, 1)])
    cat(s, "lick_paw", 384, 2)
    s.tint((255, 236, 214), "multiply", 0.35)             # soft warm morning
    s.tint((255, 214, 224), "screen", 0.10, 0, 120)       # pink haze in the sky
    s.tile("seasonal", "rain_drizzle_tile", 0, opacity=0.35)
    return s


def ha() -> Scene:
    s = Scene()
    backdrop(s, "ha", ["blue", "sky", "sky", "sky_l"], clouds=[("cloud_l2", 250, 10), ("cloud_s2", 120, 22)],
             celestial=("sun", 104, 20))
    shelter(s, "ha", waiting=[("sit_phone_ha_R", 214, SEAT_BASE_Y + 1), ("stand_wait_ha_R", 248, WAIT_BASE_Y + 2)])
    actor(s, "characters", "walk_schoolgirl_ha_R", 118, WALK_FAR_BASE_Y, 1, shadow=10)
    actor(s, "characters", "walk_tshirt_ha_L", 352, WALK_FAR_BASE_Y, 3, shadow=10)
    actor(s, "vehicles", "moto_sun_ha_L", 120, FAR_LANE_BASE_Y, shadow=24)
    actor(s, "vehicles", "scooter_couple_L", 300, FAR_LANE_BASE_Y, shadow=26)
    actor(s, "vehicles", "sedan_white_R", 250, NEAR_LANE_BASE_Y, shadow=62)
    actor(s, "vehicles", "moto_man_R", 70, NEAR_LANE_BASE_Y, shadow=24)
    birds(s, "sparrow_R", [(310, 40, 1), (330, 34, 3)])
    cat(s, "sleep", 360, 0, coat="calico")
    s.tint((255, 246, 222), "screen", 0.12)               # harsh noon bleach
    return s


def ha_mua() -> Scene:
    s = Scene()
    backdrop(s, "ha", ["slate_d", "slate", "slate", "grey"],
             clouds=[("cloud_rain1", -10, -6), ("cloud_rain2", 250, -4), ("cloud_rain1", 330, 10)])
    s.at("env", "ground_wet", 0, 158, mode="tl")
    shelter(s, "ha", waiting=[("sit_phone_ha_R", 202, SEAT_BASE_Y + 1), ("stand_wait_ha_L", 236, WAIT_BASE_Y + 2),
                             ("sit_elder_R", 226, SEAT_BASE_Y + 1)], bloom_frame=2)
    s.at("shelter", "shelter_wet", *SH, mode="tl")
    actor(s, "characters", "run_rain_ha_R", 150, WALK_FAR_BASE_Y, 2)
    actor(s, "characters", "walk_umbrella_ha_L", 360, WALK_FAR_BASE_Y, 1)
    actor(s, "vehicles", "taxi_L", 380, FAR_LANE_BASE_Y)
    actor(s, "vehicles", "moto_poncho_ha_R", 120, NEAR_LANE_BASE_Y, 1)
    actor(s, "vehicles", "moto_poncho_ha_R", 290, NEAR_LANE_BASE_Y, 3)
    s.tint((150, 160, 190), "multiply", 0.55)
    taxi_lights = full("vehicles", "car_lights_L", 380 - 36, FAR_LANE_BASE_Y - 30 + 7)
    rnd = random.Random(7)
    for _ in range(26):
        s.at("seasonal", "splash", rnd.randint(0, W), rnd.choice([rnd.randint(186, 236), rnd.randint(244, 268)]), i=rnd.randint(0, 4))
    s.tile("seasonal", "rain_heavy_tile", 0, opacity=0.75)
    s.tile("seasonal", "rain_heavy_tile", 1, opacity=0.45, dx=37, dy=53)
    return s


def thu() -> Scene:
    s = Scene()
    backdrop(s, "thu", ["sky", "sky_l", "sand", "ochre", "gold"], clouds=[("cloud_l2", 40, 8), ("cloud_s1", 270, 24)])
    shelter(s, "thu", waiting=[("sit_elder_R", 212, SEAT_BASE_Y + 1)], bloom_frame=1)
    actor(s, "characters", "walk_cardigan_thu_L", 330, WALK_FAR_BASE_Y, 2, shadow=10)
    actor(s, "characters", "walk_kid_thu_L", 352, WALK_FAR_BASE_Y, 4, shadow=8)
    actor(s, "vehicles", "bus_L", 276, FAR_LANE_BASE_Y, state="drive", shadow=150)
    actor(s, "vehicles", "moto_man_R", 120, NEAR_LANE_BASE_Y, shadow=24)
    actor(s, "vehicles", "sedan_silver_R", 380, NEAR_LANE_BASE_Y, shadow=62)
    particles(s, ["petal_bloom"], 34, (110, 80, 470, 250), 3)
    particles(s, ["leaf_yellow", "leaf_orange", "leaf_yellow"], 22, (200, 40, 470, 262), 5)
    cat(s, "sit_idle", 300, 1, coat="black")
    s.tint((255, 214, 150), "multiply", 0.30)             # golden hour
    s.tint((255, 190, 120), "screen", 0.12, 0, 160)
    return s


def thu_dem() -> Scene:
    s = Scene()
    backdrop(s, "thu", ["ink", "navy", "navy", "slate_d", "plum"], celestial=("moon_full", 236, 26),
             decor="buildings_decor_thu")
    shelter(s, "thu", waiting=[("sit_phone_ha_R", 214, SEAT_BASE_Y + 1)], decor=["decor_lanterns_thu"])
    s.at("seasonal", "lantern_string_trungthu", 300, 94, mode="tl")       # strung lamp post -> bang tree
    kids = [("kid_star_lantern_R", 226), ("kid_carp_lantern_R", 250), ("kid_carp_lantern_R", 404), ("kid_star_lantern_R", 444)]
    for i, (n, x) in enumerate(kids):
        actor(s, "seasonal", n, x, WALK_FAR_BASE_Y + 1, i=i)
    lion_gold = first("seasonal", "lion_dance_gold_R", "lion_dance_R")
    road = [("drummer_R", 36, 0, None), ("dragon_dance_R", 132, 3, None), ("ong_dia_R", 232, 1, None),
            ("lion_dance_R", 290, 2, "rear"), (lion_gold, 362, 4, None), ("drummer_R", 420, 3, None)]
    for n, x, i, st in road:
        if not has("seasonal", n):
            print("  (missing)", n); continue
        m_states = frame("seasonal", n)[1]["states"]
        actor(s, "seasonal", n, x, FAR_LANE_BASE_Y + 2, i=i, state=st if st in m_states else None, shadow=30)
    actor(s, "vehicles", "moto_man_R", 120, NEAR_LANE_BASE_Y)
    s.tint((70, 80, 150), "multiply", 0.78)
    glow(s, 236, 26, 40, (220, 205, 160), 0.55)
    s.at("seasonal", "moon_full", 236, 26)                 # moon stays bright
    bloom(s, full("env", "buildings_lights", 0, 32), 3, 0.45, opacity=0.62)
    bloom(s, full("shelter", "shelter_night_light", *SH), 3, 0.5)
    lamp_on(s, 0.55)
    for n, x in kids:
        dx, dy = (11, -31) if "star" in n else (17, -9)
        glow(s, x + dx, WALK_FAR_BASE_Y + 1 + dy, 20, (255, 170, 90), 0.6)
    for x in range(306, 460, 13):
        glow(s, x, 104, 9, (255, 150, 90), 0.35)
    glow(s, 210, 108, 30, (255, 170, 110), 0.25)
    glow(s, 240, 196, 120, (255, 150, 90), 0.12)           # warm spill of the procession on the road
    return s


def dong() -> Scene:
    s = Scene()
    backdrop(s, "dong", ["slate", "grey", "grey", "grey_l"], clouds=[("cloud_rain2", 60, -8), ("cloud_rain1", 280, -14)])
    s.at("env", "ground_wet", 0, 158, mode="tl")
    shelter(s, "dong", waiting=[("sit_phone_dong_R", 202, SEAT_BASE_Y + 1), ("stand_wait_dong_R", 246, WAIT_BASE_Y + 2)],
            decor=["decor_lights_dong"])
    actor(s, "seasonal", "vendor_corn_dong", VENDOR_X, VENDOR_BASE_Y)
    for k, (dx, dy) in enumerate([(-13, -18), (-15, -30), (-12, -42)]):
        s.at("seasonal", "smoke_puff", VENDOR_X + dx, VENDOR_BASE_Y + dy, i=k * 2)
    actor(s, "characters", "walk_puffer_dong_R", 92, WALK_FAR_BASE_Y, 1, shadow=10)
    actor(s, "characters", "walk_coat_dong_L", 396, WALK_FAR_BASE_Y, 4, shadow=10)
    actor(s, "vehicles", "bike_daisy_dong_L", 150, FAR_LANE_BASE_Y, 1)
    actor(s, "vehicles", "moto_puffer_dong_R", 250, NEAR_LANE_BASE_Y)
    actor(s, "vehicles", "moto_peach_R", 410, NEAR_LANE_BASE_Y, 1)
    cat(s, "sleep", 70, 1, coat="tuxedo")
    s.tint((170, 182, 205), "multiply", 0.45)
    s.fog([(112, 10, 0.45), (150, 9, 0.55), (204, 8, 0.30)], seed=2)
    lamp_on(s, 0.45)
    glow(s, VENDOR_X - 10, VENDOR_BASE_Y - 8, 18, (255, 120, 50), 0.5)
    bloom(s, full("shelter", "decor_lights_dong", *SH), 2, 0.5)
    s.tile("seasonal", "rain_drizzle_tile", 1, opacity=0.4)
    return s


def dong_dem() -> Scene:
    s = Scene()
    backdrop(s, "dong", ["ink", "navy", "navy", "slate_d", "slate_d"], decor="buildings_decor_xuan")
    s.at("seasonal", "pot_dao", 128, 177)
    s.at("seasonal", "pot_quat", 312, 177)
    shelter(s, "dong", waiting=[("sit_phone_dong_R", 202, SEAT_BASE_Y + 1)], decor=["decor_lights_dong", "decor_lanterns_xuan"])
    fw = [("fw_peony_red", 118, 40, 5), ("fw_peony_gold", 252, 26, 7), ("fw_willow_gold", 380, 36, 8),
          ("fw_peony_cyan", 44, 58, 3), ("fw_ring_gold", 186, 56, 4), ("fw_peony_pink", 320, 64, 2),
          ("fw_crackle", 450, 70, 2), ("fw_rocket", 214, 92, 1), ("fw_rocket", 300, 108, 2)]
    watchers = [("watch_point_dong_R", 112), ("watch_couple_dong_R", 150), ("watch_shoulders_dong_R", 312),
                ("watch_phone_dong_L", 352), ("walk_coat_dong_L", 392)]
    for n, x in watchers:
        actor(s, "characters", n, x, WALK_FAR_BASE_Y, 0, shadow=10)
    actor(s, "vehicles", "moto_puffer_dong_L", 236, FAR_LANE_BASE_Y)
    actor(s, "vehicles", "moto_peach_R", 120, NEAR_LANE_BASE_Y)
    cat(s, "look_camera", 404, 0, coat="tuxedo")
    s.tint((60, 72, 140), "multiply", 0.80)
    bloom(s, full("env", "buildings_lights", 0, 32), 3, 0.4, opacity=0.55)
    bloom(s, full("shelter", "decor_lights_dong", *SH), 2, 0.6)
    lamp_on(s, 0.5)
    tints = {"red": (255, 80, 90), "gold": (255, 200, 90), "cyan": (90, 230, 255), "pink": (255, 110, 190), "green": (110, 220, 110)}
    for n, x, y, i in fw:
        if not has("seasonal", n):
            print("  (missing)", n); continue
        col = next((v for k, v in tints.items() if k in n), (255, 220, 160))
        glow(s, x, y, 46, col, 0.30)                       # sky flash around each burst
        bloom(s, full_anchor("seasonal", n, x, y, i), 2, 1.0)
    glow(s, 240, 170, 260, (255, 190, 140), 0.08)          # faint firelight on the street
    return s


ALL = {"xuan": xuan, "ha": ha, "ha_mua": ha_mua, "thu": thu, "thu_dem": thu_dem, "dong": dong, "dong_dem": dong_dem}

if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        sc = ALL[k]()
        p = sc.save(STILLS / f"{k}.png", scale=1)
        sc.save(STILLS / f"{k}@3x.png", scale=3)
        print("->", p)
