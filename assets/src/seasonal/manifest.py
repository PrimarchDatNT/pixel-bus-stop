from common import *
import json
D = pathlib.Path(__file__).resolve().parents[2] / "out" / G
meta = {  # layer, suggested x/y, season
 "pot_dao": ("near_sidewalk_props / shelter_decor", "x~148 or 290, y=176", "xuan"),
 "pot_quat": ("shelter_decor", "x~288, y=176", "xuan"),
 "banner_tet": ("shelter_decor", "top-centre x~240,y~96 (between pole/lamp)", "xuan"),
 "flag_vn": ("shelter_decor", "x~120/330,y=176 or on balconies", "xuan"),
 "firecracker_deco": ("shelter_decor", "hang from pole/lamp arm, top y~110", "xuan"),
 "kid_star_lantern": ("far_walkers", "y=178, walk along x; _R L->R, _L R->L", "thu"),
 "kid_carp_lantern": ("far_walkers", "y=178", "thu"),
 "lion_dance": ("far_walkers", "y=178", "thu"),
 "ong_dia": ("far_walkers", "y=178", "thu"),
 "drummer": ("far_walkers", "y=178", "thu"),
 "dragon_dance": ("far_walkers / far_lane", "y=178 (sidewalk) or road y~206; anchor feet centre", "thu, xuan"),
 "lion_dance_gold": ("far_walkers", "y=178 or road", "thu"),
 "fw_rocket": ("weather_fx (sky)", "rise from y~160 to burst point", "dong (giao thua)"),
 "fw_peony_red": ("weather_fx (sky)", "burst centre y~50-90, anywhere in sky", "dong"), "fw_peony_gold": ("weather_fx (sky)", "same", "dong"),
 "fw_peony_cyan": ("weather_fx (sky)", "same", "dong"), "fw_peony_pink": ("weather_fx (sky)", "same", "dong"), "fw_peony_green": ("weather_fx (sky)", "same", "dong"),
 "fw_ring_gold": ("weather_fx (sky)", "same", "dong"), "fw_willow_gold": ("weather_fx (sky)", "burst centre y~40-70", "dong"), "fw_crackle": ("weather_fx (sky)", "same, after a burst", "dong"),
 "moon_full": ("celestial", "centre ~(400,50), rise slowly", "thu"),
 "lantern_string_trungthu": ("shelter_decor", "top-left (52,96) ->(211,96) or similar", "thu"),
 "vendor_corn_dong": ("far_walkers", "x=334,y=176", "dong"),
 "smoke_puff": ("weather_fx", "anchor at brazier ~(x-13,y-18 of vendor), loop spawn", "dong"),
 "breath_puff": ("weather_fx", "at mouths of walkers", "dong"),
 "rain_drizzle_tile": ("weather_fx", "tile full frame, scroll y+", "xuan, dong"),
 "rain_heavy_tile": ("weather_fx", "tile full frame, scroll y+", "ha"),
 "splash": ("weather_fx", "random on sidewalk/road", "ha"),
 "ripple": ("weather_fx", "random on road puddles", "ha"),
 "petal_bloom": ("weather_fx", "from bougainvillea, drift", "thu"),
 "leaf_yellow": ("weather_fx", "from tree canopy", "thu"),
 "leaf_orange": ("weather_fx", "from tree canopy", "thu"),
 "leaf_red": ("weather_fx", "from tree canopy", "thu, dong"),
 "sun": ("celestial", "~(60,30)", "ha"),
 "rainbow": ("celestial", "bottom-centre on skyline y~160", "ha"),
 "glint": ("weather_fx", "random on wet ground", "ha"),
 "title_xuan": ("grading (top UI)", "centre (240,40)", "xuan"), "title_ha": ("grading (top UI)", "centre (240,40)", "ha"),
 "title_thu": ("grading (top UI)", "centre (240,40)", "thu"), "title_dong": ("grading (top UI)", "centre (240,40)", "dong"),
}
rows = ["# seasonal manifest", "", "| name | frame | frames/fps | anchor | layer | suggested x/y | season | notes |", "|---|---|---|---|---|---|---|---|"]
for j in sorted(D.glob("*.json")):
    m = json.loads(j.read_text())
    base = m["name"].rsplit("_", 1)[0] if m["name"].endswith(("_R", "_L")) else m["name"]
    lay, pos, se = meta.get(base, ("?", "?", "?"))
    st = f" states={list(m['states'])}" if len(m["states"]) > 1 else ""
    rows.append(f"| {m['name']} | {m['frameW']}x{m['frameH']} | {m['frames']}/{m['fps']} | {tuple(m['anchor'])} | {lay} | {pos} | {se} | {m['notes']}{st} |")
rows += ["", "Previews: `_preview/placement_check@3x.png`, `_preview/rain_tile_check@3x.png`.",
 "Rev 2: no baked glows. Bloom attach points relative to anchor (feet), _R: star lantern centre (+11,-31) (y -30 on frames 0,3; x +10..+12 sway); carp lantern body centre (+17,-9). For _L negate x. Round 3: lion_dance 64x64 (walk 6f + rear 4f states, ground row fh-2), dragon 164x52, fireworks play once (loop=False). Title frames now 64x26 (anchor centre); moon 34x34; drummer 6 frames. `_L` files are mirrors with mirrored anchors."]
(D / "MANIFEST.md").write_text("\n".join(rows))
