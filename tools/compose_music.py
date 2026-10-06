#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compose_music.py — партитуры и рендер оригинального саундтрека
«Лето, которого не было» (9 треков, раздел 27 ГДД).

У каждого трека есть тональность, темп, форма и гармоническая сетка;
лейтмотив M («билет») звучит в Main Theme, возвращается в Finale (увеличение)
и в Farewell (половинный темп); мотив L («фонарь») — в Lena Theme;
мотив Z («карандаш») — в Zoya Theme. Secret-концовка по ГДД использует Main Theme.

Инструменты — аддитивный синтез с осмысленными обертонами:
  piano — обертоны 1/k^1.8, молоточковая атака, расстройка пары струн;
  guitar — щипок с быстро гаснущими обертонами и шумом ногтя;
  pad — три расстроенные пилы через ФНЧ с медленной атакой;
  box — музыкальная шкатулка (синус + 4-я гармоника);
  bass — синус + суб-октава;
  brush — полосовой шум щёток;
  bell — негармонические частичные 1 / 2.0 / 2.98 / 4.2.
Пространство — convolution-реверб (FFT) с экспоненциальной IR 1.3 c + панорама.

Выход: game/audio/*.ogg и web_demo/audio/*.ogg (Vorbis ~160 kbps)
Запуск: python3 tools/compose_music.py
"""

import os
import numpy as np
import soundfile as sf

SR = 44100
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME_AUDIO = os.path.join(ROOT, "renpy_project", "game", "audio")
WEB_AUDIO = os.path.join(ROOT, "web_demo", "audio")
rng = np.random.default_rng(20050818)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


# --------------------------------------------------------------- инструменты --
def piano(midi, dur, vel=0.8):
    n = int(SR * (dur + 2.5))
    t = np.arange(n) / SR
    f = hz(midi)
    out = np.zeros(n)
    for k in range(1, 7):
        amp = vel / (k ** 1.8)
        dec = np.exp(-t * (1.1 + 0.55 * k) * (0.6 + f / 900.0))
        det = 1.0 + 0.0006 * (k % 2)
        out += amp * dec * np.sin(2 * np.pi * f * k * det * t)
    hammer = rng.normal(0, 1, int(SR * 0.006)) * np.exp(-np.arange(int(SR * 0.006)) / (SR * 0.0015))
    out[: hammer.size] += hammer * 0.25 * vel
    env = np.minimum(1.0, t / 0.004)
    rel = np.ones(n)
    cut = int(SR * dur)
    rel[cut:] = np.exp(-np.arange(n - cut) / (SR * 0.25))
    return out * env * rel


def guitar(midi, dur, vel=0.7):
    n = int(SR * (dur + 2.0))
    t = np.arange(n) / SR
    f = hz(midi)
    out = np.zeros(n)
    for k in range(1, 9):
        amp = vel / (k ** 1.3)
        dec = np.exp(-t * (2.2 + 1.1 * k))
        out += amp * dec * np.sin(2 * np.pi * f * k * t + k)
    nail = rng.normal(0, 1, int(SR * 0.004)) * 0.12 * vel
    out[: nail.size] += nail
    return out


def pad(midi, dur, vel=0.35):
    n = int(SR * (dur + 1.5))
    t = np.arange(n) / SR
    f = hz(midi)
    out = np.zeros(n)
    for det in (-0.0035, 0.0, 0.0035):
        saw = 2.0 * ((t * f * (1 + det)) % 1.0) - 1.0
        out += saw
    # однополюсный ФНЧ через свёртку с усечённой импульсной характеристикой
    a = np.exp(-2 * np.pi * 900.0 / SR)
    k = int(np.ceil(np.log(0.01) / np.log(a)))
    ir = (1 - a) * (a ** np.arange(k))
    y = np.convolve(out, ir)[:n]
    atk = np.minimum(1.0, t / 1.2)
    rel = np.ones(n)
    cut = int(SR * dur)
    if cut < n:
        rel[cut:] = np.exp(-np.arange(n - cut) / (SR * 1.1))
    vib = 1.0 + 0.002 * np.sin(2 * np.pi * 4.7 * t)
    return y * atk * rel * vel * vib


def box(midi, dur, vel=0.6):
    n = int(SR * (dur + 1.2))
    t = np.arange(n) / SR
    f = hz(midi)
    out = (np.sin(2 * np.pi * f * t) * np.exp(-t * 5.5)
           + 0.35 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 11.0))
    return out * vel


def bass(midi, dur, vel=0.5):
    n = int(SR * (dur + 0.6))
    t = np.arange(n) / SR
    f = hz(midi)
    out = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 3)
    env = np.minimum(1.0, t / 0.01) * np.exp(-t * 1.2)
    return out * env * vel


def brush(dur=0.25, vel=0.25):
    n = int(SR * dur)
    noise = rng.normal(0, 1, n)
    # полосовой ~ 5 кГц
    x = np.fft.rfft(noise)
    fr = np.fft.rfftfreq(n, 1 / SR)
    x *= np.exp(-((fr - 5200) / 2600) ** 2)
    out = np.fft.irfft(x, n)
    env = np.exp(-np.arange(n) / (SR * 0.06))
    return out / (np.abs(out).max() + 1e-9) * env * vel


def bell(dur=6.0, vel=0.5, f0=340.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, dec in ((1.0, 1.6), (2.0, 2.2), (2.98, 3.0), (4.2, 4.2)):
        out += np.sin(2 * np.pi * f0 * k * t) * np.exp(-t * dec) / k
    strike = rng.normal(0, 1, int(SR * 0.01)) * 0.2
    out[: strike.size] += strike
    return out * vel


# ------------------------------------------------------------------ сведение --
def make_reverb_ir(sec=1.3):
    n = int(SR * sec)
    ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / (SR * 0.42))
    # слегка «тёмная» IR
    x = np.fft.rfft(ir)
    fr = np.fft.rfftfreq(n, 1 / SR)
    x *= 1.0 / (1.0 + (fr / 4200.0) ** 2)
    ir = np.fft.irfft(x, n)
    return ir / np.abs(ir).max()


IR_L = make_reverb_ir()
IR_R = make_reverb_ir()


def convolve_rev(sig, ir, mix=0.26):
    n = sig.size + ir.size - 1
    S = np.fft.rfft(sig, n)
    I = np.fft.rfft(ir, n)
    wet = np.fft.irfft(S * I, n)[: sig.size]
    return sig * (1 - mix * 0.5) + wet * mix


def render(events, seconds, rev=0.26, master=0.86):
    n = int(SR * seconds)
    L = np.zeros(n)
    R = np.zeros(n)
    for ev in events:
        t0 = int(ev["t"] * SR)
        kind = ev["inst"]
        if kind == "piano":
            s = piano(ev["m"], ev["d"], ev.get("v", 0.8))
        elif kind == "guitar":
            s = guitar(ev["m"], ev["d"], ev.get("v", 0.7))
        elif kind == "pad":
            s = pad(ev["m"], ev["d"], ev.get("v", 0.35))
        elif kind == "box":
            s = box(ev["m"], ev["d"], ev.get("v", 0.6))
        elif kind == "bass":
            s = bass(ev["m"], ev["d"], ev.get("v", 0.5))
        elif kind == "brush":
            s = brush(ev.get("d", 0.25), ev.get("v", 0.25))
        elif kind == "bell":
            s = bell(ev.get("d", 6.0), ev.get("v", 0.5), hz(ev.get("m", 57)))
        else:
            continue
        if s.size + t0 > n:
            s = s[: n - t0]
        if s.size == 0:
            continue
        pan = ev.get("pan", 0.0)
        gl = np.cos((pan + 1) * np.pi / 4)
        gr = np.sin((pan + 1) * np.pi / 4)
        L[t0: t0 + s.size] += s * gl
        R[t0: t0 + s.size] += s * gr
    L = convolve_rev(L, IR_L, rev)
    R = convolve_rev(R, IR_R, rev)
    peak = max(np.abs(L).max(), np.abs(R).max()) + 1e-9
    L = L / peak * master
    R = R / peak * master
    # мягкий лимитер
    L = np.tanh(L * 1.1) / np.tanh(1.1)
    R = np.tanh(R * 1.1) / np.tanh(1.1)
    # бесшовная петля: хвост кроссфейдом подмешивается в голову,
    # поэтому на стыке лупа нет ни щелчка, ни провала в тишину
    X = int(SR * 1.8)
    if n > 3 * X:
        ramp = np.linspace(0.0, 1.0, X)
        Lh = L[:X] * ramp + L[n - X:n] * (1.0 - ramp)
        Rh = R[:X] * ramp + R[n - X:n] * (1.0 - ramp)
        L = np.concatenate([Lh, L[X:n - X]])
        R = np.concatenate([Rh, R[X:n - X]])
    return np.stack([L, R], axis=1)


def ev(t, d, m, inst, v=0.8, pan=0.0):
    return {"t": t, "d": d, "m": m, "inst": inst, "v": v, "pan": pan}


def chord_events(t, midis, dur, inst, v=0.3, spread=0.5):
    out = []
    for i, m in enumerate(midis):
        out.append(ev(t + i * 0.012, dur, m, inst, v, pan=-spread + i * (2 * spread / max(1, len(midis) - 1))))
    return out


# мотив M («билет»): D F# A G | F# E D
MOTIF_M = [74, 78, 81, 79, 78, 76, 74]
# мотив L («фонарь»): нисходящий полутон-вздох A G# A E
MOTIF_L = [81, 80, 81, 76]
# мотив Z («карандаш»): F# E C# D (минорная колыбельная)
MOTIF_Z = [78, 76, 73, 74]


def build_main_theme():
    bpm = 92.0
    spb = 60.0 / bpm
    E = []
    prog = [[38, 45, 50, 54], [36, 43, 48, 52], [40, 47, 52, 56], [38, 45, 50, 54]]  # Dm-подобный тепло: Bb F Gm D
    chords = [[50, 54, 57, 62], [48, 52, 55, 60], [43, 50, 55, 59], [50, 54, 57, 62]]
    bar = 4 * spb
    # A: мотив M на рояле + пад
    for rep in range(2):
        base = rep * 8 * bar
        for b in range(8):
            E += chord_events(base + b * bar, chords[b % 4], bar * 1.05, "pad", 0.22)
            E.append(ev(base + b * bar, bar, prog[b % 4][0], "bass", 0.42))
        mel = [(0, 2, 74), (2, 1, 78), (3, 1, 81), (4, 2, 79), (6, 1, 78), (7, 1, 76), (8, 4, 74)]
        mel2 = [(0, 2, 74), (2, 1, 78), (3, 1, 81), (4, 2, 83), (6, 2, 81), (8, 2, 79), (10, 2, 78), (12, 4, 76)]
        seq = mel if rep == 0 else mel2
        for (b, d, m) in seq:
            E.append(ev(base + b * spb, d * spb * 0.95, m, "piano", 0.75, pan=-0.15))
        # шкатулка-контрмотив во втором проведении
        if rep == 1:
            for (b, d, m) in [(5, 1, 86), (6, 1, 85), (7, 1, 83), (11, 1, 86), (12, 1, 83), (13, 1, 81)]:
                E.append(ev(base + b * spb, d * spb, m, "box", 0.35, pan=0.4))
        for b in range(0, 8, 1):
            E.append(ev(base + b * bar + 2 * spb, 0.2, 0, "brush", 0.16, pan=0.2))
            E.append(ev(base + b * bar + 3.5 * spb, 0.2, 0, "brush", 0.12, pan=0.2))
    # кода: мотив M на шкатулке + колокол
    coda = 16 * bar
    for i, m in enumerate(MOTIF_M):
        E.append(ev(coda + i * spb, spb * 1.4, m + 12, "box", 0.4, pan=0.1))
    E.append(ev(coda, 6.0, 50, "bell", 0.3))
    return E, 16 * bar + 8 * spb + 4.0


def build_camp_day():
    bpm = 98.0
    spb = 60.0 / bpm
    bar = 4 * spb
    E = []
    chords = [[43, 50, 55, 59], [45, 52, 57, 60], [38, 50, 55, 62], [43, 50, 55, 59]]
    bars = 16
    for b in range(bars):
        ch = chords[b % 4]
        t0 = b * bar
        # гитарный бой: бас + аккорд
        E.append(ev(t0, bar, ch[0] - 12, "guitar", 0.6, pan=-0.3))
        for strt in (1.0, 2.0, 2.5, 3.0, 3.5):
            E += chord_events(t0 + strt * spb, ch[1:], spb * 0.9, "guitar", 0.22, spread=0.45)
        E.append(ev(t0 + 2 * spb, 0.2, 0, "brush", 0.18, pan=0.25))
        E.append(ev(t0 + 3.5 * spb, 0.2, 0, "brush", 0.13, pan=0.25))
    mel = [(0, 1, 71), (1, 1, 74), (2, 2, 76), (4, 1, 74), (5, 1, 71), (6, 2, 69),
           (8, 1, 71), (9, 1, 74), (10, 2, 76), (12, 2, 78), (14, 2, 76),
           (16, 1, 79), (17, 1, 78), (18, 2, 76), (20, 2, 74), (22, 2, 71),
           (24, 1, 71), (25, 1, 74), (26, 2, 76), (28, 2, 79), (30, 4, 74)]
    for (b, d, m) in mel:
        E.append(ev(b * spb, d * spb * 0.9, m, "box", 0.5, pan=0.15))
    for b in range(0, bars, 2):
        E.append(ev(b * bar + 3.5 * spb, spb, chords[b % 4][2] + 12, "piano", 0.3, pan=0.35))
    return E, bars * bar + 3.0


def build_lena_theme():
    bpm = 68.0
    spb = 60.0 / bpm
    bar = 4 * spb
    E = []
    chords = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [45, 52, 57, 64]]
    bars = 12
    for b in range(bars):
        E += chord_events(b * bar, chords[b % 4], bar * 1.2, "pad", 0.2)
        E.append(ev(b * bar, bar * 0.9, chords[b % 4][0] - 12, "bass", 0.35))
    mel = [(0, 3, 81), (3, 1, 80), (4, 3, 81), (7, 1, 76), (8, 4, 78), (12, 3, 85), (15, 1, 84),
           (16, 3, 81), (19, 1, 80), (20, 4, 76), (24, 3, 73), (27, 1, 74), (28, 6, 76)]
    for (b, d, m) in mel:
        E.append(ev(b * spb, d * spb * 0.95, m, "piano", 0.7, pan=-0.1))
    # мотив L на шкатулке в середине
    for i, m in enumerate(MOTIF_L):
        E.append(ev(6 * bar + i * 2 * spb, 2 * spb, m + 12, "box", 0.32, pan=0.35))
    for b in range(bars):
        if b % 4 == 3:
            E.append(ev(b * bar, 5.0, 69, "bell", 0.18, ))
    return E, bars * bar + 4.0


def build_vera_theme():
    bpm = 104.0
    spb = 60.0 / bpm
    bar = 4 * spb
    E = []
    chords = [[40, 47, 52, 56], [45, 52, 56, 59], [42, 49, 54, 57], [47, 54, 59, 62]]
    bars = 16
    for b in range(bars):
        ch = chords[b % 4]
        t0 = b * bar
        E.append(ev(t0, bar * 0.9, ch[0] - 12, "bass", 0.5))
        E.append(ev(t0 + 2 * spb, bar * 0.5, ch[0] - 12, "bass", 0.4))
        for strt in (0.0, 0.75, 1.5, 2.0, 2.75, 3.5):
            E += chord_events(t0 + strt * spb, ch[1:], spb * 0.5, "guitar", 0.2, spread=0.4)
        E.append(ev(t0 + 1 * spb, 0.18, 0, "brush", 0.2, pan=0.3))
        E.append(ev(t0 + 3 * spb, 0.18, 0, "brush", 0.2, pan=0.3))
        E.append(ev(t0 + 3.5 * spb, 0.18, 0, "brush", 0.14, pan=0.3))
    riff = [(0, 1, 76), (1, 1, 76), (2, 0.5, 78), (2.5, 0.5, 76), (3, 1, 71),
            (4, 1, 76), (5, 1, 78), (6, 2, 81), (8, 1, 79), (9, 1, 78), (10, 1, 76), (11, 1, 73), (12, 4, 71)]
    for rep in (0, 8):
        for (b, d, m) in riff:
            E.append(ev((rep + b) * spb, d * spb * 0.9, m, "piano", 0.55, pan=0.1))
    for i, m in enumerate([76, 79, 81, 83]):
        E.append(ev(14 * bar + i * spb, spb * 1.5, m, "box", 0.3, pan=0.3))
    return E, bars * bar + 3.0


def build_zoya_theme():
    bpm = 62.0
    spb = 60.0 / bpm
    bar = 4 * spb
    E = []
    chords = [[42, 49, 54, 57], [45, 52, 56, 59], [38, 45, 50, 54], [42, 49, 54, 57]]
    bars = 12
    for b in range(bars):
        E += chord_events(b * bar, chords[b % 4], bar * 1.25, "pad", 0.16)
        E.append(ev(b * bar, bar * 0.9, chords[b % 4][0] - 12, "bass", 0.3))
    mel = [(0, 2, 78), (2, 2, 76), (4, 2, 73), (6, 2, 74), (8, 3, 78), (11, 1, 81), (12, 4, 76),
           (16, 2, 73), (18, 2, 74), (20, 3, 76), (23, 1, 78), (24, 6, 71)]
    for (b, d, m) in mel:
        E.append(ev(b * spb, d * spb * 0.95, m, "box", 0.5, pan=0.05))
    for (b, d, m) in [(2, 2, 54), (6, 2, 55), (10, 2, 50), (14, 2, 54), (18, 2, 50), (22, 2, 55)]:
        E.append(ev(b * spb, d * spb, m + 12, "piano", 0.3, pan=-0.3))
    for i, m in enumerate(MOTIF_Z):
        E.append(ev(9 * bar + i * spb, spb * 1.6, m, "piano", 0.45, pan=-0.1))
    return E, bars * bar + 4.0


def build_mystery():
    bpm = 56.0
    spb = 60.0 / bpm
    E = []
    sec = 78.0
    # дрон D2 с медленным биением
    for det in (-0.06, 0.06):
        E.append({"t": 0.0, "d": sec - 4, "m": 38, "inst": "pad", "v": 0.3, "pan": det * 4})
    frags = [(6, MOTIF_M[:3]), (16, MOTIF_L), (28, MOTIF_Z[:3]), (40, MOTIF_M[3:]), (54, MOTIF_L)]
    for t0, frag in frags:
        for i, m in enumerate(frag):
            E.append(ev(t0 + i * spb * 1.5, spb * 2, m, "box", 0.3, pan=rng.uniform(-0.5, 0.5)))
    for t0 in (12, 34, 50, 66):
        E.append(ev(t0, 7.0, 50, "bell", 0.22))
    for t0 in (20, 44):
        E.append(ev(t0, 0.4, 0, "brush", 0.1, pan=0.4))
    return E, sec


def build_finale():
    bpm = 84.0
    spb = 60.0 / bpm
    bar = 4 * spb
    E = []
    chords = [[50, 57, 62, 66], [45, 52, 57, 64], [43, 50, 55, 62], [50, 57, 62, 69]]
    bars = 20
    for b in range(bars):
        ch = chords[b % 4]
        E += chord_events(b * bar, ch, bar * 1.1, "pad", 0.16 + 0.012 * b)
        E.append(ev(b * bar, bar * 0.9, ch[0] - 12, "bass", 0.4))
        if b >= 4:
            E.append(ev(b * bar + 2 * spb, 0.2, 0, "brush", 0.15, pan=0.25))
    # мотив M в увеличении (удвоение длительностей) на рояле
    seq = [(0, 4, 74), (4, 2, 78), (6, 2, 81), (8, 4, 79), (12, 2, 78), (14, 2, 76), (16, 8, 74)]
    for (b, d, m) in seq:
        E.append(ev(b * spb, d * spb * 0.95, m, "piano", 0.72, pan=-0.1))
    seq2 = [(24, 4, 74), (28, 2, 78), (30, 2, 81), (32, 4, 83), (36, 4, 81), (40, 4, 79), (44, 4, 78), (48, 8, 76)]
    for (b, d, m) in seq2:
        E.append(ev(b * spb, d * spb * 0.95, m, "piano", 0.75, pan=-0.1))
        E.append(ev(b * spb, d * spb * 0.95, m + 12, "box", 0.22, pan=0.35))
    for t0 in (0, 8 * bar, 16 * bar):
        E.append(ev(t0, 7.0, 50, "bell", 0.26))
    return E, bars * bar + 5.0


def build_forgotten():
    sec = 74.0
    E = []
    E.append({"t": 0.0, "d": sec - 6, "m": 38, "inst": "pad", "v": 0.26, "pan": -0.2})
    E.append({"t": 0.0, "d": sec - 6, "m": 41, "inst": "pad", "v": 0.18, "pan": 0.25})
    t = 4.0
    while t < sec - 10:
        E.append(ev(t, 3.0, 62, "piano", 0.3 + rng.uniform(-0.05, 0.05), pan=rng.uniform(-0.15, 0.15)))
        t += rng.uniform(5.5, 8.0)
    for t0 in (18, 42, 60):
        E.append(ev(t0, 6.0, 50, "bell", 0.12))
    return E, sec


def build_farewell():
    bpm = 76.0
    spb = 60.0 / bpm
    bar = 4 * spb
    E = []
    chords = [[36, 43, 48, 52], [41, 48, 52, 55], [38, 45, 50, 53], [36, 43, 48, 55]]
    bars = 16
    for b in range(bars):
        ch = chords[b % 4]
        t0 = b * bar
        for i, m in enumerate(ch):
            E.append(ev(t0 + i * spb, spb * 3.4, m, "guitar", 0.32, pan=-0.35 + i * 0.12))
        E.append(ev(t0, bar * 0.9, ch[0] - 12, "bass", 0.32))
    # мотив M в половинном темпе, контр-голос рояля
    half = [(0, 4, 74), (4, 2, 78), (6, 2, 81), (8, 4, 79), (12, 4, 74)]
    for (b, d, m) in half:
        E.append(ev((b * 2) * spb, d * 2 * spb * 0.9, m, "piano", 0.6, pan=0.05))
    for (b, m) in [(10, 79), (14, 76), (22, 79), (26, 81), (30, 76)]:
        E.append(ev(b * spb, 2 * spb, m + 12, "box", 0.28, pan=0.35))
    E.append(ev(0, 6.0, 48, "bell", 0.16))
    return E, bars * bar + 4.0


TRACKS = [
    ("main_theme", build_main_theme),
    ("camp_day", build_camp_day),
    ("lena_theme", build_lena_theme),
    ("vera_theme", build_vera_theme),
    ("zoya_theme", build_zoya_theme),
    ("mystery", build_mystery),
    ("finale", build_finale),
    ("forgotten_theme", build_forgotten),
    ("farewell_theme", build_farewell),
]


def write_ogg(path, audio, sr, chunk_sec=5):
    """Потоковая запись: обходим сегфолт libsndfile на больших однокарсовых блоках."""
    audio = np.ascontiguousarray(audio, dtype=np.float32)
    with sf.SoundFile(path, "w", sr, audio.shape[1], format="OGG", subtype="VORBIS") as f:
        step = int(sr * chunk_sec)
        for i in range(0, audio.shape[0], step):
            f.write(audio[i:i + step])


def to_web_version(audio, sr=32000):
    """Моно-версия пониженной частоты для web-сборки (меньше вес)."""
    mono = audio.mean(axis=1)
    idx = np.linspace(0, mono.size - 1, int(mono.size * sr / SR))
    return np.stack([np.interp(idx, np.arange(mono.size), mono)], axis=1)


def main():
    os.makedirs(GAME_AUDIO, exist_ok=True)
    os.makedirs(WEB_AUDIO, exist_ok=True)
    for name, builder in TRACKS:
        events, seconds = builder()
        audio = render(events, seconds)
        write_ogg(os.path.join(GAME_AUDIO, name + ".ogg"), audio, SR)
        write_ogg(os.path.join(WEB_AUDIO, name + ".ogg"), to_web_version(audio), 32000)
        kb = os.path.getsize(os.path.join(GAME_AUDIO, name + ".ogg")) // 1024
        wkb = os.path.getsize(os.path.join(WEB_AUDIO, name + ".ogg")) // 1024
        print(f"✓ {name}: {seconds:.0f} c, {len(events)} событий, game {kb} KB / web {wkb} KB")


if __name__ == "__main__":
    main()
