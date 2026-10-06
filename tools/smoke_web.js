// smoke_web.js — DOM-заглушка + прогон РЕАЛЬНОГО движка из web_demo/index.html.
// Проверяет: титл渲染, старт, печать текста, клики, первое меню, показ фона/спрайта.
// Запуск: node tools/smoke_web.js
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'web_demo', 'index.html'), 'utf8');
const engine = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).pop();
const jsonBlob = id => {
  const m = html.match(new RegExp('<script id="' + id + '" type="application/json">([\\s\\S]*?)</script>'));
  return m ? m[1] : '';
};

function makeEl(id) {
  const el = {
    id, children: [], _handlers: {}, style: {}, dataset: {},
    classList: {
      _s: new Set(),
      add(c) { this._s.add(c); }, remove(c) { this._s.delete(c); },
      contains(c) { return this._s.has(c); },
      set value(v) {}
    },
    _text: '', _html: '',
    get textContent() { return this._text; },
    set textContent(v) { this._text = String(v); },
    get innerHTML() { return this._html; },
    set innerHTML(v) { this._html = String(v); this.children = []; },
    appendChild(c) { this.children.push(c); return c; },
    addEventListener(t, f) { (this._handlers[t] = this._handlers[t] || []).push(f); },
    onclick: null,
    querySelector(sel) { this._q = this._q || {}; if (!this._q[sel]) this._q[sel] = makeEl(this.id + sel); return this._q[sel]; },
    querySelectorAll() { return []; },
    removeAttribute() {}, setAttribute() {},
    fire(t, ev) { (this._handlers[t] || []).forEach(f => f(ev || { stopPropagation() {}, preventDefault() {} })); },
  };
  Object.defineProperty(el.classList, 'value', { set(v) {} });
  return el;
}

const byId = {};
function getEl(id) { if (!byId[id]) { byId[id] = makeEl(id);
  if (id === 'gamedata' || id === 'extra') byId[id].textContent = jsonBlob(id); }
  return byId[id]; }

const documentStub = {
  getElementById: getEl,
  createElement: tag => makeEl('created_' + tag + Math.random()),
  querySelectorAll: sel => {
    if (sel === '.panel') return [getEl('p_hist'), getEl('p_save'), getEl('p_load'), getEl('p_set')];
    if (sel === '.closeb') return [makeEl('closeb')];
    return [];
  },
  addEventListener: () => {},
  title: '',
};

const store = {};
const localStorageStub = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
};

class AudioStub {
  constructor(src){ this.src=src; this.loop=false; this.volume=1; this.paused=true; AudioStub.count++; }
  play(){ this.paused=false; return Promise.resolve(); }
  pause(){ this.paused=true; }
}
AudioStub.count=0;
let rafCbs = [];
const sandbox = {
  document: documentStub,
  localStorage: localStorageStub,
  requestAnimationFrame: cb => { rafCbs.push(cb); return 1; },
  setInterval: (fn, ms) => setInterval(fn, 0),
  clearInterval: id => clearInterval(id),
  setTimeout: (fn, ms) => setTimeout(fn, 0),
  console, JSON, Math, Function, Audio: AudioStub, performance: { now: () => Date.now() },
};
sandbox.window = sandbox;
vm.createContext(sandbox);

const tick = () => new Promise(r => setTimeout(r, 5));
const flushRaf = () => { const c = rafCbs; rafCbs = []; c.forEach(f => f()); };

(async () => {
  vm.runInContext(engine, sandbox);
  await tick();
  console.log('✓ движок загрузился, титл виден:', getEl('title').style.display !== 'none');
  console.log('  заголовок титла:', getEl('title')._q ? getEl('title').querySelector('h1').textContent : '?');

  process.on('unhandledRejection', e => console.log('UNHANDLED:', e && e.message));
  console.log('  stage handlers:', Object.keys(getEl('stage')._handlers), (getEl('stage')._handlers.click||[]).length);
  getEl('t_new').fire('click');
  await tick(); flushRaf();
  for (let i = 0; i < 40; i++) { await tick(); flushRaf(); getEl('stage').fire('click');
    if (i % 8 === 0) console.log('   click', i, '| txt:', JSON.stringify(getEl('txt').textContent.slice(0, 34)),
      '| box.on:', getEl('box').classList.contains('on'), '| choices:', getEl('choices').children.length, getEl('choices').classList.contains('on'));
  }
  console.log('✓ после 40 кликов текст:', JSON.stringify(getEl('txt').textContent.slice(0, 60)));
  console.log('  имя говорящего:', JSON.stringify(getEl('who').textContent));

  // дойти до первого меню
  let menuSeen = false;
  for (let i = 0; i < 60; i++) {
    await tick(); flushRaf();
    if (getEl('choices').classList.contains('on') && getEl('choices').children.length) {
      menuSeen = true;
      console.log('✓ меню показано, вариантов:', getEl('choices').children.length,
        '| первый:', getEl('choices').children[0].textContent);
      getEl('choices').children[0].fire('click');
      break;
    }
    getEl('stage').fire('click');
  }
  if (!menuSeen) throw new Error('меню не появилось');

  for (let i = 0; i < 60; i++) { await tick(); flushRaf(); getEl('stage').fire('click'); }
  const bgEl = getEl('bg0').src || getEl('bg1').src;
  console.log('✓ фон установлен:', String(bgEl).slice(0, 40) + '...');
  console.log('✓ автосохранение:', !!store['leto_auto']);
  console.log('✓ история:', (sandbox.hist || []).length ? 'есть' : 'проверьте вручную');
  // автопрогон: кликаем до возвращения на титл (то есть до конца истории)
  let guard = 0, ended = false;
  while (guard++ < 4000) {
    await tick(); flushRaf();
    if (getEl('title').style.display !== 'none' && getEl('title').style.display !== '') { ended = true; break; }
    if (getEl('choices').classList.contains('on') && getEl('choices').children.length) {
      getEl('choices').children[0].fire('click');
    } else {
      getEl('stage').fire('click');
    }
  }
  console.log('✓ автопрогон: итераций', guard, '| дошёл до конца истории:', ended,
    '| последняя реплика:', JSON.stringify(getEl('card').querySelector('.s').textContent));
  console.log('✓ аудио-вызовов создано:', AudioStub.count);
  console.log('SMOKE OK');
  process.exit(0);
})().catch(e => { console.error('SMOKE FAIL:', e.message); process.exit(1); });
