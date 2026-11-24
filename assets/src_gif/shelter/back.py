from _c import *
im = canvas()
X0, X1 = 118, 231   # between front pillars
TOP, BOT = 151, STAND_Y
# rear frame: top rail, posts, kick rail
rect(im, X0, TOP, X1, TOP+1, "grey_m"); rect(im, X0, TOP, X1, TOP, "grey_l")
for px_ in (120, 148, 204, 229):
    rect(im, px_, TOP, px_+1, BOT-1, "grey_m"); rect(im, px_, TOP, px_, BOT-1, "grey_l")
    rect(im, px_+1, TOP, px_+1, BOT-1, "grey_d")
# kick panel (solid, lower)
rect(im, 121, 189, 228, BOT-1, "grey_m"); rect(im, 121, 189, 228, 189, "grey_l"); rect(im, 121, 190, 228, 190, "grey")
rect(im, 121, BOT-1, 228, BOT-1, "grey_d")
for x in range(124, 228, 6):  # vent slots of the perforated skirt
    rect(im, x, 192, x+2, 192, "grey_d"); rect(im, x, 194, x+2, 194, "grey_d")
# glass panes: transparent interior, light tint rails + glare strokes
def pane(x0, x1):
    y0, y1 = TOP+2, 188
    rect(im, x0, y0, x1, y0, "glass_l"); rect(im, x0, y1, x1, y1, "glass")
    rect(im, x0, y0, x0, y1, "glass_l"); rect(im, x1, y0, x1, y1, "glass")
    rect(im, x0+1, y0+1, x1-1, y0+1, "glass_l")
    # glare strokes
    for k, (dx, dy, n) in enumerate([(5, 4, 7), (10, 8, 5)]):
        for i in range(n):
            put(im, x0+dx+i+1, y0+dy+n-i, "white" if k == 0 else "glass_l")
    for i in range(4): put(im, x1-8+i, y1-6+(3-i), "glass_l")
pane(150, 175); pane(177, 202)
rect(im, 176, TOP+2, 176, 188, "grey_m")
# route map panel (left)
mx0, my0, mx1, my1 = 206, 165, 228, 187
rect(im, mx0-1, my0-1, mx1+1, my1+1, "grey_d"); rect(im, mx0, my0, mx1, my1, "paper")
rect(im, mx0, my0, mx1, my0+8, "pb"); rect(im, mx0, my0, mx1, my0, "pb_l")
text(im, mx0+3, my0+4, "TUYẾN", "white")
rect(im, mx0, my0+15, mx1, my0+16, "glass"); rect(im, mx0, my0+15, mx1, my0+15, "glass_l")
line(im, mx0+2, my0+12, mx0+10, my0+12, "red"); line(im, mx0+10, my0+12, mx0+10, my0+20, "red")
line(im, mx0+10, my0+20, mx1-2, my0+20, "red")
line(im, mx0+3, my0+19, mx0+8, my0+13, "teal"); line(im, mx0+8, my0+13, mx1-3, my0+11, "teal")
line(im, mx0+16, my0+10, mx0+16, my0+21, "or")
for (x, y) in [(mx0+2, my0+12), (mx0+10, my0+20), (mx1-2, my0+20), (mx0+16, my0+12), (mx0+16, my0+20), (mx1-3, my0+11), (mx0+3, my0+19)]:
    rect(im, x-1, y-1, x, y, "white"); put(im, x-1, y-1, "grey_d")
# lightbox (lit ad) at right end
lx0, ly0, lx1, ly1 = 122, 156, 146, 187
rect(im, lx0-1, ly0-1, lx1+1, ly1+1, "grey_d"); rect(im, lx0, ly0, lx1, ly1, "glow")
rect(im, lx0, ly0, lx1, ly0, "white"); rect(im, lx0, ly0, lx0, ly1, "white")
rect(im, lx1, ly0+1, lx1, ly1, "lamp"); rect(im, lx0+1, ly1, lx1, ly1, "lamp")
rect(im, lx0+1, ly0+1, lx1-1, ly0+11, "red"); rect(im, lx0+1, ly0+1, lx1-1, ly0+1, "red_l")
text(im, lx0+1, ly0+6, "CÀ PHÊ", "white")
# coffee cup pictogram
cx, cy = lx0+8, ly0+17
rect(im, cx, cy, cx+8, cy+8, "wc"); rect(im, cx, cy, cx+8, cy, "white"); rect(im, cx+8, cy, cx+8, cy+8, "wc_d")
rect(im, cx+9, cy+2, cx+11, cy+6, "wc"); rect(im, cx+10, cy+3, cx+10, cy+5, "glow")
rect(im, cx+1, cy+1, cx+7, cy+2, "wood")
rect(im, cx-2, cy+9, cx+10, cy+9, "wc_d")
for i in range(3): put(im, cx+2+i*2, cy-2-(i%2), "white"); put(im, cx+2+i*2, cy-3-(i%2), "wc")
text(im, lx0+5, ly1-6, "CAFE", "wood")
save_asset("shelter", "shelter_back", im, anchor=(0, 0), notes="Rear glass shelter wall: transparent glass panes (frame + glare), route map left, lit lightbox right.")
