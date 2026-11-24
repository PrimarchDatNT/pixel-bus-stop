"""Test: can ComfyUI (SDXL base + pixel-art-xl LoRA) make the small props directly? -> assets/src_gif/ai_test/raw/
Then pixelize to our sprite size with the GIF palette -> ai_test/px_<name>.png"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.comfy import gen  # noqa: E402

OUT = Path(__file__).parent / "raw"
NEG = ("blurry, photo, 3d render, realistic, gradient, noise, text, watermark, signature, multiple views, "
       "cropped, frame, border, shadow, background scenery")
JOBS = {
    "pigeon": "pixel art, a single gray rock pigeon standing on the ground, side view facing left, iridescent green "
              "and purple neck, two dark wing bars, pink feet, cute game sprite, simple flat colors, plain white background",
    "sparrow": "pixel art, a single small brown house sparrow perched, side view facing left, chestnut head, cream "
               "belly, cute round game sprite, simple flat colors, plain white background",
    "tea_stall": "pixel art, vietnamese sidewalk iced tea stall, a low wooden table with a big red thermos, glass jars "
                 "of peanut candy, glasses of iced tea on a tray, a bamboo water pipe, two small red and blue plastic "
                 "stools, front view, cute game sprite, simple flat colors, plain white background",
}
if __name__ == "__main__":
    for name, p in JOBS.items():
        for seed in (1, 2):
            print(gen(p, OUT, name, w=1024, h=1024, seed=seed, steps=28, cfg=6.0, neg=NEG, sampler="euler",
                      ckpt="sd_xl_base_1.0.safetensors", loras=(("pixel-art-xl.safetensors", 1.0),), quality=None),
                  flush=True)
