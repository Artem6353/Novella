## ============================================================
## scenes/endings.rpy
## determine_ending  — логика выбора концовки (раздел 17 ГДД)
## ending_true       — «Последняя линейка»   (истинная)
## ending_lena_stay  — «Останься до утра»     (Лена)
## ending_vera_voice — «Голос в эфире»        (Вера)
## ending_zoya_painting — «Рисунок на память» (Зоя)
## ending_farewell   — «Прощание без прощания» (нейтральная)
## ending_forgotten  — «Забытый»              (плохая)
## ending_secret     — «Билет на двоих»       (секретная)
##
## Все концовки завершаются через return (возврат в главное меню).
## persistent.true_seen устанавливается ТОЛЬКО в ending_true.
## ============================================================

## ------------------------------------------------------------
## ЛОГИКА ВЫБОРА КОНЦОВКИ
## ------------------------------------------------------------

label determine_ending:

    $ highest_love = max(lena_love, vera_love, zoya_love)

    ## --- Секретная концовка ---
    if persistent.true_seen:
        if route == "lena" and lena_love >= 8 and trusted_lena and truth_points >= 10 and memory_fragments == 6 and father_clue and final_choice == "carry_memory":
            jump ending_secret

    ## --- Плохая концовка ---
    if escape_flag or final_choice == "forget" or highest_love < 3 or truth_points <= 2:
        jump ending_forgotten

    ## --- Истинная концовка Лены ---
    if route == "lena":
        if truth_points >= 8 and memory_fragments >= 5 and trusted_lena and final_choice == "let_go":
            $ persistent.true_seen = True
            jump ending_true

        if lena_love >= 6 and final_choice == "stay":
            jump ending_lena_stay

    ## --- Концовка Веры ---
    if route == "vera":
        if vera_love >= 8 and radio_fixed and truth_points >= 6 and memory_fragments >= 4 and final_choice == "let_go":
            jump ending_vera_voice

    ## --- Концовка Зои ---
    if route == "zoya":
        if zoya_love >= 8 and drawing_found and drawing_completed and truth_points >= 6 and memory_fragments >= 4 and final_choice in ["let_go", "carry_memory"]:
            jump ending_zoya_painting

    ## --- Нейтральная концовка ---
    if highest_love >= 3 and truth_points >= 3:
        jump ending_farewell

    ## --- Если ни одно условие не выполнено ---
    jump ending_forgotten


## ============================================================
## 1. ИСТИННАЯ КОНЦОВКА — «ПОСЛЕДНЯЯ ЛИНЕЙКА»
## ============================================================

label ending_true:

    play music finale fadein 2.0 if_changed
    scene cg_true_last_lineup
    with fade

    play sound bell
    "Я ударил в колокол." id ending_true_0001

    "Раз." id ending_true_0002

    "Звук пошёл над площадью — низкий, неровный, живой." id ending_true_0003

    "Два." id ending_true_0004

    "Дети подняли головы. Все сразу, как тогда, у костра." id ending_true_0005

    "Три." id ending_true_0006

    "И на третьем ударе Лена вышла на середину сцены." id ending_true_0007

    show lena normal at tr_center
    with dissolve

    lena "Двадцатая смена. Лагерь «Сосновый берег»." id ending_true_0008

    lena "Построение окончено." id ending_true_0009

    "Её голос не дрожал. Он просто стал тише — так говорят с теми, кто уже всё знает." id ending_true_0010

    lena "Мы не уехали девятнадцатого августа." id ending_true_0011

    lena "Не потому, что не хотели. А потому, что нас не отпустили — ни вы, ни мы сами." id ending_true_0012

    "Вера щёлкнула тумблером. Красная лампочка на пульте загорелась." id ending_true_0013

    show vera determined at tr_right
    with dissolve

    play sound broadcast loop
    vera "Говорит радиоузел лагеря «Сосновый берег». Смена двадцатая. Эфир — последний." id ending_true_0014

    vera "Передаём привет первому отряду. Второму. Третьему. Четвёртому — я знаю, кто украл микрофон, и я не держу зла." id ending_true_0015

    vera "Передаём привет Гарину, который держал фонарь до последнего. Передаём привет Воронову, который молчал двадцать лет и всё-таки сказал." id ending_true_0016

    vera "И передаём привет всем, кто нас не дослушал. Вы не виноваты." id ending_true_0017

    vera "Смена закрыта. Всем пока." id ending_true_0018

    mc "Сигнал принят. Эфир доставлен. Прощание завершено." id ending_true_0102

    "Три правила петли закрылись одно за другим, как три удара колокола. Я сказал это вслух — чтобы услышал тот, кто двадцать лет не дослушивал." id ending_true_0103

    "Она выключила микрофон на целой фразе — впервые в жизни не оборвав её." id ending_true_0019

    ## Эфир закончился буквально в предыдущей реплике, а петля
    ## `play sound broadcast loop` (начало концовки) продолжала звучать
    ## до самого возвращения в главное меню — то есть ещё ~40 реплик
    ## сцены с Зоей, Леной и рассветом шли под не выключенный радиоузел.
    ## В prologue.rpy для двигателя автобуса `stop sound` стоит; здесь его
    ## просто забыли. Канал sound в Ren'Py один, поэтому петля не «наслаивалась»,
    ## но текст и звук противоречили друг другу.
    stop sound fadeout 1.5

    hide vera
    with dissolve

    show zoya calm at tr_left
    with dissolve

    "Зоя поставила картину на ступени сцены — лицом к лагерю." id ending_true_0020

    "Последний мазок был светлым. Полоса по краю листа, которая оказалась не линией, а рассветом." id ending_true_0021

    zoya "Готово." id ending_true_0022

    mc "Что теперь?" id ending_true_0023

    zoya "Теперь её можно смотреть." id ending_true_0024

    hide zoya
    with dissolve

    show lena smile at tr_center
    with dissolve

    "Лена подошла ко мне." id ending_true_0025

    lena "Артём." id ending_true_0026

    mc "Да?" id ending_true_0027

    lena "Скажи ему." id ending_true_0028

    mc "Кому?" id ending_true_0029

    lena "Тому, кто приедет сюда через двадцать лет. Или не приедет." id ending_true_0030

    mc "Я скажу." id ending_true_0031

    lena "И себе скажи. Тебе нужнее." id ending_true_0032

    "Она кивнула — коротко, по-вожатски, как кивают перед тем, как отпустить отряд." id ending_true_0033

    lena "Спасибо, что пришёл." id ending_true_0034

    mc "Спасибо, что дождалась." id ending_true_0035

    "А за её спиной, там, где площадь уже становилась светом, стоял человек в старой куртке. Он не подошёл. Он кивнул — ей, не мне. И этого хватило обоим." id ending_true_0100

    mc "Пап. Я не буду молчать двадцать лет. Слышишь? Я вообще молчать не буду." id ending_true_0101

    hide lena
    with dissolve

    "Она пошла к причалу. Не оборачиваясь." id ending_true_0036

    "У кромки воды её встретили — не дети. Дети стояли здесь, на площади, и махали руками." id ending_true_0037

    "Её встретил рассвет." id ending_true_0038

    "Лагерь растворился на рассвете." id ending_true_0039

    "Не как смерть. Как освобождение." id ending_true_0040

    "Сначала погас свет в корпусах. Потом исчез флагшток. Потом — сцена, костёр, качели." id ending_true_0041

    scene bg dawn
    with fade

    "Я стоял посреди заросшего поля, по колено в траве." id ending_true_0042

    "Никаких корпусов. Только фундаменты, два бетонных столба от ворот и старая липа." id ending_true_0043

    "В руке — билет. Выцветший, двадцатилетней давности, холодный." id ending_true_0044

    "Наконец-то холодный." id ending_true_0045

    mc "Ну вот и всё, пап. Я сказал." id ending_true_0046

    mc "Тебя никто не осудил. И я — тоже." id ending_true_0047

    mc "Но и оправдывать не буду. Хватит." id ending_true_0048

    "На ступенях, которых больше не существовало, ветер не тронул только одно." id ending_true_0049

    "Детский рисунок: причал, вода и фонарь, опущенный вниз." id ending_true_0050

    "Я поднял его, сложил вчетверо и положил к билету." id ending_true_0051

    "Автобус до Заречья уходил в шесть сорок. Впервые за пять дней я точно знал, какое сегодня число." id ending_true_0052

    $ ending_shown = "Истинная концовка: «Последняя линейка»"

    call end_card

    return


## ============================================================
## 2. ХОРОШАЯ КОНЦОВКА ЛЕНЫ — «ОСТАНЬСЯ ДО УТРА»
## ============================================================

label ending_lena_stay:

    play music lena_theme fadein 2.0 if_changed
    scene cg_lena_stay
    with fade

    play sound river loop
    "Я не пошёл к воротам." id ending_lena_stay_0001

    "Я сел на траву у самой воды, там, где тропинка уходит к причалу, и лента на ней больше никого не пугала." id ending_lena_stay_0002

    show lena surprised at tr_right
    with dissolve

    lena "Артём. Рассвет через минуту." id ending_lena_stay_0003

    mc "Я знаю." id ending_lena_stay_0004

    lena "Если ты останешься — он не наступит." id ending_lena_stay_0005

    mc "Я знаю." id ending_lena_stay_0006

    lena "Ты знаешь, чем это кончается?" id ending_lena_stay_0007

    mc "Знаю. Ничем." id ending_lena_stay_0008

    show lena sad
    with dissolve

    lena "Тогда почему?" id ending_lena_stay_0009

    mc "Потому что там, за воротами, у меня нет ни одного человека, который бы меня ждал." id ending_lena_stay_0010

    mc "А здесь есть одна, которая ждала двадцать лет." id ending_lena_stay_0011

    "Она села рядом. Так близко, что я почувствовал холод — не от воды." id ending_lena_stay_0012

    lena "Ты не обязан." id ending_lena_stay_0013

    mc "Я не обязываюсь. Я выбираю." id ending_lena_stay_0014

    lena "Выборы кончаются." id ending_lena_stay_0015

    mc "Этот — нет." id ending_lena_stay_0016

    show lena smile
    with dissolve

    "Лагерь не растворился. Он просто замолчал — мягко, как замолкает комната, в которой выключили радио." id ending_lena_stay_0017

    "Площадь за спиной осталась на месте. Корпуса остались. Дети где-то смеялись, и смех был один и тот же, но мне было всё равно." id ending_lena_stay_0018

    lena "Значит, ты правда остался." id ending_lena_stay_0019

    mc "Остался." id ending_lena_stay_0020

    "Река текла. Закат не догорал." id ending_lena_stay_0021

    "Где-то далеко щёлкнул динамик и начал песню про костёр." id ending_lena_stay_0022

    "Я знал её наизусть. Я знал её всю жизнь." id ending_lena_stay_0023

    "И лето не закончилось." id ending_lena_stay_0024

    "По крайней мере, для нас." id ending_lena_stay_0025

    "Где-то за спиной, на площади, кто-то включил радио. Песня про костёр пошла с середины — с того самого места, где её всегда обрывали." id ending_lena_stay_0026

    "На этот раз она доиграла до конца." id ending_lena_stay_0027

    "Потом заиграла снова." id ending_lena_stay_0028

    mc "Вера, наверное, счастлива." id ending_lena_stay_0029

    lena "Вера счастлива всегда. Это её работа." id ending_lena_stay_0030

    "Я засмеялся. Смех получился странным — тихим и немного чужим, как будто смеялся не я, а кто-то, кто очень давно здесь живёт." id ending_lena_stay_0031

    "Лена положила голову мне на плечо, и я подумал, что это, наверное, счастье." id ending_lena_stay_0032

    "Мысль получилась тихой и какой-то не своей — так думают люди, которые уже очень долго никуда не едут." id ending_lena_stay_0033

    hide lena
    with dissolve

    $ ending_shown = "Концовка Лены: «Останься до утра»"

    call end_card

    return


## ============================================================
## 3. ХОРОШАЯ КОНЦОВКА ВЕРЫ — «ГОЛОС В ЭФИРЕ»
## ============================================================

label ending_vera_voice:

    play music vera_theme fadein 2.0 if_changed
    scene cg_vera_voice
    with fade

    play sound broadcast loop
    "Красная лампочка на пульте горела ровно." id ending_vera_voice_0001

    "Вера села на тот самый шатающийся стул, поставила перед собой лист, отложила лист и придвинула микрофон." id ending_vera_voice_0002

    show vera determined at tr_right
    with dissolve

    vera "Говорит радиоузел лагеря «Сосновый берег». Смена двадцатая." id ending_vera_voice_0003

    vera "Это последний эфир. Не потому, что нам надоело. Потому, что пора." id ending_vera_voice_0004

    vera "Мы задержались здесь на двадцать лет из-за одной незаконченной фразы." id ending_vera_voice_0005

    vera "Так вот: до свидания, лето. Ты было хорошее. Ты было лучшее." id ending_vera_voice_0006

    "Она засмеялась. Смех вышел нужной длины — секунда в секунду." id ending_vera_voice_0007

    vera "Отдельно передаём: Гарина Елена, старшая вожатая. Все вышли. Все целы. Ты слышишь? Все." id ending_vera_voice_0008

    vera "И Воронову передаём: сигнал принят. Прощаем. Повторяю — прощаем. Это официальный эфир, тут не шутят." id ending_vera_voice_0009

    "Голос Веры разнёсся над лагерем." id ending_vera_voice_0010

    "И где-то далеко ему ответил рассвет." id ending_vera_voice_0011

    hide vera
    with dissolve

    scene bg dawn
    with fade

    "Динамики погасли один за другим, как гаснет костёр, который никто не ворошит." id ending_vera_voice_0012

    ## Ровно то же, что в ending_true: реплика говорит «динамики погасли»,
    ## а `play sound broadcast loop` из начала концовки продолжал играть
    ## и на рассвете, и в комнате Артёма («Я проснулся в своей комнате»),
    ## и неделю спустя в маршрутке — вплоть до главного меню, где канал
    ## глушит config.main_menu_stop_channels.
    stop sound fadeout 2.5

    "Я стоял у ворот и смотрел, как площадь уходит в свет — не в темноту, а именно в свет." id ending_vera_voice_0013

    "Лена кивнула мне с причала. Зоя помахала листом. Вера показала большой палец и отвернулась к микрофону, потому что не умела уходить глядя." id ending_vera_voice_0014

    with fade

    scene bg room
    with fade

    "Я проснулся в своей комнате, на полу, с телефоном в руке." id ending_vera_voice_0015

    "На экране было четыре пропущенных от мамы и дата — сегодняшняя." id ending_vera_voice_0016

    "В нагрудном кармане куртки лежал билет. Настоящий, выцветший, холодный." id ending_vera_voice_0017

    "И сложенный вчетверо лист с расписанием: «Подъём — восемь. Завтрак — девять. Линейка — девятнадцать»." id ending_vera_voice_0018

    "Я показал маме билет. Она долго смотрела, потом спросила, откуда он." id ending_vera_voice_0019

    "Я сказал: из лагеря, где отец работал." id ending_vera_voice_0020

    "Она кивнула и убрала билет в ящик — к тем самым трём склеенным монетам и инструкции к радиостанции." id ending_vera_voice_0021

    "Я не стал говорить, что знаю, почему он её хранил." id ending_vera_voice_0022

    "Некоторые вещи лучше знать одному. По крайней мере, пока не научишься говорить о них спокойно." id ending_vera_voice_0023

    "Через неделю я ехал в маршрутке и машинально включил радио." id ending_vera_voice_0024

    "Шли помехи. Сквозь помехи кто-то громко, весело и совершенно незнакомым голосом сказал:" id ending_vera_voice_0025

    vera "…и никому не советую молчать больше двадцати лет!" id ending_vera_voice_0026

    "Я улыбнулся как идиот. Весь оставшийся путь." id ending_vera_voice_0027

    mc "Принято, Вера. Сигнал принят." id ending_vera_voice_0028

    $ ending_shown = "Концовка Веры: «Голос в эфире»"

    call end_card

    return


## ============================================================
## 4. ХОРОШАЯ КОНЦОВКА ЗОИ — «РИСУНОК НА ПАМЯТЬ»
## ============================================================

label ending_zoya_painting:

    play music zoya_theme fadein 2.0 if_changed
    scene cg_zoya_painting
    with fade

    "Зоя сделала последний мазок." id ending_zoya_painting_0001

    show zoya focused at tr_right
    with dissolve

    "Не тёмный. Светлый — полоса по нижнему краю, которую я принял бы за рамку, если бы не знал." id ending_zoya_painting_0002

    zoya "Всё." id ending_zoya_painting_0003

    mc "Покажи." id ending_zoya_painting_0004

    "Она развернула картину к площади." id ending_zoya_painting_0005

    "Лагерь ожил на картине — и тихо исчез." id ending_zoya_painting_0006

    hide zoya
    with dissolve

    "Сначала ушёл звук: перестал скрипеть флагшток, замолчали качели, оборвался динамик на полуслове." id ending_zoya_painting_0007

    "Потом ушёл цвет: корпуса выцвели, как старая фотография на подоконнике." id ending_zoya_painting_0008

    "Потом ушли они." id ending_zoya_painting_0009

    "Лена вошла в картину — не шагнула, а именно вошла, как входят в тёплую воду. Она осталась в ней светом у самой кромки." id ending_zoya_painting_0010

    "Вера подмигнула и сказала: «Для радио это тоже считается эфиром»." id ending_zoya_painting_0011

    "Зоя посмотрела на меня дольше, чем когда-либо." id ending_zoya_painting_0012

    show zoya smile at tr_right
    with dissolve

    zoya "Тебе не страшно?" id ending_zoya_painting_0013

    mc "Страшно." id ending_zoya_painting_0014

    zoya "Мне тоже." id ending_zoya_painting_0015

    mc "Что будет с рисунком?" id ending_zoya_painting_0016

    zoya "Он будет у тебя." id ending_zoya_painting_0017

    mc "У меня?" id ending_zoya_painting_0018

    zoya "Я не умею носить. Я умею рисовать." id ending_zoya_painting_0019

    "Она протянула мне лист — тяжёлый, как доска, тёплый, как чужая ладонь." id ending_zoya_painting_0020

    zoya "Смотри на него иногда. Не каждый день. Каждому дню хватает своих рисунков." id ending_zoya_painting_0021

    mc "Я буду." id ending_zoya_painting_0022

    zoya "И не прячь в коробку." id ending_zoya_painting_0023

    mc "Не спрячу." id ending_zoya_painting_0024

    hide zoya
    with dissolve

    scene bg dawn
    with fade

    "Я стоял один посреди заросшего поля." id ending_zoya_painting_0025

    "Под мышкой — картина, которой не должно было существовать: четыре фигуры, площадь, причал и полоса света по краю." id ending_zoya_painting_0026

    "Краска не высохла. Она не высохла и через год." id ending_zoya_painting_0027

    with fade

    scene bg room
    with fade

    "Картина висит над столом. Мама спросила, где я её взял." id ending_zoya_painting_0028

    "Я сказал: в лагере, у одной девочки." id ending_zoya_painting_0029

    "Она долго смотрела и сказала, что свет нарисован неправильно — так не бывает." id ending_zoya_painting_0030

    "Я не стал спорить. Бывает." id ending_zoya_painting_0031

    "Зоя не оставила ни адреса, ни письма. Только картину и одну фразу, которую я повторяю иногда вслух:" id ending_zoya_painting_0032

    zoya "Каждому дню хватает своих рисунков." id ending_zoya_painting_0033

    "Я повесил её так, чтобы было видно от двери. Мама сначала ворчала, что «эта мазня портит стену», а потом сама стала поправлять её, когда та висела криво." id ending_zoya_painting_0034

    "Однажды я рассказал ей про лагерь. Весь, до конца: про грозу, про причал, про отца, про Лену." id ending_zoya_painting_0035

    "Мама выслушала молча. Потом сказала: «Значит, он не бросил нас. Он просто не вынес»." id ending_zoya_painting_0036

    "Я не согласился. Но спорить не стал — она имела право понимать это по-своему." id ending_zoya_painting_0037

    "Иногда, когда я работаю допоздна и в комнате остаётся только лампа, фигуры на картине стоят чуть ближе к краю." id ending_zoya_painting_0038

    "Я не боюсь. Я просто говорю им «спокойной ночи»." id ending_zoya_painting_0039

    "И они, кажется, отвечают." id ending_zoya_painting_0040

    $ ending_shown = "Концовка Зои: «Рисунок на память»"

    call end_card

    return


## ============================================================
## 5. НЕЙТРАЛЬНАЯ КОНЦОВКА — «ПРОЩАНИЕ БЕЗ ПРОЩАНИЯ»
## ============================================================

label ending_farewell:

    play music farewell_theme fadein 2.0 if_changed
    scene cg_farewell_dawn
    with fade

    play sound wind loop
    "Рассвет застал меня у ворот." id ending_farewell_0001

    "Я простоял там всю ночь, перебирая то, что нашёл: билет, страница журнала, обрывок плёнки, фотография, чужая записка." id ending_farewell_0002

    "Правда была у меня в руках. Целиком." id ending_farewell_0003

    "А сделать с ней я ничего не успел." id ending_farewell_0004

    "Линейка не проведена. Эфир не закрыт. Последний мазок не поставлен. Имя не названо вслух при всех." id ending_farewell_0005

    mc "Я знал. Знал — и не закончил." id ending_farewell_0006

    "Лагерь за спиной был тихий." id ending_farewell_0007

    "Не пугающий. Не давящий. Просто тихий — так бывает тихо в доме, где все легли спать, не договорив." id ending_farewell_0008

    show lena normal at tr_right
    with dissolve

    "Лена стояла у ворот. Она не звала и не останавливала." id ending_farewell_0009

    lena "Ты уходишь." id ending_farewell_0010

    mc "Ухожу." id ending_farewell_0011

    lena "Хорошо." id ending_farewell_0012

    mc "Хорошо?" id ending_farewell_0013

    show lena smile
    with dissolve

    lena "Ты не остался. Это уже больше, чем сделал твой отец." id ending_farewell_0014

    mc "Я мог закончить." id ending_farewell_0015

    lena "Мог." id ending_farewell_0016

    mc "Почему не сказала?" id ending_farewell_0017

    lena "Потому что это должен решить ты. Иначе не считается." id ending_farewell_0018

    "Вера помахала мне от радиоузла — слишком весело, так машут, когда не хотят, чтобы их заметили." id ending_farewell_0019

    "Зоя стояла у окна библиотеки. Она перевернула рисунок лицом вниз." id ending_farewell_0020

    hide lena
    with dissolve

    "Я вышел за ворота." id ending_farewell_0021

    "Дорога была на месте. Остановка — на месте. Четыре километра я прошёл за час." id ending_farewell_0022

    "Автобус пришёл вовремя." id ending_farewell_0023

    "Водитель спросил, откуда я иду. Я сказал: из лагеря." id ending_farewell_0024

    "Он посмотрел в зеркало, потом на меня, потом снова в зеркало." id ending_farewell_0025

    "«Какого лагеря?» — спросил он." id ending_farewell_0026

    "«Сосновый берег», — сказал я." id ending_farewell_0027

    "Он помолчал и ответил, уже отворачиваясь: «Там ничего нет. Сгорело всё в девяносто восьмом»." id ending_farewell_0028

    "Я не стал спорить. Я знал, что там есть." id ending_farewell_0029

    "И знал, что вернусь не сегодня." id ending_farewell_0030

    scene bg bus
    with fade

    "В окне я искал детский рисунок солнца. Его не было." id ending_farewell_0031

    "В нагрудном кармане лежал билет. Он был тёплый — и оставался тёплым ещё очень долго." id ending_farewell_0032

    mc "Я вернусь." id ending_farewell_0033

    "Я сказал это вслух, в пустом автобусе, и сам себе не поверил." id ending_farewell_0034

    "Но лагерь за спиной, кажется, услышал." id ending_farewell_0035

    "Он тихий. Он не пугает." id ending_farewell_0036

    "Он всё ещё ждёт." id ending_farewell_0037

    $ ending_shown = "Нейтральная концовка: «Прощание без прощания»"

    call end_card

    return


## ============================================================
## 6. ПЛОХАЯ КОНЦОВКА — «ЗАБЫТЫЙ»
## ============================================================

label ending_forgotten:

    play music forgotten_theme fadein 2.0 if_changed
    scene cg_forgotten_gate
    with fade

    play sound wind loop
    "Я шёл к воротам и чувствовал, как становится легче." id ending_forgotten_0001

    "Не веселее. Легче." id ending_forgotten_0002

    "Сначала ушли имена: Вера, Зоя, Лена. Я помнил, что они были, но не помнил, кто из них кто." id ending_forgotten_0003

    "Потом ушло лицо матери." id ending_forgotten_0004

    "Потом — причина, по которой я вообще приехал." id ending_forgotten_0005

    mc "Я забыл, как меня зовут." id ending_forgotten_0006

    "Но лагерь запомнил." id ending_forgotten_0007

    "Он запомнил всё: подъём в восемь, завтрак в девять, линейку в девятнадцать ноль-ноль." id ending_forgotten_0008

    "Он дал мне расписание вместо имени. Это оказалось даже удобнее." id ending_forgotten_0009

    scene bg gate
    with fade

    "Утром к воротам подошёл кто-то новый." id ending_forgotten_0010

    "Подросток с рюкзаком, в старой куртке не по размеру. Он держался за нагрудный карман каждые десять шагов." id ending_forgotten_0011

    "Я улыбнулся ему, как старому знакомому." id ending_forgotten_0012

    mc "Ну и где тут хотя бы кто-нибудь живой?" id ending_forgotten_0013

    "Я хотел ответить ему честно. Что-то очень простое. Вроде: я помню тебя. Ты был здесь. Этого достаточно." id ending_forgotten_0014

    "Но вместо этого услышал собственный голос — весёлый, ровный, чужой:" id ending_forgotten_0015

    mc "Лето только начинается." id ending_forgotten_0016

    "Он вздрогнул. Потом спросил, как пройти к площади." id ending_forgotten_0017

    "Я показал." id ending_forgotten_0018

    "Я всегда показываю." id ending_forgotten_0019

    child "Линейка в семь! Не опаздывай!" id ending_forgotten_0020

    "Где-то далеко щёлкнул динамик и ничего не сказал." id ending_forgotten_0021

    "Я стоял у ворот и ждал следующего." id ending_forgotten_0022

    "Мне было спокойно. Совсем." id ending_forgotten_0023

    "Только иногда, когда ветер шёл со стороны реки, я почему-то трогал нагрудный карман." id ending_forgotten_0024

    "Там ничего не было." id ending_forgotten_0025

    "И никогда не было." id ending_forgotten_0026

    "Просто рука привыкла." id ending_forgotten_0027

    "Иногда к воротам приходят не одни, а вдвоём. Иногда приезжают на машине и оставляют у столба букет — я не знаю зачем, мне не объясняют." id ending_forgotten_0028

    "Однажды пришла женщина лет сорока. Она постояла, посмотрела на меня и спросила:" id ending_forgotten_0029

    "«Вы тут давно работаете?»" id ending_forgotten_0030

    "Я ответил честно:" id ending_forgotten_0031

    mc "С начала смены." id ending_forgotten_0032

    "Она кивнула и ушла. А я остался." id ending_forgotten_0033

    "У меня же линейка в семь." id ending_forgotten_0034

    "Я никогда не опаздываю." id ending_forgotten_0035

    $ ending_shown = "Плохая концовка: «Забытый»"

    call end_card

    return


## ============================================================
## 7. СЕКРЕТНАЯ КОНЦОВКА — «БИЛЕТ НА ДВОИХ»
## Доступна только после ending_true (persistent.true_seen)
## ============================================================

label ending_secret:

    play music main_theme fadein 2.0 if_changed
    scene cg_secret_ticket_two
    with fade

    "Лагерь растворился на рассвете — так же, как в тот раз." id ending_secret_0001

    "Только на этот раз я унёс его с собой." id ending_secret_0002

    "Три удара колокола всё ещё жили во мне. Как и её «спасибо, что пришёл». Некоторые вещи не растворяются на рассвете — они просто становятся тише." id ending_secret_0100

    with fade

    scene bg room
    with fade

    "Коробка из-под обуви стояла на столе. Я разобрал её до конца — впервые за год." id ending_secret_0003

    "Под свитером, на самом дне, был конверт. Незаклеенный." id ending_secret_0004

    "Внутри — ещё один билет." id ending_secret_0005

    "«Сосновый берег». Смена 21-я. Заезд — пятое августа." id ending_secret_0006

    "И фамилия." id ending_secret_0007

    "«Воронов А.»" id ending_secret_0008

    mc "А." id ending_secret_0009

    "Я сел на пол. Прямо на пол, со спиной к кровати, как садятся люди, которым надо переварить слишком много." id ending_secret_0010

    "Двадцать первая смена. Год после двадцатой." id ending_secret_0011

    "Он выписал билет на моё имя." id ending_secret_0012

    "Он собирался поехать сюда со мной." id ending_secret_0013

    "В конверте лежала ещё одна бумага — почтовый бланк, заполненный наполовину. Адрес, которого я не знал: другой город, улица, дом, квартира." id ending_secret_0014

    "И дата. Год назад." id ending_secret_0015

    mc "Ты не пропал. Ты уехал." id ending_secret_0016

    mc "Уехал туда, где тебя никто не спросит про восемнадцатое августа." id ending_secret_0017

    "Я достал фотографию двадцатой смены — ту самую, из-под коряги." id ending_secret_0018

    "Лена и молодой парень в рубашке с чужого плеча. Часы без ремешка." id ending_secret_0019

    "На обороте: «Лена и И. Пусть это лето не кончается»." id ending_secret_0020

    "Я купил рамку. Простую, деревянную, без стекла — чтобы не отражаться." id ending_secret_0021

    "Поставил её на стол. Рядом положил два билета: один выцветший, второй почти новый." id ending_secret_0022

    "Билет на двоих. Он пролежал так двадцать лет." id ending_secret_0023

    "Прошлое осталось памятью, а не клеткой." id ending_secret_0024

    "А впереди было что-то новое." id ending_secret_0025

    "Я написал на бланке одно слово — «еду» — и положил его в карман." id ending_secret_0026

    "Поезд уходил через три дня." id ending_secret_0027

    "Я позвонил маме и сказал, что уезжаю на неделю и что это связано с отцом." id ending_secret_0028

    "Она молчала так долго, что я успел испугаться." id ending_secret_0029

    "Потом спросила: «Ты его нашёл?»" id ending_secret_0030

    "«Нет, — сказал я. — Я нашёл билет»." id ending_secret_0031

    "Она помолчала ещё немного и сказала: «Ну, значит, билет»." id ending_secret_0032

    "И не стала больше спрашивать ни о чём." id ending_secret_0033

    "Я не знал, что скажу отцу. Не знал, откроет ли он вообще." id ending_secret_0034

    "Но я точно знал, что не буду молчать двадцать лет." id ending_secret_0035

    mc "Лена, спасибо. Я понял." id ending_secret_0036

    mc "Отпускать — не значит выбрасывать." id ending_secret_0037

    $ ending_shown = "Секретная концовка: «Билет на двоих»"

    call end_card

    return
