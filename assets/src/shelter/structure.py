from common import *

# ------------------------------------------------------------------ helpers
def perforated(im, x0, y0, x1, y1, base="slate", hole="navy", lit="grey"):
    R(im, x0, y0, x1, y1, base)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x % 4 == 0 and y % 4 == 0) or (x % 4 == 2 and y % 4 == 2):
                P(im, x, y, hole)
    for y in range(y0, y1 + 1):          # shade the right/bottom edge of the sheet
        P(im, x1, y, "slate_d")
    for x in range(x0, x1 + 1):
        P(im, x, y1, "slate_d")


def steel_post(im, x0, y0, x1, y1):
    R(im, x0, y0, x1, y1, "slate")
    R(im, x0, y0, x0, y1, "grey")
    R(im, x1, y0, x1, y1, "slate_d")


def poster(im, x0, y0):
    """Ha Long Bay travel poster, 27x33 interior at (x0,y0)."""
    W_, H_ = 27, 33
    sky = layer()
    # sky gradient with warm horizon
    vgradient(im, x0 - OX, y0 - OY, x0 - OX + W_ - 1, y0 - OY + 13, ["sky", "sky_l", "sand"])
    R(im, x0, y0 + 14, x0 + W_ - 1, y0 + 16, "sand")
    # sun
    sx, sy = x0 + 20, y0 + 6
    R(im, sx - 1, sy - 2, sx + 1, sy + 2, "yellow"); R(im, sx - 2, sy - 1, sx + 2, sy + 1, "yellow")
    P(im, sx - 1, sy - 1, "glow"); P(im, sx - 2, sy - 1, "glow")
    P(im, sx + 2, sy + 1, "gold"); P(im, sx + 1, sy + 2, "gold")
    # birds
    for bx, by in ((x0 + 7, y0 + 3), (x0 + 10, y0 + 5)):
        P(im, bx, by, "white"); P(im, bx + 2, by, "white"); P(im, bx + 1, by + 1, "white")
    wl = y0 + 17                         # waterline
    # far karsts (hazy)
    Poly(im, [(x0 + 11, wl), (x0 + 14, wl - 6), (x0 + 16, wl - 7), (x0 + 19, wl - 3), (x0 + 21, wl)], "mint")
    Poly(im, [(x0 + 18, wl), (x0 + 22, wl - 4), (x0 + 26, wl - 5), (x0 + 26, wl)], "mint")
    R(im, x0 + 12, wl - 1, x0 + 26, wl, "green")
    # near karst (left, big)
    Poly(im, [(x0, wl), (x0, wl - 11), (x0 + 3, wl - 14), (x0 + 5, wl - 15), (x0 + 7, wl - 12),
              (x0 + 9, wl - 7), (x0 + 11, wl)], "green_d")
    Poly(im, [(x0, wl - 11), (x0 + 3, wl - 14), (x0 + 5, wl - 15), (x0 + 3, wl - 9), (x0 + 1, wl - 4), (x0, wl - 4)], "green")
    for (a, b) in ((3, -15), (4, -15), (5, -16), (2, -14)):
        P(im, x0 + a, wl + b + 1, "green_l")
    for (a, b) in ((7, -9), (8, -6), (9, -3), (6, -12)):
        P(im, x0 + a, wl + b, "teal_k")
    Ln(im, x0 + 6, wl - 11, x0 + 8, wl - 3, "teal_k")
    # mid karst (right)
    Poly(im, [(x0 + 15, wl), (x0 + 16, wl - 5), (x0 + 19, wl - 8), (x0 + 22, wl - 6), (x0 + 24, wl)], "green_d")
    Poly(im, [(x0 + 16, wl - 5), (x0 + 19, wl - 8), (x0 + 18, wl - 3), (x0 + 16, wl)], "green")
    P(im, x0 + 19, wl - 8, "green_l"); P(im, x0 + 18, wl - 7, "green_l")
    # water
    for yy in range(wl + 1, y0 + 24):
        f = (yy - wl - 1) / 6
        D(im, x0, yy, x0 + W_ - 1, yy, "blue" if f < 0.5 else "blue_d", "blue_d" if f < 0.5 else "navy", 0.25 + 0.4 * (f % 0.5) * 2)
    for (a, b, l) in ((2, 2, 3), (10, 4, 4), (18, 3, 3), (6, 6, 3), (21, 6, 4), (14, 1, 2)):
        R(im, x0 + a, wl + b, x0 + a + l - 1, wl + b, "sky_l")
    # karst reflections
    R(im, x0 + 1, wl + 1, x0 + 8, wl + 1, "teal_k"); R(im, x0 + 3, wl + 2, x0 + 6, wl + 2, "teal_k")
    # junk boat with red sails
    bx, by = x0 + 11, wl + 3
    R(im, bx, by, bx + 7, by, "brown_k"); R(im, bx + 1, by - 1, bx + 6, by - 1, "brown_d")
    P(im, bx + 4, by - 2, "brown_k"); Ln(im, bx + 3, by - 2, bx + 3, by - 8, "brown_k")
    Poly(im, [(bx + 4, by - 8), (bx + 7, by - 2), (bx + 4, by - 2)], "red")
    Poly(im, [(bx + 2, by - 6), (bx + 2, by - 2), (bx, by - 2)], "red_d")
    P(im, bx + 4, by - 7, "salmon"); P(im, bx + 4, by - 6, "salmon")
    # title band
    R(im, x0, y0 + 24, x0 + W_ - 1, y0 + 32, "navy")
    R(im, x0, y0 + 24, x0 + W_ - 1, y0 + 24, "gold")
    T(im, x0, y0 + 26, "HẠ LONG", "yellow")
    # light-box diffuser glow (top-left)
    for i in range(3):
        P(im, x0 + i, y0, "white"); 
    P(im, x0, y0 + 1, "white")
    # worn bottom-left curl
    P(im, x0, y0 + 32, "grey"); P(im, x0 + 1, y0 + 32, "slate_d")


def route_map(im, x0, y0):
    """17x24 route panel at (x0,y0)."""
    R(im, x0, y0, x0 + 16, y0 + 23, "grey_l")
    R(im, x0, y0 + 23, x0 + 16, y0 + 23, "grey")
    R(im, x0 + 16, y0, x0 + 16, y0 + 23, "grey")
    R(im, x0, y0, x0 + 16, y0 + 3, "blue_d")
    R(im, x0, y0, x0 + 16, y0, "blue")
    for i in range(6):
        P(im, x0 + 2 + i * 2, y0 + 2, "white")
    # map: a bent route line with stops
    pts = [(x0 + 2, y0 + 14), (x0 + 5, y0 + 14), (x0 + 5, y0 + 10), (x0 + 11, y0 + 10), (x0 + 11, y0 + 6), (x0 + 14, y0 + 6)]
    for a, b in zip(pts, pts[1:]):
        Ln(im, a[0], a[1], b[0], b[1], "red")
    Ln(im, x0 + 2, y0 + 7, x0 + 8, y0 + 13, "green")
    Ln(im, x0 + 8, y0 + 13, x0 + 14, y0 + 13, "green")
    for (a, b) in pts:
        P(im, a, b, "white")
    P(im, x0 + 2, y0 + 7, "white"); P(im, x0 + 14, y0 + 13, "white")
    R(im, x0 + 7, y0 + 4, x0 + 8, y0 + 5, "mint")      # park
    for yy in (y0 + 5, y0 + 8):                          # faint grid streets
        D(im, x0 + 1, yy + 0, x0 + 15, yy + 0, "grey_l", "grey", 0.25)
    # route chips
    for i, (n, col) in enumerate((("1", "red"), ("3", "green"), ("4", "blue"))):
        cx = x0 + 1 + i * 5
        R(im, cx, y0 + 16, cx + 4, y0 + 22, col)
        T(im, cx + 1, y0 + 17, n, "white")
    # frame
    R(im, x0 - 1, y0 - 1, x0 + 17, y0 - 1, "grey_l"); R(im, x0 - 1, y0 - 1, x0 - 1, y0 + 24, "grey_l")
    R(im, x0 + 17, y0 - 1, x0 + 17, y0 + 24, "slate_d"); R(im, x0 - 1, y0 + 24, x0 + 17, y0 + 24, "slate_d")


# ------------------------------------------------------------------ SHELTER BACK
def make_back():
    im = layer()
    # top beam under roof
    R(im, 160, 129, 279, 129, "slate"); R(im, 160, 130, 279, 130, "slate_d"); R(im, 160, 131, 279, 131, "navy")
    # bay A: perforated sheet w/ map
    perforated(im, 168, 132, 186, 168)
    # bay B: glass panes (transparent) in a frame; kick plate below
    R(im, 189, 132, 241, 132, "slate_d")
    for mx in (207, 224):
        R(im, mx, 133, mx, 159, "slate"); 
    # glass reflections
    for (gx, gy, ln) in ((192, 152, 9), (196, 154, 12), (211, 150, 8), (215, 154, 10), (228, 151, 9), (232, 155, 11)):
        for i in range(ln):
            P(im, gx + i, gy - i, "sky_l" if i % 5 != 4 else "white")
    # frame line on glass edges + dirt
    R(im, 189, 133, 189, 159, "slate_d"); R(im, 241, 133, 241, 159, "slate_d")
    D(im, 190, 156, 240, 159, "stone_l", "stone", 0.0) if False else None
    for x in range(190, 241):
        if (x * 7) % 5 < 2:
            P(im, x, 159, "stone_l")
    R(im, 189, 160, 241, 160, "grey"); 
    perforated(im, 189, 161, 241, 168)
    R(im, 189, 160, 241, 160, "grey")
    # uprights
    for ux in (166, 187, 242):
        steel_post(im, ux, 131, ux + 1, 168)
    steel_post(im, 278, 131, 279, 168)
    # map panel
    route_map(im, 169, 136)
    # lightbox (lit) x244..274 y130..168
    R(im, 244, 130, 274, 168, "slate")
    R(im, 244, 130, 274, 130, "grey"); R(im, 244, 130, 244, 168, "grey")
    R(im, 274, 130, 274, 168, "slate_d"); R(im, 245, 131, 273, 131, "slate_d")
    R(im, 245, 164 + 1, 273, 168, "slate_d")
    R(im, 245, 165, 273, 165, "slate")
    # vents on base
    for vx in range(248, 271, 3):
        R(im, vx, 167, vx + 1, 167, "navy")
    R(im, 245, 132, 245, 164, "grey_l"); R(im, 273, 132, 273, 164, "slate_d")  # diffuser rim
    poster(im, 246, 132)
    R(im, 245, 132, 245, 164, "white")
    # weathering: rust at feet, drips, stickers
    for (x, y) in ((166, 167), (167, 166), (187, 168), (242, 167), (278, 167), (244, 168), (274, 168)):
        P(im, x, y, "rust")
    for (x, y) in ((190, 167), (196, 168), (210, 168), (233, 168), (205, 163)):
        P(im, x, y, "brown_d")
    R(im, 172, 163, 175, 165, "yellow"); R(im, 172, 163, 175, 163, "gold"); P(im, 174, 164, "red")   # sticker
    R(im, 179, 160, 181, 161, "mint"); P(im, 180, 161, "teal_k")
    R(im, 248, 169, 270, 169, "stone_d") if False else None
    # roof shadow on top of bay A / lightbox
    D(im, 168, 132, 186, 135, "navy", "slate_d", 0.6) if False else None
    return im


# ------------------------------------------------------------------ SEATS
def seat(im, x0):
    y0 = 150
    sw = 11
    # back shell, rounded top
    for i in range(sw):
        P(im, x0 + i, y0, "sky") if 2 <= i <= 8 else None
    for yy in range(y0, y0 + 10):
        inset = 2 if yy == y0 else (1 if yy == y0 + 1 else 0)
        for i in range(inset, sw - inset):
            f = (yy - y0) / 9
            col = "sky" if f < 0.18 else "blue" if f < 0.7 else "blue_d"
            if i == inset:
                col = "sky_l" if f < 0.75 else "sky"
            elif i == sw - 1 - inset:
                col = "blue_d" if f < 0.8 else "navy"
            P(im, x0 + i, yy, col)
    for i in range(3, 8):                       # moulded slots
        P(im, x0 + i, y0 + 3, "blue_d"); P(im, x0 + i, y0 + 5, "blue_d")
    for i in range(3, 7):
        P(im, x0 + i, y0 + 4, "sky")
    P(im, x0 + 3, y0 + 2, "sky_l")
    # gap
    for i in range(sw):
        P(im, x0 + i, y0 + 10, "navy")
    # seat pan
    P(im, x0 + 1, y0 + 10, "slate_d"); P(im, x0 + 9, y0 + 10, "slate_d")
    for yy, col, lo in ((y0 + 11, "sky_l", "sky"), (y0 + 12, "blue", "blue"), (y0 + 13, "blue", "blue_d"), (y0 + 14, "blue_d", "navy")):
        for i in range(sw):
            P(im, x0 + i, yy, col if i < 7 else lo)
    P(im, x0, y0 + 11, "sky_l"); P(im, x0, y0 + 12, "sky"); P(im, x0 + 10, y0 + 13, "navy"); P(im, x0 + 10, y0 + 12, "blue_d")
    P(im, x0, y0 + 14, "navy"); P(im, x0 + 10, y0 + 14, "navy")


def make_seats():
    im = layer()
    xs = [190, 202, 214, 226]
    # legs first (behind rail)
    for lx in (192, 212, 232):
        R(im, lx, 166, lx + 1, 171, "slate"); R(im, lx + 1, 166, lx + 1, 171, "slate_d")
        R(im, lx - 1, 171, lx + 2, 171, "navy")
    for x0 in xs:
        seat(im, x0)
    # rail
    R(im, 188, 165, 237, 165, "grey"); R(im, 188, 166, 237, 166, "slate_d")
    R(im, 188, 167, 237, 167, "navy") if False else None
    # bolts / wear
    for x0 in xs:
        P(im, x0 + 2, 165, "grey_l"); P(im, x0 + 8, 165, "grey_l")
    # chewing gum / scuffs
    P(im, 207, 162, "mauve"); P(im, 221, 161, "blue_d")
    return im


def make_stool():
    rows = [
        "..ssrrrr..",
        ".sshrrrrrd",
        ".rrrrrrrdd",
        "..rrrrrdd.",
        "..drrrrdk.",
        "..rdkkdk..",
        "..rdkkdk..",
        ".rd.kk.dk.",
        ".rd.kk.dk.",
        "rd......dk",
        "rd......dk",
        "kk......kk",
    ]
    return grid(rows, {"s": "salmon", "h": "salmon", "r": "red", "d": "red_d", "k": "rust"})


# ------------------------------------------------------------------ SHELTER FRONT
def make_front():
    im = layer()
    # roof slab
    R(im, 160, 122, 279, 122, "grey_l")
    R(im, 160, 123, 279, 123, "grey")
    R(im, 160, 124, 279, 124, "slate")
    R(im, 160, 125, 279, 125, "grey")
    R(im, 160, 126, 279, 126, "blue_d")
    R(im, 160, 127, 279, 127, "slate_d")
    R(im, 160, 128, 279, 128, "navy")
    # panel seams / bolts
    for sx in range(180, 279, 20):
        P(im, sx, 123, "slate"); P(im, sx, 124, "slate_d")
        P(im, sx + 1, 125, "grey_l")
    R(im, 160, 122, 160, 127, "grey_l"); R(im, 279, 122, 279, 128, "slate_d")
    R(im, 161, 126, 161, 126, "blue")
    # stripe highlight pixels
    for sx in range(166, 279, 6):
        P(im, sx, 126, "blue")
    # weathering: water stains / rust drips under fascia
    for (x, y) in ((185, 129), (232, 129), (262, 129), (171, 129), (270, 129)):
        P(im, x, y, "brown_d"); 
    for (x, y) in ((185, 130), (232, 130), (270, 130)):
        P(im, x, y, "stone")
    for x in (190, 214, 249):
        P(im, x, 127, "stone"); P(im, x + 1, 127, "stone_d")
    # header board
    bx0, bx1, by0, by1 = 194, 245, 130, 142
    for rx in (198, 241):
        R(im, rx, 129, rx, 130, "grey"); 
    R(im, bx0, by0, bx1, by1, "blue_d")
    R(im, bx0, by0, bx1, by0, "blue"); R(im, bx0, by0, bx0, by1, "blue")
    R(im, bx1, by0, bx1, by1, "navy"); R(im, bx0, by1, bx1, by1, "navy")
    R(im, bx0 + 1, by0 + 1, bx1 - 1, by0 + 1, "blue_d")
    T(im, 196, 134, "TRẠM XE BUÝT", "white")
    P(im, bx0, by0, "sky"); P(im, bx0 + 1, by0, "sky")
    # pillars (3px) with joints and base
    for (x0, x1) in (PILL_L, PILL_R):
        R(im, x0, 129, x1, 173, "slate")
        R(im, x0, 129, x0, 173, "grey"); R(im, x1, 129, x1, 173, "slate_d")
        for jy in (146, 158):
            R(im, x0, jy, x1, jy, "slate_d"); P(im, x0, jy, "slate")
        R(im, x0 - 1, 170, x1 + 1, 171, "slate"); R(im, x0 - 1, 170, x0 - 1, 171, "grey")
        R(im, x1 + 1, 170, x1 + 1, 171, "slate_d")
        R(im, x0 - 1, 172, x1 + 1, 174, "slate_d"); R(im, x0 - 1, 172, x0 - 1, 172, "slate")
        R(im, x0 - 1, 174, x1 + 1, 174, "navy")
        P(im, x0, 172, "grey_l") if False else None
        # bracket under roof
        P(im, x0 - 1, 129, "slate"); P(im, x1 + 1, 129, "slate_d"); P(im, x0 - 1, 130, "slate_d") if False else None
        # rust at foot
        P(im, x0, 169, "rust"); P(im, x0 + 1, 168, "brown_d")
    # bus-stop sign post (right end)
    px0 = 287
    R(im, px0, 130, px0 + 1, 174, "slate"); R(im, px0, 130, px0, 174, "grey"); R(im, px0 + 1, 130, px0 + 1, 174, "slate_d")
    R(im, px0 - 1, 172, px0 + 2, 173, "slate_d"); R(im, px0 - 1, 174, px0 + 2, 174, "navy"); P(im, px0 - 1, 172, "slate")
    # blue sign 12x12
    sx0, sy0 = 282, 128
    R(im, sx0, sy0, sx0 + 11, sy0 + 11, "blue")
    R(im, sx0, sy0 + 11, sx0 + 11, sy0 + 11, "blue_d"); R(im, sx0 + 11, sy0, sx0 + 11, sy0 + 11, "blue_d")
    R(im, sx0, sy0, sx0 + 11, sy0, "sky"); R(im, sx0, sy0, sx0, sy0 + 10, "sky")
    # white inner border
    for i in range(1, 10):
        P(im, sx0 + 1 + i, sy0 + 1, "white") if False else None
    bus = grid([".wwwwww.", "wbbwbbbw", "wwwwwwww", "wwwwwwww", ".ww..ww."], {"w": "white", "b": "blue_d"})
    paste(im, bus, sx0 + 2 - OX, sy0 + 3 - OY)
    R(im, sx0 + 2, sy0 + 9, sx0 + 9, sy0 + 9, "white") if False else None
    # route plate
    R(im, 283, 142, 292, 149, "navy"); R(im, 283, 142, 292, 142, "slate_d")
    T(im, 284, 144, "32", "white")
    P(im, 291, 144, "red"); P(im, 291, 145, "red")
    # bolts
    for (x, y) in ((283, 129), (293, 129), (283, 139), (293, 139)):
        P(im, x, y, "grey_l") if False else None
    # sign weathering
    P(im, 291, 138, "stone_l"); P(im, 290, 139, "stone_l"); P(im, 283, 135, "stone_l")
    return im


if __name__ == "__main__":
    export("shelter_back", make_back(), notes="Layer shelter_back. Rear frame: perforated bay (x168-186) with route-map panel, glass bay (x189-241, transparent), lit Ha Long Bay lightbox (x244-274). Feet y168.")
    seats = make_seats()
    export("seats", seats, notes="Layer seats. 4 blue moulded bucket seats on steel rail (feet y171). Seat x: 190,202,214,226.")
    st = make_stool()
    save_asset(GROUP, "stool_red", st, anchor=(st.width // 2, st.height - 1),
               notes="Loose red plastic stool. Bottom-centre anchor = ground contact. Suggested placement x=282, base_y=177 (right of shelter, in front of sign post).")
    export("shelter_front", make_front(), notes="Layer shelter_front. Pillars x162-164 / x275-277 (feet y174), roof slab y122-128 (top face y122-124, fascia y125-127), header board 'TRAM XE BUYT', bus-stop sign on post x287-288.")
