from _c import *
im = canvas()
# pillars
for x0 in (116, 230):
    rect(im, x0, 151, x0+2, STAND_Y-1, "grey_m"); rect(im, x0, 151, x0, STAND_Y-1, "grey_hl")
    rect(im, x0+1, 151, x0+1, STAND_Y-1, "grey_l"); rect(im, x0+2, 151, x0+2, STAND_Y-1, "grey_d")
    rect(im, x0-1, STAND_Y-2, x0+3, STAND_Y-1, "grey"); rect(im, x0-1, STAND_Y, x0+3, STAND_Y, "grey_d")
    rect(im, x0-1, STAND_Y-2, x0+3, STAND_Y-2, "grey_l")
# roof slab
x0, x1 = SHELTER_X0, SHELTER_X1
rect(im, x0, 146, x1, 146, "white"); rect(im, x0, 147, x1, 148, "grey_hl")
rect(im, x0, 149, x1, 149, "grey_l"); rect(im, x0, 150, x1, 150, "grey_m")
rect(im, x0, 146, x0, 150, "white"); rect(im, x1, 147, x1, 150, "grey")
rect(im, x0+1, 151, x1-1, 151, "grey_d")       # shade band under the slab
rect(im, x0+3, 152, x1-3, 152, "grey_l")
# header board
bx0, bx1, by0, by1 = 182, 229, 152, 165
rect(im, bx0, by0, bx1, by1, "pb_d"); rect(im, bx0, by0, bx1, by0, "pb"); rect(im, bx0, by1, bx1, by1, "navy")
rect(im, bx0, by0, bx0, by1, "pb")
text(im, bx0, by0+6, "TRẠM XE BUÝT", "white")
# side marker: small bus roundel on right of fascia
save_asset("shelter", "shelter_front", im, anchor=(0, 0), notes="Pillars x116-118 & 230-232, slab y146-150, header board x182-229 y152-165.")
