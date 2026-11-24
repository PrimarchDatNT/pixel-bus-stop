import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.comfy import gen
from tools.style_v3 import STYLE, SPRITE, NEG, QUALITY
OUT = Path("assets/out_v3/sprites/characters/_cand")
W = "1girl, " ; M = "1boy, "
WALK = "walking, facing right, profile, "
A = {
 "walk_aodai_red": "1girl, vietnamese woman, red ao dai, conical hat off, long black hair, white pants, sandals, walking, facing right, profile",
 "walk_man_shirt": "1boy, vietnamese man, white collared shirt, dark trousers, holding small peach blossom branch with pink flowers, walking, facing right, profile",
 "walk_schoolgirl": "1girl, vietnamese schoolgirl, white ao dai, white pants, backpack, long black hair, walking, facing right, profile",
 "walk_umbrella": "1girl, person holding open umbrella, casual jacket, jeans, walking, facing right, profile",
 "walk_kid_scarf": "1boy, child, primary school student, white short sleeve shirt, red neckerchief scarf, dark shorts, small backpack, walking, facing right, profile",
 "walk_puffer": "1boy, vietnamese man, black puffer coat, knit beanie, scarf, jeans, hands in pockets, walking, facing right, profile",
 "walk_coat_scarf": "1girl, vietnamese woman, long beige coat, scarf, boots, long hair, walking, facing right, profile",
 "run_rain_bag": "1girl, running, holding bag over head, raincoat, from side, facing right, leaning forward",
 "sit_phone": "1girl, young person sitting on bench, looking at smartphone, casual hoodie, jeans, sneakers, side view, facing right",
 "sit_elder_newspaper": "1boy, old man, grey hair, sitting on bench, reading newspaper, cardigan, side view, facing right",
 "stand_wait": "1girl, office lady, standing, checking wristwatch, white blouse, pencil skirt, handbag, heels, facing right, side view",
 "swallow_fly": "no humans, swallow bird, flying, wings spread, forked tail, dark blue back, white belly, from side, facing right",
 "sparrow_perch": "no humans, sparrow bird, perched, brown feathers, from side, facing right",
 "sparrow_fly": "no humans, sparrow bird, flying, wings spread, brown feathers, from side, facing right",
 "lion_dance": "vietnamese lion dance, mua lan, red and gold lion costume with two performers, big head with mane, walking, side view, facing right",
 "lion_dance_gold": "vietnamese lion dance, mua lan, golden yellow lion costume with two performers, big head with mane, walking, side view, facing right",
 "kid_star_lantern": "1girl, child holding red star lantern on stick, mid autumn festival, walking, facing right, profile",
 "kid_carp_lantern": "1boy, child holding carp fish lantern on stick, mid autumn festival, walking, facing right, profile",
 "ong_dia": "ong dia, laughing round face mask character, big head mask, holding paper fan, mid autumn festival, vietnamese, robe, facing right",
 "drummer": "1boy, person beating big red drum on stand, mid autumn festival, vietnamese, facing right, side view",
 "vendor_corn": "1girl, vietnamese woman, non la conical hat, sitting on low plastic stool, grilling corn on charcoal brazier, fanning, facing right, side view",
 "pot_peach": "no humans, potted peach blossom tree, pink flowers, ceramic pot, tet decoration",
 "pot_kumquat": "no humans, potted kumquat tree, orange fruits, green leaves, ceramic pot, tet decoration",
 "red_lantern": "no humans, single red chinese lantern with gold tassel, tet decoration, hanging",
 "cau_doi_pair": "no humans, pair of red vertical couplet scrolls with gold calligraphy, tet decoration, front view",
 "watch_point": "1boy, standing, head tilted up, looking up at sky, pointing up with finger, jacket, side view, facing right",
 "watch_phone": "1girl, standing, head tilted up, looking up at sky, holding smartphone up filming, jacket, side view, facing right",
 "watch_shoulders": "father carrying small child on shoulders, both looking up at sky, head tilted up, side view, facing right",
}
SP2 = "full body, simple background, white background, isolated, centered, nothing else in the image"
def run(name, seed=None, batch=4, **kw):
    if name.startswith("cat"):
        return
    seed = seed or 1000 + list(A).index(name)
    sp = SPRITE
    if name in ("pot_peach","pot_kumquat","red_lantern","cau_doi_pair"): sp = SP2
    w, h = 1024, 1024
    if name in ("dragon_dance",): w, h = 1344, 768
    return gen(f"{A[name]}, {STYLE}, {sp}", OUT, name, w, h, seed, batch=batch, neg=NEG, quality=QUALITY, **kw)
if __name__ == "__main__":
    for n in sys.argv[1:]:
        print(n, run(n), flush=True)
