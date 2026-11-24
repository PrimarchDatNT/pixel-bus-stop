"""Character/animal/prop sprites (Animagine XL via ComfyUI).
Usage:
  gen_characters.py cand NAME[,NAME] [seed=1] [batch=3] [init_png denoise]  -> _cand/NAME[_i<dn>]_<seed>_<k>.png
  gen_characters.py cut                                                     -> cuts FINAL picks, writes manifest + sheet
FINAL (see bottom) records the chosen candidate per asset (derived ones came from img2img of cat_sit)."""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
from tools.comfy import gen
from tools.style_v3 import SPRITE_STYLE, SPRITE, NEG, QUALITY

OUT = ROOT / "assets/out_v3/sprites/characters"; C = OUT / "_cand"; C.mkdir(parents=True, exist_ok=True)
S = f"{SPRITE_STYLE}, {SPRITE}"
X = ", green tint, front view, three-quarter view, multiple people, text, logo, bench, chair, ground, shadow"
XA = ", humans, person, hands, dog, multiple animals, text, front view"

COATS = {
 "": "no humans, (orange tabby cat:1.3), (white chest:1.3), white paws, green eyes, cute, domestic shorthair, ",
 "_black": "no humans, (solid black cat:1.4), black fur, yellow eyes, cute, domestic shorthair, ",
 "_calico": "no humans, (calico cat:1.4), (white, orange and black patches:1.3), green eyes, cute, domestic shorthair, ",
 "_tuxedo": "no humans, (tuxedo cat:1.4), (black back and head, white chest, white belly, white paws:1.3), green eyes, cute, domestic shorthair, ",
 "_grey": "no humans, (grey tabby cat:1.4), (grey striped fur:1.2), (white chest:1.3), white paws, green eyes, cute, domestic shorthair, ",
}
POSE = {
 "cat_sit": "sitting, upright, tail curled around feet, looking forward, facing left, side view",
 "cat_lick_paw": "sitting, licking paw, raised paw, eyes closed, facing left, side view",
 "cat_sleep_curled": "sleeping, curled up into a ball, eyes closed, lying, nose tucked in tail, side view",
 "cat_walk": "walking, side view, facing left, one paw raised, tail up",
 "cat_look_up": "sitting, head tilted up, looking up, facing left, side view",
}
JOBS = {}
for k, v in COATS.items():
    for pn in (("cat_sit", "cat_walk", "cat_sleep_curled") if k else POSE):
        JOBS[pn + k] = (v + POSE[pn], XA, 1024, 1024)

JOBS.update({
 "walk_aodai_red": ("1girl, vietnamese woman, (red ao dai:1.4), (long black hair:1.1), (white pants:1.2), sandals, walking, facing right, profile, from side", X, 1024, 1024),
 "walk_man_shirt": ("1boy, vietnamese man, (white collared shirt:1.2), dark trousers, holding (small peach blossom sprig:1.3) with (pink flowers:1.2), walking, facing right, profile, from side", X, 1024, 1024),
 "walk_schoolgirl": ("1girl, vietnamese schoolgirl, (white ao dai:1.4), (white pants:1.2), (backpack:1.2), long black hair, walking, facing right, profile, from side", X, 1024, 1024),
 "walk_umbrella": ("1girl, walking, holding (open umbrella:1.4), (yellow umbrella:1.2), casual jacket, jeans, facing right, profile, from side", X, 1024, 1024),
 "walk_kid_scarf": ("1boy, child, primary school student, (white short sleeve shirt:1.3), (red neckerchief scarf:1.4), dark shorts, small backpack, walking, facing right, profile, from side", X, 1024, 1024),
 "walk_puffer": ("1boy, vietnamese man, (black puffer coat:1.3), (knit beanie:1.3), (scarf:1.2), jeans, hands in pockets, walking, facing right, profile, from side", X, 1024, 1024),
 "walk_coat_scarf": ("1girl, vietnamese woman, (long beige coat:1.4), (scarf:1.3), boots, long hair, walking, facing right, profile, from side", X, 1024, 1024),
 "run_rain_bag": ("1girl, running, (holding bag over head:1.4), both arms raised, leaning forward, casual jacket, jeans, sneakers, facing right, from side", X, 1024, 1024),
 "sit_phone": ("1girl, sitting, (looking at smartphone:1.3), holding phone, casual hoodie, jeans, sneakers, legs bent, seated pose, side view, facing right", X, 1024, 1024),
 "sit_elder_newspaper": ("1boy, old man, grey hair, sitting, (reading newspaper:1.3), holding newspaper, cardigan, trousers, seated pose, side view, facing right", X, 1024, 1024),
 "stand_wait": ("1girl, office lady, standing, (checking wristwatch:1.3), (white blouse:1.2), pencil skirt, handbag, heels, facing right, side view", X, 1024, 1024),
 "lion_dance": ("(vietnamese lion dance:1.3), mua lan, (red and gold lion costume:1.3), two performers, big lion head with mane, walking, side view, facing right", X, 1024, 1024),
 "lion_dance_gold": ("(vietnamese lion dance:1.3), mua lan, (golden yellow lion costume:1.4), (yellow fur:1.2), two performers, big lion head, walking, side view, facing right", X, 1024, 1024),
 "dragon_dance": ("(chinese dragon dance:1.3), (long red and gold dragon:1.3), dragon carried on poles by many performers in a row, long body, walking, side view, facing right", X, 1536, 512),
 "kid_star_lantern": ("1girl, child, holding (red star lantern:1.4) on a stick, mid autumn festival, walking, facing right, profile, from side", X, 1024, 1024),
 "kid_carp_lantern": ("1boy, child, holding (carp fish lantern:1.4) on a stick, (red and orange paper lantern:1.2), mid autumn festival, walking, facing right, profile, from side", X, 1024, 1024),
 "ong_dia": ("(ong dia:1.2), (laughing round face mask:1.3), big head mask, big smiling face, holding (paper fan:1.3), robe, mid autumn festival, vietnamese, standing, side view, facing right", X, 1024, 1024),
 "drummer": ("1boy, person beating (big red drum:1.4) on a stand, drumsticks, mid autumn festival, vietnamese, standing, side view, facing right", X, 1024, 1024),
 "vendor_corn": ("1girl, vietnamese woman, (non la conical hat:1.4), sitting on (low plastic stool:1.2), grilling corn on (charcoal brazier:1.3), holding fan, side view, facing right", ", green tint, front view, multiple people, text, logo, bench, shadow", 1024, 1024),
 "pot_peach": ("no humans, (potted peach blossom tree:1.3), (pink flowers:1.3), ceramic pot, tet decoration, front view", ", multiple, text, ground", 1024, 1024),
 "pot_kumquat": ("no humans, (potted kumquat tree:1.3), (orange kumquat fruits:1.3), green leaves, ceramic pot, tet decoration, front view", ", multiple, text, ground", 1024, 1024),
 "red_lantern": ("no humans, (single red chinese lantern:1.3), (gold tassel:1.2), tet decoration, hanging, front view", ", multiple, text, ground", 1024, 1024),
 "watch_point": ("1boy, standing, (head tilted up:1.3), looking up at sky, (pointing up with finger:1.3), jacket, trousers, side view, facing right", X, 1024, 1024),
 "watch_phone": ("1girl, standing, (head tilted up:1.3), looking up at sky, (holding smartphone up filming:1.3), jacket, side view, facing right", X, 1024, 1024),
 "watch_shoulders": ("(father carrying small child on shoulders:1.3), 1boy, 1child, both looking up at sky, head tilted up, standing, side view, facing right", X, 1024, 1024),
 "swallow_fly": ("no humans, (swallow bird:1.3), flying, wings spread, forked tail, (dark blue back:1.2), white belly, from side, facing right", XA, 1024, 1024),
 "sparrow_perch": ("no humans, (sparrow bird:1.3), perched, brown feathers, from side, facing right", XA, 1024, 1024),
 "sparrow_fly": ("no humans, (sparrow bird:1.3), flying, wings spread, brown feathers, from side, facing right", XA, 1024, 1024),
})

# ---- refine round (r2): rewritten prompts for weak first-round assets
XL = X + ", realistic lion, real animal, green body, jungle"
JOBS.update({
 "lion_dance_r2": ("(lion dance costume:1.4), vietnamese mua lan, (red lion head with gold trim and white mane:1.2), (red and gold fabric body:1.4), two performers hidden inside, human legs in trousers visible at front and back, walking, side view, facing right", XL, 1024, 1024),
 "lion_dance_gold_r2": ("(lion dance costume:1.4), vietnamese mua lan, (golden yellow lion head with red trim:1.2), (golden yellow fabric body:1.4), two performers hidden inside, human legs in trousers visible at front and back, walking, side view, facing right", XL, 1024, 1024),
 "dragon_dance_r2": ("(dragon dance:1.4), (long red and gold dragon:1.3), (row of many performers carrying the dragon on poles below:1.4), people holding poles, wavy long body, side view, facing right", X, 1536, 512),
 "sit_elder_newspaper_r2": ("1boy, old man, grey hair, (sitting:1.3), (reading newspaper:1.3), cardigan, trousers, knees bent, feet on ground, torso upright, seated pose, side view, facing right, (no chair, no stool, no furniture:1.3)", X, 1024, 1024),
 "sit_phone_r2": ("1girl, (sitting:1.3), (looking at smartphone:1.3), casual hoodie, jeans, sneakers, knees bent, feet flat on ground, torso upright, seated pose, side view, facing right, (no chair, no stool, no furniture:1.3)", X, 1024, 1024),
 "cat_lick_paw_r2": (COATS[""] + "sitting, (licking paw:1.4), (raised front paw at mouth:1.3), tongue out, eyes closed, facing left, side view", XA, 1024, 1024),
 "drummer_r2": ("1boy, full body, standing, vietnamese young man in (white shirt:1.2) and dark trousers, holding two drumsticks, striking a (large red drum on wooden stand:1.3), drum in front of him seen from side, mid autumn festival, side view, facing right", X, 1024, 1024),
 "lion_dance_r3": ("(vietnamese lion dance:1.3), mua lan, (red and gold lion costume:1.3), (red fabric body with gold trim:1.4), two performers, big lion head with mane, walking, side view, facing right", X + ", green body, blue", 1024, 1024),
 "drummer_r3": ("1boy, upper body above a (big round red drum with gold studs:1.3), standing behind the drum, holding two drumsticks, hitting the drum, drum at waist height, mid autumn festival, side view, facing right", X + ", tall drum, vertical drum, giant drum", 1024, 1024),
})

def cand(name, seed=1, batch=3, init=None, tag=""):
    p, x, w, h = JOBS[name]
    kw = dict(init=(init[0], float(init[1]))) if init else {}
    return gen(f"{p}, {S}", C, f"{name}{tag}", w, h, seed, batch=batch, neg=NEG + x, quality=QUALITY, **kw)

if __name__ == "__main__" and sys.argv[1] == "cand":
    a = sys.argv[2:]
    seed = int(a[1]) if len(a) > 1 else 1; batch = int(a[2]) if len(a) > 2 else 3
    init = (a[3], a[4]) if len(a) > 4 else None
    for n in a[0].split(","):
        print(n, cand(n, seed, batch, init, tag=f"_i{a[4]}" if init else ""), flush=True)
