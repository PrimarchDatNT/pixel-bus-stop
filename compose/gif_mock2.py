"""Blocking mock v2 — recomposed after the client's note "the GIF is more artistic; our objects/composition aren't
pretty yet". Same structure as the GIF: ONE hero building + ONE hero bloom mass, sky breathing room, pale distance,
props only at the feet. Value plan: dark-ish old house vs light sky, saturated pink only on the bougainvillea."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.px_gif import *

W, H = 384, 216
im = new(W, H)
rect(im, 0, 0, W - 1, H - 1, "sky")
rect(im, 0, 0, W - 1, 14, "sky_hl")
# clouds
for cx, cy, r in [(300, 34, 16), (320, 30, 12), (282, 38, 10), (70, 22, 9), (84, 20, 7)]:
    ellipse(im, cx - r, cy - r // 2, cx + r, cy + r // 2, "cloud")
# distance: pale Hanoi skyline + Long Bien bridge truss on the right, very low contrast
for x0, w, top in [(250, 14, 150), (264, 10, 140), (300, 16, 146), (318, 12, 136), (334, 18, 150), (356, 14, 142), (370, 14, 148)]:
    rect(im, x0, top, x0 + w, 176, "haze_l")
rect(im, 280, 160, 383, 163, "haze")                      # bridge deck
for x in range(284, 384, 12):
    line(im, x, 160, x + 6, 150, "haze"); line(im, x + 6, 150, x + 12, 160, "haze")
rect(im, 0, 168, W - 1, 178, "haze_l")                    # far haze band (river bank / far street)
# HERO building: old-quarter shophouse, 2 storeys + attic, tile roof, dark wood shutters (darker value)
X0, X1 = 118, 272
rect(im, X0, 70, X1, 186, "wy_d")                          # walls (muted ochre)
poly(im, [(X0 - 8, 72), (X1 + 8, 72), (X1 - 10, 46), (X0 + 10, 46)], "tc_d")   # tiled roof
rect(im, X0 - 8, 72, X1 + 8, 75, "wood_k")
rect(im, X0 + 50, 30, X0 + 70, 46, "tc_d")                 # attic dormer
for x in range(X0 + 12, X1 - 10, 34):                      # upper floor shutters
    rect(im, x, 86, x + 18, 116, "sh_d")
rect(im, X0, 118, X1, 122, "wood_k")                       # balcony slab
for x in range(X0 + 2, X1, 4):
    line(im, x, 108, x, 118, "wood_d")                     # railing
rect(im, X0 + 6, 132, X1 - 6, 186, "wood_d")               # ground floor shop (dark)
rect(im, X0 + 70, 126, X1 - 20, 136, "paper")              # signboard
# HERO bloom: bougainvillea towering over the shelter roof and up the facade (like the GIF cherry)
ellipse(im, 34, 40, 170, 150, "bl")
ellipse(im, 90, 88, 230, 160, "bl")
ellipse(im, 20, 90, 110, 168, "bl_d")
rect(im, 96, 120, 101, 196, "trunk")                       # twisting trunk
# shelter in front (lower half), bloom pours over its roof
rect(im, 70, 150, 240, 154, "grey_k")                      # roof slab
rect(im, 76, 154, 234, 190, "glass")
rect(im, 90, 184, 180, 188, "pb")                          # seats
rect(im, 72, 154, 74, 196, "grey_d"); rect(im, 236, 154, 238, 196, "grey_d")
rect(im, 248, 140, 249, 196, "grey_d"); rect(im, 243, 132, 254, 144, "pb")   # stop sign
# props at the feet only: tra da corner + cat + one person waiting
rect(im, 282, 186, 312, 196, "wood"); rect(im, 316, 189, 322, 196, "red"); rect(im, 300, 170, 308, 196, "wc")
rect(im, 140, 160, 147, 190, "pk")                         # person waiting
rect(im, 206, 146, 218, 150, "or")                         # cat on roof
# ground
rect(im, 0, 186, W - 1, 199, "pave"); rect(im, 0, 200, W - 1, 202, "grey_l"); rect(im, 0, 203, W - 1, H - 1, "road")
out = pathlib.Path(__file__).resolve().parents[1] / "assets/out_gif/_mock"
im.save(out / "mock2.png"); im.resize((W * 5, H * 5), Image.NEAREST).save(out / "mock2@5x.png")
print("ok")
