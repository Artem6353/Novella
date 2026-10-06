#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_web.py — собирает web_demo/index.html из шаблона движка и game_data.json.
Запуск: python3 tools/build_web.py   (после tools/export_web.py)
"""

import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TPL = os.path.join(ROOT, "web_src", "engine_template.html")
DATA = os.path.join(ROOT, "web_demo", "game_data.json")
OUT = os.path.join(ROOT, "web_demo", "index.html")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Единый словарь локализации интерфейса: он же используется tools/gen_tl.py,
# чтобы RU/EN строки web-плеера и Ren'Py-версии не могли разъехаться.
from ui_strings import EX  # noqa: E402

tpl = open(TPL, encoding="utf-8").read()
data = open(DATA, encoding="utf-8").read()

html = tpl.replace("__GAME_DATA__", data).replace("__EXTRA__", json.dumps(EX, ensure_ascii=False))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Готово: {os.path.relpath(OUT, ROOT)} — {os.path.getsize(OUT)//1024} KB")
