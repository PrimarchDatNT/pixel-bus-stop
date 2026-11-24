from common import *

TOP, BOT = 46, 76
def xl(y): return 162 - round((y - TOP) * 20 / 30)
def xr(y): return 289 + round((y - TOP) * 20 / 30)


def roof(im):
    ramp = ['tc_l', 'tc', 'tc_d']
    dark = {'tc_l': 'tc', 'tc': 'tc_d', 'tc_d': 'tc_d'}
    light = {'tc': 'tc_l', 'tc_d': 'tc', 'tc_l': 'tc_l'}
    mods = {(1, 3): dark, (2, 5): light, (3, 2): dark, (3, 12): dark, (4, 8): light, (5, 15): dark,
            (6, 4): dark, (6, 18): light, (7, 10): dark, (7, 21): dark, (8, 6): light, (1, 17): light,
            (2, 14): dark, (5, 22): light, (4, 19): dark, (8, 15): dark, (0, 9): light, (0, 20): dark}
    for y in range(49, 76):
        r, k = (y - 49) // 3, (y - 49) % 3
        for x in range(xl(y), xr(y) + 1):
            col = ramp[k]
            t = (x - xl(49) + 3 * (r % 2)) // 6
            seam = (x - xl(49) + 3 * (r % 2)) % 6 == 0
            if seam and k == 0: col = 'tc'
            if seam and k == 1: col = 'tc_d'
            m = mods.get((r, t))
            if m and not seam: col = m.get(col, col)
            put(im, x, y, col)
    # ridge cap
    for x in range(xl(TOP) - 1, xr(TOP) + 2):
        put(im, x, 46, 'tc_l'); put(im, x, 47, 'tc'); put(im, x, 48, 'wood_d')
    for x in range(xl(TOP) - 1, xr(TOP) + 2, 4):           # cap tile joints
        put(im, x, 47, 'tc_d')
    for dx in (-2, 2):
        pass
    put(im, xl(TOP) - 2, 45, 'tc_d'); put(im, xl(TOP) - 2, 46, 'tc'); put(im, xl(TOP) - 2, 47, 'tc_d')
    put(im, xr(TOP) + 2, 45, 'tc_d'); put(im, xr(TOP) + 2, 46, 'tc'); put(im, xr(TOP) + 2, 47, 'tc_d')
    # hip ribs
    for y in range(49, 77):
        put(im, xl(y) - 1, y, 'wood_d'); put(im, xl(y), y, 'tc_l')
        put(im, xr(y) + 1, y, 'wood_k'); put(im, xr(y), y, 'tc_d')
    # eave: drip row, fascia, soffit
    for x in range(xl(76) - 1, xr(76) + 2):
        put(im, x, 76, 'wood_k')
    for x in range(xl(76), xr(76) + 1):
        put(im, x, 75, 'tc_d') if (x % 6) else put(im, x, 75, 'wood_d')
    for x in range(144, 308):
        put(im, x, 77, 'wood_d')


def dormer(im):
    x0, y0, x1, y1 = DORMER   # 206,30,230,48
    cx = (x0 + x1) // 2
    # gable roof (apex y0)
    for y in range(y0, y0 + 9):
        h = (y - y0) * 13 // 8
        for x in range(cx - h - 1, cx + h + 2):
            k = (y - y0) % 3
            put(im, x, y, ['tc_l', 'tc', 'tc_d'][k])
        put(im, cx - h - 1, y, 'wood_d'); put(im, cx + h + 1, y, 'wood_k')
    put(im, cx, y0 - 1, 'wood_d'); put(im, cx, y0 - 2, 'wood_d')
    # eave board
    rect(im, x0 - 1, y0 + 9, x1 + 1, y0 + 9, 'wood_k')
    # body
    box3(im, x0 + 2, y0 + 10, x1 - 2, y1 - 1, 'wy', 'wy_l', 'wy_d')
    rect(im, x0 + 2, y0 + 10, x1 - 2, y0 + 10, 'wy_d')
    rect(im, x0 + 2, y1 - 1, x1 - 2, y1 - 1, 'wood_d')
    # window with shutters, half open
    wx0, wy0 = cx - 5, y0 + 11
    rect(im, wx0, wy0, wx0 + 9, wy0 + 6, 'wood_k')
    rect(im, wx0 + 1, wy0 + 1, wx0 + 8, wy0 + 5, 'glass')
    line(im, wx0 + 1, wy0 + 5, wx0 + 8, wy0 + 5, 'glass_d')
    put(im, wx0 + 3, wy0 + 1, 'white'); put(im, wx0 + 2, wy0 + 2, 'white'); put(im, wx0 + 6, wy0 + 3, 'glass_l')
    line(im, wx0 + 5, wy0 + 1, wx0 + 5, wy0 + 5, 'wood_k')
    # shutters opened to the sides
    for (sx) in (wx0 - 3, wx0 + 10):
        rect(im, sx, wy0, sx + 2, wy0 + 6, 'sh')
        line(im, sx, wy0, sx, wy0 + 6, 'sh_l'); line(im, sx + 2, wy0, sx + 2, wy0 + 6, 'sh_d')
        for yy in (wy0 + 1, wy0 + 3, wy0 + 5): put(im, sx + 1, yy, 'sh_d')
    rect(im, wx0 - 1, wy0 + 7, wx0 + 10, wy0 + 7, 'wood_l')


def tank(im, x, y):
    # stainless vertical tank on legs standing on the ridge cap
    rect(im, x + 1, y + 12, x + 1, 45, 'grey_d'); rect(im, x + 8, y + 12, x + 8, 45, 'grey_d')
    line(im, x + 1, y + 15, x + 8, y + 15, 'grey_d')
    for yy in range(y + 2, y + 12):
        for xx in range(x, x + 10):
            put(im, xx, yy, 'grey_hl' if xx < x + 3 else ('grey_l' if xx < x + 6 else ('grey' if xx < x + 8 else 'grey_m')))
    for (xx, yy) in [(x + 3, y), (x + 4, y), (x + 5, y), (x + 6, y), (x + 2, y + 1), (x + 3, y + 1), (x + 4, y + 1), (x + 5, y + 1), (x + 6, y + 1), (x + 7, y + 1)]:
        put(im, xx, yy, 'grey_l' if xx < x + 5 else 'grey')
    put(im, x + 3, y, 'grey_hl'); put(im, x + 2, y + 1, 'grey_hl')
    rect(im, x, y + 12, x + 9, y + 12, 'grey_d')
    for yy in (y + 5, y + 8): line(im, x, yy, x + 9, yy, 'grey_m')
    put(im, x + 4, y - 1, 'grey_d'); put(im, x + 5, y - 1, 'grey_d')


def louvre(im, x0, y0, x1, y1):
    rect(im, x0, y0, x1, y1, 'sh')
    for y in range(y0 + 1, y1, 2):
        line(im, x0, y, x1, y, 'sh_d')
    for y in range(y0, y1, 2):
        line(im, x0, y, x1, y, 'sh_l') if False else None
    line(im, x0, y0, x0, y1, 'sh_l')
    line(im, x1, y0, x1, y1, 'sh_d')


def leaf_open(im, x0, y0, y1, side):
    """open shutter leaf (4 wide) folded against the wall"""
    louvre(im, x0, y0, x0 + 3, y1)
    line(im, x0, y0, x0 + 3, y0, 'wood_k'); line(im, x0, y1, x0 + 3, y1, 'wood_k')
    line(im, x0 + (3 if side == 'l' else 0), y0, x0 + (3 if side == 'l' else 0), y1, 'wood_k')


def window(im, x0, kind):
    """tall French window, 14 wide, y 83..113. kind: closed | glassL | dimR | glassR | dimL"""
    y0, y1 = 83, 113
    rect(im, x0 - 1, 81, x0 + 14, 82, 'wood'); line(im, x0 - 1, 81, x0 + 14, 81, 'wood_hl')
    rect(im, x0 - 1, 114, x0 + 14, 115, 'wood_l'); line(im, x0 - 1, 115, x0 + 14, 115, 'wood_d')
    rect(im, x0, y0, x0 + 13, y1, 'wood_k')
    ix0, ix1 = x0 + 1, x0 + 12
    if kind == 'closed':
        louvre(im, ix0, y0 + 1, ix0 + 5, y1 - 1); louvre(im, ix0 + 6, y0 + 1, ix1, y1 - 1)
        put(im, ix0 + 5, 98, 'grey_d'); put(im, ix0 + 6, 98, 'grey_d')
        put(im, ix0 + 5, 99, 'grey_hl')
        return
    dim = kind.startswith('dim')
    openside = 'l' if kind.endswith('L') else 'r'
    # interior
    if dim:
        rect(im, ix0, y0 + 1, ix1, y1 - 1, 'wood_d')
        rect(im, ix0, y0 + 1, ix1, y0 + 3, 'wood_k')
        # curtain
        cx0, cx1 = (ix0, ix0 + 4) if openside == 'l' else (ix1 - 4, ix1)
        rect(im, cx0, y0 + 2, cx1, y1 - 1, 'wc')
        for xx in range(cx0 + 1, cx1, 2): line(im, xx, y0 + 3, xx, y1 - 1, 'wc_d')
        line(im, cx0, y0 + 2, cx1, y0 + 2, 'wc_l')
        rect(im, ix0, y1 - 4, ix1, y1 - 1, 'wood_k')
        put(im, ix0 + 6, y1 - 7, 'yl_d'); put(im, ix0 + 6, y1 - 6, 'yl')
    else:
        rect(im, ix0, y0 + 1, ix1, y1 - 1, 'glass')
        rect(im, ix0, y0 + 1, ix1, y0 + 2, 'glass_d')
        # mullions + transom
        line(im, x0 + 6, y0 + 1, x0 + 6, y1 - 1, 'wood_k'); line(im, x0 + 7, y0 + 1, x0 + 7, y1 - 1, 'wood_d')
        line(im, ix0, y0 + 9, ix1, y0 + 9, 'wood_k')
        line(im, ix0, y1 - 8, ix1, y1 - 8, 'wood_k')
        # light curtain half
        cx0 = ix0 if openside == 'l' else x0 + 8
        for yy in range(y0 + 10, y1 - 8):
            line(im, cx0, yy, cx0 + 3, yy, 'glass_l')
        # glare strokes: long diagonals up-right, one per pane
        for i in range(4): put(im, x0 + 2 + i, y0 + 8 - i, 'white')
        for i in range(3): put(im, x0 + 8 + i, y0 + 7 - i, 'glass_l')
        for i in range(6): put(im, x0 + 2 + i, y0 + 20 - i, 'white')
        for i in range(4): put(im, x0 + 8 + i, y0 + 19 - i, 'glass_l')
        for i in range(3): put(im, x0 + 3 + i, y0 + 22 - i, 'glass_l') if False else None
    # open leaf(ves)
    if openside == 'l':
        leaf_open(im, x0 - 4, y0, y1, 'l')
    else:
        leaf_open(im, x0 + 14, y0, y1, 'r')
    # right half closed leaf for dim windows (half open look)
    if dim:
        pass


def balcony_door(im):
    x0, x1 = 252, 271
    rect(im, x0 - 1, 81, x1 + 1, 82, 'wood'); line(im, x0 - 1, 81, x1 + 1, 81, 'wood_hl')
    rect(im, x0 - 1, 83, x1 + 1, 119, 'wood_k')
    rect(im, x0, 84, x1, 119, 'wood_d')
    rect(im, x0, 84, x1, 86, 'wood_k')
    # dim interior: back wall + warm floor + hanging curtain edges
    rect(im, x0 + 1, 87, x1 - 1, 113, 'wood_d')
    rect(im, x0, 114, x1, 119, 'wood')
    line(im, x0, 114, x1, 114, 'wood_l')
    rect(im, x0 + 1, 87, x0 + 3, 113, 'wc_d'); line(im, x0 + 2, 88, x0 + 2, 112, 'wc'); line(im, x0 + 1, 88, x0 + 1, 112, 'wc_d')
    rect(im, x1 - 3, 87, x1 - 1, 113, 'wc_d'); line(im, x1 - 2, 88, x1 - 2, 112, 'wc')
    leaf_open(im, x0 - 5, 84, 119, 'l')
    leaf_open(im, x1 + 2, 84, 119, 'r')
    # transom light
    line(im, x0 + 5, 88, x1 - 5, 88, 'wood_l')


def railing(im):
    y0, y1 = 110, 119
    x0, x1 = 147, 303
    rect(im, x0, y0, x1, y0, 'wood_hl'); rect(im, x0, y0 + 1, x1, y0 + 1, 'wood_d')
    rect(im, x0, y1 - 1, x1, y1 - 1, 'wood_d')
    for x in range(x0, x1 + 1):
        m = (x - x0) % 4
        if m == 0:
            line(im, x, y0 + 2, x, y1 - 2, 'ink')
        ry = y0 + 2
        # diamond between bars: rows r1..r5 relative -> use rows ry-1.. but squeeze into 5 rows
        d = {2: [0], 1: [1], 3: [1]}
    for x in range(x0, x1 - 3, 4):
        # S-scroll / diamond in the middle of each bay
        put(im, x + 2, y0 + 3, 'ink'); put(im, x + 1, y0 + 4, 'ink'); put(im, x + 3, y0 + 4, 'ink')
        put(im, x + 1, y0 + 6, 'ink'); put(im, x + 3, y0 + 6, 'ink'); put(im, x + 2, y0 + 7, 'ink')
    for x in range(x0 + 2, x1 - 3, 8):    # finials
        put(im, x, y0 - 1, 'ink')
    for x in range(x0, x1 + 1, 28):        # posts
        rect(im, x, y0 - 2, x + 1, y1 - 1, 'wood_d'); put(im, x, y0 - 2, 'wood_hl')


def slab(im):
    x0, x1 = 147, 303
    rect(im, x0, 120, x1, 120, 'wood_hl')
    rect(im, x0, 121, x1, 122, 'wood_l')
    rect(im, x0, 123, x1, 123, 'wood_k')
    for x in range(x0 + 2, x1, 6):
        put(im, x, 122, 'wood')
    rect(im, x0 + 3, 124, x1 - 3, 124, 'wy_d')
    for x in range(x0 + 6, x1 - 4, 16):         # corbel brackets under slab
        poly(im, [(x, 124), (x + 3, 124), (x, 127)], 'wood_d')


def foliage(im, cx, cy, rx, ry, flowers=()):
    S = blob_mask([(cx, cy, rx, ry)])
    for (x, y) in S:
        nx, ny = (x - cx) / (rx + .5), (y - cy) / (ry + .5)
        s = nx * 0.6 + ny * 0.8
        col = 'leaf_l' if s < -0.45 else ('leaf_d' if s > 0.5 else 'leaf')
        if s < -0.8: col = 'leaf_hl'
        put(im, x, y, col)
    for (dx, dy, col) in flowers:
        put(im, cx + dx, cy + dy, col)


def pot(im, x, kind):
    y = 119
    rect(im, x, y - 3, x + 6, y - 3, 'tc_l')
    rect(im, x + 1, y - 2, x + 5, y, 'tc'); line(im, x + 5, y - 2, x + 5, y, 'tc_d'); line(im, x + 1, y, x + 5, y, 'tc_d')
    if kind == 'bush':
        foliage(im, x + 3, y - 7, 4, 3, [(-2, -1, 'yl'), (1, 0, 'yl_l')])
    elif kind == 'tall':
        foliage(im, x + 3, y - 9, 3, 5, [])
        put(im, x + 2, y - 12, 'or_l'); put(im, x + 4, y - 10, 'or_l')
    elif kind == 'flower':
        foliage(im, x + 3, y - 7, 4, 3, [(-2, -2, 'white'), (0, -3, 'wp_l'), (2, -1, 'white'), (-1, 0, 'wp_l')])
    elif kind == 'spike':
        for i, h in enumerate([6, 9, 7, 10, 5]):
            line(im, x + 1 + i, y - 4, x + 1 + i + (i - 2) // 2, y - 4 - h + 1, 'leaf' if i % 2 else 'leaf_l')
        line(im, x + 3, y - 4, x + 3, y - 14, 'leaf_d') if False else None


def balcony_plants(im):
    for x, k in [(160, 'flower'), (169, 'bush'), (182, 'spike'), (203, 'tall'), (214, 'flower'), (224, 'bush'),
                 (236, 'spike'), (280, 'bush'), (289, 'flower'), (296, 'tall')]:
        pot(im, x, k)
    # hanging planter on the rail near right
    rect(im, 278, 108, 285, 108, 'ink')


GOODS = {}
def item(im, kind, col, x, yb):
    """draw one product, bottom row yb; return width"""
    cd = {'or_l': 'or', 'or': 'or_d', 'yl': 'yl_d', 'yl_l': 'yl', 'teal': 'teal_d', 'pb_l': 'pb', 'pb': 'pb_d',
          'red_l': 'red', 'red': 'red_d', 'leaf_l': 'leaf', 'sh_l': 'sh', 'wp': 'wp_d', 'wc_l': 'wc', 'paper': 'wc',
          'sb_l': 'sb', 'glass_l': 'glass', 'pk': 'pk_d', 'wc': 'wc_d', 'tc_l': 'tc'}[col]
    if kind == 'box':
        rect(im, x, yb - 5, x + 3, yb, col); line(im, x + 3, yb - 5, x + 3, yb, cd); put(im, x, yb - 5, 'white') if False else None
        line(im, x, yb - 3, x + 2, yb - 3, 'paper')
        return 5
    if kind == 'bottle':
        rect(im, x, yb - 4, x + 2, yb, col); line(im, x + 2, yb - 4, x + 2, yb, cd)
        put(im, x + 1, yb - 5, col); put(im, x + 1, yb - 6, col); put(im, x + 1, yb - 7, 'grey_d')
        put(im, x, yb - 2, 'paper'); put(im, x + 1, yb - 2, 'paper')
        return 4
    if kind == 'jar':
        rect(im, x, yb - 3, x + 3, yb, 'glass_l'); rect(im, x + 1, yb - 2, x + 2, yb, col); line(im, x + 3, yb - 3, x + 3, yb, 'glass')
        rect(im, x, yb - 4, x + 3, yb - 4, col)
        return 5
    if kind == 'can':
        rect(im, x, yb - 3, x + 2, yb, col); put(im, x, yb - 3, 'grey_l'); put(im, x + 1, yb - 3, 'grey_l'); put(im, x + 2, yb - 3, 'grey')
        line(im, x + 2, yb - 2, x + 2, yb, cd)
        return 4
    if kind == 'bag':
        rect(im, x, yb - 5, x + 3, yb, col); line(im, x + 3, yb - 5, x + 3, yb, cd)
        put(im, x, yb - 5, cd); put(im, x + 2, yb - 5, cd); put(im, x + 1, yb - 2, 'paper'); put(im, x + 2, yb - 2, 'paper')
        return 5
    if kind == 'tub':
        rect(im, x, yb - 2, x + 5, yb, col); rect(im, x, yb - 3, x + 5, yb - 3, 'paper'); line(im, x + 5, yb - 2, x + 5, yb, cd)
        return 7
    return 3


def shelf(im, x0, x1, y, seq):
    """board with top at y; goods stand on y-1"""
    rect(im, x0, y, x1, y, 'wood_l'); rect(im, x0, y + 1, x1, y + 1, 'wood_k')
    x = x0 + 1
    for (k, col, n) in seq:
        for _ in range(n):
            w = {'box': 5, 'bottle': 4, 'jar': 5, 'can': 4, 'bag': 5, 'tub': 7}[k]
            if x + w > x1: return
            item(im, k, col, x, y - 1)
            x += w
        x += 1


def hang_string(im, x, y, cols):
    line(im, x, y, x, y + 1, 'wood_l')
    yy = y + 2
    for col in cols:
        rect(im, x - 1, yy, x + 1, yy + 2, col); put(im, x - 1, yy, 'paper') if False else None
        put(im, x + 1, yy + 2, 'wood_d') if False else None
        yy += 4
    return yy


def shop(im):
    # interior back wall
    rect(im, 156, 128, 293, 185, 'wood_d')
    rect(im, 156, 128, 293, 130, 'wood_k')
    for x in (157, 199, 247, 276):
        rect(im, x, 131, x, 175, 'wood_l') if False else None
    # warm alcove behind the shopkeeper (x 226-246) with valance
    rect(im, 226, 150, 246, 175, 'wood')
    for x in range(226, 247, 4):
        rect(im, x, 150, x + 3, 152, 'sb'); line(im, x, 152, x + 3, 152, 'sb_d')
        put(im, x + 1, 153, 'sb_d'); put(im, x + 2, 153, 'sb_d')
    line(im, 226, 150, 226, 175, 'wood_k'); line(im, 246, 150, 246, 175, 'wood_k')
    # shelves left bay
    cols_l = [
        [('bottle', 'teal', 3), ('bottle', 'or_l', 2), ('can', 'red_l', 3), ('jar', 'yl', 2)],
        [('box', 'yl_l', 3), ('box', 'pb_l', 3), ('box', 'sh_l', 2), ('bag', 'wp', 3)],
        [('tub', 'or_l', 3), ('tub', 'pb_l', 2), ('can', 'sb_l', 4), ('bag', 'paper', 2)],
        [('jar', 'wp', 2), ('bottle', 'sh_l', 3), ('box', 'red_l', 3), ('can', 'yl_l', 3)],
    ]
    for i, y in enumerate([141, 151, 161, 171]):
        shelf(im, 157, 198 if y == 141 else 225, y, cols_l[i])
    # right bay
    cols_r = [
        [('bag', 'or_l', 3), ('bag', 'sh_l', 3), ('box', 'pb_l', 3)],
        [('can', 'teal', 4), ('bottle', 'yl_l', 3), ('jar', 'or_l', 2)],
        [('box', 'wp', 3), ('box', 'yl_l', 3), ('tub', 'red_l', 2)],
    ]
    for i, y in enumerate([151, 161, 171]):
        shelf(im, 247, 275, y, cols_r[i])
    # fridge (drinks)
    fx0, fy0, fx1, fy1 = 278, 143, 293, 175
    box3(im, fx0, fy0, fx1, fy1, 'grey_l', 'grey_hl', 'grey_m')
    rect(im, fx0, fy0, fx1, fy0 + 3, 'grey_m'); line(im, fx0, fy0, fx1, fy0, 'grey'); 
    rect(im, fx0 + 2, fy0 + 1, fx0 + 7, fy0 + 2, 'paper'); put(im, fx0 + 3, fy0 + 1, 'teal'); put(im, fx0 + 5, fy0 + 1, 'or')
    rect(im, fx0 + 1, fy0 + 5, fx1 - 1, fy1 - 1, 'glass_d')
    rect(im, fx0 + 2, fy0 + 6, fx1 - 2, fy1 - 2, 'glass')
    for r, y in enumerate([fy0 + 12, fy0 + 19, fy0 + 26]):
        line(im, fx0 + 2, y, fx1 - 2, y, 'grey_l')
        for i, cx in enumerate(range(fx0 + 3, fx1 - 3, 3)):
            col = ['teal', 'or_l', 'red_l', 'yl_l', 'pb_l', 'sh_l'][(i + r * 2) % 6]
            rect(im, cx, y - 4, cx + 1, y - 1, col)
    for (gx, gy) in [(0, 0), (1, 1), (2, 2), (3, 3)]:
        put(im, fx0 + 4 + gx, fy0 + 7 + gy, 'white'); put(im, fx0 + 8 + gx, fy0 + 7 + gy, 'glass_l')
    line(im, fx0 + 1, fy0 + 8, fx0 + 1, fy0 + 17, 'grey_k')   # handle
    # hanging snack strings under the sign
    for x, cols in [(205, ['or_l', 'sh_l', 'pb_l']), (211, ['yl_l', 'wp', 'teal']), (217, ['red_l', 'yl_l']), (223, ['sb_l', 'or_l', 'sh_l']),
                    (250, ['yl_l', 'pb_l', 'wp']), (256, ['teal', 'or_l']), (262, ['red_l', 'sh_l', 'yl_l']), (268, ['pb_l', 'wp'])]:
        hang_string(im, x, 150, cols)
    # bare bulb above shopkeeper
    line(im, 236, 150, 236, 152, 'wood_l'); rect(im, 235, 153, 237, 154, 'lamp'); put(im, 236, 155, 'glow') if False else None
    # counter
    rect(im, 156, 176, 293, 176, 'wood_hl')
    rect(im, 156, 177, 293, 177, 'wood_l')
    rect(im, 156, 178, 293, 185, 'wood')
    rect(im, 156, 185, 293, 185, 'wood_k')
    # display case
    rect(im, 160, 179, 222, 184, 'wood_d'); rect(im, 161, 180, 221, 183, 'glass_d')
    rect(im, 161, 180, 221, 180, 'glass')
    for i, x in enumerate(range(163, 220, 6)):
        col = ['or_l', 'yl_l', 'wp', 'sh_l', 'pb_l', 'wc_l'][i % 6]
        rect(im, x, 181, x + 3, 183, col); line(im, x, 183, x + 3, 183, {'or_l': 'or', 'yl_l': 'yl', 'wp': 'wp_d', 'sh_l': 'sh', 'pb_l': 'pb', 'wc_l': 'wc'}[col])
    for x in range(168, 219, 17):
        put(im, x, 180, 'white'); put(im, x + 1, 181, 'white') if False else None
    for x in (160, 190, 222):
        line(im, x, 179, x, 184, 'wood_k')
    # right planks panels
    for x in range(226, 292, 11):
        rect(im, x, 179, x + 8, 184, 'wood_l'); rect(im, x + 1, 180, x + 7, 183, 'wood'); line(im, x + 1, 183, x + 7, 183, 'wood_d')
    # things on the counter
    rect(im, 249, 168, 253, 175, 'teal'); rect(im, 249, 168, 253, 169, 'teal_d'); put(im, 250, 171, 'white'); put(im, 250, 172, 'white')
    put(im, 251, 167, 'grey_d'); put(im, 252, 167, 'grey_d')
    for x, col in [(190, 'yl'), (196, 'or_l'), (202, 'pb_l')]:
        rect(im, x, 169, x + 4, 175, 'glass_l'); rect(im, x + 1, 171, x + 3, 175, col); rect(im, x, 168, x + 4, 168, 'red' if x == 196 else 'grey_d')
    rect(im, 208, 172, 218, 175, 'paper'); line(im, 208, 174, 218, 174, 'wc_d'); rect(im, 209, 169, 216, 171, 'wc_l'); line(im, 209, 171, 216, 171, 'grey_l')
    rect(im, 258, 171, 270, 175, 'tc'); rect(im, 258, 171, 270, 171, 'tc_l'); put(im, 260, 169, 'or_l'); put(im, 262, 170, 'leaf_l'); put(im, 265, 169, 'or'); put(im, 267, 170, 'leaf_l')
    rect(im, 280, 172, 286, 175, 'paper') if False else None


def posts(im):
    # ground-floor piers
    rect(im, 150, 128, 155, 185, 'wy'); rect(im, 150, 128, 151, 185, 'wood_l'); line(im, 150, 128, 150, 185, 'wood_hl')
    rect(im, 294, 128, 299, 185, 'wy'); rect(im, 297, 128, 299, 185, 'wood_d'); line(im, 299, 128, 299, 185, 'wood_k')
    line(im, 152, 128, 152, 185, 'wood_d')
    for x0 in (150, 294):                          # plinth
        rect(im, x0, 180, x0 + 5, 185, 'wc_d')
        line(im, x0, 180, x0 + 5, 180, 'wc'); line(im, x0 + 3, 181, x0 + 3, 185, 'grey')
        line(im, x0, 183, x0 + 5, 183, 'grey')
    # header beam above shop
    rect(im, 150, 125, 299, 127, 'wood')
    rect(im, 150, 125, 299, 125, 'wood_l'); rect(im, 150, 127, 299, 127, 'wood_d')
    for x in range(153, 297, 6): put(im, x, 126, 'wood_d')


def signs(im):
    # main sign
    sx0, sy0, sx1, sy1 = 200, 126, 268, 149
    rect(im, sx0, sy0, sx1, sy1, 'wood_k')
    rect(im, sx0 + 1, sy0 + 1, sx1 - 1, sy1 - 1, 'wc_d')
    rect(im, sx0 + 2, sy0 + 2, sx1 - 2, sy1 - 2, 'paper')
    line(im, sx0 + 2, sy0 + 2, sx1 - 2, sy0 + 2, 'white')
    line(im, sx0 + 2, sy1 - 2, sx1 - 2, sy1 - 2, 'wc')
    base = 'TAP HOA'
    w = text_size(base, 2)[0]
    tx, cap = sx0 + (sx1 - sx0 + 1 - w) // 2, 134
    text(im, tx, cap, base, 'wood_d', 2)
    def start(i): return tx + (text_size(base[:i], 2)[0] + 2 if i else 0)
    ax = start(1) + text_size('A')[0]            # centre of A (scale 2)
    rect(im, ax, cap + 12, ax + 1, cap + 13, 'wood_d')          # nang: dot below
    ox = start(5) + text_size('O')[0]
    rect(im, ox - 1, cap - 4, ox, cap - 3, 'wood_d'); rect(im, ox + 1, cap - 6, ox + 2, cap - 5, 'wood_d')   # sac
    rect(im, sx0 + 4, sy0 + 3, sx1 - 4, sy0 + 3, 'wc') ; rect(im, sx0 + 4, sy1 - 3, sx1 - 4, sy1 - 3, 'wc')
    for (x, y) in [(sx0 + 3, sy0 + 3), (sx1 - 3, sy0 + 3), (sx0 + 3, sy1 - 3), (sx1 - 3, sy1 - 3)]:
        put(im, x, y, 'wood_l')
    # small boards
    def board(x0, x1, t):
        rect(im, x0, 129, x1, 140, 'wood_d'); rect(im, x0 + 1, 130, x1 - 1, 139, 'wc_l')
        line(im, x0 + 1, 139, x1 - 1, 139, 'wc')
        tw = text_size(t)[0]
        text(im, x0 + (x1 - x0 + 1 - tw) // 2, 134, t, 'tc_d')
        put(im, x0 + 2, 128, 'wood_k'); put(im, x1 - 2, 128, 'wood_k')
    board(179, 191, 'CHÈ')
    board(271, 294, 'CÀ PHÊ')
    # lantern
    line(im, 196, 128, 196, 129, 'wood_k')
    rect(im, 194, 130, 198, 130, 'yl_d'); rect(im, 194, 131, 198, 136, 'red'); line(im, 194, 131, 194, 136, 'red_l'); line(im, 198, 131, 198, 136, 'red_d')
    rect(im, 194, 137, 198, 137, 'yl_d'); put(im, 196, 138, 'yl'); put(im, 196, 139, 'yl')
    put(im, 196, 133, 'yl_l')


def hook(im):
    rect(im, 195, 90, 197, 91, 'grey_d'); put(im, 195, 90, 'grey')
    for y in (92, 94): put(im, 196, y, 'ink')
    for y in (93, 95): put(im, 196, y, 'grey_m')
    put(im, 196, 96, 'ink'); put(im, 197, 97, 'ink'); put(im, 195, 97, 'ink'); put(im, 196, 98, 'ink')


def walls(im):
    rect(im, 150, 77, 299, 185, 'wy')
    # sunlit upper-left, shaded right
    rect(im, 150, 78, 299, 80, 'wy_d')
    for x in range(150, 300):
        if (x - 150) % 4 < 2: put(im, x, 78, 'wood_d'); put(im, x, 79, 'wood_d')
    rect(im, 150, 77, 151, 124, 'wood_l'); line(im, 150, 77, 150, 124, 'wood_hl')
    rect(im, 297, 77, 299, 124, 'wood_d'); line(im, 299, 77, 299, 124, 'wood_k')
    # plaster patches, rain stains
    def patch(x, y, w, h):
        rect(im, x, y, x + w - 1, y + h - 1, 'wc')
        for (cx, cy) in [(x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)]:
            put(im, cx, cy, 'wy')
        line(im, x + 1, y + h, x + w - 1, y + h, 'wy_d'); line(im, x + w, y + 1, x + w, y + h - 1, 'wy_d')
        line(im, x + 1, y + 1, x + 2, y + 1, 'wc_l')
    patch(171, 86, 5, 8); patch(217, 98, 7, 9); patch(241, 90, 4, 6); patch(193, 112, 4, 2) if False else None
    patch(152, 94, 3, 6); patch(152, 150, 3, 12)
    for x, y, n in [(172, 100, 8), (221, 87, 6), (192, 100, 5), (244, 100, 9), (278, 100, 6)]:
        line(im, x, y, x, y + n, 'wy_d')
    # left wall lit strips beside windows
    for x in (170, 192, 216, 240):
        pass


def pipe(im):
    rect(im, 300, 80, 301, 185, 'grey_l'); line(im, 301, 80, 301, 185, 'grey_d'); line(im, 300, 80, 300, 185, 'grey_hl')
    for y in (90, 120 + 8, 160, 182):
        rect(im, 299, y, 302, y + 1, 'grey_k')


def build():
    im = canvas()
    walls(im)
    pipe(im)
    roof(im)
    dormer(im)
    tank(im, 262, 31)
    for x, k in [(156, 'closed'), (178, 'glassL'), (202, 'dimR'), (226, 'glassR'), (282, 'dimL')]:
        window(im, x, k)
    balcony_door(im)
    shop(im)
    posts(im)
    signs(im)
    hook(im)
    slab(im)
    railing(im)
    balcony_plants(im)
    return im
