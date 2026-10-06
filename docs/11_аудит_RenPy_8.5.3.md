# АУДИТ СОВМЕСТИМОСТИ И ПОЛНЫЙ АНАЛИЗ
## Ren'Py 8.5.3.26051504 (реальный SDK) · «Лето, которого не было» v0.9-demo

Дата: 2026-10-05. SDK скачан с официального релиза GitHub
(`renpy-8.5.3-sdk.zip`, та же сборка, что у пользователя: 8.5.3.26051504).

---

## 1. ОКРУЖЕНИЕ ПРОВЕРКИ

| Параметр | Значение |
|---|---|
| SDK | renpy-8.5.3-sdk, Python 3.12.8 (bundled), Linux x86_64 |
| Дисплей | headless: `SDL_VIDEODRIVER=dummy`; дополнительно пробовался Xvfb |
| Что работает headless | `lint`, загрузка скриптов, init-код, prepare экранов |
| Что НЕ работает в контейнере | test-runner и любой рендер: dummy-драйвер не даёт GL, Xvfb → segfault |
| Контрольный опыт | **собственное демо SDK `the_question` segfault'ит там же и так же** → ограничение среды, не игры |
| Попытка обойти | установлены Mesa/llvmpipe (`libgl1-mesa-dri`), GL-контекст под Xvfb создаётся (Mesa 22.3.6, GL 4.5); тем не менее `RENPY_RENDERER=gl2/gl/sw` → segmentation fault на инициализации дисплея у нашей игры и у `the_question` одинаково |

Вывод: runtime-проверки дисплея в этом контейнере невозможны ни для нашей игры,
ни для эталонного демо Ren'Py. Всё, что можно проверить без GPU, проверено ниже;
test-кейсы для машины с дисплеем положены в дистрибутив (`tests.rpy`, `tests_autogen.rpy`).

---

## 2. ПРОВЕРКИ НА РЕАЛЬНОМ ДВИЖКЕ

### 2.1 `renpy.sh <project> lint` → **EXIT 0, ноль предупреждений**
```
The game contains 1,410 dialogue blocks, containing 11,037 words and 64,372
characters, for an average of 7.8 words and 46 characters per block.
The game contains 19 menus, 52 images, and 13 screens.
```
Последнее замечание линта (`define sys replaces a built-in`) устранено:
персонаж переименован в `card`.

### 2.2 Headless-подготовка всех экранов (init-хук `prepare_screens`)
`PREPARE_OK ru` — все 13 экранов (say, choice, confirm, main_menu, save, load,
preferences, history, about, notify, quick_menu, game_menu, slot_row) готовятся
без исключений. Именно этот этап ловил все прежние рантайм-краши пользователя
(шрифты, `Preference(...)`, оконные свойства, порядок init gui/screens).

### 2.3 Загрузка и init
Все `.rpy` скомпилированы, init-код
(переменные, образы, `define audio.*`) выполнен без ошибок.

---

## 3. СТАТИЧЕСКИЙ АНАЛИЗАТОР ПРОЕКТА (`tools/validate_project.py`, 12 проверок)

| # | Проверка | Результат |
|---|---|---|
| 1 | единственность `label`, достижимость всех `jump`/`call` | ✅ 40 меток, битых переходов нет |
| 2 | все `scene`/`show`/`hide` указывают на объявленные образы | ✅ 52 образа |
| 3 | все переменные объявлены через `default` | ✅ 25 |
| 4 | говорящий ≠ зарезервированный оператор Ren'Py (`voice`-баг) | ✅ |
| 5 | белый список `config.*` (`loop_music`-баг) | ✅ |
| 6 | порядок init: `gui.rpy` не позже `screens.rpy` (`gui.*`-баг) | ✅ |
| 7 | имена `Preference(...)` из списка 8.5 (`fullscreen`-баг) | ✅ |
| 8 | шрифты: комплект Ren'Py или `game/gui/fonts/` (`DejaVuSerif`-баг) | ✅ |
| 9 | оконные свойства не на контейнерах (`ypadding`-баг) | ✅ |
| 10 | баланс кавычек, отсутствие посторонних алфавитов | ✅ |
| 11 | `play music/sound` → файлы существуют | ✅ 9 треков + 18 SFX |
| 12 | в каждой сцене есть `scene` и музыкальная подсказка | ✅ |

Итог: **0 ошибок, 0 предупреждений**.

---

## 4. ЛОГИКА, ФЛАГИ, КОНЦОВКИ (мини-VM по байткоду сцен)

`tools/sim_web.js` и `tools/gen_rpt.py` исполняют тот же граф сцен, что и движок:

| Прогон | Концовка | Ключевые флаги |
|---|---|---|
| всегда первый выбор | ending_true | truth 9, frag 6, lena 8 |
| всегда последний выбор | ending_forgotten | escape=true |
| маршрут Лены + let_go | ending_true | truth 10, frag 6, lena 11 |
| маршрут Лены + stay | ending_lena_stay | lena 11 |
| маршрут Веры | ending_vera_voice | vera 8+, radio_fixed |
| маршрут Зои | ending_zoya_painting | zoya 8+, drawing_completed |
| одиночество | ending_forgotten | escape=true, выбора нет |
| Вера без поддержки | ending_farewell | vera 6 < 8 |
| true_seen + carry_memory | ending_secret | frag 6, father_clue |

Соответствие ГДД: максимум правды 10, отношений 11, фрагментов 6 — сходится
с разделами 22–24; `father_clue` выдаётся только в `D2_NIGHT_FOREST`;
`escape_flag` сбрасывается в `d3_route_select` и ставится только в `d3_alone`;
при `escape_flag` финальное меню не показывается.

`tools/gen_rpt.py` из этих же прогонов сгенерировал **9 testcase'ов Ren'Py**
(`tests_autogen.rpy`: skip по диалогам + click по подписям меню + `assert eval ending_shown == …`)
и **4 рукописных** (`tests.rpy`: флаги пролога, история, save/load, настройки+English).
Запуск на машине с дисплеем: `renpy.sh <проект> test`.

---

## 5. WEB-СБОРКА (`web_demo/index.html`)

- `node --check` — синтаксис движка ОК;
- `tools/smoke_web.js` (DOM-эмуляция): 1400+ кликов, меню, сохранения,
  карточка истинной концовки, 30–48 аудио-вызовов — **SMOKE OK**;
- найденные и починенные баги движка: зависание при клике во время печати текста;
  неверный путь SFX (`audio/sfx/`);
- 52 изображения inline, аудио — файлы рядом (`web_demo/audio/…`).

---

## 6. КОНТЕНТ-АУДИТ

| Аспект | Состояние |
|---|---|
| Сценарий | 37 блоков сцен (25 сюжетных + ветки/служебные), 11 037 слов, диалоги > описаний |
| Тайна | не раскрывается до `D4_TRUTH`; намёки — 9 сквозных мотивов (таблица в `docs/01`) |
| Голоса персонажей | соблюдены (Артём ироничен, Лена загадками, Вера боится пауз, Зоя пряма) |
| Перевод | 1405/1405 реплик + 109 строк интерфейса/меню EN, 0 без перевода; меню и UI — через `translate english strings:` |
| Арт | 21 фон, 17 спрайтов, 13 CG, 2 меню-арта; единственный плейсхолдер — `zoya scared` (не используется в сценарии) |
| Музыка | 9 тем с лейтмотивами, бесшовные петли, `if_changed` против перезапуска |
| SFX | 18 эффектов, лупы бесшовные |
| Рейтинг 16+ | без жестокости/откровенности/хоррора; трагедия — в прошедшем времени |

---

## 7. ИСТОРИЯ ИСПРАВЛЕННЫХ КЛАССОВ ОШИБОК ЗАПУСКА (7 штук, все с регресс-тестом)

1. Шаблонный `label start` перебивал вход → `install.py` убирает шаблон.
2. `id` на пунктах меню (нет в Ren'Py 8.5) → снят, перевод через `strings:`.
3. Персонаж `voice` = оператор Ren'Py → `young_voice`.
4. `config.loop_music` не существует → удалено (луп и так по умолчанию).
5. Оконные свойства на `hbox/vbox/text` → `frame`.
6. Порядок init `gui.rpy`/`screens.rpy` → `init offset = -1` в gui.
7. `Preference("fullscreen"/"auto-forward")` → значимые формы 8.5 (`display`, `after choices`, `auto-forward time`).
8. `DejaVuSerif.ttf` отсутствует в поставке → `DejaVuSans.ttf`.
9. `define sys` тенит builtin → `card`.

---

## 8. ОСТАТОЧНЫЕ РИСКИ (честно)

- **Test-runner в этом контейнере не запускается** (segfault SDL/X11; воспроизведено на демо SDK).
  Проверены комбинации: dummy/sw, Xvfb+gl2 (Mesa llvmpipe, GL 4.5), Xvfb+gl, Xvfb+sw,
  `LP_NUM_THREADS=1`, `SDL_JOYSTICK_DISABLED=1` — результат одинаков у нашей игры и у `the_question`.
  На машине пользователя с дисплеем `renpy.sh <проект> test` прогонит 13 testcase'ов
  (9 маршрутных + 4 smoke); весь остальной анализ воспроизводится одной командой `./verify.sh`.
- **EN-prepare не проверялся в init**: `change_language` вне рантайма не поддерживается самим Ren'Py;
  в рантайме структура экранов от языка не зависит.
- **Формат файла переводов исправлен повторно (аудит 2026-10-06).** Пары `old/new`
  допустимы только внутри `translate <язык> strings:`; интерфейс, имена говорящих,
  карточки дней и названия концовок переведены блоком strings из общего словаря
  `tools/ui_strings.py` (он же кормит web-плеер), а подсказки движка `layout.*` —
  через `game/i18n.rpy` (`translate None/english python:`).
- **Web-превью в приложении** может не проиграть аудио из соседних файлов (песочница без сети);
  в обычном браузере и на itch.io звук работает.

---

## 9. КАК ПОВТОРИТЬ ПРОВЕРКУ

```bash
# статика + логика
python3 tools/validate_project.py
node tools/sim_web.js
node tools/smoke_web.js

# реальный движок (headless-часть)
SDL_VIDEODRIVER=dummy renpy.sh <проект> lint          # → exit 0

# реальный движок (runtime, нужна машина с дисплеем)
renpy.sh <проект> test                                  # 13 testcase'ов
```
