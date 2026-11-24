"""Characters rig: one reusable skeleton (IK legs/arms) + outfit specs + ASCII heads.

Frame conventions: sprite facing RIGHT, drawn on a canvas, 1px ink outline added, bottom row = feet
(no outline under the shoes), anchor bottom-centre (x = CX).
"""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *
from tools.layout import *
from tools.mockbg import mock_scene, place, save_mock

R = lambda v: int(math.floor(v + 0.5))
_put0 = put
def put(img, x, y, name):
    _put0(img, R(x), R(y), name)

# ------------------------------------------------------------------ primitives
def bres(x0, y0, x1, y1):
    x0, y0, x1, y1 = map(R, (x0, y0, x1, y1))
    pts = []
    dx = abs(x1 - x0); dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy
    return pts


def limb(img, p0, p1, col, t=2, ox=0):
    steep = abs(p1[1] - p0[1]) >= abs(p1[0] - p0[0])
    for x, y in bres(p0[0], p0[1], p1[0], p1[1]):
        for k in range(t):
            if steep: put(img, x + k + ox, y, col)
            else: put(img, x + ox, y + k, col)


def ik(hip, foot, l1, l2, bend=1):
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    d = math.hypot(dx, dy)
    d = min(d, l1 + l2 - 0.01); d = max(d, abs(l1 - l2) + 0.01)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    ux, uy = dx / math.hypot(dx, dy) if (dx or dy) else 0, dy / math.hypot(dx, dy) if (dx or dy) else 1
    mx, my = hip[0] + ux * a, hip[1] + uy * a
    knee = (mx + uy * h * bend, my - ux * h * bend)
    # true foot after clamping
    end = (hip[0] + ux * d, hip[1] + uy * d)
    return knee, end


def blit_grid(img, rows, legend, x, y):
    g = grid(rows, legend)
    paste(img, g, x, y)


def finish(img, W, H, clear_below=True):
    """add ink outline; crop back; drop outline row under feet. Canvas feet row must be H-2."""
    o = outline(img, "ink")
    o = o.crop((1, 1, W + 1, H))   # drops last (below-feet) row
    return o

# ------------------------------------------------------------------ heads (7x7 facing right)
# H hair, h hair hi, S skin, s skin shade, e eye
HEADS = {
    "short": [".hHHHH.", "hHHHHHH", "HHHHSSS", "HHsSSeS", ".HsSSSS", "..SSSSS", "...SSs."],
    "long":  [".hHHHH.", "hHHHHHH", "HHHHHSS", "HHHsSeS", "HHHsSSS", "HH.SSSS", "H..SSs."],
    "pony":  [".hHHHH.", "hHHHHHH", "HHHHHSS", "HHHsSeS", ".HHsSSS", "..sSSSS", "...SSs."],
    "bald":  [".HHHH..", "HHHHHH.", "HHHSSSS", "HHsSSeS", ".HsSSSS", "..SSSSS", "...SSs."],
    "full":  [".hHHHH.", "hHHHHHH", "HHHHHHH", "HHsSSeS", ".HsSSSS", "..SSSSS", "...SSs."],
}
HEAD_KID = [".hHHH.", "hHHHHH", "HHHSSS", "HsSSeS", ".sSSSS", "..SSs."]


def head_img(style, skin, hair, hair_hi=None, kid=False, mask=False, glasses=False):
    skin_sh = {"skin1": "skin2", "skin2": "skin3", "skin3": "skin4", "skin4": "brown_d"}[skin]
    leg = {"H": hair, "h": hair_hi or hair, "S": skin, "s": skin_sh, "e": "ink"}
    rows = HEAD_KID if kid else HEADS[style]
    g = grid(rows, leg)
    if mask:   # khau trang over nose/mouth
        w = g.width
        for (x, y) in [(w - 1, 4), (w - 2, 4), (w - 3, 4), (w - 1, 5), (w - 2, 5), (w - 3, 5), (w - 4, 5), (w - 3, 6)]:
            if y < g.height and g.getpixel((x, y))[3]:
                put(g, x, y, "white")
    if glasses:
        put(g, g.width - 1, 3, "ink")
    return g

# ------------------------------------------------------------------ dims
D_ADULT = dict(L1=6, L2=5, torso=8, head=7, A1=4, A2=4, kid=False)
D_KID = dict(L1=4, L2=3, torso=5, head=6, A1=3, A2=3, kid=True)

SKIN_SH = {"skin1": "skin2", "skin2": "skin3", "skin3": "skin4", "skin4": "brown_d"}


def shade_of(col):
    """darker neighbour on the ramp (for far limbs / shadow side)"""
    return {"red": "red_d", "red_d": "brown_d", "white": "grey_l", "grey_l": "grey", "grey": "slate",
            "sand": "ochre", "ochre": "clay", "clay": "rust", "rust": "brown_d", "mint": "green",
            "green": "green_d", "blue": "blue_d", "blue_d": "navy", "slate": "slate_d", "slate_d": "navy",
            "navy": "ink", "salmon": "mauve", "mauve": "plum", "plum": "bloom_k", "gold": "orange",
            "orange": "rust", "yellow": "gold", "brown_d": "brown_k", "brown_k": "ink", "ink": "ink",
            "stone": "stone_d", "stone_l": "stone", "skin1": "skin2", "skin2": "skin3", "skin3": "skin4",
            "skin4": "brown_d", "sky": "blue", "green_d": "teal_k", "teal_k": "ink", "bloom_l": "bloom",
            "bloom": "bloom_d", "bloom_d": "bloom_k", "red_hot": "red", "sky_l": "sky", "stone_d": "navy",
            "slate_dd": "navy"}.get(col, col)


def lighter_of(col):
    inv = {}
    for k in ("red", "sand", "grey", "grey_l", "ochre", "clay", "mint", "green", "blue", "slate", "gold",
             "mauve", "brown_d", "plum", "salmon", "orange", "slate_d", "navy", "red_d", "blue_d", "rust"):
        inv[shade_of(k)] = k
    inv.update({"red": "salmon", "white": "white", "sand": "white", "grey_l": "white", "salmon": "bloom_hl",
                "skin1": "white", "skin2": "skin1", "skin3": "skin2", "skin4": "skin3", "gold": "yellow",
                "mint": "grey_l", "blue": "sky", "slate": "grey", "slate_d": "slate", "navy": "slate_d",
                "ochre": "yellow", "clay": "orange", "green": "green_l", "grey": "grey_l", "brown_d": "rust",
                "brown_k": "brown_d", "ink": "navy", "blue_d": "blue", "red_d": "red", "rust": "clay"})
    return inv.get(col, col)

# ------------------------------------------------------------------ the rig
def joints(D, pose, cx, fy):
    Y = lambda d: fy - d
    hdy = pose["hip"]
    hip = (R(cx + pose.get("hipx", 0)), R(Y(hdy)))
    lean = pose.get("lean", 0)
    top_dy = hdy + D["torso"]
    sh = (R(cx + lean), R(Y(top_dy - 1)))
    J = dict(hip=hip, sh=sh, top_dy=top_dy, Y=Y, cx=cx, fy=fy)
    for name in ("far", "near"):
        ax, ady = pose[name + "_ankle"]
        knee, end = ik(hip, (cx + ax, Y(ady)), D["L1"], D["L2"], 1)
        J[name + "_leg"] = (hip, (R(knee[0]), R(knee[1])), (R(cx + ax), R(Y(ady))))
    for name in ("far", "near"):
        hx, hy = pose[name + "_hand"]          # hand target: (x off from cx, dy)
        tgt = (cx + hx, Y(hy))
        bend = pose.get(name + "_bend", -1)
        elbow, end = ik(sh, tgt, D["A1"], D["A2"], bend)
        J[name + "_arm"] = (sh, (R(elbow[0]), R(elbow[1])), (R(end[0]), R(end[1])))
    hx0 = cx + lean + pose.get("head_dx", 0) - 2
    hy0 = Y(top_dy + D["head"]) + 0 + pose.get("head_dy", 0) + 1 - 1
    J["head"] = (R(hx0), R(hy0))
    return J


def draw_person(S, pose, W=32, H=30, D=None, cx=None):
    """S: outfit spec dict. returns finished RGBA frame."""
    D = D or (D_KID if S.get("kid") else D_ADULT)
    cx = cx if cx is not None else W // 2
    fy = H - 2
    img = new(W, H)
    J = joints(D, pose, cx, fy)
    Y = J["Y"]
    skin = S["skin"]; skin_sh = SKIN_SH[skin]
    top = S["top"]; tb, ts, th = top   # base, shade, hi
    sleeve = S.get("sleeve", "short")
    pants = S.get("pants", ("slate_d", "navy"))
    shoe = S.get("shoe", "brown_k")
    hair = S.get("hair", "ink"); hair_hi = S.get("hair_hi") or lighter_of(hair)
    puffer = S.get("puffer", False)
    hip = J["hip"]; sh = J["sh"]
    lean = pose.get("lean", 0)
    kid = D["kid"]

    # --- back accessories (backpack, long hair trail)
    if S.get("hair_style") in ("long",) and not S.get("hat_nonla"):
        hx, hy = J["head"]
        sw = pose.get("hair_sw", 0)
        bot = hip[1] - (3 if not kid else 1) - (1 if S.get("hair_len") == "mid" else 0) + (4 if S.get("hair_len") == "mid" else 0)
        if S.get("hair_len") == "mid":
            bot = sh[1] + 2
        else:
            bot = sh[1] + 6
        poly(img, [(hx, hy + 2), (hx + 3, hy + 2), (sh[0] - 2 + 1, bot), (sh[0] - 4 + sw, bot)], hair)
        # shade rim
        line(img, sh[0] - 4 + sw, bot, sh[0] - 3 + sw, bot - 3, shade_of(hair)) if hair != "ink" else None
    if S.get("backpack"):
        bp = S["backpack"]
        bw, bh = (5, 7) if not kid else (5, 7)
        bx = sh[0] - 3 - bw + 1 + 0
        by = sh[1] + 1
        rect(img, bx, by, bx + bw - 1, by + bh - 1, bp)
        rect(img, bx + bw - 1, by, bx + bw - 1, by + bh - 1, shade_of(bp))
        rect(img, bx, by, bx + bw - 2, by, lighter_of(bp))
        rect(img, bx + 1, by + bh - 3, bx + bw - 3, by + bh - 3, shade_of(bp))   # pocket line

    # --- far leg & far arm
    def leg_draw(name, shade):
        hp, kn, an = J[name + "_leg"]
        up, lo = pants
        if shade:
            up, lo = shade_of(up), shade_of(lo)
        base_up, base_lo = (up, lo)
        if S.get("shorts"):
            limb(img, kn, an, skin_sh if shade else skin, t=2 if not S.get("thin_shin") else 1, ox=-1)
            limb(img, hp, kn, S["shorts"] if not shade else shade_of(S["shorts"]), t=3, ox=-1)
        else:
            limb(img, hp, kn, base_up, t=3 if puffer else 2, ox=-1)
            limb(img, kn, an, base_lo, t=2, ox=-1)
        # shoe
        sx, sy = an
        sc = shoe if not shade else shade_of(shoe)
        if S.get("sandal"):
            sc2 = S["sandal"] if not shade else shade_of(S["sandal"])
            put(img, sx - 1, sy, sc2); put(img, sx, sy, sc2); put(img, sx + 1, sy, sc2); put(img, sx + 2, sy, sc2)
            put(img, sx + 1, sy - 1, sc2)
        else:
            for k in range(-1, 3):
                put(img, sx + k, sy, sc)
            put(img, sx + 1, sy - 1, sc); put(img, sx, sy - 1, sc)
            if S.get("sole"):
                pass

    def arm_draw(name, shade):
        s0, el, hd = J[name + "_arm"]
        sl = tb if not shade else ts
        if sleeve == "none":
            sl = skin if not shade else skin_sh
        t = 2 if (puffer) else (2 if not kid else 1 + 1)
        t = 2
        if S.get("arm_thin") or kid:
            t = 1
        # upper arm
        if not shade and sleeve != "none" and not S.get("no_arm_edge"):
            limb(img, s0, el, ts, t=t, ox=1)
            limb(img, el, hd, ts, t=t, ox=1) if sleeve == "long" else None
        limb(img, s0, el, sl, t=t, ox=0 if t == 2 else 0)
        if sleeve == "long":
            limb(img, el, hd, sl, t=t)
            hand_col = skin if not shade else skin_sh
            put(img, R(hd[0]), R(hd[1]), hand_col)
        else:
            limb(img, el, hd, skin if not shade else skin_sh, t=1 if not puffer else 2)
        if puffer:
            put(img, R(hd[0]), R(hd[1]), S.get("glove", skin))

    far_first = True
    leg_draw("far", True)
    if S.get("panel") is None or S.get("legs_over"):
        pass
    arm_draw("far", True)

    # --- torso / lower garment
    tw_f = 2 + (1 if puffer else 0)   # front half-width
    tw_b = 2 + (1 if puffer else 0)
    ytop = sh[1] - 1
    ybot = hip[1] + (1 if not S.get("panel") else 0)
    hxm = hip[0]
    if S.get("woman"):
        quad = [(sh[0] - 1, ytop), (sh[0] + 2, ytop), (hxm + 1, ybot), (hxm - 1, ybot)]
    else:
        quad = [(sh[0] - tw_b, ytop), (sh[0] + tw_f, ytop), (hxm + tw_f, ybot), (hxm - tw_b, ybot)]
    if puffer:
        quad = [(sh[0] - 3, ytop), (sh[0] + 2, ytop), (hxm + 3, ybot + 1), (hxm - 3, ybot + 1)]
    poly(img, quad, tb)
    # shading: back (left) is lit, front-right shaded
    xs = [p[0] for p in quad]
    r_x = max(xs)
    for y in range(ytop, ybot + 1):
        # right column shade
        for x in range(sh[0] + 4, sh[0] - 5, -1):
            if img.getpixel((x, y))[:3] == RGB[tb] and img.getpixel((x, y))[3]:
                put(img, x, y, ts)
                break
    # top-left highlight
    for x in range(sh[0] - 5, sh[0] + 4):
        if img.getpixel((x, ytop))[:3] == RGB[tb] and img.getpixel((x, ytop))[3]:
            put(img, x, ytop, th)
            break
    if puffer:
        for yy in range(ytop + 2, ybot + 1, 3):
            for x in range(sh[0] - 5, sh[0] + 5):
                if img.getpixel((x, yy))[3] and img.getpixel((x, yy))[:3] in (RGB[tb],):
                    put(img, x, yy, ts)
    if S.get("inner"):
        for y in range(ytop + 1, ybot + 1):
            put(img, sh[0] + 1 if y < ybot - 2 else hxm + 1, y, S["inner"])
    if S.get("belt"):
        rect(img, hxm - 2, ybot - 1, hxm + 2, ybot - 1, S["belt"])

    # --- near leg (before panel for long garments)
    leg_draw("near", False)

    # --- panels (ao dai / coat / skirt)
    pn = S.get("panel")
    tb, ts = S.get("panel_cols", (tb, ts))
    if pn:
        flare = pose.get("flare", 0)       # swing of lower hem forward/back
        length = S.get("panel_len", 7)
        y0 = hip[1] - 1
        y1 = J["fy"] - length
        hm = hip[0]
        wback = 2; wfront = 2
        if pn == "coat":
            wback = 2; wfront = 3
        # main body panel (A-line) + trailing back flap
        if pn == "aodai":
            poly(img, [(hm - 1, y0), (hm + 2, y0), (hm + 3 + flare, y1), (hm - 2 + flare, y1)], tb)
            # back flap: trails behind, darker
            tr = pose.get("trail", 1)
            poly(img, [(hm - 2, y0 + 2), (hm - 1, y0 + 2), (hm - 2 + flare - tr, y1), (hm - 5 + flare - tr, y1)], ts)
        else:
            sp = 0 if length >= 8 else 1
            poly(img, [(hm - wback, y0), (hm + wfront, y0), (hm + wfront + flare + sp, y1), (hm - wback + flare - sp, y1)], tb)
            poly(img, [(hm - wback - 1, y0 + 1), (hm - wback + 1, y0 + 1), (hm - wback + flare - sp - pose.get("trail", 1) + 1, y1), (hm - wback + flare - sp - 2 - pose.get("trail", 1), y1)], ts)
        # shade column at front edge
        for y in range(y0, y1 + 1):
            for x in range(hm + 5, hm - 6, -1):
                if img.getpixel((x, y))[3] and img.getpixel((x, y))[:3] == RGB[tb]:
                    put(img, x, y, ts); break
        # hem highlight
        if S.get("hem"):
            for x in range(hm - wback - 3, hm + wfront + 4):
                if img.getpixel((x, y1))[3] and img.getpixel((x, y1))[:3] in (RGB[tb], RGB[ts]):
                    put(img, x, y1, S["hem"])
        if S.get("slit"):
            pass

    tb, ts, th = top
    # --- collar / scarf
    nk = (sh[0], ytop)
    if S.get("scarf"):
        sc = S["scarf"]
        rect(img, sh[0] - 2, ytop - 1, sh[0] + 2, ytop, sc)
        put(img, sh[0] + 2, ytop - 1, shade_of(sc)); put(img, sh[0] + 3, ytop, sc) if not kid else None
        # tail fluttering back
        sw = pose.get("scarf_sw", 0)
        put(img, sh[0] - 3, ytop + 1, shade_of(sc)); put(img, sh[0] - 4 - sw, ytop + 1 + sw, shade_of(sc))
        put(img, sh[0] - 3, ytop, sc)
        put(img, sh[0] - 3, ytop - 1, sc)
    if S.get("collar") and not S.get("scarf"):
        put(img, sh[0] + 1, ytop, S["collar"]); put(img, sh[0], ytop, S["collar"])
    # neck
    rect(img, sh[0], ytop - 1, sh[0] + 1, ytop - 1, skin_sh) if not S.get("scarf") else None

    # --- near arm
    arm_draw("near", False)

    # --- head
    main_img = img
    img = new(W, H)
    hx, hy = J["head"]
    hd = head_img(S.get("hair_style", "short"), skin, hair, hair_hi, kid=kid, mask=S.get("mask", False),
                  glasses=S.get("glasses", False))
    paste(img, hd, hx, hy)
    if S.get("bun"):
        bc = hair
        rect(img, hx - 1, hy - 1 + 1, hx + 1, hy + 1 + 1, bc); put(img, hx - 1, hy, hair_hi)
    if S.get("beanie"):
        bc = S["beanie"]
        w = hd.width
        rect(img, hx - 1, hy, hx + w - 2, hy + 2, bc)
        rect(img, hx - 1, hy + 2, hx + w - 2, hy + 2, shade_of(bc))
        put(img, hx, hy, lighter_of(bc)); put(img, hx + 1, hy, lighter_of(bc))
        put(img, hx + 2, hy - 1, bc); put(img, hx + 3, hy - 1, bc)
        put(img, hx + 2, hy - 2, lighter_of(bc)); 
        put(img, hx + w - 1, hy + 2, bc) if False else None
    if S.get("hat_nonla"):
        hc = S["hat_nonla"]
        cxh = hx + 3
        yb = hy + 2
        poly(img, [(cxh, yb - 4), (cxh - 6, yb), (cxh + 6, yb)], hc)
        line(img, cxh - 6, yb, cxh + 6, yb, shade_of(hc))
        put(img, cxh - 1, yb - 3, lighter_of(hc)); put(img, cxh - 2, yb - 2, lighter_of(hc))
        line(img, cxh + 3, yb + 1, cxh + 2, yb + 4, "red_d") if False else None
        pass

    tilt = pose.get("head_tilt", 0)
    if tilt:
        sheared = new(W, H); sp = img.load(); dp = sheared.load()
        for x in range(W):
            c0 = x - (hx - 1)
            sft = 0 if c0 < 3 else (1 if c0 < 6 else 2)
            sft = min(sft, tilt + 0) if tilt == 1 else sft
            for y in range(H):
                if sp[x, y][3] and 0 <= y - sft:
                    dp[x, y - sft] = sp[x, y]
        img = sheared
    main_img.alpha_composite(img)
    img = main_img
    # --- hand-held / extras (receive img, J, pose)
    for fn in S.get("extras", []):
        fn(img, J, pose)
    return finish(img, W, H)

# ------------------------------------------------------------------ walk pose
def walk_pose(i, D=None, S3=1.0, lift=(0, 0, 0, 1, 2, 1), hips=(11, 11, 12, 11, 11, 12), swing=3.0,
              hand_dy=None, extra=None, lean=0, hipoff=0, fx_scale=1.0):
    D = D or D_ADULT
    xa = [3, 1, -1, -3, -1, 1]
    A = xa[i % 6] * fx_scale; B = xa[(i + 3) % 6] * fx_scale
    LA = lift[i % 6]; LB = lift[(i + 3) % 6]
    hip = hips[i % 6] + hipoff
    hy = hip + D["torso"] - 1 - (D["A1"] + D["A2"]) * 0.88     # relaxed hang
    near_hand = (1 - A * swing / 3 * 0.9, hy + abs(A) * 0.15 + (0.8 if A < 0 else 0))
    far_hand = (1 - B * swing / 3 * 0.9, hy + abs(B) * 0.15 + (0.8 if B < 0 else 0))
    p = dict(hip=hip, near_ankle=(A, 1 + LA), far_ankle=(B, 1 + LB), near_hand=near_hand, far_hand=far_hand,
             lean=lean, flare=0, hair_sw=[0, 1, 1, 0, 1, 1][i % 6], scarf_sw=[0, 1, 0, 0, 1, 0][i % 6],
             trail=[1, 0, 0, 1, 0, 0][i % 6])
    # hem flare: lower hem leans toward forward leg
    p["flare"] = R((A + B) * 0 + (A if A > B else B) * 0.0) + [1, 0, -1, 1, 0, -1][i % 6] * 0
    p["flare"] = {0: 1, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0}[i % 6]
    if extra:
        p.update(extra(i, p))
    return p


def export_lr(group, name, frames, fps, states=None, notes="", anchor=None, **kw):
    fl = [flip(f) for f in frames]
    save_asset(group, name + "_R", frames, fps=fps, states=states, notes=notes, anchor=anchor, **kw)
    ax = anchor
    if anchor:
        ax = (frames[0].width - 1 - anchor[0], anchor[1])
    save_asset(group, name + "_L", fl, fps=fps, states=states, notes=notes + " (flip of _R)", anchor=ax, **kw)
