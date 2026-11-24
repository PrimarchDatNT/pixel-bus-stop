from common import *

# colour sets: (flash, hi, main, dim, dying)
SETS = {
    "red":   ("white", "salmon", "red_hot", "red_d", "bloom_k"),
    "gold":  ("white", "glow", "gold", "orange", "rust"),
    "cyan":  ("white", "cyan", "sky", "blue", "blue_d"),
    "pink":  ("white", "bloom_hl", "bloom_l", "bloom_d", "bloom_k"),
    "green": ("white", "glow", "green_l", "green", "green_d"),
}


def disc(img, cx, cy, r, col):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.6:
                put(img, x, y, col)


def peony(name, S=64, F=12, n=64, rmax=(23, 29), ring=False, tilt=1.0):
    flash, hi, main, dim, dying = SETS[name]
    rng = random.Random(hash(name) % 1000 + 7)
    cx = cy = S // 2
    parts = []
    for k in range(n):
        a = 2 * math.pi * k / n + rng.uniform(-0.05, 0.05)
        rin = rng.uniform(*rmax) if not ring else 25
        parts.append((a, rin, rng.uniform(8, 11) if True else 0, rng.random()))
    # a second, smaller inner shell for depth
    if not ring:
        for k in range(26):
            a = 2 * math.pi * (k + 0.5) / 26
            parts.append((a, rng.uniform(12, 18), 8, rng.random()))
    kk = 0.46
    frames = []
    for f in range(F):
        img = new(S, S)
        # flash core
        if f == 0:
            disc(img, cx, cy, 2, "white")
        elif f == 1:
            disc(img, cx, cy, 4, flash); disc(img, cx, cy, 2, "white")
            for d in (5, 6):
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    put(img, cx + dx * d, cy + dy * d, hi)
        elif f == 2:
            disc(img, cx, cy, 2, flash)
        for (a, rin, _, rr) in parts:
            t = f - 1
            if t < 0:
                continue
            frac = 1 - math.exp(-kk * t)
            r = rin * frac
            gy = 0.075 * t * t * (0.7 + 0.6 * rr)           # gravity droop
            def pos(tt):
                fr = 1 - math.exp(-kk * max(tt, 0))
                x = cx + rin * fr * math.cos(a)
                y = cy + (rin * fr * math.sin(a)) * tilt + 0.075 * max(tt, 0) ** 2 * (0.7 + 0.6 * rr)
                return int(round(x)), int(round(y))
            # stage colours
            if f <= 4:
                head, mid, tail = hi, main, dim
            elif f <= 8:
                head, mid, tail = main, main, dim
            elif f <= 9:
                head, mid, tail = dim, dim, dying
            else:
                head, mid, tail = dying, dying, dying
            # twinkle out
            if f >= 9 and ((int(rr * 97) + f * 5) % 3 == 0):
                continue
            if f >= 10 and rr < 0.35 + (f - 10) * 0.3:
                continue
            x, y = pos(t)
            put(img, x, y, head)
            if f <= 7:
                put(img, x + 1, y, head); put(img, x, y + 1, head)
                if f <= 5:
                    put(img, x - 1, y, mid); put(img, x, y - 1, mid)
            # trails (short while expanding, shorter as it dims)
            tl = 4 if f <= 6 else 3
            for j in range(1, tl + 1):
                x2, y2 = pos(t - 0.42 * j)
                put(img, x2, y2, mid if j == 1 else tail)
        frames.append(img)
    return frames


def willow(name="gold", S=(72, 80), F=16, n=48):
    W_, H_ = S
    cx, cy = W_ // 2, 16
    rng = random.Random(21)
    parts = []
    for k in range(n):
        a = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / n
        sp = rng.uniform(4.6, 7.2)
        parts.append((a, sp, rng.randint(0, 2)))
    cols = ["white", "glow", "yellow", "gold", "gold", "orange", "orange", "rust", "rust", "brown_d"]
    frames = []
    # simulate once and keep history
    hist = []
    for a, sp, delay in parts:
        x, y = float(cx), float(cy)
        vx, vy = sp * math.cos(a), sp * math.sin(a) * 0.9
        pts = []
        for f in range(F):
            pts.append((x, y))
            x += vx; y += vy
            vx *= 0.82; vy = vy * 0.82 + 0.5
        hist.append(pts)
    for f in range(F):
        img = new(W_, H_)
        if f <= 1:
            disc(img, cx, cy, 3 - f, "white")
        for pi, pts in enumerate(hist):
            life = F - 1 - (pi % 4)                   # staggered fade-out
            if f > life:
                continue
            for j in range(0, 11):
                ff = f - j
                if ff < 1:
                    break
                x, y = pts[ff]
                age = j + max(0, f - 5) * 0.55            # colours age with time
                col = cols[min(len(cols) - 1, int(age))]
                if f > 10 and (pi + j + f) % 3 == 0:
                    continue                              # twinkle-out gaps
                put(img, int(round(x)), int(round(y)), col)
                if j == 0 and f < 9:
                    put(img, int(round(x)) + 1, int(round(y)), col)
        frames.append(img)
    return frames


def crackle(S=40, F=6):
    rng = random.Random(33)
    pts = [(rng.randint(-17, 17), rng.randint(-17, 17)) for _ in range(26)]
    pts = [(x, y) for x, y in pts if x * x + y * y <= 18 * 18]
    cx = cy = S // 2
    frames = []
    for f in range(F):
        img = new(S, S)
        for k, (dx, dy) in enumerate(pts):
            ph = (k * 3 + f * 2) % 6
            x, y = cx + dx, cy + dy + f // 2
            if ph == 0:
                put(img, x, y, "white")
                for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    put(img, x + ax, y + ay, "yellow")
            elif ph == 1:
                put(img, x, y, "gold")
            elif ph == 2:
                put(img, x, y, "white")
            elif ph == 3 and k % 2:
                put(img, x, y, "orange")
        # sparse bright core flash on the first frame
        if f == 0:
            disc(img, cx, cy, 2, "white")
        frames.append(img)
    return frames


def rocket():
    frames = []
    for f in range(4):
        img = new(3, 12)
        put(img, 1, 0, "white")
        put(img, 0, 1, "yellow") if f % 2 == 0 else None
        put(img, 2, 1, "yellow") if f % 2 else None
        put(img, 1, 1, "yellow")
        tl = [8, 10, 9, 11][f]
        for j in range(2, tl):
            col = "orange" if j < 4 else ("red" if j < 6 else ("red_d" if j < 8 else "brown_d"))
            if j >= 6 and (j + f) % 2:
                continue
            put(img, 1, j, col)
        frames.append(img)
    return frames


if __name__ == "__main__":
    save_asset(G, "fw_rocket", rocket(), fps=12, anchor=(1, 0), loop=False,
               notes="Rising rocket head + fading trail, 4 frames, play looped while moving up; anchor = head (tip). Dong Giao thua.")
    for nm in SETS:
        save_asset(G, f"fw_peony_{nm}", peony(nm), fps=12, anchor=(32, 32), loop=False,
                   notes=f"Spherical burst {nm}, 64x64, 12 frames @12fps (flash, expand, droop, twinkle out), plays once; anchor = burst centre. No glow baked (compositor blooms). Dong night.")
    save_asset(G, "fw_ring_gold", peony("gold", S=56, F=10, n=40, ring=True, tilt=0.82), fps=12, anchor=(28, 28), loop=False,
               notes="Ring burst gold, 56x56, 10 frames, plays once; anchor = centre (ring slightly tilted).")
    save_asset(G, "fw_willow_gold", willow(), fps=12, anchor=(36, 16), loop=False,
               notes="Willow (drooping trails) gold, 72x80, 16 frames, plays once; anchor = burst centre (36,16).")
    save_asset(G, "fw_crackle", crackle(), fps=12, anchor=(20, 20), loop=False,
               notes="Glitter/crackle twinkles 40x40, 6 frames, plays once; anchor = centre.")
