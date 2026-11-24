"""Shared bpy helpers: pixel<->world mapping, mesh builders, materials, lighting, camera."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

PPM = 24.0                     # pixels per metre
PITCH = math.radians(10)
CP, SP = math.cos(PITCH), math.sin(PITCH)
CANVAS_X0, CANVAS_W, CANVAS_H = -32, 704, 360   # master render covers cols -32..672
ROW_C = 180

def X(col): return col / PPM
def Yrow(row, Z=0.0):
    """world Y (depth) so that a point at height Z lands on pixel row `row`."""
    return ((ROW_C - row) / PPM - Z * CP) / SP
def row_of(Y, Z): return ROW_C - PPM * (Y * SP + Z * CP)

# ------------------------------------------------------------------ scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    return sc

def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

# ------------------------------------------------------------------ mesh
def finish(name, bm, mat=None, smooth_angle=38, coll=None, loc=(0, 0, 0), rot=None, shade=True):
    me = bpy.data.meshes.new(name)
    if shade:
        for f in bm.faces: f.smooth = True
        for e in bm.edges:
            if len(e.link_faces) == 2:
                try: a = e.link_faces[0].normal.angle(e.link_faces[1].normal)
                except ValueError: a = 0.0
                e.smooth = a < math.radians(smooth_angle)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    if rot: ob.rotation_euler = rot
    if mat is not None:
        if isinstance(mat, (list, tuple)):
            for m in mat: ob.data.materials.append(m)
        else: ob.data.materials.append(mat)
    return ob

def _bevel(bm, w, seg):
    if w > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=w, segments=seg, affect='EDGES', profile=0.5, clamp_overlap=True)

def box(name, c, s, mat, bevel=0.0, seg=3, coll=None, rot=None, uv=True):
    """box centred at c with size s (full extents)."""
    bm = bmesh.new()
    bm.loops.layers.uv.verify(); bmesh.ops.create_cube(bm, size=1.0, calc_uvs=uv)
    bmesh.ops.scale(bm, vec=Vector(s), verts=bm.verts)
    _bevel(bm, min(bevel, min(s) * 0.49), seg)
    return finish(name, bm, mat, coll=coll, loc=c, rot=rot)

def cyl(name, c, r, h, mat, axis='Z', segs=32, bevel=0.0, coll=None, r2=None, rot=None):
    bm = bmesh.new()
    bm.loops.layers.uv.verify(); bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=(r if r2 is None else r2), depth=h, calc_uvs=True)
    _bevel(bm, min(bevel, r * .45, h * .45), 2)
    ob = finish(name, bm, mat, coll=coll, loc=c, rot=rot, smooth_angle=50)
    if axis == 'X': ob.rotation_euler = (0, math.pi / 2, 0)
    elif axis == 'Y': ob.rotation_euler = (math.pi / 2, 0, 0)
    return ob

def sphere(name, c, s, mat, segs=24, rings=16, coll=None, rot=None):
    bm = bmesh.new()
    bm.loops.layers.uv.verify(); bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0, calc_uvs=True)
    bmesh.ops.scale(bm, vec=Vector(s), verts=bm.verts)
    return finish(name, bm, mat, coll=coll, loc=c, rot=rot, smooth_angle=89)

def grid_plane(name, c, sx, sy, mat, coll=None, rot=None):
    bm = bmesh.new()
    bm.loops.layers.uv.verify(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5, calc_uvs=True)
    bmesh.ops.scale(bm, vec=Vector((sx, sy, 1)), verts=bm.verts)
    return finish(name, bm, mat, coll=coll, loc=c, rot=rot, shade=False)

def vplane(name, x0, x1, z0, z1, y, mat, coll=None):
    """vertical plane facing the camera (-Y normal) from x0..x1, z0..z1 at depth y (UV 0..1)."""
    w, h = x1 - x0, z1 - z0
    ob = grid_plane(name, ((x0 + x1) / 2, y, (z0 + z1) / 2), w, h, mat, coll=coll, rot=(math.pi / 2, 0, 0))
    return ob

def hplane(name, x0, x1, y0, y1, z, mat, coll=None):
    return grid_plane(name, ((x0 + x1) / 2, (y0 + y1) / 2, z), x1 - x0, y1 - y0, mat, coll=coll)

def tube(name, pts, r, mat, coll=None, res=6):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = r; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts): p.co = (q[0], q[1], q[2], 1)
    ob = bpy.data.objects.new(name, cu); (coll or bpy.context.scene.collection).objects.link(ob)
    ob.data.materials.append(mat); return ob

# ------------------------------------------------------------------ materials
def _bsdf(nt):
    return nt.nodes['Principled BSDF']

def mat(name, base=(0.5, 0.5, 0.5), rough=0.5, metal=0.0, coat=0.0, coat_rough=0.03, spec=0.5,
        sss=0.0, sss_color=None, sheen=0.0, trans=0.0, ior=1.45, emit=None, emit_k=0.0, alpha=1.0, aniso=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = _bsdf(m.node_tree)
    def S(k, v):
        if k in b.inputs: b.inputs[k].default_value = v
    S('Base Color', (*base[:3], 1)); S('Roughness', rough); S('Metallic', metal)
    S('Coat Weight', coat); S('Coat Roughness', coat_rough); S('IOR', ior)
    S('Specular IOR Level', spec); S('Subsurface Weight', sss)
    if sss: S('Subsurface Radius', (0.25, 0.1, 0.05)); S('Subsurface Scale', 0.08)
    S('Sheen Weight', sheen); S('Sheen Roughness', 0.4); S('Transmission Weight', trans)
    if emit: S('Emission Color', (*emit[:3], 1)); S('Emission Strength', emit_k)
    S('Alpha', alpha); S('Anisotropic', aniso)
    return m

def mat_nodes(name, build):
    """build(nt, bsdf) -> may rewire; returns material."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    build(m.node_tree, _bsdf(m.node_tree)); return m

def tex_mat(name, path, rough=0.8, metal=0.0, spec=0.3, emit_k=0.0, coat=0.0, interp='Closest', alpha=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = _bsdf(nt)
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); t.interpolation = interp
    t.image.colorspace_settings.name = 'sRGB'
    t.extension = 'EXTEND'
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    if alpha: nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec
    if coat: b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = 0.05
    if emit_k:
        nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit_k
    return m

def vcol_mat(name, attr='col', rough=0.5, sss=0.0, trans_mix=0.0, spec=0.4, sheen=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = _bsdf(nt)
    a = nt.nodes.new('ShaderNodeVertexColor'); a.layer_name = attr
    nt.links.new(a.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Specular IOR Level'].default_value = spec
    b.inputs['Subsurface Weight'].default_value = sss
    b.inputs['Sheen Weight'].default_value = sheen
    if emit:
        nt.links.new(a.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    if sss:
        b.inputs['Subsurface Radius'].default_value = (0.3, 0.1, 0.1); b.inputs['Subsurface Scale'].default_value = 0.05
    if trans_mix:
        tr = nt.nodes.new('ShaderNodeBsdfTranslucent'); nt.links.new(a.outputs['Color'], tr.inputs['Color'])
        mix = nt.nodes.new('ShaderNodeMixShader'); mix.inputs['Fac'].default_value = trans_mix
        out = nt.nodes['Material Output']
        nt.links.new(b.outputs['BSDF'], mix.inputs[1]); nt.links.new(tr.outputs['BSDF'], mix.inputs[2])
        nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return m

# ------------------------------------------------------------------ world / lights / camera
def make_world():
    w = bpy.data.worlds.new('W'); w.use_nodes = True
    bpy.context.scene.world = w
    nt = w.node_tree; nt.nodes.clear()
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -0.35; mr.inputs['From Max'].default_value = 0.95
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.30, 0.25, 0.20, 1)           # warm grey ground
    el[1].position = 1.0; el[1].color = (0.03, 0.12, 0.55, 1)           # deep blue zenith
    for pos, col in ((0.27, (0.40, 0.34, 0.28, 1)), (0.30, (0.95, 0.97, 1.0, 1)), (0.55, (0.45, 0.68, 1.0, 1))):
        e = el.new(pos); e.color = col
    nt.links.new(mr.outputs['Result'], cr.inputs['Fac'])
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.55
    nt.links.new(cr.outputs['Color'], bg.inputs['Color'])
    out = nt.nodes.new('ShaderNodeOutputWorld'); nt.links.new(bg.outputs[0], out.inputs[0])

def sun(name, direction, strength, color, angle_deg):
    d = bpy.data.lights.new(name, 'SUN'); d.energy = strength; d.color = color; d.angle = math.radians(angle_deg)
    ob = bpy.data.objects.new(name, d); bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = Vector(direction).normalized().to_track_quat('-Z', 'Y').to_euler()
    return ob

def lighting(key=2.7, rim=1.1):
    make_world()
    sun('key', (0.55, 0.50, -0.68), key, (1.0, 0.93, 0.80), 1.8)     # upper-left-front, shines right/back/down
    sun('rim', (-0.60, -0.55, -0.45), rim, (0.45, 0.68, 1.0), 4)      # cool rim from upper-right-back
    b = sun('bounce', (0.15, 0.55, 0.80), 0.9, (1.0, 0.62, 0.32), 20)   # warm ground bounce from below-front (objects only)
    # glossy-only strip softboxes -> 90s horizon streaks on curved paint / chrome / glass
    for name, elev, sx, sy, pw in (('stripA', 9, 160, 6.0, 3.2), ('stripB', 22, 160, 9.0, 2.4)):
        e = math.radians(elev); dirv = Vector((0.12, math.cos(e), -math.sin(e)))
        a = bpy.data.lights.new(name, 'AREA'); a.shape = 'RECTANGLE'; a.size = sx; a.size_y = sy; a.energy = pw * math.pi * sx * sy
        a.color = (1.0, 0.97, 0.9); a.diffuse_factor = 0.0; a.specular_factor = 1.0
        ob = bpy.data.objects.new(name, a); bpy.context.scene.collection.objects.link(ob)
        ob.location = (X(320) , -110 * math.cos(e) - 20, 110 * math.sin(e) )
        ob.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()

def camera():
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'
    cd.ortho_scale = CANVAS_W / PPM; cd.clip_start = 1; cd.clip_end = 400
    ob = bpy.data.objects.new('cam', cd); sc.collection.objects.link(ob); sc.camera = ob
    d = Vector((0, CP, -SP))
    cx = X(CANVAS_X0 + CANVAS_W / 2)
    ob.location = Vector((cx, 0, 0)) - d * 120
    ob.rotation_euler = (math.pi / 2 - PITCH, 0, 0)
    sc.render.resolution_x, sc.render.resolution_y = CANVAS_W, CANVAS_H
    sc.render.resolution_percentage = 100
    return ob

def configure(samples=96):
    sc = bpy.context.scene
    r = sc.render; r.engine = 'CYCLES'; r.film_transparent = True
    r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'; r.image_settings.color_depth = '8'
    c = sc.cycles; c.samples = samples; c.use_denoising = False; c.filter_width = 0.01
    c.max_bounces = 6; c.diffuse_bounces = 3; c.glossy_bounces = 4; c.transmission_bounces = 4
    c.sample_clamp_indirect = 8
    try: c.device = 'CPU'
    except Exception: pass
    c.use_adaptive_sampling = False
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.55
    sc.view_settings.gamma = 1.0
