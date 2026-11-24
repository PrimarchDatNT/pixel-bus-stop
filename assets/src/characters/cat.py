from catlib import *
from walkers import SCR
import sys

def paw(img, x, y, side):
    pc = "white" if side == "near" else "grey_l"
    sh = "grey_l" if side == "near" else "grey"
    x = R(x); y = R(y)
    for dx in range(-1, 3): put(img, x + dx, y, pc)
    for dx in range(-1, 2): put(img, x + dx, y - 1, pc)
    for dx in range(-1, 1): put(img, x + dx, y - 2, pc)
    put(img, x - 1, y, sh) if side == "near" else None

def leg_hind(img, hip, pawp, side, lift=0):
    px_, py_ = pawp
    hock = (px_ - 2, py_ - 5)
    knee, end = ik(hip, hock, 6.0, 6.0, 1)
    c0 = "orange" if side == "near" else "clay"
    limb(img, hip, knee, c0, t=4)
    limb(img, knee, hock, c0, t=2)
    limb(img, hock, (px_ - 1, py_ - 2), c0, t=2)
    paw(img, px_, py_, side)

def leg_front(img, sh, pawp, side):
    px_, py_ = pawp
    wrist = (px_ - 1, py_ - 3)
    elbow, end = ik(sh, wrist, 5.5, 5.0, -1)
    c0 = "orange" if side == "near" else "clay"
    limb(img, sh, elbow, c0, t=3)
    limb(img, elbow, wrist, c0, t=2)
    paw(img, px_, py_, side)

WALK_TORSO = [(12, 11.5), (16, 9), (22, 8.5), (28, 9), (32, 10), (35.5, 12.5), (36.5, 16), (34, 19), (28, 20), (21, 19.5), (15, 18.5), (12, 17), (11, 14)]

def shift(pts, dx=0, dy=0):
    return [(x + dx, y + dy) for x, y in pts]

def foot(f, off, hipx, A=4):
    j = (f - off) % 8
    if j <= 4:
        return hipx + 4 - 2 * j, 0
    return hipx - 4 + 2 * (j - 4), [0, 0, 0, 0, 0, 2, 3, 2][j]

def walk_frame(f):
    img = new(CW, CH)
    bob = [0, 0, -1, -1, 0, 0, -1, -1][f] * 0 + [0, -1, 0, -1, 0, -1, 0, -1][f] * 0
    bob = [0, 0, -1, -1, 0, 0, -1, -1][f]
    # tail behind
    ph = 2 * math.pi * f / 8
    sw = math.sin(ph)
    tail = [(11, 13 + bob), (7, 11 + bob), (4, 8 + bob), (4 + 1.5 * sw, 4), (7 + 2.5 * sw, 2.5 + 0.5 * sw), (10 + 2.5 * sw, 4)]
    draw_tail(img, tail, width=2, ring=3)
    # far legs
    for kind, off, hip0, paw0 in (("hind", 4, 14, 14), ("front", 6, 33, 33)):
        dx, lift = foot(f, off, 0)
        paw = (paw0 + dx, FEET - lift)
        if kind == "hind":
            leg_hind(img, (14, 15 + bob), paw, "far")
        else:
            leg_front(img, (33, 15 + bob), paw, "far")
    stripes = [14, 19, 24, 29]
    draw_torso(img, shift(WALK_TORSO, 0, bob), stripes_x=[s for s in stripes], belly_white=(32, 15 + bob, 37, 20 + bob), stripe_len=5)
    for kind, off, hip0, paw0 in (("hind", 0, 14, 14), ("front", 2, 33, 33)):
        dx, lift = foot(f, off, 0)
        paw = (paw0 + dx, FEET - lift)
        if kind == "hind":
            leg_hind(img, (14, 15 + bob), paw, "near")
        else:
            leg_front(img, (33, 15 + bob), paw, "near")
    hd = hgrid(HEAD_SIDE)
    CTX['head'] = (33, 5 + bob, hd.width)
    paste(img, hd, 33, 5 + bob)
    img.ctx = dict(CTX)
    return img


SIT_TORSO = [(12, 23), (15, 19), (21, 16), (27, 12), (31, 9), (35, 9), (36, 14), (35, 22), (33, 28.5), (27, 29), (18, 29), (11, 28.5), (9, 26)]
LOAF_TORSO = [(10, 22), (13, 19), (19, 17), (26, 16.5), (31, 17), (36, 19), (40, 23), (41, 27), (37, 29), (30, 29), (20, 29), (11, 28.5), (8, 25.5)]

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_pts(A, B, t):
    return [(lerp(p[0], q[0], t), lerp(p[1], q[1], t)) for p, q in zip(A, B)]

SIT_TAIL = [(11, 26), (6, 28), (3, 26), (3, 21), (5, 17), (8, 15)]
WALK_TAIL = [(11, 13), (7, 11), (4, 8), (4, 4), (7, 2.5), (10, 4)]

def tail_swish(f, n=4):
    t = SIT_TAIL
    dx = [0, 1, 2, 1][f % 4]; dy = [0, 0, 1, 0][f % 4]
    return t[:3] + [(t[3][0] + dx * 0.3, t[3][1]), (t[4][0] + dx * 0.8, t[4][1] + dy), (t[5][0] + dx * 1.5, t[5][1] + dy * 2)]

def sit_legs(img, near_up=False, hind_shift=0, ground=0):
    # far front leg, hind thigh + paw, near front leg
    # far front
    rect(img, 29, 20 + ground, 31, 28, "clay"); rect(img, 29, 26, 31, 29, "grey_l")
    put(img, 28, 29, "grey_l"); put(img, 32, 29, "grey_l")

def sit_hind(img, ground=0):
    # thigh arc + forward hind paw
    for (x, y) in [(20, 18), (22, 19), (23, 21), (24, 23), (23, 25), (21, 27)]:
        put(img, x, y + ground, "clay")
    for (x, y) in [(18, 19), (20, 20), (21, 22), (21, 24)]:
        put(img, x, y + ground, "gold")
    for x in range(23, 31): put(img, x, 28, "white")
    for x in range(24, 32): put(img, x, 29, "white")
    put(img, 22, 29, "grey_l"); put(img, 23, 29, "grey_l"); put(img, 31, 28, "grey_l")
    put(img, 28, 29, "grey_l")

def sit_front_near(img):
    rect(img, 32, 19, 34, 24, "orange")
    for y in range(20, 29): put(img, 31, y, "clay")
    rect(img, 34, 19, 34, 24, "clay")
    rect(img, 32, 25, 34, 29, "white"); put(img, 35, 29, "white"); put(img, 31, 29, "white")
    for y in range(25, 29): put(img, 34, y, "grey_l")
    put(img, 33, 29, "grey_l")

def haunch_ring(img, cx, cy, rx, ry):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            v = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if 0.62 < v <= 1.0 and (x - cx) + (y - cy) * 0.3 > -2 and img.getpixel((x, y))[3]:
                put(img, x, y, "clay")
            elif v <= 0.62 and (x - cx) < -2 and (y - cy) < -1 and (x - cx) ** 2 + (y - cy) ** 2 > 14 and img.getpixel((x, y))[3] and v > 0.35:
                put(img, x, y, "gold")

def sit_frame(head="side", head_pos=(32, 1), tail=None, torso=None, lick=None, tongue=False, stripes=(15, 19, 23, 27), t_to_loaf=0.0, ear_twitch=0):
    img = new(CW, CH)
    tail = tail or SIT_TAIL
    draw_tail(img, tail, width=2, ring=3)
    sit_legs(img)
    tor = torso or SIT_TORSO
    draw_torso(img, tor, stripes_x=list(stripes), belly_white=(32, 11, 37, 20), stripe_len=5, light_to=0.8)
    sit_hind(img)
    haunch_ring(img, 17, 23.5, 8, 6.5)
    if lick is None:
        sit_front_near(img)
    else:
        rect(img, 32, 22, 34, 24, "orange"); rect(img, 32, 25, 34, 29, "white")
        for y in range(23, 29): put(img, 31, y, "clay")
    g = {"side": HEAD_SIDE, "blink": HEAD_SIDE_BLINK, "front": HEAD_FRONT, "front_blink": HEAD_FRONT_BLINK, "front_half": HEAD_FRONT_HALF}[head]
    hd = hgrid(g)
    CTX['head'] = (head_pos[0], head_pos[1], hd.width)
    paste(img, hd, head_pos[0], head_pos[1])
    if lick is not None:
        paw_t = lick
        el, end = ik((33, 17), paw_t, 6.5, 6.5, 1)
        limb(img, (33, 17), el, "rust", t=3, ox=0)
        limb(img, el, paw_t, "rust", t=3, ox=0)
        limb(img, (33, 16), (el[0], el[1] - 1), "orange", t=3)
        limb(img, (el[0], el[1] - 1), (paw_t[0], paw_t[1] - 1), "orange", t=3)
        px_, py_ = paw_t
        for dx in range(-2, 4):
            for dy in range(-2, 3):
                put(img, px_ + dx, py_ + dy, "brown_k")
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                put(img, px_ + dx, py_ + dy, "white")
        put(img, px_, py_ + 1, "salmon")
        put(img, px_ + 2, py_, "white"); put(img, px_ + 2, py_ - 1, "white")
        put(img, px_ + 1, py_ + 1, "grey_l"); put(img, px_ - 1, py_ + 1, "grey_l")
    if tongue:
        put(img, head_pos[0] + 12, head_pos[1] + 10, "salmon"); put(img, head_pos[0] + 12, head_pos[1] + 11, "salmon")
    img.ctx = dict(CTX)
    return img

def with_paw_after(img, paw_t):
    pass

def sheet(frames, path, k=6, cols=None):
    w, h = frames[0].size
    cols = cols or len(frames)
    rows = (len(frames) + cols - 1) // cols
    im = Image.new("RGBA", (w * cols * k, h * rows * k), (*RGB["sky"], 255))
    for i, f in enumerate(frames):
        im.alpha_composite(f.resize((w * k, h * k), Image.NEAREST), ((i % cols) * w * k, (i // cols) * h * k))
    im.convert("RGB").save(path)


HEAD_SIDE_TWITCH = list(HEAD_SIDE_BLINK)
HEAD_SIDE_TWITCH[0] = "..RR.........";
HEAD_SIDE_TWITCH[1] = "..RIR..RRIR.."

def stand_frame(dx_nh=1, dx_fh=-2, dx_nf=1, dx_ff=-2):
    img = new(CW, CH)
    draw_tail(img, WALK_TAIL, width=2, ring=3)
    leg_hind(img, (14, 15), (14 + dx_fh, FEET), "far")
    leg_front(img, (33, 15), (33 + dx_ff, FEET), "far")
    draw_torso(img, WALK_TORSO, stripes_x=[14, 19, 24, 29], belly_white=(32, 15, 37, 20), stripe_len=5)
    leg_hind(img, (14, 15), (14 + dx_nh, FEET), "near")
    leg_front(img, (33, 15), (33 + dx_nf, FEET), "near")
    CTX['head'] = (33, 5, 13)
    paste(img, hgrid(HEAD_SIDE), 33, 5)
    img.ctx = dict(CTX)
    return img

def loaf_frame(t=1.0, head="side", head_pos=(33, 10), breathe=0, twitch=False, tail_f=0):
    img = new(CW, CH)
    tor = lerp_pts(SIT_TORSO, LOAF_TORSO, t)
    tor = [(x, y - breathe if i in (1, 2, 3, 4, 5) else y) for i, (x, y) in enumerate(tor)]
    draw_torso(img, tor, stripes_x=[14, 19, 24, 29], belly_white=(34, 19, 38, 25), stripe_len=4, light_to=0.9)
    haunch_ring(img, lerp(17, 17, t), lerp(23.5, 24.5, t), 8, lerp(6.5, 5.5, t))
    # tail wraps along the ground on the near side
    wag = [0, 0, 1, 0][tail_f % 4]
    tail = [(9, 25), (7, 28), (12, 29), (20, 28.5), (27, 28.5), (31 + wag, 27.5 - wag)]
    draw_tail(img, tail, width=2, ring=3)
    CTX['tail_after'] = True
    g = {"side": HEAD_SIDE, "blink": HEAD_SIDE_BLINK, "twitch": HEAD_SIDE_TWITCH}[head]
    CTX['head'] = (int(head_pos[0]), int(head_pos[1]), 13)
    paste(img, hgrid(g), int(head_pos[0]), int(head_pos[1]))
    # front paws forward
    px0 = int(lerp(33, 36, t))
    for dy, (a, b) in enumerate([(px0 + 1, px0 + 8), (px0, px0 + 9), (px0, px0 + 9)]):
        for x in range(a, b + 1): put(img, x, 27 + dy, "white")
    for x in (px0 + 4,): 
        put(img, x, 28, "grey_l"); put(img, x, 29, "grey_l")
    put(img, px0 + 9, 29, "grey_l"); put(img, px0, 29, "grey_l")
    put(img, px0 + 8, 27, "grey_l")
    img.ctx = dict(CTX)
    return img

CURL_TORSO = [(9, 24), (11, 19), (16, 16), (23, 15), (30, 16), (36, 19), (39, 23), (38, 27), (33, 29), (24, 29.5), (15, 29.5), (10, 28), (8.5, 26)]

def curl_frame(breathe=0, twitch=False, tail_f=0):
    img = new(CW, CH)
    tor = [(x, y - breathe if i in (1, 2, 3, 4, 5) else y) for i, (x, y) in enumerate(CURL_TORSO)]
    draw_torso(img, tor, stripes_x=[14, 18, 22, 26, 30], stripe_len=5, light_to=0.9)
    haunch_ring(img, 16, 24, 6, 5)
    g = HEAD_SIDE_TWITCH if twitch else HEAD_SIDE_BLINK
    CTX['head'] = (29, 17 + breathe * 0, 13)
    paste(img, hgrid(g), 29, 17)
    wag = [0, 0, 1, 0][tail_f % 4]
    tail = [(9, 26), (10, 29), (18, 29.5), (28, 29.5), (36, 28.5), (41, 26 - wag)]
    draw_tail(img, tail, width=2, ring=3)
    CTX['tail_after'] = True
    for x in range(38, 44): put(img, x, 29, "white")
    for x in range(39, 43): put(img, x, 28, "white")
    img.ctx = dict(CTX)
    return img

def build_cat(coat="orange"):
    F = []; states = {}
    # walk
    states["walk"] = list(range(len(F), len(F) + 8))
    F += [walk_frame(i) for i in range(8)]
    # sit_down
    states["sit_down"] = list(range(len(F), len(F) + 3))
    F += [stand_frame(),
          sit_frame(head="side", head_pos=(32, 3), torso=lerp_pts(WALK_TORSO, SIT_TORSO, 0.55), tail=lerp_pts(WALK_TAIL, SIT_TAIL, 0.55)),
          sit_frame(head="side")]
    # sit_idle
    states["sit_idle"] = list(range(len(F), len(F) + 4))
    F += [sit_frame(head="side", tail=tail_swish(0)), sit_frame(head="side", tail=tail_swish(1)),
          sit_frame(head="side", tail=tail_swish(2)), sit_frame(head="blink", tail=tail_swish(3))]
    # lick_paw
    states["lick_paw"] = list(range(len(F), len(F) + 6))
    L = [dict(head="side", head_pos=(32, 2), lick=(38, 19)),
         dict(head="blink", head_pos=(33, 4), lick=(42, 16)),
         dict(head="blink", head_pos=(33, 5), lick=(42, 15), tongue=True),
         dict(head="blink", head_pos=(33, 4), lick=(42, 16)),
         dict(head="blink", head_pos=(33, 3), lick=(37, 6)),
         dict(head="side", head_pos=(32, 2), lick=(40, 12))]
    for i, kw in enumerate(L):
        F.append(sit_frame(tail=tail_swish(i // 2 * 2), **kw))
    # look_camera
    states["look_camera"] = list(range(len(F), len(F) + 2))
    F += [sit_frame(head="front", head_pos=(30, 1), tail=tail_swish(0)), sit_frame(head="front_blink", head_pos=(30, 1), tail=tail_swish(0))]
    # lie_down
    states["lie_down"] = list(range(len(F), len(F) + 3))
    F += [loaf_frame(0.35, head_pos=(32, 3)), loaf_frame(0.7, head_pos=(33, 7)), loaf_frame(1.0, head_pos=(33, 10))]
    # sleep
    states["sleep"] = list(range(len(F), len(F) + 4))
    F += [curl_frame(0), curl_frame(1, tail_f=1), curl_frame(1, True, tail_f=2), curl_frame(0, tail_f=1)]
    from coats import apply_coat
    return [apply_coat(cat_finish(f), f.ctx, coat) for f in F], states

def zoom_frames(name):
    F, st = build_cat()
    return [F[int(i)] for i in name.split(",")]

if __name__ == "__main__":
    F, st = build_cat()
    sheet(F, SCR + "cat_all.png", 5, 6)
    if "--export" in sys.argv:
        import json
        fps = dict(walk=10, sit_down=6, sit_idle=4, lick_paw=6, look_camera=1, lie_down=4, sleep=2)
        for coat, pre in (("orange", "cat"), ("black", "cat_black"), ("calico", "cat_calico"), ("tuxedo", "cat_tuxedo"), ("grey", "cat_grey")):
            F, st = build_cat(coat)
            for nm, fl in ((pre + "_R", F), (pre + "_L", [flip(f) for f in F])):
                save_asset("characters", nm, fl, fps=10, states=st, anchor=(24, 29),
                           notes=f"foreground cat ({coat} coat), 1.6x. states walk(8@10, 2px/frame), sit_down(3@6 one-shot), sit_idle(4@4), lick_paw(6@6), look_camera(2: open/blink), lie_down(3@4 one-shot), sleep(4@2 curled ball). see state_fps.")
                jp = OUT / "characters" / f"{nm}.json"
                m = json.loads(jp.read_text()); m["state_fps"] = fps
                m["state_loop"] = dict(walk=True, sit_down=False, sit_idle=True, lick_paw=True, look_camera=False, lie_down=False, sleep=True)
                jp.write_text(json.dumps(m, indent=1))
