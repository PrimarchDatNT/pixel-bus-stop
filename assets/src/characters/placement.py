from lib import *
import json
from PIL import Image

def load(name, state=None, idx=0):
    d = OUT / "characters"
    m = json.loads((d / f"{name}.json").read_text())
    strip = Image.open(d / f"{name}.png").convert("RGBA")
    fw, fh = m["frameW"], m["frameH"]
    frames = [strip.crop((i * fw, 0, (i + 1) * fw, fh)) for i in range(m["frames"])]
    return frames, m

def pick(name, i=0):
    fr, m = load(name)
    return fr[i % len(fr)], m

bg = mock_scene()
def P(name, x, y, i=0):
    f, m = pick(name, i)
    ax, ay = m["anchor"]
    place(bg, f, x, y, anchor=(ax, ay))

P("walk_aodai_xuan_R", 70, WALK_FAR_BASE_Y, 0)
P("walk_man_xuan_L", 110, WALK_FAR_BASE_Y, 2)
P("walk_umbrella_ha_R", 320, WALK_FAR_BASE_Y, 1)
P("walk_kid_thu_L", 360, WALK_FAR_BASE_Y, 3)
P("walk_puffer_dong_R", 390, WALK_FAR_BASE_Y, 4)
P("walk_schoolgirl_ha_L", 150, WALK_FAR_BASE_Y, 1)
P("run_rain_ha_R", 255, WALK_FAR_BASE_Y, 2)
P("sit_phone_ha_R", 190, WAIT_BASE_Y, 0)
P("sit_elder_R", 212, WAIT_BASE_Y, 1)
P("stand_wait_ha_R", 245, WAIT_BASE_Y, 0)
P("dog_L", 30, WALK_FAR_BASE_Y, 2)
P("cat_R", 360, CAT_BASE_Y, 13)
P("cat_L", 100, CAT_BASE_Y, 3)
P("swallow_R", 120, 40, 1)
P("sparrow_L", 300, 60, 0)
P("sparrow_R", 330, 150, 4)
save_mock(bg, "characters", "placement_check")
