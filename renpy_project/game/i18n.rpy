## ============================================================
## i18n.rpy — доперевод общего кода движка и страховки локализации
## ============================================================
##
## ЗАЧЕМ ЭТОТ ФАЙЛ НУЖЕН
## ------------------------------------------------------------
## 1. Подсказки подтверждения (layout.*) живут в renpy/common/00layout.rpy
##    и заданы там НА АНГЛИЙСКОМ, причём БЕЗ обёртки `_()`:
##        layout.QUIT = "Are you sure you want to quit?"
##    Раз `_()` нет, блок `translate english strings:` их не переводит —
##    строки нужно переопределять напрямую. Иначе в РУССКОМ режиме игрок
##    нажимает «Выход» / «Меню» / перезаписывает слот и получает
##    англоязычный вопрос внутри собственного confirm-экрана.
##
## 2. `translate <язык> python:` — единственный механизм, который движок
##    исполняет при смене языка: renpy/common/00start.rpy вызывает
##    renpy.change_language(language, force=True) при старте, а действие
##    Language(...) — при переключении. Оба прогона исполняют early-блоки
##    своего языка (renpy/translation/__init__.py::change_language).
##    Поэтому ниже ДВА блока: `translate None` (язык по умолчанию — русский)
##    и `translate english` (возвращает английские оригиналы).
##
## 3. Источник строк — tools/ui_strings.py::LAYOUT_PROMPTS. Содержимое
##    этого файла сверяется с ним в tools/gen_tl.py: при расхождении
##    генератор переводов падает с понятным сообщением.
## ============================================================

translate None python:
    layout.ARE_YOU_SURE = "Вы уверены?"
    layout.DELETE_SAVE = "Удалить это сохранение?"
    layout.OVERWRITE_SAVE = "Перезаписать это сохранение?"
    layout.LOADING = "Загрузка прервёт несохранённый прогресс.\nВы уверены, что хотите это сделать?"
    layout.QUIT = "Вы уверены, что хотите выйти из игры?"
    layout.MAIN_MENU = "Вернуться в главное меню?\nНесохранённый прогресс будет потерян."
    layout.CONTINUE = "Продолжить с того места, где вы остановились?"
    layout.END_REPLAY = "Завершить повтор?"
    layout.SLOW_SKIP = "Начать пропуск текста?"
    layout.FAST_SKIP_SEEN = "Пропустить текст до следующего выбора?"
    layout.FAST_SKIP_UNSEEN = "Пропустить непрочитанный текст до следующего выбора?"

translate english python:
    layout.ARE_YOU_SURE = "Are you sure?"
    layout.DELETE_SAVE = "Are you sure you want to delete this save?"
    layout.OVERWRITE_SAVE = "Are you sure you want to overwrite your save?"
    layout.LOADING = "Loading will lose unsaved progress.\nAre you sure you want to do this?"
    layout.QUIT = "Are you sure you want to quit?"
    layout.MAIN_MENU = "Are you sure you want to return to the main menu?\nThis will lose unsaved progress."
    layout.CONTINUE = "Are you sure you want to continue where you left off?"
    layout.END_REPLAY = "Are you sure you want to end the replay?"
    layout.SLOW_SKIP = "Are you sure you want to begin skipping?"
    layout.FAST_SKIP_SEEN = "Are you sure you want to skip to the next choice?"
    layout.FAST_SKIP_UNSEEN = "Are you sure you want to skip unseen dialogue to the next choice?"
