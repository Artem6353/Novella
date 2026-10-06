#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_tl.py — собирает game/tl/english/game.rpy (Ren'Py) из tools/translations.py.

ВАЖНО про формат (Ren'Py 8.x):
  * Файл перевода обязан иметь расширение .rpy и лежать в game/tl/english/.
    Файлы .tl движок НЕ загружает (поддерживаются .rpy/.rpym/_ren.py) —
    локализация с .tl молча не работает.
  * Диалоговые блоки — это ПЕРЕВЕДЁННЫЕ РЕПЛИКИ (с тем же говорящим),
    а не пары old/new:
        translate english p01_room_0006:
            mc "Dad, did you really keep a walkie-talkie manual?"
    Пары old/new допустимы ТОЛЬКО внутри `translate english strings:` —
    в диалоговом блоке они превратились бы в реплики несуществующих
    персонажей old/new и уронили игру с NameError.
  * Внутри одного strings-блока ключ old обязан быть уникальным:
    повтор движок бросает как исключение при загрузке
    ("A translation for ... already exists").

Источники русских строк — те же id, что проставил tools/add_ids.py.
Запуск: python3 tools/gen_tl.py
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
OUT = os.path.join(GAME, "tl", "english", "game.rpy")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations import TRANS  # noqa: E402
from menu_captions import MENU_CAPTIONS  # noqa: E402

say_re = re.compile(r'^\s*(?:(?P<who>\w+)\s+)?"(?P<text>.*)"\s+id\s+(?P<id>\w+)\s*$')

found = {}   # id -> (who, ru_text)
for dirpath, dirnames, filenames in os.walk(GAME):
    if "tl" in dirpath.split(os.sep):
        dirnames[:] = []
        continue
    for fn in sorted(filenames):
        if not fn.endswith(".rpy"):
            continue
        for line in open(os.path.join(dirpath, fn), encoding="utf-8"):
            m = say_re.match(line)
            if m:
                found[m.group("id")] = (m.group("who"), m.group("text"))


def esc(s):
    """Экранирование для строки в двойных кавычках Ren'Py."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


os.makedirs(os.path.dirname(OUT), exist_ok=True)
out = []
out.append("## ============================================================")
out.append("## game.rpy — полная английская локализация")
out.append("## Сгенерировано tools/gen_tl.py из tools/translations.py")
out.append("## Покрытие: все сцены и все семь концовок.")
out.append("## Формат: переведённые реплики в translate-блоках + пункты")
out.append("## меню в блоке strings (см. docstring gen_tl.py).")
out.append("## ============================================================")
out.append("")

## ------------------------------------------------------------
## Диалоги: translate english <id>: <who> "<перевод>"
## ------------------------------------------------------------
n = 0
for sid, en in TRANS.items():
    if sid in MENU_CAPTIONS:
        continue  # пункты меню уходят в блок strings ниже
    if sid not in found:
        print(f"!! id не найден в коде: {sid}")
        continue
    who, ru = found[sid]
    out.append(f"translate english {sid}:")
    out.append(f'    ## {esc(ru)}')
    if who:
        out.append(f'    {who} "{esc(en)}"')
    else:
        out.append(f'    "{esc(en)}"')
    out.append("")
    n += 1

## ------------------------------------------------------------
## Пункты меню: блок translate english strings (old/new без id).
## Ключи old обязаны быть уникальны — движок бросает исключение
## на повторе, поэтому дубликаты схлопываем (первое вхождение wins).
## ------------------------------------------------------------
out.append("")
out.append("## Пункты меню переводятся блоком strings (Ren'Py 8.5 не поддерживает id на пунктах)")
out.append("translate english strings:")
out.append("")
seen = {}
menu_pairs = 0
for sid, ru in MENU_CAPTIONS.items():
    en = TRANS.get(sid)
    if not en:
        print(f"!! нет перевода пункта меню: {sid} ({ru!r})")
        continue
    if ru in seen:
        if seen[ru] != en:
            print(f"!! конфликт перевода строки {ru!r}: {seen[ru]!r} vs {en!r} — оставлен первый")
        continue
    seen[ru] = en
    out.append(f'    old "{esc(ru)}"')
    out.append(f'    new "{esc(en)}"')
    out.append("")
    menu_pairs += 1

missing = [sid for sid in found if sid not in TRANS and not found[sid][1].startswith("[")]
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Готово: {os.path.relpath(OUT, ROOT)}")
print(f"Переведено строк: {n + menu_pairs} (включая {menu_pairs} уникальных пунктов меню)")
print(f"Без перевода (останутся RU): {len(missing)}")
