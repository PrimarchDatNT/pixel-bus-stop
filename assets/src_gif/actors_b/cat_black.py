"""Black cat (mèo mun) — the client's cat. Sits on the bus-shelter roof, grooms, looks at the camera.

GIF rules: no outline, ink body with a grey_k rim light on the top/left, yellow eyes, pink nose/tongue.
Faces left. States (4 fps): sit, lick, wash, look, blink. Exported as actors/cat_black.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(Path(__file__).parent))
from tools.px_gif import *  # noqa: E402,F403

CB = {"K": "ink", "h": "grey_k", "Y": "yl_l", "p": "pk_l", "e": "grey_d"}

BODY = [               # rows 6.. (neck down), shared by most frames
    "..KKKK........",
    "..KKKKKh......",
    "..KKKKKKh.....",
    "..KKKKKKKh....",
    "..KKKKKKKK....",
    "..KKKKKKKK....",
    "..KKKKKKKKK...",
    ".hKKhKKKKKKhh.",
    "...........hKh",
]
TAIL_UP = [            # alt last two rows: tail tip lifted
    ".hKKhKKKKKKhh.",
    "............hK",
]
HEAD_SIDE = [
    "...h.h........",
    "..hKhKK.......",
    "..KKKKK.......",
    ".KYKKKK.......",
    "KKKKKKK.......",
    ".KKKKK........",
]
HEAD_FRONT = [         # looking at the camera
    "..h...h.......",
    "..Kh.hK.......",
    "..KKKKK.......",
    ".KYKKKYK......",
    ".KKKpKKK......",
    "..KKKKK.......",
]
HEAD_BLINK = [r for r in HEAD_FRONT]
HEAD_BLINK[3] = ".KeKKKeK......"
LICK0 = [              # paw raised to the mouth, eye closed, tongue out
    "..............",
    "....h.h.......",
    "...hKhKK......",
    "..KeKKKK......",
    ".pKKKKKK......",
    "KKKKKKK.......",
    "KKKKKKh.......",
    ".KKKKKKh......",
    "..KKKKKKh.....",
    "..KKKKKKKh....",
    "..KKKKKKKK....",
    "..KKKKKKKK....",
    "...KKKKKKKK...",
    "...hKKKKKKKhh.",
    "...........hKh",
]
LICK1 = [r for r in LICK0]   # head dips 1 px onto the paw
LICK1[1:6] = ["..............", "....h.h.......", "...hKhKK......", "..KeKKKK......", "KpKKKKKK......"]
WASH0 = [              # paw over the ear / face
    "...h.h........",
    ".KhKhKK.......",
    "KKKKKKK.......",
    "KKeKKKK.......",
    ".KKKKKK.......",
    "..KKKK........",
    "..KKKKKh......",
    "..KKKKKKh.....",
    "..KKKKKKKh....",
    "..KKKKKKKK....",
    "..KKKKKKKK....",
    "...KKKKKKKK...",
    "...hKKKKKKKhh.",
    "...........hKh",
    "..............",
]
WASH0 = WASH0[:-1]


def frame(head, body=BODY, tail_up=False):
    rows = list(head) + list(body)
    if tail_up:
        rows = rows[:-2] + TAIL_UP
    return rows


def build():
    sit = frame(HEAD_SIDE)
    sit_t = frame(HEAD_SIDE, tail_up=True)
    look = frame(HEAD_FRONT)
    blink = frame(HEAD_BLINK)
    frames = [sit, sit_t, LICK0, LICK1, WASH0, look, blink]
    ims = [grid([r.ljust(14, ".") for r in f], CB) for f in frames]
    h = max(i.height for i in ims)
    out = []
    for i in ims:
        c_ = new(14, h); c_.alpha_composite(i, (0, h - i.height)); out.append(c_)
    states = {"sit": [0, 0, 0, 1, 1, 0, 0, 0], "lick": [2, 3, 2, 3, 2, 3, 2, 3], "wash": [4, 4, 0, 4, 4, 0],
              "look": [5, 5, 5, 5, 5, 5, 6, 5, 5, 5, 5, 5], "watch": [0, 0, 0, 0]}
    return out, states


if __name__ == "__main__":
    frames, states = build()
    save_asset("actors", "cat_black", frames, fps=4, anchor=(6, frames[0].height - 1), states=states,
               notes="black cat on the shelter roof; anchor = paws row. compositor drives states by timeline")
    from PIL import Image
    k = 10; bg = (220, 95, 157)
    S = Image.new("RGB", (len(frames) * (14 * k + 10), frames[0].height * k), bg)
    for i, f in enumerate(frames):
        b = Image.new("RGBA", f.size, bg + (255,)); b.alpha_composite(f)
        S.paste(b.convert("RGB").resize((f.width * k, f.height * k), Image.NEAREST), (i * (14 * k + 10), 0))
    S.save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/cat_black.png")
    print("ok", [f.size for f in frames])
