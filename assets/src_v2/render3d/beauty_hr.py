"""Smooth (anti-aliased) high-res beauty render of the background plate for canny/lineart guidance."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from render import build_all
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = args[0]; SHOW = args[1:] or ['ground', 'facades', 'shelter']
colls = build_all()
sc = bpy.context.scene
sc.render.resolution_percentage = 200
sc.cycles.samples = 48; sc.cycles.filter_width = 1.5; sc.render.film_transparent = False
for n, c in colls.items():
    for ob in c.all_objects: ob.visible_camera = n in SHOW
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print('rendered beauty')
