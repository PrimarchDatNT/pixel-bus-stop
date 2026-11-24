"""Tết (spring) props, hand-pixelled in the GIF style (no outlines on figures, flat 2-3 tones, light from upper-left).

    .venv/bin/python assets/src_gif/season/tet.py [sheet.png]   # -> assets/out_gif/actors/ + preview sheet

lantern_red (sway), flag_vn (waving, on a slanted pole), kumquat (cây quất with lì xì), banner_tet
("CHÚC MỪNG NĂM MỚI" cloth for the balcony railing), moto_dao (rider on a Cub carrying a peach tree, faces left,
wheels spin), swallow (chim én, 4 flap frames), petal_peach (pink peach petals).
"""
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
from tools.px_gif import *  # noqa: E402,F403


def G(rows, legend):
    w = max(len(r) for r in rows)
    return grid([r.ljust(w, ".") for r in rows], legend)


def blobs(cells):
    S = set()
    for cx, cy, rx, ry in cells:
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / (rx + .5)) ** 2 + ((y - cy) / (ry + .5)) ** 2 <= 1.0:
                    S.add((x, y))
    return S


def shade_mass(im, S, hl, base, sh, dk=None):
    """Clump shading: top/left edge highlight, bottom/right edge shade, outer bottom-right rim darkest."""
    for x, y in S:
        col = base
        if (x, y - 1) not in S or (x - 1, y) not in S and (x, y - 2) not in S:
            col = hl
        if (x + 1, y) not in S or (x, y + 1) not in S:
            col = sh
        if dk and (x + 1, y + 1) not in S and (x, y + 1) not in S:
            col = dk
        put(im, x, y, col)


# ------------------------------------------------------------------ red lantern (đèn lồng), hangs from its top pixel
LANT = {"k": "wood_d", "Y": "gold", "y": "or", "L": "red_l", "R": "red", "D": "red_d"}
_lant_body = [
    "..yYY..",
    "LLRRRRD",
    "LRRRRRD",
    "LRRRRDD",
    "RRRRRDD",
    ".RRRDD.",
    "..yYY..",
    "...Y...",
    "..YyY..",
    "..Y.y..",
]


def lantern_frames():
    out = []
    for dx in (0, 1, 0, -1):
        im = new(9, 13)
        put(im, 4, 0, "wood_d"); put(im, 4, 1, "wood_d"); put(im, 4 + (dx if dx else 0) // 1, 2, "wood_d")
        body = G(_lant_body, LANT)
        im.alpha_composite(body, (1 + dx, 3))
        out.append(im)
    return out


# ------------------------------------------------------------------ Vietnamese flag on a slanted pole (bracket at bottom-left)
def flag_frames():
    out = []
    FW, FH = 17, 11
    for f in range(4):
        im = new(28, 22)
        line(im, 0, 21, 9, 0, "grey_l"); line(im, 1, 21, 10, 0, "grey")        # pole, 2 px
        put(im, 9, 0, "gold"); put(im, 10, 0, "gold")
        star = ["..Y..", "YYYYY", ".YYY.", ".Y.Y."]
        for cx in range(FW):
            px = 10 - 0 + cx + 1
            amp = 1.8 * (cx / FW)
            dy = round(amp * math.sin(cx * 0.55 - f * math.pi / 2))
            slope = math.cos(cx * 0.55 - f * math.pi / 2)
            col = "red_l" if slope > 0.8 else ("red_d" if slope < -0.8 else "red")
            for ry in range(FH):
                y = 1 + ry + dy
                put(im, px, y, col)
            # star stamped with the same offset
            sx = cx - 6
            if 0 <= sx < 5:
                for sy, row in enumerate(star):
                    if row[sx] == "Y":
                        put(im, px, 1 + 3 + sy + dy, "gold")
        out.append(im)
    return out


# ------------------------------------------------------------------ kumquat tree in a glazed pot (cây quất)
def kumquat():
    im = new(21, 30)
    crown = blobs([(10, 9, 8, 7), (5, 11, 4, 4), (15, 11, 4, 4), (10, 4, 5, 3), (7, 14, 4, 3), (13, 14, 4, 3)])
    shade_mass(im, crown, "leaf_l", "leaf", "leaf_d", "leaf_k")
    for x, y in [(6, 6), (12, 5), (9, 9), (14, 8), (4, 11), (17, 12), (8, 13), (12, 13), (15, 15), (5, 15), (10, 3), (11, 17)]:
        put(im, x, y, "or_l"); put(im, x + 1, y, "or"); put(im, x, y + 1, "or"); put(im, x + 1, y + 1, "or_d")
    for x, y in [(3, 8), (16, 6), (10, 15)]:                    # lì xì envelopes
        rect(im, x, y, x + 1, y + 2, "red"); put(im, x, y + 1, "gold"); put(im, x + 1, y + 2, "red_d")
    rect(im, 9, 19, 11, 21, "trunk"); put(im, 11, 20, "trunk_d")
    # pot: glazed blue-white with a lip
    rect(im, 4, 21, 16, 22, "pb_l"); rect(im, 4, 22, 16, 22, "pb")
    rect(im, 5, 23, 15, 28, "white"); rect(im, 14, 23, 15, 28, "grey_hl")
    rect(im, 5, 25, 15, 26, "pb"); rect(im, 14, 25, 15, 26, "pb_d")
    rect(im, 6, 29, 14, 29, "pb_d")
    return im


# ------------------------------------------------------------------ banner on the balcony railing
def banner():
    msg = "CHÚC MỪNG NĂM MỚI"
    tw, _ = text_size(msg)
    w = tw + 8
    im = new(w, 13)
    rect(im, 0, 1, w - 1, 12, "red"); rect(im, 0, 1, w - 1, 1, "red_l"); rect(im, 0, 12, w - 1, 12, "red_d")
    for x in range(0, w, 6):                                     # cloth sags between ties
        put(im, x, 12, "red_d")
    put(im, 0, 0, "gold"); put(im, w - 1, 0, "gold")
    text(im, 4, 5, msg, "gold")
    return im


# ------------------------------------------------------------------ motorbike carrying a peach tree, faces LEFT
RIDER = {"R": "red", "r": "red_d", "L": "red_l", "H": "hair", "S": "sk_l", "s": "sk", "E": "hair",
         "J": "sb", "j": "sb_d", "P": "wood_d", "p": "wood_k", "K": "ink", "W": "white"}
_rider = [                     # faces left, seated
    "......RRRRR.....",
    "....LLRRRRRr....",
    "...LRRRRRRRRr...",
    "..rrRRRRRRRRr...",
    "....SSSSHHHHH...",
    "....ESSSHHHHH...",
    "....SSSSSHHH....",
    ".....sSSSHH.....",
    "......sSs.......",
    ".....JJJJJJ.....",
    "....JJJJJJJJ....",
    "..JJJjJJJJJJj...",
    ".SJJjjJJJJJJj...",
    "SS..jJJJJJJJj...",
    ".....JJJJJJJj...",
    "...PPPPPPPPPP...",
    "..PPPPPPPPPPPp..",
    "..PPp...........",
    "..PPp...........",
    "..PPp...........",
    "..PPp...........",
    ".KKKK...........",
]


def bike(phase):
    """34x20, faces left. Front wheel centre (5,14), rear (28,14), r=5."""
    im = new(34, 20)
    for cx in (5, 28):
        ellipse(im, cx - 5, 9, cx + 5, 19, "grey_k")
        ellipse(im, cx - 3, 11, cx + 3, 17, "grey_l")
        put(im, cx, 14, "grey_d")
        for dx, dy in [[(0, -2), (2, 1), (-2, 1)], [(2, -1), (0, 2), (-2, -1)], [(-2, -1), (2, -1), (0, 2)]][phase]:
            put(im, cx + dx, 14 + dy, "grey")
    # rear body + fender over the rear wheel
    poly(im, [(18, 5), (31, 5), (33, 8), (33, 9), (22, 9), (19, 8)], "teal")
    rect(im, 19, 5, 31, 5, "glass_l")
    rect(im, 22, 9, 33, 9, "teal_d")
    put(im, 33, 6, "red_l"); put(im, 33, 7, "red")                          # tail light
    rect(im, 25, 3, 33, 3, "grey_d"); rect(im, 26, 4, 26, 4, "grey_d"); rect(im, 32, 4, 32, 4, "grey_d")   # rack
    # seat
    rect(im, 15, 3, 25, 4, "grey_k"); rect(im, 16, 3, 24, 3, "grey_m")
    # engine + underbone
    rect(im, 13, 10, 21, 15, "grey_m"); rect(im, 13, 10, 21, 10, "grey_l"); rect(im, 13, 15, 21, 15, "grey_d")
    ellipse(im, 15, 11, 18, 14, "grey_l"); put(im, 16, 12, "grey_d"); put(im, 17, 13, "grey_d")
    rect(im, 12, 9, 21, 9, "teal_d")                                         # footboard
    rect(im, 22, 15, 31, 16, "grey"); rect(im, 22, 15, 31, 15, "grey_l")     # muffler
    # leg shield
    poly(im, [(10, 2), (13, 2), (14, 10), (10, 10)], "teal")
    rect(im, 13, 3, 13, 9, "teal_d"); rect(im, 10, 3, 10, 9, "glass_l")
    # fork + front fender
    for i in range(10):
        put(im, 10 - i // 2, 4 + i, "grey_m"); put(im, 11 - i // 2, 4 + i, "grey_d")
    poly(im, [(1, 9), (3, 7), (8, 7), (10, 9)], "teal"); rect(im, 1, 9, 10, 9, "teal_d")
    # handlebar, cowl, headlight
    rect(im, 7, 0, 12, 0, "grey_k")
    rect(im, 5, 1, 10, 3, "teal"); rect(im, 5, 1, 10, 1, "glass_l")
    rect(im, 3, 2, 5, 4, "yl_l"); put(im, 3, 2, "white"); put(im, 5, 4, "yl_d")
    put(im, 7, 4, "or")                                                       # blinker
    return im


def peach_tree():
    """~40x34 airy peach tree (cây đào) with a wrapped root ball at the bottom-left (x 6-14, y 28-33)."""
    im = new(40, 34)
    rnd = random.Random(11)
    # branches: from the root ball up and back (right), forking
    br = [((10, 29), (14, 20)), ((14, 20), (12, 11)), ((14, 20), (22, 13)), ((12, 11), (7, 5)), ((12, 11), (16, 3)),
          ((22, 13), (28, 6)), ((22, 13), (32, 15)), ((28, 6), (34, 4)), ((16, 3), (21, 1)), ((7, 5), (3, 8)),
          ((32, 15), (37, 12)), ((14, 20), (6, 17))]
    for (x0, y0), (x1, y1) in br:
        line(im, x0, y0, x1, y1, "trunk_d")
    line(im, 11, 29, 15, 20, "trunk")
    tips = [(7, 5), (16, 3), (21, 1), (28, 6), (34, 4), (32, 15), (37, 12), (3, 8), (6, 17), (12, 11), (22, 13),
            (18, 8), (25, 10), (9, 13), (30, 10), (19, 17)]
    cells = []
    for x, y in tips:
        cells.append((x + rnd.choice((-1, 0, 1)), y, rnd.choice((2, 2, 3)), rnd.choice((2, 2, 1))))
    S = blobs(cells)
    for x, y in sorted(S):
        if not (0 <= x < 40 and 0 <= y < 34):
            continue
        h = (x * 7 + y * 13) % 11
        if h == 0:
            continue                                                         # airy gaps show branches
        col = "pk_l"
        if (x, y - 1) not in S or (x - 1, y) not in S:
            col = "bl_hl"
        elif (x + 1, y) not in S or (x, y + 1) not in S:
            col = "pk"
        if h == 5 and col == "pk_l":
            col = "white"
        put(im, x, y, col)
    for x, y in [(5, 3), (24, 4), (36, 10), (14, 15), (27, 14)]:              # new green buds
        put(im, x, y, "leaf_l")
    # root ball wrapped in red cloth, tied
    ellipse(im, 6, 27, 15, 33, "red"); rect(im, 7, 27, 13, 27, "red_l"); rect(im, 13, 29, 15, 32, "red_d")
    line(im, 7, 30, 14, 30, "gold")
    return im


def moto_dao_frames():
    out = []
    tree = peach_tree()
    for ph in range(3):
        im = new(56, 46)
        bx, by = 2, 26
        im.alpha_composite(tree, (18, 0))                                    # root ball sits on the rack (x 26-33)
        im.alpha_composite(bike(ph), (bx, by))
        im.alpha_composite(G(_rider, RIDER), (bx + 9, by - 13))
        out.append(im)
    return out


# ------------------------------------------------------------------ swallow (chim én), faces left, 4 flap frames
SW = {"N": "navy", "n": "nt", "W": "white", "R": "red_l", "w": "grey_hl"}
sw = [
    ["N.......N..", ".NN...NN...", "..NNNNN....", "RNNNNNNNN..", ".WWWNN..NN.", "..........N"],
    ["...........", "...........", "NNNNNNNNN..", "RNNNNNNNN..", ".WWWNN..NN.", "..........N"],
    ["...........", "...........", "..NNNNN....", "RNNNNNNNNN.", ".WWNNNNNNN.", "..NN..NN..N"],
    ["...........", "...........", "...NNN.....", "RNNNNNNNNN.", ".WWWNN.NNN.", "..........N"],
]


def swallow_frames():
    return [G(f, SW) for f in sw]


# ------------------------------------------------------------------ peach petals
def petal_frames():
    shapes = [[(0, 1, "pk_l"), (1, 0, "bl_hl"), (1, 1, "pk_l"), (2, 1, "pk"), (1, 2, "pk")],
              [(0, 0, "pk_l"), (1, 1, "pk_l"), (2, 2, "pk"), (1, 0, "bl_hl")],
              [(1, 0, "white"), (1, 1, "pk_l"), (1, 2, "pk")],
              [(2, 0, "pk_l"), (1, 1, "pk_l"), (0, 2, "pk"), (2, 1, "bl_hl")]]
    out = []
    for sh in shapes:
        im = new(3, 3)
        for x, y, n in sh:
            put(im, x, y, n)
        out.append(im)
    return out


def build():
    return {
        "lantern_red": (lantern_frames(), 2, (4, 0), {"sway": [0, 1, 0, 3]}),
        "flag_vn": (flag_frames(), 6, (0, 21), None),
        "kumquat": ([kumquat()], None, (10, 29), None),
        "banner_tet": ([banner()], None, (0, 0), None),
        "moto_dao": (moto_dao_frames(), 12, (7, 45), None),
        "swallow": (swallow_frames(), 10, (5, 3), None),
        "petal_peach": (petal_frames(), 6, (1, 1), None),
    }


if __name__ == "__main__":
    from PIL import Image
    out = build()
    for name, (frames, fps, anchor, states) in out.items():
        save_asset("actors", name, frames, fps=fps, anchor=anchor, states=states, notes="season: tết")
    k = 6; bg = (182, 218, 252)
    ims = [f for v in out.values() for f in v[0][:3]]
    Wt = sum(i.width * k + 10 for i in ims); Ht = max(i.height for i in ims) * k
    S = Image.new("RGB", (min(Wt, 3000), Ht * ((Wt // 3000) + 1) + 40), bg)
    x = y = 0
    for i in ims:
        if x + i.width * k > S.width:
            x = 0; y += Ht + 10
        b = Image.new("RGBA", i.size, bg + (255,)); b.alpha_composite(i)
        S.paste(b.convert("RGB").resize((i.width * k, i.height * k), Image.NEAREST), (x, y + Ht - i.height * k)); x += i.width * k + 10
    S.save(sys.argv[1] if len(sys.argv) > 1 else "review/gif_style/_sheets/tet_sheet.png")
    print("ok", {k_: v[0][0].size for k_, v in out.items()})
