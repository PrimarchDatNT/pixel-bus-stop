"""Procedural weather / light effects for the v4 GIF-style loop (384x216 logical canvas, RGBA, opaque).

All effects are deterministic in t, quantised to FPS frames, and pixel-identical at t and t+loop.
Static per-particle parameters come from random.Random(seed) and are cached; nothing random per frame.

    from compose.fx_gif import glow, rain, fog, fireworks, stars
"""
from __future__ import annotations

import math
import random
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.px_gif import RGB  # noqa: E402
from tools.layout_gif import *  # noqa: E402,F403

FPS = 12
CW, CH = W, H


# ----------------------------------------------------------------------------------------------- helpers
def _frame(t: float, loop: float) -> tuple[int, int]:
    """-> (frame index inside the loop, frames per loop)."""
    lf = int(round(loop * FPS))
    return int(round(t * FPS)) % lf, lf


def _get(cv):
    return np.array(cv.convert("RGBA"), dtype=np.uint8)


def _put(cv, a):
    cv.paste(Image.fromarray(a, "RGBA"))


def _blend(a, xs, ys, cols, alpha):
    """Flat blend of colour(s) over pixels (clipped); writes opaque result."""
    xs = np.asarray(xs, dtype=np.int64); ys = np.asarray(ys, dtype=np.int64)
    if xs.size == 0:
        return
    ok = (xs >= 0) & (xs < CW) & (ys >= 0) & (ys < CH)
    if not ok.all():
        xs, ys = xs[ok], ys[ok]
        if np.ndim(cols) == 2: cols = np.asarray(cols)[ok]
        if np.ndim(alpha) == 1: alpha = np.asarray(alpha)[ok]
    if xs.size == 0:
        return
    al = np.asarray(alpha, dtype=np.float64)
    if al.ndim == 1: al = al[:, None]
    p = a[ys, xs, :3].astype(np.float64)
    out = p + (np.asarray(cols, dtype=np.float64) - p) * al
    a[ys, xs, :3] = np.rint(out).astype(np.uint8)
    a[ys, xs, 3] = 255


def _keep(xs, ys, exclude):
    m = np.ones(xs.shape, bool)
    for x0, y0, x1, y1 in exclude:
        m &= ~((xs >= x0) & (xs <= x1) & (ys >= y0) & (ys <= y1))
    return m


# ----------------------------------------------------------------------------------------------- 1. glow
def glow(cv, cx, cy, rx, ry, color, k=0.35, steps=3):
    """Light pool: `steps` concentric flat ellipses (outer rx,ry), screen-blended toward `color`; inner is strongest."""
    a = _get(cv)
    x0, x1 = max(0, int(cx - rx) - 1), min(CW, int(cx + rx) + 2)
    y0, y1 = max(0, int(cy - ry) - 1), min(CH, int(cy + ry) + 2)
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = ((xx - cx) / max(rx, 0.5)) ** 2 + ((yy - cy) / max(ry, 0.5)) ** 2
    s = np.zeros(d.shape)
    for j in range(steps):
        s[d <= ((steps - j) / steps) ** 2] = k * (j + 1) / steps
    sub = a[y0:y1, x0:x1, :3].astype(np.float64)
    c = np.asarray(color, dtype=np.float64)
    out = sub + s[..., None] * c * (255 - sub) / 255.0
    m = s > 0
    sub2 = a[y0:y1, x0:x1]
    sub2[m, :3] = np.rint(out[m]).astype(np.uint8)
    _put(cv, a)


# ----------------------------------------------------------------------------------------------- 2. rain
@lru_cache(maxsize=16)
def _rain_params(nfar, nnear, nspl, drizzle, lf, splash_y):
    r = random.Random(11 if not drizzle else 12)
    def layer(n, ns, lens):
        return (np.array([r.randrange(CW) for _ in range(n)]), np.array([r.randrange(CH + 16) for _ in range(n)]),
                np.array([r.choice(ns) for _ in range(n)]), np.array([r.choice(lens) for _ in range(n)]))
    far = layer(nfar, (6, 7) if drizzle else (9, 10), (2,) if drizzle else (2, 3))
    near = layer(nnear, (14, 15, 16), (3, 4, 5))
    divs = [d for d in range(10, 25) if lf % d == 0] or [lf]
    sp = []
    for _ in range(nspl):
        P = r.choice(divs)
        cyc = lf // P
        sp.append((P, r.randrange(P), [r.randrange(CW) for _ in range(cyc)],
                   [r.randint(splash_y[0], splash_y[1]) for _ in range(cyc)]))
    return far, near, sp


def _streaks(a, layer, f, lf, wind, exclude, cols, alpha):
    x0, y0, n, L = layer
    span = CH + 16
    yh = (y0 + (n * span * f) // lf) % span - 8
    kmax = int(L.max())
    k = np.arange(kmax)[None, :]
    rows = yh[:, None] - k
    ok = (k < L[:, None]) & (rows >= 0) & (rows < CH)
    xs = (x0[:, None] + wind * (rows // 3)) % CW
    kk = np.broadcast_to(k, rows.shape)
    xs, ys, kk = xs[ok], rows[ok], kk[ok]
    m = _keep(xs, ys, exclude)
    xs, ys, kk = xs[m], ys[m], kk[m]
    _blend(a, xs, ys, np.where((kk == 0)[:, None], cols[0], cols[1]), alpha)


def rain(cv, t, loop=24.0, density=1.0, wind=1, exclude=(), splash_y=(188, 214), drizzle=False):
    f, lf = _frame(t, loop)
    a = _get(cv)
    if drizzle:
        nfar, nnear, nspl = int(70 * density), 0, 0
    else:
        nfar, nnear, nspl = int(150 * density), int(100 * density), int(34 * density)
    far, near, sp = _rain_params(nfar, nnear, nspl, drizzle, lf, tuple(splash_y))
    gl = np.array(RGB["glass_l"])
    if drizzle:
        _streaks(a, far, f, lf, wind, exclude, (gl, gl), 0.3)
    else:
        _streaks(a, far, f, lf, wind, exclude, (gl, gl), 0.5)
        _streaks(a, near, f, lf, wind, exclude, (np.array(RGB["white"]), np.array(RGB["cloud_s"])), 0.7)
        px, py, pc = [], [], []
        for P, ph, xt, yt in sp:
            loc = (f - ph) % P
            if loc > 2: continue
            c = ((f - ph) % lf) // P
            x, y = xt[c], yt[c]
            pts = [(0, 0)] if loc == 0 else [(-1, 0), (0, 0), (1, 0)] if loc == 1 else [(-2, -1), (2, -1)]
            for dx, dy in pts:
                px.append(x + dx); py.append(y + dy)
        if px:
            px = np.array(px); py = np.array(py)
            m = _keep(px, py, exclude)
            _blend(a, px[m], py[m], np.array(RGB["white"]), 0.7)
    _put(cv, a)


# ----------------------------------------------------------------------------------------------- 3. fog
def _default_bands():
    return [(175, 9, 0.30, 1), (141, 5, 0.22, -1), (62, 22, 0.09, 1)]


def fog(cv, t, loop=24.0, bands=None, color=None):
    f, lf = _frame(t, loop)
    bands = bands or _default_bands()
    col = np.array(color if color is not None else RGB["ov_d"], dtype=np.float64)
    a = _get(cv)
    xs = np.arange(CW)
    for bi, (yc, hh, al, nw) in enumerate(bands):
        drift = (nw * CW * f) // lf
        u = ((xs - drift) % CW) * (2 * math.pi / CW)
        ph = bi * 1.7
        top = np.rint(2.2 * np.sin(2 * u + ph) + 1.3 * np.sin(5 * u + 2 * ph + 0.5)).astype(int)
        bot = np.rint(2.0 * np.sin(3 * u + ph + 1.0) + 1.2 * np.sin(4 * u + 3 * ph)).astype(int)
        lo = (yc - hh + top)[None, :]
        hi = (yc + hh + bot)[None, :]
        y0 = max(0, int(yc - hh - 8)); y1 = min(CH, int(yc + hh + 8))
        yy = np.arange(y0, y1)[:, None]
        d = np.maximum(lo - yy, yy - hi)
        amap = np.where(d <= 0, al, np.where(d <= 2, al / 2, 0.0))
        m = amap > 0
        sub = a[y0:y1, :, :3]
        p = sub.astype(np.float64)
        out = p + (col - p) * amap[..., None]
        sub[m] = np.rint(out[m]).astype(np.uint8)
    _put(cv, a)


# ----------------------------------------------------------------------------------------------- 4. fireworks
_RAMPS = {  # white, light, base, dark
    "red": ("white", "red_l", "red", "red_d"), "yl": ("white", "yl_l", "yl", "or"),
    "pk": ("white", "pk_l", "pk", "pk_d"), "glass": ("white", "glass_l", "glass", "pb_l"),
    "gold": ("white", "gold", "or_l", "or_d"), "crack": ("white", "yl_l", "white", "yl"),
}


@lru_cache(maxsize=8)
def _fw_schedule(seed, lf, loop, region):
    r = random.Random(seed)
    rx0, ry0, rx1, ry1 = region
    kinds = [("peony", "red"), ("willow", "gold"), ("peony", "yl"), ("crackle", "crack"), ("peony", "pk"),
             ("willow", "gold"), ("peony", "glass"), ("peony", "red"), ("peony", "yl"), ("far", "yl"),
             ("far", "glass"), ("far", "pk")]
    while True:
        r.shuffle(kinds)
        # never put two far ones back to back (keep a near burst on screen most of the time)
        if all(not (kinds[i][0] == "far" and kinds[(i + 1) % len(kinds)][0] == "far") for i in range(len(kinds))):
            break
    n = len(kinds)
    xlo = max(rx0, 300)
    out = []
    for i, (kind, ramp) in enumerate(kinds):
        start = int(round(((i + 0.5) * loop / n + r.uniform(-0.3, 0.3)) * FPS)) % lf
        far = kind == "far"
        rise = r.uniform(0.6, 1.0)
        dur = r.uniform(1.6, 2.4)
        bx = r.randint(xlo + (6 if far else 12), rx1 - (6 if far else 14))
        by = r.randint(100, 135) if far else r.randint(max(ry0 + 34, 44), min(ry1 - 24, 86))
        if far:
            npart = r.randint(22, 28); R = r.uniform(11, 13); g = 3.0; K, dl = 2, 0.03; shells = (0.6, 1.0)
        elif kind == "willow":
            npart = r.randint(44, 54); R = r.uniform(26, 32); g = 11.0; K, dl = 5, 0.07; shells = (0.7, 1.0)
        elif kind == "crackle":
            npart = 20; R = r.uniform(12, 16); g = 0.0; K, dl = 0, 0.0; shells = (0.6, 1.0)
        else:
            npart = r.randint(36, 56); R = r.uniform(24, 34); g = 6.0; K, dl = 3, 0.03; shells = (0.45, 0.72, 1.0)
        sh = np.array([shells[j % len(shells)] for j in range(npart)])
        S_ = len(shells); cnt = -(-npart // S_)
        th = np.array([2 * math.pi * ((j // S_) + 0.5 * (j % S_) / S_) / cnt + (j % S_) * 0.7 + r.uniform(-0.07, 0.07)
                       for j in range(npart)])
        rr = np.array([R * sh[j] * r.uniform(0.94, 1.0) for j in range(npart)])
        life = np.array([r.uniform(0.85, 1.0) for _ in range(npart)])
        out.append(dict(kind="peony" if far else kind, ramp=ramp, start=start, rise=rise, dur=dur, bx=bx, by=by,
                        g=g, K=K, dl=dl, th=th, R=rr, life=life, far=far, wob=r.choice((-1, 1)),
                        sy=150 if not far else 152))
    return out


def fireworks(cv, t, loop=24.0, region=(250, 18, 380, 120), seed=3):
    f, lf = _frame(t, loop)
    a = _get(cv)
    sched = _fw_schedule(seed, lf, float(loop), tuple(region))
    flash, fcol = 0.0, RGB["moon"]
    X, Y, C, A, P = [], [], [], [], []

    def add(x, y, c, al, pr):
        n_ = np.size(x)
        X.append(np.atleast_1d(x)); Y.append(np.atleast_1d(y)); C.append(np.broadcast_to(c, (n_, 3)))
        A.append(np.broadcast_to(al, (n_,))); P.append(np.full(n_, pr))

    for b in sched:
        dt = ((f - b["start"]) % lf) / FPS
        if dt > b["rise"] + b["dur"]:
            continue
        ramp = [np.array(RGB[n_]) for n_ in _RAMPS[b["ramp"]]]
        white, yll = np.array(RGB["white"]), np.array(RGB["yl_l"])
        if dt < b["rise"]:
            u = dt / b["rise"]
            y = int(round(b["sy"] - (b["sy"] - b["by"]) * (1 - (1 - u) ** 2)))
            x = b["bx"] + (b["wob"] if (int(dt * FPS) // 3) % 2 else 0)
            add(x, y, white, 1.0, 11)
            for j, al in enumerate((0.85, 0.6, 0.4, 0.25)):
                add(x, y + 1 + j, yll if j < 2 else np.array(RGB["or"]), al, 10 - j)
            continue
        db = dt - b["rise"]
        fl = (1.0 - db / 0.4) * (0.6 if b["far"] else 1.0)
        if fl > flash: flash, fcol = fl, tuple(int(v) for v in ramp[1])
        fi = int(round(db * FPS))
        if fi < 2:   # bright core: diamond, white then yl_l
            rad = 1 if b["far"] else (2 if fi == 0 else 1)
            ox, oy = np.meshgrid(np.arange(-rad, rad + 1), np.arange(-rad, rad + 1))
            m = (abs(ox) + abs(oy)) <= rad
            if not b["far"] and fi == 0: m = m | (abs(ox) + abs(oy) <= 3) & ((ox == 0) | (oy == 0))
            add(b["bx"] + ox[m], b["by"] + oy[m], white if fi == 0 else yll, 1.0, 12)
        n = len(b["th"]); pid = np.arange(n)
        crack = b["kind"] == "crackle"
        for k in range(b["K"] + 1):
            radial = b["kind"] == "peony"
            tk = db if radial else db - k * b["dl"]
            if tk < 0: continue
            lam = tk / (b["dur"] * b["life"])
            tau = np.minimum(tk / (b["dur"] * (0.3 if crack else 0.5)), 1.0)
            e = 1 - (1 - tau) ** 2.4
            rad = b["R"] * e
            if radial: rad = np.maximum(rad - k * (1.0 if b["far"] else 1.4), 0)   # spatial trail along the radial motion
            x = b["bx"] + rad * np.cos(b["th"])
            y = b["by"] + rad * np.sin(b["th"]) + b["g"] * tk * tk
            vis = lam < 1.0
            xi, yi = np.rint(x).astype(int), np.rint(y).astype(int)
            if crack:
                vis &= (lam > 0.04) & (((f + pid) % 2) == 0)
                col = np.where((pid % 2 == 0)[:, None], ramp[0], ramp[1])
            else:
                stage = np.digitize(lam, [0.1, 0.45, 0.8])
                spark = lam >= 0.9
                vis &= ~spark | (((f + pid) % 2) == 0)
                stage = np.where(spark, 2, stage)
                if k > 0: stage = np.minimum(stage + 1, 3)       # trail: one tone darker than the head
                col = np.stack(ramp)[stage]
            al = 1.0 if k < 3 else 0.7
            add(xi[vis], yi[vis], col[vis], al, 5 - k if k else 9)
            if k == 0 and not crack and not b["far"]:      # chunky head: second pixel while still bright
                c1 = vis & (lam < 0.8)
                add(xi[c1] + 1, yi[c1], col[c1], 1.0, 8)
                c2 = vis & (lam < 0.45)
                add(xi[c2], yi[c2] + 1, col[c2], 1.0, 8); add(xi[c2] + 1, yi[c2] + 1, col[c2], 1.0, 8)
    if X:
        xs = np.concatenate(X); ys = np.concatenate(Y); cs = np.concatenate(C).reshape(-1, 3)
        al = np.concatenate(A); pr = np.concatenate(P)
        o = np.argsort(pr, kind="stable")
        _blend(a, xs[o], ys[o], cs[o], al[o])
    _put(cv, a)
    return max(0.0, min(1.0, flash)), fcol


# ----------------------------------------------------------------------------------------------- 5. stars
@lru_cache(maxsize=8)
def _star_params(region, n, seed):
    r = random.Random(seed)
    x0, y0, x1, y1 = region
    out = []
    for _ in range(n):
        out.append((r.randrange(x0, x1), r.randrange(y0, y1), r.random() < 0.3 and "glass_l" or "moon",
                    r.choice((0, 0, 0, 6, 8, 12, 24)) if r.random() < 0.35 else 0, r.randrange(24), r.choice((0, 1))))
    return out


def stars(cv, t, loop=24.0, region=(0, 0, 384, 70), n=40, seed=5, sky_colors=None):
    f, lf = _frame(t, loop)
    a = _get(cv)
    allowed = None if sky_colors is None else {tuple(c) for c in sky_colors}
    for x, y, cn, per, ph, mode in _star_params(tuple(region), n, seed):
        cur = tuple(int(v) for v in a[y, x, :3])
        if allowed is not None and cur not in allowed:
            continue
        col = np.array(RGB[cn])
        if per:
            frac = ((f * per + ph * lf // 24) % lf) / lf
            if frac >= 0.5:
                if mode == 0: continue                      # on / off
                _blend(a, [x], [y], col, 0.4); continue     # dim
        _blend(a, [x], [y], col, 1.0)
    _put(cv, a)


# ----------------------------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    SCR = Path("review/gif_style/_sheets")
    SCR.mkdir(parents=True, exist_ok=True)

    def bg(name):
        return Image.new("RGBA", (CW, CH), RGB[name] + (255,))

    EX = [(36, 155, 176, 199)]
    tests = {
        "glow": (lambda cv, t: glow(cv, 100, 100, 30, 18, RGB["lamp"]), "nt"),
        "rain": (lambda cv, t: rain(cv, t, exclude=EX), "ov_d"),
        "drizzle": (lambda cv, t: rain(cv, t, drizzle=True), "ov_d"),
        "fog": (lambda cv, t: fog(cv, t), "nt_d"),
        "fireworks": (lambda cv, t: fireworks(cv, t, region=(262, 10, 380, 112)), "nt_d"),
        "stars": (lambda cv, t: stars(cv, t, sky_colors={RGB["nt_d"]}), "nt_d"),
    }
    for name, (fn, b) in tests.items():
        for t0 in (0.0, 3.5, 11.25, 20.0):
            c1, c2 = bg(b), bg(b)
            r1 = fn(c1, t0); r2 = fn(c2, t0 + 24.0)
            assert c1.tobytes() == c2.tobytes() and r1 == r2, (name, t0)
        c = bg(b); ts = []
        for t0 in np.linspace(0, 23, 24):
            c = bg(b); s = time.perf_counter(); fn(c, float(t0)); ts.append((time.perf_counter() - s) * 1000)
        print(f"{name:10s} loop OK  mean {np.mean(ts):5.1f} ms  max {max(ts):5.1f} ms")

    # preview sheet
    tiles = []
    c = bg("ov_d"); rain(c, 5.0, exclude=EX)
    from PIL import ImageDraw
    ImageDraw.Draw(c).rectangle(EX[0], outline=RGB["grey_k"]); tiles.append(c)
    c = bg("nt_d"); fog(c, 7.0); tiles.append(c)
    sched = _fw_schedule(3, 288, 24.0, (262, 10, 380, 112))
    ev = sorted(sched, key=lambda b: b["start"])
    for b, off in zip((ev[1], ev[2], ev[4], ev[5]), (0.35, 0.6, 0.9, 1.2)):
        c = bg("nt_d"); stars(c, 0, sky_colors={RGB["nt_d"]})
        tt = b["start"] / FPS + b["rise"] + off
        fl = fireworks(c, tt, region=(262, 10, 380, 112)); tiles.append(c); print("fw t=%.2f %s %s" % (tt, b["kind"], fl))
    c = bg("nt")
    glow(c, 80, 100, 40, 24, RGB["lamp"]); glow(c, 200, 100, 24, 14, RGB["glow"], k=0.5); glow(c, 300, 100, 14, 14, RGB["red_l"], k=0.45)
    tiles.append(c)
    REG = (262, 10, 380, 112)
    fp = ROOT / "review/gif_style/dong/frame.png"
    if fp.exists():
        real = Image.open(fp).convert("RGBA")
        if real.size != (CW, CH): real = real.resize((CW, CH), Image.NEAREST)
        sch = _fw_schedule(3, 288, 24.0, REG)
        cand = sorted(sch, key=lambda b: b["start"])
        b = [x for x in cand if not x["far"] and x["kind"] == "peony"][0]
        tt = b["start"] / FPS + b["rise"] + 0.6
        fireworks(real, tt, region=REG); tiles.append(real)
        # onscreen coverage stat
        act = [(sum(1 for q in sch if 0 <= ((int(round(x * 12)) - q["start"]) % 288) / 12 <= q["rise"] + q["dur"])) for x in np.arange(0, 24, 0.25)]
        print("bursts on screen: min %d mean %.1f" % (min(act), sum(act) / len(act)))
    S = 3; cols = 2; rows = (len(tiles) + 1) // 2
    sheet = Image.new("RGBA", (cols * CW * S + (cols + 1) * 6, rows * CH * S + (rows + 1) * 6), (0, 0, 0, 255))
    for i, tl in enumerate(tiles):
        sheet.paste(tl.resize((CW * S, CH * S), Image.NEAREST), (6 + (i % cols) * (CW * S + 6), 6 + (i // cols) * (CH * S + 6)))
    sheet.save(SCR / "fx_sheet.png")
    print("saved", SCR / "fx_sheet.png")
