#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_tl.py — собирает game/tl/english/game.rpy (Ren'Py).

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

Источники:
  * реплики сцен        — tools/translations.py (ключи = id из add_ids.py);
  * пункты меню         — tools/menu_captions.py + tools/translations.py;
  * ВЕСЬ остальной UI   — tools/ui_strings.py (экранные строки, имена
    говорящих, карточки дней, названия концовок, «КОНЕЦ» и статистика).
    Этот же словарь кормит web-плеер (tools/build_web.py), поэтому переводы
    двух версий игры не могут разъехаться.

ЧТО ГЕНЕРАТОР ПРОВЕРЯЕТ (и падает с кодом 1 при провале):
  * в game/tl/ нет файлов, которые движок не загрузит (например .tl);
  * каждый переводческий id из translations.py существует в коде;
  * каждая реплика с id в коде имеет перевод;
  * каждая интерфейсная строка кода покрыта переводом:
      - литералы `_("...")`             (screens.rpy, options.rpy, script.rpy);
      - аргументы `call day_card(...)`  (карточки дней);
      - значения `$ ending_shown = ...` (названия концовок);
      - имена в `define ... = Character("...")`;
  * renpy_project/game/i18n.rpy синхронен с ui_strings.LAYOUT_PROMPTS.

Запуск: python3 tools/gen_tl.py
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
OUT = os.path.join(GAME, "tl", "english", "game.rpy")
I18N_RPY = os.path.join(GAME, "i18n.rpy")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations import TRANS  # noqa: E402
from menu_captions import MENU_CAPTIONS  # noqa: E402
from ui_strings import UI_STRINGS, LAYOUT_PROMPTS  # noqa: E402

say_re = re.compile(r'^\s*(?:(?P<who>\w+)\s+)?"(?P<text>.*)"\s+id\s+(?P<id>\w+)\s*$')
ui_literal_re = re.compile(r'_\(\s*"((?:[^"\\]|\\.)*)"\s*\)')
day_card_re = re.compile(r'^\s*call\s+day_card\((?P<args>[^)]*)\)')
ending_re = re.compile(r'^\s*\$\s*ending_shown\s*=\s*"(?P<text>[^"]*)"')
character_re = re.compile(r'^\s*define\s+\w+\s*=\s*Character\(\s*"(?P<name>[^"]*)"')
layout_re = re.compile(r'^\s*layout\.(?P<key>\w+)\s*=\s*"(?P<val>(?:[^"\\]|\\.)*)"')

# Строки, которые намеренно не переводятся: название языка принято
# показывать на самом этом языке.
NO_TRANSLATE_NEEDED = {"Русский", "English"}


def esc(s):
    """Экранирование для строки в двойных кавычках Ren'Py."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def unesc(s):
    """Обратная операция: текст из .rpy содержит escape-последовательности."""
    return s.replace('\\n', '\n').replace('\\"', '"').replace("\\\\", "\\")


errors = []

# ---------------------------------------------------------------------------
# 0. «Мёртвые» файлы переводов, которые движок физически не загружает
# ---------------------------------------------------------------------------
TL_DIR = os.path.join(GAME, "tl")
if os.path.isdir(TL_DIR):
    for dirpath, _, files in os.walk(TL_DIR):
        for fn in sorted(files):
            if not fn.endswith((".rpy", ".rpym", ".rpyc", ".rpymc")):
                errors.append(
                    "движок НЕ загрузит %s: Ren'Py читает из game/ только "
                    ".rpy/.rpym/.rpyc/.rpymc/*_ren.py (renpy/script.py::"
                    "scan_script_files). Переименуйте файл перевода в .rpy."
                    % os.path.relpath(os.path.join(dirpath, fn), ROOT))

# ---------------------------------------------------------------------------
# 1. Сканируем игру: реплики по id + все интерфейсные строки
# ---------------------------------------------------------------------------
found = {}    # id -> dict(who, text, path, line)
ui_used = {}  # русская строка -> "файл:строка"

rpy_files = []
for dirpath, dirnames, filenames in os.walk(GAME):
    if "tl" in dirpath.split(os.sep):
        dirnames[:] = []
        continue
    for fn in sorted(filenames):
        if fn.endswith(".rpy"):
            rpy_files.append(os.path.join(dirpath, fn))
rpy_files.sort()


def note(text, path, lineno):
    text = unesc(text)
    if not text:
        return
    ui_used.setdefault(text, "%s:%d" % (os.path.relpath(path, GAME), lineno))


for path in rpy_files:
    for lineno, line in enumerate(open(path, encoding="utf-8"), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue

        m = say_re.match(line)
        if m:
            found[m.group("id")] = {
                "who": m.group("who"),
                "text": m.group("text"),
                "path": os.path.relpath(path, GAME).replace(os.sep, "/"),
                "line": lineno,
            }

        for m in ui_literal_re.finditer(line):
            note(m.group(1), path, lineno)

        m = day_card_re.match(line)
        if m:
            for a in re.findall(r'"([^"]*)"', m.group("args")):
                note(a, path, lineno)

        m = ending_re.match(line)
        if m:
            note(m.group("text"), path, lineno)

        m = character_re.match(line)
        if m:
            note(m.group("name"), path, lineno)

# ---------------------------------------------------------------------------
# 2. Проверка: id из translations.py обязаны существовать в коде
# ---------------------------------------------------------------------------
for sid in TRANS:
    if sid in MENU_CAPTIONS:
        continue
    if sid not in found:
        errors.append("id из translations.py не найден в коде: %s "
                      "(перевод таких строк живёт в tools/ui_strings.py)" % sid)

# ---------------------------------------------------------------------------
# 3. Проверка: каждая реплика с id обязана иметь перевод
# ---------------------------------------------------------------------------
untranslated = []
for sid, info in found.items():
    if sid in MENU_CAPTIONS:
        continue
    if sid not in TRANS:
        untranslated.append("%s: %s" % (sid, info["text"][:60]))

# ---------------------------------------------------------------------------
# 4. Проверка покрытия интерфейсных строк
# ---------------------------------------------------------------------------
for ru, where in sorted(ui_used.items()):
    if ru in NO_TRANSLATE_NEEDED:
        continue
    if ru in UI_STRINGS:
        continue
    if ru in MENU_CAPTIONS.values():
        continue
    errors.append("интерфейсная строка без перевода (%s): %r" % (where, ru))

for ru in UI_STRINGS:
    if ru not in ui_used:
        errors.append("перевод в ui_strings.UI_STRINGS не используется кодом: %r" % ru)

# ---------------------------------------------------------------------------
# 5. Проверка синхронности i18n.rpy и LAYOUT_PROMPTS
# ---------------------------------------------------------------------------
blocks = {"None": {}, "english": {}}
current = None
if os.path.exists(I18N_RPY):
    for line in open(I18N_RPY, encoding="utf-8"):
        s = line.strip()
        if s.startswith("translate None python:"):
            current = "None"
            continue
        if s.startswith("translate english python:"):
            current = "english"
            continue
        if s.startswith("translate ") or s.startswith("label ") or s.startswith("screen "):
            current = None
            continue
        m = layout_re.match(line)
        if m and current:
            blocks[current][m.group("key")] = unesc(m.group("val"))
else:
    errors.append("не найден %s" % os.path.relpath(I18N_RPY, ROOT))

for key, (ru, en) in LAYOUT_PROMPTS.items():
    if blocks["None"].get(key) != ru:
        errors.append("i18n.rpy: layout.%s (ru) расходится с ui_strings.LAYOUT_PROMPTS" % key)
    if blocks["english"].get(key) != en:
        errors.append("i18n.rpy: layout.%s (en) расходится с ui_strings.LAYOUT_PROMPTS" % key)
for lang in blocks:
    for key in blocks[lang]:
        if key not in LAYOUT_PROMPTS:
            errors.append("i18n.rpy: layout.%s (%s) отсутствует в ui_strings.LAYOUT_PROMPTS" % (key, lang))

# ---------------------------------------------------------------------------
# 6. Собираем game.rpy
# ---------------------------------------------------------------------------
os.makedirs(os.path.dirname(OUT), exist_ok=True)
out = []
out.append("## ============================================================")
out.append("## game.rpy — полная английская локализация")
out.append("## Сгенерировано tools/gen_tl.py из tools/translations.py")
out.append("## (реплики) и tools/ui_strings.py + tools/menu_captions.py")
out.append("## (пункты меню и весь интерфейс).")
out.append("## Покрытие: все сцены, все семь концовок, все экраны Ren'Py.")
out.append("## РУКАМИ НЕ ПРАВИТЬ — пересоберите: python3 tools/gen_tl.py")
out.append("## ============================================================")
out.append("")

## Диалоги: translate english <id>: <who> "<перевод>"
n = 0
for sid, en in TRANS.items():
    if sid in MENU_CAPTIONS:
        continue
    info = found.get(sid)
    if info is None:
        continue                      # ошибка уже зафиксирована выше
    who = info["who"]
    prefix = (who + " ") if who else ""
    out.append("# game/%s:%d" % (info["path"], info["line"]))
    out.append("translate english %s:" % sid)
    out.append("")
    out.append("    # %s\"%s\"" % (prefix, info["text"]))
    out.append("    %s\"%s\"" % (prefix, esc(en)))
    out.append("")
    n += 1

## Пункты меню и интерфейсные строки: блок strings (old/new без id).
## Ключи old обязаны быть уникальны — движок бросает исключение
## на повторе, поэтому дубликаты схлопываем (первое вхождение wins).
out.append("")
out.append("## ============================================================")
out.append("## Пункты меню и интерфейс: блок strings")
out.append("## (Ren'Py 8.5 не поддерживает id на пунктах меню; экранные")
out.append("##  строки, имена говорящих, карточки дней и названия концовок")
out.append("##  переводятся сопоставлением по точной русской строке)")
out.append("## ============================================================")
out.append("translate english strings:")
out.append("")

seen = {}
n_str = 0


def emit_pair(ru, en):
    global n_str
    if ru in seen:
        if seen[ru] != en:
            errors.append("конфликт перевода строки %r: %r vs %r — оставлен первый"
                          % (ru, seen[ru], en))
        return
    seen[ru] = en
    out.append('    old "%s"' % esc(ru))
    out.append('    new "%s"' % esc(en))
    out.append("")
    n_str += 1


for sid, ru in MENU_CAPTIONS.items():
    en = TRANS.get(sid)
    if not en:
        errors.append("нет перевода пункта меню: %s (%r)" % (sid, ru))
        continue
    emit_pair(ru, en)

for ru, en in UI_STRINGS.items():
    if ru in NO_TRANSLATE_NEEDED or ru == en:
        continue
    emit_pair(ru, en)

if untranslated:
    errors.append("реплик без перевода: %d (первые пять: %s)"
                  % (len(untranslated), "; ".join(untranslated[:5])))

if errors:
    print("ОШИБКИ ЛОКАЛИЗАЦИИ (%d):" % len(errors))
    for e in errors:
        print("  !! " + e)
    sys.exit(1)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Готово: %s" % os.path.relpath(OUT, ROOT))
print("Переведено: %d реплик по id + %d строк интерфейса/меню = %d"
      % (n, n_str, n + n_str))
print("Проверено интерфейсных строк в коде: %d" % len(ui_used))
print("Без перевода (останутся RU): 0")
