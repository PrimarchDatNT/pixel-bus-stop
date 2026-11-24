"""Cut chosen candidates out with rembg, flip to target facing, trim, save RGBA finals + dark/grey check.
FINAL = name -> (candidate file stem, flip, model). Usage: cut_vehicles.py [name ...]"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from rembg import remove, new_session
ROOT = Path(__file__).resolve().parents[3]
C = ROOT / "assets/out_v3/sprites/vehicles/_cand/v3"; O = ROOT / "assets/out_v3/sprites/vehicles"
FINAL = {  # name: (candidate, flip, model, erode_px)
 "bus_L": ("bus_L_b3_d75_501_0", False, "isnet-general-use", 1),
 "moto_man_R": ("moto_man_R_501_1", True, "isnet-general-use", 1),
 "moto_sun_R": ("moto_sun_R_501_0", True, "isnet-general-use", 1),
 "moto_puffer_R": ("moto_puffer_R_501_1", True, "isnet-general-use", 1),
 "bike_peach_R": ("bike_peach_R_501_1", True, "isnet-general-use", 1),
 "bike_daisy_R": ("bike_daisy_R_501_1", False, "isnet-general-use", 1),
}
FILL = {'bike_daisy_R': False, 'bike_peach_R': False, 'moto_man_R': False, 'moto_puffer_R': False, 'bus_L': False}
try: FINAL.update(__import__("final_extra").EXTRA)
except ImportError: pass

def cut(name):
    stem, flip, model, er = FINAL[name]
    im = Image.open(C / f"{stem}.png").convert("RGB")
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    out = remove(im, session=new_session(model), post_process_mask=True).convert("RGBA")
    a = np.array(out)
    al = a[..., 3]
    if FILL.get(name, True):  # rembg treats big white clothing/body panels as background -> fill enclosed holes
        m = ndi.binary_fill_holes(al > 128); al = np.where(m, np.maximum(al, 255 * m), al).astype(np.uint8)
        a[..., :3][(a[..., 3] < 128) & m] = np.array(im)[(a[..., 3] < 128) & m]
    if er: al = ndi.grey_erosion(al, size=(2 * er + 1, 2 * er + 1))
    a[..., 3] = al
    # kill near-white fringe on semi-transparent edge pixels
    rgb = a[..., :3].astype(int); edge = (al < 250) & (rgb.min(-1) > 225)
    a[..., 3][edge] = 0
    out = Image.fromarray(a); out = out.crop(out.getbbox()); out.save(O / f"{name}.png")
    return out

if __name__ == "__main__":
    names = sys.argv[1:] or list(FINAL)
    for n in names: print(n, cut(n).size, flush=True)
    # check sheet
    ims = [Image.open(O / f"{n}.png") for n in names]
    for tag, col in (("dark", (25, 25, 35)), ("grey", (128, 128, 128))):
        W = 4; cell = 420
        S = Image.new("RGB", (W * cell, ((len(ims) + W - 1) // W) * cell), col)
        for k, im in enumerate(ims):
            t = im.copy(); t.thumbnail((cell - 10, cell - 10)); S.paste(t, ((k % W) * cell + 5, (k // W) * cell + 5), t)
        S.save(ROOT.parent / f"pixel-bus-stop/assets/out_v3/sprites/vehicles/_cand/v3/_check_{tag}.png")
