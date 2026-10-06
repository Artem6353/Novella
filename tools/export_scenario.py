#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_scenario.py — генерирует docs/02_сценарий.md (ЭТАП 2)
из рабочего Ren'Py-кода проекта.

Сценарий и код живут в одном месте (game/scenes/*.rpy), а человекочитаемый
документ собирается автоматически, поэтому текст и логика не разъезжаются.

Запуск:  python3 tools/export_scenario.py
"""

import os
import re
import datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
OUT = os.path.join(ROOT, "docs", "02_сценарий.md")

SCENE_FILES = [
    ("Пролог", "scenes/prologue.rpy"),
    ("День 0", "scenes/day00.rpy"),
    ("День 1", "scenes/day01.rpy"),
    ("День 2 — «Трещины»", "scenes/day02.rpy"),
    ("День 3 — «Разделение»", "scenes/day03.rpy"),
    ("День 4 — «Правда»", "scenes/day04.rpy"),
    ("День 5 — «Последний рассвет»", "scenes/day05.rpy"),
    ("Концовки", "scenes/endings.rpy"),
]

NAMES = {
    "mc": "Артём",
    "lena": "Лена",
    "vera": "Вера",
    "zoya": "Зоя",
    "radio": "Радио",
    "child": "Ребёнок",
    "voice": "Голос",
    "young_voice": "Голос",
    "lena_e": "Лена (?)",
    "sys": "",
    "card": "",
    "narrator": "",
}

label_re = re.compile(r"^(?P<indent>\s*)label\s+(?P<name>[\w]+)\s*(\(.*?\))?\s*:\s*$")
say_re = re.compile(r'^(?P<indent>\s*)(?:(?P<who>\w+)\s+)?"(?P<text>.*)"\s*$')
menu_item_re = re.compile(r'^(?P<indent>\s*)"(?P<text>[^"]*)"(?:\s+if\s+(?P<cond>.+?))?\s*:\s*$')
jump_re = re.compile(r"^(?P<indent>\s*)jump\s+(?P<target>[\w]+)\s*$")
var_re = re.compile(r"^(?P<indent>\s*)\$\s*(?P<code>.+?)\s*$")
if_re = re.compile(r'^(?P<indent>\s*)(?P<kind>if|elif|else)\b(?P<cond>.*?)\s*:\s*$')
stage_re = re.compile(r"^(?P<indent>\s*)(?P<cmd>scene|show|hide|with|pause|play|stop|window|return|call)\b(?P<rest>.*)$")

out = []


def w(line=""):
    out.append(line)


def meta_from_header(lines, idx):
    """Собирает ##-комментарий, идущий перед label."""
    header = []
    j = idx - 1
    while j >= 0 and (lines[j].strip().startswith("#") or not lines[j].strip()):
        header.append(lines[j].strip())
        j -= 1
        if len(header) > 22:
            break
    header.reverse()
    meta = {"title": "", "fields": {}}
    for h in header:
        h = h.lstrip("#").strip()
        if not h or set(h) <= {"-", "=", " "}:
            continue
        m = re.match(r"^([А-ЯA-Z][\w\- ]{2,}?)\s*[—:]\s*(.+)$", h)
        if m and m.group(1).strip() in ("Локация", "Время", "Музыка", "Фон", "Персонажи",
                                        "Эффект", "ВАЖНО", "Тип", "Условие", "Условия"):
            meta["fields"].setdefault(m.group(1).strip(), []).append(m.group(2).strip())
        elif re.match(r"^[A-Z0-9_]{3,}\s+—", h):
            meta["title"] = h
    return meta


def body_lines(lines, start):
    """Возвращает строки тела label до следующего label верхнего уровня."""
    body = []
    i = start + 1
    while i < len(lines):
        if label_re.match(lines[i]):
            break
        body.append(lines[i])
        i += 1
    while body and not body[-1].strip():
        body.pop()
    return body


def render_body(body):
    """Преобразует Ren'Py-код тела сцены в человекочитаемый сценарий."""
    lines_out = []
    menu_indent = None
    choice_letter = 0
    in_choice = False
    choice_indent = None

    for raw0 in body:
        if not raw0.strip():
            continue
        raw = re.sub(r'\s+id\s+[\w]+', '', raw0)
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()

        if line.startswith("##"):
            continue
        if line.startswith("#"):
            note = line.lstrip("#").strip()
            if note:
                lines_out.append(f"> `{note}`  ")
            continue

        # --- пункт меню ---
        m = menu_item_re.match(raw)
        if m and menu_indent is not None and indent > menu_indent:
            choice_letter += 1
            letter = chr(ord("A") + choice_letter - 1)
            cond = m.group("cond")
            cond_txt = f"  \n&nbsp;&nbsp;&nbsp;&nbsp;_условие доступа:_ `{cond}`" if cond else ""
            lines_out.append(f"\n**{letter})** «{m.group('text')}»{cond_txt}")
            in_choice = True
            choice_indent = indent
            continue

        if line == "menu:":
            menu_indent = indent
            lines_out.append("\n**ВЫБОР:**\n")
            continue

        # --- диалог / нарратив ---
        m = say_re.match(raw)
        if m and m.group("text") and not line.startswith("$"):
            who = m.group("who")
            text = m.group("text")
            prefix = f"\n**{NAMES.get(who, who)}:**" if who and NAMES.get(who, who) else ""
            if prefix:
                lines_out.append(prefix)
                lines_out.append(text + "  ")
            else:
                lines_out.append(f"_{text}_  ")
            continue

        # --- эффекты ---
        m = var_re.match(raw)
        if m:
            lines_out.append(f"&nbsp;&nbsp;&nbsp;&nbsp;→ эффект: `{m.group('code')}`")
            continue

        # --- переходы ---
        m = jump_re.match(raw)
        if m:
            lines_out.append(f"\n&nbsp;&nbsp;&nbsp;&nbsp;→ **переход:** `{m.group('target')}`")
            continue

        # --- ветвления по маршруту ---
        m = if_re.match(raw)
        if m:
            kind, cond = m.group("kind"), m.group("cond").strip()
            if kind == "if":
                lines_out.append(f"\n**ЕСЛИ** `{cond}` **:**")
            elif kind == "elif":
                lines_out.append(f"\n**ИНАЧЕ, ЕСЛИ** `{cond}` **:**")
            else:
                lines_out.append("\n**ИНАЧЕ (route == \"none\"):**")
            continue

        # --- служебные операторы ---
        m = stage_re.match(raw)
        if m:
            cmd, rest = m.group("cmd"), m.group("rest").strip()
            if cmd == "return":
                lines_out.append("\n→ **конец** (возврат в главное меню)")
            elif cmd == "scene":
                lines_out.append(f"\n`[ФОН: {rest}]`  ")
            elif cmd == "show":
                lines_out.append(f"`[ПОЯВЛЯЕТСЯ: {rest}]`")
            elif cmd == "hide":
                lines_out.append(f"`[УХОДИТ: {rest}]`")
            elif cmd == "with":
                lines_out.append(f"`[{rest.upper()}]`")
            elif cmd == "pause":
                lines_out.append(f"`[пауза {rest} сек]`")
            elif cmd == "call":
                lines_out.append(f"`[вставка: {rest}]`")
            continue

    return "\n".join(lines_out)


# ---------------------------------------------------------------------------
w("# ЭТАП 2. ПОЛНЫЙ СЦЕНАРИЙ")
w("## «Лето, которого не было» — все сцены")
w()
w(f"> Документ сгенерирован автоматически из рабочего кода `renpy_project/game/scenes/*.rpy` "
  f"({datetime.date.today().isoformat()}).")
w(">")
w("> **Единственный источник правды — код.** Этот файл пересобирается командой "
  "`python3 tools/export_scenario.py`, поэтому сценарий и логика флагов не расходятся.")
w()
w("**Правила, соблюдённые в сценарии:** длина сцены 300–900 слов; диалоги важнее описаний; "
  "одна реплика — не более 2–3 строк; в каждой сцене со Дня 2 есть минимум одна странность; "
  "тайна не раскрывается до `D4_TRUTH`; никакой жестокости, откровенности и хоррора; "
  "в финале — светлая грусть.")
w()
w("**Голоса персонажей:** Артём — коротко, с иронией; Лена — мягко, загадками, замирает "
  "на полуслове; Вера — громко, быстро, боится пауз; Зоя — тихо, коротко, пугающе прямо.")
w()
w("---")
w()

total_scenes = 0
for section, rel in SCENE_FILES:
    path = os.path.join(GAME, rel)
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    w(f"# {section}")
    w()
    w(f"_Файл: `game/{rel}`_")
    w()

    for i, line in enumerate(lines):
        m = label_re.match(line)
        if not m:
            continue
        name = m.group("name")
        meta = meta_from_header(lines, i)
        title = meta["title"] or name.upper()
        body = body_lines(lines, i)
        if not body:
            continue
        total_scenes += 1

        w("---")
        w()
        w(f"## {title}")
        w()
        w(f"`label {name}`")
        w()
        for key in ("Локация", "Время", "Музыка", "Фон", "Персонажи", "Тип", "Эффект", "Условие", "Условия", "ВАЖНО"):
            if key in meta["fields"]:
                w(f"**{key}:** " + " / ".join(meta["fields"][key]))
        w()
        w("---")
        w()
        w("*Нарратив от первого лица (Артём):*")
        w()
        w(render_body(body))
        w()

w("---")
w()
w(f"**Всего сцен в документе: {total_scenes}.**")
w()
w("Служебные метки `start`, `day_card`, `end_card` описаны в `game/script.rpy`.")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Готово: {os.path.relpath(OUT, ROOT)}")
print(f"Сцен: {total_scenes}, строк: {len(out)}")
