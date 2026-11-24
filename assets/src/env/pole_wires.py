import sys, pathlib, random, json; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *; from tools.layout import *; from tools.mockbg import mock_scene, place, save_mock

PH = 170
R = random.Random(21)
PERCH = []

def wire_y(x0, y0, x1, y1, sag, x):
    t = (x - x0) / max(1, (x1 - x0))
    return round(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t))

def wire(img, x0, y0, x1, y1, sag, col):
    prev = None
    for x in range(x0, x1 + 1):
        if not (0 <= x < W): continue
        y = wire_y(x0, y0, x1, y1, sag, x)
        if prev is not None and abs(y - prev) > 1:
            step = 1 if y > prev else -1
            mid = x if False else x
            for yy in range(prev + step, y, step): put(img, x - 1 if abs(y - prev) > 1 else x, yy, col)
        put(img, x, y, col)
        prev = y

def pole(img):
    cx, base = POLE_X, POLE_BASE_Y
    top = 28
    for y in range(top, base + 1):
        f = (y - top) / (base - top)
        hw = 3 + round(f * 2)
        x0, x1 = cx - hw, cx + hw - 1
        rect(img, x0, y, x1, y, "stone")
        put(img, x0, y, "stone_l"); 
        put(img, x0 + 1, y, "stone_l") if y % 3 else None
        put(img, x1, y, "stone_d")
        if hw >= 4: put(img, x1 - 1, y, "stone_d") if y % 2 == 0 else None
    # sectional rings + hairline cracks
    for y in range(top + 12, base, 17):
        f = (y - top) / (base - top); hw = 3 + round(f * 2)
        rect(img, cx - hw, y, cx + hw - 1, y, "stone_d")
    for (y, dx) in [(70, 0), (96, 1), (121, -1)]:
        put(img, cx + dx, y, "stone_d"); put(img, cx + dx + 1, y + 1, "stone_d"); put(img, cx + dx + 1, y + 2, "stone_d")
    # rust stain streaks
    for y in range(60, 75): put(img, cx + 1, y, "brown_d") if y % 3 else None
    # footing: little concrete collar
    rect(img, cx - 6, base - 3, cx + 5, base, "stone"); rect(img, cx - 6, base - 3, cx + 5, base - 3, "stone_l"); rect(img, cx + 4, base - 2, cx + 5, base, "stone_d")
    # climbing steps (metal rungs) on the lit side
    for y in range(100, 150, 6): rect(img, cx - 7, y, cx - 5, y, "slate_d")

def crossarm(img, y, half, ins=True, n=3):
    cx = POLE_X
    rect(img, cx - half, y, cx + half, y + 1, "slate_d")
    rect(img, cx - half, y, cx + half, y, "slate")
    # bracket
    line(img, cx - 3, y + 2, cx - 1, y + 4, "slate_d"); line(img, cx + 2, y + 2, cx + 4, y + 4, "slate_d")
    # insulators
    pts = []
    for i in range(n):
        x = cx - half + 2 + i * ((2 * half - 4) // max(1, n - 1))
        rect(img, x, y - 3, x, y - 1, "grey_l"); put(img, x, y - 4, "sand"); put(img, x - 1, y - 2, "grey"); put(img, x + 1, y - 2, "grey")
        pts.append((x, y - 4))
    return pts

def box(img, x, y):
    rect(img, x, y, x + 8, y + 11, "grey"); rect(img, x, y, x + 8, y, "grey_l"); rect(img, x, y, x, y + 11, "grey_l"); rect(img, x + 8, y, x + 8, y + 11, "slate")
    rect(img, x + 1, y + 2, x + 7, y + 10, "slate"); rect(img, x + 2, y + 3, x + 6, y + 9, "grey"); rect(img, x + 2, y + 3, x + 6, y + 3, "grey_l")
    rect(img, x + 4, y + 5, x + 5, y + 6, "navy"); put(img, x + 2, y + 7, "yellow")
    rect(img, x + 3, y + 11, x + 4, y + 18, "slate_d")  # conduit down

def stickers(img):
    cx = POLE_X
    for (y, col, dx, h) in [(88, "white", -1, 6), (97, "yellow", 0, 5), (108, "white", -1, 4), (84, "red_d", 1, 3)]:
        rect(img, cx + dx - 1, y, cx + dx + 1, y + h - 1, col)
        for k in range(1, h - 1, 2): put(img, cx + dx - 1 + (k % 2), y + k, "slate" if col != "red_d" else "yellow")

def coil(img, cx, cy):
    cols = ["ink", "navy", "slate_d", "ink", "navy"]
    for i in range(9):
        rx, ry = 4 + R.randrange(0, 6), 2 + R.randrange(0, 5)
        ox, oy = cx + R.randrange(-4, 5), cy + R.randrange(-3, 4)
        a0 = R.randrange(0, 360)
        ImageDraw.Draw(img).arc([ox - rx, oy - ry, ox + rx, oy + ry], a0, a0 + R.randrange(200, 340), fill=c(cols[i % 5]))
    for i in range(7):
        x, y = cx + R.randrange(-9, 10), cy + R.randrange(-5, 6)
        for _ in range(R.randrange(8, 16)):
            put(img, x, y, cols[i % 5]); x += R.choice([-1, 0, 1, 1]); y += R.choice([-1, 0, 1, 1])

from PIL import ImageDraw

def build():
    img = new(W, PH)
    pole(img)
    from copy import copy
    tmp = new(W, PH)
    a1 = crossarm(tmp, 34, 15, n=4)
    a2 = crossarm(tmp, 47, 11, n=3)
    box(img, POLE_X + 3, 112)
    stickers(img)
    # --- main spans (from pole crossarm insulators out to right edge / facades)
    spans = [
        # x0,y0,x1,y1,sag,col, perch?
        (a1[0][0], a1[0][1], 479, 40, 20, "ink", True),
        (a1[1][0], a1[1][1], 330, 56, 12, "navy", True),
        (a1[2][0], a1[2][1], 209, 66, 9, "ink", True),
        (a1[3][0], a1[3][1], 130, 58, 5, "slate_d", False),
        (a2[0][0], a2[0][1], 250, 74, 10, "slate_d", True),
        (a2[1][0], a2[1][1], 160, 78, 6, "ink", False),
        (a2[2][0], a2[2][1], 300, 79, 12, "navy", False),
        # continuation spans along the street (house to house)
        (209, 66, 330, 54, 8, "ink", True),
        (330, 56, 479, 62, 10, "navy", True),
        (250, 74, 400, 66, 12, "slate_d", True),
        # left side
        (a1[0][0], a1[0][1], 0, 52, 8, "ink", False),
        (a2[0][0], a2[0][1], 0, 66, 6, "navy", False),
        # service drops down to house facades
        (POLE_X + 2, 49, 100, 112, 4, "ink", False),
        (POLE_X + 1, 52, 22, 108, 3, "navy", False),
        (POLE_X + 3, 50, 150, 96, 7, "slate_d", False),
    ]
    for (x0, y0, x1, y1, sag, col, perch) in spans:
        wire(img, x0, y0, x1, y1, sag, col)
    # parallel bundle strands near the pole
    for dy, col in [(1, "navy"), (2, "slate_d")]:
        wire(img, a1[0][0] + 2, a1[0][1] + dy, 120, 48 + dy, 6, col)
    img.alpha_composite(tmp)
    # twisted coil near the pole (messy slack loops)
    coil(img, POLE_X + 17, 68)
    coil(img, POLE_X + 36, 54)
    # bird perch points: on wires (feet y = wire y - 1)
    cand = [(220, 0), (250, 4), (310, 5), (360, 6), (400, 7), (440, 8), (140, 9), (88, 10)]
    for (px_, k) in cand:
        # choose the span covering px_ most "top-most" (smallest y) among main spans
        ys = []
        for (x0, y0, x1, y1, sag, col, perch) in spans:
            if perch and x0 <= px_ <= x1: ys.append(wire_y(x0, y0, x1, y1, sag, px_))
        if ys: PERCH.append((px_, min(ys) - 1))
    return img

if __name__ == "__main__":
    img = build()
    perch = ", ".join(f"({x},{y})" for x, y in PERCH)
    save_asset("env", "pole_wires", img, anchor=(0, 0), notes=f"480x170 at (0,0). Pole base at (52,165). Bird perch points (feet): {perch}")
    print(PERCH)
    bg = mock_scene(); bg.alpha_composite(img, (0, 0)); save_mock(bg, "env", "pole_check")
