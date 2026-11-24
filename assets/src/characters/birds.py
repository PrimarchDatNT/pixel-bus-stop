from lib import *
from walkers import SCR
import sys

SW = {"N": "navy", "B": "blue_d", "W": "white", "R": "rust", "K": "ink", "g": "grey_l", "b": "blue", "S": "slate_d"}
swallow = [
    # wings up
    ["...NN....",
     "..NNN....",
     ".NNBN....",
     "NNNNNNNN.",
     "N.NWWWRRK",
     "...WWW...",
     "........."],
    # wings level-up
    [".........",
     "....N....",
     "..NNNN...",
     "NNNBNNNNN",
     "N.NWWWWRK",
     "..NWWW...",
     "........."],
    # wings down
    [".........",
     ".........",
     "....NNN..",
     "NNNNBNNNN",
     "N.NNWWWRK",
     "..NNNNN..",
     "..NN.NN.."],
    # wings level-down
    [".........",
     ".........",
     "..NNNN...",
     "NNNNBNNNN",
     "N.NWWWWRK",
     "...NNN...",
     "....N...."],
]
# fix: use consistent forked tail & navy back
swallow = [
    ["...N.....",
     "..NNN....",
     "N.NBNN...",
     "NNNNNNNNK",
     ".N.WWWRR.",
     ".........",
     "........."],
    [".........",
     "...NN....",
     "N.NBNNN..",
     "NNNNNNNNK",
     ".N.WWWRR.",
     ".........",
     "........."],
    [".........",
     ".........",
     "N........",
     "NNNBNNNNK",
     ".N.WWWRR.",
     "...NNN...",
     "........."],
    [".........",
     ".........",
     "N........",
     "NNNBNNNNK",
     ".N.WWWRR.",
     "..NNN....",
     ".N......."],
]

SP = {"c": "brown_d", "m": "clay", "s": "sand", "w": "grey_l", "i": "ink", "g": "gold", "f": "brown_k", "d": "brown_d",
      "r": "rust", "b": "brown_k", "k": "brown_k", "t": "ochre"}
sp_fly = [
    ["..d......",
     ".ddd.....",
     "dddmmcc..",
     ".dmmmccis",
     "..wsssssg",
     "...wwww..",
     "........."],
    [".........",
     ".mmmm....",
     "dmmmmmcc.",
     "ddmmmcciss",
     "..wwwsssg",
     "...wwww..",
     "........."],
    [".........",
     ".........",
     "dmmmmmcc.",
     "dddmmmcis",
     ".dmwssssg",
     "..dddd...",
     "...dd...."],
    [".........",
     ".........",
     "dmmmmmmc.",
     "ddmmmmcis",
     "..wwsssg.",
     "..wdddd..",
     "....d...."],
]
sp_fly = [[r[:9].ljust(9, ".") for r in f] for f in sp_fly]

def perched(head_dy=0, body_dy=0, tilt=0, blink=False, peck=0, hop=0):
    rows = [
        ".....cc..",
        "....cccg.",
        "..mmccisg",
        ".mmmmssss",
        ".mmmwwss.",
        "..mwwww..",
        "...f.f...",
    ]
    return rows

def perched_frame(kind, i):
    # base perched (feet at bottom row 6). returns image 9x7
    img = new(9, 7)
    def px(x, y, col): put(img, x, y, col)
    # body ellipse
    body = [(2, 3, 7), (1, 4, 7), (1, 5, 6), (2, 6, 6)]
    # use compact ascii per kind
    return img

# perched frames (hand drawn)
P_IDLE0 = [
    ".....cc..",
    "....cccc.",
    "..m.cciss",
    ".mmmcsssg",
    ".mmmwsss.",
    "..mmwww..",
    "...f.f...",
]
P_IDLE1 = [      # head tilt + blink
    ".........",
    ".....ccc.",
    "..m.cccss",
    ".mmmcsssg",
    ".mmmwsss.",
    "..mmwww..",
    "...f.f...",
]
P_PECK0 = [      # head dipping
    ".........",
    "..m..cc..",
    ".mmm.cccc",
    ".mmmmcciss",
    ".mmmwwsssg",
    "..mmwww..",
    "...f.f...",
]
P_PECK1 = [      # head down at the ground
    ".........",
    ".........",
    "..mm.....",
    ".mmmmcc..",
    ".mmmwcccs",
    "..mmwwwss",
    "...f.f.cg",
]
P_HOP0 = [       # crouch
    ".........",
    ".........",
    "....cc...",
    "..mmcccc.",
    ".mmmcisss",
    ".mmwwsssg",
    "..fwwwf..",
]
P_HOP1 = [       # airborne
    ".....cc..",
    "....cccc.",
    "..m.cciss",
    ".mmmcsssg",
    ".mmmwsss.",
    "..mmwww..",
    "..f...f..",
]
def fix(rows): return [r[:9].ljust(9, ".") for r in rows]
P = {k: fix(v) for k, v in dict(idle0=P_IDLE0, idle1=P_IDLE1, peck0=P_PECK0, peck1=P_PECK1, hop0=P_HOP0, hop1=P_HOP1).items()}

def build_sparrow():
    fr = [grid(f, SP) for f in sp_fly]
    for k in ("idle0", "idle1", "peck0", "peck1", "hop0", "hop1"):
        fr.append(grid(P[k], SP))
    # hop1 airborne: raise sprite by 1px (clear bottom row)
    return fr

def build_swallow():
    return [grid(f, SW) for f in swallow]

def sheet(fr, path, k=24):
    w, h = fr[0].size
    im = Image.new("RGBA", (w * len(fr) * k, h * k), (*RGB["sky_l"], 255))
    for i, f in enumerate(fr):
        im.alpha_composite(f.resize((w * k, h * k), Image.NEAREST), (i * w * k, 0))
    im.convert("RGB").save(path)

if __name__ == "__main__":
    sw = build_swallow(); sp = build_sparrow()
    sheet(sw, SCR + "swallow.png"); sheet(sp, SCR + "sparrow.png", 10)
    if "--export" in sys.argv:
        export_lr("characters", "swallow", sw, 10, anchor=(4, 3), notes="chim en, 9x7, anchor = body centre (flying: not ground-based)",)
        st = {"fly": [0, 1, 2, 3], "idle": [4, 5], "peck": [6, 7], "hop": [8, 9]}
        export_lr("characters", "sparrow", sp, 10, states=st, anchor=(4, 6),
                  notes="chim se; states: fly 4f@10fps, idle 2f@2fps, peck 2f@4fps, hop 2f@4fps (perched states anchor = feet)")
