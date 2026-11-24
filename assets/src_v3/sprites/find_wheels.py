"""Detect wheel circles in a cutout with Hough (tyre outline). Prints/returns [[x,y,r],...] sorted by x."""
import sys, numpy as np
from PIL import Image
from skimage.feature import canny
from skimage.transform import hough_circle, hough_circle_peaks

def wheels(path, rmin, rmax, n=2, ylow=0.45):
    im = Image.open(path).convert("RGBA"); W, H = im.size
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    g = np.array(bg.convert("L"), float) / 255
    s = 0.5; g2 = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((int(W * s), int(H * s))), float) / 255
    e = canny(g2, sigma=1.5); e[: int(H * s * ylow)] = False
    rs = np.arange(int(rmin * s), int(rmax * s), 2)
    h = hough_circle(e, rs)
    acc, cx, cy, rad = hough_circle_peaks(h, rs, total_num_peaks=12, min_xdistance=int(rmin * s * 1.3), min_ydistance=int(rmin * s))
    out = []
    for a, x, y, r in zip(acc, cx, cy, rad):
        if all(abs(x / s - o[0]) > rmin * 1.3 for o in out): out.append((x / s, y / s, r / s, a))
        if len(out) == n: break
    return sorted(out)

if __name__ == "__main__":
    p, rmin, rmax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    for o in wheels(p, rmin, rmax): print([round(v, 1) for v in o])
