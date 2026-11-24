"""Cut the Hanoi tube-house facades out of the retro AI frame (sky removed) and grade them into night fog.

Outputs (assets/out_v3/plates/layers/):
  houses_rgba.png      1920x1088, facades only, original colours, alpha = buildings
  houses_night.png     same, graded to teal night fog with some warm windows
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "assets/out_v2/ai/px/bg_ctrl_82_0.png"           # 1344x768, day, teal sky + cream clouds
OUT = ROOT / "assets/out_v3/plates/layers"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1088
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.9
BASE_Y = 800                                                  # sidewalk line in the approved plate

im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(np.int32)
lum = a.mean(-1)
h0, w0 = lum.shape
CUT = 470                                                     # below this: ground-floor shops + road (hidden anyway)

# roofline per column: first dark outline pixel (lum<70) under y=60 → buildings start there
top = np.full(w0, CUT, np.int32)
for x in range(w0):
    col = lum[60:CUT, x]
    idx = np.where(col < 70)[0]
    if len(idx):
        top[x] = 60 + idx[0]
# smooth the profile with a column-wise median so stray dark pixels in clouds don't punch holes
from scipy.ndimage import median_filter
top = median_filter(top, size=9, mode="nearest")
mask = np.zeros((h0, w0), np.uint8)
for x in range(w0):
    mask[top[x]:CUT, x] = 255

crop = im.crop((0, 0, w0, CUT))
m = Image.fromarray(mask).crop((0, 0, w0, CUT))
nw, nh = int(w0 * SCALE), int(CUT * SCALE)
crop = crop.resize((nw, nh), Image.LANCZOS)
m = m.resize((nw, nh), Image.LANCZOS)
x0 = (nw - W) // 2
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rgba = crop.copy(); rgba.putalpha(m)
layer.alpha_composite(rgba.crop((x0, 0, x0 + W, nh)), (0, BASE_Y - nh))
layer.save(OUT / "houses_rgba.png")

# night fog grade: everything sinks into teal fog, then ~30% of the windows get a warm light
from scipy import ndimage
L = np.asarray(layer).astype(np.float32)
rgb, al = L[..., :3], L[..., 3:]
fog = np.array([30, 66, 78], np.float32)
g = rgb * 0.22 + fog * 0.78
dark = (rgb.mean(-1) < 70) & (al[..., 0] > 200)
win = ndimage.binary_opening(dark, structure=np.ones((11, 11)))        # drops 1-6px outlines, keeps window panes
lab, n = ndimage.label(win)
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
lit = np.zeros_like(win)
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    hgt, wid = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if 14 < hgt < 120 and 10 < wid < 160 and rng.random() < 0.33:
        lit |= lab == i
warm = np.array([236, 190, 110], np.float32)
yy = np.mgrid[0:H, 0:W][0][..., None].astype(np.float32)
glow = ndimage.gaussian_filter(lit.astype(np.float32), 6)[..., None]
g = np.where(lit[..., None], warm * 0.85 + rgb * 0.15, g)
g = g + glow * np.array([120, 90, 30]) * 0.5
t = np.clip((yy - 250) / (BASE_Y - 250), 0, 1)                         # fog thickens towards the street
g = g * (1 - 0.35 * t) + np.array([66, 104, 110]) * 0.35 * t
g = ndimage.gaussian_filter(g, (1.6, 1.6, 0))                                  # soften: it sits far behind
out = np.concatenate([g.clip(0, 255), al], -1).astype(np.uint8)
Image.fromarray(out, "RGBA").save(OUT / "houses_night.png")
print("windows:", n, "lit:", int(ndimage.label(lit)[1]), "| roof y (src):", int(top.min()), int(np.median(top)),
      "-> scene", BASE_Y - nh + int(top.min() * SCALE))
