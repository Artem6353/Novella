## ============================================================
## tests.rpy — рукописные smoke-тесты Ren'Py (UI и обвязка)
## Запуск: SDL_VIDEODRIVER=dummy renpy.sh <проект> test
## Маршрутные тесты лежат в tests_autogen.rpy (генерирует tools/gen_rpt.py)
## ============================================================

testsuite manual:

    before testcase:
        $ _test.transition_timeout = 0.05
        $ _test.timeout = 60

        if not screen "main_menu":
            run MainMenu(confirm=False)

    teardown:
        exit


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
## (тест идёт последним: переключение языка перезапускает игру)
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
