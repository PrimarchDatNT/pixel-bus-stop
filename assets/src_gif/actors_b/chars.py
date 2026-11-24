"""Hand-pixelled characters for composition B, drawn as ASCII grids (one char = one pixel).

GIF rules (SPEC_GIF.md > Characters): big round heads (~3.5 heads tall), two 1-px eyes, flat skin, solid hair shape
with a highlight, 2-tone clothes, NO outline, 3-5 colours per figure, clean silhouettes.
Run:  .venv/bin/python assets/src_gif/actors_b/chars.py   (exports to assets/out_gif/actors/ + a comparison sheet)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
from tools.px_gif import *  # noqa: E402,F403

BASE = {  # shared legend
    "S": "sk_l", "s": "sk", "b": "wp", "E": "hair", "H": "hair", "h": "hair_l",
    "W": "white", "w": "grey_hl", "K": "ink",
}


def g(rows, **legend):
    return grid(rows, {**BASE, **legend})


def shift_rows(rows, a, b, dy):
    """Copy of rows where rows[a:b] are moved down by dy (for breathing / bob frames)."""
    out = list(rows)
    blank = "." * max(len(r) for r in rows)
    seg = rows[a:b]
    for i in range(a, b):
        out[i] = blank
    for i, r in enumerate(seg):
        if a + i + dy < len(out):
            out[a + i + dy] = r
    return out


# ------------------------------------------------------------------ cat (orange tabby loaf, asleep, faces left)
CAT = dict(O="or", L="or_l", D="or_d", Y="cat_hl", P="pk_l")
cat0 = [
    "..D....D.........",
    ".DPD..DPD........",
    ".OOOLLOOO.LLLLL..",
    "LOOOOOOOOLOOOOOOL.",
    "LOOOOOOOOOOODOOOO.",
    "OEEOOOEEOOOOODOOOD",
    "OWWOOOOODOOOOOOOOD",
    ".WWWWOODOOOOOOOOOD",
    "..DDDYYYYYYYYYDDD.",
]
cat1 = [  # breathing: back rises 1 px
    "..D....D.........",
    ".DPD..DPD.LLLL...",
    ".OOOLLOOOLOOOOOL.",
    "LOOOOOOOOOOOOOOOL.",
    "LOOOOOOOOOOODOOOO.",
    "OEEOOOEEOOOOODOOOD",
    "OWWOOOOODOOOOOOOOD",
    ".WWWWOODOOOOOOOOOD",
    "..DDDYYYYYYYYYDDD.",
]

# ------------------------------------------------------------------ dog (Vietnamese yellow dog lying, head up, faces left)
DOG = dict(O="or_l", D="or", d="or_d", Y="cat_hl", N="hair")
dog0 = [
    "..d...d..................",
    ".dOd.dOd.................",
    ".dOOOOOd.................",
    ".OYOOOOOd................",
    "NOEOOOOOd................",
    "WWWOOOOOd........d.......",
    "NWWWOOOODDDDDDDDDOd......",
    ".WWWOOOOOOOOOOOOOOOd.dd..",
    "..WWOOOOOOOOOOOOOOOODOd..",
    ".WWWWWOOOOOOOOOOOOOOOd...",
    "WWWWWWDDDDDDDDDDDDDDd....",
]
dog1 = [  # tail wag
    "..d...d..................",
    ".dOd.dOd.................",
    ".dOOOOOd.................",
    ".OYOOOOOd................",
    "NOEOOOOOd................",
    "WWWOOOOOd........d....dd.",
    "NWWWOOOODDDDDDDDDOd..dOd.",
    ".WWWOOOOOOOOOOOOOOOddOd..",
    "..WWOOOOOOOOOOOOOOOOd....",
    ".WWWWWOOOOOOOOOOOOOOOd...",
    "WWWWWWDDDDDDDDDDDDDDd....",
]

# ------------------------------------------------------------------ shopkeeper (front view, reading a newspaper)
SHOP = dict(C="wb_l", c="wb", N="paper", n="grey_l", m="wc")
shop_read = [
    ".....HHHHHHHH.....",
    "....HHhhhHHHHH....",
    "...HHhhHHHHHHHH...",
    "...HHSSSSSSSSHH...",
    "...HSSSSSSSSSSH...",
    "...SSSSSSSSSSSS...",
    "...SSSESSSSESSS...",
    "...sSbSSSSSSbSs...",
    "....sSSSSSSSSs....",
    "......sSSSSs......",
    "...CCCCCssCCCCC...",
    "..CCSSNNNNNNNSSCc.",
    "..CCSNNnnnNNnnNSc.",
    "..CcmNNNNNNNNNNmc.",
    "..CcmNnnNNnnnNNmc.",
    "..CcmNNNNNNNNNNmc.",
    "..CcmNnnnNNnnNNmc.",
]
shop_glance = [r for r in shop_read]
shop_glance[6] = "...SSSESSSSESSS..."
shop_glance[5] = "...SSSESSSSESSS..."   # eyes up: 1 px higher, 2 px tall = looking at the street
shop_glance[6] = "...SSSSSSSSSSSS..."
shop_glance[5] = "...SSSESSSSESSS..."
shop_read2 = [r for r in shop_read]
shop_read2[11] = "..CCSSNNNNNNNNSCc."   # page edge flips
shop_read2[12] = "..CCSNNnnnNNnnNNc."

# ------------------------------------------------------------------ woman waiting (seated, 3/4 to the left, phone)
WOM = dict(Y="yl_l", y="yl", J="sb", j="sb_d", P="grey_k", G="glass_l", R="red_l")
wom0 = [
    ".......HHHHH....",
    ".....HHHHHHHHH..",
    "....HHhhhHHHHHH.",
    "....HhhHHHHHHHH.",
    "....HSSSSSHHHHHH",
    "...SSSSSSSHHHHHH",
    "...SSSSSSSHHHHHH",
    "...SESSSESHHHHHH",
    "...SbSSSbsHHHHHH",
    "....sSSSsHHHHHH.",
    "......sSHHHHHH..",
    ".....YYYYYHHHH..",
    "....YYYYYYYHHy..",
    "....YYSSPYYYYy..",
    "...YYSSGPYYYYy..",
    "...YYYSSYYYYYy..",
    "....YYYYYYYYYy..",
    "....yYYYYYYYYy..",
    "..JJJJJJJJJJJj..",
    "JJJJJJJJJJJJJj..",
    "jjjjjjjjjjjjjj..",
    "JJj.............",
    "JJj.............",
    "JJj.............",
    "JJj.............",
    "JJj.............",
    "JJj.............",
    "SSs.............",
    "WWWWw...........",
]
wom1 = [r for r in wom0]          # idle: thumb taps (phone glint) + tiny head tilt via hair strand
wom1[13] = "....YYSSPYYYYy.."
wom1[14] = "...YYSSPGYYYYy.."
wom1[3] = "....HhhHHHHHHHHH"

# ------------------------------------------------------------------ old man (seated on a low stool, sipping tea, faces left)
OLD = dict(G="grey_l", g="grey", T="wc_l", t="wc", K2="wc_d", Q="wy_d", q="wood_l", A="glass_l", a="lamp")
old_rows = [
    "....GGGGG.....",
    "..GGSSSSSGG...",
    "..GSSSSSSSG...",
    ".SSSSSSSSSG...",
    ".SESSSSESSg...",
    ".SSSSSSSSSs...",
    ".SbSSSSbSs....",
    "..sSSSSSs.....",
    "....sSSs......",
    "..TTTTTTTTT...",
    ".TTTTTTTTTTt..",
    ".TTSSTTTTTTt..",
    "SSSSTTTTTTTt..",
    "AaSSTTTTTTTt..",
    "AaS.TTTTTTTt..",
    ".....TTTTTTt..",
    ".qQQQQQQQQQq..",
    "QQQQQQQQQQQq..",
    "QQQq..........",
    "QQQq..........",
    ".QQq..........",
    ".QQq..........",
    ".QQq..........",
    ".SSs..........",
    "WWWWw.........",
]
old_sip = [r for r in old_rows]   # glass raised to the mouth
old_sip[6] = "AaSSSSSbSs...."
old_sip[7] = "AaSSSSSSs....."
old_sip[11] = "SSSSTTTTTTt..."
old_sip[12] = ".SSTTTTTTTTt.."
old_sip[13] = "..TTTTTTTTTt.."
old_sip[14] = "....TTTTTTTt.."
old_sip = [r.ljust(14, ".")[:14] for r in old_sip]

# ------------------------------------------------------------------ grandma on the balcony watering plants (faces left)
GMA = dict(G="grey_l", g="grey", B="wb", b2="wb_d", V="sh", v="sh_d", X="hair", D="wb_d")
gma0 = [
    "......GGG.....",
    ".....GGGGG....",
    "....GGgGGGG...",
    "...GSSSSSGGG..",
    "..SSSSSSSSGG..",
    "..SESSSSSSG...",
    "..SSSSSSSSs...",
    "..SbSSSSSs....",
    "...sSSSSs.....",
    ".....ss.......",
    "....BBBBBB....",
    "...BBBBBBBB...",
    "..SBBBBBBBBD..",
    "VVSBBBBBBBBD..",
    "VVVSBBBBBBBD..",
    "VvVVBBBBBBBD..",
    ".VVV.BBBBBBD..",
    ".....BBBBBBD..",
    ".....XXXXXX...",
    ".....XXXXXX...",
    ".....XXX.XX...",
    ".....XXX.XX...",
    ".....XXX.XX...",
    ".....XXX.XX...",
    ".....XXX.XX...",
    "....SSs.SSs...",
]
gma1 = [r for r in gma0]          # can tipped: spout lower + 2 drops
gma1[13] = "V.SBBBBBBBBD.."
gma1[14] = "VVVSBBBBBBBD.."
gma1[15] = "VvVVBBBBBBBD.."
gma1[16] = "VVVV.BBBBBBD.."
gma1[17] = "A....BBBBBBD.."
gma1[19] = "A....XXXXXX..."
gma1 = [r.replace("A", "W") for r in gma1]


# ------------------------------------------------------------------ schoolkid who gets off the bus (walks right)
KID = dict(W="white", w="grey_hl", R="red", B="pb", p="pb_d", N="navy", K="hair")
_kid_top = [
    "....HHHH....",
    "...HHhhHH...",
    "..HHHHHHHH..",
    "..HHHSSSSH..",
    "..HHSSSSSS..",
    "..HHSSESSE..",
    "..HsSSSSbS..",
    "...sSSSSS...",
    ".....ss.....",
    "..BBWRRWW...",
    ".BBBWWRWWw..",
    ".BBBWWWWWS..",
    ".BppWWWWWS..",
    "..ppWWWWw...",
    "...NNNNNN...",
]
_kid_legs = [
    ["..NNN..NNN..", "..SS....SS..", ".SS......SS.", ".KK......KKK"],
    ["....NNNN....", "....SSSS....", "....SS.S....", "...KKK.KK..."],
    ["..NNN..NNN..", "..ss....SS..", ".ss......SS.", ".KK......KKK"],
    ["....NNNN....", "....SSSS....", "....S.SS....", "...KK.KKK..."],
]


def kid_frames():
    fr = []
    for i, legs in enumerate(_kid_legs):
        rows = list(_kid_top) + legs
        if i % 2 == 1:
            rows = shift_rows(rows, 0, 15, 1)
        fr.append(g(rows, **KID))
    return fr


def build():
    out = {}
    out["cat_sleep"] = ([g(cat0, **CAT), g(cat1, **CAT)], 2, None)
    out["dog_lie"] = ([g(dog0, **DOG), g(dog1, **DOG), g(dog0, **DOG), g(dog1, **DOG), g(dog0, **DOG), g(dog0, **DOG), g(dog0, **DOG), g(dog0, **DOG)], 6, None)
    out["shopkeeper"] = ([g(shop_read, **SHOP), g(shop_read2, **SHOP), g(shop_read, **SHOP), g(shop_glance, **SHOP)], 2, None)
    out["woman_wait"] = ([g(wom0, **WOM), g(wom1, **WOM)], 2, (7, 20))
    out["oldman_tea"] = ([g(old_rows, **OLD), g(old_rows, **OLD), g(old_sip, **OLD), g(old_sip, **OLD)], 2, None)
    out["grandma_water"] = ([g(gma0, **GMA), g(gma1, **GMA)], 3, None)
    out["walker_nonla"] = (vendor_frames(), 6, None)
    out["student_walk"] = (kid_frames(), 8, None)
    return out


# ------------------------------------------------------------------ street vendor with a shoulder pole (quang gánh), walks right
VEN = dict(N="wy_l", n="wy", m="wy_d", P="wood_l", r="wood_d", C="wb_l", c="wb", X="hair", B="wood", b="wood_d",
           F="or", f="red_l", L="leaf_l")
_ven_top = [
    "................N.................",
    "..............NNNNn...............",
    "............NNNNNNnnn.............",
    "..........NNNNNNNNNnnnn...........",
    "...........mmmmmmmmmmm............",
    ".............HHSSSSS..............",
    ".............HSSSSES..............",
    ".............HSSbSSs..............",
    "..............sSSSs...............",
    ".............CCCCCCc..............",
    "..PPPPPPPPPPPPPPPSPPPPPPPPPPPPPP..",
    "..r.........CCCCCSc...........r...",
    ".r.r........CCCCCCc..........r.r..",
    ".r.r........CCCCCCc..........r.r..",
    "r...r.......CCCCCCc.........r...r.",
    "r...r.......CCCCCCc.........r...r.",
    "FfFLFf......CCCCCCc........fFLfFf.",
    "BBBBBBB.....XXXXXXX........BBBBBBB",
    "bBBBBBb.....XXXXXXX........bBBBBBb",
    ".bBBBb......XXXXXXX.........bBBBb.",
]
_legs = [
    ["............XXX..XX..............", "...........XXX....XX.............", "..........XXX......XX............",
     "..........SS.......SS............", ".........SSS.......SSS..........."],
    ["............XXX.XX...............", "............XXX.XX...............", "...........XXX..XX...............",
     "...........SS...SS...............", "..........SSS...SSS.............."],
    ["............XX..XXX..............", "...........XX....XXX.............", "..........XX......XXX............",
     "..........SS.......SS............", ".........SSS.......SSS..........."],
    ["............XX.XXX...............", "............XX.XXX...............", "............XX..XXX..............",
     "............SS...SS..............", "............SSS..SSS............."],
]


def vendor_frames():
    fr = []
    for i, legs in enumerate(_legs):
        rows = list(_ven_top) + legs
        if i % 2 == 1:                       # body bob: baskets swing 1 px
            rows = shift_rows(rows, 0, 20, 1)
        fr.append(g(rows, **VEN))
    return fr


if __name__ == "__main__":
    from sheet import sheet
    sprites = build()
    for name, (frames, fps, anchor) in sprites.items():
        w = max(f.width for f in frames); h = max(f.height for f in frames)
        frames = [paste_to(f, w, h) if f.size != (w, h) else f for f in frames] if False else frames
        norm = []
        for f in frames:
            c_ = new(w, h); c_.alpha_composite(f, (0, h - f.height)); norm.append(c_)
        save_asset("actors", name, norm, fps=fps, anchor=anchor or (w // 2, h - 1))
    sheet([v[0][0] for v in sprites.values()], "review/gif_style/_sheets/chars_b.png")
    print("ok", list(sprites))


