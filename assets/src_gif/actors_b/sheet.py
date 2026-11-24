"""Preview helper: GIF character crops (top row) vs our hand-pixelled sprites (bottom row) at x8."""
import json, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[3]

def gif_crops():
    ref = ROOT / "refs/pinterest_pixel_shop.gif"          # third-party reference, not in the git repo
    if not ref.exists():
        return []
    g = Image.open(ref); g.seek(0)
    g = g.convert("RGB").resize((400, 300), Image.NEAREST)
    return [g.crop(b) for b in [(8, 244, 52, 268), (144, 222, 178, 256), (170, 122, 196, 154), (336, 218, 372, 282), (256, 228, 284, 256)]]

def sheet(sprites, out, k=8, bg=(182, 218, 252)):
    rows = [r for r in (gif_crops(), sprites) if r]
    strips = []
    for ims in rows:
        w = sum(i.width * k + 12 for i in ims); h = max(i.height for i in ims) * k
        s = Image.new("RGB", (w, h), bg); x = 0
        for i in ims:
            b = Image.new("RGBA", i.size, bg + (255,)); b.alpha_composite(i.convert("RGBA"))
            s.paste(b.convert("RGB").resize((i.width * k, i.height * k), Image.NEAREST), (x, h - i.height * k)); x += i.width * k + 12
        strips.append(s)
    W = max(s.width for s in strips); S = Image.new("RGB", (W, sum(s.height for s in strips) + 16), (30, 30, 30)); y = 0
    for s in strips:
        S.paste(s, (0, y)); y += s.height + 16
    S.save(out)
