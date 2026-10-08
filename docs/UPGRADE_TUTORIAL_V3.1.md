# Апгрейд кода по мотивам tutorial_for_renpy (v3.1)

Дата: 2026-10-08. Источник практик: https://github.com/Artem6353/tutorial_for_renpy
(официальный туториал Ren'Py: screens, ATL, preferences, transitions).

## Что изменено

### 1. ATL-трансформы спрайтов (`game/images.rpy`) — по образцу `tutorial_atl.rpy`
- `tr_left/tr_center/tr_right`: плавное появление (fade + подъём снизу 16px, 0.35s)
  через `on show` и мягкая смена эмоции через `on replace` — раньше спрайты
  «прыгали» при смене эмоции.
- Новый `cg_kens`: медленный наезд камеры (zoom 1.0 → 1.06 за 22s) для CG-иллюстраций.
- Новый `tr_pop`: акцентный «шаг вперёд» для важных реплик (по желанию сценариста).

### 2. CG-сцены (`game/scenes/*.rpy`)
- Все 13 вхождений `scene cg_*` получили `at cg_kens` — киноэффект на всех CG.

### 3. Экраны (`game/screens.rpy`) — по образцу `tutorial_screens.rpy`
- `skip_indicator`: штатный индикатор пропуска (движок показывает сам при скипе).
- `help` (+ кнопка «Справка» в game_menu): клавиатура/мышь/быстрое меню — по образцу
  `keyboard_help/mouse_help/gamepad_help` туториала, в палитре проекта.
- Настройки: секция «Прохождение» с `Preference("skip unseen", "toggle")`
  (валидатор проекта принимает только имена из белого списка Ren'Py 8.5).

### 4. Опции (`game/options.rpy`) — по образцу `tutorial/game/options.rpy`
- `config.has_sound/has_music = True`, `config.has_voice = False`;
- `config.enter_transition/exit_transition/intra_transition = dissolve`.

## Что НЕ менялось (осознанно)
- Сценарий (40 меток, ~1443 реплики): принят приёмкой; туториал учит практикам кода,
  а не нарративу. Точечный проход по тексту (текст-теги, паузы) — отдельная задача.
- Арт/CG/музыка: только что заменены на v3.0 финалы.
- Сборка (`dist_pack`, `tools/make_release_zip.py`): не трогали, чтобы не сломать релизный контур.

## Проверки
- `tools/validate_project.py`: ОШИБОК НЕ НАЙДЕНО ✓, ПРЕДУПРЕЖДЕНИЙ НЕТ ✓
- Совместимость сейвов: трансформы/экраны аддитивны; переменные не переименовывались.
