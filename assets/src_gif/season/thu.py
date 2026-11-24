"""Trung Thu (autumn) sprites, hand-pixelled in the GIF style.

    .venv/bin/python assets/src_gif/season/thu.py [sheet.png]

star_lantern (đèn ông sao, hangs from its top pixel, sways), lion_dance (múa lân troupe walking right: lion + ông Địa
+ drummer kid, one sprite so they stay in step), lantern_kid_a / lantern_kid_b (kids walking right holding a star lantern
on a stick), leaf_yellow (falling autumn leaf, 4 tumble frames).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "assets/src_gif/actors_b"))
from tools.px_gif import *  # noqa: E402,F403
import chars  # noqa: E402


def G(rows, legend):
    w = max(len(r) for r in rows)
    return grid([r.ljust(w, ".") for r in rows], legend)


# ------------------------------------------------------------------ star lantern
STAR = {"L": "red_l", "R": "red", "D": "red_d", "Y": "gold", "y": "or", "k": "wood_d"}
_star = [
    ".....Y.....",
    ".....L.....",
    "....LRR....",
    "....LRD....",
    "YLLLRRRRRDY",
    ".LRRRRRRRD.",
    "..LRRRRRD..",
    "...RRRRD...",
    "..LRRRRRD..",
    "..RRD.RRD..",
    ".RD.....RD.",
    "YD.......DY",
]


def star_img():
    return G(_star, STAR)


def star_lantern_frames():
    out = []
    for dx in (0, 1, 0, -1):
        im = new(13, 17)
        put(im, 6, 0, "wood_d"); put(im, 6, 1, "wood_d"); put(im, 6 + dx, 2, "wood_d"); put(im, 6 + dx, 3, "wood_d")
        im.alpha_composite(star_img(), (1 + dx, 4))
        put(im, 1 + dx, 16, "gold"); put(im, 11 + dx, 16, "gold")                       # tassels
        out.append(im)
    return out


# ------------------------------------------------------------------ lion dance troupe (walks right)
LION = {"R": "red", "r": "red_d", "L": "red_l", "Y": "gold", "y": "or", "O": "or_l", "W": "white", "w": "grey_hl",
        "K": "ink", "G": "leaf_l", "g": "leaf", "M": "red_d", "T": "white", "P": "yl", "p": "yl_d", "B": "pb_l"}
_head_open = [
    "......YGGY......",
    "....YYRRRRYY....",
    "...YRRRRRRRRY...",
    "..YRLLRRRRRRRY..",
    ".YRLWWWRRRWWWRY.",
    ".YRWKKWRRRWKKWY.",
    "YRRWWWWRRRWWWWRY",
    "YRRRRRRRRRRRRRRY",
    "WYRGGGRRRRRGGGRY",
    "WWYRRRRRRRRRRRRY",
    "WWYYYYYYYYYYYYYY",
    "WWW.TTTTTTTTTT..",
    "WWWMMMMMMMMMMM..",
    "WWWYYYYYYYYYYY..",
    ".WWWWWWWWWWWW...",
    "..WWWWWWWWWW....",
]
_head_shut = [r for r in _head_open]
_head_shut[11] = "WWWYYYYYYYYYYY.."
_head_shut[12] = "WWWWWWWWWWWWW..."
_head_shut[13] = ".WWWWWWWWWWW...."
_head_shut[14] = "..WWWWWWWWW....."
_head_shut[15] = "................"
_body = [
    "....................",
    "...............YYYYY",
    "..........YYYYRRRRRR",
    "......YYYYRRRRRRRRRR",
    "...YYYRRRYRRRYRRRYRR",
    "..YRRRYRRRYRRRYRRRYR",
    ".WYRRYRRRYRRRYRRRYRR",
    "WWYRRRRYRRRYRRRYRRRR",
    "WWRRYRRRYRRRYRRRYRRR",
    ".RRRRRRRRRRRRRRRRRRR",
    ".WWWWWWWWWWWWWWWWWWW",
    ".W.W.W.W.W.W.W.W.W.W",
]
_legs = [   # two dancers: rear (cols 3-9), front (cols 19-26); P pants, W fur cuff, K shoes
    ["...PPPP.........PPPP....", "...PP.PP........PP.PP...", "..PP...PP......PP...PP..", "..WW...WW......WW...WW..",
     ".KKK..KKK.....KKK..KKK.."],
    ["....PPP..........PPP....", "....PPP..........PPP....", "....PPPP.........PPPP...", "....WWWW.........WWWW...",
     "...KKKKK........KKKKK..."],
]
DIA = {"S": "sk_l", "s": "sk", "K": "hair", "b": "pk_l", "M": "red_d", "O": "or", "o": "or_d", "P": "wood",
       "k": "ink", "F": "wy_l", "f": "wy_d", "H": "sk"}
_dia = [
    "...SSSSSSSS......",
    "..SSSSSSSSSS.....",
    ".SSSSSSSSSSSS....",
    ".SSKKSSSSKKSS....",
    ".SSSSSSSSSSSS....",
    ".SbbSSSSSSbbS....",
    ".SSMMMMMMMMSS....",
    "..SSMMMMMMSS.....",
    "...sSSSSSSs......",
    "..OOOOOOOOOO.....",
    ".OOOSSSSSSOOO.FF.",
    "OOOSSSSSSSSOOFFFF",
    "OOSSSSSSSSSSOFFFf",
    "OOSSSSSSSSSSoHFf.",
    "OOSSSSSSSSSSo.f..",
    ".OOSSSSSSSSoo....",
    ".OOOSSSSSSOoo....",
    ".OOOOOOOOOOoo....",
]
_dia_fan2 = [r for r in _dia]
_dia_fan2[9] = "..OOOOOOOOOO.FF.."
_dia_fan2[10] = ".OOOSSSSSSOOOFFF."
_dia_fan2[11] = "OOOSSSSSSSSOOFFFf"
_dia_fan2[12] = "OOSSSSSSSSSSOHFf."
_dia_fan2[13] = "OOSSSSSSSSSSo.f.."
_dia_fan2[14] = "OOSSSSSSSSSSo...."
_dia_legs = [["..PPPP..PPPP.....", "..PPP....PPP.....", ".kkk.....kkk....."],
             ["...PPPPPPPP......", "....PPPPPP.......", "...kkk..kkk......"]]
DRUM = {"R": "red", "r": "red_d", "Y": "gold", "C": "wc_l", "c": "wc", "w": "wood_hl", "S": "sk_l"}
_drum = [
    "CCCCCCCC",
    "cCCCCCCc",
    "YRRRRRRY",
    "RRRRRRRr",
    "RRYRRYRr",
    "RRRRRRRr",
    "YRRRRRRY",
]


def drummer(i):
    """Kid (schoolkid body, red T-shirt) with a drum at the waist; sticks alternate."""
    top = [r.replace("W", "Q").replace("w", "q").replace("R", "Q") for r in chars._kid_top]
    top = [r.replace("B", ".").replace("p", ".") for r in top]
    rows = top + chars._kid_legs[i % 4]
    im = G(rows, {**chars.BASE, "Q": "red_l", "q": "red", "N": "navy", "K": "hair"})
    im2 = new(16, im.height + 2); im2.alpha_composite(im, (0, 2))
    im2.alpha_composite(G(_drum, DRUM), (5, 13))
    up = i % 2 == 0                                                          # drumsticks
    line(im2, 6, 10 if up else 12, 8, 14 if up else 13, "wood_hl")
    line(im2, 12, 12 if up else 10, 10, 13 if up else 14, "wood_hl")
    return im2


def lion_dance_frames():
    out = []
    for i in range(4):
        im = new(80, 30)
        bob = 0 if i % 2 == 0 else 1
        legs = _legs[i % 2]
        # drummer (behind, left), ông Địa (middle), lion (right)
        im.alpha_composite(drummer(i), (0, 30 - 21))
        dia = G((_dia if i % 2 == 0 else _dia_fan2) + _dia_legs[i % 2], DIA)
        im.alpha_composite(dia, (17, 30 - dia.height - (i % 2)))
        lion = new(44, 30)
        lion.alpha_composite(G(legs, LION), (6, 25))
        lion.alpha_composite(G(_body, LION), (3, 14 + bob))
        lion.alpha_composite(G(_head_open if i in (0, 1) else _head_shut, LION), (22, 3 + (1 - bob) * 2))
        im.alpha_composite(lion, (36, 0))
        out.append(im)
    return out


# ------------------------------------------------------------------ kids carrying a star lantern on a stick
def lantern_kid(shirt, shirt_d, skirt=None):
    fr = []
    for i, legs in enumerate(chars._kid_legs):
        top = [r.replace("R", "W").replace("B", "W").replace("p", "w") for r in chars._kid_top]
        top = [r[:1] + r[1:] for r in top]
        rows = top + legs
        if skirt:
            rows = rows[:14] + [skirt] + rows[15:]
        if i % 2 == 1:
            rows = chars.shift_rows(rows, 0, 15, 1)
        kid = G(rows, {**chars.BASE, "W": shirt, "w": shirt_d, "N": "navy", "K": "hair"})
        im = new(26, 34)
        im.alpha_composite(kid, (0, 34 - kid.height))
        b = i % 2
        hy = 34 - kid.height + 11 + b                                         # hand height
        line(im, 9, hy, 17, hy - 9, "wood_hl")                                # stick forward-up
        sw = (0, 1, 0, -1)[i]
        put(im, 17, hy - 8, "wood_d"); put(im, 17 + (sw > 0), hy - 7, "wood_d")
        im.alpha_composite(star_img(), (12 + sw, hy - 6))
        fr.append(im)
    return fr


# ------------------------------------------------------------------ autumn leaf
def leaf_frames():
    shapes = [[(0, 0, "yl_l"), (1, 0, "yl"), (1, 1, "yl"), (2, 1, "or"), (2, 2, "or_d")],
              [(0, 1, "yl"), (1, 1, "or"), (2, 1, "or_d"), (1, 0, "yl_l")],
              [(2, 0, "yl"), (1, 1, "yl_l"), (0, 2, "or"), (1, 2, "or_d")],
              [(1, 0, "yl_l"), (1, 1, "yl"), (1, 2, "or")]]
    out = []
    for sh in shapes:
        im = new(3, 3)
        for x, y, n in sh:
            put(im, x, y, n)
        out.append(im)
    return out


def build():
    return {
        "star_lantern": (star_lantern_frames(), 2, (6, 0), {"sway": [0, 1, 0, 3]}),
        "lion_dance": (lion_dance_frames(), 6, (40, 29), None),
        "lantern_kid_a": (lantern_kid("pk_l", "pk"), 8, (5, 33), None),
        "lantern_kid_b": (lantern_kid("yl_l", "yl"), 8, (5, 33), None),
        "leaf_yellow": (leaf_frames(), 6, (1, 1), None),
    }


if __name__ == "__main__":
    from PIL import Image
    out = build()
    for name, (frames, fps, anchor, states) in out.items():
        save_asset("actors", name, frames, fps=fps, anchor=anchor, states=states, notes="season: trung thu")
    k = 8; bg = (182, 218, 252)
    ims = [f for v in out.values() for f in v[0][:2]]
    Wt = sum(i.width * k + 10 for i in ims); Ht = max(i.height for i in ims) * k
    S = Image.new("RGB", (Wt, Ht), bg)
    x = 0
    for i in ims:
        b = Image.new("RGBA", i.size, bg + (255,)); b.alpha_composite(i)
        S.paste(b.convert("RGB").resize((i.width * k, i.height * k), Image.NEAREST), (x, Ht - i.height * k)); x += i.width * k + 10
    S.save(sys.argv[1] if len(sys.argv) > 1 else "review/gif_style/_sheets/thu_sheet.png")
    print("ok", {k_: v[0][0].size for k_, v in out.items()})
