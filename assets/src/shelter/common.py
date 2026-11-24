"""Shared helpers for the shelter group. All drawing uses GLOBAL scene coordinates;
layers share one canvas: top-left at scene (OX, OY), size CW x CH, so every layer lines up 1:1."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *
from tools.layout import *
from tools.mockbg import mock_scene, place, save_mock

OX, OY = 136, 84
CW, CH = 164, 96            # covers x136..299, y84..179
GROUP = "shelter"
SEASONS_ = ["xuan", "ha", "thu", "dong"]
PILL_L = (162, 164)         # front pillar x ranges
PILL_R = (275, 277)
ROOF_X0, ROOF_X1 = SHELTER_X0, SHELTER_X1


def layer():
    return new(CW, CH)


def R(img, x0, y0, x1, y1, col):
    rect(img, x0 - OX, y0 - OY, x1 - OX, y1 - OY, col)


def P(img, x, y, col):
    put(img, x - OX, y - OY, col)


def Ln(img, x0, y0, x1, y1, col):
    line(img, x0 - OX, y0 - OY, x1 - OX, y1 - OY, col)


def Poly(img, pts, col):
    poly(img, [(x - OX, y - OY) for x, y in pts], col)


def T(img, x, y, s, col, scale=1):
    return text(img, x - OX, y - OY, s, col, scale)


def D(img, x0, y0, x1, y1, a, b, t):
    dither(img, x0 - OX, y0 - OY, x1 - OX, y1 - OY, a, b, t)


def Paste(img, spr, x, y):
    paste(img, spr, x - OX, y - OY)


def getp(img, x, y):
    x -= OX; y -= OY
    if 0 <= x < img.width and 0 <= y < img.height:
        return img.getpixel((x, y))
    return CLEAR


def export(name, frames, fps=None, notes=""):
    n = ("Canvas %dx%d, top-left at scene (%d,%d), anchor (0,0). " % (CW, CH, OX, OY)) + notes
    save_asset(GROUP, name, frames, fps=fps, anchor=(0, 0), notes=n)
