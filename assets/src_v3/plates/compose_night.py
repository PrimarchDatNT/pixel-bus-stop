"""Night plate v3: approved lofi frame + hazy Hanoi tube houses behind the trees, rain streaks removed
(rain is animated in code). Output assets/out_v3/plates/_cand/night_comp3.png (1920x1088), then an
img2img + canny pass on ComfyUI unifies the paint. Usage: compose_night.py [seed ...]"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
C = ROOT / "assets/out_v3/plates/_cand"
base = Image.open(ROOT / "assets/out_v2/ai/lofi/lofi_h_hr_111_0.png").convert("RGB")
houses = Image.open(ROOT / "assets/out_v3/plates/layers/houses_night.png")
W, H = base.size

B = np.asarray(base).astype(np.float32)
# 1) kill thin vertical rain streaks: horizontal median, applied only where the pixel is a bright thin line
med = ndimage.median_filter(B, size=(1, 7, 1))
streak = (B.mean(-1) - med.mean(-1)) > 7
streak = ndimage.binary_dilation(streak, structure=np.ones((3, 3)))
B = np.where(streak[..., None], med, B)

# 2) sky mask: dark, not foliage-green, above the sidewalk, outside the shelter block; keep only the
#    components connected to the open sky (dark pockets inside the tree canopies must stay tree)
r, g, b = B[..., 0], B[..., 1], B[..., 2]
yy, xx = np.mgrid[0:H, 0:W]
sky = (B.mean(-1) < 85) & (g < b + 10) & (yy < 800)
sky &= ~((xx > 530) & (xx < 1385) & (yy > 455))                 # shelter + bloom
sky &= ~((xx > 1400) & (xx < 1550) & (yy > 410))                # stop sign
sky = ndimage.binary_closing(sky, structure=np.ones((7, 7)))
lab, _ = ndimage.label(sky)
seeds = {lab[y, x] for y, x in ((300, 960), (120, 960), (20, 700), (20, 1200), (430, 760), (430, 1160))} - {0}
sky = np.isin(lab, list(seeds))
sky = ndimage.binary_opening(sky, structure=np.ones((5, 5)))
Image.fromarray((sky * 255).astype(np.uint8)).save(C / "night_skymask.png")
m = np.asarray(houses)[..., 3].astype(np.float32) / 255 * sky
m = ndimage.gaussian_filter(m, 1.5)[..., None]
Hs = np.asarray(houses)[..., :3].astype(np.float32)
out = B * (1 - m) + Hs * m
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(C / "night_comp3.png")
print("comp ok")

if len(sys.argv) > 1:
    from tools.comfy import gen
    P = ("no humans, scenery, lofi anime background, night, after rain, a bus stop shelter at the center, "
         "magenta bougainvillea flowers covering the bus stop roof, warm light inside the shelter, blue plastic seats, "
         "bus stop sign, lush green trees on the left and right, row of narrow tall vietnamese tube houses in the background, "
         "hazy foggy night, a few lit windows, balconies with shutters, wet road, reflections on wet asphalt, puddles, "
         "teal and dark green color palette, warm yellow light accents, cozy atmosphere, soft lighting, anime coloring, clean lines")
    NEG = ("lowres, worst quality, low quality, blurry, text, watermark, signature, jpeg artifacts, 3d render, photo, people, car, "
           "rain, raindrops, falling rain, japanese architecture, tiled roof, wooden house, clouds, daytime, sunlight")
    for s in sys.argv[1:]:
        seed, dn = int(s.split(":")[0]), float(s.split(":")[1]) if ":" in s else 0.4
        print(gen(P, C, f"night_v3_d{int(dn*100)}", w=1920, h=1088, seed=seed, batch=1, cfg=5.5,
                  init=(C / "night_comp3.png", dn), control=(C / "night_comp3.png", 0.5, "tile", 0.8),
                  neg=NEG))
