#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_scenario_txt.py — собирает ВЕСЬ игровой текст новеллы в один .txt.

Источники: renpy_project/game/scenes/*.rpy (порядок файлов = порядок дней),
внутри файла — порядок меток и строк = порядок подачи в игре.
Ветки меню печатаются подряд с пометкой [ВЫБОР], концовки — блоками.

Запуск: python3 tools/export_scenario_txt.py [OUT]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "Лето_которого_не_было_сценарий.txt")

FILES = [
    "scenes/prologue.rpy",
    "scenes/day00.rpy",
    "scenes/day01.rpy",
    "scenes/day02.rpy",
    "scenes/day03.rpy",
    "scenes/day04.rpy",
    "scenes/day05.rpy",
    "scenes/endings.rpy",
]

# Заголовки частей (по файлам сцен)
DAY_TITLES = {
    "scenes/prologue.rpy": "ПРОЛОГ",
    "scenes/day00.rpy": "ДЕНЬ 0",
    "scenes/day01.rpy": "ДЕНЬ 1",
    "scenes/day02.rpy": "ДЕНЬ 2 — «Трещины»",
    "scenes/day03.rpy": "ДЕНЬ 3 — «Разделение»",
    "scenes/day04.rpy": "ДЕНЬ 4 — «Правда»",
    "scenes/day05.rpy": "ДЕНЬ 5 — «Последний рассвет»",
    "scenes/endings.rpy": "КОНЦОВКИ (все семь)",
}

# какие строки комментариев сцены считаем паспортом сцены (а не авторскими
# заметками): титул вида `D00_GATE — Ворота` и поля Локация/Время/Музыка/…
SCENE_PASSPORT_RE = re.compile(
    r'^(?:[A-Z0-9][\w]*\s+—\s|\d+\.\s|(?:Локация|Время|Музыка|Фон|Персонажи|Эффект|Тип)\s*:)')

# --- имена говорящих из characters.rpy ---
names = {}
for line in open(os.path.join(GAME, "characters.rpy"), encoding="utf-8"):
    m = re.match(r'^\s*define\s+(\w+)\s*=\s*Character\(\s*"([^"]+)"', line)
    if m:
        names[m.group(1)] = m.group(2)

say_re = re.compile(r'^\s*(?:(?P<who>\w+)\s+)?"(?P<text>.*)"\s+id\s+\w+\s*$')
menu_item_re = re.compile(r'^\s*"(?P<cap>[^"]+)"(?:\s+if\s+.+?)?\s*:\s*$')
day_card_re = re.compile(r'^\s*call\s+day_card\(\s*"([^"]*)"\s*,\s*"([^"]*)"\s*\)')
label_re = re.compile(r'^label\s+(\w+)')

out = []
out.append("«ЛЕТО, КОТОРОГО НЕ БЫЛО»")
out.append("Полный сценарий визуальной новеллы (текст игры дословно).")
out.append("Версия 1.2.2 · Ren'Py 8.5 · рейтинг 16+")
out.append("")
out.append("Условные обозначения:")
out.append("  ИМЯ: реплика            — реплика персонажа")
out.append("  простой абзац           — нарратив от первого лица (Артём)")
out.append("  [ВЫБОР] …               — пункт меню игрока")
out.append("  --- КАРТОЧКА: … ---     — титульная карточка дня/концовки на экране")
out.append("=" * 74)
out.append("")

stats = {"lines": 0, "menus": 0, "labels": 0}

for rel in FILES:
    path = os.path.join(GAME, rel)
    lines = open(path, encoding="utf-8").read().splitlines()

    out.append("")
    out.append("")
    out.append("#" * 74)
    out.append("## " + DAY_TITLES.get(rel, rel))
    out.append("#" * 74)

    pending_comment = []
    for i, raw in enumerate(lines):
        s = raw.strip()

        # копим комментарии-подписи сцен (## D1_CANTEEN — Столовая и т.п.)
        if s.startswith("##") and not s.startswith("###"):
            txt = s[2:].strip()
            if txt and not set(txt) <= set("=- ") and SCENE_PASSPORT_RE.match(txt):
                pending_comment.append(txt)
            continue

        m = label_re.match(s)
        if m:
            stats["labels"] += 1
            out.append("")
            out.append("—" * 70)
            for c in pending_comment:
                out.append(c)
            pending_comment = []
            out.append("—" * 70)
            continue

        m = day_card_re.match(s)
        if m:
            title, sub = m.group(1), m.group(2)
            card = title + ((" — " + sub) if sub else "")
            out.append("")
            out.append("--- КАРТОЧКА: %s ---" % card)
            out.append("")
            continue

        if s == "menu:":
            continue

        m = menu_item_re.match(raw)
        if m and not say_re.match(raw):
            stats["menus"] += 1
            out.append("")
            out.append("[ВЫБОР] %s" % m.group("cap"))
            continue

        m = say_re.match(raw)
        if m:
            stats["lines"] += 1
            who = m.group("who")
            text = m.group("text")
            if who:
                out.append("%s: %s" % (names.get(who, who), text))
            else:
                out.append(text)
            continue

        pending_comment = pending_comment[-8:]

    out.append("")

out.append("=" * 74)
out.append("КОНЕЦ СЦЕНАРИЯ")
out.append("Всего реплик и нарратива: %d · пунктов меню: %d · сцен-меток: %d"
           % (stats["lines"], stats["menus"], stats["labels"]))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print("Готово: %s" % os.path.relpath(OUT, ROOT))
print("Реплик/нарратива: %d · пунктов меню: %d · меток: %d"
      % (stats["lines"], stats["menus"], stats["labels"]))
