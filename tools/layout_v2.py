"""Scene geometry for STYLE v2 (32-bit glossy). Same composition as layout.py scaled x4/3.

Canvas 640x360, rendered at integer 3x -> 1920x1080. No electric pole (removed by client).
"""

W, H = 640, 360
RENDER_SCALE = 3

BUILDING_BASE_Y = 216
FAR_SIDEWALK_Y0, FAR_SIDEWALK_Y1 = 211, 239
FAR_CURB_Y0, FAR_CURB_Y1 = 240, 244
ROAD_Y0, ROAD_Y1 = 245, 316
LANE_DIVIDER_Y = 280
FAR_LANE_BASE_Y = 275          # wheel contact, far lane (R->L)
NEAR_LANE_BASE_Y = 311         # wheel contact, near lane (L->R)
NEAR_CURB_Y0, NEAR_CURB_Y1 = 317, 321
NEAR_SIDEWALK_Y0, NEAR_SIDEWALK_Y1 = 322, 359

SHELTER_X0, SHELTER_X1 = 213, 372      # 160 px wide
SHELTER_ROOF_TOP_Y, SHELTER_ROOF_UNDER_Y = 163, 171
SHELTER_BACK_BASE_Y, SEAT_BASE_Y, SHELTER_FRONT_BASE_Y = 224, 228, 232
LAMP_X, LAMP_BASE_Y = 395, 227
TREE_X, TREE_BASE_Y = 557, 221
WAIT_BASE_Y, WALK_FAR_BASE_Y, CAT_BASE_Y = 229, 237, 352

ADULT_H = 40          # head ~9 px
BUS_SIZE = (226, 70)
SEDAN_SIZE = (96, 32)
MOTO_SIZE = (43, 37)
CAT_FRAME = (64, 40)  # foreground cat, closer to camera

# Style-test frame placements (bottom-centre anchors unless noted)
TEST = {
    "buildings_tl": (0, 40),            # a 640x176 facade strip, bottom at BUILDING_BASE_Y
    "shelter_center_x": 292,
    "bus_L_x": 548,                     # far lane, partly cut by the right edge
    "cat_x": 150,                       # near sidewalk
}
