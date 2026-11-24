import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px_gif import *
from tools.layout_gif import *
from PIL import Image


def canvas():
    return new(W, H)


def blob_mask(blobs):
    S = set()
    for b in blobs:
        cx, cy = b[0], b[1]
        rx, ry = (b[2], b[2]) if len(b) == 3 else (b[2], b[3])
        for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
            for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
                if ((x - cx) / (rx + .5)) ** 2 + ((y - cy) / (ry + .5)) ** 2 <= 1.0:
                    S.add((x, y))
    return S


def box3(im, x0, y0, x1, y1, base, hl=None, sh=None):
    rect(im, x0, y0, x1, y1, base)
    if hl:
        line(im, x0, y0, x1 - 1, y0, hl); line(im, x0, y0, x0, y1 - 1, hl)
    if sh:
        line(im, x0, y1, x1, y1, sh); line(im, x1, y0 + 1, x1, y1, sh)


def ascii_put(im, x, y, rows, legend):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch in legend:
                put(im, x + i, y + j, legend[ch])
