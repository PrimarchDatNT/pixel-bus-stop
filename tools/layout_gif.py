"""Scene geometry for the GIF-style styleframe, composition B (23/11 after review). All values are 1x logical pixels.

Canvas 384x216, rendered at 5x -> 1920x1080. Built like refs/pinterest_pixel_shop.gif: ONE hero building, ONE hero
bloom mass, open sky with breathing room, pale distance, props only at the feet. (The first attempt with a row of
five tube houses is archived in assets/out_gif_a + tools/layout_gif_a.py.)

x (left -> right)
  0-190 ....... bougainvillea mass towering over the bus shelter (x 36-176) and climbing the house's left side
  150-300 ..... HERO: old-quarter Hanoi shophouse (2 floors + attic, tiled roof), shop on the ground floor
  300-384 ..... open sky; pale distant city + Long Biên bridge; bus-stop sign; trà đá corner at the feet
y (top -> bottom)
  0-~60 ....... sky (clouds), house roof ridge ~46, dormer up to ~30
  140-178 ..... distant skyline / bridge (haze colours), only visible right of the house
  186-199 ..... sidewalk (things stand on y=196)
  200-202 ..... curb
  203-215 ..... road lane (wheels touch y=213)
"""

W, H = 384, 216
RENDER_SCALE = 5

# ground
SIDEWALK_Y0, SIDEWALK_Y1 = 186, 199
STAND_Y = 196
CURB_Y0, CURB_Y1 = 200, 202
ROAD_Y0, ROAD_Y1 = 203, 215
WHEEL_Y = 213

# hero house (old-quarter shophouse)
HOUSE_X0, HOUSE_X1 = 150, 300
HOUSE_WALL_TOP_Y = 74        # wall top under the eaves
HOUSE_BASE_Y = 186           # meets the sidewalk
ROOF_RIDGE_Y = 46            # tiled roof from ridge 46 down to eaves ~76, overhang ~8 px each side
DORMER = (206, 30, 230, 48)  # attic dormer / small window box on the roof (x0, y0, x1, y1)
BALCONY_Y = 120              # first-floor balcony slab top (railing above it, ~10 px)
SHOP_Y0 = 128                # ground-floor shop opening top (signboard sits just above/at it)
SHOP_VISIBLE_X = (178, 296)  # part of the shop front not hidden by the shelter
SHOPKEEPER_SPOT = (236, 176) # shopkeeper behind the counter: anchor = bottom-centre of the visible upper body
BALCONY_SPOT = (262, 120)    # grandma watering plants on the balcony: anchor = feet on the slab
BIRDCAGE_SPOT = (196, 98)    # hanging bird cage under the eaves / balcony ceiling

# bus shelter + bougainvillea (left)
SHELTER_X0, SHELTER_X1 = 36, 176
SHELTER_ROOF_TOP_Y, SHELTER_ROOF_UNDER_Y = 150, 154
SEAT_Y = 188                 # seat top (~0.45 m); legs to STAND_Y
WAITER_SPOT = (96, 187)      # seated woman: anchor = thigh row on the seat
BOUGAINVILLEA_PLANTER = (22, 36)
CANOPY_BOX = (6, 40, 196, 162)   # rough extent of the bloom mass incl. the part climbing the house
CAT_SPOT = (128, 150)        # black cat sitting on the shelter roof, in front of the bloom (y = roof top)

# right side
STOP_SIGN_X = 312
TRA_DA_X = 322               # trà đá corner: tiny table + thermos + stools, x 322-372
OLDMAN_SPOT = (352, 196)
DOG_SPOT = (200, 196)        # yellow dog lying on the sidewalk in front of the shop

# scale guide (cute GIF proportions: big heads, ~3.5 heads tall)
ADULT_H = 30                 # head ~9 px tall, ~8 px wide
CHILD_H = 22
CAT_LOAF = (14, 9)
DOG_LIE = (24, 11)
MOTORBIKE_WH = (34, 20)
BUS_WH = (196, 56)
