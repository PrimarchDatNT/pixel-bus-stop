from _c import *
im = canvas()
XA, XB = 150, 203
S = SEAT_Y   # seat top
rect(im, XA-1, S+3, XB+1, S+4, "grey_m"); rect(im, XA-1, S+3, XB+1, S+3, "grey_l"); rect(im, XA-1, S+4, XB+1, S+4, "grey_d")
for lx in (153, 179, 199):
    rect(im, lx, S+5, lx+1, STAND_Y-1, "grey_m"); rect(im, lx, S+5, lx, STAND_Y-1, "grey_l")
    rect(im, lx-1, STAND_Y, lx+2, STAND_Y, "grey_d")
for (a, b) in [(150, 182), (183, 203)]:
    rect(im, a+1, S-10, b-1, S-2, "pb"); rect(im, a+2, S-11, b-2, S-11, "pb_l")
    rect(im, a+1, S-10, a+1, S-3, "pb_l"); rect(im, b-1, S-9, b-1, S-2, "pb_d")
    rect(im, a+3, S-8, b-3, S-8, "pb_l"); rect(im, a+3, S-5, b-3, S-5, "pb_d")
    rect(im, a, S, b, S+2, "pb"); rect(im, a, S, b, S, "pb_l"); rect(im, a, S+2, b, S+2, "pb_d")
    rect(im, b, S+1, b, S+2, "pb_d"); rect(im, a, S+1, a, S+1, "pb_l")
    rect(im, a+2, S-1, b-2, S-1, "pb_d")
save_asset("shelter", "seats", im, anchor=(0, 0), notes="Bench x150-203, seat top y=SEAT_Y (188), legs to y196. Module 1 x150-182 fits the seated adult.")
