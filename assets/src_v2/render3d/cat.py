"""Orange tabby with white chest, sitting. Metaball body, procedural stripe/white-mask fur shader, glossy eyes."""
import math
from common import *
from ground import HS

CAT_X, CAT_BASE_ROW, CAT_SCALE, CAT_YAW = 150, 352, 4.35, math.radians(-14)

def fur_material():
    m = bpy.data.materials.new('fur'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; Lk = nt.links
    b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping')
    Lk.new(tc.outputs['Object'], mp.inputs['Vector'])
    sep = N.new('ShaderNodeSeparateXYZ'); Lk.new(mp.outputs['Vector'], sep.inputs[0])
    noise = N.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 28; noise.inputs['Detail'].default_value = 3
    Lk.new(mp.outputs['Vector'], noise.inputs['Vector'])
    # stripes: wave texture bands around the z axis (body) distorted by noise
    wave = N.new('ShaderNodeTexWave'); wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'; wave.inputs['Scale'].default_value = 26
    wave.inputs['Distortion'].default_value = 4.0; wave.inputs['Detail'].default_value = 1; wave.inputs['Detail Scale'].default_value = 2
    Lk.new(mp.outputs['Vector'], wave.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.52; ramp.color_ramp.elements[1].position = 0.62
    Lk.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    # orange light / dark stripe
    c_or = N.new('ShaderNodeMix'); c_or.data_type = 'RGBA'
    c_or.inputs['A'].default_value = (0.95, 0.42, 0.07, 1); c_or.inputs['B'].default_value = (0.62, 0.17, 0.03, 1)
    Lk.new(ramp.outputs['Color'], c_or.inputs['Factor'])
    # stripes fade on belly/chest
    # white mask: chest, belly, paws, muzzle -> by object coordinates
    # chest sphere
    d1 = N.new('ShaderNodeVectorMath'); d1.operation = 'DISTANCE'; Lk.new(mp.outputs['Vector'], d1.inputs[0]); d1.inputs[1].default_value = (0.0, -0.14, 0.20)
    r1 = N.new('ShaderNodeMapRange'); r1.inputs['From Min'].default_value = 0.075; r1.inputs['From Max'].default_value = 0.12; r1.inputs['To Min'].default_value = 1; r1.inputs['To Max'].default_value = 0
    Lk.new(d1.outputs['Value'], r1.inputs['Value'])
    # paws (low z and in front)
    pz = N.new('ShaderNodeMapRange'); pz.inputs['From Min'].default_value = 0.045; pz.inputs['From Max'].default_value = 0.075; pz.inputs['To Min'].default_value = 1; pz.inputs['To Max'].default_value = 0
    Lk.new(sep.outputs['Z'], pz.inputs['Value'])
    py = N.new('ShaderNodeMapRange'); py.inputs['From Min'].default_value = -0.04; py.inputs['From Max'].default_value = -0.07; py.inputs['To Min'].default_value = 0; py.inputs['To Max'].default_value = 1
    Lk.new(sep.outputs['Y'], py.inputs['Value'])
    ax = N.new('ShaderNodeMath'); ax.operation = 'ABSOLUTE'; Lk.new(sep.outputs['X'], ax.inputs[0])
    axm = N.new('ShaderNodeMapRange'); axm.inputs['From Min'].default_value = 0.075; axm.inputs['From Max'].default_value = 0.1; axm.inputs['To Min'].default_value = 1; axm.inputs['To Max'].default_value = 0
    Lk.new(ax.outputs['Value'], axm.inputs['Value'])
    pm0 = N.new('ShaderNodeMath'); pm0.operation = 'MULTIPLY'; Lk.new(pz.outputs['Result'], pm0.inputs[0]); Lk.new(py.outputs['Result'], pm0.inputs[1])
    pm = N.new('ShaderNodeMath'); pm.operation = 'MULTIPLY'; Lk.new(pm0.outputs['Value'], pm.inputs[0]); Lk.new(axm.outputs['Result'], pm.inputs[1])
    # muzzle / chin
    d2 = N.new('ShaderNodeVectorMath'); d2.operation = 'DISTANCE'; Lk.new(mp.outputs['Vector'], d2.inputs[0]); d2.inputs[1].default_value = (0.0, -0.12, 0.28)
    r2 = N.new('ShaderNodeMapRange'); r2.inputs['From Min'].default_value = 0.028; r2.inputs['From Max'].default_value = 0.05; r2.inputs['To Min'].default_value = 1; r2.inputs['To Max'].default_value = 0
    Lk.new(d2.outputs['Value'], r2.inputs['Value'])
    m1 = N.new('ShaderNodeMath'); m1.operation = 'MAXIMUM'; Lk.new(r1.outputs['Result'], m1.inputs[0]); Lk.new(pm.outputs['Value'], m1.inputs[1])
    m2 = N.new('ShaderNodeMath'); m2.operation = 'MAXIMUM'; Lk.new(m1.outputs['Value'], m2.inputs[0]); Lk.new(r2.outputs['Result'], m2.inputs[1])
    mw = N.new('ShaderNodeMix'); mw.data_type = 'RGBA'; mw.inputs['B'].default_value = (1.0, 0.97, 0.92, 1)
    Lk.new(c_or.outputs['Result'], mw.inputs['A']); Lk.new(m2.outputs['Value'], mw.inputs['Factor'])
    Lk.new(mw.outputs['Result'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.55; b.inputs['Sheen Weight'].default_value = 1.0; b.inputs['Sheen Roughness'].default_value = 0.35
    b.inputs['Specular IOR Level'].default_value = 0.35
    b.inputs['Subsurface Weight'].default_value = 0.25; b.inputs['Subsurface Radius'].default_value = (0.5, 0.2, 0.1); b.inputs['Subsurface Scale'].default_value = 0.01
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35; bump.inputs['Distance'].default_value = 0.004
    n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 220; n2.inputs['Detail'].default_value = 1
    Lk.new(mp.outputs['Vector'], n2.inputs['Vector']); Lk.new(n2.outputs['Fac'], bump.inputs['Height']); Lk.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

def build(colls, work):
    c = colls['cat']
    root = bpy.data.objects.new('catroot', None); c.objects.link(root)
    root.location = (X(CAT_X), Yrow(CAT_BASE_ROW, HS), HS)
    root.scale = (CAT_SCALE,) * 3; root.rotation_euler = (0, 0, CAT_YAW)
    before = set(bpy.data.objects)
    fur = fur_material()
    mb = bpy.data.metaballs.new('catmb'); mb.resolution = 0.006; mb.render_resolution = 0.006; mb.threshold = 0.35
    ob = bpy.data.objects.new('catbody', mb); c.objects.link(ob); ob.data.materials.append(fur)
    def el(x, y, z, sx, sy, sz, rot=(0, 0, 0), st=2.0):
        e = mb.elements.new(type='ELLIPSOID'); e.co = (x, y, z); e.radius = 1.0
        k = 1.45; e.size_x, e.size_y, e.size_z = sx * k, sy * k, sz * k; e.stiffness = st
        e.rotation = Euler(rot).to_quaternion()
    # haunches (sitting hips), belly, chest, shoulders
    for s in (-1, 1):
        el(s * 0.085, 0.03, 0.085, 0.085, 0.13, 0.09, st=2)
    el(0, 0.03, 0.115, 0.11, 0.13, 0.11)
    el(0, -0.02, 0.17, 0.085, 0.09, 0.13, rot=(math.radians(-12), 0, 0))
    el(0, -0.05, 0.215, 0.085, 0.08, 0.11)
    # front legs + paws
    for s in (-1, 1):
        el(s * 0.05, -0.09, 0.115, 0.03, 0.034, 0.105)
        el(s * 0.045, -0.105, 0.03, 0.036, 0.05, 0.026)
    # neck + head
    el(0, -0.05, 0.25, 0.07, 0.07, 0.06)
    el(0, -0.075, 0.315, 0.108, 0.088, 0.085, st=2.2)
    for s in (-1, 1):
        el(s * 0.066, -0.105, 0.30, 0.055, 0.048, 0.048)   # cheeks
    el(0, -0.14, 0.295, 0.044, 0.036, 0.034)              # muzzle
    # tail: curls round the right side to the front
    path = [(0.12, 0.11, 0.05), (0.19, 0.13, 0.04), (0.25, 0.09, 0.035), (0.28, 0.01, 0.03), (0.27, -0.07, 0.03), (0.23, -0.14, 0.03), (0.17, -0.19, 0.032), (0.11, -0.2, 0.034)]
    for i, (x, y, z) in enumerate(path):
        t = i / (len(path) - 1)
        for j in range(3):
            tt = (i + j / 3) / len(path)
            el(x, y, z, 0.034 - 0.006 * t, 0.034 - 0.006 * t, 0.03 - 0.004 * t, st=2.5)
    # ---- ears (cones), eyes, nose
    ear_o = mat('ear_out', (0.85, 0.35, 0.06), 0.6, sheen=0.5)
    ear_i = mat('ear_in', (0.95, 0.5, 0.5), 0.5, sss=0.3)
    for s in (-1, 1):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.045, radius2=0.005, depth=0.075)
        bmesh.ops.scale(bm, vec=Vector((1, 0.45, 1)), verts=bm.verts)
        e = finish('ear', bm, ear_o, coll=c, loc=(s * 0.078, -0.07, 0.395), rot=(math.radians(-8), math.radians(s * 20), math.radians(s * 18)), smooth_angle=89)
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.03, radius2=0.002, depth=0.06)
        bmesh.ops.scale(bm, vec=Vector((1, 0.3, 1)), verts=bm.verts)
        finish('earin', bm, ear_i, coll=c, loc=(s * 0.076, -0.097, 0.388), rot=(math.radians(-8), math.radians(s * 20), math.radians(s * 18)), smooth_angle=89)
        # eyes
        eye = mat('eye', (0.75, 0.85, 0.12), 0.04, coat=1.0, coat_rough=0.0, spec=1.0, emit=(0.5, 0.7, 0.05), emit_k=0.3)
        pup = mat('pupil', (0.01, 0.01, 0.01), 0.05, coat=1.0, coat_rough=0.0)
        sphere('eye', (s * 0.043, -0.152, 0.325), (0.022, 0.014, 0.024), eye, coll=c)
        sphere('pupil', (s * 0.043, -0.1655, 0.325), (0.007, 0.005, 0.02), pup, coll=c)
    nose = mat('nose', (0.95, 0.4, 0.45), 0.12, coat=1.0, coat_rough=0.03, spec=1.0)
    sphere('nose', (0, -0.18, 0.298), (0.014, 0.01, 0.009), nose, coll=c)
    # whisker hint: 3 thin white tubes each side
    wh = mat('whisk', (1, 1, 1), 0.4)
    for s in (-1, 1):
        for k in range(3):
            tube('wh', [(s * 0.03, -0.176, 0.283 + k * 0.007), (s * 0.10, -0.178, 0.275 + k * 0.02)], 0.0012, wh, c, res=2)
    for o in set(bpy.data.objects) - before:
        if o.parent is None: o.parent = root
