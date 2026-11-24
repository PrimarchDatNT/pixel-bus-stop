from lib import *
import sys

SCR = "/private/tmp/claude-501/-Users-datnt1-Desktop-work-local-llm/aecac36a-4fde-49ae-bc08-0eb2ae68421d/scratchpad/"

# ---------------------------------------------------------------- extras
def sprig(img, J, pose):
    hx, hy = J["near_arm"][2]
    sw = pose.get("hair_sw", 0)
    top = (hx + 4, hy - 10 + sw)
    line(img, hx, hy, top[0], top[1], "brown_d")
    line(img, hx + 2, hy - 5 + 0, hx + 5, hy - 6, "brown_d")
    for (dx, dy, col) in [(0, 0, "bloom_l"), (-1, 1, "salmon"), (1, 1, "bloom_hl"), (-1, -1, "bloom_hl"), (1, -1, "salmon"),
                          (-2, 3, "salmon"), (3, 2, "bloom_l")]:
        put(img, top[0] + dx, top[1] + dy, col)
    put(img, hx + 5, hy - 6, "bloom_l"); put(img, hx + 6, hy - 7, "salmon"); put(img, hx + 5, hy - 7, "bloom_hl")
    put(img, hx + 1, hy - 3, "green_l")
    put(img, hx, hy, "skin2")


def make_umbrella(base, shade, hi, cx_off=0):
    def f(img, J, pose):
        hx, hy = J["near_arm"][2]
        hx = R(hx) + 0
        headtop = J["head"][1]
        yb = headtop - 3
        top = yb - 5
        # shaft
        line(img, hx, hy, hx, top - 1, "slate_d")
        # canopy: half ellipse
        a, b = 10, 5
        for yy in range(top, yb + 1):
            for xx in range(hx - a, hx + a + 1):
                dx = (xx - hx) / a; dy = (yb - yy) / b
                if dx * dx + dy * dy <= 1.0 and not (yy == yb and False):
                    put(img, xx, yy, base)
        # shade right half
        for yy in range(top, yb + 1):
            for xx in range(hx + 4, hx + a + 1):
                if img.getpixel((xx, yy))[3] and img.getpixel((xx, yy))[:3] == RGB[base]:
                    put(img, xx, yy, shade)
        for xx in range(hx - 6, hx - 1):
            for yy in range(top, top + 3):
                if img.getpixel((xx, yy))[3] and img.getpixel((xx, yy))[:3] == RGB[base]:
                    put(img, xx, yy, hi); break
        # ribs + scalloped hem
        for dx in (-7, -3, 1, 5, 9):
            put(img, hx + dx, yb, shade); put(img, hx + dx + 1, yb, base) if False else None
        put(img, hx, top - 1, "slate_d")
        # handle hook under hand
        put(img, hx, hy + 1, "slate_d")
        put(img, hx + 1, hy, "slate_d")
        put(img, hx, hy, "skin1")
    return f


def tote(col):
    def f(img, J, pose):
        hx, hy = J["near_arm"][2]
        hx = R(hx); hy = R(hy)
        rect(img, hx - 1, hy + 2, hx + 3, hy + 6, col)
        rect(img, hx + 3, hy + 2, hx + 3, hy + 6, shade_of(col))
        rect(img, hx - 1, hy + 2, hx + 2, hy + 2, lighter_of(col))
        put(img, hx, hy + 1, "brown_d"); put(img, hx + 2, hy + 1, "brown_d")
        put(img, hx + 1, hy, "brown_d") if False else None
    return f


SPECS = {}
SPECS["aodai_xuan"] = dict(skin="skin1", top=("red", "red_d", "salmon"), hair="brown_k", hair_style="long", woman=True,
    panel="aodai", panel_len=6, pants=("white", "grey_l"), shoe="white", hem="gold", sleeve="long")
SPECS["man_xuan"] = dict(skin="skin2", top=("white", "grey_l", "white"), hair="brown_k", hair_style="short",
    pants=("slate_d", "navy"), shoe="brown_k", sleeve="long", extras=[sprig], collar="grey_l")
SPECS["elder_xuan"] = dict(skin="skin2", top=("plum", "bloom_k", "mauve"), hair="grey_l", hair_style="short", woman=True,
    pants=("slate_d", "navy"), shoe="brown_d", sleeve="long", hat_nonla="sand", panel="aodai", panel_len=8)
SPECS["tshirt_ha"] = dict(skin="skin2", top=("blue", "blue_d", "sky"), hair="brown_k", hair_style="short",
    shorts="sand", pants=("sand", "ochre"), shoe="brown_d", sandal="brown_d", sleeve="short")
SPECS["schoolgirl_ha"] = dict(skin="skin1", top=("white", "grey_l", "white"), hair="brown_k", hair_style="long", woman=True,
    panel="aodai", panel_len=6, pants=("white", "grey_l"), shoe="white", sleeve="long", backpack="blue", hem="grey")
SPECS["umbrella_ha"] = dict(skin="skin1", top=("mint", "green", "grey_l"), hair="brown_k", hair_style="pony", woman=True,
    pants=("slate_d", "navy"), shoe="brown_k", sleeve="long", mask=True, extras=[make_umbrella("blue_d", "navy", "blue")],
    panel="coat", panel_len=9)
SPECS["cardigan_thu"] = dict(skin="skin2", top=("sand", "ochre", "white"), hair="brown_d", hair_style="long", hair_len="mid", woman=True,
    pants=("blue_d", "navy"), shoe="brown_k", sleeve="long", panel="coat", panel_len=9, inner="white",
    extras=[tote("clay")])
SPECS["kid_thu"] = dict(skin="skin2", top=("white", "grey_l", "white"), hair="brown_k", hair_style="short", kid=True,
    pants=("navy", "ink"), shoe="grey_l", sleeve="short", scarf="red", backpack="blue")
def envelope(img, J, pose):
    hx, hy = J["near_arm"][2]
    hx = R(hx); hy = R(hy)
    rect(img, hx, hy - 3, hx + 2, hy, "red")
    rect(img, hx, hy - 3, hx + 2, hy - 3, "red_hot") if False else None
    put(img, hx + 1, hy - 2, "gold"); put(img, hx + 1, hy - 1, "gold")
    put(img, hx + 2, hy - 3, "red_d"); put(img, hx + 2, hy - 2, "red_d"); put(img, hx + 2, hy - 1, "red_d"); put(img, hx + 2, hy, "red_d")
    put(img, hx - 1, hy, "skin2")

SPECS["kid_xuan"] = dict(skin="skin2", top=("red", "red_d", "salmon"), hair="brown_k", hair_style="short", kid=True,
    pants=("navy", "ink"), shoe="white", sleeve="long", collar="gold", extras=[envelope])
SPECS["puffer_dong"] = dict(skin="skin2", top=("green", "green_d", "green_l"), hair="brown_k", hair_style="short",
    pants=("slate_d", "navy"), shoe="brown_k", sleeve="long", puffer=True, beanie="red", scarf="grey_l", glove="slate")
SPECS["coat_dong"] = dict(skin="skin1", top=("ochre", "clay", "sand"), hair="brown_k", hair_style="long", woman=True,
    pants=("slate_d", "navy"), shoe="brown_k", sleeve="long", panel="coat", panel_len=6, scarf="mauve")

def hold_sprig(i, p):
    return dict(near_hand=(4.5, p["hip"] + 4.5), near_bend=-1)
def umb_hand(i, p):
    return dict(near_hand=(5.5, p["hip"] + 5.5), near_bend=-1)

CFG = {
    "aodai_xuan": dict(),
    "man_xuan": dict(extra=hold_sprig),
    "elder_xuan": dict(lift=(0, 0, 0, 1, 1, 1), swing=1.5, lean=1),
    "tshirt_ha": dict(swing=3.6),
    "schoolgirl_ha": dict(),
    "umbrella_ha": dict(extra=umb_hand, swing=2.2),
    "cardigan_thu": dict(),
    "kid_thu": dict(D=D_KID, hips=(7, 7, 8, 7, 7, 8)),
    "kid_xuan": dict(D=D_KID, hips=(7, 7, 8, 7, 7, 8), extra=lambda i, p: dict(near_hand=(4.5, p["hip"] + 4.5), near_bend=-1)),
    "puffer_dong": dict(swing=2.2),
    "coat_dong": dict(),
}
FRAME = {"umbrella_ha": (40, 38), "kid_thu": (24, 22), "kid_xuan": (24, 22)}
FPS = {"elder_xuan": 6}

def build(key):
    S = SPECS[key]; W, H = FRAME.get(key, (32, 30))
    cfg = CFG[key]
    D = cfg.get("D")
    kw = {k: v for k, v in cfg.items() if k != "D"}
    return [draw_person(S, walk_pose(i, D=D, **kw), W=W, H=H, D=D) for i in range(6)]

def sheet(frames, path, k=6):
    w = frames[0].width; h = frames[0].height
    im = Image.new("RGBA", (w * len(frames) * k, h * k), (*RGB["grey_l"], 255))
    for i, f in enumerate(frames):
        im.alpha_composite(f.resize((w * k, h * k), Image.NEAREST), (i * w * k, 0))
    im.convert("RGB").save(path)

if __name__ == "__main__":
    args = sys.argv[1:]
    export = "--export" in args
    keys = [a for a in args if not a.startswith("--")] or list(SPECS)
    for k in keys:
        fr = build(k)
        sheet(fr, SCR + f"{k}.png")
        if export:
            season = k.rsplit("_", 1)[1]
            export_lr("characters", "walk_" + k, fr, FPS.get(k, 8),
                      notes=f"walk cycle 6f; ground speed = 2px/frame (stance feet move 2px/frame) -> 16px/s at 8fps")
