import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.comfy import gen
from tools.style_v3 import STYLE, SPRITE, NEG, QUALITY
OUT = Path("assets/out_v3/sprites/characters/_cand")
CORE = "no humans, cat, orange tabby cat, white chest, white paws, green eyes, cute, "
POSES = {
 "cat_sit": "sitting, upright, tail curled around feet, looking forward, side view",
 "cat_lick_paw": "sitting, licking paw, raised paw, eyes closed, side view",
 "cat_sleep_curled": "sleeping, curled up, eyes closed, curled into a ball, lying",
 "cat_walk": "walking, side view, one paw raised, tail up",
 "cat_look_up": "sitting, head tilted up, looking up, side view",
}
def p(pose, coat=CORE): return f"{coat}{pose}, {STYLE}, full body, simple background, white background, isolated, centered, nothing else in the image"
if __name__ == "__main__":
    a = sys.argv[1]
    if a == "sit":
        print(gen(p(POSES["cat_sit"]), OUT, "cat_sit", 1024, 1024, 777, batch=8, neg=NEG, quality=QUALITY))
    else:  # derive: name init_path denoise
        name, init, dn = a, sys.argv[2], float(sys.argv[3])
        coat = CORE
        if "_" in name and name.split("_")[-1] in ("black","calico","tuxedo"):
            pass
        print(gen(p(POSES[name]), OUT, name, 1024, 1024, 777, batch=4, neg=NEG, quality=QUALITY, init=(init, dn)))
