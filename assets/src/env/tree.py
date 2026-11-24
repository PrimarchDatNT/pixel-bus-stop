import sys, pathlib, random, math; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *; from tools.layout import *; from tools.mockbg import mock_scene, place, save_mock

FX, FY, FW = 350, 30, 130           # frame origin in scene coords
TH = 137                            # trunk frame height (y 30..166)
CH = 95                             # canopy frame height (y 30..124)
XC = TREE_X - FX                    # trunk centre local x (68)
def LY(y): return y - FY
# (scene y of branch root, reach left, reach right)
TIERS = [(106, 60, 66), (90, 52, 58), (75, 44, 48), (61, 34, 36), (48, 22, 24)]

def branch_y(y0, side, t, L):
    return y0 - round(t * 0.10 + math.sin(t * 0.35 + side) * 0.9) + (1 if t > L * .8 else 0)

def trunk_img():
    img = new(FW, TH)
    base = LY(TREE_BASE_Y)
    top = LY(46)
    for y in range(top, base + 1):
        f = (y - top) / (base - top)
        cx = XC
        hw = 2 + round(f * 2.2) + (1 if y > base - 14 else 0) + (1 if y > base - 7 else 0) + (1 if y > base - 3 else 0)
        x0, x1 = cx - hw, cx + hw - 1
        rect(img, x0, y, x1, y, "brown_d")
        put(img, x0, y, "skin4"); put(img, x0 + 1, y, "skin4") if y % 3 else None
        put(img, x1, y, "brown_k"); put(img, x1 - 1, y, "brown_k") if y % 2 else None
        if (y * 7) % 11 < 3: put(img, cx, y, "brown_k")
        if (y * 5) % 13 == 0: put(img, x0 + 1, y, "skin3")
    # root flare + knots
    for dx in (-1, 1):
        for k in range(3): put(img, XC + dx * (7 + k), base - k, "brown_d")
    put(img, XC - 2, base - 26, "brown_k"); put(img, XC - 2, base - 25, "brown_k"); put(img, XC + 1, base - 40, "brown_k")
    put(img, XC - 3, base - 26, "skin4")
    # tiered branches
    for (y0, Ll, Lr) in TIERS:
        yy0 = LY(y0)
        for side, L in ((-1, Ll), (1, Lr)):
            for t in range(0, L + 1):
                by = branch_y(yy0, side, t, L)
                th = 3 if t < L * .35 else (2 if t < L * .75 else 1)
                x = XC + side * (t + 2)
                if th == 3:
                    put(img, x, by - 1, "skin4"); put(img, x, by, "brown_d"); put(img, x, by + 1, "brown_k")
                elif th == 2:
                    put(img, x, by, "skin4" if side < 0 or t % 2 else "brown_d"); put(img, x, by + 1, "brown_k")
                else:
                    put(img, x, by, "brown_d")
            # forks / twigs
            tt = 8
            while tt < L - 2:
                x = XC + side * (tt + 2); by = branch_y(yy0, side, tt, L)
                n = 3 + (tt % 3)
                for k in range(1, n + 1): put(img, x + side * (k // 2), by - k, "brown_d")
                put(img, x + side * (n // 2 + 1), by - n, "brown_d") if n > 3 else None
                tt += 8 + (tt % 5)
            # tip twigs
            x = XC + side * (L + 2); by = branch_y(yy0, side, L, L)
            for k in range(1, 4): put(img, x + side * k, by - k, "brown_d")
    return img

def clump_list():
    """Flat pagoda pads along each tier. (cx, cy, rx, ry, rank, tier, row)"""
    rr = random.Random(33)
    out = []
    for ti, (y0, Ll, Lr) in enumerate(TIERS):
        yy0 = LY(y0)
        for side, L in ((-1, Ll), (1, Lr)):
            t = 4
            k = 0
            while t < L + 2:
                x = XC + side * (t + 2)
                by = branch_y(yy0, side, min(t, L), L)
                tip = t > L - 10
                rx = (8 + rr.randrange(0, 3)) if not tip else 6
                out.append((x, by - 1, rx, 3, rr.random(), ti, 0))
                if not tip or t < L - 4:
                    out.append((x + side * 4 + rr.randrange(-1, 2), by - 4 - (k % 2), rx - 1, 3, rr.random(), ti, 1))
                t += 8 + rr.randrange(0, 3); k += 1
        out.append((XC, yy0 - 3, 9, 3, rr.random(), ti, 1))
        out.append((XC - 7, yy0 - 1, 8, 3, rr.random(), ti, 0)); out.append((XC + 7, yy0 - 1, 8, 3, rr.random(), ti, 0))
    out.append((XC, LY(42), 7, 3, 0.0, 5, 1)); out.append((XC - 5, LY(45), 6, 3, 0.1, 5, 0)); out.append((XC + 5, LY(45), 6, 3, 0.1, 5, 0))
    return out

def clump(img, cx, cy, rx, ry, ramp, rr):
    dk, base, lt, hl = ramp
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=c(dk))
    d.ellipse([cx - rx, cy - ry, cx + rx - 1, cy + ry - 1], fill=c(base))
    if rx >= 4:
        d.ellipse([cx - rx + 1, cy - ry, cx + rx - 4, cy + ry - 2], fill=c(lt))
    # leaf-scallop texture: a few dk notches inside base, light flecks top-left
    for _ in range(max(1, rx // 2)):
        x = cx + rr.randrange(-rx + 1, rx); y = cy + rr.randrange(0, max(1, ry - 1))
        put(img, x, y, dk)
    for k in range(max(2, rx // 2)):
        a = math.pi * (1.05 + .3 * k / max(1, rx // 2 - 1 if rx > 3 else 1))
        put(img, cx + round(math.cos(a) * (rx - 1.5)), cy + round(math.sin(a) * (ry - 1)), hl)
    put(img, cx - rx // 2, cy - ry + 1, hl)

from PIL import ImageDraw

SEASON = {
    "xuan": dict(keep=.55, shrink=.78, ramps=[("green", "green_l", "green_l", "yellow")]),
    "ha":   dict(keep=1.01, shrink=1.0, ramps=[("green_d", "green", "green_l", "yellow"), ("teal_k", "green_d", "green", "green_l")]),
    "thu":  dict(keep=.9, shrink=1.0, ramps=[("rust", "orange", "gold", "yellow"), ("orange", "gold", "yellow", "glow"),
                                              ("rust", "clay", "orange", "gold"), ("brown_d", "rust", "clay", "orange"),
                                              ("green_d", "green", "green_l", "yellow")]),
    "dong": dict(keep=.13, shrink=.35, ramps=[("red_d", "rust", "red", "orange")]),
}

def canopy(season, frame=0):
    cfg = SEASON[season]
    img = new(FW, CH)
    rr = random.Random(77 + hash(season) % 1000 if False else 77)
    cl = sorted(clump_list(), key=lambda t: (-t[5], t[6]))  # top tiers first (back), lower tiers front
    for i, (cx, cy, rx, ry, rank, ti, row) in enumerate(cl):
        if rank > cfg["keep"]: continue
        cy = cy - (FY - FY)   # local already (frame y origin = FY)
        rx2 = max(2, round(rx * cfg["shrink"])); ry2 = max(1, round(ry * cfg["shrink"]))
        if season == "dong": rx2, ry2 = 2 + (i % 2), 1 + (i % 2)
        # sway: outer clumps shift 1px on frame 1
        dx = dy = 0
        if frame == 1:
            dist = abs(cx - XC)
            if dist > 24: dx = 1 if (i % 2) else -1 if dist > 40 else 0
            if i % 3 == 0 and dist > 12: dy = 1
        rl = random.Random(i * 13 + 5)
        if season == "thu":
            r = rl.random()
            ramp = cfg["ramps"][0 if r < .28 else 1 if r < .55 else 2 if r < .75 else 3 if r < .88 else 4]
        elif season == "ha": ramp = cfg["ramps"][0 if ti % 2 == 0 or row else 1]
        else: ramp = cfg["ramps"][0]
        clump(img, cx + dx, cy + dy, rx2, ry2, ramp, rl)
        if season == "xuan":  # sparse: tiny extra leaf specks around clump so edges feel airy
            for _ in range(3):
                put(img, cx + dx + rl.randrange(-rx2 - 2, rx2 + 3), cy + dy + rl.randrange(-ry2 - 2, ry2 + 2), "green_l")
    return img

if __name__ == "__main__":
    tr = trunk_img()
    save_asset("env", "tree_trunk", tr, anchor=(XC, TREE_BASE_Y - FY), notes=f"130x137, place top-left at ({FX},{FY}); trunk base at ({TREE_X},{TREE_BASE_Y}). Draw ground BEFORE it. Canopy layers share the same top-left origin.")
    outs = {}
    for s in ("xuan", "ha", "thu", "dong"):
        frames = [canopy(s, 0), canopy(s, 1)] if s in ("ha", "thu") else canopy(s)
        outs[s] = frames
        save_asset("env", f"tree_canopy_{s}", frames, fps=2 if s in ("ha", "thu") else None, anchor=(XC, 0),
                   notes=f"130x95, place top-left at ({FX},{FY}) (same origin as tree_trunk). " + ("2 sway frames @2fps." if s in ("ha", "thu") else "static."))
    for s in ("xuan", "ha", "thu", "dong"):
        bg = new(W, H); rect(bg, 0, 0, W - 1, H - 1, "sky_l"); rect(bg, 0, FAR_SIDEWALK_Y0, W - 1, 269, "stone_l")
        bg.alpha_composite(tr, (FX, FY)); f = outs[s]; bg.alpha_composite(f[0] if isinstance(f, list) else f, (FX, FY))
        save_mock(bg.crop((330, 20, 480, 180)), "env", f"tree_check_{s}", 4)
