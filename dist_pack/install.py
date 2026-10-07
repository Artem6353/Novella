#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install.py — устанавливает игру в существующий проект Ren'Py 8.

ПРИЧИНА ПОЯВЛЕНИЯ: если после копирования файлов игра всё равно показывает
Эйлин и «Вы создали новую игру Ren'Py», значит в проекте остался ШАБЛОННЫЙ
game/script.rpy со своим label start — он переопределяет нашу точку входа.
Этот скрипт убирает конфликт автоматически.

Использование:
    python3 install.py /путь/к/вашему/проекту/RenPy

Что делает:
  1. Проверяет, что по пути есть папка game/.
  2. Делает резервную копию шаблонного script.rpy (_template_script.rpy.bak).
  3. Удаляет шаблонные авто-изображения (bg *.png, eileen *.png), которые
     конфликтуют с нашими явными `image ...` в images.rpy.
  4. Копирует наши .rpy, images/ и tl/ поверх.
  5. Правит options.rpy (название/версия) и gui.rpy (палитра) — ТОЛЬКО если
     этих файлов не было в комплекте: свои options.rpy/gui.rpy из поставки
     самодостаточны (gui.rpy включает обязательный gui.init()).
"""

import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_GAME = os.path.join(HERE, "game")

PALETTE = {
    "gui.accent_color": "#ffb703",
    "gui.idle_color": "#f6f1e7",
    "gui.idle_small_color": "#c9c2b4",
    "gui.hover_color": "#ffd166",
    "gui.selected_color": "#ffb703",
    "gui.insensitive_color": "#6f6a60",
    "gui.text_color": "#f6f1e7",
    "gui.interface_text_color": "#f6f1e7",
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    proj = os.path.abspath(sys.argv[1])
    game = os.path.join(proj, "game")
    if not os.path.isdir(game):
        print(f"ОШИБКА: не найдена папка game/ в {proj}")
        sys.exit(2)
    if not os.path.isdir(SRC_GAME):
        print(f"ОШИБКА: не найден исходный game/ рядом со скриптом: {SRC_GAME}")
        sys.exit(2)

    # 1. резервная копия шаблонного script.rpy
    tpl = os.path.join(game, "script.rpy")
    if os.path.exists(tpl):
        bak = os.path.join(game, "_template_script.rpy.bak")
        shutil.move(tpl, bak)
        print(f"[1] шаблонный script.rpy -> {os.path.basename(bak)}")

    # 2. убрать шаблонные авто-изображения, конфликтующие с images.rpy
    img_dir = os.path.join(game, "images")
    removed = 0
    if os.path.isdir(img_dir):
        for root, _, files in os.walk(img_dir):
            for fn in files:
                low = fn.lower()
                if low.startswith("bg ") or low.startswith("eileen"):
                    os.remove(os.path.join(root, fn))
                    removed += 1
    print(f"[2] удалено шаблонных авто-изображений: {removed}")

    # 3. копирование наших файлов
    ## Артефакты прогонов движка и резервные копии в чужой проект попадать
    ## не должны: скомпилированные .rpyc от другой версии Ren'Py путают кэш,
    ## а log.txt/traceback.txt пугают игрока. В релизный dist_pack/game их
    ## не пускает tools/make_release_zip.py, но install.py иногда запускают
    ## прямо из рабочей копии, где они появляются после любого прогона.
    skip_dirs = {"cache", "saves", "__pycache__"}
    skip_files = {"log.txt", "errors.txt", "traceback.txt",
                  "prepare_result.txt", "dialogue.txt"}
    skip_suffixes = (".rpyc", ".rpymc", ".rpyb", ".pyc", ".bak")

    copied = 0
    for root, dirnames, files in os.walk(SRC_GAME):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        rel = os.path.relpath(root, SRC_GAME)
        dst_root = os.path.join(game, rel) if rel != "." else game
        os.makedirs(dst_root, exist_ok=True)
        for fn in files:
            if fn in skip_files or fn.endswith(skip_suffixes):
                continue
            shutil.copyfile(os.path.join(root, fn), os.path.join(dst_root, fn))
            copied += 1
    print(f"[3] скопировано файлов: {copied}")

    # 4. options.rpy: название и версия — правим ТОЛЬКО если в комплекте
    #    не было своего options.rpy (иначе затрём каноничный из поставки).
    opt = os.path.join(game, "options.rpy")
    if os.path.exists(opt) and not os.path.exists(os.path.join(SRC_GAME, "options.rpy")):
        s = open(opt, encoding="utf-8").read()
        s2, n1 = re.subn(r'define config\.name\s*=\s*_\(".*?"\)',
                         'define config.name = _("Лето, которого не было / The Summer That Never Was")', s)
        s2, n2 = re.subn(r'define config\.version\s*=\s*"[^"]*"',
                         'define config.version = "1.3.0"', s2)
        if not n1:
            s2 += '\ndefine config.name = _("Лето, которого не было / The Summer That Never Was")\n'
        if not n2:
            s2 += '\ndefine config.version = "1.3.0"\n'
        open(opt, "w", encoding="utf-8").write(s2)
        print("[4] options.rpy: название и версия обновлены")
    else:
        print("[4] options.rpy: взят из комплекта (название/версия уже заданы)")

    # 5. gui.rpy: палитра — только если своего gui.rpy в комплекте не было.
    #    Наш gui.rpy самодостаточен (включая gui.init() — без него Ren'Py 8
    #    не показывает главное меню), поэтому перезаписывать его палитру
    #    значениями из PALETTE нельзя.
    gui = os.path.join(game, "gui.rpy")
    if os.path.exists(gui) and not os.path.exists(os.path.join(SRC_GAME, "gui.rpy")):
        s = open(gui, encoding="utf-8").read()
        hits = 0
        for var, color in PALETTE.items():
            s, n = re.subn(r'define %s\s*=\s*"[^"]*"' % re.escape(var),
                           f'define {var} = "{color}"', s)
            hits += n
        open(gui, "w", encoding="utf-8").write(s)
        print(f"[5] gui.rpy: заменено цветовых значений: {hits}")
    else:
        print("[5] gui.rpy: взят из комплекта (палитра ГДД уже в нём)")

    print()
    print("ГОТОВО. Запустите проект в Ren'Py Launcher -> Launch Project.")
    print("Если launcher держит проект открытым — сначала закройте и откройте заново,")
    print("чтобы Ren'Py перечитал файлы и кэш (или Delete Persistent/Cache в launcher).")


if __name__ == "__main__":
    main()
