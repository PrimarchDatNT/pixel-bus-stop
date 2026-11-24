"""Bougainvillea as hand-placed lobes (GIF-cherry construction) — replaces the noise-textured version.

Each lobe: bumpy ellipse, 4-tone shading by direction to the upper-left light, a cast-shadow crevice where it sits
on lobes behind it, sparse 2-px blossom clusters, leaf tufts in the crevices. Trunk + planter + drapes included.
Writes assets/out_gif/shelter/bougainvillea.png (3 sway frames, 3 fps).
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.px_gif import *       # noqa: E402,F403
from tools.layout_gif import *   # noqa: E402,F403

TONES = ["bl_k", "bl_d", "bl", "bl_l", "bl_hl"]
# (cx, cy, rx, ry) back -> front. Crown tops out ~y 64; the house (x>=150) only gets a small climbing spray.
LOBES = [
    (70, 76, 22, 14), (104, 82, 18, 12),                     # rounded crown top
    (48, 94, 24, 18), (90, 92, 26, 17), (128, 104, 20, 14),
    (34, 112, 22, 20), (74, 112, 28, 19), (114, 120, 26, 17), (150, 126, 16, 13),
    (48, 138, 26, 12), (92, 142, 30, 11), (136, 144, 24, 9),  # front lobes resting on the roof
]
DRAPES = [(44, 13), (63, 19), (82, 10), (101, 16), (121, 12), (141, 18), (160, 9)]   # (x, length) below the roof


def h(*a):  # deterministic hash -> [0,1)
    v = 0
    for x in a:
        v = (v * 1103515245 + int(x) * 2654435761 + 12345) & 0xFFFFFFFF
    return ((v >> 8) & 0xFFFF) / 65536


def lobe_mask(cx, cy, rx, ry, k, phase):
    pts = {}
    seed = cx * 7 + cy * 13
    for y in range(int(cy - ry - 4), int(cy + ry + 5)):
        for x in range(int(cx - rx - 4), int(cx + rx + 5)):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            ang = math.atan2(dy, dx)
            bump = 0.10 * math.sin(ang * 7 + seed) + 0.06 * math.sin(ang * 13 + seed * 0.7 + phase) \
                + 0.05 * math.sin(ang * 19 + seed * 1.3)
            r = math.hypot(dx, dy)
            if r <= 1 + bump:
                pts[(x, y)] = (dx, dy, r, 1 + bump)
    return pts


def tone_for(dx, dy, r, rim):
    light = -(dx * 0.55 + dy * 0.85)                 # upper-left light
    edge = rim - r                                     # distance to the rim (normalised)
    if light > 0.62 and edge < 0.28:
        return 4
    if light > 0.22:
        return 3
    if light > -0.42:
        return 2
    return 1 if edge > 0.08 else 0


def frame(k):
    im = new(W, H)
    px = im.load()
    phase = k * 2 * math.pi / 3

    def put_t(x, y, t):
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = c(TONES[max(0, min(4, t))])

    # trunk + branches (seen in gaps and below the roof)
    for (x0, y0, x1, y1, w) in [(29, 186, 34, 160, 5), (34, 160, 30, 140, 5), (30, 140, 42, 112, 4), (42, 112, 60, 94, 3),
                                (36, 128, 70, 120, 3), (44, 116, 96, 100, 2), (60, 124, 120, 128, 2)]:
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
            for j in range(w):
                tone = "trunk_l" if j == 0 else ("trunk_d" if j == w - 1 else "trunk")
                X = x - w // 2 + j
                if 0 <= X < W:
                    px[X, y] = c(tone)
    # planter
    x0, x1 = BOUGAINVILLEA_PLANTER
    rect(im, x0 - 2, STAND_Y - 13, x1 + 2, STAND_Y, "tc")
    rect(im, x0 - 2, STAND_Y - 13, x1 + 2, STAND_Y - 12, "tc_l")
    rect(im, x1 + 1, STAND_Y - 11, x1 + 2, STAND_Y, "tc_d")
    rect(im, x0 - 1, STAND_Y - 14, x1 + 1, STAND_Y - 14, "wood_d")
    # foliage by clump stamping (classic pixel-art tree technique, like the GIF cherry):
    # many small discs inside the lobe envelope, drawn top -> bottom so lower clumps overlap upper ones.
    import random
    rnd = random.Random(11)
    top = min(cy - ry for cx, cy, rx, ry in LOBES); bot = max(cy + ry for cx, cy, rx, ry in LOBES)
    # solid base fill of the envelope (bumpy lobes), graded top -> bottom, so the mass reads as one canopy
    owner = set()
    for li, (cx, cy, rx, ry) in enumerate(LOBES):
        for (x, y), (dx, dy, r, rim) in lobe_mask(cx, cy, rx, ry, k, phase * 0.5).items():
            v = (y - top) / (bot - top)
            tone = "bl" if v < 0.7 else "bl_d"
            if rim - r < 0.12 and dx * 0.55 + dy * 0.85 > 0.3:
                tone = "bl_d" if v < 0.7 else "bl_k"
            if 0 <= x < W and 0 <= y < H:
                px[x, y] = c(tone); owner.add((x, y))
    stamps = []
    while len(stamps) < 330:
        li = rnd.randrange(len(LOBES)); cx, cy, rx, ry = LOBES[li]
        a = rnd.random() * 2 * math.pi; rr = math.sqrt(rnd.random())
        x = cx + math.cos(a) * rx * rr; y = cy + math.sin(a) * ry * rr
        edge = rr                                   # 0 core .. 1 rim of its lobe
        r = rnd.choice([3, 4, 4, 5, 5, 6]) if edge < 0.8 else rnd.choice([3, 3, 4])
        leaf = rnd.random() < 0.06
        if leaf:
            r = rnd.choice([1, 2])
        stamps.append((y, x, r, edge, leaf))
    stamps.sort()
    for (y, x, r, edge, leaf) in stamps:
        if edge > 0.72:                             # rim clumps sway 1 px
            x += round(math.sin(phase + x * 0.13 + y * 0.07) * 1.0)
        v = (y - top) / (bot - top)                 # 0 top .. 1 bottom of the whole mass
        if leaf:
            hi, body, lo = "leaf", "leaf_d", "leaf_k"
        elif v < 0.38:
            hi, body, lo = "bl_l", "bl", "bl_d"
        elif v < 0.72:
            hi, body, lo = "bl", "bl", "bl_d"
        else:
            hi, body, lo = "bl", "bl_d", "bl_k"
        X, Y = round(x), round(y)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d2 = dx * dx + dy * dy
                if d2 > r * r + (1 if r > 2 else 0):
                    continue
                if d2 >= r * r - 1 and h(X + dx, Y + dy, 5) < 0.25:   # nibble the rim -> ragged edges
                    continue
                # cauliflower bulge: lit cap on top (slightly left), shaded underside
                if dy <= -r * 0.45 and dx <= r * 0.45:
                    tone = hi
                elif dy >= r * 0.5 or (dy >= r * 0.2 and dx >= r * 0.5):
                    tone = lo
                else:
                    tone = body
                if not leaf and tone == hi and v < 0.35 and dy <= -r * 0.8 and dx <= 0 and h(X, Y, dx) < 0.55:
                    tone = "bl_hl"
                PX, PY = X + dx, Y + dy
                if 0 <= PX < W and 0 <= PY < H:
                    px[PX, PY] = c(tone); owner.add((PX, PY))
    # drapes: chains of small bract clusters hanging over the roof's front edge, swaying 1 px
    for i, (dxp, L) in enumerate(DRAPES):
        for s in range(0, L, 2):
            sway = round(math.sin(phase + i + s * 0.25) * (s / max(L, 1)) * 1.6)
            x, y = dxp + sway + (1 if (s // 4) % 2 else 0), SHELTER_ROOF_TOP_Y - 2 + s
            for ox, oy, t in ((0, 0, 3), (1, 0, 2), (-1, 1, 2), (0, 1, 2), (1, 1, 1), (0, 2, 1)):
                put_t(x + ox, y + oy, t if s < L - 3 else t - 1)
            if h(i, s) < 0.3:
                put_t(x - 1, y, 4)
    # loose bracts around the crown
    for i in range(16):
        cx, cy, rx, ry = LOBES[i % len(LOBES)]
        a = h(i, 3) * 2 * math.pi
        x = round(cx + math.cos(a) * (rx + 3 + 3 * h(i, 4))); y = round(cy + math.sin(a) * (ry + 2 + 2 * h(i, 5)))
        if (x, y) not in owner and y < SHELTER_ROOF_TOP_Y - 4:
            put_t(x, y, 3); put_t(x + 1, y, 2)
    return im


if __name__ == "__main__":
    frames = [frame(k) for k in range(3)]
    save_asset("shelter", "bougainvillea", frames, fps=3, anchor=(0, 0),
               notes="hand-placed lobes (bloom_lobes.py), replaces the noise version")
    print("ok")
