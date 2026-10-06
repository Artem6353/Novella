#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_rpt.py — генерирует game/tests_autogen.rpy: авто-тесты Ren'Py (self-test framework).

Каждый testcase проигрывает целый маршрут НА РЕАЛЬНОМ ДВИЖКЕ:
  skip — мотает диалоги, click "<подпись>" — выбирает пункт меню.
Подписи меню и ожидаемая концовка вычисляются прогоном мини-VM по байткоду .rpy
(условия видимости пунктов меню учитываются).

Запуск:  python3 tools/gen_rpt.py
Проверка: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy renpy.sh <проект> test
"""

import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME = os.path.join(ROOT, "renpy_project", "game")
OUT = os.path.join(GAME, "tests_autogen.rpy")

FILES = ["script.rpy",
         "scenes/prologue.rpy", "scenes/day00.rpy", "scenes/day01.rpy",
         "scenes/day02.rpy", "scenes/day03.rpy", "scenes/day04.rpy",
         "scenes/day05.rpy", "scenes/endings.rpy"]

label_re = re.compile(r"^label\s+(?P<name>\w+)\s*(?P<args>\(.*?\))?\s*:\s*$")
say_re = re.compile(r'^(?:(?P<who>\w+)\s+)?"(?P<text>.*)"\s+id\s+(?P<id>\w+)\s*$')
menu_item_re = re.compile(r'^"(?P<text>[^"]*)"(?:\s+id\s+(?P<id>\w+))?(?P<cond>\s+if\s+.+?)?:\s*$')
jump_re = re.compile(r"^jump\s+(\w+)\s*$")
call_re = re.compile(r"^call\s+(\w+)(?:\((?P<args>.*)\))?\s*$")
var_re = re.compile(r"^\$\s*(.+)$")
if_re = re.compile(r"^(if|elif|else)\b(.*?)\s*:\s*$")


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
        if line == "menu:":
            items, i = parse_menu(lines, i + 1, cur)
            ops.append({"op": "menu", "items": items})
            continue
        if menu_item_re.match(line):
            i += 1
            continue
        if say_re.match(line):
            ops.append({"op": "say"})
            i += 1
            continue
        m = var_re.match(line)
        if m:
            ops.append({"op": "set", "code": m.group(1)})
            i += 1
            continue
        m = if_re.match(line)
        if m:
            kind, cond = m.groups()
            body, i = parse_block(lines, i + 1, cur + 1)
            if kind == "if":
                node = {"op": "if", "cond": cond, "then": body, "else": []}
            else:
                node = None
                ops.append({"op": "if", "cond": "True", "then": body, "else": []})
                i = i
                continue
            # Собираем цепочку elif/else того же уровня вложенности.
            # ВАЖНО: elif-ветки накапливаем и собираем else-цепочку с конца,
            # иначе финальный else перезатирал бы все предыдущие elif
            # (так терялись меню d4_conflict/d5_prepare для веток Веры и Зои).
            elifs = []
            final_else = []
            while i < len(lines):
                nxt = lines[i].strip()
                mm = if_re.match(nxt)
                if mm and mm.group(1) in ("elif", "else") and (len(lines[i]) - len(lines[i].lstrip())) == cur:
                    k2, c2 = mm.groups()
                    body2, i = parse_block(lines, i + 1, cur + 1)
                    if k2 == "elif":
                        elifs.append((c2, body2))
                    else:
                        final_else = body2
                        break
                else:
                    break
            else_chain = final_else
            for c2, body2 in reversed(elifs):
                else_chain = [{"op": "if", "cond": c2, "then": body2, "else": else_chain}]
            node["else"] = else_chain
            ops.append(node)
            continue
        m = jump_re.match(line)
        if m:
            ops.append({"op": "jump", "to": m.group(1)})
            i += 1
            continue
        m = call_re.match(line)
        if m:
            ops.append({"op": "call", "to": m.group(1)})
            i += 1
            continue
        if line == "return":
            ops.append({"op": "return"})
            i += 1
            continue
        i += 1
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
            items.append({"text": m.group("text"),
                          "cond": cond.strip()[3:] if cond else None,
                          "body": body})
        else:
            i += 1
    return items, i


PROGRAM = {}
for rel in FILES:
    lines = open(os.path.join(GAME, rel), encoding="utf-8").read().split("\n")
    i = 0
    while i < len(lines):
        m = label_re.match(lines[i])
        if m:
            body, i = parse_block(lines, i + 1, 1)
            PROGRAM[m.group("name")] = body
        else:
            i += 1

DEFAULTS = {}
for line in open(os.path.join(GAME, "variables.rpy"), encoding="utf-8"):
    m = re.match(r"default\s+(\w+)\s*=\s*(.+)$", line.strip())
    if m:
        v = m.group(2).strip()
        if v == "True":
            DEFAULTS[m.group(1)] = True
        elif v == "False":
            DEFAULTS[m.group(1)] = False
        elif v.startswith('"'):
            DEFAULTS[m.group(1)] = v.strip('"')
        else:
            DEFAULTS[m.group(1)] = int(v)


class Jump(Exception):
    def __init__(self, to):
        self.to = to


class Ret(Exception):
    pass


class End(Exception):
    pass


def run(strategy, preset_p=None):
    V = dict(DEFAULTS)
    P = dict(preset_p or {})
    trace, ending, steps, state = [], [None], [0], {"label": ""}

    class Pers:
        def __init__(self, d):
            self.__dict__.update(d)

        def __getattr__(self, k):
            return None

    def ev(expr):
        return eval(expr, {"max": max, "min": min},
                dict(V, persistent=Pers(P),
                     day_title="", day_sub=""))

    def setv(code):
        m = re.match(r"^([\w.]+)\s*(\+=|-=|=)\s*(.+)$", code)
        if not m:
            return
        t, op, e = m.groups()
        val = ev(e)
        if op == "+=":
            val = ev(t) + val
        elif op == "-=":
            val = ev(t) - val
        if t.startswith("persistent."):
            P[t.split(".", 1)[1]] = val
        else:
            V[t] = val

    def exec_ops(ops):
        for op in ops:
            steps[0] += 1
            if steps[0] > 60000:
                raise RuntimeError("step limit")
            k = op["op"]
            if k == "set":
                if "renpy.block_rollback()" in op["code"]:
                    continue
                setv(op["code"])
            elif k == "if":
                exec_ops(op["then"] if ev(op["cond"]) else op["else"])
            elif k == "menu":
                state["menu_label"] = state["label"]
                vis = [it for it in op["items"] if it["cond"] is None or ev(it["cond"])]
                pick = strategy(state["menu_label"], vis, V)
                trace.append(pick["text"])
                exec_ops(pick["body"])
            elif k == "call":
                run_label(op["to"])
            elif k == "jump":
                raise Jump(op["to"])
            elif k == "return":
                raise Ret()
            elif k == "endcard":
                raise End()

    def run_label(name):
        if name not in PROGRAM:
            raise RuntimeError("нет метки " + name)
        if name.startswith("ending_"):
            ending[0] = name
        prev = state["label"]
        state["label"] = name
        cur = name
        try:
            while True:
                try:
                    exec_ops(PROGRAM[cur])
                    return
                except Jump as j:
                    cur = j.to
                    state["label"] = cur
                    if cur.startswith("ending_"):
                        ending[0] = cur
                    continue
                except Ret:
                    return
                except End:
                    return
        finally:
            state["label"] = prev

    run_label("start")
    return trace, ending[0], V


def idx(table):
    def f(label, vis, V):
        return vis[table.get(label, 0) % len(vis)]
    return f


COMMON = {"p01_room": 0, "d00_gate": 1, "d00_square": 0, "d1_canteen": 0, "d1_library": 0,
          "d2_morning": 0, "d2_radio_repair": 0, "d2_lena_warning": 0, "d2_night_forest": 0,
          "d4_conflict": 0, "d5_prepare": 0, "d5_final_choice": 0}

STRATS = {
    "first":        (lambda l, vis, V: vis[0], {}),
    "last":         (lambda l, vis, V: vis[-1], {}),
    "lena_true":    (idx(dict(COMMON, d1_evening_choice=2, d3_route_select=0)), {}),
    "lena_stay":    (idx(dict(COMMON, d1_evening_choice=2, d3_route_select=0, d5_final_choice=1)), {}),
    "vera":         (idx(dict(COMMON, d1_evening_choice=0, d3_route_select=1)), {}),
    "zoya":         (idx(dict(COMMON, d1_evening_choice=1, d3_route_select=2)), {}),
    "alone":        (idx(dict(COMMON, d1_evening_choice=2, d3_route_select=3)), {}),
    "farewell":     (idx({"p01_room": 0, "d00_gate": 0, "d00_square": 0, "d1_canteen": 0,
                          "d1_library": 1, "d1_evening_choice": 2, "d2_morning": 0,
                          "d2_radio_repair": 0, "d2_lena_warning": 1, "d2_night_forest": 1,
                          "d3_route_select": 0, "d4_conflict": 1, "d5_prepare": 0,
                          "d5_final_choice": 0}), {}),
    "secret":       (idx(dict(COMMON, d1_evening_choice=2, d3_route_select=0, d5_final_choice=2)),
                     {"true_seen": True}),
}

EXPECTED = {
    "first": "ending_true", "last": "ending_forgotten",
    "lena_true": "ending_true", "lena_stay": "ending_lena_stay",
    "vera": "ending_vera_voice", "zoya": "ending_zoya_painting",
    "alone": "ending_forgotten", "farewell": "ending_farewell",
    "secret": "ending_secret",
}

out = []
out.append("## ============================================================")
out.append("## tests_autogen.rpy — автотесты Ren'Py (self-test framework)")
out.append("## Сгенерировано tools/gen_rpt.py: каждый testcase проигрывает маршрут")
out.append("## на реальном движке: skip по диалогам + click по подписям меню.")
out.append("## Запуск: renpy.sh <проект> test   (SDL_VIDEODRIVER=dummy)")
out.append("## ============================================================")
out.append("")
out.append("## teardown: exit живёт в testsuite global (tests.rpy) — он завершает")
out.append("## процесс после ВСЕХ сюит. Здесь свой teardown не нужен: он обрезал бы")
out.append("## соседние сюиты при полном прогоне.")
out.append("testsuite autogen:")
out.append("")
out.append("    before testcase:")
out.append("        $ _test.transition_timeout = 0.05")
out.append("        $ _test.timeout = 90")
out.append("")
out.append("        python:")
out.append("            if _preferences.language is not None:")
out.append("                renpy.change_language(None)")
out.append("")
out.append("        ## Возврат в главное меню только если предыдущий тест упал посреди")
out.append("        ## игры (см. комментарий в tests.rpy: наивная проверка screen")
out.append("        ## \"main_menu\" ломает загрузку движка в headless-среде).")
out.append("        if eval (renpy.exports.get_filename_line() or ('', 0))[0].startswith('game/') or (getattr(renpy.context(), '_menu', False) and not getattr(renpy.context(), '_main_menu', False)):")
out.append("            run MainMenu(confirm=False)")
out.append("            advance until screen \"main_menu\"")
out.append("        python:")
out.append("            preferences.skip_unseen = True")
out.append("            preferences.skip_after_choices = True")
out.append("")

for name, (strat, preset) in STRATS.items():
    trace, ending, V = run(strat, preset)
    assert ending == EXPECTED[name], (name, ending, EXPECTED[name])
    # ВАЖНО: testcase'ы вложены в testsuite (отступ 4 пробела) — иначе
    # хуки before testcase не применяются и тесты падают по таймауту 5 с.
    out.append(f"    testcase route_{name}:")
    out.append("")
    if preset:
        out.append("        python:")
        for k, v in preset.items():
            out.append(f"            persistent.{k} = {v}")
        out.append("")
    out.append('        click "Начать игру"')
    out.append("        skip")
    for caption in trace:
        out.append(f'        click "{caption}"')
    out.append("        skip")
    # ВАЖНО: assert проверяется ДО возврата в главное меню. Когда игра
    # возвращается в меню, движок сбрасывает все default-переменные
    # (execute_default_statement), и ending_shown снова станет "".
    out.append('        advance until eval ending_shown != ""')
    out.append(f'        assert eval ending_shown == {V["ending_shown"]!r}')
    out.append("")
    print(f"✓ route_{name}: меню={len(trace)} кликов → {ending}")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(f"Готово: {os.path.relpath(OUT, ROOT)}")
