"""Steel bus shelter, blue bucket seats, bougainvillea in full bloom."""
import random, colorsys
from common import *
from signs import *
from ground import HS

SX0, SX1 = 213, 372

def build(colls, work):
    c = colls['shelter']; rnd = random.Random(7)
    YF, YB = Yrow(232, HS), Yrow(224, HS)
    steel = mat('steel', (0.58, 0.64, 0.74), 0.26, metal=1.0)
    dark = mat('darksteel', (0.10, 0.14, 0.22), 0.35, metal=0.6, coat=0.5)
    roofm = mat('roof', (0.07, 0.30, 0.50), 0.3, coat=1.0, coat_rough=0.05)
    glass = mat('glass', (0.015, 0.05, 0.075), 0.04, coat=1.0, coat_rough=0.0, spec=1.0)
    x0, x1 = X(SX0), X(SX1)
    H = 2.58 - 0.0
    # ---- posts
    for (px, py) in [(x0 + .25, YF), (x1 - .25, YF), (x0 + .25, YB), (x1 - .25, YB), ((x0 + x1) / 2 - 1.1, YB), ((x0 + x1) / 2 + 1.7, YB)]:
        box('post', (px, py, HS + H / 2), (0.11, 0.11, H), steel, bevel=0.025, coll=c)
    # ---- roof (slight rake toward the back) with blue fascia
    roof_z = HS + H + 0.07
    box('roof', ((x0 + x1) / 2, (YF + YB) / 2 - 0.1, roof_z), (x1 - x0, YB - YF + 0.9, 0.14), roofm, bevel=0.05, coll=c)
    box('roof_trim', ((x0 + x1) / 2, YF - 0.5, roof_z - 0.05), (x1 - x0 + 0.04, 0.10, 0.26), dark, bevel=0.03, coll=c)
    box('roof_rib', ((x0 + x1) / 2, (YF + YB) / 2 - 0.1, roof_z + 0.09), (x1 - x0 - 0.4, 0.12, 0.05), steel, bevel=0.015, coll=c)
    # fascia sign "TRẠM XE BUÝT"
    t = sign_tex(f'{work}/tx_tram.png', 'TRẠM XE BUÝT', 84, 17, (14, 74, 150), (255, 255, 255), size=10, border=(150, 205, 255), shadow=(6, 30, 80))
    sm = tex_mat('tram', t, rough=0.35, spec=0.6, emit_k=0.35, coat=0.6)
    pix_plane('tram', 256, 176, 84, 17, YF - 0.6, sm, c)
    # ---- back wall: dark glass panels + lightbox poster
    for i, (gx0, gx1) in enumerate([(x0 + .31, (x0 + x1) / 2 - 1.16), ((x0 + x1) / 2 - 1.04, (x0 + x1) / 2 + 1.64), ((x0 + x1) / 2 + 1.76, x1 - .31)]):
        box(f'glass{i}', ((gx0 + gx1) / 2, YB + 0.02, HS + 0.45 + 1.05), (gx1 - gx0, 0.04, 2.1), glass, bevel=0.01, coll=c)
    box('kick', ((x0 + x1) / 2, YB + 0.02, HS + 0.22), (x1 - x0 - .3, 0.06, 0.44), dark, bevel=0.02, coll=c)
    box('railtop', ((x0 + x1) / 2, YB + 0.02, HS + 2.53), (x1 - x0 - .3, 0.08, 0.1), steel, bevel=0.02, coll=c)
    # poster lightbox on the left glass
    poster(f'{work}/tx_poster.png')
    pm = tex_mat('poster', f'{work}/tx_poster.png', rough=0.2, spec=0.6, emit_k=0.10, coat=0.4)
    pw, ph = 38, 54
    box('lbframe', (x0 + 1.15, YB - 0.04, HS + 1.35), (pw / PPM + .12, 0.16, ph / (PPM * CP) + .12), steel, bevel=0.03, coll=c)
    pix_plane('poster', int(SX0 + 1.15 * PPM - pw / 2 + 1), 0, pw, ph, YB - 0.14, pm, c)
    # fix poster row: put it so bottom sits ~Z=0.7
    ob = c.objects['poster']; ob.location.z = HS + 1.35
    # ---- glare streaks on glass
    gx = (x0 + x1) / 2
    for dx, w in ((0.0, 0.28), (0.45, 0.10), (1.9, 0.30), (2.4, 0.09)):
        glare('glare', [(gx + dx, HS + 0.55), (gx + dx + w, HS + 0.55), (gx + dx + w + 0.75, HS + 2.4), (gx + dx + 0.75, HS + 2.4)], YB - 0.03, c, k=0.16)
    # ---- bench + bucket seats
    seat_blue = mat('seatblue', (0.03, 0.22, 0.95), 0.12, coat=1.0, coat_rough=0.03, spec=0.8)
    ys = Yrow(228, HS) + 0.2
    n, pitch = 4, 0.62; bx0 = (x0 + x1) / 2 - 0.2 - (n - 1) * pitch / 2
    box('bench_beam', ((x0 + x1) / 2 - 0.2, ys, HS + 0.30), (n * pitch + 0.1, 0.10, 0.09), steel, bevel=0.02, coll=c)
    for k in range(n):
        sx = bx0 + k * pitch
        sphere('pan', (sx, ys - 0.02, HS + 0.45), (0.27, 0.27, 0.05), seat_blue, coll=c)
        box('panrim', (sx, ys - 0.02, HS + 0.43), (0.50, 0.46, 0.05), seat_blue, bevel=0.035, coll=c)
        bk = box('back', (sx, ys + 0.20, HS + 0.74), (0.48, 0.07, 0.48), seat_blue, bevel=0.035, coll=c, rot=(math.radians(-12), 0, 0))
        sphere('backdish', (sx, ys + 0.165, HS + 0.74), (0.20, 0.03, 0.19), seat_blue, coll=c, rot=(math.radians(-12), 0, 0))
        box('stem', (sx, ys + 0.14, HS + 0.36), (0.06, 0.06, 0.20), dark, coll=c)
    for sx in (bx0 - 0.4, bx0 + (n - 1) * pitch + 0.4):
        box('leg', (sx, ys, HS + 0.15), (0.07, 0.07, 0.30), steel, bevel=0.02, coll=c)
    for k in range(n - 1):
        box('div', (bx0 + (k + .5) * pitch, ys - 0.02, HS + 0.56), (0.04, 0.40, 0.14), dark, bevel=0.015, coll=c)
    # ---- route sign on right post: "32"
    t = sign_tex(f'{work}/tx_32.png', '32', 17, 20, (14, 74, 150), (255, 255, 255), size=12, border=(150, 205, 255))
    pix_plane('sign32', SX1 - 20, 170, 17, 20, YF - 0.07, tex_mat('s32', t, rough=0.3, coat=0.6, emit_k=0.3), c)
    bougainvillea(c, x0, x1, YF, YB, roof_z, rnd)

def poster(path):
    from PIL import Image, ImageDraw
    w, h = 38, 54
    im = Image.new('RGB', (w, h), (214, 226, 242)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, 8], fill=(14, 74, 150))
    d.text((3, -1), 'Tuyến', fill=(255, 255, 255), font=ImageFont.truetype(FONT_B, 8))
    cols = [(220, 40, 60), (20, 150, 90), (250, 160, 20)]
    pts = [[(4, 16), (12, 22), (20, 20), (30, 32), (34, 46)], [(5, 48), (14, 38), (22, 36), (30, 24)], [(4, 30), (14, 30), (24, 44)]]
    for col, ps in zip(cols, pts):
        d.line(ps, fill=col, width=3)
        for p in ps: d.rectangle([p[0] - 1, p[1] - 1, p[0] + 1, p[1] + 1], fill=(255, 255, 255), outline=col)
    im.save(path)

def bougainvillea(c, x0, x1, YF, YB, roof_z, rnd):
    bm = bmesh.new(); col = bm.loops.layers.color.new('col')
    leaf_bm = bmesh.new(); lcol = leaf_bm.loops.layers.color.new('col')
    pinks = [(0.98, 0.10, 0.50), (1.0, 0.16, 0.60), (0.88, 0.04, 0.45), (1.0, 0.38, 0.70), (0.95, 0.08, 0.62), (1.0, 0.62, 0.82), (0.72, 0.02, 0.38), (1.0, 0.84, 0.92)]
    wts = [3, 3, 2, 3, 2, 1.4, 0.8, 0.5]
    greens = [(0.07, 0.32, 0.07), (0.15, 0.48, 0.10), (0.30, 0.60, 0.14), (0.05, 0.22, 0.10)]

    def add_bract(b, layer, p, size, color, tilt=None):
        m = bmesh.new()
        bmesh.ops.create_uvsphere(m, u_segments=6, v_segments=4, radius=1.0)
        sx, sy, sz = size
        bmesh.ops.scale(m, vec=Vector((sx, sy, sz)), verts=m.verts)
        R = Euler((rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), rnd.uniform(0, 6.28))).to_matrix().to_4x4() if tilt is None else tilt
        bmesh.ops.transform(m, matrix=Matrix.Translation(p) @ R, verts=m.verts)
        vm = {}
        for v in m.verts: vm[v] = b.verts.new(v.co)
        for f in m.faces:
            nf = b.faces.new([vm[v] for v in f.verts]); nf.smooth = True
            for l in nf.loops: l[layer] = (*color, 1)
        m.free()

    def pick_pink():
        r = rnd.random() * sum(wts); a = 0
        for p, w in zip(pinks, wts):
            a += w
            if r <= a: return p
        return pinks[0]

    def flower(p, s=1.0, depth01=0.5):
        base = pick_pink()
        shade = 0.50 + 0.50 * depth01          # deeper = darker, richer
        cl = (base[0] * shade, base[1] * shade, base[2] * (0.8 + 0.2 * shade))
        ang0 = rnd.uniform(0, 6.28)
        nrm = Euler((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(0, 6.28)))
        for k in range(3):
            a = ang0 + k * 2.094
            off = Vector((math.cos(a), math.sin(a), 0)) * 0.045 * s
            R = nrm.to_matrix().to_4x4()
            off = R @ off
            add_bract(bm, col, p + off, (0.075 * s, 0.062 * s, 0.020 * s), cl, tilt=(R @ Euler((rnd.uniform(-.5, .5), rnd.uniform(-.5, .5), a)).to_matrix().to_4x4()))

    def leaf(p, s=1.0):
        g = rnd.choice(greens)
        add_bract(leaf_bm, lcol, p, (0.085 * s, 0.040 * s, 0.012 * s), g)

    cx = (x0 + x1) / 2
    # ---- canopy over roof: thick lumpy dome, flowers biased toward the lit surface
    def lump(x, y):
        return (math.sin(x * 2.3 + 1.1) * 0.5 + math.sin(x * 4.9 + y * 3.1) * 0.35 + math.sin(y * 5.3 - x * 1.7) * 0.25)
    xl, xr = x0 - 0.7, x1 + 0.45
    ya, yb_ = YF - 0.75, YB + 0.45
    for i in range(9500):
        x = rnd.uniform(xl, xr); y = rnd.uniform(ya, yb_)
        ex = min((x - xl) / 1.1, (xr - x) / 1.1, 1.0); ey = min((y - ya) / 0.8, (yb_ - y) / 0.8, 1.0)
        edge = max(0.0, min(ex, ey))
        prof = math.sqrt(edge)                                # dome-ish
        left = 1.0 - 0.5 * (x - xl) / (xr - xl)
        h = (0.15 + 1.25 * left * prof) * (0.78 + 0.22 * lump(x, y)) + 0.1
        if rnd.random() > 0.08 + 0.92 * min(1, edge * 2.2): continue
        u = rnd.random(); d01 = u
        z = roof_z + 0.02 + h * (1 - u ** 2.4)               # concentrated at top
        flower(Vector((x, y, z)), s=rnd.uniform(1.25, 1.85), depth01=1 - u ** 0.6)
        if rnd.random() < 0.34: leaf(Vector((x, y, z + 0.02 * rnd.random())), rnd.uniform(1.5, 2.4))
    # ---- spill over the front edge: hanging drapes
    for k in range(40):
        x = rnd.uniform(x0 - 0.4, x1 - 0.2)
        if 262 / PPM < x < 336 / PPM and rnd.random() < 0.85: continue
        L = rnd.uniform(0.3, 1.25) * (1.25 - 0.55 * (x - x0) / (x1 - x0))
        n = int(L / 0.11)
        sway = rnd.uniform(-0.12, 0.12)
        for j in range(n):
            t = j / max(1, n - 1)
            p = Vector((x + sway * t + rnd.uniform(-0.06, 0.06), YF - 0.62 - rnd.uniform(0, 0.12) * t, roof_z + 0.15 - t * L - 0.02 * j))
            flower(p, s=rnd.uniform(0.85, 1.3) * (1.0 - 0.25 * t), depth01=0.9 - 0.5 * t)
            if rnd.random() < 0.25: leaf(p + Vector((rnd.uniform(-.05, .05), 0.05, 0)), rnd.uniform(1, 1.8))
    # ---- climbing the left pillar: column of bloom
    px, py = x0 + 0.25, YF
    for i in range(900):
        z = HS + 0.25 + (roof_z - HS - 0.3) * (rnd.random() ** 0.75)
        w = 0.40 * (1.0 - 0.45 * (z - HS) / 2.6) + 0.12
        a = rnd.uniform(0, 6.28); rr = w * rnd.uniform(0.35, 1.0)
        p = Vector((px + math.cos(a) * rr - 0.1, py - abs(math.sin(a)) * rr * 0.9 + 0.1, z))
        flower(p, s=rnd.uniform(0.9, 1.35), depth01=rnd.random())
        if rnd.random() < 0.3: leaf(p, rnd.uniform(1, 1.8))
    # ---- fallen petals on sidewalk
    for i in range(24):
        p = Vector((x0 + rnd.uniform(-0.4, 1.8), YF + rnd.uniform(-0.9, 0.7), HS + 0.015))
        add_bract(bm, col, p, (0.05, 0.04, 0.012), pick_pink(), tilt=Euler((0, 0, rnd.uniform(0, 6.28))).to_matrix().to_4x4())
    bract_mat = vcol_mat('bract', rough=0.38, sss=0.25, trans_mix=0.3, spec=0.6, emit=0.22)
    leaf_mat = vcol_mat('leaf', rough=0.5, sss=0.3, trans_mix=0.3, spec=0.35)
    finish('bracts', bm, bract_mat, coll=c, shade=False)
    finish('leaves', leaf_bm, leaf_mat, coll=c, shade=False)
    # ---- woody vine climbing left pillar
    wood = mat('wood', (0.16, 0.09, 0.06), 0.8)
    pts = [(px - 0.5, YF - 0.3, HS), (px - 0.3, YF - 0.1, HS + 0.5), (px - 0.12, YF - 0.02, HS + 1.2), (px - 0.05, YF, HS + 2.0), (px + 0.1, YF - 0.1, roof_z)]
    tube('vine', pts, 0.045, wood, c)
    tube('vine2', [(px - 0.5, YF - 0.3, HS), (px - 0.62, YF - 0.5, HS + 0.12), (px - 0.8, YF - .6, HS)], 0.04, wood, c)
    # a small planter at the foot
    box('planter', (px - 0.45, YF - 0.35, HS + 0.12), (0.8, 0.55, 0.24), mat('planter', (0.45, 0.2, 0.15), 0.6), bevel=0.04, coll=c)
