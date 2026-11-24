import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px_gif import *
from tools.layout_gif import *
from PIL import Image


def canvas():
    return new(W, H)


def blob_mask(blobs):
    """blobs: (cx, cy, r) or (cx, cy, rx, ry) -> set of pixels (filled ellipses)."""
    S = set()
    for b in blobs:
        cx, cy = b[0], b[1]
        rx, ry = (b[2], b[2]) if len(b) == 3 else (b[2], b[3])
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / (rx + .5)) ** 2 + ((y - cy) / (ry + .5)) ** 2 <= 1.0:
                    S.add((x, y))
    return S


def sp(img, S, name):
    for x, y in S:
        put(img, x, y, name)


def vtext(img, x, y, s, col):
    return text(img, x, y, s, col)


def centered_text(img, cx, y, s, col):
    w, _ = text_size(s)
    text(img, cx - w // 2, y, s, col)
