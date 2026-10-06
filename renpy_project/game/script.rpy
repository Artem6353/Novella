## ============================================================
## script.rpy
## «Лето, которого не было» — точка входа и служебные метки
##
## Проект рассчитан на установку в НОВЫЙ проект Ren'Py 8:
##   1. Создайте проект в Ren'Py Launcher (шаблон «пустой»).
##   2. Скопируйте содержимое папки game/ в game/ вашего проекта.
##   3. gui.rpy / screens.rpy / options.rpy оставьте из шаблона,
##      а цвета и шрифты поправьте по docs/07_ТЗ_UI.md (раздел 28 ГДД).
## ============================================================

## Заголовок и версию поменяйте в options.rpy вашего проекта:
##     define config.name = _("Лето, которого не было")
##     define gui.about = "Версия 0.9 (демо)"

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
