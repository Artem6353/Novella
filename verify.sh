#!/usr/bin/env bash
# ============================================================
# verify.sh — единая верификация «Лета, которого не было»
#
#   ./verify.sh                 # статика + логика + web (без SDK)
#   RENPY_SDK=/путь/к/renpy-8.5.3-sdk ./verify.sh
#                               # + lint, headless-prepare и runtime-тесты
#
# Runtime-тесты работают полностью headless (без DISPLAY и GPU):
#   SDL_VIDEODRIVER=dummy + программный рендерер.
#   RENPY_PERFORMANCE_TEST=0 отключает стартовый замер производительности,
#   HOME=<временный> изолирует persistent (иначе язык/флаги концовок
#   протекают между запусками и ломают тесты).
# Полный прогон 13 тесткейсов на sw-рендерере занимает ~10–20 минут.
# ============================================================
set -u
## pipefail обязателен: шаги вида `python3 tool.py | tail -4 || exit 1`
## без него проверяют код возврата ПОСЛЕДНЕЙ команды конвейера (`tail`),
## который успешен всегда. То есть верификация не могла упасть ни на одном
## шаге и всегда рапортовала успех, даже когда инструменты падали.
set -o pipefail
cd "$(dirname "$0")"

echo "=================================================="
echo " 1. СТАТИЧЕСКИЙ АНАЛИЗ (tools/validate_project.py)"
echo "=================================================="
python3 tools/validate_project.py | tail -4 || exit 1

echo
echo "=================================================="
echo " 2. ЛОКАЛИЗАЦИЯ (tools/gen_tl.py)"
echo "=================================================="
python3 tools/gen_tl.py | tail -2 || exit 1

echo
echo "=================================================="
echo " 3. ЛОГИКА МАРШРУТОВ И КОНЦОВОК (мини-VM, node)"
echo "=================================================="
node tools/sim_web.js | grep '✓' | sed 's/^/   /' || exit 1

echo
echo "=================================================="
echo " 4. WEB-ПЛЕЕР: DOM-ЭМУЛЯЦИЯ (node)"
echo "=================================================="
node tools/smoke_web.js | tail -2 || exit 1

if [ -z "${RENPY_SDK:-}" ]; then
    echo
    echo "=================================================="
    echo " 5-7. ПРОПУЩЕНО: задайте RENPY_SDK=/путь/к/renpy-8.5.3-sdk"
    echo "=================================================="
    exit 0
fi

PROJ="${1:-renpy_project}"
SDK="$RENPY_SDK"

echo
echo "=================================================="
echo " 5. REN'PY LINT (реальный движок, headless)"
echo "=================================================="
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$SDK/renpy.sh" "$PROJ" lint | tail -10 || exit 1

echo
echo "=================================================="
echo " 6. HEADLESS-ПОДГОТОВКА ЭКРАНОВ (prepare_check.rpy)"
echo "=================================================="
rm -f "$PROJ/game/prepare_result.txt"
LETO_PREPARE_CHECK=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
    "$SDK/renpy.sh" "$PROJ" lint > /dev/null 2>&1 || true
cat "$PROJ/game/prepare_result.txt" 2>/dev/null || echo "   результата нет (см. log.txt проекта)"

echo
echo "=================================================="
echo " 7. RUNTIME-ТЕСТЫ REN'PY (13 testcase'ов, headless)"
echo "    ВНИМАНИЕ: без GPU используется программный рендерер —"
echo "    прогон может занять 10–20 минут."
echo "=================================================="
# Изолированное окружение: чистые saves/persistent, чтобы результаты
# прошлых прогонов (язык, persistent.true_seen, слоты) не влияли на тесты.
TEST_HOME="$(mktemp -d)"
rm -rf "$PROJ/game/saves" "$PROJ/game/cache"
HOME="$TEST_HOME" \
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy RENPY_PERFORMANCE_TEST=0 \
    "$SDK/renpy.sh" "$PROJ" test --report-detailed | tail -30
TEST_STATUS=${PIPESTATUS[0]}
rm -rf "$TEST_HOME"
rm -rf "$PROJ/game/saves" "$PROJ/game/cache"
if [ "$TEST_STATUS" -ne 0 ]; then
    echo "RUNTIME-ТЕСТЫ: ПРОВАЛ (код $TEST_STATUS)"
    exit 1
fi

echo
echo "Верификация завершена."
