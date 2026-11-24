from _c import *
im = canvas()
for x0 in (37, 171):
    rect(im, x0, 154, x0 + 2, STAND_Y - 1, "grey_m"); rect(im, x0, 154, x0, STAND_Y - 1, "grey_hl")
    rect(im, x0 + 1, 154, x0 + 1, STAND_Y - 1, "grey_l"); rect(im, x0 + 2, 154, x0 + 2, STAND_Y - 1, "grey_d")
    rect(im, x0 - 1, STAND_Y - 2, x0 + 3, STAND_Y - 1, "grey"); rect(im, x0 - 1, STAND_Y, x0 + 3, STAND_Y, "grey_d")
    rect(im, x0 - 1, STAND_Y - 2, x0 + 3, STAND_Y - 2, "grey_l")
x0, x1 = SHELTER_X0, SHELTER_X1
t, u = SHELTER_ROOF_TOP_Y, SHELTER_ROOF_UNDER_Y
rect(im, x0, t, x1, t, "white"); rect(im, x0, t + 1, x1, t + 1, "grey_hl")
rect(im, x0, t + 2, x1, t + 2, "grey_l"); rect(im, x0, t + 3, x1, t + 3, "grey_m"); rect(im, x0, u, x1, u, "grey_d")
rect(im, x1, t + 1, x1, u, "grey"); rect(im, x0, t, x0, u - 1, "white")
# (bản 6c: the 'TRẠM XE BUÝT' header board was removed at the client's request)
save_asset("shelter", "shelter_front", im, anchor=(0, 0), notes="Pillars x37-39 & 171-173, roof slab x36-176 y150-154 (no header board since 6c).")
