from common import *
from PIL import Image
import json
def load(name, f=0):
    m = json.load(open(OUT / G / f"{name}.json")); im = Image.open(OUT / G / f"{name}.png")
    fw = m["frameW"]; return im.crop((f * fw, 0, (f + 1) * fw, m["frameH"])), tuple(m["anchor"])
bg = mock_scene()
bus, a = load("bus_L", 2)
# front door centre in bus_L sprite = 169-(131+7)=31
place(bg, bus, 222 - 31 + a[0], FAR_LANE_BASE_Y, anchor=a)
for n, x in [("sedan_red_R", 120), ("moto_man_R", 190), ("moto_sun_ha_R", 300), ("moto_peach_R", 380)]:
    s, a = load(n); place(bg, s, x, NEAR_LANE_BASE_Y, anchor=a)
s, a = load("sedan_white_R"); place(bg, s, 250, NEAR_LANE_BASE_Y, anchor=a)
s, a = load("taxi_L"); place(bg, s, 60, FAR_LANE_BASE_Y, anchor=a)
s, a = load("bike_daisy_dong_R"); place(bg, s, 450, NEAR_LANE_BASE_Y, anchor=a)
save_mock(bg, G, "placement_check")
