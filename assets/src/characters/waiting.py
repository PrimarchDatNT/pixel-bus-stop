from lib import *
from walkers import SCR, sheet
import sys

# ---------------------------------------------------------------- props
def phone_prop(frame):
    def f(img, J, pose):
        hx, hy = J["near_arm"][2]
        hx = R(hx); hy = R(hy)
        rect(img, hx, hy - 2, hx + 1, hy, "ink")
        put(img, hx + 1, hy - 2 + (frame % 3 if frame != 1 else 0) % 3, "cyan" if frame != 1 else "glow")
        put(img, hx + 1, hy - 1, "grey_l" if frame == 2 else "cyan")
        put(img, hx - 1, hy - 1 + (1 if frame == 1 else 0), "skin2")   # thumb
    return f


def newspaper(frame):
    def f(img, J, pose):
        hx, hy = J["near_arm"][2]
        x0 = R(hx) - 1; y1 = R(hy) + 2
        h = 9; w = 6
        y0 = y1 - h
        if frame == 1:      # page lifts at the top corner
            rect(img, x0, y0 + 1, x0 + w - 1, y1, "white")
            rect(img, x0 + w - 3, y0 - 1, x0 + w - 1, y0, "white")
            put(img, x0 + w - 2, y0 - 1, "grey_l"); put(img, x0 + w, y0 - 1, "grey_l")
        elif frame == 2:    # page flipped over to the right
            rect(img, x0, y0 + 1, x0 + w - 3, y1, "white")
            rect(img, x0 + w - 2, y0 + 2, x0 + w, y1 - 1, "grey_l")
            put(img, x0 + w - 2, y0 + 1, "white")
        else:
            rect(img, x0, y0 + 1, x0 + w - 1, y1, "white")
        # headline + text lines
        rect(img, x0 + 1, y0 + 2, x0 + 3, y0 + 2, "slate_d")
        for yy in range(y0 + 4, y1, 2):
            rect(img, x0 + 1, yy, x0 + (3 if frame == 2 else 4), yy, "grey")
        rect(img, x0, y1, x0 + w - 1, y1, "grey_l")
        put(img, x0 - 1, y1 - 1, "skin3")
    return f


def watch_prop(frame):
    def f(img, J, pose):
        if frame == 1:
            hx, hy = J["near_arm"][2]
            put(img, R(hx) - 1, R(hy) + 0, "gold") ; 
    return f


def bag(col, arm="far"):
    def f(img, J, pose):
        hx, hy = J[arm + "_arm"][2]
        hx = R(hx); hy = R(hy)
        rect(img, hx - 1, hy + 1, hx + 3, hy + 4, col)
        rect(img, hx - 1, hy + 1, hx + 3, hy + 1, lighter_of(col))
        rect(img, hx + 3, hy + 2, hx + 3, hy + 4, shade_of(col))
        put(img, hx, hy, "slate_d"); put(img, hx + 2, hy, "slate_d")
    return f

# ---------------------------------------------------------------- specs
SIT = {}
SIT["phone_ha"] = dict(skin="skin2", top=("yellow", "gold", "white"), hair="brown_k", hair_style="pony", woman=True,
    shorts="blue", pants=("blue", "blue_d"), shoe="white", sleeve="short", glasses=False)
SIT["phone_dong"] = dict(skin="skin2", top=("rust", "brown_d", "clay"), hair="brown_k", hair_style="pony", woman=True,
    pants=("blue_d", "navy"), shoe="grey_l", sleeve="long", puffer=True, beanie="sand", scarf="grey_l", glove="skin2")
SIT["elder"] = dict(skin="skin3", top=("slate", "slate_d", "grey"), hair="white", hair_style="bald", glasses=True,
    pants=("brown_d", "brown_k"), shoe="brown_k", sleeve="long", collar="white", no_arm_edge=False)

STAND = {}
STAND["ha"] = dict(skin="skin1", top=("white", "grey_l", "white"), hair="brown_k", hair_style="long", hair_len="mid", woman=True, bun=False,
    panel="coat", panel_len=9, panel_cols=("slate_d", "navy"), pants=("skin1", "skin2"), shoe="ink", sleeve="short",
    belt="red_d", thin_shin=True)
STAND["dong"] = dict(skin="skin1", top=("slate", "slate_d", "grey"), hair="brown_k", hair_style="long", woman=True,
    panel="coat", panel_len=5, pants=("slate_d", "navy"), shoe="brown_k", sleeve="long", scarf="red")


def sit_pose(i, kind):
    hip = 8
    p = dict(hip=hip, hipx=-2, lean=0, head_dx=0, head_dy=0,
             near_ankle=(4, 1), far_ankle=(5, 1), flare=0, trail=0)
    if kind == "elder":
        p.update(lean=0, head_dx=0, head_dy=1 if i != 1 else 0, near_hand=(5, hip + 2.5), far_hand=(4, hip + 2))
        p["near_ankle"] = (3, 1); p["far_ankle"] = (5, 1)
    else:
        dy = [0, 1, 0][i]
        p.update(lean=1, head_dx=1, head_dy=1 + (1 if i == 1 else 0), near_hand=(5, hip + 5 + dy), far_hand=(4, hip + 3))
    p["far_bend"] = -1; p["near_bend"] = -1
    return p


def stand_pose(i):
    hip = 12
    p = dict(hip=hip, hipx=0, lean=0, head_dx=0, head_dy=0, near_ankle=(1, 1), far_ankle=(-1, 1), flare=0, trail=0,
             near_hand=(1, hip + 7 - 6.5), far_hand=(0, hip + 7 - 6.5), near_bend=-1, far_bend=-1)
    p["near_hand"] = (2, hip + 1.5); p["far_hand"] = (0, hip + 1.5)
    if i == 1:   # check watch: forearm up in front of chest, head tilts down
        p.update(head_dy=1, head_dx=1, lean=1, near_hand=(4.5, hip + 6), hipx=0)
    if i == 2:   # look right down the street: lean forward, chin up
        p.update(lean=1, head_dx=1, head_dy=0, near_hand=(2, hip + 1.5), near_ankle=(2, 1))
    if i == 3:
        p.update(far_ankle=(-2, 1), head_dy=1, near_hand=(3, hip + 3))
    return p

if __name__ == "__main__":
    export = "--export" in sys.argv
    out = {}
    for k, S in SIT.items():
        W, H = 32, 30
        fr = []
        for i in range(3):
            S2 = dict(S)
            kind = "elder" if k == "elder" else "phone"
            S2["extras"] = [newspaper(i)] if kind == "elder" else [phone_prop(i)]
            fr.append(draw_person(S2, sit_pose(i, kind), W=W, H=H))
        out["sit_" + k] = (fr, 3 if k != "elder" else 3, (14, H - 2))
    for k, S in STAND.items():
        W, H = 32, 30
        fr = []
        for i in range(4):
            S2 = dict(S); S2["extras"] = [bag("brown_d", "far")]
            fr.append(draw_person(S2, stand_pose(i), W=W, H=H))
        out["stand_wait_" + k] = (fr, 2, None)
    for n, (fr, fps, an) in out.items():
        sheet(fr, SCR + n + ".png", 8)
        if export:
            export_lr("characters", n, fr, fps, anchor=an,
                      notes="waiting person; feet at WAIT_BASE_Y; sit_* anchor x = hip/seat centre (seat surface ~7px above feet row)")
