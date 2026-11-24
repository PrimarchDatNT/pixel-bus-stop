"""Hanoi city bus, bản 6c (24/11/2026): redrawn in the chunky "toy bus" style of the client's itch.io reference —
short tall body, a front face turned toward us (3/4 cab), one long glass band with bold white diagonal glare stripes,
the interior visible (hand rail + hanging grips, seat backs, passengers), big wheels with a red hub dot, orange
chevron headlights, a mirror on a stalk. Colours stay Hanoi: yellow body, red band + skirt. No text, no route number
(the destination box only shows blank LED dashes). Old v5 bus: scratchpad/bus_v5.py.

Front = LEFT edge (drives right -> left). Frames: 0-2 driving (wheel spin), 3 idling (body dips 1 px).
Also exports actors/bus_puff (exhaust, 4 frames).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
from tools.px_gif import *  # noqa: E402,F403

BW, BH = 148, 58
WR = 9
WHEELS = (40, 117)            # wheel centre x
WY = BH - 1 - WR              # wheel centre y (tyre bottom = anchor row)
FX1 = 32                      # front panel x 3..FX1, side FX1+1..BW-3
WIN_Y0, WIN_Y1 = 12, 31       # side glass band


def body(dy=0):
    im = new(BW, BH)
    Y = lambda v: v + dy                                       # noqa: E731
    # ---------------------------------------------------------------- silhouette: tall cab, roof steps down to the rear
    for x in range(3, BW - 2):
        if x <= FX1 + 2:
            top = 1
        elif x <= FX1 + 8:
            top = 1 + (x - FX1 - 2)
        else:
            top = 7
        rect(im, x, Y(top), x, Y(48), "yl")
        put(im, x, Y(top), "yl_l"); put(im, x, Y(top + 1), "yl_l")
    im.putpixel((3, Y(1)), (0, 0, 0, 0)); im.putpixel((BW - 3, Y(7)), (0, 0, 0, 0))   # rounded corners
    rect(im, BW - 4, Y(8), BW - 3, Y(48), "yl_d")                          # rear edge shade
    # ---------------------------------------------------------------- front panel (lit face, turned toward us)
    rect(im, 3, Y(3), FX1, Y(48), "yl_l")
    rect(im, FX1 + 1, Y(2), FX1 + 1, Y(48), "yl_d")                       # cab corner
    # destination box: dark, blank LED dashes (no text)
    rect(im, 6, Y(4), FX1 - 2, Y(9), "ink"); rect(im, 6, Y(4), FX1 - 2, Y(4), "grey_k")
    for x0, n in ((8, 4), (13, 2), (17, 5), (24, 2)):
        rect(im, x0, Y(7), x0 + n - 1, Y(7), "or_l")
    put(im, 8, Y(6), "or"); put(im, 18, Y(6), "or")
    # windscreen: dark cab, driver, steering wheel, one bold glare stripe
    wx0, wx1, wy0, wy1 = 5, FX1 - 1, 12, 32
    rect(im, wx0, Y(wy0), wx1, Y(wy1), "grey_k")
    rect(im, wx0 + 1, Y(wy0 + 1), wx1 - 1, Y(wy1 - 1), "glass_d")
    rect(im, wx0 + 1, Y(wy0 + 1), wx1 - 1, Y(wy0 + 2), "glass")
    ellipse(im, 16, Y(19), 22, Y(25), "hair"); rect(im, 17, Y(23), 21, Y(25), "sk")      # driver
    rect(im, 14, Y(26), 24, Y(wy1 - 1), "wb"); rect(im, 22, Y(26), 24, Y(wy1 - 1), "wb_d")
    rect(im, 7, Y(27), 13, Y(27), "ink"); put(im, 6, Y(28), "ink"); put(im, 14, Y(28), "ink")   # steering wheel
    for i in range(16):                                                    # glare stripe
        x = wx0 + 3 + i; y = wy1 - 2 - i
        if wx0 < x < wx1 and wy0 < y < wy1:
            put(im, x, Y(y), "white"); put(im, x + 1, Y(y), "white")
            if x + 2 < wx1: put(im, x + 2, Y(y), "glass_l")
    rect(im, wx0 + 2, Y(wy1), wx0 + 9, Y(wy1), "ink")                      # wiper
    # lower front: chevron headlights, grille, bumper
    for side in (1, -1):                                                   # double orange chevrons (like the ref)
        bx = 5 if side == 1 else FX1 - 1
        for j, (dy, dx) in enumerate(((0, 0), (1, 1), (2, 2), (3, 1), (4, 0))):
            for off, col in ((0, "lamp"), (3, "or_l")):
                put(im, bx + side * (dx + off), Y(35 + dy), col); put(im, bx + side * (dx + off + 1), Y(35 + dy), col)
        put(im, bx, Y(35), "glow")
    for y in (40, 42):
        rect(im, 12, Y(y), FX1 - 9, Y(y), "yl_d")
    rect(im, 2, Y(44), FX1 + 1, Y(48), "grey_l"); rect(im, 2, Y(44), FX1 + 1, Y(44), "grey_hl")
    rect(im, 2, Y(48), FX1 + 1, Y(48), "grey")
    # mirror on a stalk, sticking out in front of the cab
    rect(im, 0, Y(13), 3, Y(13), "grey_k")
    rect(im, 0, Y(14), 1, Y(20), "ink"); put(im, 0, Y(14), "grey_k")
    # ---------------------------------------------------------------- side glass band with the interior
    x0, x1 = FX1 + 4, BW - 8
    rect(im, x0, Y(WIN_Y0), x1, Y(WIN_Y1), "glass")
    rect(im, x0, Y(WIN_Y0), x1, Y(WIN_Y0 + 1), "glass_d")                 # shade under the roof
    rect(im, x0, Y(WIN_Y0 + 3), x1, Y(WIN_Y0 + 3), "grey_l")              # hand rail
    for gx in range(x0 + 5, x1 - 2, 9):                                    # hanging grips
        put(im, gx, Y(WIN_Y0 + 4), "grey_d"); rect(im, gx - 1, Y(WIN_Y0 + 5), gx + 1, Y(WIN_Y0 + 6), "ink")
        put(im, gx, Y(WIN_Y0 + 6), "glass")
    # seat backs + passengers (backs of heads / shoulders)
    for sx in range(x0 + 2, x1 - 6, 15):
        rect(im, sx, Y(WIN_Y1 - 5), sx + 7, Y(WIN_Y1), "pb_d"); rect(im, sx, Y(WIN_Y1 - 5), sx + 7, Y(WIN_Y1 - 5), "pb")
    for px_, hair, shirt in ((x0 + 5, "hair", "wp"), (x0 + 21, "grey_l", "wb"), (x0 + 35, "hair_l", "sh_l"),
                             (x0 + 57, "hair", "red_l"), (x0 + 77, "hair", "yl_l"), (x0 + 90, "hair_l", "wc")):
        if px_ + 8 < x1:
            ellipse(im, px_, Y(WIN_Y1 - 12), px_ + 6, Y(WIN_Y1 - 6), hair)
            rect(im, px_ - 1, Y(WIN_Y1 - 5), px_ + 7, Y(WIN_Y1), shirt)
            put(im, px_ + 1, Y(WIN_Y1 - 11), "hair_l" if hair == "hair" else "grey_hl")
    # bold diagonal glare stripes (white core + light fringe), like the reference
    for sx, w in ((x0 + 4, 5), (x0 + 14, 2), (x0 + 50, 6), (x0 + 62, 2), (x0 + 88, 4)):
        for y in range(WIN_Y0 + 2, WIN_Y1 + 1):
            xs = sx + (WIN_Y1 - y)
            for k in range(w):
                if x0 <= xs + k <= x1:
                    put(im, xs + k, Y(y), "white")
            if x0 <= xs + w <= x1:
                put(im, xs + w, Y(y), "glass_l")
    for px_ in (x0 + 27, x0 + 54, x0 + 81):                                # thin window pillars
        rect(im, px_, Y(WIN_Y0), px_ + 1, Y(WIN_Y1), "yl"); rect(im, px_ + 1, Y(WIN_Y0), px_ + 1, Y(WIN_Y1), "yl_d")
    rect(im, x0, Y(WIN_Y1 + 1), x1, Y(WIN_Y1 + 1), "yl_d")                # sill shadow
    rect(im, x1 + 1, Y(WIN_Y0), x1 + 1, Y(WIN_Y1), "yl_d")
    # ---------------------------------------------------------------- belt + red band + skirt
    rect(im, FX1 + 2, Y(34), BW - 5, Y(34), "white")
    rect(im, FX1 + 2, Y(35), BW - 5, Y(37), "red"); rect(im, FX1 + 2, Y(37), BW - 5, Y(37), "red_d")
    rect(im, FX1 + 2, Y(44), BW - 3, Y(47), "red"); rect(im, FX1 + 2, Y(44), BW - 3, Y(44), "red_l")
    rect(im, 3, Y(48), BW - 3, Y(48), "red_d")
    rect(im, BW - 4, Y(35), BW - 3, Y(41), "red_l"); put(im, BW - 3, Y(41), "red_d")   # tail light
    rect(im, 76, Y(39), 81, Y(41), "yl_d"); rect(im, 77, Y(40), 80, Y(40), "yl")         # fuel flap
    # wheel arches (dark) — wheels are a separate layer so the body can dip over them
    for cx in WHEELS:
        ellipse(im, cx - WR - 2, WY - WR - 2, cx + WR + 2, WY + WR + 2, "ink")
    _clear_below(im, Y(49))
    return im


def _clear_below(im, y):
    px = im.load()
    for yy in range(y, im.height):
        for xx in range(im.width):
            px[xx, yy] = (0, 0, 0, 0)


# ------------------------------------------------------------------------------------------- easter egg: iKame bus
# The client works as an Android dev at iKame. Once per 2-minute summer clip a different bus pulls in: cream body with
# an orange -> yellow stripe in the mascot's colours, the rear window wrapped like an ad with the iKame mascot (round
# orange-yellow comet with a white visor face and closed happy eyes ^^, facing the front of the bus, tail streaming
# back), route "35" (API 35) on the destination board, and the Android robot riding inside, waving while the bus idles.
# No text / wordmark (client's choice: mascot only). The Android robot is used under CC BY 3.0 (credit in README).
IKAME_RECOLOR = {"yl_l": "white", "yl": "wc_l", "yl_d": "wc", "red": "or", "red_l": "or_l", "red_d": "or_d"}
DIGITS = {"3": ["xxx", "..x", "xxx", "..x", "xxx"], "5": ["xxx", "x..", "xxx", "..x", "xxx"]}
MASCOT = [                      # 17 x 14, faces LEFT; Y yl_l, y yl, o or_l, O or, D or_d, W white, w grey_hl, k ink
    ".....YYYYY.......",
    "...YYYYYYYYY.YY..",
    "..YYYyyyyyyYYYYYY",
    ".yyWWWWWWWyyyyyy.",
    ".yWWkWWWkWWWyyyyy",
    "yyWkWkWkWkWWyoooo",
    "yoWWWWWWWWWWoooo.",
    "ooWWWWWWWWWwooO..",
    "oooWwwwwwwwoooOO.",
    "OoooooooooooOOO..",
    ".OOoooooooOOOO...",
    "..OOOOOOOOOOD....",
    "....DOOOODD......",
    ".................",
]
MASCOT_COL = {"Y": "yl_l", "y": "yl", "o": "or_l", "O": "or", "D": "or_d", "W": "white", "w": "grey_hl", "k": "ink"}
DROID_HEAD = ["k.....k",    # antennae
              ".k...k.",
              "..ggg..",
              ".ggggg.",
              "gwgggwg",
              "ggggggd"]
DROID_COL = {"g": "droid", "d": "droid_d", "w": "white", "k": "droid_d"}


def ikame_body(dy=0, wave=False):
    im = body(dy)
    # NB: inside body() the headlight loop re-binds `dy` (for j, (dy, dx) ...), so everything body() draws after the
    # headlights sits 4 px lower than its coordinates say. That is the approved look of bus 32, so the overlays
    # below follow the same offset: Yf for the destination board (drawn before the loop), Y for the side.
    Yf = lambda v: v + dy                                      # noqa: E731
    Y = lambda v: v + 4                                        # noqa: E731
    px = im.load()
    rgb = {RGB[a]: RGB[b] for a, b in IKAME_RECOLOR.items()}
    for yy in range(im.height):                                # Hanoi yellow / red -> cream / orange
        for xx in range(im.width):
            c = px[xx, yy]
            if c[3] and c[:3] in rgb:
                px[xx, yy] = rgb[c[:3]] + (255,)
    # a yellow stripe under the orange band: the mascot's orange -> yellow
    rect(im, FX1 + 2, Y(38), BW - 5, Y(38), "yl"); rect(im, FX1 + 2, Y(39), BW - 5, Y(39), "yl_l")
    # destination board: route 35
    rect(im, 6, Yf(5), FX1 - 2, Yf(9), "ink")
    for i, ch in enumerate("35"):
        for r, row in enumerate(DIGITS[ch]):
            for c, v in enumerate(row):
                if v == "x":
                    put(im, 14 + i * 5 + c, Yf(5 + r), "or_l")
    # rear window wrapped like an ad, mascot on it
    x0, x1 = FX1 + 4, BW - 8
    rect(im, x0 + 83, Y(WIN_Y0), x1, Y(WIN_Y1), "wc_l")
    rect(im, x0 + 83, Y(WIN_Y1), x1, Y(WIN_Y1), "wc")
    for r, row in enumerate(MASCOT):
        for c, v in enumerate(row):
            if v != ".":
                put(im, x0 + 85 + c, Y(WIN_Y0 + 3 + r), MASCOT_COL[v])
    # the Android robot in the middle window, waving while the bus idles
    gx = x0 + 57
    rect(im, gx - 1, Y(WIN_Y1 - 12), gx + 7, Y(WIN_Y1), "glass")            # clear the passenger who sat here
    rect(im, gx - 2, Y(WIN_Y1 - 5), gx + 9, Y(WIN_Y1), "pb_d"); rect(im, gx - 2, Y(WIN_Y1 - 5), gx + 9, Y(WIN_Y1 - 5), "pb")
    for r, row in enumerate(DROID_HEAD):
        for c, v in enumerate(row):
            if v != ".":
                put(im, gx + c, Y(WIN_Y0 + 6 + r), DROID_COL[v])
    top = WIN_Y0 + 6 + len(DROID_HEAD) + 1                     # 1 px gap between head and body, like the logo
    rect(im, gx, Y(top), gx + 6, Y(WIN_Y1), "droid"); rect(im, gx + 6, Y(top), gx + 6, Y(WIN_Y1), "droid_d")
    rect(im, gx + 8, Y(top), gx + 9, Y(top + 4), "droid_d")                    # far arm, resting
    if wave:
        rect(im, gx - 3, Y(WIN_Y0 + 5), gx - 2, Y(top - 1), "droid")          # near arm up, waving
        put(im, gx - 3, Y(WIN_Y0 + 4), "droid")
    else:
        rect(im, gx - 3, Y(top), gx - 2, Y(top + 4), "droid")
    return im


BOLTS = [[(0, -3), (3, 0), (0, 3), (-3, 0)], [(2, -2), (2, 2), (-2, 2), (-2, -2)], [(-1, -3), (3, -1), (1, 3), (-3, 1)]]


def wheels(phase):
    im = new(BW, BH)
    for cx in WHEELS:
        ellipse(im, cx - WR, WY - WR, cx + WR, WY + WR, "ink")
        ellipse(im, cx - WR + 1, WY - WR + 1, cx + WR - 1, WY + WR - 1, "grey_k")
        ellipse(im, cx - 5, WY - 5, cx + 5, WY + 5, "grey_d")
        ellipse(im, cx - 4, WY - 4, cx + 4, WY + 4, "grey_l")
        rect(im, cx - 3, WY - 4, cx, WY - 4, "grey_hl"); put(im, cx - 4, WY - 2, "grey_hl")
        for dx, dy in BOLTS[phase]:
            put(im, cx + dx, WY + dy, "grey")
        rect(im, cx - 1, WY - 1, cx, WY, "red_l")                          # red hub dot
    return im


def build():
    frames = []
    for i in range(3):
        f = body(0); f.alpha_composite(wheels(i)); frames.append(f)       # wheels sit in front of the dark arches
    f = body(1); f.alpha_composite(wheels(0)); frames.append(f)        # idling dip
    puffs = []
    for k in range(4):
        p = new(8, 7)
        r = 1 + k // 2
        ellipse(p, 3 - r, 3 - r, 3 + r, 3 + r, "cloud_d" if k < 3 else "cloud_s")
        if k < 2:
            put(p, 3 - r, 3 - r, "cloud_s")
        puffs.append(p)
    return frames, puffs


if __name__ == "__main__":
    frames, puffs = build()
    save_asset("actors", "bus32", frames, fps=12, anchor=(0, BH - 1), states={"drive": [0, 1, 2], "idle": [0, 0, 3, 3]},
               notes="bản 6c toy-bus style; front = left edge; anchor = front-bottom (tyre contact row). drive right->left")
    save_asset("actors", "bus_puff", puffs, fps=6, anchor=(3, 3), notes="exhaust puff, grows + fades")
    ik = []
    for i in range(3):
        f = ikame_body(0); f.alpha_composite(wheels(i)); ik.append(f)
    f = ikame_body(1, wave=True); f.alpha_composite(wheels(0)); ik.append(f)    # idle frame: dips + waves
    save_asset("actors", "bus_ikame", ik, fps=12, anchor=(0, BH - 1), states={"drive": [0, 1, 2], "idle": [0, 0, 3, 3]},
               notes="easter egg: iKame bus (mascot only, route 35, Android robot waving); same geometry as bus32")
    frames = [ik[0], ik[3]] + frames
    from PIL import Image
    k = 5; bg = (169, 159, 146)
    S = Image.new("RGB", (BW * k, BH * k * 4 + 30), bg)
    for i, f in enumerate((frames[0], frames[1], frames[2], frames[5])):
        b = Image.new("RGBA", f.size, bg + (255,)); b.alpha_composite(f)
        S.paste(b.convert("RGB").resize((BW * k, BH * k), Image.NEAREST), (0, i * (BH * k + 10)))
    S.save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/bus.png")
    print("ok")
