import sys,os
sys.argv=['x','--']
exec(open('render.py').read().split("if __name__")[0])
colls=build_all()
dg=bpy.context.evaluated_depsgraph_get()
for o in colls['bus'].all_objects:
    if o.type=='MESH':
        e=o.evaluated_get(dg); vs=[v.co for v in e.data.vertices]
        if not vs: continue
        mx=[max(v[i] for v in vs) for i in range(3)]; mn=[min(v[i] for v in vs) for i in range(3)]
        if mx[0]>9.6 or mx[2]>3.5 or mn[2]<-0.1 or mx[1]>1.5 or mn[1]<-1.8: print('BIG',o.name,[round(a,2) for a in mn],[round(a,2) for a in mx])
    elif o.type=='CURVE':
        print('CURVE', o.name, o.data.bevel_depth)
