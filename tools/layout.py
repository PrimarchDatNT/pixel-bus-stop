"""Scene geometry shared by every asset + the compositor. All values are 1x logical pixels.

Canvas 480x270, rendered at 4x -> 1920x1080. Camera: fixed, standing on the NEAR sidewalk,
looking straight across a 2-lane street at a bus shelter on the FAR sidewalk.
Projection: flat side view (orthographic) with a slight top-down tilt, so the tops of
sidewalks / road are visible as horizontal bands; buildings and vehicles are pure side view.

y (top -> bottom)
  0 ............ sky (always some visible above rooftops)
  ~32-110 ...... building rooftops (row of Hanoi tube houses, drawn at ~0.75x = further back)
  122-128 ...... shelter roof slab (top 122, underside 128); bougainvillea canopy 90-135
  158-179 ...... FAR sidewalk surface (shelter, lamp, tree, pedestrians stand here)
  180-183 ...... far curb face
  184-237 ...... road; lane divider dashes at y=210..211
                  far lane  -> traffic moves RIGHT->LEFT, wheels touch y=206 (bus stops here)
                  near lane -> traffic moves LEFT->RIGHT, wheels touch y=233
  238-241 ...... near curb
  242-269 ...... NEAR sidewalk (foreground; the cat lives here, drawn at 1.6x scale)
"""

W, H = 480, 270
RENDER_SCALE = 4  # -> 1920x1080

# --- ground bands
BUILDING_BASE_Y = 162          # bottom edge of the building row (hidden behind far sidewalk)
FAR_SIDEWALK_Y0 = 158          # back edge of far sidewalk surface
FAR_SIDEWALK_Y1 = 179          # front edge (top of curb)
FAR_CURB_Y0, FAR_CURB_Y1 = 180, 183
ROAD_Y0, ROAD_Y1 = 184, 237
LANE_DIVIDER_Y = 210           # 2px tall dashes: 12 on / 10 off
FAR_LANE_BASE_Y = 206          # lowest wheel pixel, far lane (R->L)
NEAR_LANE_BASE_Y = 233         # lowest wheel pixel, near lane (L->R)
NEAR_CURB_Y0, NEAR_CURB_Y1 = 238, 241
NEAR_SIDEWALK_Y0, NEAR_SIDEWALK_Y1 = 242, 269

# --- bus shelter (hero)
SHELTER_X0, SHELTER_X1 = 160, 279      # 120px wide
SHELTER_ROOF_TOP_Y = 122
SHELTER_ROOF_UNDER_Y = 128
SHELTER_BACK_BASE_Y = 168              # rear panel / ad box feet
SEAT_BASE_Y = 171                      # plastic seats feet
SHELTER_FRONT_BASE_Y = 174             # front pillar feet
BOUGAINVILLEA_PLANTER_X = 150          # planter box centre, left of shelter; vine climbs left pillar
BUS_DOOR_STOP_X = 222                  # bus front door x when stopped at the shelter

# --- props on the far sidewalk
POLE_X, POLE_BASE_Y = 52, 165          # concrete electric pole, wires sag across the top of frame
LAMP_X, LAMP_BASE_Y = 296, 170         # street lamp, head around y~100
TREE_X, TREE_BASE_Y = 418, 166         # cay bang (Terminalia) trunk centre, canopy ~x350-480, y~30-120
VENDOR_X, VENDOR_BASE_Y = 334, 176     # seasonal street vendor spot (winter roasted corn, etc.)

# --- actor baselines (feet)
WAIT_BASE_Y = 172                      # people waiting / sitting inside the shelter
WALK_FAR_BASE_Y = 178                  # pedestrians walking along the front of the far sidewalk
CAT_BASE_Y = 264                       # foreground cat

# --- scale guide (1 m ~ 16.5 px at the far sidewalk)
ADULT_H = 28        # adult incl. hair/hat, head ~6-7px
CHILD_H = 20
BUS_SIZE = (170, 52)        # incl. roof + LED route sign
SEDAN_SIZE = (72, 24)
VAN_SIZE = (76, 32)
MOTO_SIZE = (32, 28)        # motorbike + rider
BICYCLE_SIZE = (34, 30)     # bicycle + rider (+ cargo can exceed)
CAT_FRAME = (48, 30)        # foreground cat at 1.6x
BIRD_SIZE = (9, 7)

# --- draw order, back -> front (compositor contract)
Z_ORDER = [
    "sky", "celestial", "clouds", "buildings", "buildings_lights", "ground", "wires_pole", "tree_trunk",
    "tree_canopy", "lamp", "shelter_back", "seats", "waiting_people", "shelter_front",
    "bougainvillea", "shelter_decor", "far_walkers", "far_lane", "near_lane", "near_sidewalk_props",
    "foreground_actors", "weather_fx", "grading",
]

SEASONS = {
    "xuan": "Spring / Tet - soft morning, light drizzle (mua bui), red lanterns + couplets, swallows",
    "ha":   "Summer - harsh noon sun + heat haze, bougainvillea in full bloom, sudden downpour (mua rao)",
    "thu":  "Autumn - golden afternoon wind, petals + yellow leaves blown away, Mid-Autumn lantern night",
    "dong": "Winter (Hanoi) - grey fine drizzle + fog, puffer coats, roasted-corn vendor, daisy bicycle; "
            "ends with peach-blossom motorbikes heading home for Tet -> loops back to spring",
}
