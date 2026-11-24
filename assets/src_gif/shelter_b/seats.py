"""Bus-shelter seating (bản 6c, 24/11/2026): two slatted WOODEN benches on dark iron frames (replaces the blue plastic
seat modules; the old version is in git-less backup scratchpad/seats_v5.py).

Bench A x44-112 (the waiting woman sits at WAITER_SPOT x96), bench B x120-168 (the cat shelters here in the rain).
Seat top y = SEAT_Y (188), backrest planks y177-179 and y182-184, legs to STAND_Y (196).
"""
from _c import *

im = canvas()
S = SEAT_Y
HL, BASE, SH, GAP = "tc_l", "or_d", "tc_d", "trunk_d"     # warm varnished wood
IRON, IRON_L = "grey_k", "grey_d"
BENCHES = [(44, 112, (78,)), (120, 168, ())]               # (x0, x1, middle legs)


def plank(x0, x1, y):
    """3-row plank seen front-on: lit top edge, body, shaded underside; small end grain."""
    rect(im, x0, y, x1, y, HL)
    rect(im, x0, y + 1, x1, y + 1, BASE)
    rect(im, x0, y + 2, x1, y + 2, SH)
    put(im, x1, y + 1, SH)
    for x in range(x0 + 9, x1 - 3, 17):                      # faint board joints / screws
        put(im, x, y + 1, SH)


for x0, x1, mids in BENCHES:
    # iron back posts + legs (drawn first: planks sit in front of the posts)
    for lx in (x0 + 2, x1 - 3) + mids:
        rect(im, lx, S - 13, lx + 1, S - 1, IRON)
        put(im, lx, S - 13, IRON_L)
    for lx in (x0 + 2, x1 - 3) + mids:                      # legs, slightly splayed feet
        rect(im, lx, S + 3, lx + 1, STAND_Y - 1, IRON); put(im, lx, S + 3, IRON_L)
        rect(im, lx - 1, STAND_Y, lx + 2, STAND_Y, IRON)
    # backrest: two planks with a dark gap between them
    plank(x0 + 1, x1 - 1, S - 11)
    plank(x0 + 1, x1 - 1, S - 6)
    rect(im, x0 + 3, S - 8, x1 - 3, S - 7, GAP)
    rect(im, x0 + 3, S - 3, x1 - 3, S - 1, GAP)              # shadow between back and seat
    # seat: top surface (lit band) + thick front plank
    rect(im, x0, S, x1, S, HL)
    rect(im, x0, S + 1, x1, S + 1, BASE)
    rect(im, x0, S + 2, x1, S + 2, SH)
    put(im, x0, S + 1, HL)
    # iron armrests at both ends (small curl)
    for ax, d in ((x0, 1), (x1, -1)):
        rect(im, ax, S - 5, ax, S - 1, IRON)
        put(im, ax + d, S - 5, IRON); put(im, ax, S - 6, IRON_L)
    # stretcher bar under the seat
    rect(im, x0 + 3, S + 6, x1 - 3, S + 6, IRON)

save_asset("shelter", "seats", im, anchor=(0, 0),
           notes="Two wooden benches on iron frames x44-112 (woman at x96) and x120-168. Seat top y=188, legs to 196.")
