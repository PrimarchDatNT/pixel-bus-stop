from common import *
from PIL import Image
OUTD = OUT / GROUP

def ld(name, f=0):
    im = Image.open(OUTD / f"{name}.png").convert("RGBA")
    import json
    m = json.loads((OUTD / f"{name}.json").read_text())
    w = m["frameW"]
    return im.crop((f * w, 0, (f + 1) * w, im.height))

def composite(season=None, frame=0, parts=("back", "seats", "front", "boug", "decor"), name=None, crop=None, scale=3):
    bg = mock_scene()
    # replace mock shelter with clean sidewalk behind it
    rect(bg, SHELTER_X0 - 2, SHELTER_ROOF_TOP_Y - 1, SHELTER_X1 + 6, SHELTER_FRONT_BASE_Y, "x") if False else None
    return bg
