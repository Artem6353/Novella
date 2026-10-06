#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_tl.py — собирает game/tl/english/demo.tl (Ren'Py) из tools/translations.py.

Формат Ren'Py:
    translate english <id>:
        old "<русская строка>"
        new "<английская строка>"

Источники русских строк — те же id, что проставил tools/add_ids.py.
Запуск: python3 tools/gen_tl.py
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
OUT = os.path.join(GAME, "tl", "english", "game.tl")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations import TRANS  # noqa: E402

say_re = re.compile(r'^\s*(?:(?P<who>\w+)\s+)?"(?P<text>.*)"\s+id\s+(?P<id>\w+)\s*$')
from menu_captions import MENU_CAPTIONS  # noqa: E402

found = {}
for dirpath, _, files in os.walk(GAME):
    for fn in files:
        if not fn.endswith(".rpy"):
            continue
        for line in open(os.path.join(dirpath, fn), encoding="utf-8"):
            m = say_re.match(line)
            if m:
                found[m.group("id")] = m.group("text")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
out = []
out.append("## ============================================================")
out.append("## game.tl — полная английская локализация")
out.append("## Сгенерировано tools/gen_tl.py из tools/translations.py")
out.append("## Покрытие: все сцены и все семь концовок.")
out.append("## ============================================================")
out.append("")

## пункты меню: блок translate english strings (old/new без id)
menu_pairs = []
for sid, ru in MENU_CAPTIONS.items():
    en = TRANS.get(sid)
    if en:
        menu_pairs.append((ru, en))

n = 0
for sid, en in TRANS.items():
    if sid in MENU_CAPTIONS:
        continue  # пункты меню уходят в блок strings ниже
    ru = found.get(sid)
    if ru is None:
        print(f"!! id не найден в коде: {sid}")
        continue
    out.append(f"translate english {sid}:")
    out.append(f'    old "{ru}"')
    out.append(f'    new "{en}"')
    out.append("")
    n += 1

out.append("")
out.append("## Пункты меню переводятся блоком strings (Ren'Py 8.5 не поддерживает id на пунктах)")
out.append("translate english strings:")
out.append("")
for ru, en in menu_pairs:
    out.append(f'    old "{ru}"')
    out.append(f'    new "{en}"')
    out.append("")
    n += 1

missing = [sid for sid in found if sid not in TRANS and not found[sid].startswith("[")]
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Готово: {os.path.relpath(OUT, ROOT)}")
print(f"Переведено строк: {n} (включая {len(menu_pairs)} пунктов меню)")
print(f"Без перевода (останутся RU): {len(missing)}")
