"""Season looks for compose/gif_frame.py (--season xuan | ha | mua | thu | dong).

Each season is a dict of overrides on top of the summer base scene:
  sky        (group, name) that replaces env/sky
  add        [(after_name, (group, name, place))]  extra layers inserted into ORDER after the named layer
  place      {place_key: [positions]}              extra / overridden PLACE entries
  hide       {names}                               layers, place keys or movers to skip
  recolor    {sprite: {palette_from: palette_to}}  clothes etc. (applied before grading)
  bloom_leaf bougainvillea tones that turn to leaves (fewer flowers out of season)
  grade      None | "dusk" | "night" | "overcast"  per-colour light grade (pixel-crisp, flat areas stay flat)
  soft       {layer: [rects]} lit interiors that get the soft warm grade instead (full-canvas layers)
  soft_all   {sprites} that get the soft grade (people inside the lit shop)
  emit       {layer: [(rect|None, {from: to})]}    pixels that glow: they skip the grade and take a lit colour
  glows      [(cx, cy, rx, ry, colour, k)]          static light pools drawn after the scene
  glow_place {place_key: (dy, r, colour, k)}       a light pool on every placed instance (lanterns)
  walker / students / birds / moto / particles     mover choices (see gif_frame.draw_movers)
  fx         {"stars", "fireworks", "fog", "rain", "fairy"}
"""
LAMP_WIN = {"glass": "lamp", "glass_l": "glow", "glass_d": "or_l", "white": "glow", "sb": "or", "teal": "or_l"}
BUS_LIT = {"glass_d": "lamp", "glass": "glow", "glass_l": "white", "white": "white", "lamp": "glow", "glow": "glow",
           "red_l": "red_l", "yl_l": "yl_l"}
LANTERN_LIT = {"red": "red_l", "red_d": "red", "red_l": "or_l", "gold": "yl_l", "or": "or_l", "wood_d": "wood_d"}
WINDOWS = [(178, 82, 193, 114), (226, 82, 241, 114), (207, 31, 229, 47)]
SHOP = (157, 127, 300, 186)
SHELTER_DRY = (36, 155, 176, 199)
NIGHT_BIRDS = {"pigeon_perch", "sparrow_perch", "sparrow_stool", "pigeon_peck", "pigeon_walker", "pigeon_fly", "bird"}

SEASONS = {
    # ------------------------------------------------------------------ summer noon (the approved styleframe)
    "ha": dict(title="Hạ · trưa nắng"),

    # ------------------------------------------------------------------ Tết morning
    "xuan": dict(
        title="Xuân · sáng mùng Một Tết",
        sky=("season", "sky_xuan"),
        add=[("grandma_water", ("actors", "banner_tet", "banner")),
             ("house", ("actors", "lantern_red", "lanterns_tet")),
             ("house", ("actors", "flag_vn", "flag")),
             ("dog_lie", ("actors", "kumquat", "kumquat"))],
        place={"banner": [(174, 106)], "lanterns_tet": [(166, 126), (292, 126)],
               "flag": [(299, 117)], "kumquat": [(296, 197)]},
        recolor={"woman_wait": {"yl_l": "red_l", "yl": "red"}},
        bloom_leaf=["bl_k"],
        birds="swallow", moto="moto_dao",
        particles=[("petal_peach", 10, 7, "fall"), ("petal", 5, 9, "fall")],
    ),

    # ------------------------------------------------------------------ summer shower
    "mua": dict(
        title="Hạ · mưa rào",
        sky=("season", "sky_mua"),
        grade="overcast",
        hide=NIGHT_BIRDS | {"oldman_tea", "steam", "grandma_water"},
        place={"cat_black": [(124, 188)]},                    # the cat shelters on the bench next to the woman
        recolor={"walker": {"wb_l": "pb_l", "wb": "pb"},     # blue raincoat under the nón lá
                 "student": {"white": "yl_l", "grey_hl": "yl", "red": "yl"}},  # yellow kid's raincoat
        soft={"house": [SHOP]}, soft_all={"shopkeeper"},
                particles=[("petal", 16, 7, "rain")],
        fx={"rain": dict(density=3.0, exclude=[SHELTER_DRY])},
    ),

    # ------------------------------------------------------------------ Trung Thu dusk
    "thu": dict(
        title="Thu · tối Trung Thu",
        sky=("season", "sky_thu"),
        grade="dusk",
        add=[("house", ("actors", "star_lantern", "stars_shop")),
             ("shelter_front", ("actors", "lantern_red", "lanterns_shelter"))],
        place={"stars_shop": [(167, 126), (182, 126), (291, 126)],
               "lanterns_shelter": [(52, 155), (76, 155)]},
        hide={"sparrow_perch", "sparrow_stool", "bird"},
        soft={"house": [SHOP]}, soft_all={"shopkeeper"},
        emit={"house": [(r, LAMP_WIN) for r in WINDOWS], "bus32": [(None, BUS_LIT)],
              "star_lantern": [(None, LANTERN_LIT)], "lantern_red": [(None, LANTERN_LIT)],
              "lantern_kid_a": [((10, 0, 26, 34), LANTERN_LIT)], "lantern_kid_b": [((10, 0, 26, 34), LANTERN_LIT)],
              "shelter_back": [(None, {"glow": "glow", "lamp": "lamp"})]},
        glows=[(236, 160, 40, 26, "lamp", 0.16), (236, 194, 56, 6, "lamp", 0.22)],
        glow_place={"stars_shop": (10, 9, "or_l", 0.30), "lanterns_shelter": (8, 8, "or_l", 0.30)},
        bloom_leaf=["bl_k", "bl_d"],
        walker="lion_dance", students=[("lantern_kid_a", 0.0, 0), ("lantern_kid_b", 0.7, -16)], birds=None,
        particles=[("leaf_yellow", 12, 5, "blow"), ("petal", 4, 9, "fall")],
        fx={"city_lights": 0.5},
    ),

    # ------------------------------------------------------------------ New Year's Eve, winter fog
    "dong": dict(
        title="Đông · đêm Giao thừa sương mù",
        sky=("season", "sky_dong"),
        grade="night",
        hide=NIGHT_BIRDS | {"grandma_water"},
        recolor={"woman_wait": {"yl_l": "wp_l", "yl": "wp"},              # pink puffer coat
                 "oldman_tea": {"wc_l": "leaf_d", "wc": "leaf_k"},         # army-green coat
                 "shopkeeper": {"wb_l": "sb", "wb": "sb_d"},
                 "walker": {"wb_l": "trunk_l", "wb": "trunk"},
                 "student": {"white": "red_l", "grey_hl": "red"}},
        soft={"house": [SHOP]}, soft_all={"shopkeeper"},
        emit={"house": [(r, LAMP_WIN) for r in WINDOWS[:2]], "bus32": [(None, BUS_LIT)],
              "cat_black": [(None, {"yl_l": "yl_l"})],
              "shelter_back": [(None, {"glow": "glow", "lamp": "lamp", "white": "glow", "glass_l": "glass_l",
                                       "paper": "glow"})]},
        glows=[(236, 160, 40, 26, "lamp", 0.20), (236, 194, 60, 6, "lamp", 0.26), (100, 176, 54, 20, "glass_l", 0.10)],
        bloom_leaf=["bl_k", "bl_d", "bl"],
        birds=None,
        particles=[("petal", 3, 9, "fall")],
        fx={"stars": True, "fireworks": True, "fog": True, "fairy": True, "city_lights": 1.0},
    ),
}
ORDER_OF_SEASONS = ["xuan", "ha", "mua", "thu", "dong"]

# ------------------------------------------------------------------------------------------------------------------
# Park scene (bản 6): low kiosk (layer alias "kiosk") + park behind. Keys given here REPLACE the house-scene values,
# except "recolor", which is merged (clothes recolours stay, tree recolours are added).
K_OPEN = (156, 148, 293, 185)
SCONCES = [(182, 118, 189, 127), (282, 118, 289, 127)]
PARK_LAMP = (315, 106, 330, 118)
KIOSK_LIT = {"lamp": "lamp", "glow": "glow"}
SCONCE_LIT = {"glass_l": "glow", "white": "glow", "glass": "lamp"}
LAMP_LIT = {"white": "glow", "glass_l": "lamp"}
K_SIGN = (196, 116, 274, 136)
PARK_EMIT_BIKE = {"bike_flowers": [(None, {"lamp": "lamp"})]}
PARK_EMIT = {"kiosk": [(None, KIOSK_LIT), (K_SIGN, {"paper": "paper", "yl_l": "yl_l"})] + [(r, SCONCE_LIT) for r in SCONCES],
             "park_front": [(PARK_LAMP, LAMP_LIT)],
             "bus32": [(None, BUS_LIT)], **PARK_EMIT_BIKE}
PARK_GLOWS = [(225, 166, 62, 20, "lamp", 0.16), (225, 194, 70, 6, "lamp", 0.22),
              (186, 123, 9, 9, "lamp", 0.22), (286, 123, 9, 9, "lamp", 0.22),
              (322, 112, 15, 11, "glow", 0.26), (322, 170, 22, 7, "lamp", 0.14)]
BANG_SPRING = {"leaf_k": "leaf_d", "leaf_d": "leaf", "leaf": "leaf_l", "leaf_l": "leaf_hl"}     # fresh new leaves
BANG_AUTUMN = {"leaf_hl": "yl_l", "leaf_l": "yl", "leaf": "or", "leaf_d": "or_d", "leaf_k": "tc_d"}
BIKE_RAIN = {"wb_l": "pb_l", "wb": "pb"}            # the vendor wears a blue raincoat (season flowers: park/bike.py)
BANG_WINTER = {"leaf_hl": "or_l", "leaf_l": "red_l", "leaf": "red", "leaf_d": "red_d", "leaf_k": "tc_d"}  # bàng đỏ
PARK = {
    "xuan": dict(
        add=[("shopkeeper", ("actors", "lantern_red", "lanterns_tet")),      # (no text banner: client, 6c)
             ("park_front", ("actors", "flag_vn", "flag")),
             ("dog_lie", ("actors", "kumquat", "kumquat"))],
        place={"lanterns_tet": [(174, 114), (294, 114)],
               "flag": [(323, 140)], "kumquat": [(290, 197)]},
        recolor={"park_bang": BANG_SPRING},
    ),
    "mua": dict(soft={"kiosk": [K_OPEN]}, place={}, recolor={"bike_flowers": BIKE_RAIN}),   # cat already on the bench
    "thu": dict(
        add=[("shopkeeper", ("actors", "star_lantern", "stars_shop")),
             ("shelter_front", ("actors", "lantern_red", "lanterns_shelter"))],
        place={"stars_shop": [(176, 114), (291, 114)], "lanterns_shelter": [(52, 155), (76, 155)]},
        soft={"kiosk": [K_OPEN]},
        emit={**PARK_EMIT, "star_lantern": [(None, LANTERN_LIT)], "lantern_red": [(None, LANTERN_LIT)],
              "lantern_kid_a": [((10, 0, 26, 34), LANTERN_LIT)], "lantern_kid_b": [((10, 0, 26, 34), LANTERN_LIT)],
              "shelter_back": [(None, {"glow": "glow", "lamp": "lamp"})]},
        glows=PARK_GLOWS,
        recolor={"park_bang": BANG_AUTUMN, "park_xacu": {"leaf_hl": "yl_l"}},
    ),
    "dong": dict(
        soft={"kiosk": [K_OPEN]},
        emit={**PARK_EMIT, "cat_black": [(None, {"yl_l": "yl_l", "grey_k": "nt_l"})],   # moonlit rim: cat reads at night
              "shelter_back": [(None, {"glow": "glow", "lamp": "lamp", "white": "glow", "glass_l": "glass_l",
                                       "paper": "glow"})]},
        glows=[(225, 166, 62, 20, "lamp", 0.20), (225, 194, 74, 6, "lamp", 0.26), (100, 176, 54, 20, "glass_l", 0.10),
               (186, 123, 10, 10, "lamp", 0.28), (286, 123, 10, 10, "lamp", 0.28),
               (322, 112, 18, 13, "glow", 0.32), (322, 170, 26, 8, "lamp", 0.18)],
        recolor={"park_bang": BANG_WINTER},
        fairy_row=(152, 298, 115),
    ),
}
PARK_TOWERS = [(0, 12, 74), (176, 188, 28), (262, 273, 36), (296, 309, 46), (312, 322, 82), (352, 363, 46),
               (372, 384, 62)]                                     # = assets/src_gif/park/park.py TOWERS
PARK_COMMON = dict(far_blocks=PARK_TOWERS, far_rows_end=148, deck_lamps=False, fw_region=(232, 6, 384, 74))


def season_for(key: str, scene: str = "house") -> dict:
    S = dict(SEASONS[key])
    if scene == "house":
        return S
    S.update(PARK_COMMON)
    for k, v in PARK.get(key, {}).items():
        S[k] = {**S.get("recolor", {}), **v} if k == "recolor" else v
    if "grandma_water" in S.get("hide", ()):                       # no exercise in the rain or at midnight
        S["hide"] = set(S["hide"]) | {"grandma_ex"}
    if "shopkeeper" in S.get("soft_all", ()):                       # the café cat is lit like the barista
        S["soft_all"] = set(S["soft_all"]) | {"cat_tabby"}
    return S


# ------------------------------------------------------------------------------------------------------------------
# 6c: smooth gradient skies (client: "trời nền gradient, không cần pixel"). (y as a fraction of the frame, hex colour)
# The pixel clouds / moon / streaks are drawn on top from the "<sky>_fg" overlays.
SKY_GRAD = {
    "ha": [(0.0, "#7fb0e0"), (0.45, "#b0d6f8"), (0.75, "#d6eafb"), (1.0, "#eaf4fb")],
    "xuan": [(0.0, "#98c5ee"), (0.5, "#cfe6fa"), (0.8, "#f2eee2"), (1.0, "#fbf0db")],
    "mua": [(0.0, "#5c6573"), (0.5, "#939dab"), (1.0, "#c3cbd3")],
    "thu": [(0.0, "#3d3d7a"), (0.2, "#5e5292"), (0.4, "#94649d"), (0.58, "#d4769a"), (0.74, "#f39c8c"),
            (0.9, "#ffc08e"), (1.0, "#ffd3a0")],
    "dong": [(0.0, "#0a0f27"), (0.35, "#151e46"), (0.65, "#22305f"), (1.0, "#34477d")],
}
MOON_GLOW = {"thu": (336, 34, 30, "#fff1c9", 0.55)}           # soft halo around the full moon (cx, cy, r, colour, k)
