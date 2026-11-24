"""Flat blocking background so each asset group can check scale/placement in context
before the real environment exists.

    from tools.mockbg import mock_scene, place, save_mock
    bg = mock_scene()
    place(bg, sprite_frame, x=222, base_y=FAR_LANE_BASE_Y)      # bottom-centre anchor
    save_mock(bg, "vehicles", "placement_check")                 # -> assets/out/vehicles/_preview/placement_check@4x.png
"""
from __future__ import annotations

from PIL import Image

from tools.layout import *
from tools.px import OUT, c, new, rect, line, put


def mock_scene() -> Image.Image:
    img = new(W, H)
    rect(img, 0, 0, W - 1, BUILDING_BASE_Y, "sky_l")
    # blocky building row
    xs = [0, 62, 120, 190, 250, 318, 380, 430, W]
    tops = [70, 52, 80, 60, 74, 48, 66, 58]
    cols = ["sand", "ochre", "mint", "sand", "grey_l", "ochre", "sand", "mint"]
    for i in range(len(xs) - 1):
        rect(img, xs[i], tops[i], xs[i + 1] - 1, BUILDING_BASE_Y, cols[i])
    rect(img, 0, FAR_SIDEWALK_Y0, W - 1, FAR_SIDEWALK_Y1, "stone_l")
    rect(img, 0, FAR_CURB_Y0, W - 1, FAR_CURB_Y1, "stone")
    rect(img, 0, ROAD_Y0, W - 1, ROAD_Y1, "stone_d")
    for x in range(0, W, 22):
        rect(img, x, LANE_DIVIDER_Y, x + 11, LANE_DIVIDER_Y + 1, "grey_l")
    rect(img, 0, NEAR_CURB_Y0, W - 1, NEAR_CURB_Y1, "stone")
    rect(img, 0, NEAR_SIDEWALK_Y0, W - 1, NEAR_SIDEWALK_Y1, "stone_l")
    # shelter silhouette
    rect(img, SHELTER_X0, SHELTER_ROOF_TOP_Y, SHELTER_X1, SHELTER_ROOF_UNDER_Y, "slate")
    for x in (SHELTER_X0 + 2, SHELTER_X1 - 4):
        rect(img, x, SHELTER_ROOF_UNDER_Y, x + 2, SHELTER_FRONT_BASE_Y, "slate")
    # lamp + pole + tree trunk markers
    rect(img, LAMP_X, 100, LAMP_X + 1, LAMP_BASE_Y, "slate_d")
    rect(img, POLE_X - 2, 40, POLE_X + 2, POLE_BASE_Y, "stone")
    rect(img, TREE_X - 3, 110, TREE_X + 3, TREE_BASE_Y, "brown_d")
    # 28px reference human (ink) at the shelter
    rect(img, 236, WAIT_BASE_Y - ADULT_H + 1, 240, WAIT_BASE_Y, "ink")
    return img


def place(bg: Image.Image, sprite: Image.Image, x: int, base_y: int, anchor: tuple[int, int] | None = None) -> None:
    """Paste sprite so its anchor (default bottom-centre) lands on (x, base_y)."""
    ax, ay = anchor if anchor else (sprite.width // 2, sprite.height - 1)
    bg.alpha_composite(sprite, (x - ax, base_y - ay))


def save_mock(img: Image.Image, group: str, name: str, scale: int = 3) -> None:
    d = OUT / group / "_preview"
    d.mkdir(parents=True, exist_ok=True)
    img.resize((img.width * scale, img.height * scale), Image.NEAREST).save(d / f"{name}@{scale}x.png")
