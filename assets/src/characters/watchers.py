from lib import *
from walkers import SPECS, SCR, sheet
import sys

def pointing_finger(frame):
    def f(img, J, pose):
        hx, hy = J["near_arm"][2]
        put(img, hx + 1, hy - 1, "skin2"); put(img, hx + 1, hy - 2 - (frame % 2), "skin2")
    return f

def phone_up(frame):
    def f(img, J, pose):
        hx, hy = J["near_arm"][2]
        rect(img, hx, hy - 3, hx + 2, hy, "ink")
        put(img, hx + 1, hy - 2, "yellow" if frame == 0 else "white")
        put(img, hx + 1, hy - 1, "cyan")
        put(img, hx - 1, hy, "skin1")
    return f

def stand_pose(i, hip=12, extra=None):
    p = dict(hip=hip, hipx=0, lean=-1, head_dx=-1, head_dy=0, head_tilt=2, near_ankle=(1, 1), far_ankle=(-2, 1),
             near_hand=(1, hip + 1.5), far_hand=(0, hip + 1.5), near_bend=-1, far_bend=-1, flare=0, trail=0, scarf_sw=0)
    if extra: p.update(extra)
    return p

MAN = dict(SPECS["puffer_dong"])
WOMAN = dict(skin="skin1", top=("rust", "brown_d", "clay"), hair="brown_k", hair_style="long", woman=True, puffer=True,
             beanie="sand", scarf="grey_l", pants=("blue_d", "navy"), shoe="brown_k", sleeve="long", glove="skin1")
COAT = dict(SPECS["coat_dong"])

def build_point():
    fr = []
    for i in range(3):
        S = dict(MAN); S["extras"] = [pointing_finger(i)]
        fr.append(draw_person(S, stand_pose(i, extra=dict(near_hand=(6 + (i == 1), 12 + 8 + 3 + i), head_dy=0, head_tilt=2, scarf_sw=i % 2)), W=32, H=36))
    return fr

def build_phone():
    fr = []
    for i in range(2):
        S = dict(COAT); S["extras"] = [phone_up(i)]
        fr.append(draw_person(S, stand_pose(i, extra=dict(near_hand=(6, 12 + 10 + i), far_hand=(4, 12 + 8), head_tilt=1, flare=0, near_bend=-1)), W=32, H=34))
    return fr

def shoulders_shoes(img, J, pose):
    hx, hy = J["near_arm"][2]
    put(img, hx + 1, hy - 1, "ink"); put(img, hx + 1, hy, "white"); put(img, hx + 2, hy, "white")

def build_shoulders():
    W, H = 32, 48
    fr = []
    kid = dict(skin="skin2", top=("red", "red_d", "salmon"), hair="brown_k", hair_style="short", kid=True,
               pants=("navy", "ink"), shoe="white", sleeve="long", beanie="gold", scarf="white")
    for i in range(3):
        dad = dict(MAN); dad["extras"] = [shoulders_shoes]
        dd = draw_person(dad, stand_pose(i, extra=dict(near_hand=(3, 12 + 7), far_hand=(2, 12 + 7), head_tilt=2, head_dy=0)), W=W, H=H)
        wave = [(4, 8 + 11), (6, 8 + 12), (4, 8 + 12)][i]
        kp = dict(hip=8, hipx=0, lean=0, head_dx=0, head_dy=0, head_tilt=2, near_ankle=(3, 2), far_ankle=(2, 2),
                  near_hand=wave, far_hand=(0, 8 + 3), near_bend=-1, far_bend=-1, flare=0, trail=0, scarf_sw=i % 2)
        kd = draw_person(kid, kp, W=24, H=24, D=D_KID)    # frame 24x23, feet row 22
        base = new(W, H - 1)
        # dad feet row = H-2 -> kid feet row should sit at dad dy 17
        ky = (H - 2 - 17) - (kd.height - 1)
        base.alpha_composite(kd, (W // 2 - 12 - 3, ky - 1))
        base.alpha_composite(dd, (0, 0))
        fr.append(base)
    return fr

def build_couple():
    fr = []
    A = dict(COAT); B = dict(MAN)
    for i in range(2):
        a = draw_person(A, stand_pose(i, extra=dict(lean=1, head_dx=0, head_tilt=2, near_hand=(2, 13), far_hand=(1, 13))), W=32, H=32)
        b = draw_person(B, stand_pose(i, extra=dict(lean=-1, head_dx=-2 - i, head_tilt=2, near_hand=(3, 13), far_hand=(1, 13))), W=32, H=32)
        base = new(40, a.height)
        base.alpha_composite(a, (0, 0)); base.alpha_composite(b, (8, 0))
        fr.append(base)
    return fr

ASSETS = {"watch_point_dong": (build_point, 3), "watch_phone_dong": (build_phone, 2),
          "watch_shoulders_dong": (build_shoulders, 3), "watch_couple_dong": (build_couple, 2)}
if __name__ == "__main__":
    for n, (fn, fps) in ASSETS.items():
        fr = fn()
        sheet(fr, SCR + n + ".png", 8)
        if "--export" in sys.argv:
            export_lr("characters", n, fr, 3 if n != "watch_phone_dong" else 2, notes="fireworks night watcher, face tilted up; anchor bottom-centre (feet)")
