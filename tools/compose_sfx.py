#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compose_sfx.py — 18 звуковых эффектов «Лета, которого не было» (раздел 26/этап 6 ТЗ).
Все эффекты синтезированы как звуковой дизайн (шумовые спектры, резонансы, огибающие),
а не как музыкальные ноты; лупы бесшовные (кроссфейд краёв).
Выход: game/audio/sfx/*.ogg + web_demo/audio/sfx/*.ogg
Запуск: python3 tools/compose_sfx.py
"""

import os
import numpy as np
import soundfile as sf

SR = 44100
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME = os.path.join(ROOT, "renpy_project", "game", "audio", "sfx")
WEB = os.path.join(ROOT, "web_demo", "audio", "sfx")
rng = np.random.default_rng(190818)


def t(n):
    return np.arange(n) / SR


def noise(n, color="white"):
    x = rng.normal(0, 1, n)
    if color == "white":
        return x
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR) + 1e-6
    if color == "pink":
        X /= np.sqrt(f)
    elif color == "brown":
        X /= f
    y = np.fft.irfft(X, n)
    return y / (np.abs(y).max() + 1e-9)


def bandpass(x, lo, hi, order=2.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(x.size, 1 / SR)
    m = 1.0 / (1.0 + (np.maximum(lo - f, 0) / (lo * 0.35 + 1e-6)) ** (2 * order))
    m *= 1.0 / (1.0 + (np.maximum(f - hi, 0) / (hi * 0.35 + 1e-6)) ** (2 * order))
    return np.fft.irfft(X * m, x.size)


def env_ad(n, a, d, curve=1.0):
    e = np.ones(n)
    ai = max(1, int(a * SR))
    di = max(1, int(d * SR))
    e[:ai] = np.linspace(0, 1, ai) ** curve
    if di < n:
        e[n - di:] *= np.linspace(1, 0, di) ** curve
    return e


def loopify(x, fade=0.35):
    n = int(SR * fade)
    w = np.linspace(0, 1, n)
    x = x.copy()
    x[:n] = x[:n] * w + x[-n:] * (1 - w)
    x[-n:] = x[:n]
    return x


def stereo(x, pan=0.0, width=0.0):
    if width:
        d = int(SR * width)
        r = np.roll(x, d)
        return np.stack([x, r], axis=1)
    gl = np.cos((pan + 1) * np.pi / 4)
    gr = np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * gl, x * gr], axis=1)


def norm(x, peak=0.7):
    return x / (np.abs(x).max() + 1e-9) * peak


# ------------------------------------------------------------------- эффекты --
def sfx_bus_engine(sec=20):
    n = int(SR * sec)
    tt = t(n)
    x = noise(n, "brown") * 0.6
    x = bandpass(x, 30, 220)
    pulse = (1 + 0.5 * np.sin(2 * np.pi * 27 * tt)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * tt))
    rattle = bandpass(noise(n), 300, 900) * (0.25 * (np.sin(2 * np.pi * 54 * tt) > 0.6))
    x = x * pulse + rattle * 0.4
    return loopify(norm(x)), True


def sfx_wind(sec=15):
    n = int(SR * sec)
    tt = t(n)
    x = bandpass(noise(n, "pink"), 150, 1400)
    gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.09 * tt + 1.2) * np.sin(2 * np.pi * 0.031 * tt)
    return loopify(norm(x * gust)), True


def sfx_gate_creak(sec=3):
    n = int(SR * sec)
    tt = t(n)
    f = 170 + 140 * tt / sec + 25 * np.sin(2 * np.pi * 3.1 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3.01 * ph)
    stick = (rng.normal(0, 1, n) * 0.35) * (np.sin(2 * np.pi * 7.3 * tt) > 0.2)
    x = bandpass(x + stick, 120, 1800) * env_ad(n, 0.25, 0.8)
    return norm(x), False


def sfx_crickets(sec=25):
    n = int(SR * sec)
    tt = t(n)
    x = np.zeros(n)
    c = 0.0
    while c < sec - 1:
        start = int(c * SR)
        for k in range(3):
            s0 = start + int(k * 0.035 * SR)
            ln = int(0.03 * SR)
            if s0 + ln < n:
                chirp = np.sin(2 * np.pi * 4200 * t(ln)) * np.exp(-t(ln) / 0.012)
                x[s0:s0 + ln] += chirp * 0.5
        c += rng.uniform(0.45, 0.75)
    bed = bandpass(noise(n, "pink"), 80, 500) * 0.06
    return loopify(norm(x + bed)), True


def sfx_radio_noise(sec=4):
    n = int(SR * sec)
    tt = t(n)
    x = noise(n) * 0.5
    bursts = np.zeros(n)
    for _ in range(6):
        s0 = int(rng.uniform(0, sec - 0.4) * SR)
        ln = int(rng.uniform(0.05, 0.3) * SR)
        bursts[s0:s0 + ln] += rng.uniform(0.4, 1.0)
    x = x * (0.5 + bursts)
    whine = 0.06 * np.sin(2 * np.pi * 1050 * tt + 3 * np.sin(2 * np.pi * 2.2 * tt))
    x = bandpass(x, 300, 6000) + whine
    return norm(x * env_ad(n, 0.05, 0.4)), False


def sfx_gravel(sec=6):
    n = int(SR * sec)
    x = np.zeros(n)
    pos = 0.2
    side = -1
    while pos < sec - 0.5:
        s0 = int(pos * SR)
        ln = int(0.09 * SR)
        step = bandpass(noise(ln), 900, 5200) * np.exp(-t(ln) / 0.03)
        x[s0:s0 + ln] += step * (0.9 if side < 0 else 0.7)
        side *= -1
        pos += rng.uniform(0.55, 0.7)
    return norm(x), False


def sfx_river(sec=20):
    n = int(SR * sec)
    tt = t(n)
    x = bandpass(noise(n, "pink"), 200, 2200)
    wave = 0.7 + 0.3 * np.sin(2 * np.pi * 0.23 * tt) * np.sin(2 * np.pi * 0.11 * tt + 0.7)
    blips = np.zeros(n)
    for _ in range(14):
        s0 = int(rng.uniform(0, sec - 0.3) * SR)
        ln = int(0.12 * SR)
        f0 = rng.uniform(500, 1400)
        blips[s0:s0 + ln] += np.sin(2 * np.pi * f0 * t(ln)) * np.exp(-t(ln) / 0.04) * 0.15
    return loopify(norm(x * wave + blips)), True


def sfx_glitch(sec=1.5):
    n = int(SR * sec)
    src = bandpass(noise(int(SR * 0.5)), 200, 4000) * np.exp(-t(int(SR * 0.5)) / 0.2)
    x = np.zeros(n)
    p = 0
    i = 0
    while p < n - 1:
        ln = int(rng.uniform(0.03, 0.12) * SR)
        seg = src[:min(ln, src.size)]
        if i % 3 == 2:
            seg = seg * 0.0  # dropout
        if p + seg.size < n:
            x[p:p + seg.size] = seg
        p += ln
        i += 1
    wobble = 1 + 0.25 * np.sin(2 * np.pi * 13 * t(n))
    return norm(x * wobble * env_ad(n, 0.01, 0.3)), False


def sfx_bell(sec=8):
    n = int(SR * sec)
    tt = t(n)
    f0 = 520.0
    x = np.zeros(n)
    for k, dec in ((1.0, 1.1), (2.0, 1.7), (2.98, 2.4), (4.2, 3.4), (5.6, 4.4)):
        x += np.sin(2 * np.pi * f0 * k * tt) * np.exp(-tt * dec) / k
    strike = rng.normal(0, 1, int(SR * 0.012)) * 0.3
    x[:strike.size] += strike
    return norm(x * 0.9), False


def sfx_cassette(sec=2):
    n = int(SR * sec)
    click = np.zeros(n)
    for s0, amp in ((0.05, 0.8), (0.5, 0.5)):
        i0 = int(s0 * SR)
        ln = int(0.02 * SR)
        click[i0:i0 + ln] += bandpass(noise(ln), 800, 6000) * np.exp(-t(ln) / 0.006) * amp
    whir = bandpass(noise(n), 150, 900) * 0.25 * np.minimum(1, t(n) / 0.3)
    hiss = noise(n) * 0.05 * np.minimum(1, t(n) / 0.4)
    return norm(click + whir + hiss), False


def sfx_door(sec=3):
    n = int(SR * sec)
    tt = t(n)
    f = 140 + 90 * np.minimum(1, tt / 1.6) + 12 * np.sin(2 * np.pi * 2.3 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    creak = bandpass(np.sin(ph) + 0.4 * np.sin(2.02 * ph), 100, 1500) * env_ad(n, 0.5, 1.0)
    latch = np.zeros(n)
    i0 = int(1.9 * SR)
    ln = int(0.03 * SR)
    latch[i0:i0 + ln] += bandpass(noise(ln), 1200, 7000) * np.exp(-t(ln) / 0.008) * 0.7
    thud = np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 9) * 0.5
    thud[:int(0.4 * SR)] = 0
    i1 = int(2.0 * SR)
    thud = np.roll(np.sin(2 * np.pi * 70 * tt) * np.exp(-np.maximum(0, tt - 2.0) * 9) * 0.5, 0)
    thud[:i1] = 0
    return norm(creak * 0.7 + latch + thud), False


def sfx_rain(sec=25):
    n = int(SR * sec)
    x = bandpass(noise(n), 400, 7000) * 0.5
    x += bandpass(noise(n, "pink"), 100, 800) * 0.4
    drops = np.zeros(n)
    for _ in range(60):
        s0 = int(rng.uniform(0, sec - 0.1) * SR)
        ln = int(0.02 * SR)
        drops[s0:s0 + ln] += rng.uniform(0.1, 0.35) * bandpass(noise(ln), 1500, 9000) * np.exp(-t(ln) / 0.006)
    return loopify(norm(x + drops)), True


def sfx_swing(sec=10):
    n = int(SR * sec)
    tt = t(n)
    x = np.zeros(n)
    period = 2.4
    c = 0.3
    while c < sec - 0.5:
        s0 = int(c * SR)
        ln = int(0.5 * SR)
        tl = t(ln)
        f = 950 + 420 * np.sin(2 * np.pi * 2.2 * tl)
        squeak = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tl / 0.18) * 0.35
        tick = bandpass(noise(int(0.01 * SR)), 2000, 8000) * np.exp(-t(int(0.01 * SR)) / 0.004) * 0.3
        if s0 + ln < n:
            x[s0:s0 + ln] += squeak
            x[s0:s0 + tick.size] += tick
        c += period / 2
    return loopify(norm(x)), True


def sfx_glass(sec=1.5):
    n = int(SR * sec)
    tt = t(n)
    x = np.sin(2 * np.pi * 2600 * tt) * np.exp(-tt * 14) * 0.6
    x += np.sin(2 * np.pi * 3900 * tt) * np.exp(-tt * 20) * 0.3
    rattle = bandpass(noise(n), 2000, 8000) * np.exp(-tt * 10) * 0.25
    return norm(x + rattle), False


def sfx_heartbeat(sec=4):
    n = int(SR * sec)
    tt = t(n)
    x = np.zeros(n)
    for beat in (0.0, 0.55, 1.5, 2.05, 3.0, 3.55):
        s0 = int(beat * SR)
        ln = int(0.25 * SR)
        th = np.sin(2 * np.pi * 52 * t(ln)) * np.exp(-t(ln) / 0.07)
        if s0 + ln < n:
            x[s0:s0 + ln] += th * 0.9
    return norm(x), False


def sfx_broadcast(sec=5):
    n = int(SR * sec)
    tt = t(n)
    hum = 0.12 * np.sin(2 * np.pi * 50 * tt) + 0.07 * np.sin(2 * np.pi * 100 * tt)
    room = bandpass(noise(n, "pink"), 120, 1200) * 0.12
    click = np.zeros(n)
    i0 = int(0.1 * SR)
    ln = int(0.015 * SR)
    click[i0:i0 + ln] += bandpass(noise(ln), 600, 5000) * np.exp(-t(ln) / 0.005) * 0.8
    return loopify(norm(hum + room + click)), True


def sfx_owl(sec=3):
    n = int(SR * sec)
    x = np.zeros(n)
    for start, f0, f1, dur in ((0.15, 480, 430, 0.5), (0.85, 460, 400, 0.7)):
        s0 = int(start * SR)
        ln = int(dur * SR)
        tl = t(ln)
        f = np.linspace(f0, f1, ln)
        hoot = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tl / dur) ** 1.5
        hoot = bandpass(hoot, 250, 1200)
        if s0 + ln < n:
            x[s0:s0 + ln] += hoot * 0.8
    return norm(x), False


def sfx_lineup_horn(sec=3):
    n = int(SR * sec)
    tt = t(n)
    on = ((tt > 0.25) & (tt < 2.4)).astype(float)
    on = np.convolve(on, np.exp(-np.arange(200) / 60.0))[:n] / 1.0
    on = np.clip(on, 0, 1)
    sq = np.sign(np.sin(2 * np.pi * 620 * tt)) * 0.4 + np.sin(2 * np.pi * 620 * tt) * 0.6
    sq += 0.3 * np.sign(np.sin(2 * np.pi * 1240 * tt))
    x = bandpass(sq, 400, 3200) * on * 0.6
    crackle = noise(n) * 0.06 * on
    click = np.zeros(n)
    for s0 in (0.22, 2.42):
        i0 = int(s0 * SR)
        ln = int(0.01 * SR)
        click[i0:i0 + ln] += bandpass(noise(ln), 800, 6000) * 0.6
    return norm(x + crackle + click), False


SFX = [
    ("bus_engine", sfx_bus_engine), ("wind", sfx_wind), ("gate_creak", sfx_gate_creak),
    ("crickets", sfx_crickets), ("radio_noise", sfx_radio_noise), ("gravel", sfx_gravel),
    ("river", sfx_river), ("glitch", sfx_glitch), ("bell", sfx_bell), ("cassette", sfx_cassette),
    ("door", sfx_door), ("rain", sfx_rain), ("swing", sfx_swing), ("glass", sfx_glass),
    ("heartbeat", sfx_heartbeat), ("broadcast", sfx_broadcast), ("owl", sfx_owl),
    ("lineup_horn", sfx_lineup_horn),
]


def write_ogg(path, audio, sr, chunk_sec=5):
    audio = np.ascontiguousarray(audio, dtype=np.float32)
    with sf.SoundFile(path, "w", sr, audio.shape[1], format="OGG", subtype="VORBIS") as f:
        step = int(sr * chunk_sec)
        for i in range(0, audio.shape[0], step):
            f.write(audio[i:i + step])


def main():
    os.makedirs(GAME, exist_ok=True)
    os.makedirs(WEB, exist_ok=True)
    for name, fn in SFX:
        x, is_loop = fn()
        st = stereo(x, width=0.012 if is_loop else 0.0)
        write_ogg(os.path.join(GAME, name + ".ogg"), st, SR)
        mono = np.stack([st.mean(axis=1)], axis=1)
        idx = np.linspace(0, mono.size - 1, int(mono.size * 32000 / SR))
        web = np.stack([np.interp(idx, np.arange(mono.size), mono[:, 0])], axis=1)
        write_ogg(os.path.join(WEB, name + ".ogg"), web, 32000)
        kb = os.path.getsize(os.path.join(GAME, name + ".ogg")) // 1024
        print(f"✓ {name}{' (loop)' if is_loop else ''}: {kb} KB")


if __name__ == "__main__":
    main()
