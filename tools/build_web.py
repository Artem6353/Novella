#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_web.py — собирает web_demo/index.html из шаблона движка и game_data.json.
Запуск: python3 tools/build_web.py   (после tools/export_web.py)
"""

import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TPL = os.path.join(ROOT, "web_src", "engine_template.html")
DATA = os.path.join(ROOT, "web_demo", "game_data.json")
OUT = os.path.join(ROOT, "web_demo", "index.html")

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

tpl = open(TPL, encoding="utf-8").read()
data = open(DATA, encoding="utf-8").read()

html = tpl.replace("__GAME_DATA__", data).replace("__EXTRA__", json.dumps(EX, ensure_ascii=False))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Готово: {os.path.relpath(OUT, ROOT)} — {os.path.getsize(OUT)//1024} KB")
