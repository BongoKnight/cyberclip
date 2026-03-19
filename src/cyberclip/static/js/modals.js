/* modals.js – all modal dialogs */

// ── Generic helpers ───────────────────────────────────────────────────
function openModal(id)  { document.getElementById(id).classList.remove('hidden'); }
function closeModal(id) { document.getElementById(id).classList.add('hidden'); }

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.modal-close').forEach(btn =>
    btn.addEventListener('click', () =>
      btn.closest('.modal-overlay').classList.add('hidden')
    )
  );
  document.querySelectorAll('.modal-overlay').forEach(overlay =>
    overlay.addEventListener('click', e => {
      if (e.target === overlay) overlay.classList.add('hidden');
    })
  );
});

// ── Full text modal ───────────────────────────────────────────────────
function showFullText(title, text) {
  document.getElementById('fulltext-title').textContent = title;
  document.getElementById('fulltext-body').textContent = text;
  openModal('fulltext-modal');
}
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-fulltext-copy').addEventListener('click', () =>
    copyText(document.getElementById('fulltext-body').textContent)
  );
});

// ── Params modal ──────────────────────────────────────────────────────
// ── JSON pick button helper ───────────────────────────────────────────
// Creates a small button that opens JSON selector and calls onPath(path) with selected path
function _makeJsonPickButton(jsonValue, onPath) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn btn-sm';
  btn.style.marginTop = '4px';
  btn.textContent = '🌲 Pick from JSON';
  btn.title = 'Open JSON selector to choose a field path';
  btn.addEventListener('click', () => {
    let data;
    try { data = JSON.parse(jsonValue); } catch { toast('Cannot parse JSON', 'error'); return; }
    // Temporarily close params modal, open JSON selector, then restore
    const paramsModal = document.getElementById('params-modal');
    paramsModal.style.opacity = '0.3';
    openJsonSelectorFromNode(jsonValue, 'Select field path', (paths) => {
      paramsModal.style.opacity = '';
      if (paths.length) {
        // Call for each selected path
        paths.forEach(p => onPath(p));
      }
    });
  });
  return btn;
}

function showParamsModal(action, jsonNodeValue = null) {
  return new Promise(resolve => {
    const schema = action.complex_param || {};
    if (!Object.keys(schema).length) { resolve({}); return; }

    document.getElementById('params-modal-title').textContent =
      `Parameters: ${action.description || action.name}`;
    const body = document.getElementById('params-modal-body');
    body.innerHTML = '';
    const paramValues = {};

    Object.entries(schema).forEach(([key, def]) => {
      const grp = document.createElement('div'); grp.className = 'param-group';
      const lbl = document.createElement('div'); lbl.className = 'param-label'; lbl.textContent = key;
      grp.appendChild(lbl);

      const type = def?.type || 'text';
      const defVal = def?.value ?? def ?? '';

      if (type === 'tags') {
        const wrap = document.createElement('div'); wrap.className = 'tags-input-wrap';
        const current = Array.isArray(defVal) ? [...defVal] : [];
        paramValues[key] = { type: 'tags', value: [...current] };
        const renderTags = () => {
          wrap.innerHTML = '';
          paramValues[key].value.forEach(tag => {
            const pill = document.createElement('span'); pill.className = 'tag-pill';
            const txt = document.createTextNode(tag);
            const del = document.createElement('button'); del.type = 'button'; del.textContent = '✕';
            del.addEventListener('click', () => { paramValues[key].value = paramValues[key].value.filter(t => t !== tag); renderTags(); });
            pill.append(txt, del); wrap.appendChild(pill);
          });
          const inp = document.createElement('input'); inp.type = 'text'; inp.placeholder = 'Add tag, press Enter…';
          inp.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ',') {
              e.preventDefault();
              const v = inp.value.trim();
              if (v && !paramValues[key].value.includes(v)) { paramValues[key].value.push(v); renderTags(); }
              else inp.value = '';
            }
            if (e.key === 'Backspace' && !inp.value && paramValues[key].value.length) { paramValues[key].value.pop(); renderTags(); }
          });
          wrap.appendChild(inp);
          wrap.addEventListener('click', () => inp.focus());
        };
        renderTags();
        grp.appendChild(wrap);
        // JSON selector button for tags params too (e.g. extract fields list)
        if (jsonNodeValue) {
          const jsonPickBtn = _makeJsonPickButton(jsonNodeValue, (path) => {
            if (!paramValues[key].value.includes(path)) {
              paramValues[key].value.push(path); renderTags();
            }
          });
          grp.appendChild(jsonPickBtn);
        }

      } else if (type === 'list' || type === 'fixedlist') {
        const choices = def?.choices || [];
        if (type === 'list') {
          const sel = document.createElement('select'); sel.className = 'param-select';
          choices.forEach(o => {
            const opt = document.createElement('option'); opt.value = o; opt.textContent = o;
            if (o === String(defVal)) opt.selected = true;
            sel.appendChild(opt);
          });
          paramValues[key] = { type: 'list', value: String(defVal) };
          sel.addEventListener('change', e => { paramValues[key].value = e.target.value; });
          grp.appendChild(sel);
        } else {
          const wrap = document.createElement('div'); wrap.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;';
          const selected = Array.isArray(defVal) ? [...defVal] : [];
          paramValues[key] = { type: 'fixedlist', value: [...selected] };
          choices.forEach(o => {
            const lbl2 = document.createElement('label'); lbl2.className = 'checkbox-label';
            lbl2.style.cssText = 'background:var(--bg3);padding:4px 8px;border-radius:5px;border:1px solid var(--border);';
            const cb = document.createElement('input'); cb.type = 'checkbox'; cb.value = o; cb.checked = selected.includes(o);
            cb.addEventListener('change', () => {
              if (cb.checked) paramValues[key].value.push(o);
              else paramValues[key].value = paramValues[key].value.filter(v => v !== o);
            });
            lbl2.append(cb, document.createTextNode(' ' + o)); wrap.appendChild(lbl2);
          });
          grp.appendChild(wrap);
        }

      } else if (type === 'bool' || type === 'boolean') {
        const row = document.createElement('div'); row.className = 'param-bool-row';
        const toggle = document.createElement('label'); toggle.className = 'param-toggle';
        const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = !!defVal;
        const track = document.createElement('span'); track.className = 'param-toggle-track';
        const thumb = document.createElement('span'); thumb.className = 'param-toggle-thumb';
        toggle.append(cb, track, thumb);
        const valLbl = document.createElement('span');
        valLbl.textContent = cb.checked ? 'Enabled' : 'Disabled';
        valLbl.style.cssText = 'font-size:12px;color:var(--text2)';
        paramValues[key] = { type: 'bool', value: !!defVal };
        cb.addEventListener('change', () => { paramValues[key].value = cb.checked; valLbl.textContent = cb.checked ? 'Enabled' : 'Disabled'; });
        row.append(toggle, valLbl); grp.appendChild(row);

      } else if (type === 'jsonpath' || type === 'json_path' || type === 'json') {
        // ── Inline jq path selector widget ───────────────────────────────
        // Self-contained: paste JSON or auto-loads from selected node.
        // Renders a live JSON tree; clicking a leaf adds its jq path as a tag.
        paramValues[key] = { type: 'jsonpath', value: Array.isArray(defVal) ? [...defVal] : (defVal ? [String(defVal)] : []) };

        const container = document.createElement('div');
        container.className = 'param-jsonpath-container';

        // ── Row 1: source selector ──────────────────────────────────────
        const sourceRow = document.createElement('div');
        sourceRow.style.cssText = 'display:flex;gap:6px;align-items:center;flex-wrap:wrap;';

        const srcLabel = document.createElement('span');
        srcLabel.style.cssText = 'font-size:11px;color:var(--text2);flex-shrink:0;';
        srcLabel.textContent = 'JSON source:';

        const loadNodeBtn = document.createElement('button');
        loadNodeBtn.type = 'button'; loadNodeBtn.className = 'btn btn-sm';
        loadNodeBtn.textContent = jsonNodeValue ? '📋 Load from selected node' : '📋 No JSON node selected';
        if (!jsonNodeValue) loadNodeBtn.disabled = true;

        const pasteHint = document.createElement('span');
        pasteHint.style.cssText = 'font-size:11px;color:var(--text3);';
        pasteHint.textContent = '— or paste JSON below ↓';
        sourceRow.append(srcLabel, loadNodeBtn, pasteHint);

        // ── Row 2: JSON paste area (collapsible) ────────────────────────
        const pasteArea = document.createElement('textarea');
        pasteArea.className = 'param-textarea';
        pasteArea.rows = 3;
        pasteArea.placeholder = 'Paste JSON here to browse its fields…';
        pasteArea.style.fontFamily = 'monospace';
        if (jsonNodeValue) {
          pasteArea.value = jsonNodeValue;
        }

        // ── Row 3: JSON tree ────────────────────────────────────────────
        const treeWrap = document.createElement('div');
        treeWrap.className = 'param-jsonpath-tree';

        // ── Row 4: selected path tags ────────────────────────────────────
        const tagsLabel = document.createElement('div');
        tagsLabel.style.cssText = 'font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:.06em;margin-top:4px;';
        tagsLabel.textContent = 'Selected jq paths (click to remove):';

        const tagsEl = document.createElement('div'); tagsEl.className = 'json-tags param-jsonpath-tags';

        // ── Render path tags ─────────────────────────────────────────────
        const renderPathTags = () => {
          tagsEl.innerHTML = '';
          paramValues[key].value.forEach(p => {
            const tag = document.createElement('span'); tag.className = 'json-path-tag';
            tag.textContent = p; tag.title = 'Click to remove';
            tag.addEventListener('click', () => {
              paramValues[key].value = paramValues[key].value.filter(x => x !== p);
              renderPathTags();
            });
            tagsEl.appendChild(tag);
          });
        };
        renderPathTags();

        // ── Row 5: manual path input ─────────────────────────────────────
        const manualRow = document.createElement('div');
        manualRow.style.cssText = 'display:flex;gap:6px;align-items:center;';
        const manualInp = document.createElement('input');
        manualInp.type = 'text'; manualInp.className = 'param-input';
        manualInp.placeholder = 'Type jq path manually, e.g. .name or ."items"[]."id"';
        manualInp.style.fontFamily = 'monospace';
        const addManualBtn = document.createElement('button');
        addManualBtn.type = 'button'; addManualBtn.className = 'btn btn-sm'; addManualBtn.textContent = '＋ Add';
        addManualBtn.addEventListener('click', () => {
          const v = manualInp.value.trim();
          if (v && !paramValues[key].value.includes(v)) { paramValues[key].value.push(v); renderPathTags(); manualInp.value = ''; }
        });
        manualInp.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); addManualBtn.click(); } });
        manualRow.append(manualInp, addManualBtn);

        // ── Inline tree renderer (mirrors openJsonSelectorFromNode) ──────
        let _inlineRowPathMap = new WeakMap();
        let _inlineSelectedPaths = [...paramValues[key].value];

        const renderInlineTree = (jsonStr) => {
          treeWrap.innerHTML = '';
          _inlineRowPathMap = new WeakMap();
          let data;
          try { data = JSON.parse(jsonStr); } catch { treeWrap.textContent = ''; return; }

          const togglePath = (path, row) => {
            const idx = _inlineSelectedPaths.indexOf(path);
            if (idx === -1) {
              _inlineSelectedPaths.push(path);
              row.classList.add('jt-selected');
              if (!paramValues[key].value.includes(path)) { paramValues[key].value.push(path); renderPathTags(); }
            } else {
              _inlineSelectedPaths.splice(idx, 1);
              row.classList.remove('jt-selected');
              paramValues[key].value = paramValues[key].value.filter(x => x !== path);
              renderPathTags();
            }
          };

          const attachToggle = (row, children) => {
            const t = row.querySelector('.jt-toggle'); t.textContent = '▾'; t.style.cursor = 'pointer';
            t.addEventListener('click', e => { e.stopPropagation(); children.classList.toggle('collapsed'); t.textContent = children.classList.contains('collapsed') ? '▸' : '▾'; });
          };

          const makeRow = (key2, val, isIdx, jqPath) => {
            const row = document.createElement('div'); row.className = 'jt-row';
            if (_inlineSelectedPaths.includes(jqPath)) row.classList.add('jt-selected');
            _inlineRowPathMap.set(row, jqPath);
            const toggle = document.createElement('span'); toggle.className = 'jt-toggle'; toggle.textContent = ' ';
            const keyEl = document.createElement('span'); keyEl.className = isIdx ? 'jt-index' : 'jt-key';
            keyEl.textContent = isIdx ? key2 : ('"' + key2 + '"');
            const colon = document.createElement('span'); colon.className = 'jt-colon'; colon.textContent = ': ';
            const valEl = document.createElement('span');
            if      (val === null)              { valEl.className = 'jt-type-null'; valEl.textContent = 'null'; }
            else if (typeof val === 'boolean')  { valEl.className = 'jt-type-bool'; valEl.textContent = String(val); }
            else if (typeof val === 'number')   { valEl.className = 'jt-type-num';  valEl.textContent = String(val); }
            else if (typeof val === 'string')   { valEl.className = 'jt-type-str';  valEl.textContent = '"' + (val.length > 60 ? val.slice(0,60)+'…' : val) + '"'; }
            else if (Array.isArray(val))        { valEl.className = 'jt-type-arr';  valEl.textContent = '[ ' + val.length + ' ]'; }
            else                                { valEl.className = 'jt-type-obj';  valEl.textContent = '{ ' + Object.keys(val).length + ' }'; }
            const hint = document.createElement('span'); hint.className = 'jt-path-hint'; hint.textContent = jqPath || '.';
            row.title = 'jq: ' + (jqPath || '.');
            row.append(toggle, keyEl, colon, valEl, hint);
            row.addEventListener('click', e => { if (e.target === toggle) return; togglePath(jqPath, row); });
            return row;
          };

          const buildObj = (obj, container2, parentPath) => {
            Object.entries(obj).forEach(([k, v]) => {
              const isArr = Array.isArray(v), isObj = typeof v === 'object' && v !== null && !isArr;
              const seg = parentPath === '' ? ('."' + k + '"') : (parentPath + '."' + k + '"');
              const nodePath = isArr ? seg + '[]' : seg;
              const row = makeRow(k, v, false, nodePath);
              container2.appendChild(row);
              if (isObj || isArr) {
                const cd = document.createElement('div'); cd.className = 'jt-node jt-children';
                isArr ? buildArr(v, cd, nodePath) : buildObj(v, cd, nodePath);
                container2.appendChild(cd);
                attachToggle(row, cd);
              }
            });
          };

          const buildArr = (arr, container2, arrayPath) => {
            arr.slice(0, 100).forEach((item, i) => {
              const isLeaf = typeof item !== 'object' || item === null;
              const itemPath = isLeaf ? (arrayPath.endsWith('[]') ? arrayPath.slice(0,-2) + '[' + item + ']' : arrayPath + '[' + item + ']') : arrayPath;
              const row = makeRow('[' + i + ']', item, true, itemPath);
              container2.appendChild(row);
              if (!isLeaf) {
                const cd = document.createElement('div'); cd.className = 'jt-node jt-children';
                Array.isArray(item) ? buildArr(item, cd, itemPath + '[]') : buildObj(item, cd, itemPath);
                container2.appendChild(cd);
                attachToggle(row, cd);
              }
            });
          };

          if (Array.isArray(data)) buildArr(data, treeWrap, '.[]');
          else if (typeof data === 'object' && data !== null) buildObj(data, treeWrap, '');
        };

        // ── Wire up events ────────────────────────────────────────────────
        const debouncedRender = debounce((v) => renderInlineTree(v), 400);
        pasteArea.addEventListener('input', e => debouncedRender(e.target.value));

        loadNodeBtn.addEventListener('click', () => {
          if (jsonNodeValue) { pasteArea.value = jsonNodeValue; renderInlineTree(jsonNodeValue); }
        });

        // Initial render
        if (jsonNodeValue) renderInlineTree(jsonNodeValue);
        else if (pasteArea.value) renderInlineTree(pasteArea.value);

        container.append(sourceRow, pasteArea, treeWrap, tagsLabel, tagsEl, manualRow);
        grp.appendChild(container);

      } else if (type === 'longtext') {
        const ta = document.createElement('textarea'); ta.className = 'param-textarea'; ta.value = String(defVal); ta.rows = 4;
        paramValues[key] = { type: 'longtext', value: String(defVal) };
        ta.addEventListener('input', e => { paramValues[key].value = e.target.value; });
        grp.appendChild(ta);

      } else if (type === 'save') {
        const inp = document.createElement('input'); inp.className = 'param-input'; inp.type = 'text';
        inp.value = String(defVal); inp.placeholder = './output.txt';
        paramValues[key] = { type: 'save', value: String(defVal) };
        inp.addEventListener('input', e => { paramValues[key].value = e.target.value; });
        grp.appendChild(inp);

      } else {
        const inp = document.createElement('input'); inp.className = 'param-input'; inp.type = 'text'; inp.value = String(defVal);
        paramValues[key] = { type: 'text', value: String(defVal) };
        inp.addEventListener('input', e => { paramValues[key].value = e.target.value; });
        grp.appendChild(inp);
        // JSON selector button: if a JSON node is selected, allow picking a field path
        if (jsonNodeValue) {
          const jsonPickBtn = _makeJsonPickButton(jsonNodeValue, (path) => {
            inp.value = path; paramValues[key].value = path;
          });
          grp.appendChild(jsonPickBtn);
        }
      }
      body.appendChild(grp);
    });

    openModal('params-modal');
    const runBtn = document.getElementById('btn-params-run');
    const cancelBtn = document.getElementById('btn-params-cancel');
    const newRun = runBtn.cloneNode(true); const newCancel = cancelBtn.cloneNode(true);
    runBtn.replaceWith(newRun); cancelBtn.replaceWith(newCancel);
    newRun.addEventListener('click',    () => { closeModal('params-modal'); resolve(paramValues); });
    newCancel.addEventListener('click', () => { closeModal('params-modal'); resolve(null); });
  });
}

// ── Metadata picker modal ─────────────────────────────────────────────
function showMetaPickModal(node) {
  return new Promise(resolve => {
    const meta = node.metadata || {};
    const keys = Object.keys(meta).filter(k => meta[k]);
    if (!keys.length) { toast('No metadata on this node', 'warn'); resolve(null); return; }

    let modal = document.getElementById('meta-pick-modal');
    if (!modal) {
      modal = document.createElement('div'); modal.id = 'meta-pick-modal'; modal.className = 'modal-overlay';
      modal.innerHTML = `
        <div class="modal">
          <div class="modal-header"><span>Create nodes from metadata</span><button class="modal-close btn-icon">✕</button></div>
          <div class="modal-body">
            <div style="font-size:12px;color:var(--text2)">Pick a metadata field to parse into new nodes:</div>
            <div class="meta-pick-list" id="meta-pick-list"></div>
          </div>
          <div class="modal-footer"><button id="btn-meta-pick-cancel" class="btn">Cancel</button></div>
        </div>`;
      document.body.appendChild(modal);
      modal.querySelector('.modal-close').addEventListener('click', () => { modal.classList.add('hidden'); resolve(null); });
      modal.addEventListener('click', e => { if (e.target === modal) { modal.classList.add('hidden'); resolve(null); } });
    }
    const list = document.getElementById('meta-pick-list'); list.innerHTML = '';
    keys.forEach(k => {
      const item = document.createElement('div'); item.className = 'meta-pick-item';
      const kEl = document.createElement('div'); kEl.className = 'meta-pick-key'; kEl.textContent = k;
      const vEl = document.createElement('div'); vEl.className = 'meta-pick-val'; vEl.textContent = trunc(String(meta[k]), 100);
      item.append(kEl, vEl);
      item.addEventListener('click', () => { modal.classList.add('hidden'); resolve({ key: k, value: String(meta[k]) }); });
      list.appendChild(item);
    });
    document.getElementById('btn-meta-pick-cancel').onclick = () => { modal.classList.add('hidden'); resolve(null); };
    modal.classList.remove('hidden');
  });
}

// ── Datatype selection modal ──────────────────────────────────────────
function showDatatypeModal(availableTypes) {
  return new Promise(resolve => {
    if (!availableTypes || !availableTypes.length) {
      toast('No data types available', 'warn');
      resolve(null);
      return;
    }

    const modal = document.getElementById('datatype-modal');
    const list = document.getElementById('datatype-list');
    const deleteCheckbox = document.getElementById('datatype-delete-original');
    const confirmBtn = document.getElementById('btn-datatype-confirm');
    const cancelBtn = document.getElementById('btn-datatype-cancel');

    // Clear and populate datatype list
    list.innerHTML = '';
    const selectedTypes = new Set();

    // Select all by default
    availableTypes.forEach(type => selectedTypes.add(type));

    const renderTypes = () => {
      list.innerHTML = '';
      availableTypes.forEach(type => {
        const item = document.createElement('label');
        item.className = 'datatype-item' + (selectedTypes.has(type) ? ' selected' : '');

        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = selectedTypes.has(type);
        cb.addEventListener('change', () => {
          if (cb.checked) selectedTypes.add(type);
          else selectedTypes.delete(type);
          renderTypes();
        });

        const label = document.createElement('span');
        label.className = 'datatype-label';
        label.textContent = type;

        item.append(cb, label);
        item.addEventListener('click', e => {
          if (e.target !== cb) {
            cb.checked = !cb.checked;
            cb.dispatchEvent(new Event('change'));
          }
        });

        list.appendChild(item);
      });
    };

    renderTypes();

    // Event handlers
    const cleanup = () => {
      modal.classList.add('hidden');
      confirmBtn.replaceWith(confirmBtn.cloneNode(true));
      cancelBtn.replaceWith(cancelBtn.cloneNode(true));
    };

    const handleConfirm = () => {
      if (!selectedTypes.size) {
        toast('Please select at least one data type', 'warn');
        return;
      }
      cleanup();
      resolve({
        types: Array.from(selectedTypes),
        deleteOriginal: deleteCheckbox.checked
      });
    };

    const handleCancel = () => {
      cleanup();
      resolve(null);
    };

    document.getElementById('btn-datatype-confirm').addEventListener('click', handleConfirm);
    document.getElementById('btn-datatype-cancel').addEventListener('click', handleCancel);

    modal.classList.remove('hidden');
  });
}

// ══════════════════════════════════════════════════════════════════════
// JSON SELECTOR MODAL
// ══════════════════════════════════════════════════════════════════════
// Path building mirrors get_path() from JSONSelector.py exactly:
//
//   Python label types              → JS computed path
//   ────────────────────────────────────────────────────
//   root dict   "{} "               → ""
//   root array  "[] "               → ".[]"
//   dict key    "{} keyname"        → parentPath."keyname"
//   array node  "[] keyname"        → parentPath."keyname"[]
//   leaf under dict                 → parentPath."key"
//   leaf under array (scalar arr)   → parentPath_without_[]  + [value]
//   object under array              → inherits parentPath (the …[])
//   object under array → children   → parentPath."childkey"
//
// The parentPath is computed at tree-build time, stored on each row.
// ══════════════════════════════════════════════════════════════════════

let _jsonData = null;
let _jsonSelectedPaths = [];
let _jsonConfirmCallback = null;
// WeakMap: DOM row → jq path string
let _rowPathMap = new WeakMap();

// ── Open from a specific node value ───────────────────────────────────
function openJsonSelectorFromNode(nodeOrData, label, callback) {
  let data;
  if (typeof nodeOrData === 'string') {
    try { data = JSON.parse(nodeOrData); }
    catch(e) { toast('Cannot parse JSON: ' + e.message, 'error'); return; }
  } else {
    data = nodeOrData;
  }

  _jsonData = data;
  _jsonSelectedPaths = [];
  _jsonConfirmCallback = callback;
  _rowPathMap = new WeakMap();

  // Update source label in modal header
  const srcEl = document.getElementById('json-modal-source');
  if (srcEl) srcEl.textContent = label ? `Source: ${trunc(label, 50)}` : '';

  const pane = document.getElementById('json-tree-pane');
  pane.innerHTML = '';

  // Render root
  if (Array.isArray(data)) {
    // Root array: path = ".[]", each element is anonymous
    _buildJtArray(data, pane, '.[]');
  } else if (typeof data === 'object' && data !== null) {
    // Root object: path = ""
    _buildJtObject(data, pane, '');
  } else {
    pane.textContent = '(not an object or array)';
  }

  _updateJsonSelectedTags();
  document.getElementById('json-preview').textContent = '';
  openModal('json-modal');
}

// Legacy: open with arbitrary data (import modal path)
function openJsonSelectorModal(data, callback) {
  openJsonSelectorFromNode(data, null, callback);
}

// Open from AppState: prefer a specific selected JSON node
function openJsonSelectorFromGraph(appState, callback) {
  let target = null;

  // 1. Prefer the most recently selected node that has a JSON value
  const selIds = [...appState.selectedNodes];
  for (let i = selIds.length - 1; i >= 0; i--) {
    const n = appState.nodes.get(selIds[i]);
    if (n && looksLikeJson(n.value)) { target = n; break; }
  }

  // 2. Fall back: any json-typed node
  if (!target) {
    for (const [, n] of appState.nodes) {
      if (n.type === 'json' || looksLikeJson(n.value)) { target = n; break; }
    }
  }

  if (!target) {
    toast('Select a node with a JSON value first', 'warn');
    return;
  }

  openJsonSelectorFromNode(target.value, `[${target.type}] ${trunc(target.value, 40)}`, callback);
}

// ── Path helpers (mirroring Python get_path logic) ────────────────────
//
// _pathForDictKey(parentPath, key, valIsArray):
//   key inside an object/dict → .parentPath."key" or .parentPath."key"[]
//
function _pathForDictKey(parentPath, key, valIsArray) {
  const seg = parentPath === '' ? `."${key}"` : `${parentPath}."${key}"`;
  return valIsArray ? seg + '[]' : seg;
}

//
// _pathForArrayElement(arrayPath, item):
//   Python rule: if the element is a LEAF (scalar), strip the trailing []
//   from the array path and append [value].
//   If the element is an OBJECT, it inherits the full array path (the .key[]).
//   This exactly mirrors: if not node.children → parent[:-2] + f'[{clean_key}]'
//                          else                 → get_path(parent)   i.e. .key[]
//
function _pathForArrayElement(arrayPath, item) {
  const isLeaf = typeof item !== 'object' || item === null;
  if (isLeaf) {
    // strip trailing [] and append [value]
    const base = arrayPath.endsWith('[]') ? arrayPath.slice(0, -2) : arrayPath;
    return `${base}[${item}]`;
  }
  // object/array element: inherit parent array path
  return arrayPath;
}

// ── Build tree: array ─────────────────────────────────────────────────
function _buildJtArray(data, container, arrayPath) {
  const MAX = 200;
  data.slice(0, MAX).forEach((item, i) => {
    const itemPath = _pathForArrayElement(arrayPath, item);
    const row = _makeJtRow(`[${i}]`, item, true, itemPath);
    container.appendChild(row);

    if (typeof item === 'object' && item !== null) {
      const childDiv = document.createElement('div');
      childDiv.className = 'jt-node jt-children';
      if (Array.isArray(item)) {
        // Nested array element — e.g. .matrix[][]
        const innerPath = itemPath.endsWith('[]') ? itemPath : itemPath + '[]';
        _buildJtArray(item, childDiv, innerPath);
      } else {
        // Object element: children extend the inherited path
        _buildJtObject(item, childDiv, itemPath);
      }
      container.appendChild(childDiv);
      _attachToggle(row, childDiv);
    }
  });
  if (data.length > MAX) {
    const more = document.createElement('div');
    more.style.cssText = 'padding:3px 5px;color:var(--text3);font-size:11px;';
    more.textContent = `… ${data.length - MAX} more items not shown`;
    container.appendChild(more);
  }
}

// ── Build tree: object ────────────────────────────────────────────────
function _buildJtObject(data, container, parentPath) {
  Object.entries(data).forEach(([key, val]) => {
    const valIsArr = Array.isArray(val);
    const valIsObj = typeof val === 'object' && val !== null && !valIsArr;
    const nodePath = _pathForDictKey(parentPath, key, valIsArr);
    const row = _makeJtRow(key, val, false, nodePath);
    container.appendChild(row);

    if (valIsObj || valIsArr) {
      const childDiv = document.createElement('div');
      childDiv.className = 'jt-node jt-children';
      if (valIsArr) {
        _buildJtArray(val, childDiv, nodePath); // nodePath already ends with []
      } else {
        _buildJtObject(val, childDiv, nodePath);
      }
      container.appendChild(childDiv);
      _attachToggle(row, childDiv);
    }
  });
}

function _attachToggle(row, children) {
  const toggle = row.querySelector('.jt-toggle');
  toggle.textContent = '▾'; toggle.style.cursor = 'pointer';
  toggle.addEventListener('click', e => {
    e.stopPropagation();
    children.classList.toggle('collapsed');
    toggle.textContent = children.classList.contains('collapsed') ? '▸' : '▾';
  });
}

// ── Make a single tree row ────────────────────────────────────────────
function _makeJtRow(key, val, isIdx, jqPath) {
  const row = document.createElement('div'); row.className = 'jt-row';
  _rowPathMap.set(row, jqPath);

  const toggle = document.createElement('span'); toggle.className = 'jt-toggle'; toggle.textContent = ' ';
  const keyEl  = document.createElement('span');
  keyEl.className = isIdx ? 'jt-index' : 'jt-key';
  keyEl.textContent = isIdx ? key : `"${key}"`;

  const colon = document.createElement('span'); colon.className = 'jt-colon'; colon.textContent = ': ';

  const valEl = document.createElement('span');
  if      (val === null)             { valEl.className = 'jt-type-null'; valEl.textContent = 'null'; }
  else if (typeof val === 'boolean') { valEl.className = 'jt-type-bool'; valEl.textContent = String(val); }
  else if (typeof val === 'number')  { valEl.className = 'jt-type-num';  valEl.textContent = String(val); }
  else if (typeof val === 'string')  { valEl.className = 'jt-type-str';  valEl.textContent = `"${trunc(val, 80)}"`; }
  else if (Array.isArray(val))       { valEl.className = 'jt-type-arr';  valEl.textContent = `[ ${val.length} items ]`; }
  else                               { valEl.className = 'jt-type-obj';  valEl.textContent = `{ ${Object.keys(val).length} keys }`; }

  // Show jq path in tooltip and inline path hint
  const pathHint = document.createElement('span');
  pathHint.className = 'jt-path-hint';
  pathHint.textContent = jqPath || '.';

  row.title = `jq: ${jqPath || '.'}`;
  row.append(toggle, keyEl, colon, valEl, pathHint);
  row.addEventListener('click', e => {
    if (e.target === toggle) return;
    _toggleRow(jqPath, row);
  });
  return row;
}

// ── Toggle selection ──────────────────────────────────────────────────
function _toggleRow(path, clickedRow) {
  const idx = _jsonSelectedPaths.indexOf(path);
  if (idx === -1) {
    // Select: highlight all rows sharing this path (e.g. multiple array elements)
    _jsonSelectedPaths.push(path);
    document.querySelectorAll('.jt-row').forEach(r => {
      if (_rowPathMap.get(r) === path) r.classList.add('jt-selected');
    });
  } else {
    // Deselect
    _jsonSelectedPaths.splice(idx, 1);
    document.querySelectorAll('.jt-row').forEach(r => {
      if (_rowPathMap.get(r) === path) r.classList.remove('jt-selected');
    });
  }
  _updateJsonSelectedTags();
  _updateJsonPreview();
}

function _updateJsonSelectedTags() {
  const c = document.getElementById('json-selected-paths'); c.innerHTML = '';
  _jsonSelectedPaths.forEach(p => {
    const tag = document.createElement('span'); tag.className = 'json-path-tag';
    tag.textContent = p; tag.title = 'Click to remove';
    tag.addEventListener('click', () => {
      _jsonSelectedPaths = _jsonSelectedPaths.filter(x => x !== p);
      document.querySelectorAll('.jt-row.jt-selected').forEach(r => {
        if (_rowPathMap.get(r) === p) r.classList.remove('jt-selected');
      });
      _updateJsonSelectedTags(); _updateJsonPreview();
    });
    c.appendChild(tag);
  });
}

// ── Preview: evaluate jq path against data ────────────────────────────
// Tokenizer handles: ."key", "key"[], .[], .[N], .key
function _evalJqPath(data, path) {
  try {
    if (!path || path === '.') return data;
    let cur = [data];
    let rem = path;
    // Remove leading dot
    if (rem.startsWith('.')) rem = rem.slice(1);

    while (rem.length > 0) {
      const next = [];

      if (rem.startsWith('"')) {
        // Quoted key: "keyname" or "keyname"[]
        const close = rem.indexOf('"', 1);
        if (close < 0) break;
        const k = rem.slice(1, close);
        rem = rem.slice(close + 1);
        const iterate = rem.startsWith('[]');
        if (iterate) rem = rem.slice(2);
        if (rem.startsWith('.')) rem = rem.slice(1);
        cur.forEach(item => {
          const v = item?.[k];
          if (iterate) { if (Array.isArray(v)) v.forEach(el => next.push(el)); else if (v !== undefined) next.push(v); }
          else         { if (v !== undefined) next.push(v); }
        });

      } else if (rem.startsWith('[]')) {
        // Iterate current arrays
        rem = rem.slice(2);
        if (rem.startsWith('.')) rem = rem.slice(1);
        cur.forEach(item => { if (Array.isArray(item)) item.forEach(el => next.push(el)); else next.push(item); });

      } else if (rem.startsWith('[')) {
        // Subscript: [value] or [N]
        const close = rem.indexOf(']');
        if (close < 0) break;
        const subscript = rem.slice(1, close);
        rem = rem.slice(close + 1);
        if (rem.startsWith('.')) rem = rem.slice(1);
        const num = Number(subscript);
        cur.forEach(item => {
          if (Array.isArray(item)) {
            // Numeric index
            if (!isNaN(num)) next.push(item[num]);
            else {
              // String value → filter elements equal to subscript (Python flat array case)
              item.forEach(el => { if (String(el) === subscript) next.push(el); });
            }
          } else if (item !== null && item !== undefined) {
            const v = item[subscript] ?? item[num];
            if (v !== undefined) next.push(v);
          }
        });

      } else {
        // Unquoted key
        const m = rem.match(/^([^.["\]]+)/);
        if (!m) break;
        const k = m[1];
        rem = rem.slice(k.length);
        const iterate = rem.startsWith('[]');
        if (iterate) rem = rem.slice(2);
        if (rem.startsWith('.')) rem = rem.slice(1);
        cur.forEach(item => {
          const v = item?.[k];
          if (iterate) { if (Array.isArray(v)) v.forEach(el => next.push(el)); else if (v !== undefined) next.push(v); }
          else         { if (v !== undefined) next.push(v); }
        });
      }
      cur = next;
    }
    return cur.length === 1 ? cur[0] : cur;
  } catch { return undefined; }
}

function _updateJsonPreview() {
  const pre = document.getElementById('json-preview');
  if (!_jsonData || !_jsonSelectedPaths.length) { pre.textContent = ''; return; }
  try {
    const out = {};
    _jsonSelectedPaths.forEach(p => { out[p] = _evalJqPath(_jsonData, p); });
    pre.textContent = JSON.stringify(out, null, 2);
  } catch { pre.textContent = 'Preview error'; }
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-json-clear').addEventListener('click', () => {
    _jsonSelectedPaths = [];
    document.querySelectorAll('.jt-row.jt-selected').forEach(r => r.classList.remove('jt-selected'));
    _updateJsonSelectedTags(); _updateJsonPreview();
  });
  document.getElementById('btn-json-confirm').addEventListener('click', () => {
    closeModal('json-modal');
    if (_jsonConfirmCallback) _jsonConfirmCallback([..._jsonSelectedPaths]);
  });
});