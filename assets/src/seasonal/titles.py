from common import *

FW, FH = 64, 26
FILL, FILL_D, EDGE, SHADOW = "glow", "sand", "brown_d", "brown_k"

# hand-drawn 7x9 title face (2px strokes); marks drawn separately
GL = {
 "X": ["##...##", "##...##", ".##.##.", "..###..", "..###..", "..###..", ".##.##.", "##...##", "##...##"],
 "U": ["##...##"] * 7 + [".#####.", "..###.."],
 "N": ["###..##", "###..##", "####.##", "####.##", "##.####", "##.####", "##..###", "##...##", "##...##"],
 "H": ["##...##"] * 4 + ["#######", "#######"] + ["##...##"] * 3,
 "A": ["..###..", ".##.##.", ".##.##.", "##...##", "##...##", "#######", "#######", "##...##", "##...##"],
 "T": ["#######", "#######"] + ["..###.."] * 7,
 "D": ["..#####.", "..##..##", "..##..##", "..##..##", "#####.##", "..##..##", "..##..##", "..##..##", "..#####."],
 "O": [".#####."] + ["##...##"] * 7 + [".#####."],
 "G": [".#####.", "##...##", "##.....", "##.....", "##..###", "##...##", "##...##", "##...##", ".#####."],
}
CIRC = ["...#...", "..###..", ".##.##."]
GAP = 1


def word_mask(word, marks):
    """returns (w, list of (x,y,row_in_cap or -1)) with cap top at y=3 (marks above), dot below."""
    pts = []
    x = 0
    for ch, mk in zip(word, marks):
        g = GL[ch]
        gw = len(g[0])
        for r, row in enumerate(g):
            for cidx, v in enumerate(row):
                if v == "#":
                    pts.append((x + cidx, 4 + r, r))
        if mk == "^":
            off = (gw - 7) // 2
            for r, row in enumerate(CIRC):
                for cidx, v in enumerate(row):
                    if v == "#":
                        pts.append((x + off + cidx, 0 + r, -1))
        if mk == ".":
            cxm = gw // 2 - 1
            for dx in (0, 1):
                for dy in (0, 1):
                    pts.append((x + cxm + dx, 4 + 9 + 1 + dy, 8))
        x += gw + GAP
    return x - GAP, pts


def icon_peach():
    g = new(11, 11)
    cx = cy = 5
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        x, y = round(cx + 2.9 * math.cos(a)), round(cy + 2.9 * math.sin(a))
        ellipse(g, x - 2, y - 2, x + 2, y + 2, "bloom")
        ellipse(g, x - 2, y - 2, x + 1, y + 1, "bloom_l")
        put(g, x - 1, y - 1, "bloom_hl")
    rect(g, cx - 1, cy - 1, cx + 1, cy + 1, "gold")
    put(g, cx - 1, cy - 1, "yellow")
    return g


def icon_sun():
    g = new(11, 11)
    cx = cy = 5
    for k in range(8):
        a = k * math.pi / 4
        for r in (4.0, 5.0):
            put(g, round(cx + r * math.cos(a)), round(cy + r * math.sin(a)), "gold" if k % 2 == 0 else "orange")
    ellipse(g, cx - 3, cy - 3, cx + 3, cy + 3, "orange")
    ellipse(g, cx - 3, cy - 3, cx + 2, cy + 2, "gold")
    ellipse(g, cx - 2, cy - 2, cx + 1, cy + 1, "yellow")
    put(g, cx - 1, cy - 1, "glow")
    return g


def icon_leaf():
    """bang leaf: broad obovate, red tip fading to orange, midrib + stem (tilted)"""
    g = new(11, 11)
    ang = -math.pi / 4
    ca, sa = math.cos(ang), math.sin(ang)
    for y in range(11):
        for x in range(11):
            dx, dy = x - 5, y - 5
            u = dx * ca + dy * sa      # along the leaf axis, + toward tip (up-right)
            v = -dx * sa + dy * ca
            t = (u + 4.6) / 9.6
            if 0 < t < 1:
                wdt = 4.4 * math.sin(math.pi * t ** 0.8)
                if abs(v) <= wdt:
                    col = "red" if t > 0.72 else ("orange" if t > 0.4 else "gold")
                    if v < -wdt * 0.4 and t > 0.3:
                        col = {"red": "salmon", "orange": "gold", "gold": "yellow"}[col]
                    put(g, x, y, col)
    # midrib + stem
    for k in range(-5, 5):
        x, y = round(5 + k * 0.707), round(5 - k * 0.707)
        if g.getpixel((x, y))[3]:
            put(g, x, y, "rust")
    put(g, 1, 9, "rust"); put(g, 0, 10, "rust")
    return g


def icon_daisy():
    g = new(11, 11)
    cx = cy = 5
    for k in range(8):
        a = k * math.pi / 4
        x, y = round(cx + 3.7 * math.cos(a)), round(cy + 3.7 * math.sin(a))
        line(g, cx, cy, x, y, "white")
        put(g, x, y, "white")
        for dx, dy in ((1, 0), (0, 1)):
            put(g, x + dx, y + dy, "white") if (k % 2 == 0) else None
    for k in (1, 3, 5, 7):
        a = k * math.pi / 4
        put(g, round(cx + 4.4 * math.cos(a)), round(cy + 4.4 * math.sin(a)), "grey_l")
    rect(g, cx - 1, cy - 1, cx + 1, cy + 1, "gold")
    put(g, cx - 1, cy - 1, "yellow")
    put(g, cx + 1, cy + 1, "orange")
    return g


def title(word, marks, icon):
    tw, pts = word_mask(word, marks)
    gap = 4
    total = 11 + gap + tw
    x0 = (FW - total) // 2
    glyph = new(FW, FH)
    tx = x0 + 11 + gap
    for (x, y, r) in pts:
        put(glyph, tx + x, y + 2, FILL_D if r >= 7 else FILL)
    # icon centred on cap height (cap rows 4..12 -> centre 8)
    ic = new(FW, FH)
    ic.alpha_composite(icon, (x0, 2 + 8 - 5 + 0))
    both = glyph.copy()
    both.alpha_composite(ic)
    edge = outline(both, EDGE, diagonal=True)   # +1 margin each side
    out = new(FW + 2, FH + 2)
    # drop shadow (1px down-right) under the outline
    sh = new(FW + 2, FH + 2)
    px = edge.load()
    for y in range(edge.height):
        for x in range(edge.width):
            if px[x, y][3]:
                if x + 1 < sh.width and y + 1 < sh.height:
                    sh.putpixel((x + 1, y + 1), c(SHADOW))
    out.alpha_composite(sh)
    out.alpha_composite(edge)
    return out.crop((1, 1, FW + 1, FH + 1))


if __name__ == "__main__":
    for nm, w, mk, ic, se in (("xuan", "XUAN", "..^.", icon_peach(), "Xuan"), ("ha", "HA", ".", icon_sun(), "Ha"),
                              ("thu", "THU", "...", icon_leaf(), "Thu"), ("dong", "DONG", ".^..", icon_daisy(), "Dong")):
        pass
    sets = (("xuan", "XUAN", ["", "", "^", ""], icon_peach(), "Xuan"), ("ha", "HA", ["", "."], icon_sun(), "Ha"),
            ("thu", "THU", ["", "", ""], icon_leaf(), "Thu"), ("dong", "DONG", ["", "^", "", ""], icon_daisy(), "Dong"))
    for nm, w, mk, ic, se in sets:
        save_asset(G, f"title_{nm}", title(w, mk, ic), anchor=(FW // 2, FH // 2),
                   notes=f"Season title card {FW}x{FH} (was 88x44), hand-drawn 7x9 face, cream fill + 1px outline + drop shadow, 11x11 icon; anchor=centre. {se}.")
