from lib import *
from catlib import catmull
from walkers import SCR
import sys
W, H = 32, 19
FY = H - 2

def dog_frame(f):
    img = new(W, H)
    bob = [0, -1, 0, 0, -1, 0][f]
    def foot(off):
        j = (f - off) % 6
        if j <= 3: return 3 - 2 * j, 0
        return -3 + 2 * (j - 3), 2
    # tail (up-curved, wags)
    wag = [0, 1, 1, 0, -1, -1][f]
    for (x, y, col) in [(7, 6, "ochre"), (6, 5, "ochre"), (5, 4, "ochre"), (4 + wag, 3, "clay"), (4 + wag, 2, "sand")]:
        put(img, x, y + bob, col)
    put(img, 6, 6 + bob, "ochre")
    def leg(hip, x0, off, far):
        dx, lift = foot(off)
        paw = (x0 + dx, FY - lift)
        knee, _ = ik(hip, (paw[0], paw[1] - 1), 3.0, 3.0, 1 if hip[0] < 14 else -1)
        col = "clay" if far else "ochre"
        limb(img, hip, knee, col, t=2)
        limb(img, knee, (paw[0], paw[1] - 1), col, t=2)
        put(img, paw[0], paw[1], "sand" if not far else "grey_l"); put(img, paw[0] + 1, paw[1], "sand" if not far else "grey_l")
        put(img, paw[0] + 2, paw[1], "sand" if not far else "grey_l") if False else None
    leg((9, 9 + bob), 9, 0 + 3, True)      # far hind (pair B)
    leg((19, 9 + bob), 19, 0, True)         # far front (pair A)
    torso = [(7, 6), (10, 4.5), (15, 4.3), (19, 5), (21, 7), (20, 9.5), (15, 10.5), (10, 10.5), (7.5, 9), (6.5, 7.5)]
    pts = [(R(x), R(y + bob)) for x, y in catmull(torso, 6)]
    ImageDraw.Draw(img).polygon(pts, fill=c("ochre"))
    for (x, y) in pts:
        pass
    # shading: top highlight, belly shade, white chest
    px = img.load()
    for x in range(6, 22):
        ys = [y for y in range(H) if px[x, y][3] and px[x, y][:3] in (RGB["ochre"],)]
        if not ys: continue
        t, b = min(ys), max(ys)
        if x < 16: px[x, t] = c("yellow") if False else c("sand")
        px[x, b] = c("clay")
    for (x, y) in [(20, 8 + bob), (20, 9 + bob), (19, 9 + bob), (19, 8 + bob)]:
        put(img, x, y, "white")
    # saddle patch
    for (x, y) in [(11, 5), (12, 5), (13, 5), (12, 6), (13, 6), (14, 5)]:
        put(img, x, y + bob, "clay")
    leg((9, 9 + bob), 9, 0, False)         # near hind (pair A)
    leg((19, 9 + bob), 19, 3, False)        # near front (pair B)
    # head
    head = grid([
        "..dd....",
        ".dddoo..",
        "dooooo..",
        "ooiooosk",
        ".ooooss.",
        "..sss...",
    ], {"d": "brown_d", "o": "ochre", "i": "ink", "s": "sand", "k": "ink"})
    paste(img, head, 19, 2 + bob + (1 if f in (1, 4) else 0) * 0)
    return finish(img, W, H)

if __name__ == "__main__":
    fr = [dog_frame(i) for i in range(6)]
    k = 10
    w, h = fr[0].size
    im = Image.new("RGBA", (w * 6 * k, h * k), (*RGB["sky_l"], 255))
    for i, f in enumerate(fr): im.alpha_composite(f.resize((w * k, h * k), Image.NEAREST), (i * w * k, 0))
    im.convert("RGB").save(SCR + "dog.png")
    if "--export" in sys.argv:
        export_lr("characters", "dog", fr, 10, notes="street dog trot 6f; ground speed 2px/frame (20px/s @10fps)")
