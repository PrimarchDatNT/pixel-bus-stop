"""Rebuild every sprite the current video (bản 6, café + park) uses, in dependency order.

    .venv/bin/python tools/build_assets.py            # all groups
    .venv/bin/python tools/build_assets.py park bus   # only scripts whose path contains one of these words

Each generator script draws its sprites in code (ASCII grids / rect / ellipse on the locked palette in tools/px_gif.py)
and writes assets/out_gif/<group>/<name>.png (horizontal frame strip) + <name>.json (fps, anchor, states, notes)
through tools.px_gif.save_asset(). Older generations (assets/src_gif/env, shelter, actors) are kept for history only.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

SCRIPTS = [
    # environment of the old house scene (sky / distance / ground are still the base layers)
    "assets/src_gif/env_b/run.py",
    # bus shelter
    "assets/src_gif/shelter_b/back.py",
    "assets/src_gif/shelter_b/front.py",
    "assets/src_gif/shelter_b/seats.py",
    "assets/src_gif/shelter_b/stop_sign.py",
    "assets/src_gif/shelter_b/petals.py",
    "assets/src_gif/shelter_b/bloom_lobes.py",
    # characters, animals, props, bus
    "assets/src_gif/actors_b/chars.py",
    "assets/src_gif/actors_b/cat_black.py",
    "assets/src_gif/actors_b/props.py",
    "assets/src_gif/actors_b/bus.py",
    # season sprites + skies (the moon overlay for the soft sky comes from skies.py)
    "assets/src_gif/season/tet.py",
    "assets/src_gif/season/thu.py",
    "assets/src_gif/season/skies.py",
    # park scene: kiosk (café / tạp hóa), trees, lawn, towers, tabby cat, cat on the bench, flower bike
    "assets/src_gif/park/park.py",
    "assets/src_gif/park/people.py",
    "assets/src_gif/park/bike.py",
]


def main():
    want = sys.argv[1:]
    (ROOT / "review/gif_style/_sheets").mkdir(parents=True, exist_ok=True)   # preview sheets land here
    for s in SCRIPTS:
        if want and not any(w in s for w in want):
            continue
        print("==>", s, flush=True)
        subprocess.run([PY, str(ROOT / s)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    print("assets ok -> assets/out_gif/")


if __name__ == "__main__":
    main()
