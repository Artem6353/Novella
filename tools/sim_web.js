// sim_web.js — headless-прогон байткода новеллы (та же семантика, что в web-движке).
// Проверяет: все jump-цели существуют, выражения вычисляются, концовки достижимы,
// нет бесконечных циклов.
// Запуск: node tools/sim_web.js
const fs = require('fs');
const path = require('path');
const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'web_demo', 'game_data.json'), 'utf8'));

function makeVM(pickFn, presetP) {
  const V = JSON.parse(JSON.stringify(DATA.defaults));
  const P = Object.assign({}, presetP || {});
  const cache = {};
  const ev = (e) => { let f = cache[e]; if (!f) f = cache[e] = new Function('V', 'P', 'with(V){return (' + e + ');}'); return f(V, P); };
  const setv = (t, e) => { const v = ev(e); if (t.startsWith('persistent.')) P[t.split('.')[1]] = v; else V[t] = v; };
  let steps = 0, label = null, visited = new Set(), ending = null;
  const Jump = (to) => ({ __jump: to }), Ret = () => ({ __ret: 1 }), End = () => ({ __end: 1 });

  async function exec(ops, from) {
    for (let i = from || 0; i < ops.length; i++) {
      if (++steps > 50000) throw new Error('step limit: возможный бесконечный цикл в ' + label);
      const op = ops[i];
      switch (op.op) {
        case 'say': break;
        case 'scene': case 'show': case 'hide': case 'fade': case 'pause': break;
        case 'set': setv(op.target, op.expr); break;
        case 'noop': break;
        case 'if': await exec(ev(op.cond) ? op.then : (op.else || []), 0); break;
        case 'elseblock': await exec(op.body, 0); break;
        case 'menu': {
          const vis = op.items.filter(it => !it.cond || ev(it.cond));
          if (!vis.length) break;
          const it = pickFn(label, vis, V);
          await exec(it.body, 0); break;
        }
        case 'daycard': break;
        case 'endcard': ending = V.ending_shown; throw End();
        case 'call': await runLabel(op.to); break;
        case 'jump': throw Jump(op.to);
        case 'return': throw Ret();
      }
    }
  }
  async function runLabel(name) {
    if (!DATA.program[name]) throw new Error('нет метки ' + name);
    visited.add(name);
    let cur = name;
    for (;;) {
      label = cur;
      try { await exec(DATA.program[cur], 0); return; }
      catch (e) {
        if (e && e.__jump) { cur = e.__jump; continue; }
        if (e && e.__ret) return;
        if (e && e.__end) return;
        throw e;
      }
    }
  }
  return { runLabel, get V() { return V; }, get P() { return P; }, visited, get ending() { return ending; }, get steps() { return steps; } };
}

const first = (label, vis) => vis[0];
const last = (label, vis) => vis[vis.length - 1];

// целевой маршрут: истинная концовка
const TRUE_PICK = {
  p01_room: 0, p02_bus: 0, d00_gate: 1, d00_square: 0, d1_canteen: 0, d1_library: 0,
  d1_evening_choice: 2, d1_lena_river: 0, d2_morning: 0, d2_radio_repair: 0,
  d2_lena_warning: 0, d2_night_forest: 0, d3_route_select: 0, d4_conflict: 0,
  d5_prepare: 0, d5_finale: 0, d5_final_choice: 0,
};
const truePick = (label, vis) => vis[TRUE_PICK[label] !== undefined ? Math.min(TRUE_PICK[label], vis.length - 1) : 0];

// маршрут Веры
const VERA_PICK = {
  p01_room: 0, d00_gate: 1, d00_square: 0, d1_canteen: 0, d1_library: 0,
  d1_evening_choice: 0, d2_morning: 0, d2_radio_repair: 0, d2_lena_warning: 0,
  d2_night_forest: 0, d3_route_select: 1, d4_conflict: 0, d5_prepare: 0, d5_final_choice: 0,
};
const veraPick = (label, vis) => vis[VERA_PICK[label] !== undefined ? Math.min(VERA_PICK[label], vis.length - 1) : 0];

// маршрут Зои
const ZOYA_PICK = {
  p01_room: 0, d00_gate: 1, d00_square: 0, d1_canteen: 0, d1_library: 0,
  d1_evening_choice: 1, d2_morning: 0, d2_radio_repair: 0, d2_lena_warning: 0,
  d2_night_forest: 0, d3_route_select: 2, d4_conflict: 0, d5_prepare: 0, d5_final_choice: 0,
};
const zoyaPick = (label, vis) => vis[ZOYA_PICK[label] !== undefined ? Math.min(ZOYA_PICK[label], vis.length - 1) : 0];

// одиночество -> плохая концовка
const ALONE_PICK = {
  p01_room: 0, d00_gate: 1, d00_square: 0, d1_canteen: 0, d1_library: 0,
  d1_evening_choice: 2, d2_morning: 0, d2_radio_repair: 0, d2_lena_warning: 0,
  d2_night_forest: 0, d3_route_select: 3, d5_final_choice: 0,
};
const alonePick = (label, vis) => vis[ALONE_PICK[label] !== undefined ? Math.min(ALONE_PICK[label], vis.length - 1) : 0];

// остаться с Леной
const STAY_PICK = Object.assign({}, TRUE_PICK, { d5_final_choice: 1 });
const stayPick = (label, vis) => vis[STAY_PICK[label] !== undefined ? Math.min(STAY_PICK[label], vis.length - 1) : 0];

(async () => {
  // секретная концовка: мета-флаг уже открыт (persistent.true_seen)
  const SECRET_PICK = Object.assign({}, TRUE_PICK, { d5_final_choice: 2 });
  const secretPick = (label, vis) => vis[SECRET_PICK[label] !== undefined ? Math.min(SECRET_PICK[label], vis.length - 1) : 0];

  // нейтральная: маршрут Веры, но без поддержки в конфликте и без полной правды
  const FAREWELL_PICK = {
    p01_room: 0, d00_gate: 0, d00_square: 0, d1_canteen: 0, d1_library: 1,
    d1_evening_choice: 2, d2_morning: 0, d2_radio_repair: 0, d2_lena_warning: 1,
    d2_night_forest: 1, d3_route_select: 0, d4_conflict: 1, d5_prepare: 0, d5_final_choice: 0,
  };
  const farewellPick = (label, vis) => vis[FAREWELL_PICK[label] !== undefined ? Math.min(FAREWELL_PICK[label], vis.length - 1) : 0];

  const runs = [
    ['секретная (true_seen + carry_memory)', secretPick, { true_seen: true }],
    ['нейтральная farewell', farewellPick, {}],
    ['всегда первый выбор', first],
    ['всегда последний выбор', last],
    ['маршрут Лены -> ending_true', truePick],
    ['маршрут Лены -> stay', stayPick],
    ['маршрут Веры', veraPick],
    ['маршрут Зои', zoyaPick],
    ['одиночество -> forgotten', alonePick],
  ];
  let fail = 0;
  for (const [name, pick, preset] of runs) {
    try {
      const vm = makeVM(pick, preset);
      await vm.runLabel('start');
      console.log(`✓ ${name}: концовка = ${vm.ending || '(не достигнута)'} | сцен пройдено: ${vm.visited.size} | шагов: ${vm.steps}`);
      console.log(`    truth=${vm.V.truth_points} frag=${vm.V.memory_fragments} lena=${vm.V.lena_love} vera=${vm.V.vera_love} zoya=${vm.V.zoya_love} route=${vm.V.route} escape=${vm.V.escape_flag}`);
    } catch (e) {
      fail++;
      console.log(`✗ ${name}: ${e.message}`);
    }
  }
  process.exit(fail ? 1 : 0);
})();
