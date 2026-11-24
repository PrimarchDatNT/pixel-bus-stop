"""Shrink the ComfyUI test images to our sprite sizes (GIF palette, no dither) for the hand-vs-AI comparison."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from rembg import remove
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.px_gif import PALETTE_GIF  # noqa: E402

D = Path(__file__).parent
pal_rgb = [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in PALETTE_GIF.values()]
P = Image.new("P", (1, 1)); flat = sum(pal_rgb, ()); P.putpalette(flat + flat[:3] * (256 - len(pal_rgb)))
TARGET_W = {"pigeon": 14, "sparrow": 8, "tea_stall": 38}
for name, tw in TARGET_W.items():
    src = Image.open(D / "raw" / f"{name}_1_0.png").convert("RGB")
    cut = remove(src)                                         # RGBA, background removed
    bb = cut.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox()
    cut = cut.crop(bb)
    th = max(1, round(cut.height * tw / cut.width))
    small = cut.resize((tw, th), Image.BOX)
    rgb = small.convert("RGB").quantize(palette=P, dither=Image.Dither.NONE).convert("RGBA")
    a = np.asarray(small.getchannel("A")); o = np.asarray(rgb).copy(); o[..., 3] = np.where(a > 128, 255, 0)
    Image.fromarray(o).save(D / f"px_{name}.png")
    cut.save(D / f"cut_{name}.png")
    print(name, (tw, th))
