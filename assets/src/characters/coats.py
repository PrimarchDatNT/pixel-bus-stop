"""Coat variants: recolor / region-paint the master (orange tabby) cat frames."""
from lib import *

def _map(frame, m):
    return recolor(frame, m)

BLACK = {"orange": "navy", "gold": "slate", "clay": "ink", "rust": "ink", "brown_d": "ink",
         "white": "slate_d", "grey_l": "navy", "green_l": "yellow", "brown_k": "ink"}
BLACK_KEEPWHITE = {"orange": "navy", "gold": "slate", "clay": "ink", "rust": "ink", "brown_d": "ink", "brown_k": "ink"}
GREY = {"orange": "grey", "gold": "grey_l", "clay": "slate", "rust": "slate_d", "brown_d": "slate_d", "brown_k": "navy"}
WHITE_MAP = {"orange": "white", "gold": "white", "clay": "grey_l", "rust": "grey_l", "brown_d": "grey_l"}
BLACK_MAP = {"orange": "navy", "gold": "slate", "clay": "ink", "rust": "ink", "brown_d": "ink"}
FAM = {RGB[k] for k in ("orange", "gold", "clay", "rust", "brown_d")}


def rim(frame, body="navy"):
    """slate rim light on top/left edges so black fur reads on dark ground (call before outline remap)"""
    out = frame.copy(); px = frame.load(); po = out.load()
    for y in range(1, frame.height):
        for x in range(1, frame.width):
            p = px[x, y]
            if p[3] and p[:3] == RGB[body]:
                for q in (px[x, y - 1], px[x - 1, y]):
                    if q[3] and q[:3] == RGB["brown_k"]:
                        po[x, y] = c("slate"); break
    return out


def calico(frame, ctx):
    out = frame.copy(); px = frame.load(); po = out.load()
    hx, hy, hw = ctx["head"]
    x0, x1, tops = ctx["torso"]
    tail = ctx["tail"]; n = len(tail)
    tailpix = {}
    for i, (x, y) in enumerate(tail):
        for p in ((x, y), (x + 1, y), (x, y + 1)):
            tailpix[p] = i / max(1, n - 1)
    tail_after = ctx.get("tail_after", False)
    for y in range(frame.height):
        for x in range(frame.width):
            p = px[x, y]
            if not p[3] or p[:3] not in FAM:
                continue
            dx, dy = x - hx, y - hy
            if 0 <= dx < hw and 0 <= dy < 12:
                front = hw == 14
                if front:
                    cls = "O" if (dx < 7 and dy <= 8) else "B" if (dx >= 7 and dy <= 8) else "W"
                else:
                    cls = "O" if (dx <= 6 and dy <= 5) else "B" if (dx >= 7 and dy <= 3) else "W"
            else:
                in_torso = x0 <= x <= x1 and y >= tops.get(x, 99) - 1
                if (x, y) in tailpix and (tail_after or not in_torso):
                    cls = "O" if tailpix[(x, y)] < 0.45 else "B"
                elif in_torso:
                    fr = (x - x0) / max(1, x1 - x0); d = y - tops[x]
                    if 0.28 <= fr <= 0.62 and d <= 6: cls = "O"
                    elif fr < 0.22 and d <= 7: cls = "B"
                    else: cls = "W"
                else:
                    cls = "W"
            if cls == "W":
                m = WHITE_MAP
            elif cls == "B":
                m = BLACK_MAP
            else:
                continue
            for k, v in m.items():
                if p[:3] == RGB[k]:
                    po[x, y] = c(v); break
    return out


def apply_coat(frame, ctx, coat):
    if coat == "orange":
        return frame
    if coat == "black":
        f = recolor(frame, {"orange": "navy"}); f = rim(f)
        return recolor(f, BLACK)
    if coat == "tuxedo":
        f = recolor(frame, {"orange": "navy"}); f = rim(f)
        return recolor(f, BLACK_KEEPWHITE)
    if coat == "grey":
        return recolor(frame, GREY)
    if coat == "calico":
        return calico(frame, ctx)
    raise ValueError(coat)
