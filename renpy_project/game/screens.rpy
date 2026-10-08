## ============================================================
## screens.rpy — полный самодостаточный набор экранов Ren'Py 8
## (say / choice / confirm / main_menu / save / load / preferences /
##  history / about / notify / quick_menu)
## Палитра и размеры берутся из gui.rpy (раздел 28 ГДД).
## ВАЖНО: background/padding — свойства window-стилей, поэтому все подложки
## сделаны через frame, а не на hbox/vbox/text.
## ============================================================

init offset = -1

style default:
    font gui.interface_text_font
    size gui.interface_text_size
    color gui.interface_text_color
    xalign 0.0


## ------------------------------------------------------------
## ПОЛОСЫ И ПОЛЗУНКИ (bar / vbar / scrollbar / vscrollbar / slider)
## ------------------------------------------------------------
## ОБЯЗАТЕЛЬНЫЙ БЛОК. Базовый `style default` движка объявляет
##     fore_bar Null()
##     aft_bar  Null()
##     thumb    Null()
## то есть ПУСТОТУ. Пока проект не переопределил эти стили сам, любой
## `bar`/`vbar` рисуется невидимым. В этой игре это означало:
##   * в «Настройках» пять ползунков (скорость текста, авто-режим,
##     музыка, звуки, голос) не отображались вообще — игрок не видел
##     ни текущего значения, ни того, что сюда можно нажать;
##   * в игровом меню (Сохранение / Загрузка / История / Об игре)
##     полоса прокрутки `vbar value YScrollValue("gm_viewport")` была
##     невидимой, поэтому список из 8 слотов нельзя было прокрутить
##     глазами — только колесом мыши.
##
## Имена свойств: left_bar/right_bar — горизонталь (left_bar = заполненная
## часть), bottom_bar/top_bar — вертикаль, base_bar задаёт сразу обе
## половины (трек) и используется там, где есть перетаскиваемый thumb.
## Картинки не нужны — рисуем Solid'ами из палитры gui.rpy.
style bar:
    ysize gui.bar_size
    left_bar Solid(gui.accent_color)
    right_bar Solid("#f6f1e71f")
    hover_left_bar Solid("#ffd166")
    thumb None
    thumb_shadow None

style vbar:
    xsize gui.bar_size
    bottom_bar Solid(gui.accent_color)
    top_bar Solid("#f6f1e71f")
    hover_bottom_bar Solid("#ffd166")
    thumb None
    thumb_shadow None

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Solid("#f6f1e71f")
    thumb Solid(gui.idle_color)
    hover_thumb Solid(gui.accent_color)
    thumb_shadow None

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Solid("#f6f1e71f")
    thumb Solid(gui.idle_color)
    hover_thumb Solid(gui.accent_color)
    thumb_shadow None

style slider:
    ysize gui.bar_size
    base_bar Solid("#f6f1e71f")
    hover_base_bar Solid("#f6f1e733")
    thumb Solid(gui.accent_color)
    hover_thumb Solid("#ffd166")
    thumb_shadow None

style vslider:
    xsize gui.bar_size
    base_bar Solid("#f6f1e71f")
    hover_base_bar Solid("#f6f1e733")
    thumb Solid(gui.accent_color)
    hover_thumb Solid("#ffd166")
    thumb_shadow None


## ------------------------------------------------------------
## ЭКРАН ДИАЛОГА
## ------------------------------------------------------------
screen say(who, what):

    window id "window":
        background Frame("gui/box_frame.png", 26, 26, 26, 26)
        xalign 0.5
        yalign 0.985
        xmaximum 1560
        ymaximum gui.textbox_height
        xpadding 44
        ypadding 20

        vbox:
            xalign 0.5
            yalign 0.5
            xmaximum gui.textbox_inner_width
            spacing 8

            if who:
                frame:
                    background Solid("#e0a458e8")
                    xpadding 16
                    ypadding 3
                    xalign 0.0
                    text who id "who" font gui.name_font size 26 color "#241505"

            text what id "what" font gui.text_font size gui.text_size line_spacing 4


## ------------------------------------------------------------
## БЫСТРОЕ МЕНЮ (поверх игрового экрана)
## ВАЖНО: подключается как overlay-экран (init-блок ниже), а НЕ через
## `use quick_menu` внутри screen say: на экранах выбора (menu/choice)
## screen say не показывается, и встроенное туда быстрое меню исчезало
## ровно тогда, когда оно нужнее всего (и ломало автотесты).
## Overlay-экраны движок сам скрывает в главном/игровом меню.
## ------------------------------------------------------------
screen quick_menu():

    zorder 100

    if quick_menu:

        hbox:
            xalign 1.0
            yalign 1.0
            xoffset -12
            yoffset -6
            spacing 14

            textbutton _("История") action ShowMenu("history") text_size 15 text_color "#f6f1e775" text_hover_color "#ffb703"
            textbutton _("Сохранить") action ShowMenu("save") text_size 15 text_color "#f6f1e775" text_hover_color "#ffb703"
            textbutton _("Загрузить") action ShowMenu("load") text_size 15 text_color "#f6f1e775" text_hover_color "#ffb703"
            textbutton _("Настройки") action ShowMenu("preferences") text_size 15 text_color "#f6f1e775" text_hover_color "#ffb703"
            textbutton _("Пропуск") action Skip() text_size 15 text_color "#f6f1e775" text_hover_color "#ffb703"
            textbutton _("Меню") action MainMenu() text_size 15 text_color "#f6f1e775" text_hover_color "#ffb703"


## Быстрое меню показывается в игре всегда, когда игрок не в меню
## (штатный механизм Ren'Py — config.overlay_screens).
init python:
    config.overlay_screens.append("quick_menu")


## Флаг позволяет сценам временно прятать быстрое меню:
## $ quick_menu = False
default quick_menu = True


## ------------------------------------------------------------
## ВЫБОРЫ
## ------------------------------------------------------------
screen choice(items):

    vbox:
        xalign 0.045
        yalign 0.34
        xmaximum 820
        spacing 10

        for i in items:
            textbutton i.caption action i.action:
                background Solid("#0e1219cc")
                hover_background Solid("#1c2432e8")
                xfill True
                ypadding 12
                xpadding 22
                text_color "#f2ead8"
                text_hover_color "#ffb703"
                text_size 26
                text_xalign 0.0
                text_font gui.text_font


## ------------------------------------------------------------
## ПОДТВЕРЖДЕНИЕ (выход, перезапись слота и т.п.)
## ------------------------------------------------------------
screen confirm(message, yes_action, no_action):

    modal True
    zorder 200

    add Solid("#000000b8")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 28
        xmaximum 1100

        text message xalign 0.5 size 32 color gui.paper font gui.text_font

        hbox:
            xalign 0.5
            spacing 28

            textbutton _("Да") action yes_action:
                xpadding 26
                ypadding 10
                background Solid("#f6f1e7e8")
                text_color gui.ink
                text_hover_color "#8a5a00"
                text_size 28

            textbutton _("Нет") action no_action:
                xpadding 26
                ypadding 10
                background Solid("#f6f1e7e8")
                text_color gui.ink
                text_hover_color "#8a5a00"
                text_size 28


## ------------------------------------------------------------
## ГЛАВНОЕ МЕНЮ
## ------------------------------------------------------------
screen main_menu():

    tag menu

    if renpy.loadable(gui.main_menu_background):
        add gui.main_menu_background
    else:
        add Solid("#1b2b23")
    add Solid("#00000030")

    vbox:
        xalign 0.055
        yalign 0.60
        spacing 10

        textbutton _("Начать игру") action Start() style "mm_button"
        textbutton _("Продолжить") action Continue() style "mm_button"
        textbutton _("Загрузить") action ShowMenu("load") style "mm_button"
        textbutton _("Настройки") action ShowMenu("preferences") style "mm_button"
        textbutton _("Об игре") action ShowMenu("about") style "mm_button"
        textbutton _("Выход") action Quit() style "mm_button"

    ## Версия берётся из config.version (options.rpy), а не хардкодится:
    ## иначе номер в меню и номер сборки разъезжаются (ранее здесь было
    ## захардкожено v1.1 при config.version = "0.9-demo" и релизе v1.2).
    text "v[config.version] · RU/EN · HTML5: web_demo/index.html":
        xalign 0.99
        yalign 0.985
        size 17
        color "#ffffff66"


style mm_button is button:
    background Solid("#0e1219b4")
    hover_background Solid("#1c2432d8")
    xminimum 400
    ypadding 10
    xpadding 26

## В Ren'Py 8.5 текст кнопки оформляется отдельным стилем <имя>_text:
## свойства text_* внутри блока style недопустимы (ошибка разбора).
style mm_button_text is text:
    font gui.interface_text_font
    size 28
    color "#f2ead8"
    hover_color "#ffb703"
    xalign 0.0


## ------------------------------------------------------------
## КАРТОЧКА ГЛАВЫ / КОНЦОВКИ
## ------------------------------------------------------------
screen chapter_card(title, sub="", stats=""):

    zorder 150

    add "gui/card_bg.jpg"

    fixed:
        add Solid("#e0a458cc") xalign 0.5 yalign 0.345 xsize 460 ysize 2
        add Solid("#e0a458cc") xalign 0.5 yalign 0.60 xsize 460 ysize 2

    vbox:
        xalign 0.5
        yalign 0.47
        spacing 16

        text title font "gui/fonts/PTSerif-BoldItalic.ttf" size 76 color "#f4e9d2" xalign 0.5 text_align 0.5
        if sub:
            text sub font "gui/fonts/PTSans-Italic.ttf" size 30 color "#d9b982" xalign 0.5 text_align 0.5
        if stats:
            null height 8
            text stats font gui.interface_text_font size 26 color "#cbb98a" xalign 0.5 text_align 0.5


screen game_menu(title):

    modal True
    tag menu

    if renpy.loadable(gui.game_menu_background):
        add gui.game_menu_background
    else:
        add Solid("#0d0f12")
    add Solid("#0d0f12e0")

    vbox:
        xalign 0.5
        ypos 26
        spacing 10

        text title font gui.name_font size 42 color gui.accent_color xalign 0.5

        hbox:
            xalign 0.5
            spacing 18

            textbutton _("Назад") action Return():
                xpadding 20
                ypadding 6
                background Solid("#f6f1e722")
                text_color gui.paper
                text_hover_color gui.accent_color
                text_size 22

            textbutton _("В главное меню") action MainMenu():
                xpadding 20
                ypadding 6
                background Solid("#f6f1e722")
                text_color gui.paper
                text_hover_color gui.accent_color
                text_size 22

            textbutton _("Справка") action ShowMenu("help"):
                xpadding 20
                ypadding 6
                background Solid("#f6f1e722")
                text_color gui.paper
                text_hover_color gui.accent_color
                text_size 22

    side "c r":
        xalign 0.5
        yalign 0.56
        xmaximum 1500
        ymaximum 840

        viewport id "gm_viewport":
            mousewheel True
            draggable True

            vbox:
                xalign 0.5
                spacing 14
                transclude

        vbar value YScrollValue("gm_viewport") xsize 14


## ------------------------------------------------------------
## СЛОТ (общий блок для сохранения и загрузки)
## ------------------------------------------------------------
screen slot_row(i, save_mode):

    frame:
        background Solid("#f6f1e714")
        xpadding 16
        ypadding 8
        xfill True

        hbox:
            spacing 16

            if save_mode:
                textbutton _("Слот [i]") action FileSave(i):
                    text_size 26
                    text_color gui.paper
                    text_hover_color gui.accent_color
            else:
                textbutton _("Слот [i]") action FileLoad(i):
                    text_size 26
                    text_color gui.paper
                    text_hover_color gui.accent_color

            text FileTime(i, empty=_("— пусто —")):
                size 20
                color "#c9c2b4"
                yalign 0.5


## ------------------------------------------------------------
## СОХРАНЕНИЕ
## ------------------------------------------------------------
screen save():

    use game_menu(_("Сохранение")):

        vbox:
            spacing 12
            xsize 1200

            for i in range(1, 9):
                use slot_row(i, True)


## ------------------------------------------------------------
## ЗАГРУЗКА
## ------------------------------------------------------------
screen load():

    use game_menu(_("Загрузка")):

        vbox:
            spacing 12
            xsize 1200

            for i in range(1, 9):
                use slot_row(i, False)


## ------------------------------------------------------------
## НАСТРОЙКИ
## ------------------------------------------------------------
screen preferences():

    use game_menu(_("Настройки")):

        vbox:
            spacing 20
            xsize 1000

            text _("Текст") size 28 color "#ffd166"

            hbox:
                spacing 16

                text _("Скорость вывода") size 24 yalign 0.5

                bar value Preference("text speed") xsize 420 ysize 22 yalign 0.5

            hbox:
                spacing 16

                text _("Авто-режим: пауза") size 24 yalign 0.5

                bar value Preference("auto-forward time") xsize 420 ysize 22 yalign 0.5

            hbox:
                spacing 16

                text _("Пропуск после выборов") size 24 yalign 0.5

                textbutton _("останавливаться") action Preference("after choices", "stop"):
                    text_size 22
                    text_color gui.paper
                    text_hover_color gui.accent_color
                    text_selected_color gui.accent_color

                textbutton _("продолжать") action Preference("after choices", "keep"):
                    text_size 22
                    text_color gui.paper
                    text_hover_color gui.accent_color
                    text_selected_color gui.accent_color

            text _("Прохождение") size 28 color "#ffd166"

            hbox:
                spacing 16

                textbutton _("Пропускать нечитанный текст") action Preference("skip unseen", "toggle"):
                    text_size 22
                    text_color gui.paper
                    text_hover_color gui.accent_color
                    text_selected_color gui.accent_color

            text _("Звук") size 28 color "#ffd166"

            hbox:
                spacing 16

                text _("Музыка") size 24 yalign 0.5

                bar value Preference("music volume") xsize 420 ysize 22 yalign 0.5

            hbox:
                spacing 16

                text _("Звуки") size 24 yalign 0.5

                bar value Preference("sound volume") xsize 420 ysize 22 yalign 0.5

            hbox:
                spacing 16

                text _("Голос") size 24 yalign 0.5

                bar value Preference("voice volume") xsize 420 ysize 22 yalign 0.5

            text _("Экран и язык") size 28 color "#ffd166"

            hbox:
                spacing 16

                text _("Экран") size 24 yalign 0.5

                textbutton _("окно") action Preference("display", "window"):
                    text_size 22
                    text_color gui.paper
                    text_hover_color gui.accent_color
                    text_selected_color gui.accent_color

                textbutton _("полный") action Preference("display", "fullscreen"):
                    text_size 22
                    text_color gui.paper
                    text_hover_color gui.accent_color
                    text_selected_color gui.accent_color

            hbox:
                spacing 16

                textbutton _("Русский") action Language(None):
                    xpadding 18
                    ypadding 6
                    background Solid("#f6f1e722")
                    text_size 22
                    text_color gui.paper
                    text_selected_color gui.accent_color

                textbutton _("English") action Language("english"):
                    xpadding 18
                    ypadding 6
                    background Solid("#f6f1e722")
                    text_size 22
                    text_color gui.paper
                    text_selected_color gui.accent_color


## ------------------------------------------------------------
## ИСТОРИЯ ДИАЛОГОВ
## ------------------------------------------------------------
screen history():

    use game_menu(_("История диалогов")):

        vbox:
            spacing 16
            xsize 1300

            if _history_list:

                for h in _history_list:

                    frame:
                        background Solid("#f6f1e710")
                        xpadding 16
                        ypadding 10
                        xfill True

                        vbox:
                            spacing 4

                            if h.who:
                                text h.who font gui.name_font size 24 color "#ffd166"

                            text h.what font gui.text_font size 22 color gui.paper

            else:
                text _("История пуста.") size 24 color "#c9c2b4"


## ------------------------------------------------------------
## ОБ ИГРЕ
## ------------------------------------------------------------
screen about():

    use game_menu(_("Об игре")):

        vbox:
            spacing 14
            xsize 1200

            text _("«Лето, которого не было» — визуальная новелла по дизайн-документу 3.0.") size 26 color gui.paper

            text _("Движок: Ren'Py [renpy.version_only].") size 22 color "#c9c2b4"

            text _("Текст и звуковой дизайн — оригинальные. Арт: полуреалистичная живописная стилистика, 1990-е, постсоветский лагерь.") size 22 color "#c9c2b4"

            text _("Музыка: Kevin MacLeod (incompetech.com) — Morning, Carefree, Gymnopédie No. 1, Cheery Monday, Laid Back Guitars, Darkling, Inspired, Heartbreaking, Village Consort. Лицензия CC-BY 3.0.") size 22 color "#c9c2b4"

            text _("Прошлое нужно не удерживать, а отпускать.") size 24 color "#ffd166"


## ------------------------------------------------------------
## УВЕДОМЛЕНИЯ (быстрое сохранение и т.п.)
## ------------------------------------------------------------
screen notify(message):

    zorder 150

    vbox:
        xalign 0.5
        yalign 0.06

        frame:
            background Solid("#f6f1e7dd")
            xpadding 18
            ypadding 8

            text message:
                size 22
                color gui.ink

    timer 2.0 action Hide("notify")


## ------------------------------------------------------------
## ИНДИКАТОР ПРОПУСКА (скип) — штатное имя экрана, движок показывает
## его сам во время пропуска (практика tutorial_screens.rpy).
## ------------------------------------------------------------
screen skip_indicator():

    zorder 100

    hbox:
        xalign 0.5
        yalign 0.03
        spacing 8

        text _("Пропуск…") size 24 color gui.accent_color:
            linear 0.6 alpha 0.35
            linear 0.6 alpha 1.0
            repeat


## ------------------------------------------------------------
## СПРАВКА (по образцу help/keyboard_help/mouse_help из tutorial)
## ------------------------------------------------------------
screen help():

    tag menu

    use game_menu(_("Справка")):

        vbox:
            xalign 0.5
            spacing 14

            text _("Клавиатура") size 28 color "#ffd166"

            text _("Enter — подтвердить / продолжить;  Пробел — продолжить;  Esc — меню;  Колесо — история диалогов;  Ctrl — пропуск;  Tab — скрыть текст (self-voicing режим: Shift+Alt+S).") size 22 color gui.paper

            text _("Мышь") size 28 color "#ffd166"

            text _("ЛКМ — подтвердить;  ПКМ — игровое меню;  Колесо — история;  Средняя кнопка — скрыть интерфейс.") size 22 color gui.paper

            text _("Быстрое меню (под текстом)") size 28 color "#ffd166"

            text _("Сохранить / Загрузить / Настройки / История / Меню — одним нажатием.") size 22 color gui.paper


init offset = 0
