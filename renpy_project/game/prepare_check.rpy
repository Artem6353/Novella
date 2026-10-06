## ============================================================
## prepare_check.rpy — оптиональная headless-самопроверка экранов
## Включается внешней переменной окружения:
##     LETO_PREPARE_CHECK=1 renpy.sh <проект> lint     (или обычный запуск)
## Пишет результат в game/prepare_result.txt.
## Ловит класс рантайм-ошибок «screen prepare»: шрифты, Preference(...),
## оконные свойства, порядок init gui/screens — без дисплея и без кликов.
## ============================================================

init 950 python:
    import os
    if os.environ.get("LETO_PREPARE_CHECK") == "1":
        _leto_res = []
        try:
            renpy.display.screen.prepare_screens()
            _leto_res.append("PREPARE_OK: все экраны подготовлены без ошибок")
        except Exception as _leto_e:
            import traceback
            _leto_res.append("PREPARE_FAIL: %r\n%s" % (_leto_e, traceback.format_exc()))
        try:
            with open(os.path.join(renpy.config.gamedir, "prepare_result.txt"), "w") as _leto_f:
                _leto_f.write("\n".join(_leto_res) + "\n")
        except Exception:
            pass
