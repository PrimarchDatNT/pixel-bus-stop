"""Gust particles for the season-change transition (bản 6c): a leaf (5x4) and a petal (4x4), 4 tumble frames each.

Drawn once in a neutral ramp (leaf_l / leaf / leaf_d and bl_hl / bl_l / bl); compose/transition.py recolours them for
the season that blows in (peach petals for Tết, bougainvillea + green leaves for summer, yellow-orange leaves for
Trung Thu, red bàng leaves for winter).

    .venv/bin/python assets/src_gif/season/gust.py      # -> assets/out_gif/actors/gust_leaf, gust_petal
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.px_gif import *  # noqa: E402,F403

LEAF = {"a": "leaf_l", "b": "leaf", "c": "leaf_d"}
LEAF_FRAMES = [
    ["..aa.",          # flat, pointing right, lit upper edge
     ".abbb",
     "cbbb.",
     ".cc.."],
    ["...ab",          # tipped up on its side
     "..abb",
     ".bbc.",
     "cc..."],
    [".....",          # edge-on: a thin sliver
     "aabbc",
     ".....",
     "....."],
    [".cc..",          # flipped: the darker underside shows
     "cbbc.",
     ".bbbb",
     "..bc."],
]
PETAL = {"a": "bl_hl", "b": "bl_l", "c": "bl"}
PETAL_FRAMES = [
    [".ab.",
     "abbb",
     ".bbc",
     "..c."],
    ["..a.",
     ".abb",
     "abbc",
     ".c.."],
    ["....",
     "abbc",
     "....",
     "...."],
    [".a..",
     "bba.",
     "cbb.",
     ".c.."],
]


def build():
    leaf = [grid(f, LEAF) for f in LEAF_FRAMES]
    petal = [grid(f, PETAL) for f in PETAL_FRAMES]
    save_asset("actors", "gust_leaf", leaf, fps=8, anchor=(2, 2),
               notes="transition gust leaf, neutral green ramp (recoloured per season in compose/transition.py)")
    save_asset("actors", "gust_petal", petal, fps=8, anchor=(2, 2),
               notes="transition gust petal, neutral pink ramp (recoloured per season in compose/transition.py)")
    return leaf, petal


if __name__ == "__main__":
    build()
    print("ok")
