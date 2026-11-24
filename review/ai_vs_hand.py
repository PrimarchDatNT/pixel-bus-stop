"""Comparison sheet: ComfyUI (SDXL + pixel-art-xl) vs hand-pixelled sprites -> review/gif_style/ai_vs_hand.png"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
AI = ROOT / "assets/src_gif/ai_test"
ACT = ROOT / "assets/out_gif/actors"
BG = (182, 218, 252)
K = 8


def first(name):
    meta = json.loads((ACT / f"{name}.json").read_text())
    return Image.open(ACT / f"{name}.png").convert("RGBA").crop((0, 0, meta["frameW"], meta["frameH"]))


def on_bg(im, k):
    b = Image.new("RGBA", im.size, BG + (255,)); b.alpha_composite(im)
    return b.convert("RGB").resize((im.width * k, im.height * k), Image.NEAREST)


rows = [("Bồ câu", "pigeon", first("pigeon_walk")), ("Chim sẻ", "sparrow", first("sparrow_perch")),
        ("Trà đá", "tea_stall", first("tea_table"))]
cells = []
for label, ai, hand in rows:
    raw = Image.open(AI / "raw" / f"{ai}_1_0.png").convert("RGB"); raw.thumbnail((300, 300))
    small = on_bg(Image.open(AI / f"px_{ai}.png").convert("RGBA"), K)
    cells.append((label, raw, small, on_bg(hand, K)))
cw = [max(c[i].width for c in cells) + 30 for i in (1, 2, 3)]
rh = [max(c[1].height, c[2].height, c[3].height) + 30 for c in cells]
head = 50
S = Image.new("RGB", (sum(cw) + 20, sum(rh) + head), (245, 243, 238))
d = ImageDraw.Draw(S)
try:
    f = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 22)
except OSError:
    f = ImageFont.load_default()
for i, t in enumerate(["ComfyUI gốc (1024 px)", "ComfyUI thu về cỡ trong cảnh", "Vẽ tay (props.py)"]):
    d.text((10 + sum(cw[:i]), 12), t, fill=(30, 30, 30), font=f)
y = head
for (label, *ims), h in zip(cells, rh):
    x = 10
    for im, w in zip(ims, cw):
        S.paste(im, (x, y + (h - 30 - im.height) // 2)); x += w
    y += h
S.save(ROOT / "review/gif_style/ai_vs_hand.png")
print(S.size)
