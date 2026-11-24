"""shade25d -- hand-pixel art with computed 3D lighting (STYLE v2, "32-bit glossy").

Pipeline
  1. Build a Buf (per-pixel mask / normal / depth / material / part-id) from 2.5D primitives:
     box (bevelled, bulged), cylinders, ellipsoid, capsule, cone, inflate (distance-transform
     blob for any mask), scatter_bumps (clumps of bracts/leaves/fur tufts).
  2. render(): Lambert key (upper-left-front) + Blinn-Phong + cool rim (upper-right-back)
     + warm bounce (below) + environment reflection (sky/horizon/ground) + screen-space AO
     and shadows -> a scalar tone per pixel -> quantised to the material's hue-shifted ramp.
  3. Coloured selective outline (outer silhouette + inner part/depth lines), pixel-perfect
     corner cleanup, orphan-pixel removal, hot spots and glass glare helpers.
Output: RGBA uint8, alpha 0/255 only.
"""
import colorsys
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw

# ----------------------------------------------------------------------------- colour maths
_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])
_M1i = np.linalg.inv(_M1)
_M2i = np.linalg.inv(_M2)


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def srgb2lin(c):
    c = np.asarray(c, float) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin2srgb(l):
    l = np.clip(l, 0, 1)
    return np.where(l <= 0.0031308, l * 12.92, 1.055 * l ** (1 / 2.4) - 0.055) * 255.0


def rgb2lch(rgb):
    lab = _M2 @ np.cbrt(_M1 @ srgb2lin(rgb))
    return lab[0], float(np.hypot(lab[1], lab[2])), float(np.degrees(np.arctan2(lab[2], lab[1])) % 360)


def lch2rgb(L, C, h, clip=True):
    """OKLCH -> sRGB 0..255, reducing chroma until in gamut."""
    for _ in range(40):
        a, b = C * np.cos(np.radians(h)), C * np.sin(np.radians(h))
        lms = (_M2i @ np.array([L, a, b])) ** 3
        lin = _M1i @ lms
        if lin.min() >= -0.002 and lin.max() <= 1.002:
            break
        C *= 0.93
    return np.clip(lin2srgb(lin), 0, 255)


def _hue_toward(h, target, k):
    d = ((target - h + 180) % 360) - 180
    return (h + d * k) % 360


def make_ramp(base, n=8, l0=0.27, l1=0.97, dark_h=292., light_h=98., dk=0.42, lk=0.34,
              cmul=1.0, cdark=0.70, clight=0.45, mid_t=0.58, cfloor_d=0.0, cfloor_l=0.0):
    """Hue-shifted n-tone ramp (dark->light) whose mid tone is `base` (hex or rgb).
    Shadows rotate toward blue/violet, highlights toward warm yellow, chroma peaks at mid."""
    base = hexrgb(base) if isinstance(base, str) else np.asarray(base, float)
    L0, C0, h0 = rgb2lch(base)
    l0 = min(l0, L0 - 0.18)
    out = []
    for i in range(n):
        t = i / (n - 1)
        if t <= mid_t:
            L = l0 + (L0 - l0) * (t / mid_t) ** 0.92
            u = (mid_t - t) / mid_t
            h = _hue_toward(h0, dark_h, dk * u ** 0.9)
            C = C0 * cmul * (cdark + (1 - cdark) * (1 - u ** 1.6))
            C = max(C, cfloor_d * u)
        else:
            u = (t - mid_t) / (1 - mid_t)
            L = L0 + (l1 - L0) * u ** 0.95
            h = _hue_toward(h0, light_h, lk * u ** 1.25)
            C = C0 * cmul * (1 - (1 - clight) * u ** 1.4)
            C = max(C, cfloor_l * u)
        out.append(lch2rgb(L, C, h))
    return np.round(np.array(out)).astype(np.uint8)


def mix_ramp(ramp, col, k):
    col = hexrgb(col) if isinstance(col, str) else np.asarray(col, float)
    return np.round(ramp * (1 - k) + col * k).astype(np.uint8)


# ----------------------------------------------------------------------------- materials
class Mat:
    def __init__(self, name, ramp, gloss=12., spec=0.0, refl=0.0, env='sky', rim=0.0, bounce=0.5,
                 wrap=0.25, amb=0.10, hi=0.86, tex=0.0, tex_sx=2.0, tex_sy=2.0, dither=0.0,
                 ol=0.0, ao=0.30, bounce_col=(255, 170, 90), rim_col=(150, 210, 255), fres=3.0, emit=0.0):
        self.name, self.ramp = name, np.asarray(ramp, np.uint8)
        self.n = len(ramp)
        self.gloss, self.spec, self.refl, self.env = gloss, spec, refl, env
        self.rim, self.bounce, self.wrap, self.amb, self.hi = rim, bounce, wrap, amb, hi
        self.tex, self.tex_sx, self.tex_sy, self.dither = tex, tex_sx, tex_sy, dither
        self.ol, self.fres, self.emit, self.ao = ol, fres, emit, ao
        mid = self.ramp[self.n // 2].astype(float)
        self.bounce_ramp = mix_ramp(self.ramp, 0.5 * np.array(bounce_col) + 0.5 * mid, 0.26)
        self.rim_ramp = mix_ramp(self.ramp, 0.65 * np.array(rim_col) + 0.35 * mid, 0.58)
        self.id = -1


class Lib:
    """Material registry. Ids are global per library instance."""

    def __init__(self):
        self.mats = []
        self.by = {}

    def add(self, name, base=None, ramp=None, n=8, ramp_kw=None, **kw):
        if ramp is None:
            ramp = make_ramp(base, n=n, **(ramp_kw or {}))
        m = Mat(name, ramp, **kw)
        m.id = len(self.mats)
        self.mats.append(m)
        self.by[name] = m
        return m

    def __getitem__(self, k):
        return self.by[k].id if isinstance(k, str) else k

    def derive(self, name, src, mix=None, k=0.0, **over):
        """New material from an existing one (e.g. behind-glass or hazed versions)."""
        s = self.by[src]
        r = mix_ramp(s.ramp, mix, k) if mix is not None else s.ramp.copy()
        kw = dict(gloss=s.gloss, spec=s.spec, refl=s.refl, env=s.env, rim=s.rim, bounce=s.bounce,
                  wrap=s.wrap, amb=s.amb, hi=s.hi, tex=s.tex, tex_sx=s.tex_sx, tex_sy=s.tex_sy,
                  dither=s.dither, ol=s.ol, ao=s.ao)
        kw.update(over)
        return self.add(name, ramp=r, **kw)


# ----------------------------------------------------------------------------- noise helpers
_noise_cache = {}


def vnoise(h, w, sx, sy, seed=0, ox=0, oy=0):
    key = (seed,)
    if key not in _noise_cache:
        _noise_cache[key] = np.random.RandomState(seed).rand(512, 512)
    lat = _noise_cache[key]
    ys, xs = np.mgrid[0:h, 0:w]
    gx = (xs + ox) / sx
    gy = (ys + oy) / sy
    return ndi.map_coordinates(lat, [gy % 500, gx % 500], order=1, mode='wrap')


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------------------------- geometry buffer
NEG = -1e3
KEY = np.array([-0.55, 0.60, 0.58])
KEY = KEY / np.linalg.norm(KEY)
RIMDIR = np.array([0.60, 0.55, -0.55])
RIMDIR = RIMDIR / np.linalg.norm(RIMDIR)
BOUNCE = np.array([0.15, -0.9, 0.35])
BOUNCE = BOUNCE / np.linalg.norm(BOUNCE)
HALF = KEY + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)


class Buf:
    def __init__(self, w, h, lib):
        self.w, self.h, self.lib = w, h, lib
        self.mask = np.zeros((h, w), bool)
        self.nx = np.zeros((h, w), np.float32)
        self.ny = np.zeros((h, w), np.float32)
        self.nz = np.ones((h, w), np.float32)
        self.z = np.full((h, w), NEG, np.float32)
        self.mat = np.zeros((h, w), np.int16)
        self.pid = np.full((h, w), -1, np.int32)
        self.bias = np.zeros((h, w), np.float32)    # additive tone (glare, hand shading)
        self.nolit = np.zeros((h, w), bool)         # no outline-generating (decals etc.)
        self.skip_ol = np.zeros((h, w), bool)       # pixels that must not receive inner lines
        self.line = np.zeros((h, w), np.int8)       # inner line: 1 dark, 2 darker
        self.ops = []                               # post ops (hot spots)
        self.clip = None                            # optional bool mask restricting primitives
        self.flat = np.full((h, w), -1.0, np.float32)   # >=0: fixed tone (crisp text/LED)
        self._pid = 0

    # ------------------------------------------------------------ commit
    def newpid(self):
        self._pid += 1
        return self._pid

    def _commit(self, x0, y0, m, nx, ny, nz, z, mat, pid=None, bias=0.0, force=False):
        """Depth-tested write of a bbox-local patch."""
        hh, ww = m.shape
        sx0, sy0 = max(0, -x0), max(0, -y0)
        ex, ey = min(ww, self.w - x0), min(hh, self.h - y0)
        if ex <= sx0 or ey <= sy0:
            return np.zeros((self.h, self.w), bool)
        sl = (slice(sy0, ey), slice(sx0, ex))
        gl = (slice(y0 + sy0, y0 + ey), slice(x0 + sx0, x0 + ex))
        m, nx, ny, nz, z = m[sl], nx[sl], ny[sl], nz[sl], z[sl]
        if self.clip is not None:
            m = m & self.clip[gl]
        if np.ndim(bias) == 2:
            bias = bias[sl]
        win = m & (z >= self.z[gl] - 1e-4) if not force else m
        n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2) + 1e-6
        self.nx[gl] = np.where(win, nx / n, self.nx[gl])
        self.ny[gl] = np.where(win, ny / n, self.ny[gl])
        self.nz[gl] = np.where(win, nz / n, self.nz[gl])
        self.z[gl] = np.where(win, z, self.z[gl])
        if np.ndim(mat) == 2:
            mat = mat[sl]
        self.mat[gl] = np.where(win, mat, self.mat[gl])
        self.pid[gl] = np.where(win, self.newpid() if pid is None else pid, self.pid[gl])
        self.bias[gl] = np.where(win, bias, self.bias[gl])
        self.line[gl] = np.where(win, 0, self.line[gl])
        self.flat[gl] = np.where(win, -1.0, self.flat[gl])
        self.mask[gl] = self.mask[gl] | win
        out = np.zeros((self.h, self.w), bool)
        out[gl] = win
        return out

    # ------------------------------------------------------------ primitives
    def box(self, x0, y0, x1, y1, mat, z=0.0, bevel=2.0, bulge_y=0.0, bulge_x=0.0, rc=0,
            pid=None, bias=0.0, zscale=1.0, tilt=(0, 0)):
        """Bevelled box (x1,y1 exclusive).  bevel = float or (l, r, t, b) radii of circular
        edge bevels.  bulge_*: overall convex curvature (normal tilts away from centre).
        rc: corner cut radius in pixels (silhouette)."""
        bl, br, bt, bb = (bevel,) * 4 if np.isscalar(bevel) else bevel
        ys, xs = np.mgrid[y0:y1, x0:x1]
        px, py = xs + 0.5, ys + 0.5
        dl, dr, dt, db = px - x0, x1 - px, py - y0, y1 - py
        tl = np.clip(1 - dl / bl, 0, 1) if bl > 0 else 0 * px
        tr = np.clip(1 - dr / br, 0, 1) if br > 0 else 0 * px
        tt = np.clip(1 - dt / bt, 0, 1) if bt > 0 else 0 * px
        tb = np.clip(1 - db / bb, 0, 1) if bb > 0 else 0 * px
        nxv = tr - tl + tilt[0]
        nyv = tt - tb + tilt[1]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        nxv = nxv + bulge_x * (px - cx) / max(1, (x1 - x0) / 2)
        nyv = nyv + bulge_y * (-(py - cy)) / max(1, (y1 - y0) / 2)
        q = np.clip(nxv ** 2 + nyv ** 2, 0, 0.97)
        s = np.sqrt(nxv ** 2 + nyv ** 2 + 1e-9)
        f = np.where(s > 0.97, 0.97 / s, 1.0)
        nxv, nyv = nxv * f, nyv * f
        nzv = np.sqrt(1 - q)
        zz = z - (bl * (1 - np.sqrt(1 - tl ** 2)) + br * (1 - np.sqrt(1 - tr ** 2)) +
                  bt * (1 - np.sqrt(1 - tt ** 2)) + bb * (1 - np.sqrt(1 - tb ** 2))) * zscale
        m = np.ones(px.shape, bool)
        if rc > 0:
            for (ax, ay, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
                cxx, cyy = ax + sx * rc, ay + sy * rc
                zone = ((px - cxx) * sx < 0) & ((py - cyy) * sy < 0)
                m &= ~(zone & (np.hypot(px - cxx, py - cyy) > rc))
        return self._commit(x0, y0, m, nxv, nyv, nzv, zz, self.lib[mat], pid, bias)

    def cyl_v(self, x0, y0, x1, y1, mat, z=0.0, cap=1.0, **kw):
        r = (x1 - x0) / 2
        return self.box(x0, y0, x1, y1, mat, z, bevel=(r, r, cap, cap), **kw)

    def cyl_h(self, x0, y0, x1, y1, mat, z=0.0, cap=1.0, **kw):
        r = (y1 - y0) / 2
        return self.box(x0, y0, x1, y1, mat, z, bevel=(cap, cap, r, r), **kw)

    def ellipsoid(self, cx, cy, rx, ry, mat, z=0.0, rz=None, pid=None, bias=0.0, fat=0.35, ang=0.0):
        """Ellipsoid; `ang` rotates its rx axis (radians, screen space, clockwise positive)."""
        rz = rz or min(rx, ry)
        R = max(rx, ry) if ang else None
        if ang:
            x0, x1 = int(np.floor(cx - R - 1)), int(np.ceil(cx + R + 1))
            y0, y1 = int(np.floor(cy - R - 1)), int(np.ceil(cy + R + 1))
        else:
            x0, x1 = int(np.floor(cx - rx - 1)), int(np.ceil(cx + rx + 1))
            y0, y1 = int(np.floor(cy - ry - 1)), int(np.ceil(cy + ry + 1))
        ys, xs = np.mgrid[y0:y1, x0:x1]
        dx, dy = xs + 0.5 - cx, ys + 0.5 - cy
        ca, sa = np.cos(ang), np.sin(ang)
        lx, ly = dx * ca + dy * sa, -dx * sa + dy * ca
        u, v = lx / rx, ly / ry
        q = u * u + v * v
        m = q <= (1 + fat / min(rx, ry)) ** 2
        qq = np.clip(q, 0, 0.995)
        nzv = np.sqrt(1 - qq)
        # local normal -> screen (rotate back)
        lnx, lny = u / rx, v / ry
        nxv = lnx * ca - lny * sa
        nys = lnx * sa + lny * ca
        nyv, nzn = -nys, nzv / rz
        zz = z + rz * nzv
        return self._commit(x0, y0, m, nxv, nyv, nzn, zz, self.lib[mat], pid, bias)

    def capsule(self, p0, p1, r0, r1, mat, z=0.0, pid=None, bias=0.0, rz=None, fat=0.3):
        (ax, ay), (bx, by) = p0, p1
        rm = max(r0, r1)
        x0, x1 = int(min(ax, bx) - rm - 1), int(max(ax, bx) + rm + 2)
        y0, y1 = int(min(ay, by) - rm - 1), int(max(ay, by) + rm + 2)
        ys, xs = np.mgrid[y0:y1, x0:x1]
        px, py = xs + 0.5, ys + 0.5
        d = np.array([bx - ax, by - ay], float)
        L2 = max(d @ d, 1e-6)
        t = np.clip(((px - ax) * d[0] + (py - ay) * d[1]) / L2, 0, 1)
        qx, qy = ax + t * d[0], ay + t * d[1]
        r = r0 + (r1 - r0) * t
        dx, dy = px - qx, py - qy
        dist = np.hypot(dx, dy)
        m = dist <= r + fat
        u = np.clip(dist / r, 0, 0.995)
        nzv = np.sqrt(1 - u * u)
        nxv = dx / r
        nyv = -dy / r
        zz = z + r * nzv * (rz / r if rz else 1.0)
        return self._commit(x0, y0, m, nxv, nyv, nzv, zz, self.lib[mat], pid, bias)

    def cone(self, cx, y_apex, y_base, r_base, mat, z=0.0, pid=None, bias=0.0, lean=0.0):
        """Vertical cone/triangle (apex up if y_apex<y_base)."""
        x0, x1 = int(cx - r_base - 1 - abs(lean)), int(cx + r_base + 2 + abs(lean))
        ya, yb = min(y_apex, y_base), max(y_apex, y_base)
        ys, xs = np.mgrid[int(ya):int(yb) + 1, x0:x1]
        px, py = xs + 0.5, ys + 0.5
        frac = np.clip((py - y_apex) / (y_base - y_apex), 0, 1)
        ccx = cx + lean * (1 - frac)
        w = np.maximum(r_base * frac, 0.4)
        u = (px - ccx) / w
        m = (np.abs(u) <= 1.0) & (frac > 0) & (frac <= 1.0)
        nzv = np.sqrt(1 - np.clip(u * u, 0, 0.99))
        slope = r_base / abs(y_base - y_apex)
        sgn = 1.0 if y_apex < y_base else -1.0
        nxv, nyv, nzn = u * nzv, 0 * u + slope * 0.9 * sgn, nzv
        return self._commit(int(x0), int(ya), m, nxv, nyv, nzn, z + w * nzv, self.lib[mat], pid, bias)

    def inflate(self, mask, mat, z=0.0, b=3.0, height=None, noise=0.0, nseed=1, nscale=3.0,
                pid=None, bias=0.0, base_n=(0, 0, 1), smooth=0.8, zscale=1.0, flat_top=True):
        """Distance-transform inflation of an arbitrary boolean mask (full-buffer size).
        Circular bevel of radius b around the silhouette; b large -> pillow/blob."""
        mask = mask.copy()
        dist = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
        if noise:
            dist = dist + (vnoise(self.h, self.w, nscale, nscale, nseed) - 0.5) * 2 * noise
        d = ndi.gaussian_filter(dist, smooth) if smooth else dist
        gy, gx = np.gradient(d)
        gn = np.hypot(gx, gy) + 1e-6
        outx, outy = -gx / gn, gy / gn          # outward, world y up
        t = np.clip(1 - (d - 0.5) / b, 0, 1)
        t = np.clip(t, 0, 0.98)
        nxv = outx * t + base_n[0] * (1 - t)
        nyv = outy * t + base_n[1] * (1 - t)
        nzv = np.sqrt(np.clip(1 - t * t, 0.02, 1)) * base_n[2]
        zz = z + b * zscale * np.sqrt(np.clip(1 - (1 - np.clip((d - 0.5) / b, 0, 1)) ** 2, 0, 1))
        return self._commit(0, 0, mask, nxv, nyv, nzv, zz, self.lib[mat], pid, bias)

    def scatter_bumps(self, region, count, rmin, rmax, mats, z=0.0, seed=0, aspect=(1.0, 1.0),
                      zrange=4.0, bias_jit=0.06, pid=None, rz_k=0.8, angle_jit=0.0, bias_by_y=0.0):
        """Fill `region` (bool mask) with overlapping ellipsoids (bracts, leaves, tufts)."""
        rng = np.random.RandomState(seed)
        ys, xs = np.nonzero(region)
        if len(xs) == 0:
            return
        pid = pid if pid is not None else self.newpid()
        order = []
        for i in range(count):
            k = rng.randint(len(xs))
            r = rng.uniform(rmin, rmax)
            order.append((rng.uniform(0, zrange), xs[k] + 0.5, ys[k] + 0.5, r, mats[rng.randint(len(mats))],
                          rng.uniform(-bias_jit, bias_jit), rng.uniform(aspect[0], aspect[1])))
        order.sort(key=lambda t: t[0])
        for zc, cx, cy, r, mt, bj, asp in order:
            rx, ry = r * asp, r / asp
            self.ellipsoid(cx, cy, rx, ry, mt, z=z + zc, rz=min(rx, ry) * rz_k, pid=pid,
                           bias=bj + bias_by_y * (cy / self.h))

    def erase(self, m):
        self.mask[m] = False
        self.z[m] = NEG
        self.pid[m] = -1
        self.line[m] = 0
        self.bias[m] = 0

    def mask_poly(self, pts):
        im = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
        return np.array(im) > 0

    def mask_ellipse(self, cx, cy, rx, ry):
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        return ((xs + 0.5 - cx) / rx) ** 2 + ((ys + 0.5 - cy) / ry) ** 2 <= 1.0

    def mask_rect(self, x0, y0, x1, y1):
        m = np.zeros((self.h, self.w), bool)
        m[max(0, int(y0)):max(0, int(y1)), max(0, int(x0)):max(0, int(x1))] = True
        return m

    def mask_line(self, pts, width=1):
        im = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(im).line([tuple(p) for p in pts], fill=255, width=width)
        return np.array(im) > 0

    # ------------------------------------------------------------ decals / hand shading
    def decal(self, m, mat, bias=None, only_mat=None, flat=None):
        """Re-material pixels of m (keeps normals / depth) -> panel paint, stripes, text."""
        sel = m & self.mask
        if only_mat is not None:
            sel &= self.mat == self.lib[only_mat]
        self.mat[sel] = self.lib[mat]
        if flat is not None:
            self.flat[sel] = flat
        if bias is not None:
            self.bias[sel] += bias
        return sel

    def tone(self, m, amount):
        sel = m & self.mask
        self.bias[sel] += (amount[sel] if np.ndim(amount) == 2 else amount)

    def set_line(self, m, level=1):
        self.line[m & self.mask] = level

    def text(self, x, y, s, mat, spacing=1, scale=1, bias=None, flat=None):
        if flat is None:
            flat = 0.96 if mat in ('sign_white', 'sign_yellow', 'light_warm', 'paint_white') else 0.62
        from_font = viet_mask(s, spacing)
        if scale > 1:
            from_font = np.kron(from_font, np.ones((scale, scale), bool))
        h, w = from_font.shape
        m = np.zeros((self.h, self.w), bool)
        sy0, sx0 = max(0, -y), max(0, -x)
        ey, ex = min(h, self.h - y), min(w, self.w - x)
        if ey > sy0 and ex > sx0:
            m[y + sy0:y + ey, x + sx0:x + ex] = from_font[sy0:ey, sx0:ex]
        return self.decal(m, mat, bias, flat=flat)

    def glare(self, m, offset=0.0, period=22.0, bands=((0.0, 4, 0.20), (6.0, 2, 0.28)), slope=1.0):
        """Diagonal glass glare streaks (added to tone before quantising)."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        u = (xs + slope * ys + offset) % period
        add = np.zeros((self.h, self.w), np.float32)
        for o, w_, s in bands:
            add += np.where((u >= o) & (u < o + w_), s, 0.0)
        self.bias += np.where(m & self.mask, add, 0)

    def hot(self, x, y, w=2, h=1, mat=None, shoulder=True, col=None):
        """Specular hot spot: near-white w*h rect with a 1px shoulder in the material's top-1 tone."""
        self.ops.append(('hot', x, y, w, h, mat, shoulder, col))

    def px(self, pts):
        """Explicit post-render pixels [(x, y, (r, g, b)), ...] (whiskers, sparkles)."""
        self.ops.append(('px', pts))

    def shade_poly(self, pts, amount):
        self.tone(self.mask_poly(pts), amount)

    # ------------------------------------------------------------ rendering
    def _shadow(self, K=22):
        sh = np.zeros((self.h, self.w), bool)
        z = self.z
        for k in range(1, K + 1):
            s = k * 1.2
            dx, dy = int(round(KEY[0] * s)), int(round(-KEY[1] * s))
            sz = np.full_like(z, NEG)
            ys0, ys1 = max(0, -dy), min(self.h, self.h - dy)
            xs0, xs1 = max(0, -dx), min(self.w, self.w - dx)
            sz[ys0:ys1, xs0:xs1] = z[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
            sh |= sz > z + KEY[2] * s * 0.9 + 0.8
        return sh & self.mask

    def _ao(self):
        zm = ndi.maximum_filter(self.z, size=5)
        occ = np.clip((zm - self.z - 0.6) / 5.0, 0, 1)
        occ = ndi.uniform_filter(occ, 3)
        return np.where(self.mask, occ, 0)

    def render(self, outline=True, cleanup=True, shadows=True, ao=True, env_scale=1.0,
               skyline_seed=3, ol_strength=1.0, shadow_k=22, ground_amt=1.0, sun=1.0):
        H, W = self.h, self.w
        m = self.mask
        lib = self.lib
        sh = self._shadow(shadow_k) if shadows else np.zeros((H, W), bool)
        occ = self._ao() if ao else np.zeros((H, W), np.float32)
        N = np.stack([self.nx, self.ny, self.nz], -1)
        ndl = N @ KEY
        ndh = np.clip(N @ HALF, 0, 1)
        rim_d = np.clip(N @ RIMDIR, 0, 1)
        bnc = np.clip(N @ BOUNCE, 0, 1)
        # reflection vector (view = +z): r = 2 nz n - v
        rx_, ry_ = 2 * self.nz * self.nx, 2 * self.nz * self.ny
        ys, xs = np.mgrid[0:H, 0:W]
        skyline = (vnoise(H, W, 7.0, 7.0, skyline_seed, ox=0, oy=0)) - 0.5
        step_sky = np.floor((np.sin(xs * 0.11 + rx_ * 6) * 0.5 + np.sin(xs * 0.047 + 1.3) * 0.5) * 3) / 3.0
        ryw_base = ry_ - 0.045 * (step_sky + 0.5) * np.where(ry_ > -0.2, 1, 0)
        idx = np.zeros((H, W), np.int16)
        variant = np.zeros((H, W), np.int8)      # 0 base, 1 bounce, 2 rim
        t_all = np.zeros((H, W), np.float32)
        spec_all = np.zeros((H, W), np.float32)
        noise_cache = {}
        for mt in lib.mats:
            sel = m & (self.mat == mt.id)
            if not sel.any():
                continue
            diff = np.clip((ndl + mt.wrap) / (1 + mt.wrap), 0, 1)
            diff = diff * np.where(sh, 0.28, 1.0) * sun + (1 - sun) * 0.5 * diff
            t = mt.amb + (mt.hi - mt.amb) * diff
            # bounce lifts the lower shadow edge
            bamt = bnc * (1 - diff) * mt.bounce
            t = t + 0.20 * bamt * (diff < 0.5)
            # environment reflection
            if mt.refl > 0:
                fres = mt.refl + (1 - mt.refl) * (1 - self.nz) ** mt.fres
                wob = {'chrome': 0.30, 'glass': 0.02, 'sky': 0.05}.get(mt.env, 0.0)
                ryw = ryw_base - wob * (np.sin(rx_ * 5.0 + xs * 0.05) * 0.5 + 0.2)
                te = env_tone(ryw, mt.env)
                t = t * (1 - fres * env_scale) + te * fres * env_scale
            spec = (ndh ** mt.gloss) * (mt.spec) * np.where(sh, 0, 1)
            t = t - mt.ao * occ * (1 - 0.5 * mt.refl)
            t = t + self.bias
            t = np.where(self.flat >= 0, self.flat, t)
            if mt.tex:
                key = (mt.tex_sx, mt.tex_sy)
                if key not in noise_cache:
                    noise_cache[key] = vnoise(H, W, mt.tex_sx, mt.tex_sy, 11)
                t = t + (noise_cache[key] - 0.5) * mt.tex
            if mt.dither:
                bay = np.array([[0, 2], [3, 1]]) / 4.0 - 0.375
                t = t + bay[ys % 2, xs % 2] * mt.dither
            n = mt.n
            i = np.clip(np.floor(t * (n - 1) + 0.5), 0, n - 1).astype(np.int16)
            i = np.where(t >= 0.985, n - 1, i)
            spec = np.where(self.flat >= 0, 0, spec)
            i = np.where(spec > 0.50, n - 1, np.where(spec > 0.22, np.maximum(i, n - 2), i))
            idx[sel] = i[sel]
            t_all[sel] = t[sel]
            v = np.zeros((H, W), np.int8)
            if mt.rim > 0:
                edge = (1 - self.nz)
                rimv = rim_d * edge * mt.rim
                v = np.where((rimv > 0.20) & (~sh | (rim_d > 0.5)), 2, v)
            v = np.where((v == 0) & (bamt > 0.30) & (t < 0.62), 1, v)
            variant[sel] = v[sel]
        # --- cleanup of orphan tone pixels (same material neighbourhood)
        if cleanup:
            idx = self._orphans(idx, variant)
        # --- colours
        out = np.zeros((H, W, 4), np.uint8)
        for mt in lib.mats:
            sel = m & (self.mat == mt.id)
            if not sel.any():
                continue
            for v, rp in ((0, mt.ramp), (1, mt.bounce_ramp), (2, mt.rim_ramp)):
                s2 = sel & (variant == v)
                out[s2, :3] = rp[idx[s2]]
        out[m, 3] = 255
        self.idx = idx
        # --- inner part lines
        if outline:
            out = self._inner_lines(out, idx, ol_strength)
        # --- explicit inner lines (set_line)
        for lv in (1, 2):
            s = (self.line == lv) & m
            if s.any():
                for mt in lib.mats:
                    s2 = s & (self.mat == mt.id)
                    if s2.any():
                        out[s2, :3] = mt.ramp[0 if lv == 2 else 1]
        # --- outer outline
        if outline:
            out = self._outer_outline(out, idx, ol_strength)
        for op in self.ops:
            if op[0] == 'hot':
                out = self._do_hot(out, *op[1:])
            elif op[0] == 'px':
                for (x, y, c) in op[1]:
                    if 0 <= x < self.w and 0 <= y < self.h:
                        out[y, x] = (c[0], c[1], c[2], 255)
        return out

    def _orphans(self, idx, variant):
        H, W = idx.shape
        m = self.mask
        for _ in range(2):
            pad = lambda a, v: np.pad(a, 1, constant_values=v)
            pi, pm, pt = pad(idx, -9), pad(self.mat, -9), pad(self.pid, -9)
            nb = []
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                sl = (slice(1 + dy, H + 1 + dy), slice(1 + dx, W + 1 + dx))
                nb.append((pi[sl], (pm[sl] == self.mat) & (pt[sl] == self.pid)))
            cnt = np.zeros((H, W), int)
            val = np.zeros((H, W), int)
            for (a, ok), (b, ok2) in [(nb[0], nb[1]), (nb[2], nb[3])]:
                pass
            # orphan: >=3 same-part neighbours that share one idx different from own
            new = idx.copy()
            for cand in nb:
                a, ok = cand
                same = np.zeros((H, W), int)
                for b, ok2 in nb:
                    same += ((b == a) & ok & ok2)
                hit = ok & (same >= 3) & (a != idx) & m & (self.mat != -1) & (idx < self._maxidx() - 0)
                new = np.where(hit & (np.abs(a - idx) <= 3), a, new)
            top = np.array([mt.n - 1 for mt in self.lib.mats])[self.mat]
            idx = np.where(idx >= top, idx, new)      # keep specular hot pixels
        return idx

    def _maxidx(self):
        return 99

    def _inner_lines(self, out, idx, strength):
        H, W = self.h, self.w
        z, pid, m = self.z, self.pid, self.mask
        line = np.zeros((H, W), bool)
        dark = np.zeros((H, W), np.int8)
        for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            zs = np.full((H, W), NEG, np.float32)
            ps = np.full((H, W), -9, np.int32)
            ys0, ys1 = max(0, -dy), min(H, H - dy)
            xs0, xs1 = max(0, -dx), min(W, W - dx)
            zs[ys0:ys1, xs0:xs1] = z[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
            ps[ys0:ys1, xs0:xs1] = pid[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx]
            nbm = zs > NEG / 2
            dz = zs - z
            # the farther pixel gets the line
            hit = m & nbm & (dz > 1.6) & (ps != pid)
            line |= hit
            # lit side: neighbour is to the right/below (light is upper-left) -> this pixel is on a lit edge?
            dark |= np.where(hit & ((dx <= 0) & (dy <= 0)), 2, np.where(hit, 1, 0)).astype(np.int8)
        for mt in self.lib.mats:
            s = line & (self.mat == mt.id) & ~self.skip_ol
            if not s.any():
                continue
            lo = np.where(dark[s] == 2, 1, 0)   # lit-side lines are one tone lighter
            out[s, :3] = mt.ramp[np.minimum(lo, mt.n - 1)] if False else mt.ramp[lo]
        return out

    def _outer_outline(self, out, idx, strength):
        H, W = self.h, self.w
        m = self.mask
        pm = np.pad(m, 1)
        cand = np.zeros((H, W), bool)
        src = np.full((H, W), -1, np.int16)
        lit = np.zeros((H, W), np.float32)
        colr = np.zeros((H, W, 3), np.uint8)
        # pixel-perfect: 4-neighbourhood only
        order = [(-1, 0, (0.0, -1.0)), (0, -1, (-1.0, 0.0)), (1, 0, (0.0, 1.0)), (0, 1, (1.0, 0.0))]
        for dy, dx, dirv in order:
            sl = (slice(1 + dy, H + 1 + dy), slice(1 + dx, W + 1 + dx))
            nb = pm[sl]
            take = ~m & nb & ~cand
            mat_nb = np.pad(self.mat, 1)[sl]
            idx_nb = np.pad(idx, 1)[sl]
            # light dir on screen is up-left: outline pixel above/left of the shape is a lit edge
            l = -(dirv[0] * -0.7 + dirv[1] * -0.7)  # dirv = pixel->shape ; outline pixel lies opposite
            for mt in self.lib.mats:
                s = take & (mat_nb == mt.id)
                if not s.any():
                    continue
                lvl = 1 if l > 0.2 else 0
                # darker where the neighbouring surface is dark, lighter where it is lit
                base = np.where(idx_nb[s] >= mt.n - 3, 2, lvl + (idx_nb[s] >= mt.n // 2))
                base = np.minimum(base, 2)
                if l <= 0.2:
                    base = np.minimum(base, 1)
                colr[s] = mt.ramp[base]
                if mt.ol:
                    colr[s] = np.round(colr[s] * (1 - mt.ol)).astype(np.uint8)
            cand |= take
        # pixel-perfect corner cleanup: remove L-corner outline pixels (keeps diagonal connectivity)
        pc = np.pad(cand, 1)
        up, dn, lf, rt = pc[:-2, 1:-1], pc[2:, 1:-1], pc[1:-1, :-2], pc[1:-1, 2:]
        corner = cand & ((up & lf & ~dn & ~rt) | (up & rt & ~dn & ~lf) | (dn & lf & ~up & ~rt) | (dn & rt & ~up & ~lf))
        # only drop if shape pixels are not exposed to a 4-neighbour of the dropped pixel
        keep = cand & ~corner
        out[keep, :3] = colr[keep]
        out[keep, 3] = 255
        return out

    def _do_hot(self, out, x, y, w, h, mat, shoulder, col):
        if not (0 <= x < self.w and 0 <= y < self.h):
            return out
        hc = np.array(col if col is not None else (255, 252, 235), np.uint8)
        if mat is not None and col is None:
            mt = self.lib.mats[self.lib[mat]]
            hc = np.minimum(255, mt.ramp[-1].astype(int) + 60).astype(np.uint8)
            hc = np.array([max(hc[0], 250), max(hc[1], 246), max(hc[2], 225)], np.uint8)
        if shoulder:
            for yy in range(y - 1, y + h + 1):
                for xx in range(x - 1, x + w + 1):
                    if 0 <= xx < self.w and 0 <= yy < self.h and self.mask[yy, xx]:
                        if not (x <= xx < x + w and y <= yy < y + h):
                            if (xx in (x - 1, x + w) and yy in (y - 1, y + h)):
                                continue
                            mt = self.lib.mats[self.mat[yy, xx]]
                            out[yy, xx, :3] = mt.ramp[-2]
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < self.w and 0 <= yy < self.h and self.mask[yy, xx]:
                    out[yy, xx, :3] = hc
        return out

    def image(self, **kw):
        return Image.fromarray(self.render(**kw), 'RGBA')


def env_tone(ry, kind='sky'):
    """Environment tone for reflection-vector elevation ry (up positive).
    Sky -> sharp bright horizon line -> dark ground (90s chrome / car-paint look)."""
    if kind == 'chrome':
        top, hor, gh, gb = 0.70, 0.93, 0.34, 0.08
    elif kind == 'glass':
        top, hor, gh, gb = 0.62, 0.86, 0.18, 0.08
    elif kind == 'wet':
        top, hor, gh, gb = 0.78, 0.96, 0.30, 0.18
    else:  # paint
        top, hor, gh, gb = 0.74, 0.92, 0.40, 0.20
    up = hor + (top - hor) * np.clip((ry - 0.07) / 0.55, 0, 1)
    dn = gh + (gb - gh) * np.clip((-ry) / 0.55, 0, 1)
    t = np.where(ry > 0.07, up, np.where(ry > 0.0, 1.0, dn))
    return t


# ----------------------------------------------------------------------------- font (5x7) + Vietnamese
_G = {
    'A': ".###.|#...#|#...#|#####|#...#|#...#|#...#", 'B': "####.|#...#|#...#|####.|#...#|#...#|####.",
    'C': ".####|#....|#....|#....|#....|#....|.####", 'D': "####.|#...#|#...#|#...#|#...#|#...#|####.",
    'E': "#####|#....|#....|####.|#....|#....|#####", 'F': "#####|#....|#....|####.|#....|#....|#....",
    'G': ".####|#....|#....|#.###|#...#|#...#|.###.", 'H': "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    'I': ".###.|..#..|..#..|..#..|..#..|..#..|.###.", 'J': "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    'K': "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#", 'L': "#....|#....|#....|#....|#....|#....|#####",
    'M': "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#", 'N': "#...#|##..#|#.#.#|#..##|#...#|#...#|#...#",
    'O': ".###.|#...#|#...#|#...#|#...#|#...#|.###.", 'P': "####.|#...#|#...#|####.|#....|#....|#....",
    'Q': ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#", 'R': "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    'S': ".####|#....|#....|.###.|....#|....#|####.", 'T': "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    'U': "#...#|#...#|#...#|#...#|#...#|#...#|.###.", 'V': "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    'W': "#...#|#...#|#...#|#.#.#|#.#.#|##.##|#...#", 'X': "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    'Y': "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..", 'Z': "#####|....#|...#.|..#..|.#...|#....|#####",
    '0': ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.", '1': "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    '2': ".###.|#...#|....#|...#.|..#..|.#...|#####", '3': "####.|....#|....#|.###.|....#|....#|####.",
    '4': "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.", '5': "#####|#....|####.|....#|....#|#...#|.###.",
    '6': ".###.|#....|#....|####.|#...#|#...#|.###.", '7': "#####|....#|...#.|..#..|.#...|.#...|.#...",
    '8': ".###.|#...#|#...#|.###.|#...#|#...#|.###.", '9': ".###.|#...#|#...#|.####|....#|....#|.###.",
    '-': ".....|.....|.....|.###.|.....|.....|.....", '.': ".....|.....|.....|.....|.....|.....|..#..",
    '&': ".##..|#..#.|.##..|.#.#.|#..##|#..#.|.##.#", '/': "....#|....#|...#.|..#..|.#...|#....|#....",
    'Đ': "####.|#...#|#...#|#####|#...#|#...#|####.", ' ': ".....|.....|.....|.....|.....|.....|.....",
}
_G = {k: np.array([[c == '#' for c in row] for row in v.split('|')]) for k, v in _G.items()}
_MARKS = {
    '\u0301': [(4, -3), (3, -2), (2, -1)],                       # acute
    '\u0300': [(0, -3), (1, -2), (2, -1)],                       # grave
    '\u0309': [(2, -4), (3, -4), (3, -3), (2, -2), (2, -1)],     # hook above
    '\u0303': [(0, -2), (1, -3), (2, -2), (3, -3), (4, -2)],     # tilde
    '\u0302': [(2, -3), (1, -2), (3, -2), (0, -1), (4, -1)],     # circumflex
    '\u0306': [(0, -2), (1, -1), (2, -1), (3, -1), (4, -2)],     # breve
}


def viet_mask(s, spacing=1):
    import unicodedata
    s = s.upper()
    glyphs = []
    for ch in unicodedata.normalize('NFD', s):
        if unicodedata.combining(ch):
            glyphs[-1][1].append(ch)
        else:
            glyphs.append([ch, []])
    cells = []
    x = 0
    pts = []
    for ch, marks in glyphs:
        g = _G.get(ch, _G[' '])
        horn = '̛' in marks
        gy = 6
        for yy in range(7):
            for xx in range(g.shape[1]):
                if g[yy, xx]:
                    pts.append((x + xx, gy + yy))
        if horn:
            pts += [(x + 5, gy), (x + 5, gy + 1), (x + 5, gy + 2)]
        has_shape = any(mk in ('̂', '̆') for mk in marks)
        for mk in marks:
            if mk == '̣':
                pts += [(x + 2, gy + 8), (x + 2, gy + 9)]
            elif mk in _MARKS:
                off = -3 if (has_shape and mk not in ('̂', '̆')) else 0
                for (px, py) in _MARKS[mk]:
                    pts.append((x + px + (1 if off else 0), gy + py + off))
        x += g.shape[1] + (1 if horn else 0) + spacing
    W = max(1, x - spacing)
    img = np.zeros((18, W + 1), bool)
    for px, py in pts:
        if 0 <= px < img.shape[1] and 0 <= py < 18:
            img[py, px] = True
    # trim empty rows top/bottom but keep letter baseline alignment: baseline row 5..11
    return img[1:16]            # rows: accent zone 4 rows, letters 7 rows, dot-below 2 rows


# ----------------------------------------------------------------------------- utilities
def paste(dst, src, x, y):
    """Alpha-test paste of PIL RGBA src onto PIL RGBA dst (hard alpha)."""
    dst.alpha_composite(src, (int(x), int(y))) if False else dst.paste(src, (int(x), int(y)), src)


def count_colors(img):
    a = np.array(img.convert('RGBA'))
    a = a[a[..., 3] > 0][:, :3]
    return len(np.unique(a, axis=0))


def harden_alpha(img):
    a = np.array(img.convert('RGBA'))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    return Image.fromarray(a, 'RGBA')


def upscale(img, k=3):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


# ----------------------------------------------------------------------------- material library
def default_lib():
    L = Lib()
    A = L.add
    # car paint / gloss
    A('paint_yellow', '#f7c313', n=9, gloss=40, spec=1.0, refl=0.30, env='sky', rim=1.0, bounce=0.8, wrap=0.2, fres=3)
    A('paint_orange', '#f27d12', n=9, gloss=40, spec=1.0, refl=0.30, env='sky', rim=1.0, bounce=0.8, wrap=0.2)
    A('paint_red', '#d8222c', n=9, gloss=40, spec=1.0, refl=0.30, env='sky', rim=1.0, bounce=0.8, wrap=0.2)
    A('paint_white', '#e9edf2', n=9, gloss=40, spec=1.0, refl=0.28, env='sky', rim=1.0, bounce=0.8, wrap=0.2,
      ramp_kw=dict(l0=0.38, cdark=1.0, cfloor_d=0.05))
    A('paint_green', '#1f8a4c', n=9, gloss=40, spec=1.0, refl=0.28, env='sky', rim=1.0)
    A('chrome', '#a9b6cc', n=9, gloss=90, spec=1.0, refl=0.88, env='chrome', rim=0.6, wrap=0.1,
      ramp_kw=dict(l0=0.2, cdark=1.0, cfloor_d=0.05, cfloor_l=0.02, dk=0.6))
    A('metal_dark', '#4a5568', n=8, gloss=30, spec=0.8, refl=0.35, env='chrome', rim=0.8,
      ramp_kw=dict(l0=0.2, cfloor_d=0.04))
    A('metal_light', '#c4ccd8', n=8, gloss=35, spec=0.8, refl=0.35, env='chrome', rim=0.8,
      ramp_kw=dict(l0=0.3, cfloor_d=0.04))
    A('rubber', '#2b2c38', n=7, gloss=12, spec=0.3, rim=0.8, ramp_kw=dict(l0=0.12, l1=0.6))
    A('glass', '#2f7aa0', n=9, gloss=120, spec=1.0, refl=0.55, env='glass', rim=0.6, wrap=0.1, amb=0.25, hi=0.65,
      ramp_kw=dict(l0=0.2, l1=0.97, dk=0.35, cdark=0.9))
    A('glass_light', '#7fc8e8', n=9, gloss=120, spec=1.0, refl=0.6, env='glass', rim=0.6, amb=0.3, hi=0.7)
    A('plastic_blue', '#2a6fe0', n=9, gloss=55, spec=1.0, refl=0.18, env='sky', rim=1.0, bounce=0.9)
    A('plastic_teal', '#18a6b0', n=8, gloss=55, spec=0.9, refl=0.15, rim=1.0)
    A('concrete', '#b7b2a8', n=8, gloss=6, spec=0.1, rim=0.4, bounce=0.6, wrap=0.3, tex=0.06, tex_sx=3, tex_sy=2,
      ramp_kw=dict(cfloor_d=0.03, cdark=0.9))
    A('concrete_dark', '#8e8a88', n=8, gloss=6, spec=0.1, rim=0.4, bounce=0.6, wrap=0.3, tex=0.06,
      ramp_kw=dict(cfloor_d=0.03))
    A('asphalt', '#555766', n=8, gloss=25, spec=0.35, refl=0.10, env='wet', rim=0.0, wrap=0.3, tex=0.14, tex_sx=1.5,
      tex_sy=1.5, ramp_kw=dict(l0=0.2, cfloor_d=0.04, cfloor_l=0.02))
    A('bark', '#80553a', n=8, gloss=8, spec=0.1, rim=0.7, tex=0.2, tex_sx=2, tex_sy=4)
    A('leaf_a', '#3ea23e', n=9, gloss=25, spec=0.5, rim=0.8, bounce=0.5, wrap=0.35)
    A('leaf_b', '#2c7d3d', n=9, gloss=25, spec=0.5, rim=0.8, bounce=0.5, wrap=0.35)
    A('leaf_c', '#7fc43c', n=9, gloss=25, spec=0.5, rim=0.8, bounce=0.5, wrap=0.35)
    A('bract_a', '#e3228f', n=10, gloss=30, spec=0.42, refl=0.0, rim=0.55, bounce=0.9, wrap=0.22, amb=0.10, ao=0.55, hi=0.84,
      ramp_kw=dict(dk=0.5, lk=0.28, cdark=0.75))
    A('bract_b', '#ff4fb4', n=10, gloss=30, spec=0.42, refl=0.0, rim=0.55, bounce=0.9, wrap=0.22, ao=0.55, hi=0.84,
      ramp_kw=dict(dk=0.5, lk=0.3))
    A('bract_c', '#a81f93', n=10, gloss=30, spec=0.42, refl=0.0, rim=0.55, bounce=0.9, wrap=0.22, ao=0.55, hi=0.84,
      ramp_kw=dict(dk=0.4, lk=0.3))
    A('bract_d', '#ff7cc9', n=10, gloss=30, spec=0.42, refl=0.0, rim=0.55, bounce=0.9, wrap=0.22, ao=0.55, hi=0.84,
      ramp_kw=dict(dk=0.5, lk=0.3))
    A('fur_orange', '#f0912a', n=9, gloss=10, spec=0.15, rim=1.0, bounce=0.9, wrap=0.55, amb=0.14, tex=0.10, tex_sx=1.4,
      tex_sy=2.4, ramp_kw=dict(dk=0.5, cdark=0.8))
    A('fur_dark', '#a8501c', n=9, gloss=10, spec=0.15, rim=1.0, bounce=0.9, wrap=0.55, tex=0.08,
      ramp_kw=dict(dk=0.5, l0=0.2))
    A('fur_cream', '#fff2dc', n=9, gloss=10, spec=0.1, rim=1.0, bounce=0.9, wrap=0.55, tex=0.08, tex_sx=1.4, tex_sy=2.4,
      ramp_kw=dict(l0=0.5, dk=0.9, cdark=1.4, cmul=1.3))
    A('pink', '#ff8fa8', n=7, gloss=40, spec=0.8, rim=0.6, refl=0.1)
    A('eye', '#7ed23a', n=8, gloss=80, spec=1.0, refl=0.25, env='glass', rim=0.0, amb=0.3, hi=0.9)
    A('black', '#1a1a26', n=6, gloss=60, spec=0.9, refl=0.2, env='glass', rim=0.6, ramp_kw=dict(l0=0.1, l1=0.55))
    A('skin', '#e9a97c', n=8, gloss=18, spec=0.3, rim=1.0, bounce=0.8, wrap=0.45)
    A('hair', '#2a2230', n=7, gloss=40, spec=0.8, rim=0.9, ramp_kw=dict(l0=0.1, l1=0.62))
    A('cloth_blue', '#3b78c8', n=8, gloss=6, spec=0.1, rim=0.8, wrap=0.4, tex=0.05)
    A('cloth_white', '#f0f0f4', n=8, gloss=6, spec=0.1, rim=0.8, wrap=0.4, ramp_kw=dict(l0=0.45, cfloor_d=0.04))
    A('cloth_red', '#d8403c', n=8, gloss=6, spec=0.1, rim=0.8, wrap=0.4)
    A('cloth_dark', '#3a3f5a', n=8, gloss=6, spec=0.1, rim=0.8, wrap=0.4, ramp_kw=dict(l0=0.15))
    # wall paints
    for nm, hx in (('yellow', '#f0c466'), ('pink', '#e8a08c'), ('teal', '#74b8a0'), ('cream', '#efdcae'),
                   ('blue', '#7aa0c8'), ('orange', '#e89850'), ('white', '#e8e4dc'), ('green', '#8fc478'),
                   ('red', '#c8584c')):
        A('wall_' + nm, hx, n=8, gloss=6, spec=0.05, rim=0.4, wrap=0.35, tex=0.04, tex_sx=3, tex_sy=3,
          ramp_kw=dict(cfloor_d=0.03))
    A('roof_tile', '#c8553c', n=8, gloss=10, spec=0.2, rim=0.5, tex=0.12, tex_sx=3, tex_sy=1.2)
    A('roof_grey', '#8890a0', n=8, gloss=20, spec=0.4, rim=0.5, tex=0.06)
    A('sign_white', '#fbfaf2', n=7, gloss=40, spec=0.5, rim=0.3, amb=0.35, hi=0.95, wrap=0.4,
      ramp_kw=dict(l0=0.55))
    A('sign_yellow', '#ffd84a', n=7, gloss=40, spec=0.5, rim=0.3, amb=0.35, hi=0.95, wrap=0.4)
    A('sign_red', '#d3263a', n=8, gloss=40, spec=0.6, rim=0.5, wrap=0.4)
    A('sign_blue', '#1f58b8', n=8, gloss=40, spec=0.6, rim=0.5, wrap=0.4)
    A('sign_green', '#1c8e58', n=8, gloss=40, spec=0.6, rim=0.5, wrap=0.4)
    A('sky_cloud', '#f6f9ff', n=8, gloss=4, spec=0, rim=1.0, wrap=0.6, amb=0.3, ramp_kw=dict(l0=0.62, dk=0.9, cdark=2.0))
    A('water_tank', '#2a62c8', n=8, gloss=50, spec=0.9, refl=0.3, env='sky', rim=0.9)
    A('tank_steel', '#b8c0cc', n=8, gloss=45, spec=0.9, refl=0.4, env='chrome', rim=0.9)
    A('shutter', '#9aa4b2', n=8, gloss=20, spec=0.4, refl=0.1, rim=0.4, tex=0.12, tex_sx=20, tex_sy=1.0)
    A('interior', '#5a4a6a', n=7, gloss=8, spec=0.1, rim=0.0, ramp_kw=dict(l0=0.12, l1=0.7))
    A('light_warm', '#ffe488', n=7, gloss=50, spec=1.0, refl=0.2, rim=0.0, amb=0.5, hi=1.0)
    A('tail_red', '#d4162e', n=7, gloss=60, spec=1.0, refl=0.2, rim=0.0, amb=0.3, hi=0.8)
    A('paper_map', '#f4eedc', n=7, gloss=30, spec=0.4, rim=0.3, amb=0.3, hi=0.9, wrap=0.4)
    return L


def reduce_palette(img, n):
    """Median-cut quantise opaque pixels to n colours (no dither) -- optional last step."""
    a = np.array(img.convert('RGBA'))
    op = a[..., 3] > 0
    rgb = Image.fromarray(a[..., :3], 'RGB')
    q = rgb.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    qa = np.array(q)
    a[..., :3] = np.where(op[..., None], qa, 0)
    return Image.fromarray(a, 'RGBA')
