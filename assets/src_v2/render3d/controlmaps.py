"""Render ControlNet guide maps (depth, normal, id) of the background plate from the render3d master scene.

    Blender -b -P controlmaps.py -- <outdir> [collections...]
Writes depth.png (near=white), normal.png (camera-space), id.png (flat colour per collection), 1280x720.
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
from render import build_all

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUTDIR = args[0] if args else f'{HERE}/work/control'
SHOW = args[1:] or ['ground', 'facades', 'shelter']
os.makedirs(OUTDIR, exist_ok=True)

colls = build_all()
sc = bpy.context.scene
sc.render.resolution_percentage = 200          # 704x360 -> 1408x720, cropped to 1280x720 below
sc.render.film_transparent = False
sc.cycles.samples = 4
sc.cycles.filter_width = 1.0
sc.view_settings.view_transform = 'Standard'
sc.view_settings.exposure = 0.0
sc.world.use_nodes = True
bg = sc.world.node_tree.nodes.get('Background')
for n in list(sc.world.node_tree.nodes):
    if n.type == 'BACKGROUND':
        n.inputs[0].default_value = (0, 0, 0, 1)
        n.inputs[1].default_value = 0.0
for ob in sc.objects:
    if ob.type == 'LIGHT':
        ob.hide_render = True

shown = set()
for n, c in colls.items():
    for ob in c.all_objects:
        ob.visible_camera = n in SHOW
        if n in SHOW:
            shown.add(ob)

# depth range from bounding boxes of what is shown
bpy.context.view_layer.update()
cam = sc.camera
inv = cam.matrix_world.inverted()
zs = []
for ob in shown:
    if ob.type != 'MESH':
        continue
    for v in ob.bound_box:
        zs.append(-(inv @ (ob.matrix_world @ Vector(v))).z)
near, far = min(zs), max(zs)
print('depth range', near, far)


def emission_mat(name, build):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(em.outputs[0], out.inputs[0])
    build(nt, em)
    return m


def depth_build(nt, em):
    cd = nt.nodes.new('ShaderNodeCameraData')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = near
    mr.inputs['From Max'].default_value = far
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.08
    nt.links.new(cd.outputs['View Z Depth'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], em.inputs['Color'])


def normal_build(nt, em):
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    vt = nt.nodes.new('ShaderNodeVectorTransform')
    vt.vector_type = 'NORMAL'; vt.convert_from = 'WORLD'; vt.convert_to = 'CAMERA'
    mul = nt.nodes.new('ShaderNodeVectorMath'); mul.operation = 'MULTIPLY_ADD'
    mul.inputs[1].default_value = (0.5, 0.5, -0.5)
    mul.inputs[2].default_value = (0.5, 0.5, 0.5)
    nt.links.new(geo.outputs['Normal'], vt.inputs[0])
    nt.links.new(vt.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], em.inputs['Color'])


vl = sc.view_layers[0]
mesh_obs = [ob for ob in shown if ob.type == 'MESH']
orig = {ob.name: list(ob.data.materials) for ob in mesh_obs}
for tag, build in (('depth', depth_build), ('normal', normal_build)):
    m = emission_mat(tag, build)
    for ob in mesh_obs:
        ob.data.materials.clear(); ob.data.materials.append(m)
    sc.render.filepath = f'{OUTDIR}/{tag}_full.png'
    bpy.ops.render.render(write_still=True)
    print('rendered', tag)

# id: flat colour per collection (and per top-level object name prefix inside shelter)
palette = {'ground': (0.5, 0.5, 0.5), 'facades': (0.2, 0.4, 1.0), 'shelter': (1.0, 0.6, 0.0),
           'bus': (1.0, 1.0, 0.0), 'cat': (1.0, 0.3, 0.0)}
for n, c in colls.items():
    col = palette.get(n, (1, 1, 1))
    mat = emission_mat(f'id_{n}', lambda nt, em, col=col: em.inputs['Color'].__setattr__('default_value', (*col, 1)))
    for ob in c.all_objects:
        if ob.type == 'MESH':
            if 'bloom' in ob.name.lower() or 'bract' in ob.name.lower() or 'leaf' in ob.name.lower() or 'vine' in ob.name.lower():
                m2 = emission_mat(f'id_bloom_{ob.name}', lambda nt, em: em.inputs['Color'].__setattr__('default_value', (1.0, 0.0, 0.6, 1)))
                ob.data.materials.clear(); ob.data.materials.append(m2)
            else:
                ob.data.materials.clear(); ob.data.materials.append(mat)
sc.render.filepath = f'{OUTDIR}/id_full.png'
bpy.ops.render.render(write_still=True)
print('rendered id')
