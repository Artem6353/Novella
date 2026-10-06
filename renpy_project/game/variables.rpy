## ============================================================
## variables.rpy
## «Лето, которого не было» — все игровые переменные (раздел 13)
## Правило: КАЖДАЯ переменная объявляется через default.
## persistent.* здесь не объявляется (это мета-прогресс).
## ============================================================

## --- Отношения ---
default lena_love = 0
default vera_love = 0
default zoya_love = 0

## --- Маршрут: "none" | "lena" | "vera" | "zoya" ---
default route = "none"

## --- Ключевые флаги ---
default trusted_lena      = False
default journal_found     = False
default radio_fixed       = False
default drawing_found     = False
default drawing_completed = False
default father_clue       = False
default escape_flag       = False
default zoya_sketch_found = False
default has_ticket        = False

## --- Фрагменты памяти (всего 6, раздел 22) ---
default memory_fragments = 0
default frag_ticket     = False
default frag_drawing    = False
default frag_journal    = False
default frag_cassette   = False
default frag_photo      = False
default frag_final_note = False

## --- Прогресс правды (максимум 10, раздел 23) ---
default truth_points = 0

## --- Финал: "" | "let_go" | "stay" | "carry_memory" | "forget" ---
default final_choice = ""

## --- Служебные ---
## highest_love вычисляется в determine_ending, но объявлен здесь,
## чтобы rollback и save/load никогда не ловили NameError.
default highest_love = 0

## Счётчик повторов канонной фразы «Линейка в семь» — используется
## в D3_GLITCH, чтобы мир «проваливался» в повтор с нарастанием.
default lineup_repeats = 0

## Смотрел ли игрок концовки в текущем прохождении (для титров/подсказок)
default ending_shown = ""
default stats_line = ""
