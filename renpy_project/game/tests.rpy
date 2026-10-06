## ============================================================
## tests.rpy — рукописные smoke-тесты Ren'Py (UI и обвязка)
## Запуск: SDL_VIDEODRIVER=dummy renpy.sh <проект> test
## Маршрутные тесты лежат в tests_autogen.rpy (генерирует tools/gen_rpt.py)
##
## СТРУКТУРА (по образцу tutorial/the_question из SDK Ren'Py 8.5):
##   * testsuite global — корневой сюит движка: здесь живёт teardown exit,
##     который завершает процесс ПОСЛЕ ВСЕХ тестов (и manual, и autogen).
##   * testsuite manual / testsuite autogen — вложенные сюиты со своими
##     хуками before testcase.
##   * testcase ОБЯЗАТЕЛЬНО вложены в свои сюиты (отступ 4 пробела):
##     на верхнем уровне хуки не применяются, и тесты падают по
##     дефолтному таймауту 5 секунд.
## ============================================================

init python:

    ## HEADLESS-СТРАХОВКА SELF-ТЕСТОВ.
    ## Программный рендерер Ren'Py (sw) не рисует новый кадр, пока что-то
    ## явно не запросит перерисовку (swdraw.should_redraw требует
    ## needs_redraw). Тестовый фреймворк renpy.test получает управление
    ## ТОЛЬКО на нарисованном кадре (renpy/display/core.py вызывает
    ## testexecution.execute() после отрисовки). Итог: на статичном экране
    ## (главное меню, реплика без анимаций) тесты «замерзают» навсегда —
    ## в headless-среде без GPU это ловят даже тесты SDK-примеров.
    ## Колбэк ниже во время тестового прогона запрашивает перерисовку на
    ## каждой итерации цикла — это «сердцебиение» для фреймворка.
    ## В обычной игре is_in_test() == False и колбэк ничего не делает.
    def _leto_test_heartbeat():
        try:
            import renpy.test.testexecution as _leto_te
            return _leto_te.is_in_test()
        except Exception:
            return False

    config.needs_redraw_callbacks.append(_leto_test_heartbeat)

    ## ОБХОД БАГА REN'PY 8.5.3: условия `advance until label X` работают
    ## через множество renpy.test.testexecution.reached_labels, которое
    ## наполняет колбэк add_reached_label. Движок регистрирует его ТОЛЬКО
    ## в renpy.reload_modules() (девелоперская перезагрузка shift+R), а при
    ## обычном запуске `renpy.sh <проект> test` — никогда; в итоге reached_
    ## labels всегда пусто и `until label` висит до таймаута. Регистрируем
    ## колбэк сами (в обычной игре он лишь добавляет имена меток в множество).
    try:
        import renpy.test.testexecution as _leto_te2
        if _leto_te2.add_reached_label not in config.label_callbacks:
            config.label_callbacks.append(_leto_te2.add_reached_label)
    except Exception:
        pass


testsuite global:

    before testsuite:
        ## ЯЗЫКОВАЯ СТРАХОВКА: persistent общий между запусками игры, и
        ## упавший prefs-тест может оставить язык english — тогда все
        ## тесты, ждущие русских подписей, тоже упадут. Возвращаем
        ## язык по умолчанию перед прогоном.
        python:
            if _preferences.language is not None:
                renpy.change_language(None)

    teardown:
        exit


testsuite manual:

    before testcase:
        $ _test.transition_timeout = 0.05
        $ _test.timeout = 60

        python:
            if _preferences.language is not None:
                renpy.change_language(None)

        ## Возврат в главное меню, если предыдущий тест упал посреди игры.
        ## ВАЖНО: проверка «мы именно в игре» (текущий узел из game/ или
        ## открыто внутриигровое меню). Наивная проверка `not screen "main_menu"`
        ## срабатывает во время загрузки движка, когда меню ещё не показано,
        ## и MainMenu() вызывает full_restart прямо во время boot — тестовый
        ## фреймворк после этого не запускает testcase (проверено на SDK-примере
        ## the_question: он так же виснет в headless-среде).
        if eval (renpy.exports.get_filename_line() or ('', 0))[0].startswith('game/') or (getattr(renpy.context(), '_menu', False) and not getattr(renpy.context(), '_main_menu', False)):
            run MainMenu(confirm=False)
            advance until screen "main_menu"

    ## Пролог: флаги считаются верно, быстрые меню работают
    testcase ui_smoke:

        click "Начать игру"
        advance until "Осмотреть билет внимательно"
        click "Осмотреть билет внимательно"
        advance until "Смотреть в окно"
        click "Смотреть в окно"
        advance until label d00_gate
        assert eval has_ticket
        assert eval truth_points == 1
        assert eval memory_fragments == 1
        advance until "Отшутиться"
        click "Отшутиться"
        advance until "Спросить про лагерь"
        click "Спросить про лагерь"
        advance until label d1_morning
        assert eval truth_points == 2
        assert eval lena_love == 2
        run MainMenu(confirm=False)
        advance until screen "main_menu"


    ## История и возврат из quick_menu
    testcase quick_menu_history:

        click "Начать игру"
        advance until "Осмотреть билет внимательно"
        click "История"
        advance until screen "history"
        click "Назад"
        advance until "Осмотреть билет внимательно"
        run MainMenu(confirm=False)
        advance until screen "main_menu"


    ## Сохранение и загрузка слота 1
    testcase save_load:

        click "Начать игру"
        advance until "Осмотреть билет внимательно"
        click "Сохранить"
        advance until screen "save"
        click "Слот 1"
        pause 0.5
        run MainMenu(confirm=False)
        advance until screen "main_menu"
        click "Загрузить"
        advance until screen "load"
        click "Слот 1"
        advance until "Осмотреть билет внимательно"
        run MainMenu(confirm=False)
        advance until screen "main_menu"


    ## Настройки открываются; English включает перевод; возврат на RU
    ## (тест идёт последним в сюите: переключение языка перезапускает игру)
    testcase prefs_and_english:

        click "Настройки"
        advance until screen "preferences"
        click "English"
        advance until screen "main_menu"
        click "Начать игру"
        advance until "Examine the ticket closely"
        click "Examine the ticket closely"
        advance until "Look out the window"
        run MainMenu(confirm=False)
        advance until screen "main_menu"
        click "Настройки"
        advance until screen "preferences"
        click "Русский"
        advance until screen "main_menu"
