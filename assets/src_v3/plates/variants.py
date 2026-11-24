"""Season / time-of-day plates on the same layout as the canonical night plate (assets/out_v3/plates/night_rain.png).

Pipeline per variant (same as the night plate, so the house row is identical in every season):
  1. ComfyUI: plate with OPEN SKY behind the trees, layout locked by canny edges of the night plate
     (house edges and wet-road reflections removed from the edge map).
  2. Paste the shared tube-house layer (layers/houses_rgba.png) into the sky, graded for the variant.
  3. Unify pass: img2img + tile ControlNet at low denoise.
Usage: variants.py <key> <seed> [denoise1] [denoise3]"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from skimage import feature, segmentation
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
from tools.comfy import gen

P = ROOT / "assets/out_v3/plates"; C = P / "_cand"; Lr = P / "layers"
night = Image.open(P / "night_rain.png").convert("RGB")
W, H = night.size
houses = Image.open(Lr / "houses_rgba.png")
HA = np.asarray(houses)[..., 3] > 8

VIS = ndimage.binary_dilation(np.asarray(Image.open(C / "night_skymask.png")) > 0, iterations=4) & HA   # houses seen at night
edges_p = Lr / "edges_houses.png"
if not edges_p.exists():
    g = np.asarray(night.convert("L")).astype(np.float32) / 255
    e = feature.canny(g, sigma=2.2, low_threshold=0.04, high_threshold=0.10)
    e &= ~ndimage.binary_dilation(VIS, iterations=4)          # replace the soft night house edges...
    hg = np.asarray(houses.convert("L")).astype(np.float32) / 255
    eh = feature.canny(hg, sigma=1.6, low_threshold=0.05, high_threshold=0.14) & VIS
    e |= eh                                                    # ...with crisp ones from the source facades
    e[835:, :] = False                                         # no wet-road reflections
    e = ndimage.binary_dilation(e, iterations=1)
    Image.fromarray((e * 255).astype(np.uint8)).convert("RGB").save(edges_p)

def init_from_night(gamma, mul, sat):
    a = (np.asarray(night).astype(np.float32) / 255) ** gamma * np.array(mul)
    im = Image.fromarray((a.clip(0, 1) * 255).astype(np.uint8))
    return ImageEnhance.Color(im).enhance(sat)

def sky_mask(img):
    """Region-grow the sky from seeds above the shelter, per channel, on a smoothed copy."""
    a = ndimage.gaussian_filter(np.asarray(img).astype(np.float32) / 255, (3, 3, 0))
    m = np.zeros((H, W), bool)
    for y, x in ((140, 960), (60, 700), (60, 1220), (300, 960), (420, 960)):
        if m[y, x]:
            continue
        r = np.ones((H, W), bool)
        for c in range(3):
            r &= segmentation.flood(a[..., c], (y, x), tolerance=0.09)
        if r.sum() < W * H * 0.4:                # a seed that leaks into everything is not sky
            m |= r
    m[810:, :] = False
    m = ndimage.binary_closing(m, structure=np.ones((9, 9)))
    return ndimage.binary_opening(m, structure=np.ones((5, 5)))

def grade_houses(haze_rgb, haze_k, mul=(1, 1, 1), sat=1.0, blur=1.2):
    L = np.asarray(houses).astype(np.float32)
    rgb = L[..., :3] * np.array(mul)
    grey = rgb.mean(-1, keepdims=True); rgb = grey + (rgb - grey) * sat
    yy = np.mgrid[0:H, 0:W][0][..., None].astype(np.float32)
    k = haze_k + (1 - haze_k) * 0.35 * np.clip((yy - 250) / 550, 0, 1)   # thicker toward the street
    rgb = rgb * (1 - k) + np.array(haze_rgb) * k
    rgb = ndimage.gaussian_filter(rgb, (blur, blur, 0))
    return rgb, L[..., 3:] / 255

BASE = ("no humans, scenery, lofi anime background, a bus stop shelter at the center, blue plastic seats, bus stop sign, "
        "lush trees on the left and right, row of narrow tall vietnamese tube houses in the background behind the trees, "
        "balconies, shutters, slightly hazy distance, road in the foreground, ")
TAIL = ", cozy atmosphere, anime coloring, clean lines, highly detailed"
NEG = ("lowres, worst quality, low quality, blurry, text, watermark, signature, jpeg artifacts, 3d render, photo, people, car, "
       "skyscraper, glass building, japanese architecture, tiled roof, rain streaks, reflections on the road")
UNIFY_ADD = ", row of narrow tall vietnamese tube houses in the background with balconies and shutters, slightly hazy"
V = {  # desc, extra neg, init (gamma, mul, sat), houses (haze_rgb, haze_k, mul, sat)
    "ha_noon": ("magenta bougainvillea in full bloom covering the bus stop roof, summer, noon, bright sunny day, clear blue sky, "
                "white cumulus clouds, strong sunlight, dappled leaf shadows on the sidewalk, dry asphalt road, vivid green trees",
                ", night, dark, rain, wet, puddles", (0.45, (1.05, 1.0, 0.95), 1.2), ((170, 205, 235), 0.28, (1.0, 1.0, 1.0), 0.9)),
    "xuan_morning": ("few pink bougainvillea buds on the bus stop roof, fresh young green leaves, spring, early morning, soft pastel light, "
                     "light mist, pale blue sky, sidewalk and asphalt city road in the foreground",
                     ", night, dark, heavy rain, autumn leaves, forest path, dirt path, grass path, meadow", (0.5, (1.02, 1.0, 1.0), 1.0), ((215, 222, 225), 0.42, (1.0, 1.0, 1.0), 0.75)),
    "thu_afternoon": ("bus stop roof with few remaining magenta bougainvillea flowers, autumn, late afternoon, golden hour, warm orange sunlight, "
                      "long shadows, yellow and orange leaves on the trees, fallen leaves on the road",
                      ", night, rain, spring blossoms", (0.5, (1.15, 1.0, 0.8), 1.1), ((235, 190, 140), 0.33, (1.08, 0.98, 0.85), 0.9)),
    "dong_fog": ("sparse withered bougainvillea with a few magenta flowers and bare twigs on the bus stop roof, winter in hanoi, "
                 "overcast grey sky, cold morning fog, damp asphalt road, sidewalk, muted desaturated colors",
                 ", sunny, blue sky, bright colors, night, snow, snowing, snow on roof, ice, frost, icicles", (0.6, (0.95, 1.0, 1.05), 0.7), ((190, 196, 198), 0.55, (0.95, 1.0, 1.02), 0.6)),
}
key, seed = sys.argv[1], int(sys.argv[2])
args = [a for a in sys.argv if not a.startswith("--")]
dn1 = float(args[3]) if len(args) > 3 else 0.88
dn3 = float(args[4]) if len(args) > 4 else 0.4
desc, negx, ini, hs = V[key]
init = C / f"{key}_init.png"
base = np.asarray(init_from_night(*ini)).astype(np.float32)
hrgb, ha = grade_houses(*hs)
m = ndimage.gaussian_filter(ha[..., 0] * VIS, 1.5)[..., None]
Image.fromarray((base * (1 - m) + hrgb * m).clip(0, 255).astype(np.uint8)).save(init)
# 1) open-sky plate
p1 = C / f"{key}_s1_{seed}_0.png"
if "--reuse" not in sys.argv or not p1.exists():
    p1 = gen(BASE + desc + TAIL, C, f"{key}_s1", w=W, h=H, seed=seed, batch=1, cfg=5.5, init=(init, dn1),
             control=(edges_p, 0.6, "canny/lineart/anime_lineart/mlsd", 0.75), neg=NEG + negx)[0]
print(key, "->", p1, flush=True)
if "--comp" not in sys.argv:
    sys.exit()
plate = Image.open(p1).convert("RGB")
# 2) houses into the sky
# paste our tube houses where the night plate showed them, except where step 1 grew foliage over them
A = ndimage.gaussian_filter(np.asarray(plate).astype(np.float32), (2, 2, 0))
foliage = (A[..., 1] > A[..., 2] + 6) & (A[..., 1] > A[..., 0] - 4)
foliage = ndimage.binary_opening(foliage, structure=np.ones((5, 5)))
sky = VIS & ~foliage
Image.fromarray((sky * 255).astype(np.uint8)).save(C / f"{key}_{seed}_skymask.png")
hrgb, ha = grade_houses(*hs)
m = ndimage.gaussian_filter(ha[..., 0] * sky, 1.5)[..., None]
comp = np.asarray(plate).astype(np.float32) * (1 - m) + hrgb * m
comp_p = C / f"{key}_{seed}_comp.png"; Image.fromarray(comp.clip(0, 255).astype(np.uint8)).save(comp_p)
# 3) unify
NEG3 = NEG + negx
p3 = gen(BASE + desc + UNIFY_ADD + TAIL, C, f"{key}_v3", w=W, h=H, seed=seed + 1000, batch=1, cfg=5.5, init=(comp_p, dn3),
         control=(comp_p, 0.5, "tile", 0.8), neg=NEG3)[0]
print(key, "sky px:", int(sky.sum()), "->", p3, flush=True)
