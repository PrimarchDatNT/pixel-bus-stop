"""Blocking mock for composition B, drawn from tools/layout_gif.py constants."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.px_gif import *
from tools.layout_gif import *

im = new(W, H)
rect(im, 0, 0, W - 1, H - 1, "sky"); rect(im, 0, 0, W - 1, 14, "sky_hl")
for cx, cy, r in [(330, 34, 16), (350, 30, 12), (312, 38, 10), (110, 18, 9), (124, 16, 7)]:
    ellipse(im, cx - r, cy - r // 2, cx + r, cy + r // 2, "cloud")
for x0, w, top in [(300, 14, 150), (314, 10, 140), (330, 16, 146), (346, 12, 136), (358, 18, 150), (376, 10, 142)]:
    rect(im, x0, top, x0 + w, 178, "haze_l")
rect(im, 300, 160, 383, 163, "haze")
for x in range(302, 384, 12):
    line(im, x, 160, x + 6, 150, "haze"); line(im, x + 6, 150, x + 12, 160, "haze")
rect(im, 0, 170, W - 1, 180, "haze_l")
# hero house
rect(im, HOUSE_X0, HOUSE_WALL_TOP_Y, HOUSE_X1, HOUSE_BASE_Y, "wy_d")
poly(im, [(HOUSE_X0 - 8, HOUSE_WALL_TOP_Y + 2), (HOUSE_X1 + 8, HOUSE_WALL_TOP_Y + 2), (HOUSE_X1 - 12, ROOF_RIDGE_Y), (HOUSE_X0 + 12, ROOF_RIDGE_Y)], "tc_d")
rect(im, *DORMER, "tc_d")
for x in range(HOUSE_X0 + 12, HOUSE_X1 - 12, 34):
    rect(im, x, 84, x + 18, BALCONY_Y - 4, "sh_d")
rect(im, HOUSE_X0, BALCONY_Y, HOUSE_X1, BALCONY_Y + 3, "wood_k")
for x in range(HOUSE_X0 + 2, HOUSE_X1, 4):
    line(im, x, BALCONY_Y - 10, x, BALCONY_Y, "wood_d")
rect(im, SHOP_VISIBLE_X[0], SHOP_Y0, HOUSE_X1 - 4, HOUSE_BASE_Y, "wood_d")
rect(im, 200, SHOP_Y0 - 2, 280, SHOP_Y0 + 8, "paper")
# bloom + shelter
x0, y0, x1, y1 = CANOPY_BOX
ellipse(im, x0, y0, x0 + 150, y0 + 110, "bl"); ellipse(im, 60, 90, x1, y1, "bl"); ellipse(im, x0, 100, 90, y1 + 6, "bl_d")
rect(im, BOUGAINVILLEA_PLANTER[0], STAND_Y - 10, BOUGAINVILLEA_PLANTER[1], STAND_Y, "tc")
rect(im, SHELTER_X0, SHELTER_ROOF_TOP_Y, SHELTER_X1, SHELTER_ROOF_UNDER_Y, "grey_k")
rect(im, SHELTER_X0 + 6, SHELTER_ROOF_UNDER_Y, SHELTER_X1 - 6, STAND_Y - 6, "glass")
rect(im, SHELTER_X0 + 20, SEAT_Y, SHELTER_X1 - 40, SEAT_Y + 2, "pb")
for px_ in (SHELTER_X0 + 2, SHELTER_X1 - 4):
    rect(im, px_, SHELTER_ROOF_UNDER_Y, px_ + 2, STAND_Y, "grey_d")
rect(im, STOP_SIGN_X, 140, STOP_SIGN_X + 1, STAND_Y, "grey_d"); rect(im, STOP_SIGN_X - 6, 132, STOP_SIGN_X + 7, 146, "pb")
# actors blocks
rect(im, WAITER_SPOT[0] - 4, WAITER_SPOT[1] - 22, WAITER_SPOT[0] + 4, WAITER_SPOT[1] + 8, "pk")
rect(im, CAT_SPOT[0] - 7, CAT_SPOT[1] - 9, CAT_SPOT[0] + 7, CAT_SPOT[1] - 1, "or")
rect(im, SHOPKEEPER_SPOT[0] - 6, SHOPKEEPER_SPOT[1] - 18, SHOPKEEPER_SPOT[0] + 6, SHOPKEEPER_SPOT[1], "sb")
rect(im, BALCONY_SPOT[0] - 4, BALCONY_SPOT[1] - 26, BALCONY_SPOT[0] + 4, BALCONY_SPOT[1] - 10, "wp")
rect(im, DOG_SPOT[0] - 12, DOG_SPOT[1] - 10, DOG_SPOT[0] + 12, DOG_SPOT[1], "or_l")
rect(im, TRA_DA_X, STAND_Y - 8, TRA_DA_X + 20, STAND_Y, "wood"); rect(im, OLDMAN_SPOT[0] - 4, OLDMAN_SPOT[1] - 26, OLDMAN_SPOT[0] + 4, OLDMAN_SPOT[1], "wc")
rect(im, 0, SIDEWALK_Y0, W - 1, SIDEWALK_Y1, "pave"); rect(im, 0, CURB_Y0, W - 1, CURB_Y1, "grey_l"); rect(im, 0, ROAD_Y0, W - 1, H - 1, "road")
out = pathlib.Path(__file__).resolve().parents[1] / "assets/out_gif/_mock"
im.save(out / "mock3.png"); im.resize((W * 5, H * 5), Image.NEAREST).save(out / "mock3@5x.png")
print("ok")
