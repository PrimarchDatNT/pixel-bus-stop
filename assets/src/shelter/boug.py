import math, random
from common import *

RAMPS = {
    "bloom": ["bloom_k", "bloom_d", "bloom", "bloom_l", "bloom_hl"],
    "leaf":  ["teal_k", "green_d", "green", "green_l", "mint"],
    "dry":   ["brown_d", "green_d", "green", "green_l", "ochre"],
    "fade":  ["plum", "bloom_k", "mauve", "salmon", "skin1"],
    "paper": ["brown_d", "rust", "skin4", "skin3", "skin2"],
    "brown": ["brown_k", "brown_d", "rust", "clay", "ochre"],
    "dark":  ["teal_k", "teal_k", "green_d", "green", "green"],
}
LOOKUP = {}
for rn, rr in RAMPS.items():
    for i, n in enumerate(rr):
        LOOKUP.setdefault(RGB[n], (rn, i))

CTRL = [(150, 112), (160, 103), (175, 93), (195, 87), (215, 91), (235, 88), (255, 93), (270, 101), (284, 113)]


def prof(x):
    if x <= CTRL[0][0]: return CTRL[0][1]
    for (x0, y0), (x1, y1) in zip(CTRL, CTRL[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return CTRL[-1][1]


# ------------------------------------------------------------------ skeleton (identical for all seasons)
def build_skeleton(seed=11):
    rng = random.Random(seed)
    S = {"masses": [], "blobs": [], "drapes": [], "limbs": [], "twigs": []}
    # canopy masses: poisson-ish scatter + a roof-edge row
    pts = []
    for _ in range(4000):
        x = rng.uniform(154, 284)
        y = rng.uniform(prof(x) + 3, 121)
        R_ = rng.uniform(5.5, 8.5)
        if all((x - a) ** 2 + (y - b) ** 2 > (R_ * 0.8 + c * 0.8) ** 2 for a, b, c in pts):
            pts.append((x, y, R_))
    for x in range(156, 286, 8):
        pts.append((x + rng.uniform(-2, 2), prof(x) + rng.uniform(3, 5), rng.uniform(5, 6.5)))
    for x in range(160, 284, 8):
        y = 118 + rng.uniform(-2.5, 1.5)
        pts.append((x + rng.uniform(-3, 3), y, rng.uniform(3.8, 6.5)))
    for (x, y, r) in ((264, 100, 6.0), (272, 105, 5.0), (276, 111, 4.5)):
        pts.append((x, y, r))
    # right side spill masses
    for (x, y, r) in ((279, 124, 4.0), (277, 131, 3.4), (280, 138, 3.0), (279, 144, 2.6)):
        pts.append((x, y, r))
    # left: vine tufts hugging the trunk / pillar, and low planter bush
    for (x, y, r) in ((158, 118, 4.5), (152, 112, 4.5), (156, 131, 2.4), (169, 140, 2.0), (158, 149, 2.2),
                      (146, 160, 3.0), (153, 158, 2.6), (160, 155, 2.0)):
        pts.append((x, y, r))
    for i, (x, y, R_) in enumerate(pts):
        mv = rng.random()
        S["masses"].append(dict(cx=x, cy=y, R=R_))
        n = max(3, int(R_ * R_ * 0.85))
        for _ in range(n):
            a = rng.uniform(0, 6.283); d = math.sqrt(rng.random()) * R_ * 0.92
            bx, by = x + math.cos(a) * d, y + math.sin(a) * d * 0.9
            r = rng.uniform(1.3, 2.4)
            if y < 135 and by + r > 123.2: continue
            if y >= 135 and by + r > 168: continue
            ux, uy = (bx - x) / R_, (by - y) / R_
            top = prof(bx)
            tipness = by < top + 5
            S["blobs"].append(dict(x=bx, y=by, r=r, ux=ux, uy=uy, u1=rng.random(), u2=0.5 * mv + 0.5 * rng.random(), u3=rng.random(),
                                   z=rng.random() * 0.55 + 0.45 * ((by - top) / 30.0), notch=rng.randrange(4),
                                   tip=tipness or bx < 156 or bx > 280, ph=rng.random(), mass=i, drape=False,
                                   low=(y >= 135 or bx < 158)))
    # drapes hanging over the roof front edge
    x = 158
    while x < 282:
        L = rng.choice([5, 7, 9, 11, 14, 17])
        if 194 <= x <= 245: L = rng.choice([2, 3, 4, 5])
        if 246 <= x <= 266: L = rng.choice([3, 5, 6])
        if x < 172: L = rng.choice([9, 12, 15, 18])
        if x > 268: L = rng.choice([14, 18, 22, 26])
        S["drapes"].append(dict(x=x, L=L, ph=rng.random(), wig=rng.uniform(0, 6.28)))
        x += rng.choice([3, 4, 4, 5, 6])
    # a few longer drapes spilling over the front fascia
    for lo, hi, L in ((176, 190, 20), (176, 190, 17), (250, 258, 13)):
        for d in S["drapes"]:
            if lo <= d["x"] <= hi and d["L"] < L and not d.get("long"):
                d["L"] = L; d["long"] = True; break
    # planter trailing vines
    for x, L in ((141, 7), (144, 5), (147, 4), (156, 4), (159, 6)):
        S["drapes"].append(dict(x=x, L=L, ph=rng.random(), wig=rng.uniform(0, 6.28), y0=165, planter=True))
    for d in S["drapes"]:
        y0 = d.get("y0", 122)
        bl = []
        n = d["L"]
        yy = 0
        while yy < n:
            f = yy / max(1, n)
            r = 2.3 - 1.3 * f + rng.uniform(-0.3, 0.3)
            wx = d["x"] + math.sin(d["wig"] + yy * 0.45) * 0.9
            bl.append(dict(x=wx + rng.uniform(-0.8, 0.8), y=y0 + yy + 1, r=max(1.2, r), frac=f, u1=rng.random(), u2=rng.random(),
                           u3=rng.random(), z=2 + rng.random(), notch=rng.randrange(4), ph=d["ph"], ux=rng.uniform(-.5, .5), uy=f - .3))
            yy += rng.choice([2, 2, 3])
        d["blobs"] = bl
    # woody limbs: (points, width)
    S["limbs"] = [
        ([(166, 124), (170, 120), (182, 119), (200, 121), (222, 119), (246, 121), (266, 120), (281, 121)], 2),
        ([(167, 123), (170, 113), (178, 104), (190, 98), (204, 94)], 2),
        ([(190, 120), (198, 110), (209, 102), (224, 97)], 1),
        ([(232, 120), (240, 110), (248, 102), (260, 99)], 1),
        ([(256, 121), (266, 114), (275, 109), (283, 112)], 1),
        ([(168, 122), (158, 116), (154, 110)], 1),
        ([(212, 121), (214, 111), (222, 106), (232, 106)], 1),
    ]
    # twigs sprout off limbs
    for pts_, w in S["limbs"]:
        for (a, b) in zip(pts_, pts_[1:]):
            for t in (0.3, 0.7):
                px_, py_ = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                for _ in range(2):
                    ang = rng.uniform(-3.0, -0.1)
                    ln = rng.uniform(4, 9)
                    tw = [(px_, py_)]
                    cx_, cy_ = px_, py_
                    for k in range(3):
                        ang += rng.uniform(-0.6, 0.6)
                        cx_ += math.cos(ang) * ln / 3; cy_ += math.sin(ang) * ln / 3
                        tw.append((cx_, cy_))
                    S["twigs"].append(tw)
    S["petals"] = [(rng.randrange(138, 172), rng.randrange(175, 179)) for _ in range(26)]
    return S


SK = build_skeleton()

SEASON = {
    #        keep   bloom   faded  (kind thresholds)
    "ha":   dict(keep=1.0, bloom=0.90, faded=0.0, core=1.0, drape_keep=1.0),
    "xuan": dict(keep=0.93, bloom=0.0, faded=0.0, core=1.0, drape_keep=0.9, bud=0.11),
    "thu":  dict(keep=0.62, bloom=0.48, faded=0.5, core=0.55, drape_keep=0.6),
    "dong": dict(keep=0.12, bloom=0.22, faded=0.0, core=0.0, drape_keep=0.30),
}


def darken(im, x, y, steps=1):
    p = getp(im, x, y)
    if p[3] == 0: return
    k = LOOKUP.get(p[:3])
    if not k: return
    rn, i = k
    P(im, x, y, RAMPS[rn][max(0, i - steps)])


def footprint(cx, cy, r, notch):
    fp = []
    ci, cj = int(round(cx)), int(round(cy))
    ri = int(math.ceil(r))
    for dy in range(-ri, ri + 1):
        for dx in range(-ri, ri + 1):
            if dx * dx + dy * dy <= r * r + 0.4:
                fp.append((dx, dy))
    if notch == 0 and r > 1.6 and (1, 1) in fp: fp.remove((1, 1))
    if notch == 1 and r > 1.6 and (-1, 1) in fp: fp.remove((-1, 1))
    return ci, cj, fp


def blob(im, cx, cy, r, ramp, base, notch, shadow=True):
    ci, cj, fp = footprint(cx, cy, r, notch)
    S_ = set(fp)
    RP = RAMPS[ramp]
    if shadow:
        for dx, dy in fp:
            t = (dx + 1, dy + 2)
            if t not in S_:
                darken(im, ci + t[0], cj + t[1])
            t = (dx + 1, dy + 1)
            if t not in S_ and (dx, dy + 2) not in S_:
                darken(im, ci + t[0], cj + t[1])
    rr = max(r, 1.0)
    for dx, dy in fp:
        s = -(dx * 0.62 + dy * 0.78) / rr
        idx = base
        if s > 0.3: idx += 1
        elif s < -0.3: idx -= 1
        if idx >= 4 and s <= (0.55 if r >= 1.9 else 0.78): idx = 3
        idx = max(0, min(4, idx))
        P(im, ci + dx, cj + dy, RP[idx])


def thick_line(im, pts, w, cols):
    """polyline with bark shading: cols = (light, mid, dark)."""
    for (a, b) in zip(pts, pts[1:]):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) * 2 + 1
        for i in range(n + 1):
            x = a[0] + (b[0] - a[0]) * i / n; y = a[1] + (b[1] - a[1]) * i / n
            xi, yi = int(round(x)), int(round(y))
            if w == 1:
                P(im, xi, yi, cols[1])
            else:
                P(im, xi + 1, yi, cols[2]); P(im, xi, yi, cols[1]); P(im, xi, yi - 1, cols[0]) if i % 2 == 0 else None


def draw_trunk(im):
    bark = ("skin4", "brown_d", "brown_k")
    def centre(y, ph):
        s = max(0.0, min(1.0, (166 - y) / 16.0))
        base = 156 + (163 - 156) * s
        return base + 4.3 * s * math.sin((166 - y) / 6.8 + ph)
    # strand B (thinner) and A (thicker), front one drawn last
    for y in range(166, 121, -1):
        ca, cb = centre(y, 0.6), centre(y, 0.6 + math.pi)
        wa = 3 if y > 135 else 2
        wb = 2
        front_a = math.cos((166 - y) / 6.8 + 0.6) > 0
        def strand(c, w, tip):
            x0 = int(round(c)) - (1 if w == 3 else 0)
            for k in range(w):
                col = bark[0] if k == 0 else (bark[2] if k == w - 1 else bark[1])
                if w == 2: col = bark[0] if k == 0 else bark[2]
                P(im, x0 + k, y, col)
            if y % 9 == 4:   # knots
                P(im, x0 - 1, y, "brown_d"); P(im, x0, y - 1, "skin4")
            if y % 7 == 2:
                P(im, x0 + 1, y, "brown_d") if w == 3 else None
        if front_a:
            strand(cb, wb, 0); strand(ca, wa, 1)
        else:
            strand(ca, wa, 1); strand(cb, wb, 0)
    # base flare into the planter soil
    for dx in (-2, -1, 0, 1, 2, 3):
        P(im, 156 + dx, 164, "brown_d"); P(im, 156 + dx, 165, "brown_k")
    P(im, 154, 163, "skin4"); P(im, 155, 162, "skin4")


season_g = 'ha'


def draw_wood(im, sw):
    for pts_, w in SK["limbs"]:
        thick_line(im, pts_, w, ("skin4", "brown_d", "brown_k"))
    for tw in SK["twigs"]:
        if season_g != "dong" and any(p[1] < prof(p[0]) + 3 or p[0] < 156 or p[0] > 282 for p in tw): continue
        for (a, b) in zip(tw, tw[1:]):
            thick_line(im, [a, b], 1, ("skin4", "brown_d", "brown_k"))
    # drape stems
    for d in SK["drapes"]:
        y0 = d.get("y0", 122)
        for yy in range(d["L"]):
            f = yy / max(1, d["L"])
            sx = d["x"] + math.sin(d["wig"] + yy * 0.45) * 0.9
            off = sway_dx(f, d["ph"], sw)
            P(im, int(round(sx)) + off, y0 + yy, "brown_d" if yy % 3 else "green_d")


def sway_dx(frac, ph, sw, amp=1.7):
    if sw == 0: return 0
    v = amp * frac * math.sin(2 * math.pi * (sw / 3.0 + ph))
    return 0 if abs(v) < 0.8 else (1 if v > 0 else -1)


def tip_off(ph, sw):
    if sw == 0: return (0, 0)
    v = math.sin(2 * math.pi * (sw / 3.0 + ph))
    return (0 if abs(v) < 0.5 else (1 if v > 0 else -1), 0)


def draw_planter(im):
    R(im, 140, 163, 160, 163, "stone_l"); R(im, 140, 163, 140, 165, "stone_l")
    R(im, 141, 164, 159, 165, "brown_d"); R(im, 141, 164, 159, 164, "brown_k")
    for x in (143, 147, 151, 158): P(im, x, 165, "brown_k")
    P(im, 145, 164, "clay"); P(im, 149, 165, "rust")
    R(im, 160, 163, 160, 165, "stone")
    R(im, 140, 166, 160, 174, "stone")
    R(im, 140, 166, 160, 166, "stone_l"); R(im, 140, 166, 141, 174, "stone_l"); P(im, 141, 166, "grey_l")
    R(im, 159, 167, 160, 174, "stone_d"); R(im, 140, 174, 160, 174, "stone_d")
    R(im, 142, 168, 158, 168, "stone_d") if False else None
    for (x, y) in ((144, 170), (145, 171), (150, 169), (151, 170), (152, 171), (155, 172)):
        P(im, x, y, "stone_d")
    for (x, y) in ((142, 173), (143, 173), (146, 174), (153, 173)):
        P(im, x, y, "green_d")
    P(im, 143, 172, "green"); P(im, 142, 172, "green_d")
    R(im, 146, 167, 154, 167, "stone_l") if False else None


def render(season, sw):
    global season_g
    season_g = season
    P_ = SEASON[season]
    im = layer()
    draw_planter(im)
    draw_wood(im, sw)
    draw_trunk(im)
    keep_all = lambda b: b["u1"] < P_["keep"]
    # core (dark undergrowth) per mass
    core_col = {"ha": "bloom_k", "xuan": "teal_k", "thu": "plum", "dong": None}[season]
    if core_col:
        for m in SK["masses"]:
            if (m["cx"] * 7 + m["cy"] * 13) % 1.0 > P_["core"] and season != "ha": pass
            if hash((round(m["cx"]), round(m["cy"]))) % 100 / 100.0 > P_["core"]: continue
            cx, cy, R_ = m["cx"], m["cy"], m["R"] - 0.8
            if m["R"] < 5: continue
            ci, cj, fp = footprint(cx, cy + 0.5, max(1.5, R_), 5)
            for dx, dy in fp:
                P(im, ci + dx, cj + dy, core_col)
    items = []
    for b in SK["blobs"]:
        if b["u1"] >= P_["keep"]: continue
        items.append((b["z"], b, False))
    for d in SK["drapes"]:
        for b in d["blobs"]:
            if b["u1"] >= P_["drape_keep"]: continue
            items.append((b["z"] + 1.0, b, True))
    items.sort(key=lambda t: t[0])
    for z, b, isd in items:
        x, y = b["x"], b["y"]
        if isd:
            x += sway_dx(b["frac"], b["ph"], sw)
        elif b["tip"]:
            x += tip_off(b["ph"], sw)[0]
        # kind
        k = b["u2"]
        r = b["r"]
        if season == "ha":
            ramp = "bloom" if k < P_["bloom"] else "leaf"
            if not isd and b["z"] < 0.55 and b["u3"] < 0.28: ramp = "leaf"
        elif season == "xuan":
            ramp = "leaf"
        elif season == "thu":
            if k < P_["bloom"]:
                ramp = ("fade" if b["u3"] < P_["faded"] * 0.5 else "paper") if b["u3"] < P_["faded"] else "bloom"
            else:
                ramp = "dry"
        else:
            ramp = "bloom" if k < P_["bloom"] else "dark"
            r = min(r, 1.6) if ramp == "bloom" else r * 0.78
        # base tone from mass position / depth
        if isd:
            base = 3 - int(b["frac"] * 1.5)
        else:
            top = prof(b["x"])
            hrel = max(0.0, min(1.0, (b["y"] - top) / max(8.0, 122 - top)))
            mb = -(b["ux"] * 0.5 + b["uy"] * 0.9) * 1.5
            base = int(round(3.0 - 2.0 * hrel + mb * 0.8 + (b["u3"] - 0.5) * 0.9))
            if b["z"] < 0.5: base -= 1
            if b["low"]: base = max(base, 2)
        if ramp in ("leaf", "dry", "dark"): base -= 0 if ramp != "dark" else 0
        base = max(1, min(3, base))
        blob(im, x, y, r, ramp, base, b["notch"])
        if season == "xuan" and b["u3"] < P_["bud"] and not isd or (season == "xuan" and isd and b["u3"] < P_["bud"] * 0.8):
            blob(im, x - 1, y - 1, 1.3, "bloom", 3, 2, shadow=False)
            P(im, int(round(x)) - 2, int(round(y)) - 2, "bloom_hl")
    # petals on ground
    if season in ("ha", "thu", "xuan"):
        cnt = {"ha": 26, "thu": 14, "xuan": 3}[season]
        for (x, y) in SK["petals"][:cnt]:
            P(im, x, y, "bloom" if season == "ha" else ("mauve" if season == "thu" else "bloom_l"))
            if season == "ha" and (x + y) % 3 == 0: P(im, x + 1, y, "bloom_d")
    return im


def make(season):
    return [render(season, f) for f in range(3)]


if __name__ == "__main__":
    import sys
    seasons = sys.argv[1:] or SEASONS_
    for s in seasons:
        export("bougainvillea_" + s, make(s), fps=3,
               notes="Layer bougainvillea. 3 sway frames @3fps (drapes/outer tips +-1px, core static). Planter centre x150 (box x140-160,y163-174), trunk twists up left pillar, canopy y92-123 over roof, drapes over front edge, spill on right to y~150.")
