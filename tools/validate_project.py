#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_project.py — статическая проверка Ren'Py-проекта
«Лето, которого не было» без установленного движка.

Что проверяет:
  1. Все label объявлены один раз.
  2. Все jump / call ведут на существующие label.
  3. Все scene / show / hide используют объявленные image.
  4. Все переменные в $-строках и условиях объявлены в variables.rpy
     (persistent.*, renpy.*, config.* и встроенные — в белом списке).
  5. Баланс кавычек в строках диалогов.
  6. В каждой сюжетной сцене есть `scene` и комментарий-подсказка музыки.
  7. Случайные латинские вкрапления в русский текст (опечатки).

Запуск:  python3 tools/validate_project.py
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renpy_project", "game")
if len(sys.argv) > 1:          # можно проверить любую копию game/: validate_project.py <путь>
    ROOT = os.path.abspath(sys.argv[1])

FILES = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # переводы (game/tl/<язык>/*.rpy) — не игровой скрипт: там блоки
    # old/new, которые проверки диалогов приняли бы за «говорящих»
    if "tl" in dirpath.split(os.sep):
        dirnames[:] = []
        continue
    for fn in sorted(filenames):
        if fn.endswith(".rpy"):
            FILES.append(os.path.join(dirpath, fn))
FILES.sort()

errors = []
warnings = []
stats = {"labels": 0, "lines_dialogue": 0, "words": 0, "scenes": 0, "menus": 0}


def rel(p):
    return os.path.relpath(p, ROOT)


# ---------------------------------------------------------------------------
# 1-2. labels / jumps / calls
# ---------------------------------------------------------------------------
labels = {}
label_re = re.compile(r"^\s*label\s+([a-zA-Z_][\w]*)\s*(\(.*?\))?\s*:\s*$")
jump_re = re.compile(r"\bjump\s+([a-zA-Z_][\w]*)")
call_re = re.compile(r"\bcall\s+([a-zA-Z_][\w]*)\b(?!\s*screen)")

all_lines = {}
for path in FILES:
    with open(path, encoding="utf-8") as f:
        all_lines[path] = f.read().splitlines()

for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        m = label_re.match(line)
        if m:
            name = m.group(1)
            if name in labels:
                errors.append(f"{rel(path)}:{i} повторное объявление label {name} "
                              f"(первое: {labels[name]})")
            labels[name] = f"{rel(path)}:{i}"
            stats["labels"] += 1

known_targets = set(labels)

for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for m in jump_re.finditer(line):
            if m.group(1) not in known_targets:
                errors.append(f"{rel(path)}:{i} jump на несуществующий label "
                              f"'{m.group(1)}'")
        for m in call_re.finditer(line):
            tgt = m.group(1)
            if tgt in ("screen", "expression", "end_card", "day_card"):
                pass
            if tgt not in known_targets and not line.strip().startswith("#"):
                errors.append(f"{rel(path)}:{i} call несуществующего label '{tgt}'")

# ---------------------------------------------------------------------------
# 3. images
# ---------------------------------------------------------------------------
declared_images = set()
image_re = re.compile(r"^\s*image\s+([\w ]+?)\s*=")
for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        m = image_re.match(line)
        if m:
            declared_images.add(m.group(1).strip())
            declared_images.add(m.group(1).strip().split()[0])  # тег

# встроенные transform'ы и служебные слова
BUILTIN = {"fade", "dissolve", "center", "left", "right", "truecenter", "None"}

scene_re = re.compile(r"^\s*scene\s+([\w ]+?)(?:\s+with\s+[\w]+)?\s*$")
show_re = re.compile(r"^\s*show\s+([\w ]+?)(?:\s+at\s+[\w ]+?)?(?:\s+with\s+[\w]+)?\s*$")
hide_re = re.compile(r"^\s*hide\s+([\w]+)")

scene_stats = {}
for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = scene_re.match(line)
        if m:
            img = m.group(1).strip()
            if img not in declared_images and img.split()[0] not in declared_images:
                errors.append(f"{rel(path)}:{i} scene использует необъявленный образ '{img}'")
            stats["scenes"] += 1
            scene_stats.setdefault(path, []).append(i)
            continue
        m = show_re.match(line)
        if m:
            img = m.group(1).strip()
            if img not in declared_images and img.split()[0] not in declared_images:
                errors.append(f"{rel(path)}:{i} show использует необъявленный образ '{img}'")
            continue
        m = hide_re.match(line)
        if m:
            tag = m.group(1)
            if tag not in declared_images:
                if tag != "screen":
                    errors.append(f"{rel(path)}:{i} hide использует необъявленный тег '{tag}'")

# ---------------------------------------------------------------------------
# 4. переменные
# ---------------------------------------------------------------------------
declared_vars = set()
default_re = re.compile(r"^\s*default\s+([\w]+)\s*=")
for path, lines in all_lines.items():
    for line in lines:
        m = default_re.match(line)
        if m:
            declared_vars.add(m.group(1))

WHITELIST = set(declared_vars) | {
    "persistent", "renpy", "config", "store", "gui", "audio",
    "True", "False", "None", "max", "min", "len", "int", "str", "range",
    "day_title", "day_sub",  # параметры label day_card
    "OBJ",  # подстановка вместо renpy.* / persistent.* / config.* / _test.*
    "_return", "_args", "_kwargs",
    ## `_` — встроенная функция перевода Ren'Py (renpy.translation.translate_string),
    ## а не игровая переменная. Используется в script.rpy для карточек дня/концовки.
    "_",
}

assign_re = re.compile(r"^\s*\$\s*(.*)$")
ident_re = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")

for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = assign_re.match(line)
        if m:
            code = m.group(1)
            code = re.sub(r'"[^"]*"', '""', code)
            code = re.sub(r"\b(renpy|persistent|config|store|gui|audio|_test)\.[\w]+", "OBJ", code)
            code = re.sub(r"\b(renpy|persistent)\.", "", code)
            for ident in ident_re.findall(code):
                base = ident.split(".")[0]
                if ident not in WHITELIST and base not in WHITELIST:
                    warnings.append(f"{rel(path)}:{i} переменная '{ident}' не объявлена через default")

# ---------------------------------------------------------------------------
# 4.5 говорящий не должен быть зарезервированным оператором Ren'Py
#     (история бага: персонаж `voice` ломал парсер Ren'Py 8.5)
RENPY_RESERVED = {
    "play", "queue", "stop", "pause", "scene", "show", "hide", "with", "jump",
    "call", "return", "if", "elif", "else", "while", "pass", "menu", "label",
    "define", "default", "init", "python", "image", "screen", "style",
    "transform", "translate", "voice", "window", "camera", "at", "behind",
    "as", "on", "expression", "id", "in", "and", "or", "not", "early",
}
speaker_re = re.compile(r'^\s*(?P<who>[a-z_][a-z_0-9]*)\s+"')
## Список говорящих НЕ хардкодим, а читаем из самого проекта: единственное
## место объявления персонажей — characters.rpy (`define X = Character(...)`).
## Хардкод молча расходился с кодом: нового персонажа валидатор счёл бы
## опечаткой, а удалённого продолжал бы считать валидным.
character_define_re = re.compile(r'^\s*define\s+(?P<name>\w+)\s*=\s*Character\(')
KNOWN_SPEAKERS = {"narrator"}   # встроенный рассказчик Ren'Py
for _p in all_lines:
    for _line in all_lines[_p]:
        _m = character_define_re.match(_line)
        if _m:
            KNOWN_SPEAKERS.add(_m.group("name"))
## слова языка экранов и стилевые свойства — не говорящие
SCREEN_WORDS = {
    "text", "textbutton", "button", "add", "vbox", "hbox", "fixed", "frame",
    "window", "side", "viewport", "grid", "null", "key", "timer", "image",
    "input", "label", "bar", "vbar", "hbar", "use", "has", "if", "elif",
    "else", "for", "python", "in", "color", "background", "font", "outline_color",
    "text_color", "text_hover_color", "text_selected_color", "hover_background",
    "selected_background", "insensitive_background", "value", "action",
    ## ключевые слова test-языка Ren'Py (tests.rpy / tests_autogen.rpy)
    "click", "advance", "assert", "skip", "run", "keysym", "type", "scroll",
    "drag", "move", "exit", "pass", "until", "while", "screen", "label",
    "eval", "testcase", "testsuite", "teardown", "before", "parameter",
    "screenshot", "hover", "pause",
}
def style_block_lines(lines):
    """Номера строк (1-based) внутри блоков `style ...:` — там нет диалогов,
    а строки вида `hover_color "#..."` не являются «говорящий + текст»."""
    inside = set()
    block_indent = None
    style_start_re = re.compile(r"^\s*style\s+[\w.]+.*:\s*$")
    for i, line in enumerate(lines, 1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if block_indent is not None:
            if indent > block_indent:
                inside.add(i)
                continue
            block_indent = None
        if style_start_re.match(line):
            block_indent = indent
    return inside


for path, lines in all_lines.items():
    in_style = style_block_lines(lines)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or i in in_style:
            continue
        m = speaker_re.match(line)
        if m and m.group("who") not in KNOWN_SPEAKERS and m.group("who") not in SCREEN_WORDS:
            if m.group("who") in RENPY_RESERVED:
                errors.append(f"{rel(path)}:{i} говорящий '{m.group('who')}' — "
                              f"зарезервированный оператор Ren'Py")
            else:
                warnings.append(f"{rel(path)}:{i} неизвестный говорящий '{m.group('who')}'")

# ---------------------------------------------------------------------------
# 4.6 используем только официальные переменные config.*
CONFIG_WHITELIST = {
    "has_music", "has_sound", "has_voice", "language", "name", "version",
    "window_title", "about", "save_directory", "screens", "textbox_height",
    "main_menu_music", "history_length", "rollback_enabled", "quit_action",
    "allow_skipping", "developer", "screen_width", "screen_height",
    "default_music_volume", "default_sfx_volume", "default_voice_volume",
    "logfile", "enter_transition", "exit_transition", "intra_transition",
    "main_menu_music", "game_music", "help", "about", "license",
}
for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r"config\.([a-z_]+)\s*=", line):
            if m.group(1) not in CONFIG_WHITELIST and not line.strip().startswith("#"):
                errors.append(f"{rel(path)}:{i} config.{m.group(1)} не входит в белый список "
                              f"известных переменных Ren'Py")

# ---------------------------------------------------------------------------
# 4.65 gui.rpy обязан исполняться не позже screens.rpy (style default читает gui.*)
GUI = os.path.join(ROOT, "gui.rpy")
SCR = os.path.join(ROOT, "screens.rpy")
if os.path.exists(GUI) and os.path.exists(SCR):
    gui_off = 0
    scr_off = 0
    m = re.search(r"^\s*init offset\s*=\s*(-?\d+)", open(GUI, encoding="utf-8").read(), re.M)
    if m:
        gui_off = int(m.group(1))
    m = re.search(r"^\s*init offset\s*=\s*(-?\d+)", open(SCR, encoding="utf-8").read(), re.M)
    if m:
        scr_off = int(m.group(1))
    if "gui." in open(SCR, encoding="utf-8").read() and gui_off > scr_off:
        errors.append(f"gui.rpy (init offset {gui_off}) исполнится позже screens.rpy "
                      f"(init offset {scr_off}) — style-блоки не увидят gui.*")

# ---------------------------------------------------------------------------
# 4.64 шрифты gui.rpy: только комплект Ren'Py или файлы из game/gui/fonts/
RENPY_BUNDLED_FONTS = {
    "DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf",
    "DejaVuSans-BoldOblique.ttf",
}
if os.path.exists(GUI):
    for line in open(GUI, encoding="utf-8"):
        if line.strip().startswith("#"):
            continue
        m = re.match(r'\s*define\s+gui\.\w*font\w*\s*=\s*"([^"]+)"', line)
        if not m:
            continue
        fn = m.group(1)
        if fn in RENPY_BUNDLED_FONTS:
            continue
        if not os.path.exists(os.path.join(ROOT, fn)):
            errors.append(f"gui.rpy: шрифт '{fn}' не найден ни в комплекте Ren'Py, "
                          f"ни в game/{fn}")


# ---------------------------------------------------------------------------
# 4.65x ATL-ключевики не могут быть детьми screen-стейтмента text/add без трансформа
ATL_CHILD = re.compile(r'^\s*(linear|ease|easein|easeout|pause|repeat|parallel|choice|on|contains|animation)\s')
for path in FILES:
    lines = all_lines[path]
    for i, line in enumerate(lines):
        m = re.match(r'^(\s*)(text|add)\b.*:\s*$', line)
        if not m:
            continue
        base = len(m.group(1))
        for j in range(i + 1, min(i + 12, len(lines))):
            nxt = lines[j]
            if not nxt.strip() or nxt.strip().startswith("#"):
                continue
            ind = len(nxt) - len(nxt.lstrip())
            if ind <= base:
                break
            if ATL_CHILD.match(nxt):
                errors.append(f"{rel(path)}:{j+1} ATL-ключевик ребёнком у {m.group(2)}: "
                              f"вынесите в transform и подключите через at")
            break

# 4.66 Preference() только с именами, существующими в Ren'Py 8.5
PREF_WHITELIST = {
    "text speed", "auto-forward time", "after choices", "music volume",
    "sound volume", "voice volume", "display",
    "emphasize audio", "wait for voice", "voice sustain", "transitions",
    "skip transitions", "skip", "all",
}
for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'Preference\(\s*"([^"]+)"', line):
            if m.group(1) not in PREF_WHITELIST:
                errors.append(f"{rel(path)}:{i} Preference(\"{m.group(1)}\") — "
                              f"имя не из списка Ren'Py 8.5 (для тумблеров используйте "
                              f"значения: Preference(\"display\", \"fullscreen\") и т.п.)")

# ---------------------------------------------------------------------------
# 4.7 оконные свойства (background/padding) не должны стоять на контейнерах/тексте
SCREENS = os.path.join(ROOT, "screens.rpy")
if os.path.exists(SCREENS):
    cur = None
    for i, ln in enumerate(open(SCREENS, encoding="utf-8"), 1):
        st = ln.rstrip()
        if not st.strip() or st.strip().startswith("#"):
            continue
        indent = len(st) - len(st.lstrip())
        m = re.match(r"\s*(hbox|vbox|text|grid|fixed)\b.*:\s*$", st)
        if m:
            cur = (m.group(1), indent)
            continue
        pm = re.match(r"\s*(background|xpadding|ypadding|padding)\s", st)
        if pm and cur and indent == cur[1] + 4:
            errors.append(f"screens.rpy:{i} свойство '{pm.group(1)}' на контейнере "
                          f"'{cur[0]}' — нужен frame/window")

# ---------------------------------------------------------------------------
# 4.8 все play music / play sound указывают на существующие файлы
for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = re.match(r"play music (\w+)", stripped)
        if m:
            f = os.path.join(ROOT, "audio", m.group(1) + ".ogg")
            if not os.path.exists(f):
                errors.append(f"{rel(path)}:{i} нет файла музыки audio/{m.group(1)}.ogg")
        m = re.match(r"play sound (\w+)", stripped)
        if m:
            cands = (os.path.join(ROOT, "audio", "sfx", m.group(1) + ".ogg"),
                     os.path.join(ROOT, "audio", m.group(1) + ".ogg"))
            if not any(os.path.exists(c) for c in cands):
                errors.append(f"{rel(path)}:{i} нет файла звука audio/sfx/{m.group(1)}.ogg")

# ---------------------------------------------------------------------------
# 5-7. кавычки, музыка, латиница
# ---------------------------------------------------------------------------
say_re = re.compile(r'^\s*(?:(mc|lena|vera|zoya|radio|child|young_voice|voice|lena_e|sys|narrator)\s+)?"(.*)"\s*$')
latin_in_russian = re.compile(r"[А-Яа-яЁё]{2,}[\s]*[A-Za-z]{3,}|[A-Za-z]{3,}[\s]*[А-Яа-яЁё]{2,}")

for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        stripped = re.sub(r'\s+id\s+[\w]+', '', line).strip()
        if stripped.startswith("#"):
            continue
        if stripped.count('"') % 2 != 0:
            errors.append(f"{rel(path)}:{i} нечётное число кавычек: {stripped[:60]}")
        m = say_re.match(stripped)
        if m:
            text = m.group(2)
            stats["lines_dialogue"] += 1
            stats["words"] += len(text.split())
            if latin_in_russian.search(text):
                warnings.append(f"{rel(path)}:{i} подозрительная латиница в тексте: "
                                f"{latin_in_russian.search(text).group(0)!r}")

# проверка: в каждой сюжетной сцене есть scene + комментарий про музыку
label_pos = []
for path, lines in all_lines.items():
    for i, line in enumerate(lines, 1):
        m = label_re.match(line)
        if m:
            label_pos.append((path, i, m.group(1)))

for idx, (path, start, name) in enumerate(label_pos):
    end = len(all_lines[path]) + 1
    for npath, nstart, _n in label_pos[idx + 1:]:
        if npath == path:
            end = nstart
            break
    body = all_lines[path][start - 1:end - 1]
    text = "\n".join(body)
    if name in ("start", "day_card", "end_card", "determine_ending", "d2_night_check"):
        continue
    if "scene " not in text:
        warnings.append(f"{rel(path)}: сцена '{name}' не содержит оператора scene")
    if "play music" not in text and "stop music" not in text:
        warnings.append(f"{rel(path)}: сцена '{name}' без комментария-подсказки музыки")

# ---------------------------------------------------------------------------
# Отчёт
# ---------------------------------------------------------------------------
print("=" * 62)
print("ПРОВЕРКА ПРОЕКТА «ЛЕТО, КОТОРОГО НЕ БЫЛО»")
print("=" * 62)
print(f"Файлов .rpy:            {len(FILES)}")
print(f"Меток (label):          {stats['labels']}")
print(f"Сцен-образов (scene):   {stats['scenes']}")
print(f"Реплик/нарратива:       {stats['lines_dialogue']}")
print(f"Слов в тексте:          ~{stats['words']}")
print(f"Объявлено переменных:   {len(declared_vars)}")
print(f"Объявлено образов:      {len([x for x in declared_images if ' ' in x])}")
print("-" * 62)

if errors:
    print(f"\nОШИБКИ ({len(errors)}):")
    for e in errors:
        print("  ✗", e)
else:
    print("\nОШИБОК НЕ НАЙДЕНО ✓")

if warnings:
    print(f"\nПРЕДУПРЕЖДЕНИЯ ({len(warnings)}):")
    for w in warnings:
        print("  !", w)
else:
    print("ПРЕДУПРЕЖДЕНИЙ НЕТ ✓")

print()
sys.exit(1 if errors else 0)
