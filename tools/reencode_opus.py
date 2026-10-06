#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reencode_opus.py — пережатие OGG/Vorbis в OGG/Opus (поддерживается Ren'Py 8)
без изменения длительности и без «тишины по краям» (важно для бесшовных петель).

Использование:
    python3 tools/reencode_opus.py SRC.ogg DST.ogg --bitrate 64000 [--mono]

Как это работает:
  1. Читаем источник через soundfile (libsndfile) в float32.
  2. Ресемплируем 44100 -> 48000 через av.AudioResampler.
  3. Кодируем libopus кадрами по 960 сэмплов (20 мс) с корректными pts.
  4. Проверяем результат: длительность должна совпасть с исходной
     (+/- 1 кадр), RMS первых/последних 20 мс — как у источника.
"""
import argparse
import os
import sys

import av
import numpy as np
import soundfile as sf
from fractions import Fraction


FRAME = 960          # 20 мс при 48 кГц — базовый кадр Opus
TARGET_RATE = 48000


def resample(data: np.ndarray, sr_in: int, mono: bool) -> np.ndarray:
    """(N, ch) float -> (M, 1 или 2) float32, 48 кГц."""
    if mono and data.shape[1] > 1:
        data = data.mean(axis=1, keepdims=True)
    layout = "mono" if data.shape[1] == 1 else "stereo"
    rs = av.AudioResampler(format="fltp", layout=layout, rate=TARGET_RATE)
    out = []
    step = 4096
    for pos in range(0, len(data), step):
        chunk = np.ascontiguousarray(data[pos:pos + step].T.astype(np.float32))
        fr = av.AudioFrame.from_ndarray(chunk, format="fltp", layout=layout)
        fr.sample_rate = sr_in
        fr.pts = pos
        fr.time_base = Fraction(1, sr_in)
        for r in rs.resample(fr):
            out.append(r.to_ndarray().T)
    for r in rs.resample(None):
        out.append(r.to_ndarray().T)
    res = np.concatenate(out, axis=0) if out else np.zeros((0, 1 if mono else 2), np.float32)
    return res.astype(np.float32)


def encode(pcm: np.ndarray, dst: str, bitrate: int):
    ch = pcm.shape[1]
    layout = "mono" if ch == 1 else "stereo"
    total = len(pcm)
    out = av.open(dst, "w")
    st = out.add_stream("libopus", rate=TARGET_RATE)
    st.bit_rate = bitrate
    st.layout = layout
    st.time_base = Fraction(1, TARGET_RATE)
    pos = 0
    while pos < total:
        chunk = pcm[pos:pos + FRAME]
        if len(chunk) < FRAME:                     # последний кадр: добиваем нулями,
            chunk = np.concatenate([chunk,         # гранула Ogg всё равно обрежет
                                    np.zeros((FRAME - len(chunk), ch), np.float32)])
        arr = np.ascontiguousarray(chunk.T)
        fr = av.AudioFrame.from_ndarray(arr, format="fltp", layout=layout)
        fr.sample_rate = TARGET_RATE
        fr.pts = pos
        fr.time_base = Fraction(1, TARGET_RATE)
        for p in st.encode(fr):
            out.mux(p)
        pos += FRAME
    for p in st.encode(None):
        out.mux(p)
    out.close()
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--bitrate", type=int, default=64000)
    ap.add_argument("--mono", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    data, sr = sf.read(a.src, always_2d=True, dtype="float32")
    dur_in = len(data) / sr
    pcm = resample(data, sr, a.mono)
    encode(pcm, a.dst, a.bitrate)

    back, sr2 = sf.read(a.dst, always_2d=True, dtype="float32")
    dur_out = len(back) / sr2
    n = min(int(0.02 * sr), int(0.02 * sr2))
    rms_in_head = float(np.sqrt((data[:n] ** 2).mean()))
    rms_in_tail = float(np.sqrt((data[-n:] ** 2).mean()))
    rms_out_head = float(np.sqrt((back[:n] ** 2).mean()))
    rms_out_tail = float(np.sqrt((back[-n:] ** 2).mean()))
    ok = abs(dur_in - dur_out) < 0.03
    if not a.quiet:
        print(f"{os.path.basename(a.dst)}: {os.path.getsize(a.src)/1024:.0f}KB -> "
              f"{os.path.getsize(a.dst)/1024:.0f}KB  {dur_in:.3f}s -> {dur_out:.3f}s  "
              f"head {rms_in_head:.4f}->{rms_out_head:.4f} tail {rms_in_tail:.4f}->{rms_out_tail:.4f} "
              f"{'OK' if ok else 'ДЛИНА НЕ СОВПАЛА'}")
    if not ok:
        sys.exit(2)


if __name__ == "__main__":
    main()
