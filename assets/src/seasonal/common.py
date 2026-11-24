"""Shared helpers for the seasonal group (not an asset script)."""
import sys, pathlib, math, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *
from tools.layout import *
from tools.mockbg import mock_scene, place, save_mock

G = "seasonal"


def thick(img, x0, y0, x1, y1, col, w=1):
    """line, w px wide horizontally"""
    for k in range(w):
        line(img, x0 + k, y0, x1 + k, y1, col)


# kinds of body proportions: head_h, head_w, torso_h, torso_w, leg_len, arm_len, swing, lift
KINDS = {
    "kid":   dict(hh=6, hw=6, th=6, tw=5, ll=8, al=5, A=4, lm=2),
    "adult": dict(hh=7, hw=6, th=10, tw=6, ll=11, al=8, A=4, lm=2),
}


def legs(img, cx, by, i, n, kind, pants, pants_d, shoes, drop=None, near=True, w=2, phase=0.0):
    """draw both legs. returns hip_y."""
    k = KINDS[kind]
    a = 2 * math.pi * (i / n + phase)
    if drop is None:
        drop = 1 if (i % (n // 2)) == 0 else 0
    hip_y = by - k["ll"] + 1 + drop
    fa = round(k["A"] * math.cos(a))
    sa = math.sin(a)
    for who in ("far", "near"):
        sgn = -1 if who == "far" else 1
        fx = fa * sgn
        sw = sa * sgn  # >0 backward
        lift = round(k["lm"] * max(0.0, -sw))
        col = pants if who == "near" else pants_d
        thick(img, cx + 0 + (0 if who == "near" else 0), hip_y, cx + fx, by - lift, col, w)
        # shoe: 1px forward of the foot
        put(img, cx + fx + w, by - lift, shoes)
        put(img, cx + fx + w - 1, by - lift, shoes)
        put(img, cx + fx, by - lift, shoes)
        if who == "far":
            put(img, cx + fx + w, by - lift, shoes)
    return hip_y


def torso(img, cx, hip_y, kind, shirt, shirt_d, shirt_l=None, hem=None):
    k = KINDS[kind]
    x0 = cx - k["tw"] // 2 + 1
    x1 = x0 + k["tw"] - 1
    y0 = hip_y - k["th"]
    rect(img, x0, y0, x1, hip_y, shirt)
    rect(img, x1, y0 + 1, x1, hip_y, shirt_d)
    if shirt_l:
        rect(img, x0, y0, x0, y0 + 2, shirt_l)
    if hem:
        rect(img, x0, hip_y, x1, hip_y, hem)
    return x0, x1, y0


def arms(img, sx, sy, i, n, kind, sleeve, sleeve_d, skin, near_to=None, far_to=None, w=1):
    k = KINDS[kind]
    a = 2 * math.pi * (i / n)
    sw = round(k["A"] * 0.8 * math.cos(a))
    far = far_to or (sx + sw, sy + k["al"])
    near = near_to or (sx - sw, sy + k["al"])
    hands = {}
    for who, (hx, hy), col in (("far", far, sleeve_d), ("near", near, sleeve)):
        thick(img, sx, sy, hx, hy, col, w)
        put(img, hx, hy, skin)
        hands[who] = (hx, hy)
    return hands


def head(img, cx, y0, kind, skin, skin_d, hair, hair_style="short", blush=True, hat=None):
    """profile head facing right. cx = centre x, y0 = top. returns (x0,x1,y_bot)"""
    k = KINDS[kind]
    hw, hh = k["hw"], k["hh"]
    x0 = cx - hw // 2 + 1
    x1 = x0 + hw - 1
    rect(img, x0, y0 + 1, x1, y0 + hh - 1, skin)
    rect(img, x0 + 1, y0, x1 - 1, y0 + hh - 1, skin)
    # chin/neck shade
    rect(img, x0 + 1, y0 + hh - 1, x1 - 1, y0 + hh - 1, skin_d)
    # hair: top + back (kept light so the face reads)
    rect(img, x0, y0, x1 - 1, y0, hair)
    rect(img, x0, y0, x0 + 1, y0 + 2, hair)
    put(img, x1 - 1, y0 + 1, hair)
    put(img, x1, y0 + 1, hair)
    if hair_style == "long":
        rect(img, x0, y0 + 1, x0 + 1, y0 + hh + 3, hair)
    if hair_style == "bob":
        rect(img, x0, y0, x0 + 1, y0 + hh - 1, hair)
        put(img, x0 + 2, y0 + 1, hair)
    if hair_style == "pony":
        rect(img, x0 - 1, y0 + 1, x0 - 1, y0 + hh, hair)
        rect(img, x0, y0, x0 + 1, y0 + 2, hair)
    # eye + nose
    ey = y0 + hh // 2
    put(img, x1 - 1, ey, "ink")
    put(img, x1 + 1, ey + 1, skin)  # nose
    if blush:
        put(img, x1 - 2, ey + 1, "salmon")
    return x0, x1, y0 + hh - 1
