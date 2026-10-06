## ============================================================
## tests_autogen.rpy — автотесты Ren'Py (self-test framework)
## Сгенерировано tools/gen_rpt.py: каждый testcase проигрывает маршрут
## на реальном движке: skip по диалогам + click по подписям меню.
## Запуск: renpy.sh <проект> test   (SDL_VIDEODRIVER=dummy)
## ============================================================

## teardown: exit живёт в testsuite global (tests.rpy) — он завершает
## процесс после ВСЕХ сюит. Здесь свой teardown не нужен: он обрезал бы
## соседние сюиты при полном прогоне.
testsuite autogen:

    before testcase:
        $ _test.transition_timeout = 0.05
        $ _test.timeout = 90

        python:
            if _preferences.language is not None:
                renpy.change_language(None)

        ## Возврат в главное меню только если предыдущий тест упал посреди
        ## игры (см. комментарий в tests.rpy: наивная проверка screen
        ## "main_menu" ломает загрузку движка в headless-среде).
        if eval (renpy.exports.get_filename_line() or ('', 0))[0].startswith('game/') or (getattr(renpy.context(), '_menu', False) and not getattr(renpy.context(), '_main_menu', False)):
            run MainMenu(confirm=False)
            advance until screen "main_menu"
        python:
            preferences.skip_unseen = True
            preferences.skip_after_choices = True

    testcase route_first:

        click "Начать игру"
        skip
        click "Осмотреть билет внимательно"
        click "Смотреть в окно"
        click "Спросить, кто она"
        click "Спросить про лагерь"
        click "Помочь Вере"
        click "Посмотреть рисунки"
        click "Пойти в радиоузел к Вере"
        click "Обыскать комнату"
        click "Помочь починить радио"
        click "Поверить Лене"
        click "Идти на звук"
        click "Пойти с Леной"
        click "Сказать правду вслух"
        click "Постоять рядом"
        click "Отпустить прошлое"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Истинная концовка: «Последняя линейка»'

    testcase route_last:

        click "Начать игру"
        skip
        click "Просто убрать в карман"
        click "Думать об отце"
        click "Отшутиться"
        click "Промолчать"
        click "Отказаться"
        click "Пройти мимо"
        click "Пойти к реке с Леной"
        click "Выйти и пойти к радиоузлу"
        click "Отказаться или отложить ремонт"
        click "Усомниться"
        click "Остаться одному"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Плохая концовка: «Забытый»'

    testcase route_lena_true:

        click "Начать игру"
        skip
        click "Осмотреть билет внимательно"
        click "Смотреть в окно"
        click "Отшутиться"
        click "Спросить про лагерь"
        click "Помочь Вере"
        click "Посмотреть рисунки"
        click "Пойти к реке с Леной"
        click "Обыскать комнату"
        click "Помочь починить радио"
        click "Поверить Лене"
        click "Идти на звук"
        click "Пойти с Леной"
        click "Сказать правду вслух"
        click "Постоять рядом"
        click "Отпустить прошлое"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Истинная концовка: «Последняя линейка»'

    testcase route_lena_stay:

        click "Начать игру"
        skip
        click "Осмотреть билет внимательно"
        click "Смотреть в окно"
        click "Отшутиться"
        click "Спросить про лагерь"
        click "Помочь Вере"
        click "Посмотреть рисунки"
        click "Пойти к реке с Леной"
        click "Обыскать комнату"
        click "Помочь починить радио"
        click "Поверить Лене"
        click "Идти на звук"
        click "Пойти с Леной"
        click "Сказать правду вслух"
        click "Постоять рядом"
        click "Остаться с Леной"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Концовка Лены: «Останься до утра»'

    testcase route_vera:

        click "Начать игру"
        skip
        click "Осмотреть билет внимательно"
        click "Смотреть в окно"
        click "Отшутиться"
        click "Спросить про лагерь"
        click "Помочь Вере"
        click "Посмотреть рисунки"
        click "Пойти в радиоузел к Вере"
        click "Обыскать комнату"
        click "Помочь починить радио"
        click "Поверить Лене"
        click "Идти на звук"
        click "Помочь Вере"
        click "Поддержать Веру"
        click "Предложить помочь с текстом"
        click "Отпустить прошлое"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Концовка Веры: «Голос в эфире»'

    testcase route_zoya:

        click "Начать игру"
        skip
        click "Осмотреть билет внимательно"
        click "Смотреть в окно"
        click "Отшутиться"
        click "Спросить про лагерь"
        click "Помочь Вере"
        click "Посмотреть рисунки"
        click "Пойти в библиотеку к Зое"
        click "Обыскать комнату"
        click "Помочь починить радио"
        click "Поверить Лене"
        click "Идти на звук"
        click "Пойти с Зоей"
        click "Назвать вещи своими именами"
        click "Держать лист, пока она рисует"
        click "Отпустить прошлое"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Концовка Зои: «Рисунок на память»'

    testcase route_alone:

        click "Начать игру"
        skip
        click "Осмотреть билет внимательно"
        click "Смотреть в окно"
        click "Отшутиться"
        click "Спросить про лагерь"
        click "Помочь Вере"
        click "Посмотреть рисунки"
        click "Пойти к реке с Леной"
        click "Обыскать комнату"
        click "Помочь починить радио"
        click "Поверить Лене"
        click "Идти на звук"
        click "Остаться одному"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Плохая концовка: «Забытый»'

    testcase route_farewell:

        click "Начать игру"
        skip
        click "Осмотреть билет внимательно"
        click "Смотреть в окно"
        click "Спросить, кто она"
        click "Спросить про лагерь"
        click "Помочь Вере"
        click "Пройти мимо"
        click "Пойти к реке с Леной"
        click "Обыскать комнату"
        click "Помочь починить радио"
        click "Усомниться"
        click "Уйти"
        click "Помочь Вере"
        click "Промолчать"
        click "Предложить помочь с текстом"
        click "Отпустить прошлое"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Нейтральная концовка: «Прощание без прощания»'

    testcase route_secret:

        python:
            persistent.true_seen = True

        click "Начать игру"
        skip
        click "Осмотреть билет внимательно"
        click "Смотреть в окно"
        click "Отшутиться"
        click "Спросить про лагерь"
        click "Помочь Вере"
        click "Посмотреть рисунки"
        click "Пойти к реке с Леной"
        click "Обыскать комнату"
        click "Помочь починить радио"
        click "Поверить Лене"
        click "Идти на звук"
        click "Пойти с Леной"
        click "Сказать правду вслух"
        click "Постоять рядом"
        click "Унести память с собой"
        skip
        advance until eval ending_shown != ""
        assert eval ending_shown == 'Секретная концовка: «Билет на двоих»'
