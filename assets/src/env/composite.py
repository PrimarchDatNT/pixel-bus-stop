import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px import *; from tools.layout import *; from tools.mockbg import mock_scene, place, save_mock
from PIL import Image
def ld(n): return Image.open(OUT / "env" / f"{n}.png").convert("RGBA")
def frame(n, i=0):
    im = ld(n); fw = im.height and __import__("json").load(open(OUT / "env" / f"{n}.json"))["frameW"]
    return im.crop((i * fw, 0, (i + 1) * fw, im.height))
def comp(season="ha", night=False, wet=False):
    bg = new(W, H)
    rect(bg, 0, 0, W - 1, H - 1, "sky_l")
    bg.alpha_composite(frame("cloud_l1"), (30, 14)); bg.alpha_composite(frame("cloud_l2"), (300, 30)); bg.alpha_composite(frame("cloud_s1"), (200, 8))
    bg.alpha_composite(ld("buildings"), (0, 32))
    if night: bg.alpha_composite(ld("buildings_lights"), (0, 32))
    bg.alpha_composite(ld("ground"), (0, 158))
    if wet: bg.alpha_composite(ld("ground_wet"), (0, 158))
    bg.alpha_composite(ld("pole_wires"), (0, 0))
    bg.alpha_composite(ld("tree_trunk"), (350, 30))
    bg.alpha_composite(frame(f"tree_canopy_{season}"), (350, 30))
    bg.alpha_composite(ld("lamp"), (288, 90))
    if night: bg.alpha_composite(ld("lamp_lit"), (288, 90))
    # shelter silhouette for context
    rect(bg, SHELTER_X0, SHELTER_ROOF_TOP_Y, SHELTER_X1, SHELTER_ROOF_UNDER_Y, "slate")
    for x in (SHELTER_X0 + 2, SHELTER_X1 - 4): rect(bg, x, SHELTER_ROOF_UNDER_Y, x + 2, SHELTER_FRONT_BASE_Y, "slate")
    rect(bg, 236, WAIT_BASE_Y - ADULT_H + 1, 240, WAIT_BASE_Y, "ink")
    return bg
if __name__ == "__main__":
    save_mock(comp(), "env", "env_composite")
    save_mock(comp("thu", night=True), "env", "env_composite_night")
