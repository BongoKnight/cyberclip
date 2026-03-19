/* utils.js – shared utilities */

// ── Type → consistent colour (hash-based, stable) ─────────────────────
const TYPE_COLOR_CACHE = {};
function typeColor(type) {
  if (TYPE_COLOR_CACHE[type]) return TYPE_COLOR_CACHE[type];
  let h = 5381;
  for (let i = 0; i < type.length; i++) h = ((h << 5) + h) ^ type.charCodeAt(i);
  h = h >>> 0;
  const hue = h % 360;
  const sat = 50 + (h >> 8) % 22;
  const lum = 38 + (h >> 16) % 18;
  const c = {
    background: `hsl(${hue},${sat}%,${lum}%)`,
    border:     `hsl(${hue},${sat}%,${Math.max(lum-15,15)}%)`,
    highlight:  { background: `hsl(${hue},${sat+8}%,${lum+16}%)`, border: `hsl(${hue},${sat}%,${lum+8}%)` },
    hover:      { background: `hsl(${hue},${sat}%,${lum+10}%)`,   border: `hsl(${hue},${sat}%,${lum+5}%)` },
    text: '#ffffff',
    raw: `hsl(${hue},${sat}%,${lum}%)`,
  };
  TYPE_COLOR_CACHE[type] = c;
  return c;
}

// ── Debounce ─────────────────────────────────────────────────────────
function debounce(fn, delay = 200) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

// ── UUID ──────────────────────────────────────────────────────────────
function uuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

// ── API helpers ───────────────────────────────────────────────────────
async function apiPost(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const j = await r.json().catch(() => ({}));
    throw new Error(j.error || `HTTP ${r.status}`);
  }
  return r.json();
}
async function apiGet(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

// ── Toast notifications (replaces alert/confirm) ──────────────────────
const _toastCont = (() => {
  const el = document.createElement('div');
  el.id = 'toast-container';
  document.addEventListener('DOMContentLoaded', () => document.body.appendChild(el));
  return el;
})();

function toast(msg, type = 'info', duration = 3500) {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  _toastCont.appendChild(t);
  setTimeout(() => {
    t.classList.add('out');
    setTimeout(() => t.remove(), 220);
  }, duration);
}

// ── Spinner ───────────────────────────────────────────────────────────
let _spinnerCount = 0;
function showSpinner(label = '') {
  _spinnerCount++;
  let el = document.getElementById('spinner-overlay');
  if (!el) {
    el = document.createElement('div');
    el.id = 'spinner-overlay';
    el.innerHTML = `<div style="text-align:center"><div class="spinner"></div><div class="spinner-label" id="spinner-label"></div></div>`;
    document.body.appendChild(el);
  }
  document.getElementById('spinner-label').textContent = label;
  el.classList.remove('hidden');
}
function hideSpinner() {
  _spinnerCount = Math.max(0, _spinnerCount - 1);
  if (_spinnerCount === 0) document.getElementById('spinner-overlay')?.classList.add('hidden');
}

// ── Copy to clipboard ─────────────────────────────────────────────────
function copyText(text) {
  navigator.clipboard.writeText(text)
    .then(() => toast('Copied!', 'success', 1800))
    .catch(() => {
      const ta = document.createElement('textarea');
      ta.value = text; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy'); ta.remove();
      toast('Copied!', 'success', 1800);
    });
}

// ── Escape HTML ───────────────────────────────────────────────────────
function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

// ── Truncate ──────────────────────────────────────────────────────────
function trunc(s, n = 60) {
  s = String(s);
  return s.length > n ? s.slice(0, n) + '…' : s;
}

// ── Check JSON ────────────────────────────────────────────────────────
function looksLikeJson(s) {
  const t = s.trim(); return t.startsWith('{') || t.startsWith('[');
}

// ── Simple confirm (non-blocking dialog) ──────────────────────────────
function confirmDialog(msg) {
  // Falls back to native confirm — can be overridden if needed
  return window.confirm(msg);
}
