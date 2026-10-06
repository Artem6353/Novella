## ============================================================
## options.rpy — базовые настройки проекта (самодостаточная сборка)
## ============================================================

define config.name = _("Лето, которого не было / The Summer That Never Was")
define config.version = "1.2.2"

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
