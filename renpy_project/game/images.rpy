## ============================================================
## images.rpy
## «Лето, которого не было» — все фоны, спрайты и CG
##
## ВАЖНО: сейчас здесь Solid-плейсхолдеры (раздел 25 дизайн-документа).
## Как только появятся реальные ассеты, замените тело объявления:
##     image bg gate = "images/bg_gate.webp"
## Имя образа менять НЕЛЬЗЯ — на него завязаны все сцены.
##
## Формат реальных фонов: 1920x1080, PNG/WebP.
## Формат спрайтов: высота 1000–1400 px, прозрачный фон, PNG.
## ============================================================

## ------------------------------------------------------------
## ФОН: город (пролог)
## ------------------------------------------------------------
image bg room       = "images/bg_room.jpg"   # Комната Артёма, ночь, лампа
image bg bus        = "images/bg_bus.jpg"   # Автобус, утро

## ------------------------------------------------------------
## ФОН: лагерь «Сосновый берег»
## ------------------------------------------------------------
image bg gate         = "images/bg_gate.jpg" # Ворота лагеря, закат
image bg gate_night      = "images/bg_gate_night.jpg" # Ворота ночью (fallback плохой концовки)
image bg square       = "images/bg_square.jpg" # Главная площадь, закат
image bg square_night    = "images/bg_square_night.jpg" # Главная площадь, ночь
image bg river        = "images/bg_river.jpg" # Река, закат
image bg river_night     = "images/bg_river_night.jpg" # Река и причал, ночь
image bg canteen      = "images/bg_canteen.jpg" # Столовая
image bg library      = "images/bg_library.jpg" # Библиотека / мастерская
image bg radio        = "images/bg_radio.jpg" # Радиоузел
image bg forest_day      = "images/bg_forest_day.jpg" # Лес днём
image bg forest_night    = "images/bg_forest_night.jpg" # Лес ночью
image bg stage           = "images/bg_stage.jpg" # Старая сцена
image bg abandoned       = "images/bg_abandoned.jpg" # Заброшенный корпус / вожатская
image bg campfire        = "images/bg_campfire.jpg" # Костровая поляна
image bg pier            = "images/bg_pier.jpg" # Причал, ночь
image bg dorm_day        = "images/bg_dorm_day.jpg" # Жилой корпус днём
image bg dorm_night      = "images/bg_dorm_night.jpg" # Жилой корпус ночью
image bg dawn            = "images/bg_dawn.jpg" # Рассвет над лагерем (технический фон)

## ------------------------------------------------------------
## СПРАЙТЫ: Лена (6 эмоций, раздел 26)
## ------------------------------------------------------------
image lena normal    = "images/lena_normal.png"
image lena smile     = "images/lena_smile.png"
image lena sad       = "images/lena_sad.png"
image lena anxious   = "images/lena_anxious.png"
image lena surprised  = "images/lena_surprised.png"
image lena mystery    = "images/lena_mystery.png"

## ------------------------------------------------------------
## СПРАЙТЫ: Вера (6 эмоций)
## ------------------------------------------------------------
image vera happy      = "images/vera_happy.png"
image vera excited    = "images/vera_excited.png"
image vera stubborn   = "images/vera_stubborn.png"
image vera offended   = "images/vera_offended.png"
image vera thoughtful = "images/vera_thoughtful.png"
image vera determined = "images/vera_determined.png"
image vera sad        = "images/vera_sad.png"

## ------------------------------------------------------------
## СПРАЙТЫ: Зоя (6 эмоций)
## ------------------------------------------------------------
image zoya calm       = "images/zoya_calm.png"
image zoya sleepy     = "images/zoya_sleepy.png"
image zoya focused    = "images/zoya_focused.png"
## Эмоция `zoya scared` удалена в v1.3.0 (ТЗ v2.0, задача 14):
## файл images/zoya_scared.png не существовал, объявление было Solid-
## заглушкой и не использовалось ни в одной сцене — «мёртвый» образ
## убран, чтобы не вводить в соблазн показать игроку синий прямоугольник.
## Если эмоция понадобится: сгенерировать спрайт (хромокей-пайплайн как
## у остальных), положить images/zoya_scared.png и вернуть объявление
## `image zoya scared = "images/zoya_scared.png"`, затем прогнать
## tools/fix_sprites.py для нормализации высоты 840 px.
image zoya sad        = "images/zoya_sad.png"
image zoya smile      = "images/zoya_smile.png"

## ------------------------------------------------------------
## CG (раздел 25, приоритет P2 — обязательные)
## ------------------------------------------------------------
image cg_lena_gate        = "images/cg_lena_gate.jpg"  # Лена у ворот на фоне заката
image cg_d3_glitch           = "images/cg_d3_glitch.jpg"  # Первый крупный сбой лагеря
image cg_d4_truth_pier       = "images/cg_d4_truth_pier.jpg"  # Причал, ночь, силуэт Лены
image cg_true_last_lineup    = "images/cg_true_last_lineup.jpg"  # Истинная: рассвет и последняя линейка
image cg_lena_stay           = "images/cg_lena_stay.jpg"  # Лена: Артём и Лена у реки
image cg_vera_voice          = "images/cg_vera_voice.jpg"  # Вера: у микрофона, тёплый свет
image cg_zoya_painting       = "images/cg_zoya_painting.jpg"  # Зоя: последний мазок
image cg_farewell_dawn       = "images/cg_farewell_dawn.jpg"  # Нейтральная: ворота на рассвете
image cg_forgotten_gate      = "images/cg_forgotten_gate.jpg"  # Плохая: размытая фигура у ворот
image cg_secret_ticket_two   = "images/cg_secret_ticket_two.jpg" # Секретная: билет и фото в рамке

## ------------------------------------------------------------
## CG (раздел 25, приоритет P1 — опциональные)
## Подключаются в сценах комментариями: раскомментируйте строку
## "scene cg_*", когда иллюстрация будет готова.
## ------------------------------------------------------------
image cg_vera_meet        = "images/cg_vera_meet.jpg"  # Знакомство с Верой у радиоузла
image cg_zoya_meet        = "images/cg_zoya_meet.jpg"  # Знакомство с Зоей и рисунком
image cg_lena_river       = "images/cg_lena_river.jpg"   # Лена у реки на закате


## ------------------------------------------------------------
## ТРАНСФОРМЫ СПРАЙТОВ
## Встроенные at left/center/right центрируют спрайт по вертикали,
## из-за чего высокие спрайты обрезаются сверху. Здесь спрайт
## стоит ногами на нижней кромке экрана и отмасштабирован под 1080p.
## ------------------------------------------------------------
transform tr_left:
    xalign 0.22 yalign 1.0 zoom 1.18

transform tr_center:
    xalign 0.50 yalign 1.0 zoom 1.18

transform tr_right:
    xalign 0.78 yalign 1.0 zoom 1.18
