const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

// Run the shipped navigation against controlled layout/animation changes.
function page({ mobile = false, hash = '' } = {}) {
  const state = { y: 0, height: mobile ? 51 : 71, menuOpen: false,
    tops: { top: 0, news: 1000, publications: 2000 }, animations: [], offsets: {} };
  const events = new Map();
  const window = {
    location: { hash, pathname: '/', search: '' },
    history: { pushState(_, __, url) { window.location.hash = url.includes('#') ? url.slice(url.indexOf('#')) : ''; } },
    matchMedia: () => ({ matches: false }),
    scrollTo(_, y) { state.y = y; }
  };
  Object.defineProperty(window, 'pageYOffset', { get: () => state.y });
  const root = {};
  const document = {
    scrollingElement: root,
    documentElement: { style: { setProperty(k, v) { state.offsets[k] = v; } } },
    getElementById(id) {
      return Object.hasOwn(state.tops, id) ? {
        id, getBoundingClientRect: () => ({ top: state.tops[id] - state.y })
      } : null;
    },
    fonts: { ready: { then(fn) { state.fontReady = fn; } } }
  };
  function listener(key) {
    return { on(names, fn) {
      names.split(' ').forEach(name => {
        const id = key + ':' + name;
        events.set(id, [...(events.get(id) || []), fn]);
      });
      return this;
    } };
  }
  const scroller = {
    stop() { state.animations.forEach(a => { a.cancelled = true; }); return this; },
    animate(properties, duration, finish) {
      state.animations.push({ properties, duration, finish }); return this;
    }
  };
  const toggle = { is: () => mobile };
  const header = { outerHeight: () => state.height - 1 };
  const navbar = {
    outerHeight: () => state.menuOpen ? 350 : state.height,
    find: selector => selector === '.navbar-toggle' ? toggle : header,
    css: name => name === 'border-bottom-width' ? '1px' : '0px'
  };
  const menu = {
    get length() { return state.menuOpen ? 1 : 0; },
    one(_, fn) { state.menuHidden = fn; return this; },
    collapse() { state.hideRequested = true; return this; }
  };
  function $(value) {
    if (value === window) return listener('window');
    if (value === root) return scroller;
    if (value && value.id) return { hasClass: () => value.id !== 'top' };
    if (value === '#homepage') return { length: 1 };
    if (value === '#navbar-main') return navbar;
    if (value === '#navbar-main .navbar-toggle') return toggle;
    if (value === '#navbar-main .navbar-collapse.in, #navbar-main .navbar-collapse.collapsing') return menu;
    if (value === '#navbar-main li.nav-item a' || value === '#back_to_top') return listener(value);
    throw new Error('Unexpected scrolling target or selector: ' + value);
  }
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../js/hugo-academic.js'), 'utf8'), { jQuery: $, window, document });
  state.emit = (type, extra = {}) => (events.get('window:' + type) || []).forEach(fn => fn({ type, ...extra }));
  state.click = hash => events.get('#navbar-main li.nav-item a:click')[0].call({ hash }, { preventDefault() {} });
  state.complete = () => {
    const a = state.animations.at(-1);
    assert.ok(!a.cancelled);
    state.y = a.properties.scrollTop;
    a.finish();
  };
  state.window = window;
  return state;
}

test('re-measures target and navbar after layout changes during a click', () => {
  const p = page();
  p.click('#news');
  p.tops.news -= 80; // Late font wrapping moves the section upwards.
  p.height = 141; // Navigation wraps at an intermediate desktop width.
  p.complete();
  assert.equal(p.y, 920 - 141 - 24);
  assert.equal(p.window.location.hash, '#news');
});

test('a stale completion cannot override a newer navigation request', () => {
  const p = page();
  p.click('#news');
  const staleFinish = p.animations[0].finish;
  p.click('#publications');
  p.complete();
  staleFinish();
  assert.equal(p.y, 2000 - 71 - 24);
});

test('mobile navigation waits until the expanded menu is hidden', () => {
  const p = page({ mobile: true });
  p.menuOpen = true;
  p.click('#news');
  assert.equal(p.animations.length, 0);
  assert.equal(p.hideRequested, true);
  p.menuOpen = false;
  p.menuHidden();
  p.complete();
  assert.equal(p.y, 1000 - 51 - 24);
});

test('direct anchors realign after fonts and resize, but manual scrolling cancels it', () => {
  const p = page({ hash: '#publications' });
  p.emit('load');
  assert.equal(p.y, 2000 - 71 - 24);
  p.tops.publications -= 80;
  p.fontReady();
  assert.equal(p.y, 1920 - 71 - 24);
  p.height = 141;
  p.emit('resize');
  assert.equal(p.y, 1920 - 141 - 24);
  p.emit('wheel', { preventDefault() { assert.fail('Do not hijack native wheel scrolling'); } });
  p.y = 2500;
  p.fontReady();
  assert.equal(p.y, 2500);
});

test('wheel input cancels pending animation corrections', () => {
  const p = page();
  p.click('#news');
  const finish = p.animations[0].finish;
  p.emit('wheel');
  p.y = 500;
  finish();
  assert.equal(p.y, 500);
});
