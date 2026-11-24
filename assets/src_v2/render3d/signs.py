"""Pixel-exact sign textures (Vietnamese text via Arial) and plane helpers."""
from PIL import Image, ImageDraw, ImageFont
from common import *

FONT_B = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT_R = '/System/Library/Fonts/Supplemental/Arial.ttf'

def sign_tex(path, text, w, h, bg, fg, size=10, border=None, font=FONT_B, shadow=None, sub=None, subsize=7):
    im = Image.new('RGB', (w, h), bg); d = ImageDraw.Draw(im)
    if border:
        d.rectangle([0, 0, w - 1, h - 1], outline=border)
        d.rectangle([1, 1, w - 2, h - 2], outline=tuple(int(c * .6 + b * .4) for c, b in zip(border, bg)))
    f = ImageFont.truetype(font, size)
    tb = d.textbbox((0, 0), text, font=f, anchor='ls')
    tw = tb[2] - tb[0]
    # Vietnamese stacked diacritics: baseline slightly lower when `sub` is None
    x = (w - tw) // 2 - tb[0]; y = h - 4 if not sub else h - 9
    if shadow: d.text((x + 1, y + 1), text, font=f, fill=shadow, anchor='ls')
    d.text((x, y), text, font=f, fill=fg, anchor='ls')
    if sub:
        f2 = ImageFont.truetype(FONT_R, subsize)
        tb2 = d.textbbox((0, 0), sub, font=f2, anchor='ls')
        d.text(((w - (tb2[2] - tb2[0])) // 2, h - 3), sub, font=f2, fill=fg, anchor='ls')
    im.save(path); return path

def pix_plane(name, col0, row_top, wpx, hpx, y, m, coll=None, zlift=0.0):
    """Vertical plane at depth y covering exactly wpx x hpx screen pixels with top-left at (col0,row_top)."""
    zt = ((ROW_C - row_top) / PPM - y * SP) / CP
    hm = hpx / (PPM * CP)
    return vplane(name, X(col0), X(col0 + wpx), zt - hm, zt, y, m, coll)

def glare(name, pts_xz, y, coll, k=0.25):
    """semi-transparent white diagonal streak (list of (x,z)) at depth y."""
    bm = bmesh.new(); vs = [bm.verts.new((px, y, pz)) for px, pz in pts_xz]; bm.faces.new(vs)
    m = bpy.data.materials.new('glare'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.6
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = k
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], o.inputs[0])
    ob = finish(name, bm, m, coll=coll, shade=False); ob.visible_shadow = False
    return ob
