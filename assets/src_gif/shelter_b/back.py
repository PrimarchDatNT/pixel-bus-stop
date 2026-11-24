from _c import *
im = canvas()
TOP, BOT = 155, STAND_Y
X0, X1 = 41, 170
def pane(x0, x1, glares):
    y0, y1 = TOP, 190
    rect(im, x0, y0, x1, y0, "glass_l"); rect(im, x0, y1, x1, y1, "glass")
    rect(im, x0, y0, x0, y1, "glass_l"); rect(im, x1, y0, x1, y1, "glass")
    rect(im, x0 + 1, y0 + 1, x1 - 1, y0 + 1, "glass_l")
    for (gx, gy, n, nm) in glares:
        for i in range(n): put(im, gx + i, gy + n - i, nm)
pane(41, 115, [(98, 160, 9, "white"), (104, 163, 6, "glass_l"), (50, 165, 7, "glass_l")])
pane(118, 150, [(124, 172, 8, "white"), (131, 175, 5, "glass_l")])
pane(153, 170, [(156, 164, 7, "white")])
for mx in (116, 151):
    rect(im, mx, TOP, mx + 1, 190, "grey_m"); rect(im, mx, TOP, mx, 190, "grey_l")
# top rail under roof
rect(im, X0, 154, X1, 154, "grey_d")
# kick panel with vents
rect(im, X0, 191, X1, BOT - 1, "grey_l"); rect(im, X0, 191, X1, 191, "grey_hl"); rect(im, X0, BOT - 1, X1, BOT - 1, "grey")
for x in range(X0 + 3, X1 - 2, 6): rect(im, x, 193, x + 2, 193, "grey")
# lightbox (muted ad)
lx0, ly0, lx1, ly1 = 50, 160, 70, 179
rect(im, lx0 - 1, ly0 - 1, lx1 + 1, ly1 + 1, "grey_d"); rect(im, lx0, ly0, lx1, ly1, "glow")
rect(im, lx0, ly0, lx1, ly0, "white"); rect(im, lx0, ly0, lx0, ly1, "white")
rect(im, lx1, ly0 + 1, lx1, ly1, "lamp"); rect(im, lx0 + 1, ly1, lx1, ly1, "lamp")
rect(im, lx0 + 1, ly0 + 1, lx1 - 1, ly0 + 8, "wb_d"); rect(im, lx0 + 1, ly0 + 1, lx1 - 1, ly0 + 1, "wb")
text(im, lx0 + 2, ly0 + 6, "CAFE", "white")
rect(im, lx0 + 6, ly0 + 11, lx0 + 13, ly0 + 15, "wp"); rect(im, lx0 + 6, ly0 + 11, lx0 + 13, ly0 + 11, "wp_l")
rect(im, lx0 + 14, ly0 + 12, lx0 + 15, ly0 + 14, "wp_d"); rect(im, lx0 + 4, ly0 + 16, lx0 + 15, ly0 + 16, "wc_d")
for i in range(2): put(im, lx0 + 8 + i * 3, ly0 + 9 - i % 2, "wc_d")
# route map
mx0, my0, mx1, my1 = 73, 160, 86, 179
rect(im, mx0 - 1, my0 - 1, mx1 + 1, my1 + 1, "grey_d"); rect(im, mx0, my0, mx1, my1, "paper")
rect(im, mx0, my0, mx1, my0 + 6, "pb"); rect(im, mx0, my0, mx1, my0, "pb_l")
text(im, mx0 + 1, my0 + 4, "32", "white")
rect(im, mx0, my0 + 12, mx1, my0 + 13, "glass"); rect(im, mx0, my0 + 12, mx1, my0 + 12, "glass_l")
line(im, mx0 + 2, my0 + 10, mx0 + 8, my0 + 10, "red"); line(im, mx0 + 8, my0 + 10, mx0 + 8, my0 + 16, "red"); line(im, mx0 + 8, my0 + 16, mx1 - 2, my0 + 16, "red")
line(im, mx0 + 2, my0 + 15, mx0 + 6, my0 + 9, "teal"); line(im, mx0 + 6, my0 + 9, mx1 - 2, my0 + 8, "teal")
for (x, y) in [(mx0 + 2, my0 + 10), (mx0 + 8, my0 + 16), (mx1 - 2, my0 + 16), (mx1 - 2, my0 + 8)]:
    rect(im, x - 1, y - 1, x, y, "white"); put(im, x - 1, y - 1, "grey_d")
save_asset("shelter", "shelter_back", im, anchor=(0, 0), notes="Rear wall x41-170 y154-195: transparent glass panes with glare, kick panel, lightbox x42-68 y158-179, route map x70-90 y159-179.")
