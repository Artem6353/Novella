## ============================================================
## audio.rpy
## «Лето, которого не было» — музыка и звуки
##
## ПО ПРАВИЛАМ ТЗ (этап 3) музыка в сценах стоит КОММЕНТАРИЯМИ:
##     # play music main_theme fadein 1.0
## Когда треки будут готовы (этап 5/6), выполните три шага:
##   1. положите файлы в game/audio/;
##   2. раскомментируйте define-блоки ниже;
##   3. раскомментируйте строки "play music ..." / "play sound ..." в сценах.
## ============================================================

## ------------------------------------------------------------
## 9 МУЗЫКАЛЬНЫХ ТРЕКОВ (раздел 27 дизайн-документа)
## ------------------------------------------------------------
define audio.main_theme     = "audio/main_theme.ogg"      # ностальгия, лето
define audio.camp_day       = "audio/camp_day.ogg"        # светлая, тёплая
define audio.lena_theme     = "audio/lena_theme.ogg"      # нежная, загадочная
define audio.vera_theme     = "audio/vera_theme.ogg"      # живая, радиоформатная
define audio.zoya_theme     = "audio/zoya_theme.ogg"      # тихая, сонная
define audio.mystery        = "audio/mystery.ogg"         # тревога, сбой памяти
define audio.finale         = "audio/finale.ogg"          # эмоциональная, светлая
define audio.forgotten_theme = "audio/forgotten_theme.ogg" # пустота, потеря
define audio.farewell_theme = "audio/farewell_theme.ogg"  # спокойное завершение

## ------------------------------------------------------------
## SFX (этап 6, файл docs/06_ТЗ_звуки.md)
## ------------------------------------------------------------
define audio.bus_engine   = "audio/sfx/bus_engine.ogg"
define audio.wind         = "audio/sfx/wind.ogg"
define audio.gate_creak   = "audio/sfx/gate_creak.ogg"
define audio.crickets     = "audio/sfx/crickets.ogg"
define audio.radio_noise  = "audio/sfx/radio_noise.ogg"
define audio.gravel       = "audio/sfx/gravel.ogg"
define audio.river        = "audio/sfx/river.ogg"
define audio.glitch       = "audio/sfx/glitch.ogg"
define audio.bell         = "audio/sfx/bell.ogg"
define audio.cassette     = "audio/sfx/cassette.ogg"
define audio.door         = "audio/sfx/door.ogg"
define audio.rain         = "audio/sfx/rain.ogg"
define audio.swing        = "audio/sfx/swing.ogg"
define audio.glass        = "audio/sfx/glass.ogg"
define audio.heartbeat    = "audio/sfx/heartbeat.ogg"
define audio.broadcast    = "audio/sfx/broadcast.ogg"
define audio.owl          = "audio/sfx/owl.ogg"
define audio.lineup_horn  = "audio/sfx/lineup_horn.ogg"

## ------------------------------------------------------------
## Настройки звуковых каналов
## ------------------------------------------------------------
init python:
    ## Каналы звука. ВАЖНО: в Ren'Py 8.5 музыкальный канал зациклен по умолчанию,
    ## отдельной переменной config.loop_music НЕ существует (и не нужна).
    ## Громкости по умолчанию задаются в настройках игрока (Preferences),
    ## а не через config.* — поэтому здесь только официальные флаги каналов.
    config.has_music = True
    config.has_sound = True

    ## Озвучка не планируется (раздел 29 ГДД): канал голоса оставлен включённым,
    ## но пустым — его можно будет заполнить позже без правок кода.
    config.has_voice = True
