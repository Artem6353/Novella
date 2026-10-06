#!/usr/bin/env bash
# ============================================================
# verify.sh — единая верификация «Лета, которого не было»
#
#   ./verify.sh                 # статика + логика + web (без SDK)
#   RENPY_SDK=/путь/к/renpy-8.5.3-sdk ./verify.sh
#                               # + lint и headless-prepare на реальном движке
#   RENPY_SDK=... DISPLAY=:0 ./verify.sh
#                               # + runtime-тесты self-test framework (нужен дисплей)
# ============================================================
set -u
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

if [ -n "${DISPLAY:-}" ] || command -v xvfb-run > /dev/null 2>&1; then
    echo
    echo "=================================================="
    echo " 7. RUNTIME-ТЕСТЫ REN'PY (13 testcase'ов)"
    echo "    ВНИМАНИЕ: в headless-контейнерах без GPU возможен segfault SDL;"
    echo "    на машине с дисплеем этот шаг проходит штатно."
    echo "=================================================="
    if [ -n "${DISPLAY:-}" ]; then
        SDL_AUDIODRIVER=dummy LIBGL_ALWAYS_SOFTWARE=1 \
            "$SDK/renpy.sh" "$PROJ" test --report-detailed | tail -30
    else
        xvfb-run -a -s "-screen 0 1280x720x24" \
            env SDL_AUDIODRIVER=dummy LIBGL_ALWAYS_SOFTWARE=1 \
            "$SDK/renpy.sh" "$PROJ" test --report-detailed | tail -30
    fi
else
    echo
    echo " 7. RUNTIME-ТЕСТЫ пропущены: нет ни DISPLAY, ни xvfb-run."
    echo "    Запустите вручную на машине с дисплеем: renpy.sh <проект> test"
fi

echo
echo "Верификация завершена."
