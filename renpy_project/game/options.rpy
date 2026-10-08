## ============================================================
## options.rpy — базовые настройки проекта (самодостаточная сборка)
## ============================================================

define config.name = _("Лето, которого не было / The Summer That Never Was")
define config.version = "1.3.0"

## Уникальная папка сохранений (не пересекаться с другими проектами)
define config.save_directory = "leto-kotorogo-ne-bylo-8"

## Виртуальное разрешение (все арты и размеры gui посчитаны под него)
define config.screen_width = 1920
define config.screen_height = 1080

## Точка входа
define config.main_menu_music = ""

## История диалогов (экран history)
define config.history_length = 250

## Откат (rollback) разрешён на всю глубину
define config.rollback_enabled = True

## Разрешаем сохранение в любой момент
define config.allow_skipping = True

## ------------------------------------------------------------
## Штатные флаги из практики tutorial (options.rpy):
## медиа-каналы и переходы между контекстами меню/игры.
## ------------------------------------------------------------
define config.has_sound = True
define config.has_music = True
define config.has_voice = False

## Переходы при входе/выходе из меню и между сценами игры (tutorial-практика:
## единый мягкий dissolve по умолчанию).
define config.enter_transition = dissolve
define config.exit_transition = dissolve
define config.intra_transition = dissolve
