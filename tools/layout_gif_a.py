"""Scene geometry for the GIF-style styleframe (v4). All values are 1x logical pixels.

Canvas 384x216, rendered at 5x -> 1920x1080. Camera close and front-on (orthographic elevation),
like refs/pinterest_pixel_shop.gif: the bus shelter + its bougainvillea are the hero, a row of Hanoi
tube houses stands right behind the sidewalk, a big tree frames the left, one road lane runs along
the bottom edge.

y (top -> bottom)
  0-~95 ......... sky; pale distant Hanoi skyline silhouette 70-150 (haze colours)
  ~8-186 ........ tube-house row (rooftops vary 8..60), facades touch the sidewalk at y=186
  104-160 ....... bougainvillea canopy over the shelter roof (roof slab 146-150), climbing onto H1's balcony
  186-199 ....... sidewalk surface (people, shelter, stools stand on y=196)
  200-202 ....... curb
  203-215 ....... road lane (vehicles' wheels touch y=213), traffic runs both ways
"""

W, H = 384, 216
RENDER_SCALE = 5

# ground
FACADE_BASE_Y = 186        # houses' ground-floor bottom edge (behind the sidewalk)
SIDEWALK_Y0, SIDEWALK_Y1 = 186, 199
STAND_Y = 196              # feet / furniture contact line for things on the sidewalk
CURB_Y0, CURB_Y1 = 200, 202
ROAD_Y0, ROAD_Y1 = 203, 215
WHEEL_Y = 213              # lowest wheel pixel of vehicles on the road

# tube houses (x0, x1, roof_top_y, floors) — left to right; house 0 is partly behind the tree
HOUSES = [
    (60, 124, 92, 2),      # H0: pale-blue, low, partly hidden by tree + bougainvillea
    (124, 190, 58, 3),     # H1: yellow ochre; bougainvillea climbs onto its 1st-floor balcony
    (190, 244, 22, 5),     # H2: dusty pink, tallest, balconies with plants, laundry
    (244, 316, 80, 3),     # H3: cream, ground floor = tạp hóa (shop shelves, shopkeeper)
    (316, 384, 44, 4),     # H4: yellow, cut by the right frame edge
]
# sky + the pale distant skyline show above H0, H1, H3 and between roof heights

# bus shelter (hero) — sits in front of H1/H2, on the sidewalk
SHELTER_X0, SHELTER_X1 = 112, 236      # 124 px wide incl. roof overhang
SHELTER_ROOF_TOP_Y, SHELTER_ROOF_UNDER_Y = 146, 150   # ~2.6 m roof vs 1.65 m adult (30 px)
SHELTER_BASE_Y = STAND_Y
SEAT_Y = 188                           # seat top surface (~0.45 m); seat legs to STAND_Y
BOUGAINVILLEA_PLANTER = (100, 112)     # x range of the planter box at the shelter's left foot
CANOPY_BOX = (86, 104, 248, 160)       # rough extent of the bloom mass (x0, y0, x1, y1)
STOP_SIGN_X = 244                      # bus-stop sign post, sign plate around y 128-146

# left tree (sấu / bàng): trunk centre + canopy extent
TREE_TRUNK_X = 34
TREE_CANOPY_BOX = (0, 0, 104, 120)

# props
TRA_DA_X = 262              # trà đá stall: thermos, low table, 3 plastic stools (x 262-318)
MOTORBIKE_X = 336           # parked cub-style motorbike, front wheel to the right
CAT_SPOT = (214, 146)       # cat sleeping on the shelter roof edge, right end clear of bloom (y = roof top)

# scale guide (heights in px)
ADULT_H = 30                # head 7 px
CHILD_H = 21
CAT_SIT_H = 11
MOTORBIKE_WH = (34, 20)
BUS_WH = (196, 56)
