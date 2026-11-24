import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from tools.px_gif import *
from tools.layout_gif import *
import tools.px as _px
from PIL import Image

# one-char legend
L = {
 'k':'ink','h':'hair','l':'hair_l','s':'sk','S':'sk_l','d':'sk_d',
 'w':'white','g':'grey_hl','G':'grey_l','m':'grey','M':'grey_m','D':'grey_d','K':'grey_k',
 'y':'yl','Y':'yl_l','z':'yl_d','r':'red','R':'red_l','q':'red_d',
 'o':'or','O':'or_l','p':'or_d','c':'cat_hl',
 'b':'pb','B':'pb_l','n':'pb_d','N':'navy',
 'a':'wc','A':'wc_l','e':'wc_d','t':'tc','T':'tc_l','u':'tc_d',
 'f':'wood','F':'wood_l','j':'wood_d','J':'wood_k','x':'wood_hl',
 'v':'leaf','V':'leaf_l','W':'leaf_hl','X':'leaf_d',
 'i':'glass','I':'glass_l','1':'bl','2':'bl_l','3':'bl_d','4':'bl_hl',
 '5':'sh','6':'sh_l','7':'sh_d','8':'sk_d','9':'paper','0':'sb', 'P':'pave_l','Q':'pave',
 'E':'haze','C':'cloud_d','Z':'teal','H':'teal_d','U':'sb_d',
}
def G(rows, extra=None):
    lg = dict(L); lg.update(extra or {})
    w = max(len(r) for r in rows); im = new(w, len(rows))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch not in '. ': put(im, x, y, lg[ch])
    return im

_DARK = {}
def _mk():
    ramps = [('sk_l','sk','sk_d'),('yl_l','yl','yl_d'),('red_l','red','red_d'),('or_l','or','or_d'),('cat_hl','or','or_d'),
             ('pb_l','pb','pb_d'),('wc_l','wc','wc_d'),('wood_hl','wood_l','wood','wood_d'),('leaf_hl','leaf_l','leaf','leaf_d'),
             ('grey_hl','grey_l','grey','grey_m','grey_d'),('white','paper'),('sh_l','sh','sh_d'),('sb_l','sb','sb_d'),
             ('tc_l','tc','tc_d'),('glass_l','glass','glass_d'),('teal','teal_d'),('wb_l','wb','wb_d'),('bl_hl','bl_l','bl','bl_d'),('pave_l','pave','pave_d')]
    for rp in ramps:
        for n in rp: _DARK[RGB[n]] = RGB[rp[-1]]
    for n in ('hair','hair_l','ink','grey_k','wood_k','navy','red_d','or_d','yl_d','pb_d','sk_d','wc_d','leaf_d','sh_d','sb_d','tc_d','bl_d','grey_d','pave_d','teal_d','glass_d'):
        _DARK[RGB[n]] = RGB['ink'] if n in ('hair','hair_l','ink','grey_k','wood_k','navy') else RGB[n]
    # darker-of-dark
    for n,t in (('sk_d','wood_d'),('or_d','wood_d'),('yl_d','wood_d'),('red_d','wood_k'),('pb_d','navy'),('wc_d','wood_d'),('tc_d','wood_k'),('leaf_d','leaf_k'),('grey_d','ink'),('wood_d','ink'),('wood','wood_k')):
        _DARK[RGB[n]] = RGB[t]
    _DARK[RGB['hair']] = RGB['ink']
_mk()
def sout(img, diag=False, fixed=None):
    """selective outline: 1px outside, colour = dark tone of the neighbouring fill. Canvas grows 1px each side."""
    w,h = img.size; src = new(w+2,h+2); src.paste(img,(1,1)); out = new(w+2,h+2)
    sp,op = src.load(), out.load()
    nb=[(-1,0),(1,0),(0,-1),(0,1)]
    for y in range(h+2):
        for x in range(w+2):
            if sp[x,y][3]: continue
            for dx,dy in nb:
                xx,yy=x+dx,y+dy
                if 0<=xx<w+2 and 0<=yy<h+2 and sp[xx,yy][3]:
                    col = RGB[fixed] if fixed else _DARK.get(sp[xx,yy][:3], RGB['ink'])
                    op[x,y]=(*col,255); break
    out.alpha_composite(src); return out

def over(base, spr, x, y):
    b = base.copy(); b.alpha_composite(spr,(x,y)); return b
def stamp(img, rows, x, y, extra=None):
    img.alpha_composite(G(rows, extra), (x,y)); return img
def px_(img, pts, col):
    for x,y in pts: put(img,x,y,col)
    return img

MOCK = Image.open(_px.ROOT/'assets/out_gif/_mock/mock.png').convert('RGBA')
def sheet(items, scale=6, pad=4, bg='grey_l', cols=None):
    """items: list of (label-less) images -> contact sheet"""
    cols = cols or len(items)
    rows = [items[i:i+cols] for i in range(0,len(items),cols)]
    W = max(sum(i.width+pad for i in r) for r in rows)+pad
    H = sum(max(i.height for i in r)+pad for r in rows)+pad
    s = Image.new('RGBA',(W,H),(*RGB[bg],255)); y=pad
    for r in rows:
        x=pad
        for i in r: s.alpha_composite(i,(x,y+max(j.height for j in r)-i.height)); x+=i.width+pad
        y+=max(i.height for i in r)+pad
    return s.resize((W*scale,H*scale),Image.NEAREST)
def strip_frames(path_name, group='actors'):
    import json
    d=_px.OUT/group; m=json.loads((d/f'{path_name}.json').read_text()); st=Image.open(d/f'{path_name}.png')
    return [st.crop((i*m['frameW'],0,(i+1)*m['frameW'],m['frameH'])) for i in range(m['frames'])], m

def crop_union(frames):
    """crop all frames to the union bbox; returns (frames, (left, top))"""
    bb = None
    for f in frames:
        b = f.getbbox()
        if b: bb = b if bb is None else (min(bb[0],b[0]),min(bb[1],b[1]),max(bb[2],b[2]),max(bb[3],b[3]))
    return [f.crop(bb) for f in frames], (bb[0], bb[1])
def save_c(name, frames, ax, ay, **kw):
    """ax, ay given in uncropped frame coords; they are translated after crop. anchor y = row of lowest contact pixel"""
    fr,(l,t) = crop_union(frames)
    return save_asset('actors', name, fr, anchor=(ax-l, ay-t), **kw)
