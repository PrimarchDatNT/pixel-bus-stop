from _c import *
im = canvas()
px_ = STOP_SIGN_X
rect(im, px_, 140, px_+1, STAND_Y-1, "grey_m"); rect(im, px_, 140, px_, STAND_Y-1, "grey_l"); rect(im, px_+1, 140, px_+1, STAND_Y-1, "grey_d")
rect(im, px_-1, STAND_Y-1, px_+2, STAND_Y, "grey_d")
# plate 14x13
a, b = px_-6, px_+7
rect(im, a, 128, b, 141, "pb"); rect(im, a, 128, b, 128, "pb_l"); rect(im, a, 128, a, 141, "pb_l")
rect(im, b, 129, b, 141, "pb_d"); rect(im, a+1, 141, b, 141, "pb_d")
rect(im, a+1, 129, b-1, 140, "pb")
rect(im, a, 128, b, 141, "navy") if False else None
# white bus pictogram (front view, 9x8)
bx, by = a+2, 130
rect(im, bx, by, bx+9, by+7, "white")
rect(im, bx+1, by+1, bx+8, by+3, "pb")                 # windscreen
rect(im, bx+1, by+1, bx+2, by+1, "glass_l")
rect(im, bx+1, by+5, bx+2, by+5, "pb"); rect(im, bx+7, by+5, bx+8, by+5, "pb")  # lights
rect(im, bx+1, by+8, bx+2, by+9, "white"); rect(im, bx+7, by+8, bx+8, by+9, "white")  # wheels
rect(im, bx, by+6, bx+9, by+6, "grey_l")
# route plate
r0, r1 = px_-5, px_+6
rect(im, r0, 143, r1, 152, "white"); rect(im, r0, 143, r1, 143, "grey_hl"); rect(im, r1, 144, r1, 152, "grey_l"); rect(im, r0, 152, r1, 152, "grey_l")
rect(im, r0, 143, r1, 143, "red"); rect(im, r0, 143, r1, 144, "red")
text(im, r0+2, 148, "32", "navy")
save_asset("shelter", "stop_sign", im, anchor=(0, 0), notes="Post at STOP_SIGN_X (312): plate x306-319 y128-141, route plate 32 y143-152.")
