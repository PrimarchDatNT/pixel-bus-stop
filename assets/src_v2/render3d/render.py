import sys, os, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.append(os.path.abspath(HERE+'/../../../.venv/lib/python3.13/site-packages'))
import bpy
from common import *
import ground
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
WORK = f'{HERE}/work'

def build_all(only=None):
    reset(); camera(); lighting(); configure(int(os.environ.get('SPP', 96)))
    names = ['ground', 'facades', 'shelter', 'bus', 'cat']
    colls = {n: collection(n) for n in names}
    ground.build(colls, WORK)
    for ob in colls['ground'].all_objects: ob.visible_shadow = False if ob.name.startswith(('under','nearbody')) else True
    for n in ('facades', 'shelter', 'bus', 'cat'):
        try:
            mod = importlib.import_module(n)
        except ModuleNotFoundError as e:
            if e.name == n: continue
            raise
        mod.build(colls, WORK)
    return colls

def render(colls, show, out):
    sc = bpy.context.scene
    for n, c in colls.items():
        for ob in c.all_objects:
            ob.visible_camera = n in show
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)

if __name__ == '__main__':
    passes = args or ['ground']
    colls = build_all()
    for p in passes:
        if p == 'ground': show = ['ground']
        elif p == 'full': show = list(colls)
        else: show = [p]
        render(colls, show, f'{WORK}/{p}.png')
        print('rendered', p)
