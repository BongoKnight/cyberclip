/* actions.js – action execution & command palette */

class ActionManager {
  constructor(appState) {
    this.state = appState;
    this.allActions = [];
    this._paletteOpen = false;
    this._paletteIdx = 0;
    this._filtered = [];
    this._mode = 'free';
    this._bulkColumn = null;
    this._pickMode = false;
    this._resolvePickAction = null;
    this._bindPalette();
  }

  async loadActions() {
    try { this.allActions = await apiGet('/api/actions'); }
    catch(e) { toast('Failed to load actions: ' + e.message, 'error'); }
  }

  // ── Command palette ───────────────────────────────────────────────────
  _bindPalette() {
    document.getElementById('btn-palette').addEventListener('click', () => this.openPalette());
    const overlay = document.getElementById('palette-overlay');
    overlay.addEventListener('click', e => { if (e.target === overlay) this.closePalette(false); });
    const inp = document.getElementById('palette-input');
    inp.addEventListener('input', () => this._filterPalette(inp.value));
    inp.addEventListener('keydown', e => {
      if (e.key === 'Escape')    { this.closePalette(false); return; }
      if (e.key === 'ArrowDown') { e.preventDefault(); this._moveIdx(1); }
      if (e.key === 'ArrowUp')   { e.preventDefault(); this._moveIdx(-1); }
      if (e.key === 'Enter')     { e.preventDefault(); this._selectCurrent(); }
    });
  }

  openPalette(bulkColumn = null, pickMode = false) {
    this._pickMode = pickMode;
    this._mode = bulkColumn ? 'column' : (this.state.selectedNodes.size ? 'selection' : 'free');
    this._bulkColumn = bulkColumn;
    this._paletteOpen = true;
    document.getElementById('palette-overlay').classList.remove('hidden');
    const inp = document.getElementById('palette-input');
    inp.value = ''; inp.focus();
    const ctx = document.getElementById('palette-context');
    if (bulkColumn) {
      ctx.textContent = `Column: ${bulkColumn === '__value__' ? 'Value' : bulkColumn}`;
      ctx.className = 'palette-context';
    } else {
      const n = this.state.selectedNodes.size;
      ctx.textContent = n ? `${n} node${n > 1 ? 's' : ''} selected` : 'Free text mode';
      ctx.className = n ? 'palette-context' : 'palette-context palette-empty-ctx';
    }
    this._filterPalette('');
  }

  closePalette(resolved = true) {
    this._paletteOpen = false;
    document.getElementById('palette-overlay').classList.add('hidden');
    if (this._pickMode && !resolved && this._resolvePickAction) {
      this._resolvePickAction(null); this._resolvePickAction = null;
    }
  }

  pickAction() {
    return new Promise(resolve => {
      this._resolvePickAction = resolve;
      this.openPalette(null, true);
    });
  }

  _filterPalette(query) {
    const q = query.toLowerCase().trim();
    this._filtered = q ? this.allActions.filter(a => (a.description || a.name).toLowerCase().includes(q)) : [...this.allActions];
    this._paletteIdx = 0;
    this._renderPaletteList();
  }

  _renderPaletteList() {
    const list = document.getElementById('palette-list');
    list.innerHTML = '';
    if (!this._filtered.length) { list.innerHTML = '<div class="palette-empty">No matching actions</div>'; return; }
    this._filtered.forEach((a, i) => {
      const item = document.createElement('div');
      item.className = 'palette-item' + (i === this._paletteIdx ? ' active' : '');
      const name = document.createElement('span'); name.className = 'palette-item-name'; name.textContent = a.description || a.name;
      const types = document.createElement('div'); types.className = 'palette-item-types';
      (a.supportedType || []).slice(0, 4).forEach(t => {
        const b = document.createElement('span'); b.className = 'palette-item-badge'; b.textContent = t; types.appendChild(b);
      });
      item.append(name, types);
      if (a.indicators) { const ind = document.createElement('span'); ind.className = 'palette-item-indicator'; ind.textContent = a.indicators; item.appendChild(ind); }
      item.addEventListener('click', () => { this._paletteIdx = i; this._selectCurrent(); });
      list.appendChild(item);
    });
  }

  _moveIdx(delta) {
    this._paletteIdx = Math.max(0, Math.min(this._filtered.length - 1, this._paletteIdx + delta));
    this._renderPaletteList();
    document.querySelector('.palette-item.active')?.scrollIntoView({ block: 'nearest' });
  }

  async _selectCurrent() {
    if (!this._filtered.length) return;
    const action = this._filtered[this._paletteIdx];
    if (this._pickMode && this._resolvePickAction) {
      this.closePalette(true); this._resolvePickAction(action); this._resolvePickAction = null; return;
    }
    this.closePalette(true);

    let params = {};
    if (action.complex_param && Object.keys(action.complex_param).length) {
      // Pass the JSON of a selected node (if any) so JSON-path params can use the selector
      const jsonNodeValue = this._findJsonNodeValue();
      const result = await showParamsModal(action, jsonNodeValue);
      if (result === null) return;
      params = result;
    }

    if (this._mode === 'column' && this._bulkColumn) await this._executeBulkColumn(action, params, this._bulkColumn);
    else if (this._mode === 'selection' && this.state.selectedNodes.size) await this._executeOnSelected(action, params);
    else await this._executeFreeText(action, params);
  }

  // Find first JSON value among selected nodes (for params modal)
  _findJsonNodeValue() {
    for (const id of this.state.selectedNodes) {
      const n = this.state.nodes.get(id);
      if (n && looksLikeJson(n.value)) return n.value;
    }
    return null;
  }

  // ── Execute on selected → add metadata ───────────────────────────────
  async _executeOnSelected(action, params) {
    const nodeIds = [...this.state.selectedNodes];
    showSpinner(`Running "${action.description}"…`);
    try {
      // Run sequentially to avoid race conditions with shared parser state
      const results = [];
      let errors = 0;
      for (const id of nodeIds) {
        const node = this.state.nodes.get(id);
        try {
          const res = await apiPost('/api/execute', { text: node.value, action: action.name, complex_param: params });
          results.push(res);
          _applyMetadata(node, action.name, res.result ?? '');
        } catch (e) {
          results.push({ error: e.message, result: '' });
          errors++;
        }
      }
      if (errors) toast(`${errors} error(s) during execution`, 'warn');
      else toast(`"${action.description}" applied to ${nodeIds.length} node(s)`, 'success');
      if (this.state.onDataChanged) this.state.onDataChanged();
    } finally { hideSpinner(); }
  }

  // ── Execute on column ─────────────────────────────────────────────────
  // FIX: use table manager's sorted/ordered node list, not nodes.keys()
  async _executeBulkColumn(action, params, columnName) {
    // Use the SAME order as the table currently shows (respects sort)
    const nodeIds = this.state.tableManager
      ? this.state.tableManager.getVisibleNodeIds()
      : [...this.state.nodes.keys()].filter(id => !this.state.hiddenNodes.has(id));

    const values = nodeIds.map(id => {
      const n = this.state.nodes.get(id);
      return columnName === '__value__' ? n.value : String((n.metadata || {})[columnName] ?? '');
    });

    showSpinner(`Running "${action.description}" on column…`);
    try {
      const res = await apiPost('/api/execute_bulk', { values, action: action.name, complex_param: params });
      if (res.error) { toast('Error: ' + res.error, 'error'); return; }
      const { results, num_columns } = res;

      // FIX: iterate nodeIds (same order as values sent to server) not nodes.keys()
      nodeIds.forEach((id, rowIdx) => {
        const node = this.state.nodes.get(id);
        if (!node) return;
        const rowVals = results[rowIdx] || [''];
        rowVals.forEach((val, colIdx) => {
          // Merge: same key → update value (no duplicate columns)
          node.metadata[colIdx === 0 ? action.name : `${action.name}_${colIdx + 1}`] = val;
        });
      });
      toast(`Column action "${action.description}" done (${num_columns} col${num_columns > 1 ? 's' : ''})`, 'success');
      if (this.state.onDataChanged) this.state.onDataChanged();
    } catch(e) { toast('Error: ' + e.message, 'error'); }
    finally { hideSpinner(); }
  }

  // ── Free-text execute ─────────────────────────────────────────────────
  async _executeFreeText(action, params) {
    const text = await _promptText(`Text for: ${action.description}`);
    showSpinner('Running…');
    try {
      const res = await apiPost('/api/execute', { text, action: action.name, complex_param: params });
      showFullText(`Result: ${action.description}`, res.result || '(empty)');
    } catch(e) { toast('Error: ' + e.message, 'error'); }
    finally { hideSpinner(); }
  }

  // ── Run on single node → metadata ─────────────────────────────────────
  async runOnNode(nodeId, action, params = {}) {
    const node = this.state.nodes.get(nodeId);
    if (!node) return;
    if (action.complex_param && Object.keys(action.complex_param).length && !Object.keys(params).length) {
      const jsonVal = looksLikeJson(node.value) ? node.value : null;
      const result = await showParamsModal(action, jsonVal);
      if (result === null) return;
      params = result;
    }
    showSpinner(`Running "${action.description}"…`);
    try {
      const res = await apiPost('/api/execute', { text: node.value, action: action.name, complex_param: params });
      _applyMetadata(node, action.name, res.result || '');
      toast(`Done: "${action.description}"`, 'success');
      if (this.state.onDataChanged) this.state.onDataChanged();
    } catch(e) { toast('Error: ' + e.message, 'error'); }
    finally { hideSpinner(); }
  }

  // ── Run action → create new nodes + edges ─────────────────────────────
  async runAndCreateNodes(nodeIds, action, params = {}) {
    if (action.complex_param && Object.keys(action.complex_param).length && !Object.keys(params).length) {
      const jsonVal = nodeIds.length ? (() => { const n = this.state.nodes.get(nodeIds[0]); return n && looksLikeJson(n.value) ? n.value : null; })() : null;
      const result = await showParamsModal(action, jsonVal);
      if (result === null) return;
      params = result;
    }
    showSpinner('Creating nodes…');
    let created = 0;
    try {
      for (const id of nodeIds) {
        const node = this.state.nodes.get(id);
        const res = await apiPost('/api/execute', { text: node.value, action: action.name, complex_param: params }).catch(() => null);
        if (!res?.result) continue;
        const before = this.state.nodes.size;
        // Pass sourceNodeId and action name so edges are created with proper labels
        await this.state.parseAndAdd(res.result, true, id, action.name);
        created += this.state.nodes.size - before;
      }
      toast(`Created ${created} new node(s)`, 'success');
    } finally { hideSpinner(); }
  }
}

// ── Apply metadata (split TSV → multiple columns) ──────────────────────────
function _applyMetadata(node, actionName, raw) {
  if (!node.metadata) node.metadata = {};
  const parts = raw.split('\t');
  parts.forEach((v, i) => {
    node.metadata[i === 0 ? actionName : `${actionName}_${i + 1}`] = v;
  });
}

// ── Inline text prompt modal ──────────────────────────────────────────────
function _promptText(title) {
  return new Promise(resolve => {
    let modal = document.getElementById('_prompt-modal');
    if (!modal) {
      modal = document.createElement('div'); modal.id = '_prompt-modal'; modal.className = 'modal-overlay hidden';
      modal.innerHTML = `
        <div class="modal">
          <div class="modal-header"><span id="_prompt-title">Input</span><button class="modal-close btn-icon">✕</button></div>
          <div class="modal-body"><textarea id="_prompt-input" class="param-textarea" rows="5" placeholder="Enter text…"></textarea></div>
          <div class="modal-footer">
            <button id="_prompt-cancel" class="btn">Cancel</button>
            <button id="_prompt-ok" class="btn btn-primary">OK</button>
          </div>
        </div>`;
      document.body.appendChild(modal);
      modal.querySelector('.modal-close').addEventListener('click', () => { modal.classList.add('hidden'); resolve(null); });
      modal.addEventListener('click', e => { if (e.target === modal) { modal.classList.add('hidden'); resolve(null); } });
    }
    document.getElementById('_prompt-title').textContent = title;
    const inp = document.getElementById('_prompt-input'); inp.value = '';
    modal.classList.remove('hidden'); inp.focus();
    const ok = document.getElementById('_prompt-ok').cloneNode(true);
    const cancel = document.getElementById('_prompt-cancel').cloneNode(true);
    document.getElementById('_prompt-ok').replaceWith(ok);
    document.getElementById('_prompt-cancel').replaceWith(cancel);
    ok.addEventListener('click', () => { modal.classList.add('hidden'); resolve(inp.value || ''); });
    cancel.addEventListener('click', () => { modal.classList.add('hidden'); resolve(null); });
  });
}
