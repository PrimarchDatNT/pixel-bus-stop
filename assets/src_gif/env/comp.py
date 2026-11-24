import sys
from common import *
from PIL import Image
D = ROOT / "assets" / "out_gif"
def load(g, n, f=0):
    im = Image.open(D / g / f"{n}.png").convert("RGBA")
    fw = im.height and 384
    return im.crop((f * 384, 0, f * 384 + 384, 216))
def composite(names, tree_frame=0):
    bg = Image.new("RGBA", (384, 216), (255, 0, 255, 255))
    for g, n in names:
        p = D / g / f"{n}.png"
        if p.exists():
            bg.alpha_composite(load(g, n, tree_frame if n == "tree" else 0))
    return bg
if __name__ == "__main__":
    names = [("env", "sky"), ("env", "skyline"), ("env", "ground"), ("env", "houses"), ("shelter", "shelter"), ("env", "tree"), ("actors", "actors")]
    bg = composite(names)
    scale = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/g/comp.png"
    if len(sys.argv) > 6:
        x0, y0, x1, y1 = map(int, sys.argv[3:7]); bg = bg.crop((x0, y0, x1, y1))
    bg.resize((bg.width * scale, bg.height * scale), 0).convert("RGB").save(out)
