"""Hanoi-style city bus, facing left, driver's (near) side visible. Lattice body with real window holes + interior."""
import math, random
from common import *
from signs import *
from ground import HS

L, HW = 9.4, 1.25
ZB, ZS, ZT = 0.40, 2.25, 2.60
WINDOWS = [(1.05, 2.40), (2.55, 3.62), (3.77, 4.84), (4.99, 6.06), (6.21, 7.28), (7.43, 8.50), (8.65, 9.05)]
WZ0, WZ1 = 1.30, 2.10
AXLES = [1.55, 7.05]
WR = 0.5; ARCH = 0.585

def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def warp(x, y, z):
    t = max(0.0, min(1.0, (z - ZB) / (ZT - ZB)))
    b = 0.19 * math.sin(math.pi * t) ** 0.9
    ay = abs(y); sg = 1 if y >= 0 else -1
    y = sg * (ay + b * smoothstep(0.3, 1.0, ay / HW))
    if z > 1.85:
        u = (z - 1.85) / (ZT - 1.85); y *= 1 - 0.07 * u * u
    # raked windshield
    sh = 1.15 * (max(0.0, min(1.0, (z - 0.95) / 1.65)) ** 1.15)
    x = x + sh * max(0.0, 1 - x / 1.55)
    # tail slight rake
    st = 0.28 * (max(0.0, min(1.0, (z - 1.9) / 0.7)) ** 1.3)
    x = x - st * max(0.0, 1 - (L - x) / 1.2)
    # rounded ends (plan view)
    d = min(x - (sh if x < 1.55 else 0) * 0 , L - x)
    return x, y, z

def end_inset(x):
    r = 0.16; d = min(x, L - x)
    return 0.0 if d >= r else r - math.sqrt(max(0.0, r * r - (r - d) ** 2))

def profile(zlines):
    rc, rs = 0.2, 0.35
    P = [(0.0, ZB)]
    for i in range(1, 10): P.append((-(HW - rc) * i / 9, ZB))
    for k in range(1, 7):
        a = math.radians(-90 - 90 * k / 6); P.append((-(HW - rc) + rc * math.cos(a), ZB + rc + rc * math.sin(a)))
    z = ZB + rc
    zs = sorted(set([round(v, 4) for v in zlines if ZB + rc < v < ZS] + [round(ZB + rc + 0.045 * i, 4) for i in range(1, int((ZS - ZB - rc) / 0.045))]))
    for z in zs: P.append((-HW, z))
    for k in range(0, 9):
        a = math.radians(180 - 90 * k / 8); P.append((-(HW - rs) + rs * math.cos(a), ZS + rs * math.sin(a) * 1.0))
    # roof crown
    ytop = -(HW - rs)
    for i in range(1, 12):
        y = ytop * (1 - i / 11); P.append((y, ZT - 0.0 + 0.045 * (1 - (y / ytop) ** 2)))
    return P

def build(colls, work):
    c = colls['bus']; rnd = random.Random(3)
    root = bpy.data.objects.new('busroot', None); c.objects.link(root)
    Yw = Yrow(275, 0)
    root.location = (X(548) - L / 2, Yw + HW - 0.2, 0.0)
    before = set(bpy.data.objects)

    # ---------- materials
    orange = mat('b_orange', (0.95, 0.36, 0.015), 0.28, metal=0.25, coat=1.0, coat_rough=0.015)
    red = mat('b_red', (0.78, 0.015, 0.03), 0.28, metal=0.2, coat=1.0, coat_rough=0.015)
    white = mat('b_white', (0.95, 0.93, 0.88), 0.3, coat=1.0, coat_rough=0.02)
    roofm = mat('b_roof', (0.62, 0.70, 0.82), 0.3, metal=0.3, coat=1.0, coat_rough=0.02)
    skirt = mat('b_skirt', (0.06, 0.06, 0.09), 0.5, metal=0.4)
    glass_far = mat('b_glassf', (0.01, 0.03, 0.05), 0.04, coat=1.0, coat_rough=0.0, spec=1.0)
    chrome = mat('chrome', (0.9, 0.93, 1.0), 0.07, metal=1.0)
    rubber = mat('rubber', (0.025, 0.025, 0.03), 0.7)
    glass = mat('b_glass', (0.01, 0.05, 0.08), 0.03, coat=1.0, coat_rough=0.0, spec=1.0, alpha=0.55)

    # ---------- lattice body
    zlines = [1.0, 1.06, WZ0, WZ1]
    P = profile(zlines)
    near = P; 
    ring = near + [(-y, z) for (y, z) in reversed(near[:-1])][:-0 or None]
    # drop duplicate bottom centre handled by closed loop; remove last mirrored point == (0,ZB)
    ring = near + [(-y, z) for (y, z) in reversed(near[1:-1])]
    ring_mid = len(near)                       # index range of near half = [0, len(near)-1]
    xs = {0.0, 0.03, 0.075, 0.14, L, L - 0.03, L - 0.075, L - 0.14}
    for (a, b) in WINDOWS: xs.add(round(a, 4)); xs.add(round(b, 4))
    i = 0
    while i * 0.11 < L: xs.add(round(i * 0.11, 4)); i += 1
    xs = sorted(xs); xx = [xs[0]]
    for v in xs[1:]:
        if v - xx[-1] > 0.02: xx.append(v)
    bm = bmesh.new()
    holes = []
    V = []
    for x in xx:
        ins = end_inset(x); row = []
        for (y, z) in ring:
            yy = y - math.copysign(ins, y) if abs(y) > 0.05 else y
            zz = z - ins if z > 1.5 else (z + ins if z < 1.5 and False else z)
            if z <= ZB + 0.001: zz = z + ins
            xw, yw, zw = warp(x, yy, zz)
            row.append(bm.verts.new((xw, yw, zw)))
        V.append(row)
    n = len(ring)
    def in_win(x0_, x1_):
        xm = (x0_ + x1_) / 2
        return any(a < xm < b for a, b in WINDOWS)
    def mat_idx(xc, yc, zc):
        if yc > 0 and WZ0 < zc < WZ1 and in_win(xc, xc): return 5      # far glass
        if zc < 0.5: return 4
        if zc < 1.0: return 1
        if zc < 1.06: return 2
        if zc < ZS: return 0
        return 3
    for a in range(len(xx) - 1):
        for j in range(n):
            j2 = (j + 1) % n
            f = bm.faces.new([V[a][j], V[a + 1][j], V[a + 1][j2], V[a][j2]])
            xc = (xx[a] + xx[a + 1]) / 2; yc = (ring[j][0] + ring[j2][0]) / 2; zc = (ring[j][1] + ring[j2][1]) / 2
            f.material_index = mat_idx(xc, yc, zc)
            f.smooth = True
            # near-side window hole / wheel arch hole
            if yc < -0.2:
                if WZ0 < zc < WZ1 and in_win(xc, xc): holes.append(f)
                for ax in AXLES:
                    if (xc - ax) ** 2 + (zc - WR) ** 2 < ARCH ** 2: holes.append(f)
    caps = [bm.faces.new(V[0][::-1]), bm.faces.new(V[-1])]
    for cp in caps: cp.material_index = 4 if False else 0
    caps[0].material_index = 4; caps[1].material_index = 3
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    probe = [f for f in bm.faces if f.calc_center_median().y < -1.0 and f.calc_center_median().z > 1.3][0]
    print('NORMAL', probe.normal)
    if probe.normal.y > 0: bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bmesh.ops.delete(bm, geom=holes, context='FACES')
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new('busbody'); bm.to_mesh(me); bm.free()
    body = bpy.data.objects.new('busbody', me); c.objects.link(body)
    for m in (orange, red, white, roofm, skirt, glass_far): me.materials.append(m)
    sol = body.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = 0.07; sol.offset = -1; sol.use_even_offset = False; sol.solidify_mode = 'EXTRUDE'; sol.nonmanifold_thickness_mode = 'FIXED'
    sol.use_rim = True; sol.material_offset = 0; sol.material_offset_rim = 4

    # ---------- window panes
    for (a, b) in WINDOWS:
        bmw = bmesh.new(); nx = max(2, int((b - a) / 0.15)); nz = 6
        g = [[bmw.verts.new(tuple(warp(a + (b - a) * i / nx, -HW + 0.045, WZ0 + (WZ1 - WZ0) * k / nz))) for k in range(nz + 1)] for i in range(nx + 1)]
        for i in range(nx):
            for k in range(nz): bmw.faces.new([g[i][k], g[i + 1][k], g[i + 1][k + 1], g[i][k + 1]])
        bmesh.ops.recalc_face_normals(bmw, faces=list(bmw.faces))
        for f in bmw.faces: f.smooth = True
        o = finish('pane', bmw, glass, coll=c, shade=False)
    # ---------- glare streaks (near windows)
    for (a, b, dx) in [(1.05, 2.40, 0.2), (3.77, 4.84, 0.1), (6.21, 7.28, 0.35)]:
        w1 = 0.20; 
        pts = [warp(a + dx, -HW + 0.02, WZ0 + 0.02), warp(a + dx + w1, -HW + 0.02, WZ0 + 0.02),
               warp(a + dx + w1 + 0.55, -HW + 0.02, WZ1 - 0.02), warp(a + dx + 0.55, -HW + 0.02, WZ1 - 0.02)]
        pts = [(p[0], p[1] - 0.045, p[2]) for p in pts]
        bg = bmesh.new(); vs = [bg.verts.new(p) for p in pts]; bg.faces.new(vs)
        gm = bpy.data.materials.new('glare'); gm.use_nodes = True; nt = gm.node_tree; nt.nodes.clear()
        em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.6
        tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = 0.26
        o_ = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], o_.inputs[0])
        go = finish('glare', bg, gm, coll=c, shade=False); go.visible_shadow = False
    # window rubber frames (thin dark strips around holes)
    for (a, b) in WINDOWS:
        for (xa, xb, za, zb_) in [(a - 0.05, b + 0.05, WZ1, WZ1 + 0.05), (a - 0.05, b + 0.05, WZ0 - 0.05, WZ0),
                                 (a - 0.05, a, WZ0, WZ1), (b, b + 0.05, WZ0, WZ1)]:
            bmf = bmesh.new(); nx = max(1, int((xb - xa) / 0.1)); nz = max(1, int((zb_ - za) / 0.1))
            g = [[bmf.verts.new(tuple(warp(xa + (xb - xa) * i / nx, -HW - 0.004, za + (zb_ - za) * k / nz))) for k in range(nz + 1)] for i in range(nx + 1)]
            for i in range(nx):
                for k in range(nz): bmf.faces.new([g[i][k], g[i + 1][k], g[i + 1][k + 1], g[i][k + 1]])
            bmesh.ops.recalc_face_normals(bmf, faces=list(bmf.faces))
            finish('frame', bmf, rubber, coll=c, shade=False)

    # ---------- chrome belt trim along white stripe base
    ptsL = []
    xk = 1.5
    while xk < L - 0.25:
        if not any(abs(xk - ax) < ARCH + 0.02 for ax in AXLES):
            x, y, z = warp(xk, -HW - 0.0, 1.065); ptsL.append((x, y - 0.012, z))
        else:
            if len(ptsL) > 1: tube('trim', ptsL, 0.014, chrome, c, res=3)
            ptsL = []
        xk += 0.1
    if len(ptsL) > 1: tube('trim', ptsL, 0.014, chrome, c, res=3)
    # ---------- wheels
    for ax in AXLES:
        wy = -HW + 0.24
        tire = cyl('tire', (ax, wy, WR), WR, 0.34, rubber, axis='Y', segs=40, bevel=0.07, coll=c)
        cyl('hubface', (ax, wy - 0.17, WR), 0.31, 0.04, chrome, axis='Y', segs=32, bevel=0.015, coll=c)
        cyl('hubdark', (ax, wy - 0.19, WR), 0.235, 0.03, mat('hubdark', (0.05, 0.05, 0.08), 0.35, metal=0.7), axis='Y', segs=24, coll=c)
        for k in range(6):
            a_ = k * math.pi / 3 + 0.3
            box('spoke', (ax + math.cos(a_) * 0.15, wy - 0.215, WR + math.sin(a_) * 0.15), (0.08, 0.03, 0.2), chrome, bevel=0.01, coll=c, rot=(0, -a_ + math.pi / 2, 0))
        cyl('hubcap', (ax, wy - 0.225, WR), 0.09, 0.04, chrome, axis='Y', segs=20, bevel=0.015, coll=c)
        cyl('wheelhouse', (ax, -HW + 0.62, WR), ARCH + 0.04, 0.1, skirt, axis='Y', segs=40, coll=c)
        cyl('wheelhouse2', (ax, -HW + 0.58, WR + 0.45), ARCH + 0.1, 0.2, skirt, axis='Y', segs=40, coll=c)
    # undercarriage
    box('under', (L / 2, 0, 0.3), (L - 0.6, 1.9, 0.30), skirt, coll=c)
    # ---------- bumpers / lamps / mirror
    box('bumperF', (-0.07, 0, 0.58), (0.20, 2.35, 0.20), chrome, bevel=0.07, coll=c)
    box('bumperR', (L + 0.04, 0, 0.58), (0.16, 2.35, 0.20), chrome, bevel=0.06, coll=c)
    lamp = mat('lamp', (1, 0.95, 0.8), 0.05, emit=(1, 0.9, 0.6), emit_k=6)
    sphere('headl', (0.08, -0.82, 0.92), (0.14, 0.2, 0.14), lamp, coll=c)
    tail = mat('tail', (0.9, 0.02, 0.02), 0.1, emit=(1, 0.1, 0.05), emit_k=1.5)
    box('tail', (L - 0.02, -1.0, 1.0), (0.12, 0.2, 0.34), tail, bevel=0.04, coll=c)
    # side mirror: arm + housing
    tube('mirarm', [(0.75, -HW - 0.02, 1.55), (0.58, -HW - 0.28, 1.72), (0.52, -HW - 0.38, 1.9)], 0.018, chrome, c)
    box('mirror', (0.52, -HW - 0.42, 1.98), (0.09, 0.07, 0.34), mat('mirhouse', (0.85, 0.88, 0.95), 0.18, metal=1.0), bevel=0.025, coll=c)
    # roof AC/vent pods
    box('vent1', (3.6, 0.0, ZT + 0.12), (1.6, 1.3, 0.20), mat('vent', (0.93, 0.93, 0.95), 0.3, coat=0.8), bevel=0.07, coll=c)
    box('vent2', (6.4, 0.0, ZT + 0.07), (0.9, 0.9, 0.12), mat('vent', (0.93, 0.93, 0.95), 0.3, coat=0.8), bevel=0.05, coll=c)
    for k in range(5): box('vlouv', (3.1 + k * 0.28, -0.66, ZT + 0.12), (0.12, 0.02, 0.14), skirt, coll=c)
    # ---------- interior (visible through windows)
    liner = mat('liner', (0.55, 0.52, 0.42), 0.7)
    box('liner_far', (L / 2 + 0.6, HW - 0.14, 1.5), (L - 2.1, 0.04, 1.4), liner, coll=c)
    box('ceiling', (L / 2 + 0.5, 0, 2.24), (L - 1.6, 2.1, 0.06), mat('ceil', (0.95, 0.95, 0.9), 0.6, emit=(1, 1, 0.9), emit_k=0.8), coll=c)
    box('floor', (L / 2, 0, 0.78), (L - 0.6, 2.1, 0.06), mat('floor', (0.18, 0.18, 0.22), 0.7), coll=c)
    fab = [mat('fabA', (0.03, 0.22, 0.75), 0.75, sheen=0.5), mat('fabB', (0.85, 0.35, 0.02), 0.75, sheen=0.5)]
    sp = [2.9, 4.2, 5.5, 6.8, 8.0]
    for k, sx in enumerate(sp):
        box('seatback', (sx, -0.88, 1.3), (0.5, 0.12, 0.62), fab[k % 2], bevel=0.05, coll=c)
        box('seatpan', (sx, -0.7, 1.0), (0.5, 0.45, 0.10), fab[k % 2], bevel=0.04, coll=c)
    # passengers
    skin = mat('skin', (0.78, 0.55, 0.40), 0.5, sss=0.2, spec=0.4)
    hair = mat('hair', (0.02, 0.02, 0.03), 0.45)
    shirts = [(0.9, 0.9, 0.85), (0.15, 0.35, 0.8), (0.85, 0.25, 0.3), (0.3, 0.6, 0.35)]
    for k, sx in enumerate([4.2, 6.8, 8.0]):
        sphere('ph', (sx, -0.88, 1.78), (0.105, 0.105, 0.12), skin, coll=c)
        sphere('phh', (sx, -0.85, 1.83), (0.115, 0.115, 0.11), hair, coll=c)
        sphere('pb', (sx, -0.88, 1.40), (0.20, 0.13, 0.22), mat(f'sh{k}', shirts[k], 0.7), coll=c)
    # driver
    dx_ = 1.85
    box('dseat', (dx_ + 0.28, -0.78, 1.05), (0.1, 0.5, 0.7), mat('dseat', (0.35, 0.12, 0.1), 0.7), bevel=0.03, coll=c)
    sphere('dbody', (dx_ + 0.12, -0.78, 1.30), (0.17, 0.24, 0.27), mat('dshirt', (0.95, 0.97, 1.0), 0.5), coll=c)
    sphere('dhead', (dx_ + 0.06, -0.78, 1.70), (0.115, 0.105, 0.13), skin, coll=c)
    sphere('dhair', (dx_ + 0.10, -0.78, 1.78), (0.12, 0.11, 0.11), hair, coll=c)
    tube('darm', [(dx_ + 0.10, -0.60, 1.44), (dx_ - 0.12, -0.55, 1.30), (dx_ - 0.32, -0.60, 1.30)], 0.045, mat('dsleeve', (0.82, 0.88, 0.92), 0.6), c)
    wheelpts = [(dx_ - 0.42 + 0.0 + math.cos(a) * 0.16 * 0.5, -0.78 + math.cos(a) * 0.16, 1.22 + math.sin(a) * 0.16) for a in [i * math.pi / 8 for i in range(17)]]
    tube('steer', [(dx_ - 0.40 + math.sin(a) * 0.05, -0.78 + math.cos(a) * 0.19, 1.20 + math.sin(a) * 0.15) for a in [i * math.pi / 8 for i in range(17)]], 0.018, rubber, c)
    # handrail / stanchion poles
    for px in (2.45, 3.7, 5.0, 6.3, 7.6):
        tube('pole', [(px, -0.45, 0.8), (px, -0.45, 2.2)], 0.022, mat('pole', (0.95, 0.75, 0.1), 0.3, metal=0.9), c, res=4)
    tube('rail', [(2.5, -0.45, 2.15), (8.8, -0.45, 2.15)], 0.02, chrome, c, res=4)
    # ---------- lettering decals (flat, in front of the body side)
    def decal(col0_m, z_top, wpx, hpx, tex, y=-HW - 0.075, emit=0.0):
        zm = z_top
        w = wpx / PPM; h = hpx / (PPM * CP)
        x0 = col0_m
        bmd = bmesh.new(); bmd.loops.layers.uv.verify()
        vs = [bmd.verts.new((x0, y, zm - h)), bmd.verts.new((x0 + w, y, zm - h)), bmd.verts.new((x0 + w, y, zm)), bmd.verts.new((x0, y, zm))]
        f = bmd.faces.new(vs)
        uv = bmd.loops.layers.uv.active
        for l, (u, v) in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]): l[uv].uv = (u, v)
        m = tex_mat('decal', tex, rough=0.3, spec=0.4, emit_k=emit, coat=0.4, alpha=True)
        o = finish('decal', bmd, m, coll=c, shade=False); o.visible_shadow = False
    # red band: lettering
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGBA', (120, 13), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_B, 9)
    d.text((2, 10), 'BUÝT HÀ NỘI', font=f, fill=(255, 245, 225, 255), anchor='ls')
    im.save(f'{work}/tx_busband.png')
    # snap decals to pixel grid: width/height integer pixels; place so top sits on z=1.0 minus
    decal(3.15, 0.98 + 0.0, 120, 13, f'{work}/tx_busband.png', y=-HW - 0.30)
    # route number plate near front above windows
    t = sign_tex(f'{work}/tx_route.png', '32', 21, 12, (12, 12, 16), (255, 170, 20), size=10, border=(70, 70, 80))
    decal(2.75, 2.30, 21, 12, t, y=-HW - 0.30, emit=0.9)
    # big white route number on the orange rear panel (lower side)
    t2 = sign_tex(f'{work}/tx_route2.png', '32', 22, 14, (250, 235, 215), (200, 20, 25), size=12, border=(200, 20, 25))
    decal(7.95, 0.98, 22, 14, t2, y=-HW - 0.30)
    # parent everything
    for ob in set(bpy.data.objects) - before:
        if ob is not root and ob.parent is None: ob.parent = root
