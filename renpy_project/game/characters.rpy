## ============================================================
## characters.rpy
## «Лето, которого не было» — определение персонажей
## ВНИМАНИЕ: все персонажи объявляются ТОЛЬКО здесь.
## В сценах повторно писать define mc / lena / vera / zoya нельзя.
## ============================================================

## Основной состав (палитра — из раздела 28 дизайн-документа)
define mc   = Character("Артём", color="#2d6a4f")
define lena = Character("Лена",  color="#c8a2ff")
define vera = Character("Вера",  color="#ffd166")
define zoya = Character("Зоя",   color="#8ecae6")

## Служебные голоса
## narrator — безымянный рассказчик (мысли Артёма и описания мира).
## Намеренно не переопределяем: используется narrator движка со стилями gui.rpy,
## чтобы цвет текста гарантированно совпадал с настройками интерфейса.

## Голоса «из прошлого»: радиоэфир, ребёнок на площади, вожатский голос.
## Отдельные Character нужны, чтобы игрок слышал разницу тембров текста.
define radio  = Character("Радио",     color="#9d4c4c")
define child  = Character("Ребёнок",   color="#2d6a4f")
define young_voice = Character("Голос",  color="#5e548e")   # НЕ `voice`: это оператор RenPy
define lena_e = Character("Лена (?)",  color="#c8a2ff")

## Системные подписи (дни, концовки)
define card = Character(None, what_color="#ffb703", what_italic=False, what_size=34,
                       what_xalign=0.5)
