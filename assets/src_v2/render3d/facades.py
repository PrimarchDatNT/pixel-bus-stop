"""Four Hanoi tube houses: shops, signs, balconies with railings, AC units, steel water tanks."""
import random
from PIL import Image, ImageDraw
from common import *
from signs import *
from ground import HS

BASE_ROW = 216
HOUSES = [  # x0,x1, stucco colour, upper floor heights, shop text, sign bg, sign fg, roof
    (0, 150, (0.93, 0.66, 0.24), [2.0, 1.7], 'TẠP HÓA', (150, 30, 30), (255, 225, 160), 'tank'),
    (150, 300, (0.38, 0.72, 0.58), [2.0, 1.6], 'PHỞ BÒ', (200, 35, 35), (255, 235, 200), 'flat'),
    (300, 470, (0.95, 0.52, 0.40), [2.1], 'CẮT TÓC', (14, 74, 150), (255, 255, 255), 'tile'),
    (470, 640, (0.40, 0.50, 0.78), [2.0, 1.9], 'ĐIỆN MÁY', (14, 90, 150), (255, 240, 120), 'tank'),
]

def shutter_tex(path, w, h):
    a = Image.new('RGB', (w, h)); px = a.load()
    for y in range(h):
        for x in range(w):
            k = y % 4
            v = [168, 150, 120, 104][k]
            px[x, y] = (v, v + 4, v + 14)
    a.save(path); return path

def build(colls, work):
    c = colls['facades']; rnd = random.Random(21)
    Yf0 = Yrow(BASE_ROW, HS)
    stucco_n = 0
    for hi, (px0, px1, col, floors, text, sbg, sfg, roof) in enumerate(HOUSES):
        stagger = [0.0, 0.5, 0.2, 0.7][hi]
        Yf = Yf0 + stagger; x0, x1 = X(px0), X(px1); w = x1 - x0; cx = (x0 + x1) / 2
        SHOP = 2.75
        Hs = SHOP + sum(floors)
        depth = 4.5
        wall = mat(f'wall{hi}', col, 0.82, spec=0.3)
        trim = mat(f'trim{hi}', tuple(min(1, v * 1.12 + 0.07) for v in col), 0.75)
        dtrim = mat(f'dtrim{hi}', tuple(v * 0.55 for v in col), 0.8)
        box(f'body{hi}', (cx, Yf + depth / 2, HS + Hs / 2), (w - 0.06, depth, Hs), wall, bevel=0.03, coll=c)
        # cornices at every floor line + parapet
        zs = [SHOP]; 
        for f in floors: zs.append(zs[-1] + f)
        for z in zs:
            box('cornice', (cx, Yf - 0.07, HS + z), (w - 0.02, 0.16, 0.14), trim, bevel=0.04, coll=c)
        box('plinth', (cx, Yf - 0.03, HS + 0.18), (w - 0.04, 0.10, 0.36), dtrim, bevel=0.03, coll=c)
        # pilasters at edges
        for sx in (x0 + 0.1, x1 - 0.1):
            box('pil', (sx, Yf - 0.04, HS + Hs / 2), (0.2, 0.1, Hs), trim, bevel=0.03, coll=c)
        # ---- shop front
        sw0, sw1 = x0 + 0.55, x1 - 0.55
        dark = mat('shopdark', (0.07, 0.05, 0.05), 0.6)
        box('shopcav', ((sw0 + sw1) / 2, Yf - 0.04, HS + 1.21), (sw1 - sw0, 0.05, 1.7), dark, coll=c)
        # interior: shelves with colourful goods
        for k in range(int((sw1 - sw0) / 0.45)):
            for lv in range(3):
                if rnd.random() < 0.75:
                    gc = rnd.choice([(0.9, 0.2, 0.1), (0.95, 0.75, 0.1), (0.2, 0.6, 0.9), (0.9, 0.9, 0.85), (0.2, 0.7, 0.3), (0.9, 0.4, 0.7)])
                    box('good', (sw0 + 0.3 + k * 0.45, Yf - 0.1, HS + 0.55 + lv * 0.5), (0.30, 0.1, 0.30), mat('good', tuple(v * 0.7 for v in gc), 0.5, emit=gc, emit_k=0.06), bevel=0.03, coll=c)
        # roll-up shutter (half open) with painted corrugation
        shw = int((sw1 - sw0) * PPM); sh_h = int(0.95 * PPM * CP)
        st = shutter_tex(f'{work}/tx_shut{hi}.png', shw, sh_h)
        sm = tex_mat('shut', st, rough=0.35, metal=0.7, spec=0.5)
        pix_plane('shutter', int(sw0 * PPM), int(row_of(Yf - 0.1, HS + 2.0)), shw, sh_h, Yf - 0.1, sm, c)
        box('shbox', ((sw0 + sw1) / 2, Yf - 0.1, HS + 2.04), (sw1 - sw0 + 0.1, 0.18, 0.16), mat('shbox', (0.55, 0.57, 0.62), 0.3, metal=0.8), bevel=0.04, coll=c)
        for sx in (sw0, sw1):
            box('shframe', (sx, Yf - 0.09, HS + 1.2), (0.1, 0.12, 1.75), trim, bevel=0.03, coll=c)
        # sign
        tw = min(int((sw1 - sw0) * PPM) - 6, 70); th = 17
        t = sign_tex(f'{work}/tx_sign{hi}.png', text, tw, th, sbg, sfg, size=10, border=tuple(min(255, int(v * 1.3 + 30)) for v in sfg), shadow=tuple(int(v * 0.4) for v in sbg))
        sg = tex_mat('sign', t, rough=0.35, spec=0.5, emit_k=0.2, coat=0.5)
        scol = int(cx * PPM - tw / 2)
        pix_plane('shopsign', scol, int(row_of(Yf - 0.26, HS + 2.72)), tw, th, Yf - 0.26, sg, c)
        box('signback', (cx, Yf - 0.13, HS + 2.37), (tw / PPM + 0.12, 0.18, th / (PPM * CP) + 0.1), dtrim, bevel=0.03, coll=c)
        # vertical hanging side sign
        if hi in (1, 3):
            vt = sign_tex(f'{work}/tx_vs{hi}.png', 'QUÁN' if hi == 1 else 'BH', 12, 38, (255, 215, 60), (190, 20, 20), size=9, border=(190, 20, 20))
        # ---- upper floors
        zb = SHOP
        for fi, fh in enumerate(floors):
            nwin = 2 if w < 6.0 else 3
            wwid, whei = 0.95, 1.35
            gaps = w / nwin
            glass = mat('wglass', (0.03, 0.09, 0.14), 0.05, coat=1.0, coat_rough=0.0, spec=1.0)
            for k in range(nwin):
                wx = x0 + gaps * (k + 0.5)
                wz = HS + zb + fh * 0.5 - 0.05
                balcony = (fi == 0 and k == nwin // 2) or (fi == 1 and rnd.random() < 0.35)
                if balcony:
                    # glass door + balcony slab and railing
                    box('door', (wx, Yf - 0.02, HS + zb + 1.0), (wwid + 0.1, 0.06, 1.9), glass, bevel=0.01, coll=c)
                    box('doorframe', (wx, Yf - 0.04, HS + zb + 1.0), (wwid + 0.2, 0.05, 2.0), trim, bevel=0.02, coll=c)
                    box('doormid', (wx, Yf - 0.07, HS + zb + 1.0), (0.05, 0.05, 1.9), trim, coll=c)
                    bw = wwid + 1.2; by = Yf - 0.6
                    box('slab', (wx, by, HS + zb + 0.07), (bw, 1.1, 0.14), trim, bevel=0.04, coll=c)
                    rail = mat('rail', (0.07, 0.08, 0.12), 0.4, metal=0.7)
                    ny = by - 0.55 + 0.03
                    box('rtop', (wx, ny, HS + zb + 1.0), (bw, 0.05, 0.06), rail, bevel=0.015, coll=c)
                    nb = int(bw / 0.17)
                    for q in range(nb + 1):
                        bx = wx - bw / 2 + 0.04 + q * (bw - 0.08) / nb
                        box('bar', (bx, ny, HS + zb + 0.55), (0.034, 0.034, 0.88), rail, coll=c)
                    for sx in (-1, 1):
                        box('rside', (wx + sx * (bw / 2 - 0.03), by - 0.25, HS + zb + 1.0), (0.05, 1.1 - 0.1, 0.06), rail, coll=c)
                        for q in range(5):
                            box('bar', (wx + sx * (bw / 2 - 0.03), by - 0.75 + q * 0.28 + 0.2, HS + zb + 0.55), (0.034, 0.034, 0.88), rail, coll=c)
                    # potted plants
                    for q in range(rnd.randint(1, 3)):
                        pxp = wx - bw / 2 + 0.25 + rnd.random() * (bw - 0.5)
                        box('pot', (pxp, ny - 0.15, HS + zb + 0.3), (0.24, 0.24, 0.16), mat('pot', (0.7, 0.3, 0.2), 0.6), bevel=0.03, coll=c)
                        sphere('plant', (pxp, ny - 0.15, HS + zb + 0.5), (0.2, 0.2, 0.22), mat('plant', (0.1, 0.45, 0.12), 0.6, sss=0.3), coll=c)
                    # laundry
                    if rnd.random() < 0.75:
                        for q in range(rnd.randint(2, 4)):
                            lc = rnd.choice([(0.95, 0.9, 0.9), (0.9, 0.2, 0.3), (0.2, 0.5, 0.9), (0.95, 0.85, 0.2), (0.3, 0.75, 0.4)])
                            box('cloth', (wx - bw / 2 + 0.2 + q * 0.34, ny - 0.04, HS + zb + 1.55), (0.22, 0.015, 0.5), mat('cloth', lc, 0.9), coll=c)
                        box('wire', (wx, ny - 0.04, HS + zb + 1.82), (bw, 0.012, 0.012), rail, coll=c)
                else:
                    ww = mat('win', (0.03, 0.09, 0.14), 0.05, coat=1.0, coat_rough=0.0, spec=1.0)
                    box('win', (wx, Yf - 0.02, wz), (wwid, 0.06, whei), ww, bevel=0.01, coll=c)
                    fr = mat('frame', (0.92, 0.92, 0.9), 0.5)
                    box('fl', (wx - wwid / 2 - 0.03, Yf - 0.05, wz), (0.07, 0.07, whei + 0.14), fr, coll=c)
                    box('fr_', (wx + wwid / 2 + 0.03, Yf - 0.05, wz), (0.07, 0.07, whei + 0.14), fr, coll=c)
                    box('ft', (wx, Yf - 0.05, wz + whei / 2 + 0.03), (wwid + 0.14, 0.07, 0.07), fr, coll=c)
                    box('fb', (wx, Yf - 0.1, wz - whei / 2 - 0.03), (wwid + 0.2, 0.2, 0.08), trim, bevel=0.03, coll=c)
                    box('fm', (wx, Yf - 0.05, wz), (0.05, 0.06, whei), fr, coll=c)
                    if (hi + k + fi) % 2 == 0:       # green louvre shutters
                        shm = mat('shut', (0.12, 0.38, 0.22), 0.45, coat=0.3)
                        for sx in (-1, 1):
                            box('shutter', (wx + sx * (wwid / 2 + 0.28), Yf - 0.06, wz), (0.42, 0.05, whei + 0.1), shm, bevel=0.015, coll=c)
                            for q in range(8):
                                box('louv', (wx + sx * (wwid / 2 + 0.28), Yf - 0.09, wz - whei / 2 + 0.08 + q * 0.16), (0.38, 0.03, 0.05), mat('lv', (0.06, 0.24, 0.14), 0.5), coll=c)
                    # AC unit on a wall bracket
                    if rnd.random() < 0.45:
                        axx = wx + (wwid / 2 + 0.75) * (1 if (k + fi) % 2 == 0 else -1)
                        if x0 + 0.5 < axx < x1 - 0.5 and not (hi + k + fi) % 2 == 0:
                            box('ac', (axx, Yf - 0.25, wz + 0.2), (0.78, 0.42, 0.52), mat('ac', (0.92, 0.94, 0.96), 0.35, coat=0.6), bevel=0.06, coll=c)
                            box('acg', (axx, Yf - 0.47, wz + 0.2), (0.6, 0.02, 0.3), mat('acg', (0.1, 0.12, 0.16), 0.4, metal=0.5), coll=c)
            zb += fh
        # ---- roof
        ztop = HS + Hs
        box('parapet', (cx, Yf - 0.04, ztop + 0.18), (w, 0.3, 0.36), trim, bevel=0.05, coll=c)
        steel = mat('tank', (0.9, 0.93, 0.97), 0.16, metal=1.0)
        if roof == 'tank':
            for q, tx in enumerate([cx - 1.0, cx + 1.3] if w > 5.5 else [cx]):
                cyl('tank', (tx, Yf + 0.9, ztop + 0.36 + 0.5), 0.52, 1.0, steel, segs=32, bevel=0.02, coll=c)
                sphere('tankcap', (tx, Yf + 0.9, ztop + 0.36 + 1.0), (0.52, 0.52, 0.2), steel, coll=c)
                for lx in (-0.36, 0.36):
                    box('tleg', (tx + lx, Yf + 0.9, ztop + 0.36 + 0.18), (0.06, 0.06, 0.36), mat('tleg', (0.1, 0.1, 0.15), 0.5, metal=0.6), coll=c)
            # antenna
            ax = x1 - 0.8; rail = mat('ant', (0.12, 0.12, 0.16), 0.5, metal=0.5)
            tube('ant', [(ax, Yf + 1.2, ztop + 0.36), (ax, Yf + 1.2, ztop + 2.2)], 0.025, rail, c, res=3)
            for q in range(4): box('antb', (ax, Yf + 1.2, ztop + 1.2 + q * 0.28), (0.9 - q * 0.17, 0.03, 0.03), rail, coll=c)
        elif roof == 'tile':
            tile = mat('tile', (0.62, 0.20, 0.10), 0.4, coat=0.5)
            th_ = math.radians(27)
            box('tileroof', (cx, Yf + 0.95, ztop + 0.36 + 0.42), (w + 0.2, 2.1, 0.12), tile, bevel=0.03, coll=c, rot=(th_, 0, 0))
            box('ridge', (cx, Yf + 1.95, ztop + 0.36 + 0.9), (w + 0.25, 0.25, 0.16), mat('ridge', (0.55, 0.2, 0.12), 0.5), bevel=0.05, coll=c)
            # horizontal tile courses along the slope
            cs, sn = math.cos(th_), math.sin(th_)
            for q in range(11):
                u = -1.0 + q * 0.19
                pc = Vector((cx, Yf + 0.95 + cs * u - sn * 0.075, ztop + 0.36 + 0.42 + sn * u + cs * 0.075))
                box('course', tuple(pc), (w + 0.18, 0.05, 0.07), mat('course', (0.48, 0.14, 0.07), 0.45), bevel=0.02, coll=c, rot=(th_, 0, 0))
        else:
            cyl('tank', (cx + 1.4, Yf + 1.1, ztop + 0.36 + 0.45), 0.45, 0.9, steel, segs=28, bevel=0.02, coll=c)
            sphere('tankcap', (cx + 1.4, Yf + 1.1, ztop + 0.36 + 0.9), (0.45, 0.45, 0.18), steel, coll=c)
            box('dish', (cx - 1.4, Yf + 1.0, ztop + 0.9), (0.7, 0.08, 0.7), mat('dish', (0.9, 0.9, 0.92), 0.4, metal=0.5), bevel=0.2, coll=c)
