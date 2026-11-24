from lib import *
from walkers import SCR, sheet
import sys

def bag_over_head(img, J, pose):
    shx, shy = J["sh"]
    headtop = J["head"][1]
    hx = shx + 6; hy = headtop - 1
    ex, ey = shx + 6, shy - 2
    # arm: upper arm (sleeve) forward-up, forearm vertical in front of the face
    line(img, shx, shy, ex, ey, "ink") if False else None
    limb(img, (shx, shy), (ex - 1, ey), "white", t=2)
    limb(img, (ex, ey), (hx, hy + 1), "skin2", t=1)
    put(img, ex - 1, ey + 1, "grey_l")
    t = pose.get("bagtilt", 0)
    x0, x1 = hx - 8, hx + 2
    y = hy - 1
    rect(img, x0, y - 1 + t, x1, y + 1, "gold")
    rect(img, x0, y - 1 + t, x1, y - 1 + t, "yellow")
    rect(img, x1 - 1, y, x1, y + 1, "orange")
    put(img, x0 + 2, y + 2, "orange"); put(img, x1 - 4, y + 2, "orange")
    put(img, hx, hy + 1, "skin2")

S = dict(skin="skin2", top=("white", "grey_l", "white"), hair="brown_k", hair_style="pony", woman=True,
         pants=("blue", "blue_d"), shoe="white", sleeve="short", extras=[bag_over_head])

def run_pose(i):
    xa = [5, 2, -2, -5, -2, 2]
    lifts = [0, 0, 0, 1, 4, 3]
    hips = [11, 12, 12, 11, 12, 12]
    A = xa[i]; B = xa[(i + 3) % 6]
    hip = hips[i]
    ph = 2 * math.pi * i / 6
    far_hand = (2 + 3.5 * math.cos(ph + math.pi), hip + 7 - 4 + 1.5 * math.sin(ph + math.pi))
    p = dict(hip=hip, near_ankle=(A, 1 + lifts[i]), far_ankle=(B, 1 + lifts[(i + 3) % 6]),
             near_hand=(6, hip + 15), far_hand=far_hand, lean=2, head_dx=0, head_dy=0,
             near_bend=-1, far_bend=-1, hair_sw=[0, 1, 1, 0, 1, 1][i], flare=1, trail=2,
             bagtilt=[0, 1, 0, 0, 1, 0][i])
    return p

if __name__ == "__main__":
    W, H = 36, 36
    fr = [draw_person(S, run_pose(i), W=W, H=H) for i in range(6)]
    sheet(fr, SCR + "run_rain_ha.png", 8)
    if "--export" in sys.argv:
        export_lr("characters", "run_rain_ha", fr, 12, notes="running, bag held over head; ~3.5px/frame ground speed (~42px/s @12fps)")
