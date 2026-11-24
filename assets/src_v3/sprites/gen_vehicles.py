"""Generate vehicle sprite candidates (Animagine XL via ComfyUI). Usage: gen_vehicles.py [round] [asset ...]
Candidates -> assets/out_v3/sprites/vehicles/_cand/v3/. Final picks are listed in FINAL (seed/index) and cut by cut_vehicles.py."""
import sys
from pathlib import Path
from PIL import Image, ImageFilter
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
from tools.comfy import gen
from tools.style_v3 import SPRITE_STYLE, SPRITE, NEG, QUALITY

C = ROOT / "assets/out_v3/sprites/vehicles/_cand/v3"; C.mkdir(parents=True, exist_ok=True)
S = f"{SPRITE_STYLE}, {SPRITE}"
CAR_X = ", multiple vehicles, people, driver, green tint, front view, three-quarter view, from above, text, logo"
MOTO_X = ", sport bike, big motorcycle, kick scooter, wings, dragon, fantasy, multiple people, green tint, front view, three-quarter view"
BIKE_X = ", motorcycle, multiple people, green tint, front view, three-quarter view, fantasy, wings"

def guide_bus(blur):
    bus = Image.open(ROOT / "assets/out_v2/shade25d/bus_L.png").convert("RGBA")
    bus = bus.resize((bus.width * 5, bus.height * 5), Image.LANCZOS)
    g = Image.new("RGBA", (1344, 512), (255, 255, 255, 255)); g.alpha_composite(bus, ((1344 - bus.width) // 2, (512 - bus.height) // 2))
    p = C / f"guide_bus_b{blur}.png"; g.convert("RGB").filter(ImageFilter.GaussianBlur(blur)).save(p); return p

BUS = ("(yellow city bus:1.3), (red lower body stripe:1.2), single bus, long boxy modern city bus, flat roof, row of tinted windows, "
       "passengers silhouettes, driver behind front windshield, facing left, black wheels, round plain wheels, solo, no text")
CAR = "(single small modern {col} sedan car:1.3), side view, facing right, four wheels, black tires, silver rims, tinted windows, solo, no text"
JOBS = {
 "sedan_white_R": (CAR.format(col="white") + ", (white body:1.3)", CAR_X, 1344, 512),
 "sedan_red_R": (CAR.format(col="red") + ", (red body:1.4)", CAR_X, 1344, 512),
 "taxi_R": ("(single small sedan taxi car:1.3), (white and green two-tone body:1.2), (white upper body, green lower stripe:1.2), taxi roof light sign on top, side view, facing right, four wheels, black tires, tinted windows, solo, no text", CAR_X, 1344, 512),
 "moto_man_R": ("1boy riding underbone motorbike, sitting, vietnamese man, (black half helmet:1.2), (dark grey jacket:1.2), jeans, sneakers, red motorbike, side view, facing right, solo", MOTO_X, 1024, 1024),
 "moto_sun_R": ("1girl riding scooter, sitting, vietnamese woman, (long light blue sun protection coat:1.3), (white face mask:1.2), (white half helmet:1.2), gloves, white scooter, side view, facing right, solo", MOTO_X, 1024, 1024),
 "moto_poncho_R": ("(person riding scooter under a huge bright yellow translucent rain poncho covering rider and scooter:1.4), (yellow raincoat bat wing sleeves:1.2), rain poncho, only wheels and feet visible, side view, facing right, solo", MOTO_X, 1024, 1024),
 "moto_peach_R": ("2people riding scooter, sitting, vietnamese man driving, girl passenger behind holding (big pink peach blossom branch:1.4), (pink flowers:1.3), side view, facing right, red scooter", MOTO_X.replace("multiple people, ", ""), 1024, 1024),
 "moto_quat_R": ("1man riding motorbike, sitting, (large potted kumquat tree strapped on back seat:1.4), (orange kumquat fruits:1.3), green leaves, big ceramic pot, side view, facing right, solo", MOTO_X, 1024, 1024),
 "moto_puffer_R": ("1girl riding scooter, sitting, vietnamese woman, (thick winter puffer coat:1.3), (red scarf:1.2), (white half helmet:1.2), gloves, scooter, side view, facing right, solo", MOTO_X, 1024, 1024),
 "bike_daisy_R": ("1girl riding old bicycle, pedalling, vietnamese woman, (nón lá conical hat:1.4), (bicycle loaded with big bunches of white daisies:1.4), white daisy flowers piled on rear rack and baskets, long sleeve shirt, side view, facing right, solo", BIKE_X, 1024, 1024),
 "bike_peach_R": ("1girl riding old bicycle, pedalling, vietnamese woman, (nón lá conical hat:1.4), (bicycle loaded with big bunches of pink peach blossom branches:1.4), (pink flowers:1.3) piled on rear rack, long sleeve shirt, side view, facing right, solo", BIKE_X, 1024, 1024),
}

# round-2 prompt overrides (after reviewing round 1: sporty-coupe cars, bat-wing poncho, kumquat pot-only, missing pillion)
SH = ", cast shadow, ground shadow, sports car, coupe, spoiler, long hood, wide fender"
SEDAN = ("(single compact family sedan car:1.3), (three-box sedan with trunk:1.2), {col}, side profile view, facing right, four wheels, "
         "black tires, small hubcaps, tinted windows, side mirror, solo, no text")
JOBS2 = {
 "sedan_white_R": (SEDAN.format(col="(white car:1.5), (pure white paint:1.4), grey shading"), CAR_X + SH + ", beige, cream, yellow", 1344, 512),
 "sedan_red_R": (SEDAN.format(col="(red body:1.4)"), CAR_X + SH, 1344, 512),
 "taxi_R": ("(single compact sedan taxi car:1.3), (white car:1.5), (green lower body stripe:1.3), taxi roof light sign, side profile view, facing right, four wheels, black tires, tinted windows, solo, no text", CAR_X + SH + ", yellow car, yellow taxi", 1344, 512),
 "moto_poncho_R": ("1person riding scooter in the rain, sitting, (bright yellow translucent raincoat poncho covering rider and scooter:1.4), hooded poncho draped over the rider and over the scooter body, wheels and shoes visible below, side view, facing right, solo", MOTO_X + ", bat wings, bubble, dome, umbrella, water", 1024, 1024),
 "moto_peach_R": ("(2people on one scooter:1.4), man driving scooter, young woman sitting behind as pillion passenger holding (big pink peach blossom branch:1.4), (pink flowers:1.3), scooter with two wheels, side view, facing right", MOTO_X.replace("multiple people, ", "") + ", flying, floating", 1024, 1024),
 "moto_quat_R": ("1man riding underbone motorbike, sitting, (motorcycle with two wheels:1.3), (big potted kumquat tree tied on the rear seat:1.3), orange kumquat fruits, green leaves, side view, facing right, solo", MOTO_X, 1024, 1024),
}

# round 3: pillion tandem wording for the peach scooter
JOBS3 = {
 "moto_peach_R": ("2girls on one scooter, tandem, (two riders one behind the other:1.4), front girl driving, back girl sitting on rear seat holding a (huge pink peach blossom branch:1.4), (pink flowers:1.3), side view, facing right", MOTO_X.replace("multiple people, ", "") + ", flying, floating, single person", 1024, 1024),
}

def run(names, seed, batch=2, init=None):
    for n in names:
        if n == "bus_L":
            for blur in (2, 3):
                print(gen(f"{BUS}, {S}", C, f"bus_L_b{blur}_d{int((init or .75)*100)}", 1344, 512, seed, batch=batch,
                          init=(guide_bus(blur), init or .75), neg=NEG + ", multiple vehicles, green bus, interior, double-decker, star-shaped hubs", quality=QUALITY), flush=True)
            continue
        p, x, w, h = JOBS[n]
        print(gen(f"{p}, {S}", C, n, w, h, seed, batch=batch, neg=NEG + x, quality=QUALITY), flush=True)

if __name__ == "__main__":
    seed = int(sys.argv[1]); names = sys.argv[2:] or ["bus_L", *JOBS]
    if seed >= 600: JOBS.update(JOBS2)  # round-2 seeds
    if seed >= 700: JOBS.update(JOBS3)
    run(names, seed)
