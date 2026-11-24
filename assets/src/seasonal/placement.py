from common import *
import json
D = pathlib.Path(__file__).resolve().parents[2] / "out" / G

def load(name, f=0):
    m = json.loads((D / f"{name}.json").read_text())
    im = Image.open(D / f"{name}.png").convert("RGBA")
    fw = m["frameW"]
    return im.crop((f * fw, 0, (f + 1) * fw, im.height)), tuple(m["anchor"])

def put_(bg, name, x, y, f=0):
    im, a = load(name, f)
    place(bg, im, x, y, a)

bg = mock_scene()
put_(bg, "moon_full", 400, 50)
put_(bg, "lantern_string_trungthu", 60, 100) if False else None
im, a = load("lantern_string_trungthu"); bg.alpha_composite(im, (52, 96))
im, a = load("banner_tet"); bg.alpha_composite(im, (300 - 50 + 0, 90)) if False else None
for name, x in (("drummer_R", 90), ("lion_dance_R", 140), ("ong_dia_R", 196), ("kid_star_lantern_R", 330), ("kid_carp_lantern_R", 380)):
    put_(bg, name, x, WALK_FAR_BASE_Y, 2)
put_(bg, "vendor_corn_dong", VENDOR_X + 40, VENDOR_BASE_Y)
put_(bg, "pot_dao", 150, 176); put_(bg, "pot_quat", 288, 176)
put_(bg, "flag_vn", 120, 176)
im, a = load("banner_tet"); bg.alpha_composite(im, (310, 120)) if False else None
put_(bg, "smoke_puff", VENDOR_X + 40 - 10, VENDOR_BASE_Y - 18, 2)
put_(bg, "sun", 60, 30, 0)
put_(bg, "rainbow", 330, 160)
put_(bg, "firecracker_deco", 20, 110)
# fog + rain overlay on right side to test seam
save_mock(bg, G, "placement_check")

# rain seam test: tile 4x2 of each tile on mock frame
bg2 = mock_scene()
for name, yoff in (("rain_drizzle_tile", 0), ("rain_heavy_tile", 0)):
    im, a = load(name, 0)
    x0 = 0 if "drizzle" in name else 240
    for ty in range(0, H, 120):
        for tx in range(x0, x0 + 240, 120):
            bg2.alpha_composite(im, (tx, ty))
save_mock(bg2, G, "rain_tile_check")
