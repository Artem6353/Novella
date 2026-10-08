# -*- coding: utf-8 -*-
"""
ui_strings.py — ЕДИНЫЙ словарь интерфейсных строк RU → EN.

Зачем этот файл нужен
---------------------
Раньше локализация интерфейса жила только в `EX` внутри tools/build_web.py,
то есть переводил исключительно HTML5-плеер. Ren'Py-проект при этом брал
переводы из tools/translations.py по `id`, а у интерфейсных строк id нет —
они переводятся блоком `translate english strings:` (сопоставлением по
точной русской строке). В результате в английском режиме Ren'Py оставались
русскими:

  * главное меню, быстрое меню, confirm-диалог;
  * экраны «Сохранение» / «Загрузка» / «История» / «Об игре» / «Настройки»;
  * карточки дней (`call day_card("День 1", "Трещины")`);
  * заголовок «КОНЕЦ» и строка статистики на финальной карточке;
  * названия всех семи концовок (`ending_shown`);
  * имена говорящих (Артём / Лена / Вера / Зоя / Радио / Ребёнок / Голос).

Теперь и web-плеер, и Ren'Py берут переводы из одного места.

Кто использует
--------------
  tools/build_web.py  — сериализует EX в web_demo/index.html (как и раньше);
  tools/gen_tl.py     — печатает UI_STRINGS в блок `translate english strings:`
                        в renpy_project/game/tl/english/game.rpy и проверяет,
                        что каждая интерфейсная строка кода покрыта переводом.

Как добавлять строку
--------------------
1. Добавьте пару в UI_STRINGS (или в соответствующий подсловарь EX, если
   строка нужна и web-плееру).
2. Перезапустите `python3 tools/gen_tl.py` и `python3 tools/build_web.py`.
"""

import collections

# =============================================================================
# 1. Словарь web-плеера (перенесён из tools/build_web.py без изменений —
#    index.html после переноса собирается байт-в-байт тем же).
# =============================================================================

EX = {
    "ui": {
        "new":      {"ru": "Начать игру", "en": "New game"},
        "continue": {"ru": "Продолжить", "en": "Continue"},
        "language": {"ru": "Язык", "en": "Language"},
        "about_b":  {"ru": "Об игре", "en": "About"},
        "tagline":  {"ru": "Лагерь «Сосновый берег» закрыли двадцать лет назад. Но смена там всё ещё идёт — и линейка начнётся в семь.",
                     "en": "Pine Shore camp was closed twenty years ago. But the shift is still running — and the line-up starts at seven."},
        "history":  {"ru": "История", "en": "History"},
        "save":     {"ru": "Сохранить", "en": "Save"},
        "load":     {"ru": "Загрузить", "en": "Load"},
        "settings": {"ru": "Настройки", "en": "Settings"},
        "menu":     {"ru": "В меню", "en": "Title"},
        "speed":    {"ru": "Скорость текста", "en": "Text speed"},
        "about":    {"ru": "«Лето, которого не было» — визуальная новелла по дизайн-документу 3.0. "
                          "HTML5-демо собрано из того же сценария, что и Ren'Py-проект. "
                          "Полная английская локализация: все дни и все семь концовок. "
                          "Управление: клик / пробел / Enter — дальше, Esc — закрыть панель.",
                     "en": "The Summer That Never Was — a visual novel based on design document 3.0. "
                           "This HTML5 demo runs the same script as the Ren'Py project. "
                           "Fully localized in English: all days and all seven endings. "
                           "Controls: click / Space / Enter — advance, Esc — close panel."},
        "the_end":  {"ru": "КОНЕЦ", "en": "THE END"},
        "auto":     {"ru": "Автосохранение", "en": "Autosave"},
        "slot":     {"ru": "Слот", "en": "Slot"},
        "empty":    {"ru": "пусто", "en": "empty"},
        "music_vol": {"ru": "Музыка", "en": "Music"},
        "sfx_vol":  {"ru": "Звуки", "en": "Sounds"},
        "fullscreen": {"ru": "Полный экран", "en": "Fullscreen"},
    },
    "stats": {
        "ru": "Фрагментов памяти найдено: [memory_fragments] из 6. Очков правды: [truth_points] из 10.",
        "en": "Memory fragments found: [memory_fragments] of 6. Truth points: [truth_points] of 10.",
    },
    "names": {
        "mc":   {"ru": "Артём", "en": "Artyom"},
        "lena": {"ru": "Лена", "en": "Lena"},
        "vera": {"ru": "Вера", "en": "Vera"},
        "zoya": {"ru": "Зоя", "en": "Zoya"},
        "radio": {"ru": "Радио", "en": "Radio"},
        "child": {"ru": "Ребёнок", "en": "A kid"},
        "voice": {"ru": "Голос", "en": "A voice"},
        "young_voice": {"ru": "Голос", "en": "A voice"},
        "lena_e": {"ru": "Лена (?)", "en": "Lena (?)"},
        "sys":  {"ru": "", "en": ""},
        "card": {"ru": "", "en": ""},
    },
    "colors": {
        "mc": "#8fd18f", "lena": "#c8a2ff", "vera": "#ffd166", "zoya": "#8ecae6",
        "radio": "#e08a8a", "child": "#7fc7a0", "voice": "#a99ae0", "young_voice": "#a99ae0", "lena_e": "#c8a2ff",
        "narr": "#f6f1e7",
    },
    "days": {
        "Пролог": {"ru": "Пролог", "en": "Prologue"},
        "День 0": {"ru": "День 0", "en": "Day 0"},
        "День 1": {"ru": "День 1", "en": "Day 1"},
        "День 2": {"ru": "День 2", "en": "Day 2"},
        "День 3": {"ru": "День 3", "en": "Day 3"},
        "День 4": {"ru": "День 4", "en": "Day 4"},
        "День 5": {"ru": "День 5", "en": "Day 5"},
        "Последнее лето начинается": {"ru": "Последнее лето начинается", "en": "The last summer begins"},
        "Смена продолжается": {"ru": "Смена продолжается", "en": "The shift goes on"},
        "Трещины": {"ru": "Трещины", "en": "Cracks"},
        "Разделение": {"ru": "Разделение", "en": "The Parting"},
        "Правда": {"ru": "Правда", "en": "The Truth"},
        "Последний рассвет": {"ru": "Последний рассвет", "en": "The Last Dawn"},
    },
    "endings": {
        "Истинная концовка: «Последняя линейка»": {"ru": "Истинная концовка: «Последняя линейка»", "en": "True ending: The Last Line-Up"},
        "Концовка Лены: «Останься до утра»": {"ru": "Концовка Лены: «Останься до утра»", "en": "Lena's ending: Stay Till Morning"},
        "Концовка Веры: «Голос в эфире»": {"ru": "Концовка Веры: «Голос в эфире»", "en": "Vera's ending: A Voice on Air"},
        "Концовка Зои: «Рисунок на память»": {"ru": "Концовка Зои: «Рисунок на память»", "en": "Zoya's ending: A Painting to Remember"},
        "Нейтральная концовка: «Прощание без прощания»": {"ru": "Нейтральная концовка: «Прощание без прощания»", "en": "Neutral ending: A Farewell Without Goodbyes"},
        "Плохая концовка: «Забытый»": {"ru": "Плохая концовка: «Забытый»", "en": "Bad ending: The Forgotten"},
        "Секретная концовка: «Билет на двоих»": {"ru": "Секретная концовка: «Билет на двоих»", "en": "Secret ending: A Ticket for Two"},
    },
}


# =============================================================================
# 2. Строки, общие для web-плеера и Ren'Py. Собираются из EX, чтобы перевод
#    не мог «разъехаться» между двумя версиями игры.
# =============================================================================

def _from_ex():
    pairs = collections.OrderedDict()

    # Имена говорящих: в Ren'Py их переводит renpy.substitutions.substitute()
    # (Character.name проходит через translate_string), поэтому достаточно
    # попадания строки в блок `translate english strings:`.
    for entry in EX["names"].values():
        if entry["ru"] and entry["ru"] != entry["en"]:
            pairs[entry["ru"]] = entry["en"]

    # Карточки дней и подзаголовки
    for entry in EX["days"].values():
        if entry["ru"] != entry["en"]:
            pairs[entry["ru"]] = entry["en"]

    # Названия концовок (ending_shown)
    for entry in EX["endings"].values():
        pairs[entry["ru"]] = entry["en"]

    # Заголовок и статистика финальной карточки
    pairs[EX["ui"]["the_end"]["ru"]] = EX["ui"]["the_end"]["en"]
    pairs[EX["stats"]["ru"]] = EX["stats"]["en"]

    return pairs


# =============================================================================
# 3. Полный словарь Ren'Py: RU → EN.
#    Ключи ДОЛЖНЫ байт-в-байт совпадать со строками в `_()` из screens.rpy,
#    с аргументами `call day_card(...)` и со значениями `ending_shown`.
#    tools/gen_tl.py проверяет это и падает при расхождении.
# =============================================================================

UI_STRINGS = _from_ex()

UI_STRINGS.update(collections.OrderedDict([
    ("Прохождение", "Playthrough"),
    ("Справка", "Help"),
    ("Сохранить / Загрузить / Настройки / История / Меню — одним нажатием.",
     "Save / Load / Preferences / History / Menu — one click away."),
    ("Пропускать нечитанный текст", "Skip unread text"),
    ("Пропуск…", "Skipping…"),
    # --- options.rpy: название игры (заголовок окна, метаданные сейвов) ---
    ("Лето, которого не было / The Summer That Never Was", "The Summer That Never Was"),

    # --- screens.rpy: быстрое меню ---
    ("История", "History"),
    ("Сохранить", "Save"),
    ("Загрузить", "Load"),
    ("Настройки", "Settings"),
    ("Пропуск", "Skip"),
    ("Меню", "Menu"),

    # --- screens.rpy: confirm ---
    ("Да", "Yes"),
    ("Нет", "No"),

    # --- screens.rpy: главное меню ---
    ("Начать игру", "New game"),
    ("Продолжить", "Continue"),
    ("Об игре", "About"),
    ("Выход", "Quit"),

    # --- screens.rpy: шапка игрового меню ---
    ("Назад", "Back"),
    ("В главное меню", "Main menu"),

    # --- screens.rpy: слоты сохранений ---
    ("Слот [i]", "Slot [i]"),
    ("— пусто —", "— empty —"),
    ("Сохранение", "Save game"),
    ("Загрузка", "Load game"),

    # --- screens.rpy: настройки ---
    ("Текст", "Text"),
    ("Скорость вывода", "Text speed"),
    ("Авто-режим: пауза", "Auto-forward pause"),
    ("Пропуск после выборов", "Skip after choices"),
    ("останавливаться", "stop"),
    ("продолжать", "keep going"),
    ("Звук", "Sound"),
    ("Музыка", "Music"),
    ("Звуки", "Sounds"),
    ("Голос", "Voice"),
    ("Экран и язык", "Display and language"),
    ("Экран", "Display"),
    ("окно", "window"),
    ("полный", "fullscreen"),

    # Названия языков намеренно НЕ переводятся: кнопку языка принято
    # показывать на самом этом языке.

    # --- screens.rpy: история ---
    ("История диалогов", "Dialogue history"),
    ("История пуста.", "History is empty."),

    # --- screens.rpy: «Об игре» ---
    ("«Лето, которого не было» — визуальная новелла по дизайн-документу 3.0.",
     "“The Summer That Never Was” — a visual novel based on design document 3.0."),
    ("Движок: Ren'Py [renpy.version_only].",
     "Engine: Ren'Py [renpy.version_only]."),
    ("Текст и звуковой дизайн — оригинальные. Арт: полуреалистичная живописная стилистика, 1990-е, постсоветский лагерь.",
     "Text and sound design are original. Art: semi-realistic painterly style, 1990s, a post-Soviet summer camp."),
    ("Музыка: Kevin MacLeod (incompetech.com) — Morning, Carefree, Gymnopédie No. 1, Cheery Monday, Laid Back Guitars, Darkling, Inspired, Heartbreaking, Village Consort. Лицензия CC-BY 3.0.",
     "Music: Kevin MacLeod (incompetech.com) — Morning, Carefree, Gymnopédie No. 1, Cheery Monday, Laid Back Guitars, Darkling, Inspired, Heartbreaking, Village Consort. Licensed CC-BY 3.0."),
    ("Прошлое нужно не удерживать, а отпускать.",
     "The past should be let go, not held on to."),
]))


# =============================================================================
# 4. Подсказки общего движкового кода (renpy/common/00layout.rpy).
#    Они заданы в SDK на английском и НЕ обёрнуты в `_()`, поэтому блоком
#    `strings` их не перевести — приходится переопределять `layout.*`.
#    В renpy_project/game/i18n.rpy это сделано через `translate <lang> python:`.
#    Словарь здесь — источник правды; gen_tl.py сверяет i18n.rpy с ним.
# =============================================================================

LAYOUT_PROMPTS = collections.OrderedDict([
    ("ARE_YOU_SURE", ("Вы уверены?", "Are you sure?")),
    ("DELETE_SAVE", ("Удалить это сохранение?", "Are you sure you want to delete this save?")),
    ("OVERWRITE_SAVE", ("Перезаписать это сохранение?", "Are you sure you want to overwrite your save?")),
    ("LOADING", ("Загрузка прервёт несохранённый прогресс.\nВы уверены, что хотите это сделать?",
                 "Loading will lose unsaved progress.\nAre you sure you want to do this?")),
    ("QUIT", ("Вы уверены, что хотите выйти из игры?", "Are you sure you want to quit?")),
    ("MAIN_MENU", ("Вернуться в главное меню?\nНесохранённый прогресс будет потерян.",
                   "Are you sure you want to return to the main menu?\nThis will lose unsaved progress.")),
    ("CONTINUE", ("Продолжить с того места, где вы остановились?",
                  "Are you sure you want to continue where you left off?")),
    ("END_REPLAY", ("Завершить повтор?", "Are you sure you want to end the replay?")),
    ("SLOW_SKIP", ("Начать пропуск текста?", "Are you sure you want to begin skipping?")),
    ("FAST_SKIP_SEEN", ("Пропустить текст до следующего выбора?",
                        "Are you sure you want to skip to the next choice?")),
    ("FAST_SKIP_UNSEEN", ("Пропустить непрочитанный текст до следующего выбора?",
                          "Are you sure you want to skip unseen dialogue to the next choice?")),
])
