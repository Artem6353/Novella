init offset = -1

## ============================================================
## gui.rpy — значения интерфейса (палитра из раздела 28 ГДД)
## Используются только штатные шрифты дистрибутива Ren'Py (DejaVu),
## чтобы сборка работала без внешних файлов шрифтов.
## ============================================================

## ОБЯЗАТЕЛЬНО: штатная инициализация GUI (как в шаблоне Ren'Py 8).
## Без gui.init() движок не загружает модуль _layout/screen_main_menu,
## метка main_menu_screen не появляется — и главное меню НЕ показывается:
## игра сразу прыгает в label start. Кроме того, gui.init() задаёт
## виртуальный размер экрана, сбрасывает стили и включает layout.defaults().
init python:
    gui.init(1920, 1080)

## --- Шрифты ---
## В поставке Ren'Py гарантированно есть только семейство DejaVuSans.
## Хотите PT Serif / PT Sans (раздел 28 ГДД) — положите файлы в game/gui/fonts/
## и поправьте три define ниже, например:
##     define gui.text_font = "gui/fonts/PTSerif-Regular.ttf"
define gui.text_font = "gui/fonts/PTSans-Regular.ttf"
define gui.name_font = "gui/fonts/PTSans-Bold.ttf"
define gui.interface_text_font = "gui/fonts/PTSans-Regular.ttf"

## --- Размеры ---
define gui.text_size = 30
define gui.name_text_size = 32
define gui.interface_text_size = 26
define gui.label_text_size = 34
define gui.notify_text_size = 24
define gui.title_text_size = 56

## --- Палитра (раздел 28 ГДД) ---
define gui.paper = "#f6f1e7"        ## молочная бумага
define gui.ink = "#1f1b16"          ## тёмный графит
define gui.accent_color = "#ffb703" ## закатный янтарь
define gui.pine_color = "#2d6a4f"   ## сосновый зелёный
define gui.mystic_color = "#5e548e" ## сумеречный фиолетовый
define gui.danger_color = "#9d4c4c" ## приглушённый красный

define gui.text_color = "#f6f1e7"
define gui.interface_text_color = "#f6f1e7"
define gui.idle_color = "#c9c2b4"
define gui.hover_color = "#ffb703"
define gui.selected_color = "#ffb703"
define gui.insensitive_color = "#6f6a60"

## --- Диалоговое окно ---
define gui.textbox_height = 232
define gui.textbox_x_margin = 60
define gui.textbox_inner_width = 1472

## --- Кнопки выбора ---
define gui.choice_width = 900
define gui.choice_spacing = 12

## --- Фоны меню (кладутся install.py / лежат в game/gui/) ---
define gui.main_menu_background = "gui/main_menu.png"
define gui.game_menu_background = "gui/game_menu.png"
