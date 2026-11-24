"""Sound for the park/café loops (bản 6c, 24/11/2026). Everything is synthesised (numpy/scipy), so there are no
licensing questions, and every season is a seamless 24 s loop like the picture (events wrap around the loop end,
noise beds and reverbs are circular).

    .venv/bin/python compose/audio_gif.py            # all seasons -> review/gif_style/v6_cafe/<season>/loop.wav,
                                                     # muxed into loop.mp4, + bon_mua.wav muxed into bon_mua.mp4

Music: a lofi beat at 80 BPM (8 bars = exactly 24 s): Rhodes-like FM electric piano chords, round bass, dusty
boom-bap drums, vinyl crackle, and a đàn bầu-like lead (pure harmonic tone with glides, vibrato and the end-of-note
bend). Each season has its own chords and feel.
Sound effects follow the picture (times come from compose/gif_frame.py): the bus arrives (diesel engine panned
right -> centre), brakes, air hiss, doors, idles, pulls away to the left; the flower bike rings its bell; the Tết
motorbike; sparrows, pigeons, swallows; the café's cups and steam; summer cicadas; rain + thunder; autumn wind,
crickets and the lion-dance drums; winter night hum, fireworks synced to fx_gif's schedule and a far temple bell.
"""
from __future__ import annotations

import math
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy.signal as ss

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "compose"))
import gif_frame as gf  # noqa: E402
import fx_gif as fx  # noqa: E402
from seasons import ORDER_OF_SEASONS, PARK_COMMON  # noqa: E402

SR = 48000
LOOP = gf.LOOP
N = int(SR * LOOP)
W = gf.W
BEAT = 60 / 80                      # 80 BPM -> 32 beats = 8 bars = 24 s
OUT = ROOT / "review/gif_style/v6_cafe"


# ------------------------------------------------------------------------------------------------ mixing helpers
def pan_gains(p):
    a = (np.clip(p, -1, 1) + 1) * math.pi / 4
    return np.cos(a), np.sin(a)


class Bus:
    """Circular stereo buffer of one loop: anything added past the end wraps to the start (seamless loop)."""

    def __init__(self):
        self.buf = np.zeros((2, N))

    def add(self, sig, t0, pan=0.0, gain=1.0):
        sig = np.asarray(sig, dtype=np.float64) * gain
        if sig.ndim == 1:
            L, R = pan_gains(pan)
            sig = np.vstack([sig * L, sig * R])
        s = int(round(t0 * SR)) % N
        n = sig.shape[1]
        i = 0
        while i < n:
            k = min(n - i, N - s)
            self.buf[:, s:s + k] += sig[:, i:i + k]
            i += k; s = (s + k) % N

    def rms(self):
        return float(np.sqrt(np.mean(self.buf ** 2)) + 1e-12)


def t_arr(dur):
    return np.arange(int(dur * SR)) / SR


def lp(x, f, order=2):
    return ss.sosfilt(ss.butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return ss.sosfilt(ss.butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, f0, f1, order=2):
    return ss.sosfilt(ss.butter(order, [f0, f1], "band", fs=SR, output="sos"), x)


def circ_band(x, f0, f1, tilt=0.0):
    """Circular (loop-seamless) band filter in the frequency domain, with a soft edge and a dB/oct tilt."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1 / (1 + (f0 / np.maximum(f, 1)) ** 4) / (1 + (f / f1) ** 4)
    if tilt:
        g *= (np.maximum(f, 20) / 1000) ** (tilt / 6.02)
    return np.fft.irfft(X * g, len(x))


def circ_reverb(buf, tau, mix, lowpass=5000, seed=1):
    """Circular convolution with an exponentially decaying noise tail (outdoor / small room)."""
    rng = np.random.default_rng(seed)
    n_ir = int(tau * 5 * SR)
    t = np.arange(n_ir) / SR
    out = np.empty_like(buf)
    for ch in range(2):
        ir = rng.standard_normal(n_ir) * np.exp(-t / tau)
        ir = lp(ir, lowpass); ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
        ir /= np.sqrt(np.sum(ir ** 2))
        IR = np.zeros(N); IR[:n_ir] = ir
        wet = np.fft.irfft(np.fft.rfft(buf[ch]) * np.fft.rfft(IR), N)
        out[ch] = buf[ch] + mix * wet
    return out


def env(n, a=0.005, tau=0.3, rel_at=None, rel=0.05):
    t = np.arange(n) / SR
    e = (1 - np.exp(-t / max(a, 1e-4))) * np.exp(-t / tau)
    if rel_at is not None:
        e *= np.where(t > rel_at, np.exp(-(t - rel_at) / rel), 1.0)
    return e


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------------------------------------ instruments
def epiano(f, dur, vel=1.0):
    t = t_arr(dur + 1.6)
    I = 1.5 * np.exp(-t * 7) + 0.25
    mod = I * np.sin(2 * np.pi * f * t)
    s = np.sin(2 * np.pi * f * t + mod) + 0.6 * np.sin(2 * np.pi * f * 1.0025 * t + 0.8 * mod)
    s += 0.12 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 35)          # tine bark
    s *= 1 + 0.08 * np.sin(2 * np.pi * 4.0 * t)                              # gentle tremolo (4 Hz divides the loop)
    return vel * 0.22 * s * env(len(t), 0.004, 1.5, dur, 0.28)


def bass(f, dur, vel=1.0):
    t = t_arr(dur + 0.4)
    s = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    return vel * 0.5 * np.tanh(1.4 * s * env(len(t), 0.008, 0.9, dur, 0.08))


def kick(vel=1.0):
    t = t_arr(0.4)
    f = 46 + 75 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
    s += 0.15 * lp(np.random.default_rng(3).standard_normal(len(t)), 2500) * np.exp(-t * 90)
    return vel * 0.75 * s


def snare(vel=1.0, seed=0):
    t = t_arr(0.3)
    nz = bp(np.random.default_rng(seed).standard_normal(len(t)), 900, 5500) * np.exp(-t * 17)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 24)
    return vel * 0.33 * lp(nz * 0.9 + tone * 0.6, 6000)


def hat(vel=1.0, seed=0, open_=False):
    t = t_arr(0.25 if open_ else 0.07)
    nz = hp(np.random.default_rng(100 + seed).standard_normal(len(t)), 7000)
    return vel * 0.12 * lp(nz, 11000) * np.exp(-t * (14 if open_ else 55))


def rim(vel=1.0):
    t = t_arr(0.08)
    return vel * 0.25 * (np.sin(2 * np.pi * 1650 * t) + 0.5 * np.sin(2 * np.pi * 820 * t)) * np.exp(-t * 70)


def dan_bau(m0, dur, m_end=None, vel=1.0, scoop=True):
    """Đàn bầu-like voice: an almost pure harmonic tone, a scoop into the note, vibrato that blooms, and the
    characteristic bend at the end of the note (the player pushes the flexible rod)."""
    t = t_arr(dur + 0.5)
    f0 = mtof(m0)
    f = np.full(len(t), f0)
    if scoop:
        f *= 2 ** (-0.6 / 12 * np.exp(-t / 0.07))
    vib = np.clip((t - 0.25) / 0.6, 0, 1) * 0.006 * np.sin(2 * np.pi * 5.5 * t)
    f *= 1 + vib
    if m_end is not None:
        b = np.clip((t - dur * 0.65) / (dur * 0.3), 0, 1)
        f *= 2 ** ((m_end - m0) / 12 * (b * b * (3 - 2 * b)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
    e = env(len(t), 0.006, 2.2, dur, 0.18) * (0.75 + 0.25 * np.exp(-t * 6))
    return vel * 0.16 * lp(s * e, 4500)


def music_box(m, vel=1.0):
    t = t_arr(1.6)
    f = mtof(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 6)
    return vel * 0.12 * s * np.exp(-t * 2.6) * (1 - np.exp(-t / 0.002))


# ------------------------------------------------------------------------------------------------ music per season
# (bass midi, chord voicing) x 4, two bars each; pentatonic scale for the lead; drum feel
SONGS = {
    "xuan": dict(ch=[(38, [54, 57, 61, 64]), (35, [57, 61, 62, 66]), (40, [55, 59, 62, 66]), (33, [55, 59, 61, 66])],
                 scale=[62, 64, 66, 69, 71], drums="full", lead="bau"),          # D major, bright
    "ha": dict(ch=[(41, [57, 60, 64, 67]), (40, [55, 59, 62, 64]), (38, [53, 57, 60, 64]), (36, [52, 55, 59, 62])],
               scale=[60, 62, 64, 67, 69], drums="full", lead="bau"),            # C major, Fmaj7-Em7-Dm7-Cmaj7
    "mua": dict(ch=[(33, [55, 59, 60, 64]), (41, [57, 60, 64, 67]), (38, [53, 57, 60, 64]), (40, [56, 59, 62, 64])],
                scale=[57, 60, 62, 64, 67], drums="soft", lead="bau"),           # A minor, rainy
    "thu": dict(ch=[(38, [53, 57, 60, 64]), (31, [53, 57, 59, 62]), (36, [52, 55, 59, 62]), (33, [55, 61, 65, 67])],
                scale=[62, 65, 67, 69, 72], drums="light", lead="bau"),          # D minor, nostalgic
    "dong": dict(ch=[(39, [55, 58, 62, 65]), (36, [51, 55, 58, 62]), (32, [55, 58, 60, 63]), (34, [56, 62, 65, 67])],
                 scale=[63, 65, 67, 70, 72], drums="brush", lead="box"),         # Eb major, cosy night
}
PHRASES = [  # (bar, beat, beats, scale degree, end degree or None)
    (2, 0.5, 1.0, 2, None), (2, 1.5, 1.5, 3, None), (2, 3.0, 4.0, 4, 3),
    (6, 0.0, 1.5, 4, None), (6, 2.0, 1.0, 3, None), (6, 3.0, 4.5, 2, 1),
]


def deg(scale, d, octave=1):
    return scale[d % 5] + 12 * (d // 5 + octave)


def music(key):
    S = SONGS[key]
    bus = Bus()
    rng = random.Random(7)
    for c, (bm, voicing) in enumerate(S["ch"]):
        for b2 in range(2):
            bar = c * 2 + b2
            t0 = bar * 4 * BEAT
            hits = [(0.0, 3.2, 0.9), (3.5, 0.9, 0.55)] if b2 == 0 else [(0.0, 2.2, 0.6), (2.5, 1.8, 0.7)]
            for beat, beats, vel in hits:
                for j, m in enumerate(voicing):
                    bus.add(epiano(mtof(m), beats * BEAT, vel * (0.9 + 0.1 * j)), t0 + beat * BEAT + j * 0.012,
                            pan=-0.25 + 0.17 * j)
            bl = [(0.0, 1.6, bm, 1.0), (2.5, 0.9, bm + 7, 0.7)] if b2 == 0 else [(0.0, 1.4, bm, 0.9), (2.0, 0.9, bm + 12, 0.6), (3.5, 0.45, bm + 7, 0.6)]
            for beat, beats, m, vel in bl:
                bus.add(bass(mtof(m), beats * BEAT, vel), t0 + beat * BEAT)
            # drums
            sw = 0.09 * BEAT                                                      # swing on the off-beats
            if S["drums"] in ("full", "soft", "light"):
                kv = {"full": 0.9, "soft": 0.55, "light": 0.5}[S["drums"]]
                for beat in ((0.0, 1.75, 2.5) if S["drums"] == "full" else (0.0, 2.5)):
                    bus.add(kick(kv), t0 + beat * BEAT + (sw if beat % 1 else 0))
                for beat in (1.0, 3.0):
                    bus.add(snare(0.85 if S["drums"] == "full" else 0.5, seed=bar * 2 + int(beat)), t0 + beat * BEAT)
            else:                                                                 # brushes: rim + soft hats
                for beat in (1.0, 3.0):
                    bus.add(rim(0.5), t0 + beat * BEAT)
                bus.add(kick(0.35), t0)
            for h in range(8):
                beat = h * 0.5
                v = (0.55 if h % 2 else 0.8) * (0.8 + 0.4 * rng.random()) * (0.6 if S["drums"] in ("soft", "brush") else 1)
                bus.add(hat(v, seed=bar * 8 + h, open_=(h == 7 and b2 == 1)), t0 + beat * BEAT + (sw if h % 2 else 0),
                        pan=0.3)
    for bar, beat, beats, d, d_end in PHRASES:                                    # the lead
        t0 = (bar * 4 + beat) * BEAT
        if S["lead"] == "bau":
            m = deg(S["scale"], d)
            bus.add(dan_bau(m, beats * BEAT, deg(S["scale"], d_end) if d_end is not None else None), t0, pan=0.15)
        else:
            for k in range(int(beats * 2)):                                       # music-box arpeggio for winter
                bus.add(music_box(deg(S["scale"], d + (k % 3)), 0.8 - 0.1 * (k % 3)), t0 + k * BEAT / 2, pan=0.2)
    # vinyl: hiss + crackle (circular)
    rng_n = np.random.default_rng(11)
    hiss = circ_band(rng_n.standard_normal(N), 2500, 12000) * 0.006
    crackle = np.zeros(N)
    idx = rng_n.integers(0, N, 260)
    crackle[idx] = rng_n.uniform(0.1, 0.5, len(idx)) * rng_n.choice([-1, 1], len(idx))
    crackle = circ_band(crackle, 800, 9000) * 0.5
    bus.buf += np.vstack([hiss + crackle, hiss + np.roll(crackle, 37)])
    out = bus.buf
    out[0] = circ_band(out[0], 25, 7000); out[1] = circ_band(out[1], 25, 7000)    # dusty top end
    out = np.tanh(out * 1.3) / 1.3
    return circ_reverb(out, 0.45, 0.22, 4000, seed=5)


# ------------------------------------------------------------------------------------------------ sound effects
def x_to_pan(x):
    return np.clip((np.asarray(x, dtype=float) - W / 2) / (W / 2), -1, 1) * 0.85


def dist_gain(cx, near=120, fall=140):
    d = np.maximum(0, np.abs(np.asarray(cx, dtype=float) - W / 2) - near)
    return 1 / (1 + (d / fall) ** 2)


def engine(f0, rng, harmonics=14, roll=0.75, chug=0.5, lowpass=1100):
    ph = 2 * np.pi * np.cumsum(f0) / SR
    s = np.zeros(len(f0))
    for k in range(1, harmonics + 1):
        s += np.sin(k * ph + rng.uniform(0, 6.28)) / k ** roll
    nz = lp(rng.standard_normal(len(f0)), 500) * (1 + chug * np.sin(ph) ** 6)
    return lp(s * 0.5 + nz * 0.8, lowpass)


def add_moving(bus, sig, t0, xs_fn, gain):
    t = t0 + np.arange(len(sig)) / SR
    xs = np.array([xs_fn(tt) for tt in t[::480]])
    xs = np.interp(np.arange(len(sig)), np.arange(0, len(sig), 480)[: len(xs)], xs)
    g = dist_gain(xs) * gain
    L, R = pan_gains(x_to_pan(xs))
    bus.add(np.vstack([sig * g * L, sig * g * R]), t0)


def noise_burst(dur, f0, f1, a=0.01, tau=0.3, seed=0):
    n = int(dur * SR)
    return bp(np.random.default_rng(seed).standard_normal(n), f0, f1) * env(n, a, tau)


def sfx_bus(bus, key):
    rng = np.random.default_rng(21)
    BW_ = 148
    t0, t1 = gf.BUS_T_IN - 1.5, gf.BUS_T_OUT + 1.0

    def bx(t):
        x = gf.bus_x(t, BW_)
        if x is None:
            x = W + 4 + (gf.BUS_T_IN - t) * 60 if t < gf.BUS_T_STOP else -BW_ - 12 - (t - gf.BUS_T_OUT) * 80
        return x + BW_ / 2

    t = t0 + t_arr(t1 - t0)
    f0 = np.where(t < gf.BUS_T_STOP, 30 - 4 * np.clip((t - gf.BUS_T_IN) / (gf.BUS_T_STOP - gf.BUS_T_IN), 0, 1),
                  np.where(t < gf.BUS_T_GO, 25.5, 27 + 16 * np.clip((t - gf.BUS_T_GO) / 3.0, 0, 1) ** 0.7))
    f0 = f0 * (1 + 0.01 * np.sin(2 * np.pi * 0.5 * t))
    load = np.where((t > gf.BUS_T_GO) & (t < gf.BUS_T_GO + 4), 1.5, 1.0)
    sig = engine(f0, rng) * load
    sig *= np.clip((t - t0) / 1.2, 0, 1) * np.clip((t1 - t) / 1.0, 0, 1)
    if key == "mua":                                                                   # tyres on a wet road
        v = np.abs(np.gradient(np.array([bx(tt) for tt in t[::480]])))
        v = np.interp(np.arange(len(t)), np.arange(0, len(t), 480)[: len(v)], v)
        sig += bp(rng.standard_normal(len(t)), 900, 6000) * np.clip(v / 3, 0, 1) * 0.5
    add_moving(bus, sig, t0, bx, 0.30)
    stop_x = gf.BUS_X_STOP + BW_ / 2
    p = float(x_to_pan(stop_x))
    sq = t_arr(0.55)                                                                     # brake squeal
    bus.add(np.sin(2 * np.pi * (2350 + 18 * np.sin(2 * np.pi * 7 * sq)) * sq) * np.sin(np.pi * sq / 0.55) ** 2,
            gf.BUS_T_STOP - 0.55, pan=p, gain=0.035)
    bus.add(noise_burst(0.9, 1800, 9000, 0.01, 0.35, seed=1), gf.BUS_T_STOP + 0.1, pan=p, gain=0.20)   # air brake
    for tt, s_ in ((gf.BUS_T_STOP + 0.7, 2), (gf.BUS_T_GO - 0.8, 3)):                   # doors: hiss + thunk
        bus.add(noise_burst(0.45, 1200, 7000, 0.02, 0.15, seed=s_), tt, pan=p * 0.7, gain=0.12)
        th = t_arr(0.2)
        bus.add(np.sin(2 * np.pi * 85 * th) * np.exp(-th * 25), tt + 0.4, pan=p * 0.7, gain=0.25)


def sfx_moto(bus):
    rng = np.random.default_rng(5)
    t0, t1 = gf.MOTO_T0 - 1.0, gf.MOTO_T1 + 1.0
    v = (W + 70) / (gf.MOTO_T1 - gf.MOTO_T0)
    t = t0 + t_arr(t1 - t0)
    sig = engine(np.full(len(t), 44.0) * (1 + 0.02 * np.sin(2 * np.pi * 0.8 * t)), rng, harmonics=10, roll=0.9,
                 chug=1.2, lowpass=1600)
    sig *= np.clip((t - t0) / 0.8, 0, 1) * np.clip((t1 - t) / 0.8, 0, 1)
    add_moving(bus, sig, t0, lambda tt: W + 8 - (tt - gf.MOTO_T0) * v + 18, 0.16)


def bell_ring(strikes=6, rate=22.0, seed=0):
    """Bicycle bell 'kring': a rotating striker hits the dome several times quickly."""
    t = t_arr(1.2)
    rng = np.random.default_rng(seed)
    s = np.zeros(len(t))
    parts = [(3150, 1.0, 0.55), (4370, 0.6, 0.45), (6020, 0.35, 0.3), (7900, 0.2, 0.2)]
    for k in range(strikes):
        st = int(k / rate * SR)
        tt = t[: len(t) - st]
        a = 0.85 ** k * rng.uniform(0.8, 1.0)
        for f, amp, tau in parts:
            s[st:] += a * amp * np.sin(2 * np.pi * f * (1 + 0.002 * k) * tt) * np.exp(-tt / tau)
    return s * 0.12


def sfx_bike(bus):
    span = W + 60
    def bxf(tt):
        u = (tt - gf.BIKE_T0) % LOOP
        return -30 + u * span / gf.BIKE_DUR
    for du, seed in ((2.6, 1), (3.0, 2), (6.2, 3)):                                      # "kring kring" ... "kring"
        x = bxf(gf.BIKE_T0 + du)
        bus.add(bell_ring(5 if seed != 2 else 4, seed=seed), gf.BIKE_T0 + du, pan=float(x_to_pan(x)),
                gain=float(dist_gain(x)) * 0.9)
    tick = t_arr(0.012)                                                                   # freewheel ticks
    click = np.sin(2 * np.pi * 5200 * tick) * np.exp(-tick * 600)
    for k in range(int(gf.BIKE_DUR * 9)):
        tt = gf.BIKE_T0 + k / 9
        x = bxf(tt)
        bus.add(click, tt, pan=float(x_to_pan(x)), gain=0.02 * float(dist_gain(x)))


def chirp(rng, f0, f1, dur):
    t = t_arr(dur)
    f = f0 + (f1 - f0) * (t / dur) + 300 * np.sin(2 * np.pi * rng.uniform(25, 45) * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) ** 2


def sfx_birds(bus, key, rng):
    perches = [312, 377]                                                                  # stop sign, stool
    for g in range(7):
        t0 = rng.uniform(0, LOOP)
        x = perches[g % 2]
        for k in range(rng.integers(2, 5)):
            f0 = rng.uniform(3800, 5200)
            bus.add(chirp(rng, f0, f0 + rng.uniform(-1200, 900), rng.uniform(0.05, 0.11)), t0 + k * rng.uniform(0.12, 0.2),
                    pan=float(x_to_pan(x)), gain=0.05)
    for tt in (4.6, 12.3, 19.8):                                                          # pigeons cooing on the roof
        t = t_arr(1.1)
        f = 330 + 90 * np.sin(np.pi * np.clip(t / 0.5, 0, 1)) - 40 * (t > 0.6)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t))
        e = np.where(t < 0.55, np.sin(np.pi * t / 0.55), np.where(t > 0.62, np.sin(np.pi * np.clip((t - 0.62) / 0.45, 0, 1)), 0))
        bus.add(lp(s * e, 1200), tt, pan=float(x_to_pan(258)), gain=0.07)
    if key == "xuan":                                                                    # swallows twittering
        for g in range(10):
            t0 = rng.uniform(0, LOOP)
            for k in range(rng.integers(3, 7)):
                f0 = rng.uniform(5500, 7500)
                bus.add(chirp(rng, f0, f0 + rng.uniform(-1500, 1500), 0.04), t0 + k * 0.07, pan=rng.uniform(-0.6, 0.6),
                        gain=0.035)


def sfx_cafe(bus, rng, steam=True):
    pc = float(x_to_pan(235))
    for tt in rng.uniform(0, LOOP, 4):                                                    # cups on saucers
        t = t_arr(0.4)
        s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, a, d in ((2850, 1, 14), (4620, 0.6, 20), (7130, 0.3, 30)))
        bus.add(s, tt, pan=pc, gain=0.035)
    if steam:
        bus.add(noise_burst(1.6, 2500, 10000, 0.15, 0.7, seed=9) * 0.8, 15.2, pan=pc, gain=0.05)


def bed(bus, sig_l, sig_r, gain):
    bus.buf[0] += sig_l * gain; bus.buf[1] += sig_r * gain


def sfx_beds(bus, key, rng):
    t = np.arange(N) / SR
    nl, nr = rng.standard_normal(N), rng.standard_normal(N)
    city = 0.5 if key == "dong" else 1.0
    bed(bus, circ_band(nl, 60, 700, -3), circ_band(nr, 60, 700, -3), 0.045 * city)       # far traffic hum
    if key == "ha":                                                                       # cicadas (ve sầu)
        for side, ph, fc in ((-0.7, 0.0, 5200), (0.6, 2.1, 6100)):
            c = circ_band(rng.standard_normal(N), fc - 700, fc + 700)
            puls = (0.5 + 0.5 * np.sin(2 * np.pi * 125 * t)) ** 3
            swell = np.clip(0.55 + 0.45 * np.sin(2 * np.pi * t / 8 + ph), 0, 1) ** 2
            L, R = pan_gains(side)
            bed(bus, c * puls * swell * L, c * puls * swell * R, 0.05)
    if key == "mua":                                                                      # rain + drips + thunder
        bed(bus, circ_band(nl, 400, 9000, -2), circ_band(nr, 400, 9000, -2), 0.11)
        for k in range(900):
            tt = rng.uniform(0, LOOP); x = rng.uniform(0, W)
            d = t_arr(0.02)
            bus.add(np.sin(2 * np.pi * rng.uniform(2500, 6000) * d) * np.exp(-d * 260), tt, pan=float(x_to_pan(x)),
                    gain=rng.uniform(0.01, 0.04))
        tt = t_arr(5.0)
        rumble = lp(np.random.default_rng(4).standard_normal(len(tt)), 160) * np.minimum(tt / 0.6, 1) * np.exp(-tt / 1.6)
        bus.add(rumble * (1 + 0.6 * np.sin(2 * np.pi * 3 * tt)), 5.5, pan=0.3, gain=0.55)
    if key == "thu":                                                                      # wind, leaves, crickets
        wind = np.clip(0.5 + 0.5 * np.sin(2 * np.pi * t / 6), 0, 1) ** 1.5
        bed(bus, circ_band(nl, 150, 1400) * wind, circ_band(nr, 150, 1400) * np.roll(wind, SR), 0.06)
        for side, rate in ((-0.6, 0.55), (0.7, 0.62)):
            for k in range(int(LOOP / rate)):
                tt = k * rate + rng.uniform(0, 0.05)
                for j in range(3):
                    d = t_arr(0.018)
                    bus.add(np.sin(2 * np.pi * 4600 * d) * np.sin(np.pi * d / 0.018), tt + j * 0.03, pan=side, gain=0.018)
    if key == "dong":
        d = t_arr(7.0)                                                                    # far temple bell (Giao thừa)
        s = sum(a * np.sin(2 * np.pi * 98 * r * d) * np.exp(-d / tau)
                for r, a, tau in ((1, 1, 3.0), (2.0, 0.5, 2.0), (2.76, 0.4, 1.6), (5.4, 0.2, 0.8), (8.9, 0.1, 0.5)))
        bus.add(lp(s, 1500) * (1 - np.exp(-d / 0.004)), 0.6, pan=-0.4, gain=0.09)


def sfx_lion(bus):
    """Trống lân + chũm chọe, loud when the troupe is on screen (thu)."""
    rng = np.random.default_rng(8)
    span = W + 110
    def lx(tt):
        return -50 + ((tt + 4.95) * span / LOOP) % span
    pattern = [(0, "T"), (0.5, "T"), (1, "T"), (1.5, "c"), (2, "T"), (2.5, "c"), (3, "T"), (3.5, "T")]
    for bar in range(8):
        for beat, kind in pattern:
            tt = (bar * 4 + beat) * BEAT
            x = lx(tt)
            g = float(dist_gain(x, near=150, fall=110))
            d = t_arr(0.5)
            if kind == "T":
                f = 95 + 60 * np.exp(-d * 40)
                s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-d * 9) + 0.3 * lp(rng.standard_normal(len(d)), 1500) * np.exp(-d * 60)
            else:
                s = (np.sin(2 * np.pi * 1500 * d) + 0.6 * np.sin(2 * np.pi * 2300 * d)) * np.exp(-d * 55)
            bus.add(s, tt, pan=float(x_to_pan(x)), gain=0.22 * g)
        tt = bar * 4 * BEAT; x = lx(tt)
        c = t_arr(0.9)
        cym = hp(rng.standard_normal(len(c)), 3000) * np.exp(-c * 5) + 0.3 * sum(np.sin(2 * np.pi * f * c) for f in (3400, 5100, 6800)) * np.exp(-c * 6)
        bus.add(cym, tt, pan=float(x_to_pan(x)), gain=0.05 * float(dist_gain(x, 150, 110)))


def sfx_fireworks(bus):
    region = tuple(PARK_COMMON["fw_region"])
    sched = fx._fw_schedule(3, int(LOOP * gf.FPS), float(LOOP), region)
    rng = np.random.default_rng(12)
    for b in sched:
        launch = b["start"] / gf.FPS
        boom = launch + b["rise"] + (0.35 if b["far"] else 0.2)                            # sound arrives a bit late
        p = float(x_to_pan(b["bx"]))
        g = 0.45 if b["far"] else 1.0
        if not b["far"]:                                                                   # whistle on the way up
            d = t_arr(b["rise"])
            f = 700 + 1400 * (d / b["rise"])
            bus.add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * d / b["rise"]) ** 2, launch, pan=p, gain=0.015)
        d = t_arr(2.5)
        thump = np.sin(2 * np.pi * np.cumsum(55 + 40 * np.exp(-d * 20)) / SR) * np.exp(-d * 4)
        crack = lp(rng.standard_normal(len(d)), 2200) * np.exp(-d * 7)
        bus.add(thump * 0.8 + crack * 0.5, boom, pan=p, gain=0.25 * g)
        if b["kind"] in ("crackle", "willow"):
            for k in range(40 if b["kind"] == "crackle" else 18):
                tt = boom + 0.3 + rng.uniform(0, 1.4)
                c = t_arr(0.01)
                bus.add(rng.standard_normal(len(c)) * np.exp(-c * 400), tt, pan=p + rng.uniform(-0.1, 0.1), gain=0.06 * g)


def effects(key):
    rng = np.random.default_rng({"xuan": 1, "ha": 2, "mua": 3, "thu": 4, "dong": 5}[key])
    bus = Bus()
    sfx_beds(bus, key, rng)
    sfx_bus(bus, key)
    sfx_bike(bus)
    if key == "xuan":
        sfx_moto(bus)
    if key in ("xuan", "ha", "thu"):
        sfx_birds(bus, key, rng)
    sfx_cafe(bus, rng, steam=key != "mua")
    if key == "thu":
        sfx_lion(bus)
    if key == "dong":
        sfx_fireworks(bus)
    return circ_reverb(bus.buf, 0.28, 0.18, 6000, seed=9)


# ------------------------------------------------------------------------------------------------ render + mux
def season_audio(key):
    m = music(key)
    e = effects(key)
    m *= 0.085 / (np.sqrt(np.mean(m ** 2)) + 1e-9)                    # music forward, effects under it
    e *= 0.060 / (np.sqrt(np.mean(e ** 2)) + 1e-9)
    mix = m + e
    return mix * (0.89 / max(1e-9, np.max(np.abs(mix))))


def write_wav(path, stereo):
    import wave
    a = np.clip(stereo.T, -1, 1)
    pcm = (a * 32767).astype("<i2").tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm)


def mux(video, wav, out):
    tmp = out.with_suffix(".tmp.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(wav), "-map", "0:v:0", "-map",
                    "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(tmp)], check=True)
    tmp.replace(out)


WHOOSH_GAIN = 0.32


def whoosh(dur, seed=0):
    """The season-change gust: band-passed noise that swells as the front crosses the frame, a gusty flutter, a scatter
    of leaf ticks, panned left -> right with the same easing as the picture (compose/transition.py)."""
    rng = np.random.default_rng(300 + seed)
    n = int(round(dur * SR))
    t = np.arange(n) / SR
    u = t / dur
    x = rng.standard_normal(n)
    lo, mid, hi_ = bp(x, 120, 450), bp(x, 450, 1600), bp(x, 1800, 6000)
    swell = np.sin(np.pi * u) ** 1.6
    bright = np.sin(np.pi * np.clip((u - 0.15) / 0.7, 0, 1)) ** 2
    flutter = 1 + 0.3 * np.sin(2 * np.pi * (4.2 * t + 0.6 * np.sin(2 * np.pi * 0.9 * t)))
    sig = (lo + 0.8 * mid * bright + 0.25 * hi_ * bright) * swell * flutter
    ticks = np.zeros(n)
    k = np.arange(400)
    for _ in range(int(dur * 70)):                       # leaves / petals ticking past
        i0 = int(rng.integers(0, n - 400))
        ticks[i0:i0 + 400] += rng.uniform(0.3, 1.0) * rng.standard_normal(400) * np.exp(-k / 60)
    sig = sig / (np.max(np.abs(sig)) + 1e-9) + 0.22 * hp(ticks, 2500) / (np.max(np.abs(ticks)) + 1e-9) * swell ** 2
    L, R = pan_gains(-0.9 + 1.8 * u * u * (3 - 2 * u))
    st = np.vstack([sig * L, sig * R])
    return st / (np.max(np.abs(st)) + 1e-9)


def montage_audio(loops, trans=None):
    """Same timeline as gif_frame.montage: each season 24 s, starting `trans` s into its loop (its first seconds play
    under the gust that brings it in); the last `trans` s cross-fade into the next season under a wind whoosh."""
    trans = gf.MONTAGE_TRANS if trans is None else trans
    tf = int(round(trans * SR))
    parts = []
    keys = list(loops)
    for i, k in enumerate(keys):
        a = np.roll(loops[k], -tf, axis=1)
        nxt = loops[keys[(i + 1) % len(keys)]]
        u = np.linspace(0, 1, tf)
        a[:, -tf:] = a[:, -tf:] * np.cos(u * np.pi / 2) + nxt[:, :tf] * np.sin(u * np.pi / 2)
        a[:, -tf:] += WHOOSH_GAIN * whoosh(trans, seed=i)
        parts.append(a)
    m = np.concatenate(parts, axis=1)
    pk = float(np.max(np.abs(m)))
    return m * (0.97 / pk) if pk > 0.97 else m


def attach(video: Path, wav: Path):
    """Keep the picture-only render as <name>_silent.mp4 (refreshed whenever gif_frame re-renders), mux the sound."""
    silent = video.with_name(video.stem + "_silent.mp4")
    if not _has_audio(video):
        video.replace(silent)
    mux(silent, wav, video)


def main():
    loops = {}
    for key in ORDER_OF_SEASONS:
        a = season_audio(key)
        loops[key] = a
        wav = OUT / key / "loop.wav"
        reps = max(1, round(_duration(OUT / key / "loop.mp4") / gf.LOOP))   # 6c: the clip is 5 x 24 s (drifting clouds)
        write_wav(wav, np.tile(a, (1, reps)))
        attach(OUT / key / "loop.mp4", wav)
        print(key, "peak", round(float(np.max(np.abs(a))), 3), "rms", round(float(np.sqrt(np.mean(a ** 2))), 3))
    ma = montage_audio(loops)
    write_wav(OUT / "bon_mua.wav", ma)
    attach(OUT / "bon_mua.mp4", OUT / "bon_mua.wav")
    print("montage audio:", OUT / "bon_mua.mp4")


def _duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def _has_audio(path: Path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0",
                        str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())


if __name__ == "__main__":
    main()
