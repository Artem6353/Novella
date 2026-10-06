#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_web.py — собирает автономную HTML5-версию новеллы (web_demo/index.html).

Что делает:
  1. Парсит game/*.rpy и game/scenes/*.rpy в байткод мини-движка (ops).
  2. Конвертирует ограниченный подмножество Python-выражений в JS.
  3. Подшивает перевод из tools/translations.py (RU/EN переключатель).
  4. Вшивает изображения (base64) и собирает ОДИН самодостаточный index.html.

Запуск: python3 tools/export_web.py
Результат: web_demo/index.html — открывается двойным кликом и в любом браузере,
и в предпросмотре файлов (всё инлайном, внешних запросов нет).
"""

import base64
import io
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
OUTDIR = os.path.join(ROOT, "web_demo")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations import TRANS  # noqa: E402
from menu_captions import MENU_CAPTIONS  # noqa: E402

# подпись пункта меню (RU) -> EN
MENU_EN = {MENU_CAPTIONS[k]: v for k, v in TRANS.items() if k in MENU_CAPTIONS}

FILES = ["script.rpy",
         "scenes/prologue.rpy", "scenes/day00.rpy", "scenes/day01.rpy",
         "scenes/day02.rpy", "scenes/day03.rpy", "scenes/day04.rpy",
         "scenes/day05.rpy", "scenes/endings.rpy"]

# ---------------------------------------------------------------- парсинг ----
label_re = re.compile(r"^label\s+(?P<name>\w+)\s*(?P<args>\(.*?\))?\s*:\s*$")
say_re = re.compile(r'^(?:(?P<who>mc|lena|vera|zoya|radio|child|young_voice|lena_e|card|narrator)\s+)?"(?P<text>.*)"\s+id\s+(?P<id>\w+)\s*$')
menu_item_re = re.compile(r'^"(?P<text>[^"]*)"(?:\s+id\s+(?P<id>\w+))?(?P<cond>\s+if\s+.+?)?:\s*$')
jump_re = re.compile(r"^jump\s+(\w+)\s*$")
call_re = re.compile(r"^call\s+(\w+)(?:\((?P<args>.*)\))?\s*$")
var_re = re.compile(r"^\$\s*(.+)$")
if_re = re.compile(r"^(if|elif|else)\b(.*?)\s*:\s*$")
scene_re = re.compile(r"^scene\s+([\w ]+?)\s*$")
show_re = re.compile(r"^show\s+([\w ]+?)(?:\s+at\s+(\w+))?\s*$")
hide_re = re.compile(r"^hide\s+(\w+)\s*$")
with_re = re.compile(r"^with\s+(\w+)\s*$")
pause_re = re.compile(r"^pause\s+([\d.]+)\s*$")
playmusic_re = re.compile(r"^play music\s+(\w+)")
playmusic_fade_re = re.compile(r"fadein\s+([\d.]+)")
playsound_re = re.compile(r"^play sound\s+(\w+)(\s+loop)?\s*$")
stopmusic_re = re.compile(r"^stop music\b.*$")
stopsound_re = re.compile(r"^stop sound\b.*$")


def to_js(expr):
    e = expr.strip()
    e = re.sub(r"\bpersistent\.(\w+)", r"P.\1", e)
    e = e.replace("renpy.block_rollback()", "0")
    e = re.sub(r"\bmax\(", "Math.max(", e)
    e = re.sub(r"\bmin\(", "Math.min(", e)
    e = re.sub(r"(\w+)\s+in\s+\[([^\]]*)\]", r"[\2].indexOf(\1) >= 0", e)
    e = re.sub(r"\band\b", "&&", e)
    e = re.sub(r"\bor\b", "||", e)
    e = re.sub(r"\bnot\s+", "!", e)
    e = e.replace("True", "true").replace("False", "false").replace("None", "null")
    return e


def parse_block(lines, i, indent):
    ops = []
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.strip().startswith("#"):
            i += 1
            continue
        cur = len(raw) - len(raw.lstrip())
        if cur < indent:
            break
        line = raw.strip()

        m = say_re.match(line)
        if m:
            ops.append({"op": "say", "who": m.group("who"), "id": m.group("id"),
                        "ru": m.group("text"), "en": TRANS.get(m.group("id"))})
            i += 1
            continue

        if line == "menu:":
            items, i = parse_menu(lines, i + 1, cur)
            ops.append({"op": "menu", "items": items})
            continue

        m = menu_item_re.match(line)
        if m:  # одиночный пункт вне menu (не должно случаться)
            i += 1
            continue

        m = var_re.match(line)
        if m:
            code = m.group(1)
            if "renpy.block_rollback()" in code:
                ops.append({"op": "noop"})
            else:
                mm = re.match(r"^([\w.]+)\s*(\+=|-=|=)\s*(.+)$", code)
                if mm:
                    target, op, expr = mm.groups()
                    if op == "+=":
                        expr = f"{target} + ({expr})"
                    elif op == "-=":
                        expr = f"{target} - ({expr})"
                    ops.append({"op": "set", "target": target, "expr": to_js(expr)})
                else:
                    ops.append({"op": "noop"})
            i += 1
            continue

        m = if_re.match(line)
        if m:
            kind, cond = m.groups()
            body, i = parse_block(lines, i + 1, cur + 1)
            if kind == "if":
                node = {"op": "if", "cond": to_js(cond), "then": body, "else": []}
            else:
                node = {"op": "elseblock", "body": body}
            # приклеиваем elif/else
            while i < len(lines):
                nxt = lines[i].strip()
                mm = if_re.match(nxt)
                if (mm and mm.group(1) in ("elif", "else")
                        and (len(lines[i]) - len(lines[i].lstrip())) == cur):
                    k2, c2 = mm.groups()
                    body2, i = parse_block(lines, i + 1, cur + 1)
                    if k2 == "elif":
                        node["else"] = [{"op": "if", "cond": to_js(c2), "then": body2, "else": node["else"]}]
                    else:
                        node["else"] = body2
                else:
                    break
            ops.append(node)
            continue

        m = jump_re.match(line)
        if m:
            ops.append({"op": "jump", "to": m.group(1)})
            i += 1
            continue

        m = call_re.match(line)
        if m:
            name, args = m.group(1), m.group("args")
            if name == "day_card":
                a = re.findall(r'"([^"]*)"', args or "")
                ops.append({"op": "daycard", "a": a[0] if a else "", "b": a[1] if len(a) > 1 else ""})
            elif name == "end_card":
                ops.append({"op": "endcard"})
            else:
                ops.append({"op": "call", "to": name})
            i += 1
            continue

        m = scene_re.match(line)
        if m:
            ops.append({"op": "scene", "img": m.group(1).strip()})
            i += 1
            continue
        m = show_re.match(line)
        if m:
            at_val = m.group(2) or "center"
            if at_val.startswith("tr_"):
                at_val = at_val[3:]
            ops.append({"op": "show", "img": m.group(1).strip(), "at": at_val})
            i += 1
            continue
        m = hide_re.match(line)
        if m:
            ops.append({"op": "hide", "tag": m.group(1)})
            i += 1
            continue
        m = with_re.match(line)
        if m:
            ops.append({"op": "fade", "kind": m.group(1)})
            i += 1
            continue
        m = pause_re.match(line)
        if m:
            ops.append({"op": "pause", "s": float(m.group(1))})
            i += 1
            continue

        m = playmusic_re.match(line)
        if m:
            fm = playmusic_fade_re.search(line)
            ops.append({"op": "music", "track": m.group(1), "fade": float(fm.group(1) if fm else 1.0)})
            i += 1
            continue
        m = playsound_re.match(line)
        if m:
            ops.append({"op": "sfx", "name": m.group(1), "loop": bool(m.group(2))})
            i += 1
            continue
        if stopmusic_re.match(line):
            ops.append({"op": "stopmusic"})
            i += 1
            continue
        if stopsound_re.match(line):
            ops.append({"op": "stopsfx"})
            i += 1
            continue

        if line == "return":
            ops.append({"op": "return"})
            i += 1
            continue

        i += 1  # прочее (play/stop/window и т.п.) игнорируем
    return ops, i


def parse_menu(lines, i, menu_indent):
    items = []
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.strip().startswith("#"):
            i += 1
            continue
        cur = len(raw) - len(raw.lstrip())
        if cur <= menu_indent:
            break
        m = menu_item_re.match(raw.strip())
        if m:
            cond = m.group("cond")
            body, i = parse_block(lines, i + 1, cur + 1)
            items.append({"ru": m.group("text"), "en": MENU_EN.get(m.group("text")),
                          "cond": to_js(cond.strip()[3:]) if cond else None,
                          "body": body})
        else:
            i += 1
    return items, i


program = {}
for rel in FILES:
    lines = open(os.path.join(GAME, rel), encoding="utf-8").read().split("\n")
    i = 0
    while i < len(lines):
        m = label_re.match(lines[i])
        if m:
            body, i = parse_block(lines, i + 1, 1)
            program[m.group("name")] = body
        else:
            i += 1

# ------------------------------------------------------------- изображения ---
from PIL import Image  # noqa: E402

ART = os.path.join(ROOT, "art")
IMAGES = {}


def b64_jpg(src, w=1100, q=70):
    im = Image.open(src).convert("RGB")
    r = w / im.width
    im = im.resize((w, int(im.height * r)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def b64_webp(src, h=900, q=72):
    im = Image.open(src).convert("RGBA")
    r = h / im.height
    im = im.resize((int(im.width * r), h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=q)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


for name, src in [("bg room", f"{ART}/bg169/bg_room.jpg"),
                  ("bg bus", f"{ART}/bg169/bg_bus.jpg"),
                  ("bg gate", f"{ART}/bg169/bg_gate.jpg"),
                  ("bg square", f"{ART}/bg169/bg_square.jpg"),
                  ("bg river", f"{ART}/bg169/bg_river.jpg"),
                  ("cg_lena_gate", f"{ART}/bg169/cg_lena_gate.jpg")]:
    IMAGES[name] = b64_jpg(src)
IMAGES["menu_bg"] = b64_jpg(f"{ART}/bg169/menu_bg.jpg", w=1400, q=68)
for name, src in [("lena normal", f"{ART}/sprites_half/lena_normal.png"),
                  ("lena smile", f"{ART}/sprites_half/lena_smile.png"),
                  ("lena sad", f"{ART}/sprites_half/lena_sad.png"),
                  ("lena anxious", f"{ART}/sprites_half/lena_anxious.png"),
                  ("lena surprised", f"{ART}/sprites_half/lena_surprised.png"),
                  ("lena mystery", f"{ART}/sprites_half/lena_mystery.png")] + \
                 [(f"vera {e}", f"{ART}/sprites_half/vera_{e}.png") for e in
                  ("happy", "excited", "stubborn", "offended", "thoughtful", "determined", "sad")] + \
                 [(f"zoya {e}", f"{ART}/sprites_half/zoya_{e}.png") for e in
                  ("calm", "focused", "sad", "sleepy", "smile")]:
    IMAGES[name] = b64_webp(src)
P2_BG = ["bg forest_day", "bg forest_night", "bg stage", "bg abandoned", "bg campfire",
         "bg pier", "bg gate_night", "bg square_night", "bg river_night",
         "bg dorm_day", "bg dorm_night", "bg dawn"]
P2_CG = ["cg_d3_glitch", "cg_d4_truth_pier", "cg_true_last_lineup", "cg_lena_stay",
         "cg_vera_voice", "cg_zoya_painting", "cg_farewell_dawn", "cg_forgotten_gate",
         "cg_secret_ticket_two", "cg_vera_meet", "cg_zoya_meet", "cg_lena_river"]
for name in ("bg canteen", "bg library", "bg radio", *P2_BG, *P2_CG):
    IMAGES[name] = b64_jpg(f"{ART}/bg169/{name.replace(' ', '_')}.jpg", w=960, q=66)
for name, src in [("lena surprised", f"{ART}/sprites_half/lena_surprised.png"),
                  ("lena mystery", f"{ART}/sprites_half/lena_mystery.png")]:
    IMAGES[name] = b64_webp(src, h=900, q=72)

# цвета-заглушки для образов, которых пока нет (из images.rpy)
SOLID = {}
for line in open(os.path.join(GAME, "images.rpy"), encoding="utf-8"):
    m = re.match(r'image\s+([\w ]+?)\s+=\s+Solid\("(#\w+)"', line)
    if m:
        SOLID[m.group(1).strip()] = m.group(2)

# дефолты переменных из variables.rpy
DEFAULTS = {}
for line in open(os.path.join(GAME, "variables.rpy"), encoding="utf-8"):
    m = re.match(r"default\s+(\w+)\s*=\s*(.+)$", line.strip())
    if m:
        val = m.group(2).strip()
        if val == "True":
            val = True
        elif val == "False":
            val = False
        elif val.startswith('"'):
            val = val.strip('"')
        else:
            try:
                val = int(val)
            except ValueError:
                val = 0
        DEFAULTS[m.group(1)] = val

DATA = {"program": program, "images": IMAGES, "solid": SOLID,
        "defaults": DEFAULTS, "start": "start"}

os.makedirs(OUTDIR, exist_ok=True)
with open(os.path.join(OUTDIR, "game_data.json"), "w", encoding="utf-8") as f:
    json.dump(DATA, f, ensure_ascii=False)

print(f"program labels: {len(program)}")
print(f"images embedded: {len(IMAGES)}")
print(f"game_data.json: {os.path.getsize(os.path.join(OUTDIR, 'game_data.json')) // 1024} KB")
