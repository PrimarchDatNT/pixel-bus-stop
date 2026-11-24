"""Procedural-assisted cat: spline torso + ASCII heads + IK legs + spline tail. 48x30 frames, faces RIGHT."""
from lib import *
from PIL import ImageDraw

CTX = {}
CW, CH = 48, 31          # canvas (outline adds 1px; final frame 48x30, feet row = 29)
FEET = CH - 2            # 29

LEG = {"O": "orange", "G": "gold", "Y": "yellow", "R": "rust", "D": "brown_d", "W": "white", "w": "grey_l",
       "N": "salmon", "I": "salmon", "E": "green_l", "P": "ink", "C": "clay", "K": "brown_k", "L": "white"}

# ---------------------------------------------------------------- heads (facing right, side/3-4 view)
HEAD_SIDE = [
    "..RR....RR...",
    "..RIR..RIIR..",
    "..ROORROOOR..",
    ".RGGOOOOOOOOR",
    ".RGOODOODOOOO",
    "ROOODOOOOOOOO",
    "ROOOOOOELLOOO",
    "ROOOOOOEPLOWW",
    ".ROOOOOOOOWWN",
    "..COOOOOWWWWW",
    "...CCOOWWWWW.",
    ".....CCWWWW..",
]
HEAD_SIDE_BLINK = [r for r in HEAD_SIDE]
HEAD_SIDE_BLINK[6] = "ROOOOOOODDOOO"
HEAD_SIDE_BLINK[7] = "ROOOOOOOOOOWW"
HEAD_FRONT = [
    ".RR........RR.",
    ".RIR......RIR.",
    ".RIIORRRROIIR.",
    ".ROOOODDOOOOR.",
    ".GOODOOOODOOO.",
    "ROOOOOOOOOOOOR",
    "ROELOOOOOOELOR",
    "ROEPOOOOOOEPOR",
    ".OOOOWWWWOOOO.",
    ".COOWWNNWWOOC.",
    "..COWWWWWWOC..",
    "...CCWWWWCC...",
]
HEAD_FRONT_BLINK = list(HEAD_FRONT)
HEAD_FRONT_BLINK[6] = "ROOOOOOOOOOOOR"
HEAD_FRONT_BLINK[7] = "RDDDOOOOOODDDR"
HEAD_FRONT_HALF = list(HEAD_FRONT)
HEAD_FRONT_HALF[6] = "RDDDOOOOOODDDR"
HEAD_FRONT_HALF[7] = "ROEPOOOOOOEPOR"


def hgrid(rows, flipx=False):
    w = max(len(r) for r in rows)
    rows = [r.ljust(w, ".") for r in rows]
    g = grid(rows, LEG)
    return g


def catmull(pts, n=6, closed=True):
    out = []
    N = len(pts)
    for i in range(N if closed else N - 1):
        p0 = pts[(i - 1) % N] if closed or i > 0 else pts[0]
        p1 = pts[i % N]
        p2 = pts[(i + 1) % N]
        p3 = pts[(i + 2) % N] if closed or i + 2 < N else pts[-1]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(pts[-1])
    return out


def draw_torso(img, pts, stripes_x=(), bib=None, light_to=0.65, stripe_len=4, belly_white=None):
    """pts: closed control polygon. Fills + shades the torso (light upper-left, shadow below, tabby stripes)."""
    poly_pts = [(R(x), R(y)) for x, y in catmull(pts, 8)]
    lay = new(img.width, img.height)
    ImageDraw.Draw(lay).polygon(poly_pts, fill=c("orange"))
    px = lay.load()
    xs = [p[0] for p in poly_pts]
    x0, x1 = min(xs), max(xs)
    CTX['tail_after'] = False
    CTX['torso'] = (x0, x1, {x: min([y for y in range(lay.height) if px[x, y][3]] or [99]) for x in range(x0, x1 + 1)})
    for x in range(x0, x1 + 1):
        ys = [y for y in range(lay.height) if px[x, y][3]]
        if not ys:
            continue
        t, b = min(ys), max(ys)
        fr = (x - x0) / max(1, x1 - x0)
        # top highlight band (left lit)
        if fr < light_to:
            px[x, t] = c("gold")
            if fr < light_to * 0.5 and t + 1 <= b:
                px[x, t + 1] = c("gold")
        # underside shade
        px[x, b] = c("rust")
        if b - 1 > t:
            px[x, b - 1] = c("clay")
    # tabby stripes (diagonal, from the back edge down)
    for sx in stripes_x:
        ys = [y for y in range(lay.height) if 0 <= sx < lay.width and px[sx, y][3]]
        if not ys:
            continue
        t = min(ys)
        for k in range(stripe_len):
            xx = sx + (k // 2) * -1 * 0
            yy = t + 1 + k
            xx2 = sx - (1 if k >= 2 else 0)
            for dx in ((0, 1) if k < stripe_len - 1 else (0,)):
                X = xx2 + dx
                if 0 <= X < lay.width and px[X, yy][3] and px[X, yy][:3] in (RGB["orange"], RGB["gold"]):
                    px[X, yy] = c("rust")
    if belly_white:
        bx0, by0, bx1, by1 = belly_white
        for y in range(by0, by1 + 1):
            for x in range(bx0, bx1 + 1):
                if px[x, y][3]:
                    # elliptical white bib
                    ex = (x - (bx0 + bx1) / 2) / ((bx1 - bx0) / 2 + 0.5)
                    ey = (y - (by0 + by1) / 2) / ((by1 - by0) / 2 + 0.5)
                    if ex * ex + ey * ey <= 1:
                        px[x, y] = c("white") if (x + y) % 5 or True else c("grey_l")
                        if ey > 0.4:
                            px[x, y] = c("grey_l")
    img.alpha_composite(lay)
    return poly_pts


def draw_tail(img, ctrl, width=2, ring=3, tip="brown_d", base="orange", sway_pts=None):
    pts = catmull(ctrl, 8, closed=False)
    # dedupe pixel path
    path = []
    for x, y in pts:
        p = (R(x), R(y))
        if not path or path[-1] != p:
            path.append(p)
    n = len(path)
    for i, (x, y) in enumerate(path):
        col = base
        if (i // ring) % 2 == 1 and i < n - 3:
            col = "rust"
        if i >= n - 3:
            col = tip
        # width via perpendicular pixel (use 2 px: x and x+1 / y and y+1 depending on slope)
        if i + 1 < n:
            dx, dy = path[i + 1][0] - x, path[i + 1][1] - y
        else:
            dx, dy = x - path[i - 1][0], y - path[i - 1][1]
        put(img, x, y, col)
        if width >= 2 and i < n - 1:
            if abs(dy) >= abs(dx):
                put(img, x + 1, y, col if col != "orange" else "gold" if False else col)
            else:
                put(img, x, y + 1, col)
    # highlight along the top-left of the tail (light upper-left)
    CTX['tail'] = list(path)
    return path


def draw_leg3(img, hip, knee, foot, col_hi, col, col_sh, paw=True, w=2, white_len=3, paw_dx=1, side="near"):
    """upper leg hip->knee in fur colors, lower knee->foot ending in a white paw"""
    limb(img, hip, knee, col, t=w, ox=-0)
    limb(img, knee, foot, col, t=w)
    fx, fy = R(foot[0]), R(foot[1])
    # white sock: last white_len px of lower leg
    for k, (x, y) in enumerate(bres(knee[0], knee[1], foot[0], foot[1])[::-1]):
        if k < white_len:
            for dx in range(w):
                put(img, x + dx, y, "white" if side == "near" else "grey_l")
    # paw
    pc = "white" if side == "near" else "grey_l"
    put(img, fx - 1 + 0, fy, pc); put(img, fx, fy, pc); put(img, fx + 1, fy, pc)
    if paw_dx:
        put(img, fx + 2, fy, pc)
    put(img, fx + 1, fy, pc)


def cat_finish(img):
    o = outline(img, "brown_k")
    return o.crop((1, 1, CW + 1, CH))
