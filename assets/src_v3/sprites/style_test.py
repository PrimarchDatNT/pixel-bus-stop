"""Find a sprite recipe that keeps true colours: neutral SPRITE_STYLE, bus guided by the v2 shade25d bus."""
import sys
from pathlib import Path
from PIL import Image, ImageFilter
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
from tools.comfy import gen
from tools.style_v3 import SPRITE_STYLE, SPRITE, NEG, QUALITY

O = ROOT / "assets/out_v3/sprites/_test"; O.mkdir(parents=True, exist_ok=True)
# guide: v2 bus (226x70) x5 on white, blurred so the sampler doesn't keep pixel blocks
bus = Image.open(ROOT / "assets/out_v2/shade25d/bus_L.png").convert("RGBA")
bus = bus.resize((bus.width * 5, bus.height * 5), Image.LANCZOS)
g = Image.new("RGBA", (1344, 512), (255, 255, 255, 255)); g.alpha_composite(bus, ((1344 - bus.width) // 2, (512 - bus.height) // 2))
g = g.convert("RGB").filter(ImageFilter.GaussianBlur(4)); g.save(O / "guide_bus.png")

BUS = ("(yellow city bus:1.3), (red lower body stripe:1.2), single bus, long boxy modern city bus, flat roof, row of tinted windows, "
       "passengers silhouettes, driver behind front windshield, facing left, black wheels, solo, no text")
X = ", multiple vehicles, green bus, interior, double-decker"
jobs = sys.argv[1:] or ["bus_i2i", "bus_t2i", "moto"]
if "bus_i2i" in jobs:
    for dn in (0.6, 0.72):
        print(gen(f"{BUS}, {SPRITE_STYLE}, {SPRITE}", O, f"bus_i2i{int(dn*100)}", 1344, 512, 301, batch=2,
                  init=(O / "guide_bus.png", dn), neg=NEG + X, quality=QUALITY), flush=True)
if "bus_t2i" in jobs:
    print(gen(f"{BUS}, {SPRITE_STYLE}, {SPRITE}", O, "bus_t2i", 1344, 512, 302, batch=2, neg=NEG + X, quality=QUALITY), flush=True)
if "moto" in jobs:
    M = ("1girl riding a small step-through scooter, vietnamese woman, long light blue sun protection coat, face mask, "
         "white half helmet, gloves, side view, facing right, solo")
    print(gen(f"{M}, {SPRITE_STYLE}, {SPRITE}", O, "moto_sun", 1024, 1024, 303, batch=2,
              neg=NEG + ", sport bike, big motorcycle, wings", quality=QUALITY), flush=True)
