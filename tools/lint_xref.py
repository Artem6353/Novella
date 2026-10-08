#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lint_xref.py — кросс-ссылочный линт Ren'Py-проекта (по мотивам проверок туториала).

Ловит до запуска движка:
  * `show/scene <имя>` с несуществующим образом (нет объявления и нет файла);
  * `at <трансформ>` с неопределённым трансформом (вне builtins);
  * `play music/sound <имя>` с неопределённым audio-именем;
  * `with <переход>` с неопределённым переходом;
  * ATL-ключевики (linear/ease/pause/repeat...) ребёнком у text/add
    (ошибка вида «'linear' is not a valid child of the text statement»).

Не проверяет tl/ (там строки перевода, не код) и `show screen ...`.
Запуск: python3 tools/lint_xref.py   (из корня репозитория)
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
G = os.path.join(ROOT, "renpy_project", "game")

BUILTIN_T = {"left", "right", "center", "truecenter", "topleft", "topright",
             "bottomleft", "bottomright", "offscreenleft", "offscreenright", "reset"}
BUILTIN_TR = {"dissolve", "fade", "None", "pixellate", "move", "ease", "easein",
              "easeout", "zoomin", "zoominout", "vpunch", "hpunch", "flash",
              "wipe", "slideaway"}
ATL_CHILD = re.compile(r'^\s*(linear|ease|easein|easeout|pause|repeat|parallel|'
                       r'choice|on|contains|animation)\s')


def main():
    rpy = []
    for root, _dirs, files in os.walk(G):
        if os.sep + "tl" in root:
            continue
        for fn in files:
            if fn.endswith(".rpy"):
                rpy.append(os.path.join(root, fn))
    src = {f: open(f, encoding="utf-8").read().splitlines() for f in rpy}
    allsrc = "\n".join("\n".join(v) for v in src.values())

    transforms = set(re.findall(r'^transform (\w+)', allsrc, re.M))
    images = set(re.findall(r'^image ([a-z0-9_]+(?: [a-z0-9_]+)*)\s*=', allsrc, re.M))
    for fn in os.listdir(os.path.join(G, "images")):
        base = os.path.splitext(fn)[0]
        images.add(base.replace("_", " ", 1) if base.startswith(("bg_", "cg_")) else base)
    audio = set(re.findall(r'define audio\.(\w+)', allsrc))
    transitions = set(re.findall(
        r'^define (\w+)\s*=\s*(?:Dissolve|Fade|Pixellate|CropMove|Wipe|Slide|PushMove)',
        allsrc, re.M))

    problems = []
    for f in rpy:
        lines = src[f]
        for i, ln in enumerate(lines):
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            m = re.match(r'^(show|scene)\s+(?!screen\b)([a-z0-9_]+(?: [a-z0-9_]+)*)', s)
            if m and '"' not in s:
                name = m.group(2)
                if not name.startswith(("bg", "cg", "gui", "black", "white")):
                    words = name.split()
                    if not any(" ".join(words[:k]) in images
                               for k in range(len(words), 0, -1)):
                        problems.append((f, i + 1, "image не найдена", name))
                ma = re.search(r'\bat ([a-z_][\w]*)\s*$', s)
                if ma and ma.group(1) not in transforms | BUILTIN_T:
                    problems.append((f, i + 1, "at-трансформ не определён", ma.group(1)))
            m = re.match(r'^play (music|sound) (\w+)', s)
            if m and m.group(2) not in audio | {"None"}:
                problems.append((f, i + 1, "audio не определён", m.group(2)))
            m = re.search(r'\bwith (\w+)$', s)
            if m and m.group(1) not in transitions | BUILTIN_TR:
                problems.append((f, i + 1, "transition не определён", m.group(1)))
            m = re.match(r'^(\s*)(text|add)\b.*:\s*$', ln)
            if m:
                base = len(m.group(1))
                for j in range(i + 1, min(i + 12, len(lines))):
                    nxt = lines[j]
                    if not nxt.strip() or nxt.strip().startswith("#"):
                        continue
                    if len(nxt) - len(nxt.lstrip()) <= base:
                        break
                    if ATL_CHILD.match(nxt):
                        problems.append((f, j + 1, "ATL-ключевик ребёнком у "
                                         + m.group(2), nxt.strip()[:40]))
                    break
    for p in problems:
        print("%s:%d %s: %s" % p)
    print("problems:", len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
