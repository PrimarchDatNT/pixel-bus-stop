"""Blocking mock for the v4 GIF-style frame: flat shapes at the layout_gif positions."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.px_gif import *
from tools.layout_gif import *

im = new(W, H)
rect(im, 0, 0, W - 1, H - 1, "sky")
rect(im, 0, 0, W - 1, 20, "sky_hl")
# distant skyline
import random
r = random.Random(3); x = 0
while x < W:
    w = r.randint(10, 24); top = r.randint(84, 130)
    rect(im, x, top, x + w - 1, FACADE_BASE_Y, r.choice(["haze_l", "haze"])); x += w
# houses
cols = ["wb", "wy", "wp", "wc", "wy"]
for (x0, x1, top, fl), col in zip(HOUSES, cols):
    rect(im, x0, top, x1 - 1, FACADE_BASE_Y - 1, col)
    rect(im, x0, top, x1 - 1, top + 3, "wood_d")
    fh = (FACADE_BASE_Y - top - 4) // fl
    for f in range(fl):
        y = top + 4 + f * fh
        rect(im, x0 + 6, y + 6, x1 - 7, y + fh - 6, "glass_d" if f else "wood_d")
        rect(im, x0 + 2, y + fh - 3, x1 - 3, y + fh - 2, "grey_d")
# tree
x0, y0, x1, y1 = TREE_CANOPY_BOX
ellipse(im, x0 - 20, y0 - 10, x1, y1, "leaf")
rect(im, TREE_TRUNK_X - 5, 90, TREE_TRUNK_X + 5, STAND_Y, "trunk")
# shelter
rect(im, SHELTER_X0 + 6, SHELTER_ROOF_UNDER_Y, SHELTER_X1 - 6, STAND_Y - 10, "glass")
rect(im, SHELTER_X0 + 14, SEAT_Y, SHELTER_X1 - 30, SEAT_Y + 3, "pb")
rect(im, SHELTER_X0, SHELTER_ROOF_TOP_Y, SHELTER_X1, SHELTER_ROOF_UNDER_Y, "grey_k")
for px_ in (SHELTER_X0 + 4, SHELTER_X1 - 6):
    rect(im, px_, SHELTER_ROOF_UNDER_Y, px_ + 2, STAND_Y, "grey_d")
cx0, cy0, cx1, cy1 = CANOPY_BOX
ellipse(im, cx0, cy0, cx1, cy1, "bl")
rect(im, BOUGAINVILLEA_PLANTER[0], STAND_Y - 10, BOUGAINVILLEA_PLANTER[1], STAND_Y, "tc")
rect(im, STOP_SIGN_X, 132, STOP_SIGN_X + 1, STAND_Y, "grey_d"); rect(im, STOP_SIGN_X - 6, 128, STOP_SIGN_X + 7, 142, "pb")
# props + people blocks
rect(im, TRA_DA_X, STAND_Y - 8, TRA_DA_X + 50, STAND_Y, "red")
rect(im, TRA_DA_X + 20, STAND_Y - ADULT_H + 8, TRA_DA_X + 30, STAND_Y - 6, "sb")
rect(im, MOTORBIKE_X, STAND_Y - MOTORBIKE_WH[1], MOTORBIKE_X + MOTORBIKE_WH[0], STAND_Y, "red_d")
rect(im, 170, STAND_Y - ADULT_H + 6, 178, STAND_Y - 8, "pk")       # waiting woman (seated)
rect(im, CAT_SPOT[0], CAT_SPOT[1] - 5, CAT_SPOT[0] + 12, CAT_SPOT[1] - 1, "or")
# ground
rect(im, 0, SIDEWALK_Y0, W - 1, SIDEWALK_Y1, "pave")
rect(im, 0, CURB_Y0, W - 1, CURB_Y1, "grey_l")
rect(im, 0, ROAD_Y0, W - 1, ROAD_Y1, "road")
out = pathlib.Path(__file__).resolve().parents[1] / "assets/out_gif/_mock"
im.save(out / "mock.png"); im.resize((W * 5, H * 5), Image.NEAREST).save(out / "mock@5x.png")
print("ok")
