"""Compose the 640x360 style frame from processed sprites + summer sky; also writes @3x."""
import json, os, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(f'{HERE}/../../out_v2/render3d')

def sky():
    W, H = 640, 360
    bands = [(0, (18, 84, 196)), (22, (28, 104, 214)), (46, (44, 126, 228)), (72, (66, 148, 238)), (98, (92, 168, 244)),
             (124, (122, 188, 248)), (150, (154, 206, 250)), (176, (186, 222, 252)), (198, (212, 236, 252))]
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    for i, (y, c) in enumerate(bands):
        y1 = bands[i + 1][0] if i + 1 < len(bands) else H
        d.rectangle([0, y, W, y1], fill=c)
    return im.convert('RGBA')

def cloud(im, cx, cy, s, seed):
    import random
    r = random.Random(seed); d = ImageDraw.Draw(im)
    puffs = [(cx + dx * s, cy + dy * s, rr * s) for dx, dy, rr in [(-30, 4, 12), (-14, -4, 16), (4, -9, 19), (22, -3, 15), (38, 4, 11), (0, 6, 14), (20, 7, 10), (-20, 8, 9)]]
    cols = [(255, 255, 255), (244, 249, 255), (226, 238, 252), (200, 218, 244), (176, 194, 232)]
    for k, col in enumerate(cols):
        for (x, y, rr) in puffs:
            yy = y + k * 2.4 * s * 0.5 - (len(cols) - 1 - k) * 0.0
            d.ellipse([x - rr, y - rr + k * 1.9, x + rr, y + rr * 0.78 + 1.0 - 0 * k], fill=col) if k == 0 else None
    # simple shaded cloud: base white, lower-right shade bands
    base = Image.new('L', im.size, 0); bd = ImageDraw.Draw(base)
    for (x, y, rr) in puffs: bd.ellipse([x - rr, y - rr, x + rr, y + rr * 0.8], fill=255)
    b = np.array(base) > 0
    ys, xs = np.nonzero(b); arr = np.array(im)
    y0, y1 = ys.min(), ys.max()
    for y, x in zip(ys, xs):
        t = (y - y0) / max(1, y1 - y0)
        k = 0 if t < 0.45 else 1 if t < 0.62 else 2 if t < 0.8 else 3
        if x < xs.min() + (xs.max() - xs.min()) * 0.18 and k < 2: k = max(0, k - 1)
        arr[y, x, :3] = cols[k]
    im.paste(Image.fromarray(arr))

def main():
    pl = json.load(open(f'{OUT}/placements.json'))
    f = sky()
    for (cx, cy, s, sd) in [(236, 52, 0.95, 1), (404, 36, 0.8, 2), (570, 24, 0.6, 3), (58, 30, 0.55, 4)]:
        cloud(f, cx, cy, s, sd)
    for name in ('ground', 'facades', 'shelter_ha', 'bus_L', 'cat_sit'):
        im = Image.open(f'{OUT}/{name}.png').convert('RGBA'); x, y = pl[name]
        f.alpha_composite(im, (x, y)) if x >= 0 and y >= 0 else f.alpha_composite(im.crop((max(0, -x), max(0, -y), im.width, im.height)), (max(0, x), max(0, y)))
    # crop to 640x360 (bus partially cut by right edge)
    f = f.crop((0, 0, 640, 360)).convert('RGB')
    f.save(f'{OUT}/styleframe.png'); f.resize((1920, 1080), Image.NEAREST).save(f'{OUT}/styleframe@3x.png')
    print('styleframe done')
if __name__ == '__main__': main()
