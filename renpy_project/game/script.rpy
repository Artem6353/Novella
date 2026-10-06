## ============================================================
## script.rpy
## «Лето, которого не было» — точка входа и служебные метки
##
## Проект САМОДОСТАТОЧЕН: папка renpy_project/ — это готовый проект
## Ren'Py 8 (game/ со своими gui.rpy, screens.rpy, options.rpy).
## Запуск: renpy.sh <путь>/renpy_project  (или добавить папку в список
## проектов Launcher'а). Установка в шаблонный проект — dist_pack/install.py.
## ВАЖНО: game/gui.rpy обязан остаться своим — в нём вызов gui.init(),
## без которого Ren'Py 8 не показывает главное меню (игра стартовала бы
## сразу со сцены, минуя меню).
## ============================================================

## Заголовок и версия задаются в options.rpy:
##     define config.name = _("Лето, которого не было / The Summer That Never Was")
##     define config.version = "1.2"

label start:

    ## Стартовая страховка: даже если игрок загрузил старое сохранение,
    ## счётчики не уедут в минус и не сложатся дважды.
    $ lineup_repeats = 0
    $ ending_shown = ""

    play music main_theme fadein 1.5 if_changed
    jump p01_room


## ------------------------------------------------------------
## Служебная метка: карточка дня.
## Вызывается как: call day_card("День 1", "Первая смена")
## ------------------------------------------------------------
label day_card(day_title="", day_sub=""):

    show screen chapter_card(day_title, day_sub) with dissolve
    pause 1.7
    hide screen chapter_card with dissolve

    return


## ------------------------------------------------------------
## Служебная метка: финальная карточка концовки.
## Перед вызовом положите название в $ ending_shown.
## ------------------------------------------------------------
label end_card:

    $ stats_line = "Фрагментов памяти найдено: [memory_fragments] из 6. Очков правды: [truth_points] из 10."

    show screen chapter_card("КОНЕЦ", ending_shown, stats_line) with dissolve
    pause 3.2
    hide screen chapter_card with dissolve

    stop music fadeout 2.0
    return
