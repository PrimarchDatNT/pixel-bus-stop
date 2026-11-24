from common import *
import sky_ground as sg, house as hs
import subprocess

def build_all():
    save_asset("env", "sky", sg.sky(), anchor=(0, 0))
    save_asset("env", "distance", sg.distance(), anchor=(0, 0))
    save_asset("env", "house", hs.build(), anchor=(0, 0))
    save_asset("env", "ground", sg.ground(), anchor=(0, 0))

def composite(path=None, over_mock=True):
    base = Image.new("RGBA", (W, H))
    for n in ["sky", "distance", "house", "ground"]:
        f = Image.open(pathlib.Path(__file__).resolve().parents[3] / "assets/out_gif/env" / f"{n}.png").convert("RGBA")
        base.alpha_composite(f)
    if over_mock:
        mk = Image.open(pathlib.Path(__file__).resolve().parents[3] / "assets/out_gif/_mock/mock3.png").convert("RGBA")
        keep = {(220, 95, 157), (178, 63, 125), (63, 68, 73), (93, 100, 107), (159, 195, 220), (193, 98, 120), (232, 145, 63)}
        mp = mk.load(); bp = base.load()
        for y in range(H):
            for x in range(W):
                if mp[x, y][:3] in keep:
                    bp[x, y] = mp[x, y]
    return base

if __name__ == "__main__":
    build_all()
    comp = composite()
    outd = pathlib.Path(__file__).resolve().parents[3] / "assets/out_gif/env/_preview"
    outd.mkdir(parents=True, exist_ok=True)
    comp.resize((W * 3, H * 3), Image.NEAREST).convert("RGB").save(outd / "env_composite@3x.png")
    comp.crop((140, 24, 310, 190)).resize((170 * 5, 166 * 5), Image.NEAREST).convert("RGB").save("review/gif_style/_sheets/house5.png")
