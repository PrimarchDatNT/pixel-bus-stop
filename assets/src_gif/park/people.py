"""Park-scene characters (bản 6b, 24/11/2026).

grandma_ex : the grandma (same look as the old balcony grandma) doing morning exercise on the park path, front view.
             4 frames @ 2 fps, state "ex" = arms down -> out -> up -> out (one cycle = 2 s, divides the 24 s loop).
cat_black_lie : the client's black cat lying on the shelter bench (sleep / look / watch, driven by a timeline).
cat_tabby  : a mèo mướp (grey-brown tabby) sitting on the café counter, front view; tail flick, blink, ear twitch.
             4 frames @ 4 fps, state "idle" (12 steps = 3 s).
GIF rules: no outline, flat 2-3 tones, light from the upper-left.

    .venv/bin/python assets/src_gif/park/people.py [sheet.png]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.px_gif import *  # noqa: E402,F403

# ------------------------------------------------------------------ grandma exercising (16 x 28, feet on the last row)
GLEG = {"G": "grey_l", "g": "grey", "S": "sk_l", "s": "sk", "E": "hair", "b": "wp", "B": "wb", "D": "wb_d",
        "X": "hair"}
G_BODY = [
    "................",
    "................",
    "......GGG.......",
    ".....GgGGG......",
    "....GGGGGGG.....",
    "...GGgGGGGGG....",
    "...GSSSSSSSG....",
    "...GSESSSESG....",
    "...GSSSSSSSs....",
    "....SbSSSbs.....",
    ".....SSSSs......",
    "......sss.......",
    "....BBBBBBB.....",
    ".....BBBBD......",
    ".....BBBBD......",
    ".....BBBBD......",
    ".....BBBBD......",
    ".....BBBBD......",
    ".....BBBBD......",
    ".....BBBBD......",
    ".....XXXXX......",
    ".....XX.XX......",
    ".....XX.XX......",
    ".....XX.XX......",
    ".....XX.XX......",
    ".....XX.XX......",
    ".....XX.XX......",
    "....SSs.sSS.....",
]
# arms: polylines of 2x2 blocks from the shoulder to the hand (left arm lit "B", right arm shaded "D")
ARMS = {
    "down": ([(3, 13), (3, 17)], (3, 19), [(10, 13), (10, 17)], (10, 19)),
    "out": ([(3, 12), (1, 12)], (0, 12), [(10, 12), (13, 12)], (14, 12)),
    "up": ([(3, 11), (1, 7), (1, 2)], (1, 0), [(11, 11), (13, 7), (13, 2)], (13, 0)),
}


def grandma(pose):
    rows = [list(r) for r in G_BODY]

    def block(x, y, ch, w=2, h=2):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < 16 and 0 <= yy < 28 and rows[yy][xx] in ".":
                    rows[yy][xx] = ch

    if pose == "down":                    # arms hang 1 px wide with a gap, so the torso stays slim
        for y in range(13, 19):
            rows[y][3] = "B"; rows[y][11] = "D"
        rows[13][4] = "B"; rows[13][10] = "D"
        rows[19][3] = "S"; rows[19][11] = "s"; rows[20][3] = "S"; rows[20][11] = "s"
        return grid(["".join(r) for r in rows], GLEG)
    la, lh, ra, rh = ARMS[pose]
    for pts, hand, ch, sk in ((la, lh, "B", "S"), (ra, rh, "D", "s")):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(abs(x1 - x0), abs(y1 - y0), 1)
            for i in range(n + 1):
                block(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), ch)
        if len(pts) == 1:
            block(*pts[0], ch)
        block(hand[0], hand[1], sk, 2, 2 if pose == "down" else 2)
    if pose == "out":                     # shoulders spread into the arms
        for x in (4, 10):
            rows[12][x] = "B" if x == 4 else "D"
    return grid(["".join(r) for r in rows], GLEG)


# ------------------------------------------------------------------ tabby cat sitting, front view (12 x 12)
TAB = {"T": "wood_l", "t": "wood", "H": "wood_hl", "W": "wc_l", "w": "wc", "Y": "leaf_hl", "p": "pk_l", "k": "wood_d"}
CAT0 = [
    ".H.....H....",
    ".HT...TT....",
    ".HTTTTTT....",
    ".TtTtTtT....",
    "HTYkTkYTT...",
    "TTTWpWTTt...",
    ".TTWWWTt....",
    "..TWWWT.....",
    ".TTWWWtT....",
    ".TtWWWTtT...",
    "HTtWwWtTTt..",
    "TTWWTWWTTTTk",
]
CAT_BLINK = list(CAT0); CAT_BLINK[4] = "HTkkTkkTT..."
CAT_TAIL = list(CAT0)                     # tail tip flicks up
CAT_TAIL[9] = ".TtWWWTtT.Tk"; CAT_TAIL[10] = "HTtWwWtTT.T."; CAT_TAIL[11] = "TTWWTWWTTTT."
CAT_EAR = list(CAT0)                      # right ear twitches flat
CAT_EAR[0] = ".H.........."; CAT_EAR[1] = ".HT....TT..."


def build():
    gm = [grandma(p) for p in ("down", "out", "up")]
    save_asset("actors", "grandma_ex", gm, fps=2, anchor=(7, 27), states={"ex": [0, 1, 2, 1]},
               notes="grandma exercising on the park path (park scene); anchor = feet")
    cats = [grid(f, TAB) for f in (CAT0, CAT_BLINK, CAT_TAIL, CAT_EAR)]
    save_asset("actors", "cat_tabby", cats, fps=4, anchor=(5, 11),
               states={"idle": [0, 0, 0, 2, 0, 0, 1, 0, 0, 2, 0, 3]},
               notes="mèo mướp sitting on the café counter; anchor = paws row")
    return gm, cats


# ------------------------------------------------------------------ the black cat (mèo mun) lying on the shelter bench
# Same rules as actors/cat_black: ink body, grey_k rim light on top/left edges, yellow eyes, pink nose. Faces left.
CBL = {"K": "ink", "h": "grey_k", "Y": "yl_l", "p": "pk_l", "e": "grey_d"}
LIE_BODY = [                 # rows 3..9 (body loaf + front paws + tail wrapped along the front)
    "........hhhhhhh.....",
    ".......hKKKKKKKKh...",
    "......KKKKKKKKKKKh..",
    "......KKKKKKKKKKKKh.",
    ".....KKKKKKKKKKKKKKh",
    "hKhhKKhhhhhhhhhhKKKK",
    "KKKKKKKKKKKKKKKKKKK.",
]
HEAD_DOWN = [                # asleep: front-facing head resting on the paws, eyes shut
    "....................",
    "....................",
    "....................",
    ".h...h..............",
    ".Kh.hK..............",
    ".KKKKKK.............",
    "KeeKeeKK............",
    "KKKpKKKK............",
]
HEAD_FRONT_UP = [            # head up, looking at the camera / the arriving bus
    "..h...h.............",
    "..Kh.hK.............",
    "..KKKKK.............",
    ".KYKKKYK............",
    ".KKKpKKK............",
    "..KKKKK.............",
]
HEAD_SIDE_UP = [             # head up in profile, watching the bus pull away to the left
    "..h.h...............",
    ".hKhKK..............",
    ".KKKKK..............",
    "KYKKKK..............",
    "KKKKKKK.............",
    ".KKKKK..............",
]


def lie(head, top=0, breath=False, tail_up=False, blink=False):
    rows = [["."] * 20 for _ in range(10)]
    body = list(LIE_BODY)
    start = 3
    if breath:                               # the middle of the back rises 1 px (rounded, not a box)
        body = list(body)
        body[0] = "........hKKKKKh....."
        rows[2][9:14] = list("hhhhh")
    for j, r in enumerate(body):
        for i, ch in enumerate(r):
            if ch != "." and 0 <= start + j < 10:
                rows[start + j][i] = ch
    for j, r in enumerate(head):
        for i, ch in enumerate(r):
            if ch != ".":
                rows[top + j][i] = ch
    if tail_up:                              # tail tip lifts off the bench for a beat
        rows[7][19] = "K"; rows[6][19] = "h"; rows[8][19] = "."
    out = ["".join(r) for r in rows]
    if blink:
        out = [r.replace("Y", "e") for r in out]
    return out


def build_cat_lie():
    frames = [lie(HEAD_DOWN), lie(HEAD_DOWN, breath=True), lie(HEAD_DOWN, tail_up=True),
              lie(HEAD_FRONT_UP), lie(HEAD_FRONT_UP, blink=True), lie(HEAD_SIDE_UP), lie(HEAD_SIDE_UP, tail_up=True)]
    ims = [grid(f, CBL) for f in frames]
    states = {"sleep": [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 2, 1],     # 4 s breathing cycle + a tail twitch
              "look": [3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3],
              "watch": [5, 5, 5, 6, 5, 5, 5, 5]}
    save_asset("actors", "cat_black_lie", ims, fps=4, anchor=(0, 9), states=states,
               notes="mèo mun lying on the shelter bench (park scene); anchor = left end of the bottom row")
    return ims


if __name__ == "__main__":
    build_cat_lie()
    gm, cats = build()
    from PIL import Image
    k = 10; bg = (63, 68, 73)
    ims = gm + cats + build_cat_lie()
    Wd = sum(i.width * k + 20 for i in ims); Hd = max(i.height for i in ims) * k
    S = Image.new("RGB", (Wd, Hd), bg); x = 0
    for i in ims:
        b = Image.new("RGBA", i.size, bg + (255,)); b.alpha_composite(i)
        S.paste(b.convert("RGB").resize((i.width * k, i.height * k), Image.NEAREST), (x, Hd - i.height * k)); x += i.width * k + 20
    S.save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/people.png")
    print("ok")
