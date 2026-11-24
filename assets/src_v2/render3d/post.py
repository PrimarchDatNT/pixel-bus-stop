"""Post-process Blender renders into clean pixel art.
alpha threshold -> hue-shift grade -> k-means quantise (OKLab, <=32 colours incl. outline tones)
-> coloured selective outline (lit side lightened) -> orphan / speckle clean-up.
Usage: python post.py [sprite ...]
"""
import sys, os, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = f'{HERE}/work'
OUT = os.path.abspath(f'{HERE}/../../out_v2/render3d')
CX0 = 32          # master canvas col offset (image x = canvas x + 32)

# ---------------------------------------------------------------- colour maths
def srgb2lin(c): c = c / 255.0; return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin2srgb(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255.0
M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
def to_lab(rgb):
    l = srgb2lin(rgb.astype(float)) @ M1.T
    return np.cbrt(l) @ M2.T
def from_lab(lab):
    l = (lab @ np.linalg.inv(M2).T) ** 3
    return lin2srgb(l @ np.linalg.inv(M1).T)

def grade(rgb, shadow=(-0.020, -0.012, 0.050), warm=(0.040, 0.022, -0.030), sat=1.18, contrast=1.08, gamma=0.95):
    """hue-shift: shadows toward blue/purple, highlights toward warm yellow-white; saturation peak in mid-tones."""
    x = rgb.astype(float) / 255.0
    L = (x * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
    x = np.clip((x - 0.5) * contrast + 0.5, 0, 1) ** gamma
    g = (x * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
    mid = 4 * g * (1 - g)
    x = g + (x - g) * (1 + (sat - 1) * (0.4 + 0.6 * mid))
    x = x + np.array(shadow) * (1 - g) ** 2 + np.array(warm) * g ** 3
    return np.clip(x * 255, 0, 255)

# ---------------------------------------------------------------- k-means
def kmeans_palette(rgb_pixels, k, iters=14, seed=1, lw=1.0):
    if len(rgb_pixels) == 0: return np.zeros((0, 3))
    q = (rgb_pixels // 4).astype(np.int32)
    key = q[:, 0] * 4096 + q[:, 1] * 64 + q[:, 2]
    uk, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    rep = np.zeros((len(uk), 3)); np.add.at(rep, inv, rgb_pixels.astype(float)); rep /= cnt[:, None]
    lab = to_lab(rep); w = cnt.astype(float)
    sc = np.array([lw, 1, 1])
    labw = lab * sc
    k = min(k, len(uk)); rng = np.random.RandomState(seed)
    C = [labw[rng.choice(len(uk), p=w / w.sum())]]
    for _ in range(1, k):
        d = np.min(((labw[:, None] - np.array(C)[None]) ** 2).sum(-1), axis=1) * w
        C.append(labw[rng.choice(len(uk), p=d / d.sum())] if d.sum() > 0 else labw[0])
    C = np.array(C)
    for _ in range(iters):
        a = np.argmin(((labw[:, None] - C[None]) ** 2).sum(-1), axis=1)
        for j in range(k):
            m = a == j
            if m.any(): C[j] = (labw[m] * w[m, None]).sum(0) / w[m].sum()
    pal = from_lab(C / sc)
    return np.clip(np.round(pal), 0, 255)

def map_to_palette(rgb, pal):
    lab = to_lab(rgb.reshape(-1, 3)); pl = to_lab(pal)
    d = ((lab[:, None] - pl[None]) ** 2).sum(-1)
    return np.argmin(d, axis=1).reshape(rgb.shape[:-1])

# ---------------------------------------------------------------- sprite ops
def nb4(a):
    p = np.pad(a, 1, mode='constant')
    return p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]     # up, down, left, right

def clean_alpha(alpha, fill_holes=True):
    a = alpha.copy()
    for _ in range(2):
        u, d, l, r = nb4(a)
        n = u.astype(int) + d + l + r
        a = a & (n >= 1)                          # orphans
        if fill_holes: a = a | (~a & (n >= 4))
    # also drop pixels with only a single diagonal-ish link
    u, d, l, r = nb4(a); n = u.astype(int) + d + l + r
    a = a & ~((n == 1) & False)
    return a

def despeckle(idx, alpha, pal, thr=0.07, passes=1):
    lab = to_lab(pal)
    idx = idx.copy()
    for _ in range(passes):
        P = np.pad(idx, 1, mode='edge'); PA = np.pad(alpha, 1, mode='constant')
        nbs = [P[:-2, 1:-1], P[2:, 1:-1], P[1:-1, :-2], P[1:-1, 2:]]
        nas = [PA[:-2, 1:-1], PA[2:, 1:-1], PA[1:-1, :-2], PA[1:-1, 2:]]
        new = idx.copy()
        for y in range(idx.shape[0]):
            for x in range(idx.shape[1]):
                if not alpha[y, x]: continue
                v = [nbs[i][y, x] for i in range(4) if nas[i][y, x]]
                if len(v) < 3: continue
                vals, cnt = np.unique(v, return_counts=True)
                m = vals[np.argmax(cnt)]
                if cnt.max() >= 3 and m != idx[y, x] and np.sqrt(((lab[m] - lab[idx[y, x]]) ** 2).sum()) < thr and idx[y, x] not in v:
                    new[y, x] = m
        idx = new
    return idx

def dark_of(c, k=0.50):
    lab = to_lab(c.reshape(1, 3))[0]
    lab = lab * np.array([k, 0.95, 0.95]) + np.array([0.0, -0.012, -0.03])   # darker, toward blue-purple
    return np.clip(np.round(from_lab(lab)), 0, 255)

def process(img, k=32, out_colors=6, outline=True, do_grade=True, haze=None, despeckle_thr=0.07, lit_edges=True, ban_outline=None):
    """img: RGBA uint8 (H,W,4) -> RGBA uint8 pixel art."""
    h, w = img.shape[:2]
    alpha = clean_alpha(img[..., 3] >= 128)
    rgb = img[..., :3].astype(float)
    if haze is not None:
        col, amt = haze; rgb = rgb * (1 - amt) + np.array(col) * amt
    if do_grade: rgb = grade(rgb)
    kbody = k - (out_colors if outline else 0)
    pal = kmeans_palette(np.clip(rgb[alpha], 0, 255).astype(np.uint8), kbody)
    idx = map_to_palette(np.clip(rgb, 0, 255), pal)
    idx = despeckle(idx, alpha, pal, thr=despeckle_thr)
    out = np.zeros((h + 2, w + 2, 4), np.uint8)
    # pad by 1 so outside outline fits
    PA = np.pad(alpha, 1); PI = np.pad(idx, 1)
    body = pal[PI].astype(np.uint8)
    out[..., :3] = body; out[..., 3] = np.where(PA, 255, 0)
    if outline:
        u, d, l, r = nb4(PA)
        edge = ~PA & (u | d | l | r)
        # neighbour colour (prefer darker one) and lit-side flag
        cols = np.zeros((h + 2, w + 2, 3)); best = np.full((h + 2, w + 2), 1e9); lit = np.zeros((h + 2, w + 2), bool)
        Pp = np.pad(PI, 1, mode='edge'); PAp = np.pad(PA, 1)
        for (dy, dx, litflag) in ((-1, 0, False), (1, 0, True), (0, -1, False), (0, 1, True)):
            # neighbour at (y+dy, x+dx); if neighbour opaque, outline pixel sits on its (−dy,−dx) side
            nidx = Pp[1 + dy:1 + dy + h + 2, 1 + dx:1 + dx + w + 2]; na = PAp[1 + dy:1 + dy + h + 2, 1 + dx:1 + dx + w + 2]
            c = pal[nidx]; Lm = c.sum(-1)
            m = edge & na & (Lm < best)
            cols[m] = c[m]; best[m] = Lm[m]; lit[m] = litflag
        # litflag semantics: neighbour is below/right of the outline pixel => outline on top/left = lit side
        oc = np.zeros_like(cols)
        flat = cols[edge]
        dk = np.array([dark_of(c) for c in flat]) if len(flat) else np.zeros((0, 3))
        # lit side: broken / lightened outline
        lf = lit[edge] & lit_edges
        mix = dk.copy()
        if len(flat): mix[lf] = np.clip(0.45 * dk[lf] + 0.55 * flat[lf], 0, 255)
        if len(mix):
            opal = kmeans_palette(mix.astype(np.uint8), out_colors, seed=3, lw=1.0)
            oi = map_to_palette(mix, opal)
            oc[edge] = opal[oi]
            # break outline on the lit side every 4th pixel for a hand-inked feel
            ys, xs = np.nonzero(edge)
            for n, (yy, xx) in enumerate(zip(ys, xs)):
                if lf[n] and ((yy * 7 + xx * 3) % 5 == 0):
                    edge[yy, xx] = False
            out[..., :3][edge] = oc[edge].astype(np.uint8); out[..., 3][edge] = 255
    return out, (-1, -1)   # offset of padding

def load_master(name):
    return np.array(Image.open(f'{WORK}/{name}.png').convert('RGBA'))

def bbox(alpha, thr=128):
    ys, xs = np.nonzero(alpha >= thr)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1

def save(arr, name):
    Image.fromarray(arr).save(f'{OUT}/{name}.png')

def ncolors(arr): 
    m = arr[..., 3] > 0; return len(np.unique(arr[m][:, :3], axis=0))

def run(names):
    os.makedirs(OUT, exist_ok=True)
    pl_path = f'{OUT}/placements.json'
    pl = json.load(open(pl_path)) if os.path.exists(pl_path) else {}
    for n in names:
        m = load_master(n)
        if n in ('shelter', 'bus', 'cat'):
            x0, y0, x1, y1 = bbox(m[..., 3])
            sub = m[y0:y1, x0:x1]
            nm = {'shelter': 'shelter_ha', 'bus': 'bus_L', 'cat': 'cat_sit'}[n]
            kk = {'shelter': 32, 'bus': 32, 'cat': 32}[n]
            res, off = process(sub, k=kk, out_colors=6, despeckle_thr=0.06 if n != 'shelter' else 0.05)
            save(res, nm); pl[nm] = [int(x0 - CX0 + off[0]), int(y0 + off[1])]
            print(nm, res.shape, 'colors', ncolors(res), 'at', pl[nm])
        elif n == 'facades':
            sub = m[40:216, CX0:CX0 + 640].copy()
            res = np.zeros_like(sub)
            for (a, b) in ((0, 150), (150, 300), (300, 470), (470, 640)):
                part = sub[:, a:b].copy()
                r, _ = process(part[:, :, :], k=32, outline=False, haze=((196, 214, 238), 0.10), despeckle_thr=0.05)
                res[:, a:b] = r[1:-1, 1:-1]
            save(res, 'facades'); pl['facades'] = [0, 40]
            print('facades', res.shape, 'colors/house', [ncolors(res[:, a:b]) for a, b in ((0, 150), (150, 300), (300, 470), (470, 640))])
        elif n == 'ground':
            sub = m[:, CX0:CX0 + 640].copy()
            r, _ = process(sub, k=32, outline=False, despeckle_thr=0.03)
            res = r[1:-1, 1:-1]
            save(res, 'ground'); pl['ground'] = [0, 0]
            print('ground', res.shape, 'colors', ncolors(res))
    json.dump(pl, open(pl_path, 'w'), indent=1)

if __name__ == '__main__':
    run(sys.argv[1:] or ['ground', 'facades', 'shelter', 'bus', 'cat'])
