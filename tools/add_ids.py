#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_ids.py — проставляет явные переводческие id во все реплики и пункты меню.

После прогона каждая реплика выглядит так:
    mc "Текст." id p01_room_0007
а пункт меню так:
    "Осмотреть билет внимательно" id p01_room_m1:

Это нужно двум потребителям:
  1. Ren'Py: game/tl/english/*.tl использует `translate english <id>:`;
  2. web-движок: tools/export_web.py мапит id на английский текст.

Запуск: python3 tools/add_ids.py   (идемпотентно: строки с id не трогает)
"""

import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
FILES = ["script.rpy"] + [os.path.join("scenes", f) for f in sorted(os.listdir(os.path.join(GAME, "scenes"))) if f.endswith(".rpy")]

label_re = re.compile(r"^\s*label\s+([\w]+)")
say_re = re.compile(r'^(?P<ind>\s*)(?:(?P<who>mc|lena|vera|zoya|radio|child|young_voice|voice|lena_e|card|narrator)\s+)?"(?P<text>.*)"\s*$')
menu_item_re = re.compile(r'^(?P<ind>\s*)"(?P<text>[^"]*)"(?P<cond>\s+if\s+.+?)?\s*:\s*$')

total = 0
for rel in FILES:
    path = os.path.join(GAME, rel)
    lines = open(path, encoding="utf-8").read().split("\n")
    cur_label = None
    n = 0
    m = 0
    out = []
    for line in lines:
        lm = label_re.match(line)
        if lm:
            cur_label = lm.group(1)
            n = 0
            m = 0
            out.append(line)
            continue
        if line.strip().startswith("#"):
            out.append(line)
            continue
        sm = say_re.match(line)
        if sm and " id " not in line:
            n += 1
            out.append(f'{line.rstrip()} id {cur_label}_{n:04d}')
            total += 1
            continue
        ## Пункты меню НЕ получают id: Ren'Py 8.5 не поддерживает id на пунктах меню.
        ## Их перевод идёт через блок `translate english strings:` (см. gen_tl.py).
        out.append(line)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print(f"{rel}: +id")

print(f"Всего помечено строк: {total}")
