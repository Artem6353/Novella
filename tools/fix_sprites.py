#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_sprites.py — лечение и нормализация спрайтов (ТЗ v2.0, задача 11).

Что делает (по пунктам ТЗ):
  11.1  все спрайты приводятся к высоте 840 px с якорем по НИЖНЕЙ границе
        фигуры (ноги/бёдра): сначала обрезка по альфа-bbox, затем
        масштабирование — после этого смена эмоции не даёт «прыжков»;
  11.4  чистый альфа-канал:
        * дыры внутри фигуры (следы хромокея) закрываются морфологически,
          цвет в дырах восстанавливается итеративным заполнением от
          соседей (inpaint);
        * белые непрозрачные «точки» (протравленный хромокей) детектируются
          как светлые пиксели в небелом окружении и также_inpaint_ятся;
        * мелкий мусор вне фигуры (компоненты < 60 px) удаляется;
  11.2  опционально: хромокей нового файла vera_excited с мадженты
        (--key-from work_art/vera_excited_raw.png).

Побочные продукты: GIF-доказательства sprite_proof_<имя>.gif (смена эмоций
без рывков) и таблица «было/стало» в stdout.

Запуск:
    python3 tools/fix_sprites.py                 # лечение + нормализация
    python3 tools/fix_sprites.py --key-vera      # сначала хромокей vera_excited
Оригиналы до правки складываются в /tmp/sprites_orig/ (для до/после).
"""
import os
import shutil
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
IMG = os.path.join(ROOT, "renpy_project", "game", "images")
BACKUP = "/tmp/sprites_orig"
TARGET_H = 840
MIN_COMPONENT = 60


def load(path):
    im = Image.open(path).convert("RGBA")
    return np.array(im)


def save(path, arr):
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(path, optimize=True)


def components(mask, min_area):
    """Маска, в которой остались только компоненты площадью >= min_area."""
    lab = np.zeros(mask.shape, np.int32)
    cur = 0
    h, w = mask.shape
    keep = np.zeros(mask.shape, bool)
    for i in range(h):
        for j in range(w):
            if mask[i, j] and lab[i, j] == 0:
                cur += 1
                q = deque([(i, j)])
                lab[i, j] = cur
                pix = []
                while q:
                    y, x = q.popleft()
                    pix.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            q.append((ny, nx))
                if len(pix) >= min_area:
                    for y, x in pix:
                        keep[y, x] = True
    return keep


def holes_of(mask):
    """Внутренние дыры: недостижимые из-за границы участки фона."""
    h, w = mask.shape
    free = ~mask
    seen = np.zeros_like(free)
    q = deque()
    for j in range(w):
        for i in (0, h - 1):
            if free[i, j] and not seen[i, j]:
                seen[i, j] = True
                q.append((i, j))
    for i in range(h):
        for j in (0, w - 1):
            if free[i, j] and not seen[i, j]:
                seen[i, j] = True
                q.append((i, j))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and free[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return free & ~seen


def inpaint(rgb, fill):
    """Итеративно залить пиксели `fill` цветом соседей."""
    col = rgb.astype(np.float32)
    known = ~fill
    for _ in range(60):
        if not fill.any():
            break
        acc = np.zeros_like(col)
        cnt = np.zeros(fill.shape, np.float32)
        known_f = known.astype(np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            acc += np.roll(np.roll(col * known_f[..., None], dy, 0), dx, 1)
            cnt += np.roll(np.roll(known_f, dy, 0), dx, 1)
        take = fill & (cnt > 0)
        if not take.any():
            break
        col[take] = acc[take] / cnt[take][..., None]
        known |= take
        fill = fill & ~take
    return col


def white_specks(arr):
    """Белые точки: светлые непрозрачные пиксели в преимущественно тёмном/цветном окружении."""
    rgb = arr[..., :3].astype(np.int16)
    a = arr[..., 3]
    white = (rgb.min(axis=2) > 225) & (a > 0)
    wm = Image.fromarray((white * 255).astype(np.uint8), "L").filter(
        __import__("PIL.ImageFilter", fromlist=["BoxBlur"]).BoxBlur(3))
    density = np.array(wm, np.float32) / 255.0
    return white & (density < 0.75)


def chroma_key(arr, thresh=90, feather=40):
    bg = np.median(np.stack([
        arr[0, 0, :3], arr[0, -1, :3], arr[-1, 0, :3], arr[-1, -1, :3]
    ]).astype(np.float32), axis=0)
    rgb = arr[..., :3].astype(np.float32)
    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))
    alpha = arr[..., 3].astype(np.float32)
    alpha[dist < thresh] = 0
    zone = (dist >= thresh) & (dist < thresh + feather)
    alpha[zone] *= (dist[zone] - thresh) / feather
    arr = arr.copy()
    arr[..., 3] = alpha
    return arr


def process(path, key=False):
    arr = load(path)
    if key:
        arr = chroma_key(arr)
    a = arr[..., 3]
    mask = a >= 128
    mask = components(mask, MIN_COMPONENT)
    hol = holes_of(mask)
    n_fill = int(hol.sum())
    if hol.any():
        arr[..., :3] = np.clip(inpaint(arr[..., :3], hol), 0, 255).astype(np.uint8)
        arr[..., 3][hol] = 255
    ## белые точки снимаем в несколько проходов: после inpaint соседние
    ## точки перестают поддерживать друг друга в «белом большинстве»
    for _ in range(3):
        sp = white_specks(arr) & mask
        if not sp.any():
            break
        n_fill += int(sp.sum())
        arr[..., :3] = np.clip(inpaint(arr[..., :3], sp), 0, 255).astype(np.uint8)
        arr[..., 3][sp] = 255
    fill = hol
    new_a = arr[..., 3].copy()
    new_a[fill] = 255
    ## полупрозрачную обводку (антиалиасинг) оставляем только там, где она
    ## прилегает к фигуре; ореолы от удалённого мусора гасим
    dil = mask.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        dil |= np.roll(np.roll(mask, dy, 0), dx, 1)
    fringe = (~mask) & (~fill) & (arr[..., 3] > 0) & (arr[..., 3] < 128) & dil
    new_a[~mask & ~fill] = 0
    new_a[fringe] = arr[..., 3][fringe]
    arr[..., 3] = new_a
    # обрезка по bbox и нормализация высоты
    ys, xs = np.where(arr[..., 3] > 0)
    arr = arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = arr.shape[:2]
    if h != TARGET_H:
        nw = max(1, int(round(w * TARGET_H / h)))
        arr = np.array(Image.fromarray(arr, "RGBA").resize((nw, TARGET_H), Image.LANCZOS))
    return arr, n_fill


def main():
    key_vera = "--key-vera" in sys.argv
    os.makedirs(BACKUP, exist_ok=True)
    files = sorted(f for f in os.listdir(IMG)
                   if f.endswith(".png") and not f.startswith(("bg_", "cg_")))
    print(f"{'файл':22}{'было':>12}{'стало':>12}{'закрыто дыр':>13}")
    for f in files:
        p = os.path.join(IMG, f)
        bak = os.path.join(BACKUP, f)
        if not os.path.exists(bak):
            shutil.copyfile(p, bak)
        key = key_vera and f == "vera_excited.png"
        if key:
            raw = os.path.join(ROOT, "work_art", "vera_excited_raw.png")
            if os.path.exists(raw):
                shutil.copyfile(raw, p)
        old = Image.open(p if not key else p)
        ow, oh = old.size
        arr, n = process(p, key=key)
        save(p, arr)
        print(f"{f:22}{ow:>5}x{oh:<5}{arr.shape[1]:>5}x{arr.shape[0]:<5}{n:>10}")

    # GIF-доказательство: смена эмоций без рывков
    for who in ("lena", "vera", "zoya"):
        names = [f for f in files if f.startswith(who)]
        if not names:
            continue
        frames = []
        for f in names:
            im = Image.open(os.path.join(IMG, f)).convert("RGBA")
            bg = Image.new("RGBA", (560, 880), (27, 43, 35, 255))
            bg.paste(im, ((560 - im.width) // 2, 880 - im.height), im)
            frames.append(bg.convert("P", palette=Image.ADAPTIVE))
        out = os.path.join(ROOT, "..", f"sprite_proof_{who}.gif")
        frames[0].save(out, save_all=True, append_images=frames[1:],
                       duration=650, loop=0)
        print("GIF: %s (%d кадров)" % (os.path.normpath(out), len(frames)))


if __name__ == "__main__":
    main()
