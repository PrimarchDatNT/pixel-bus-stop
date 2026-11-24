"""Hand-pixelled birds + trà đá corner in the GIF style (no outline, flat 2-3 tones, darker right face).

    .venv/bin/python assets/src_gif/actors_b/props.py     # -> assets/out_gif/actors/ + preview sheet in scratchpad

Sprites: sparrow_perch, sparrow_fly, pigeon_walk (states walk/peck), pigeon_perch, pigeon_fly,
tea_table (table + thermos + teapot basket + candy jar + iced-tea glasses + ice box; no điếu cày), stool_red, stool_blue,
steam. All face left; flip() for the other way.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
from tools.px_gif import *  # noqa: E402,F403


def G(rows, legend):
    w = max(len(r) for r in rows)
    return grid([r.ljust(w, ".") for r in rows], legend)


def pad(frames, anchor_row=None):
    """Same-size frames, bottom-aligned (or aligned so `anchor_row` of each source lands on the same row)."""
    w = max(f.width for f in frames); h = max(f.height for f in frames)
    out = []
    for f in frames:
        c_ = new(w, h); c_.alpha_composite(f, (0, h - f.height)); out.append(c_)
    return out


# ------------------------------------------------------------------ sparrow (house sparrow, faces left)
SP = {"T": "trunk", "R": "tc", "t": "trunk_d", "C": "wc", "c": "wc_d", "K": "ink", "b": "or_d", "d": "grey_d", "w": "white"}
sp_idle = [
    "..TTT...",
    ".TTTTT..",
    "bKwTTRR.",
    ".wCTRRtt",
    "..CCRRtt",
    "...Cct..",
    "...d.d..",
]
sp_look = [            # head raised, chest puffed
    "..TTT...",
    ".TTTTT..",
    "bKwTTT..",
    ".wCCTRR.",
    ".CCCRRtt",
    "..CcRRtt",
    "...d.d..",
]
sp_peck = [
    "........",
    "...TTT..",
    "..TTTRRt",
    ".TTCRRtt",
    "bKwCCRt.",
    "..wCct..",
    "...d.d..",
]
sp_fly = [
    ["....RR..", "...tRR..", "..TtR...", "bKTTTTtt", ".wCCtt..", "........", "........"],   # wings up
    ["........", "........", "..TT....", "bKTRRRRt", ".wCCTtt.", "........", "........"],   # wings level
    ["........", "........", "..TT....", "bKTTTTtt", ".wCtRt..", "...RR...", "...R...."],   # wings down
    ["........", "........", "..TT....", "bKTRRRRt", ".wCCTtt.", "........", "........"],
]

# ------------------------------------------------------------------ pigeon (rock pigeon, faces left)
PG = {"G": "grey_l", "g": "grey", "m": "grey_m", "d": "grey_d", "N": "teal", "n": "teal_d", "W": "white",
      "K": "ink", "b": "grey_k", "P": "pk_l", "H": "grey_hl", "D": "grey_k"}
pg_stand = [
    "..HHG.........",
    ".HGKGg........",
    "bWGGgg........",
    "..GNNg........",
    "..NNnGGg......",
    "..GNGGGgggg...",
    "..GGGGgmmggggd",
    "...GGGggmmgddd",
    "....GgggggggD.",
    ".....gggggg...",
    "......P..P....",
]
pg_step = [            # head forward (bob), feet together
    ".HHG..........",
    "HGKGg.........",
    "WGGgg.........",
    ".GNNgg........",
    "..NNnGGg......",
    "..GNGGGgggg...",
    "..GGGGgmmggggd",
    "...GGGggmmgddd",
    "....GgggggggD.",
    ".....gggggg...",
    ".......PP.....",
]
pg_peck0 = [           # leaning down
    "..............",
    "..............",
    "..............",
    "......GGgg....",
    "....HGGGgggg..",
    "...GGGGgmmgggd",
    "..NNGGGggmmddd",
    ".GNnGGGgggggD.",
    "HGKGgggggggg..",
    "WGGg..gggg....",
    "b.....P..P....",
]
pg_peck1 = [           # beak on the ground
    "..............",
    "..............",
    "..............",
    "......GGgg....",
    "....HGGGgggg..",
    "...GGGGgmmgggd",
    "..NNGGGggmmddd",
    "..NnGGGgggggD.",
    ".HGGgggggggg..",
    "HGKg..gggg....",
    "WbG...P..P....",
]
pg_fly = [
    ["......mG......", ".....mGG......", "....mGGg......", ".HG.GGg.......", "WKGGGGGgggdd..", "..NGGGGggdd...", "....gggg......", "..............", ".............."],
    ["..............", "..............", "..............", ".HG...........", "WKGGmmGGGgggdd", "..NGGGGGGgdd..", "....gggg......", "..............", ".............."],
    ["..............", "..............", "..............", ".HG...........", "WKGGGGGgggdd..", "..NGGgGggdd...", "....gmGg......", ".....mGg......", "......mg......"],
    ["..............", "..............", "..............", ".HG...........", "WKGGmmGGGgggdd", "..NGGGGGGgdd..", "....gggg......", "..............", ".............."],
]

# ------------------------------------------------------------------ plastic stool (front view, low Vietnamese stool)
ST = {"L": "red_l", "R": "red", "D": "red_d"}
stool_rows = [
    ".LLLLLLLLL.",
    "LRRRRRRRRRD",
    ".RRRRRRRRD.",
    ".RD.....RD.",
    ".RD.....RD.",
    ".RD.....RD.",
    "RRD.....RDD",
    "RD.......RD",
]

# ------------------------------------------------------------------ trà đá table pieces
THERMOS = (["..gg..", ".HHgg.", ".DDDD.", "LRRRRD", "LRRRRD", "LWWHRD", "LWPWRD", "LHWWRD", "LRRRRD", "LRRRRD",
            "LRRRRD", "LRRRRD", ".DDDD."],
           {"g": "grey_l", "H": "grey_hl", "L": "red_l", "R": "red", "D": "red_d", "W": "white", "P": "pk_l"})
BASKET = ([".....W....", "....WWH...", "S..WWWWH..", ".SSWbbbWH.", ".RRRRRRRRD", "YyyyyyyyyD", "YyyyyyyyyD",
           "mmmmmmmmmD", ".YyyyyyyD.", "..yyyyyD.."],                      # teapot in a padded rattan basket (ấm ủ)
          {"W": "white", "H": "grey_hl", "S": "grey_hl", "b": "sb", "R": "red", "D": "wy_d", "Y": "wy_l", "y": "wy",
           "m": "wy_d"})
JAR = ([".RRRR.", ".DDDD.", "IggggG", "IYYYyG", "ImmmmG", "IYYYyG", "ImmmmG", ".gggg."],
       {"R": "red", "D": "red_d", "I": "glass_l", "g": "glass", "G": "glass_d", "Y": "yl", "y": "yl_d", "m": "or_d"})
GLASS = (["IWH", "Ioo", "IoO", "Ioo"], {"I": "glass_l", "W": "white", "H": "grey_hl", "o": "or", "O": "or_d"})
ICEBOX = (["HHHHHHHHHH", "WWWWWWWWWc", "WWWWWWWWWc", "WWWWWWWWWc", "WWWWWWWWWc", "WWWWWWWWWc"],
          {"H": "grey_hl", "W": "white", "c": "wc"})


def tea_table():
    """Low wooden table, front elevation. Returns (image, anchor) with anchor = bottom-centre of the table legs."""
    tw = 34                                   # table width
    ox = 4                                    # (left margin kept so the table stays where it was)
    im = new(ox + tw + 1, 24)
    top = 13
    rect(im, ox, top, ox + tw - 1, top, "wood_hl")
    rect(im, ox, top + 1, ox + tw - 1, top + 2, "trunk_l")
    rect(im, ox + tw - 1, top + 1, ox + tw - 1, top + 2, "trunk")
    rect(im, ox + 1, top + 3, ox + tw - 2, top + 3, "trunk_d")         # shade under the top
    for lx in (ox + 2, ox + tw - 4):                                   # front legs
        rect(im, lx, top + 4, lx, 23, "trunk_l"); rect(im, lx + 1, top + 4, lx + 1, 23, "trunk")
    # ice box under the table (behind the stretcher)
    box = G(*ICEBOX)
    under = new(im.width, im.height); under.alpha_composite(box, (ox + 7, 18))
    under.alpha_composite(im); im = under
    rect(im, ox + 4, 20, ox + tw - 5, 20, "trunk"); rect(im, ox + 4, 21, ox + tw - 5, 21, "trunk_d")   # stretcher
    # items standing on the table top (bottom row = top - 1)
    def stand(sprite, x):
        s = G(*sprite); im.alpha_composite(s, (ox + x, top - s.height))
    stand(THERMOS, 1)
    stand(BASKET, 9)
    stand(JAR, 19)
    rect(im, ox + 26, top - 1, ox + 33, top - 1, "pb")               # small plastic tray
    rect(im, ox + 33, top - 1, ox + 33, top - 1, "pb_d")
    for gx in (26, 30):
        g_ = G(*GLASS); im.alpha_composite(g_, (ox + gx, top - 1 - g_.height))
    # (no điếu cày: the client doesn't want tobacco in the film)
    return im, (ox + tw // 2, 23)


def steam_frames():
    paths = [[(1, 8), (2, 7), (2, 6), (1, 5), (1, 4), (2, 3)],
             [(2, 8), (1, 7), (1, 6), (2, 5), (2, 4), (1, 3), (1, 2)],
             [(1, 7), (2, 6), (2, 5), (1, 4), (1, 3), (2, 2), (2, 1)],
             [(2, 7), (1, 6), (1, 5), (2, 4), (2, 3), (1, 2)]]
    out = []
    for p in paths:
        im = new(4, 9)
        for j, (x, y) in enumerate(p):
            put(im, x, y, "white" if j < len(p) - 2 else "cloud_d")
        out.append(im)
    return out


def build():
    out = {}
    out["sparrow_perch"] = (pad([G(sp_idle, SP), G(sp_idle, SP), G(sp_look, SP), G(sp_idle, SP), G(sp_peck, SP),
                                 G(sp_idle, SP)]), 3, None, None)
    out["sparrow_fly"] = ([G(r, SP) for r in sp_fly], 10, (3, 3), None)
    walk = [G(pg_stand, PG), G(pg_step, PG)]
    peck = [G(pg_peck0, PG), G(pg_peck1, PG)]
    out["pigeon_walk"] = (pad(walk + peck), 4, None, {"walk": [0, 1], "peck": [0, 2, 3, 2, 3, 0, 0, 0]})
    perch = [G(pg_stand[:-1], PG), G(pg_stand[:-1], PG), G(pg_step[:-1], PG), G(pg_stand[:-1], PG)]
    out["pigeon_perch"] = (pad(perch), 2, None, None)
    out["pigeon_fly"] = ([G(r, PG) for r in pg_fly], 9, (6, 4), None)
    tt, anc = tea_table()
    out["tea_table"] = ([tt], 0, anc, None)
    st = G(stool_rows, ST)
    out["stool_red"] = ([st], 0, None, None)
    out["stool_blue"] = ([recolor(st, {"red_l": "pb_l", "red": "pb", "red_d": "pb_d"})], 0, None, None)
    out["steam"] = (steam_frames(), 4, (1, 8), None)
    return out


def preview(sprites, path, k=8, bg=(182, 218, 252)):
    from PIL import Image
    ims = [v[0] for v in sprites.values()]
    rows = [[f for f in fr] for fr in ims]
    W_ = max(sum(f.width * k + 10 for f in r) for r in rows); H_ = sum(max(f.height for f in r) * k + 10 for r in rows)
    S = Image.new("RGB", (W_, H_), bg); y = 0
    for r in rows:
        x = 0; h = max(f.height for f in r) * k
        for f in r:
            b = Image.new("RGBA", f.size, bg + (255,)); b.alpha_composite(f)
            S.paste(b.convert("RGB").resize((f.width * k, f.height * k), Image.NEAREST), (x, y + h - f.height * k))
            x += f.width * k + 10
        y += h + 10
    S.save(path)


if __name__ == "__main__":
    sprites = build()
    for name, (frames, fps, anchor, states) in sprites.items():
        w, h = frames[0].size
        kw = dict(fps=fps or None, anchor=anchor or (w // 2, h - 1))
        if states:
            kw["states"] = states
        save_asset("actors", name, frames, notes="hand-pixelled, props.py (GIF style)", **kw)
    preview(sprites, sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "review/gif_style/props_sheet.png"))
    print("ok", list(sprites))
