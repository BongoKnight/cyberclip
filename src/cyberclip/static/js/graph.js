/* graph.js – vis.js Network graph management */

class GraphManager {
  constructor(appState) {
    this.state = appState;
    this.network = null;
    this.visNodes = null;
    this.visEdges = null;
    this._physicsOn = true;
    this._selBox = { active: false, startX: 0, startY: 0 };
    this._currentLayout = 'physics';
    this._currentShape = 'dot';
    this._init();
  }

  _visNodeFor(node, selected) {
    const c = typeColor(node.type);
    return {
      id: node.id,
      label: trunc(node.value, 24),
      title: `[${node.type}]\n${node.value}`,
      hidden: this.state.hiddenNodes.has(node.id),
      shape: this._currentShape,
      color: selected
        ? { background:'#1f6feb', border:'#58a6ff',
            highlight:{ background:'#388bfd', border:'#79c0ff' },
            hover:{ background:'#388bfd', border:'#79c0ff' } }
        : { background: c.background, border: c.border,
            highlight: c.highlight, hover: c.hover },
      borderWidth: selected ? 3 : 2,
      borderWidthSelected: 3,
      font: {
        color: '#c9d1d9',
        face: 'Atkinson Hyperlegible, sans-serif',
        size: 11,
        multi: false,
        align: 'center'
      },
      size: node.size || 22,  // Allow custom size per node, default 22
      labelHighlightBold: false,
    };
  }

  _init() {
    this.visNodes = new vis.DataSet();
    this.visEdges = new vis.DataSet();
    const container = document.getElementById('graph-canvas');
    const options = this._getNetworkOptions();
    this.network = new vis.Network(container, { nodes: this.visNodes, edges: this.visEdges }, options);
    this._bindNetworkEvents(container);
    this._bindControls();
  }

  _getNetworkOptions() {
    const options = {
      nodes:   {
        shape: this._currentShape,
        shadow: false,
        font: {
          size: 11,
          color: '#c9d1d9',
          face: 'Atkinson Hyperlegible, sans-serif',
          multi: false,
          align: 'center'
        },
        size: 22,  // Default size, can be overridden per node
        labelHighlightBold: false
      },
      edges:   {
        width: 1, arrows:{ to:{ enabled:true, scaleFactor:0.55 } },
        color:  { color:'#30363d', hover:'#58a6ff', highlight:'#58a6ff' },
        font:   { size: 10, color:'#8b949e', background:'#161b22' },
        smooth: { type:'continuous' },
      },
      physics: { enabled: this._physicsOn,
        barnesHut:{ gravitationalConstant:-5000, centralGravity:0.3, springLength:150 },
        stabilization:{ iterations:250, fit:true },
      },
      interaction: {
        multiselect: false, selectConnectedEdges: false,
        hover: true, tooltipDelay: 500, zoomView: true, dragView: true,
      },
    };

    // Apply layout configuration
    if (this._currentLayout === 'physics') {
      options.layout = { improvedLayout: true };
    } else if (this._currentLayout.startsWith('hierarchical-')) {
      const direction = this._currentLayout.split('-')[1];
      options.layout = {
        hierarchical: {
          enabled: true,
          direction: direction,
          sortMethod: 'directed',
          nodeSpacing: 150,
          levelSeparation: 150
        }
      };
      options.physics = { enabled: false };
    }

    return options;
  }

  // ── Full sync from state ───────────────────────────────────────────────
  sync() {
    const updates = [];
    const toRemove = [];
    const existing = new Set(this.visNodes.getIds().map(String));
    const current  = new Set();

    this.state.nodes.forEach((node, id) => {
      current.add(String(id));
      updates.push(this._visNodeFor(node, this.state.selectedNodes.has(id)));
    });
    existing.forEach(id => { if (!current.has(id)) toRemove.push(id); });
    if (toRemove.length) this.visNodes.remove(toRemove);
    this.visNodes.update(updates);

    // Edges
    const edgeUpdates = [];
    const edgeRemove  = [];
    const existingEdges = new Set(this.visEdges.getIds().map(String));
    const currentEdges  = new Set();
    this.state.edges.forEach((e, id) => {
      currentEdges.add(String(id));
      edgeUpdates.push({ id: e.id, from: e.from, to: e.to, label: e.label || '' });
    });
    existingEdges.forEach(id => { if (!currentEdges.has(id)) edgeRemove.push(id); });
    if (edgeRemove.length)  this.visEdges.remove(edgeRemove);
    this.visEdges.update(edgeUpdates);

    this._updateSelUI();
  }

  // ── Fast selection-only update ────────────────────────────────────────
  syncSelection() {
    const updates = [];
    this.state.nodes.forEach((node, id) => {
      updates.push(this._visNodeFor(node, this.state.selectedNodes.has(id)));
    });
    this.visNodes.update(updates);
    this._updateSelUI();
  }

  _updateSelUI() {
    const n = this.state.selectedNodes.size;
    document.getElementById('sel-count').textContent = n ? `${n} selected` : '';
    document.getElementById('btn-del-nodes').classList.toggle('hidden', n === 0);
    document.getElementById('btn-palette').disabled = false;
  }

  // ── Event bindings ────────────────────────────────────────────────────
  _bindNetworkEvents(container) {
    this.network.on('click', params => {
      const nodeId = this.network.getNodeAt(params.pointer.DOM);
      if (nodeId !== undefined) {
        if (params.event.ctrlKey || params.event.metaKey) {
          // Ctrl: toggle
          if (this.state.selectedNodes.has(nodeId)) this.state.selectedNodes.delete(nodeId);
          else this.state.selectedNodes.add(nodeId);
        } else {
          this.state.selectedNodes.clear();
          this.state.selectedNodes.add(nodeId);
          this._showNodeInfo(nodeId);
        }
      } else {
        if (!params.event.ctrlKey && !params.event.metaKey) {
          this.state.selectedNodes.clear();
          document.getElementById('node-info').classList.add('hidden');
        }
      }
      this.syncSelection();
    });

    this.network.on('doubleClick', params => {
      const nodeId = this.network.getNodeAt(params.pointer.DOM);
      if (nodeId !== undefined) {
        const n = this.state.nodes.get(nodeId);
        if (n) showFullText(`${n.type}: value`, n.value);
      }
    });

    this.network.on('oncontext', params => {
      params.event.preventDefault();
      const nodeId = this.network.getNodeAt(params.pointer.DOM);
      if (nodeId !== undefined) {
        if (!this.state.selectedNodes.has(nodeId)) {
          this.state.selectedNodes.clear();
          this.state.selectedNodes.add(nodeId);
          this.syncSelection();
        }
        this._showContextMenu(params.event.clientX, params.event.clientY, nodeId);
      }
    });

    this.network.on('stabilized', () => {
      if (this._physicsOn) {
        this.network.setOptions({ physics: { enabled: false } });
        this._physicsOn = false;
        document.getElementById('btn-physics').classList.remove('active');
      }
    });

    // ── Shift+drag box select ──────────────────────────────────────────
    const selBox   = document.getElementById('sel-box');
    const graphArea = document.getElementById('graph-area');

    graphArea.addEventListener('mousedown', e => {
      if (!e.shiftKey) return;
      e.preventDefault();
      const rect = graphArea.getBoundingClientRect();
      this._selBox = { active:true, startX: e.clientX-rect.left, startY: e.clientY-rect.top };
      selBox.classList.remove('hidden');
      selBox.style.cssText = `left:${this._selBox.startX}px;top:${this._selBox.startY}px;width:0;height:0;`;
    });

    document.addEventListener('mousemove', e => {
      if (!this._selBox.active) return;
      const rect = graphArea.getBoundingClientRect();
      const cx = e.clientX-rect.left, cy = e.clientY-rect.top;
      const x = Math.min(cx,this._selBox.startX), y = Math.min(cy,this._selBox.startY);
      selBox.style.left   = x + 'px'; selBox.style.top    = y + 'px';
      selBox.style.width  = Math.abs(cx-this._selBox.startX) + 'px';
      selBox.style.height = Math.abs(cy-this._selBox.startY) + 'px';
    });

    document.addEventListener('mouseup', e => {
      if (!this._selBox.active) return;
      this._selBox.active = false;
      selBox.classList.add('hidden');
      const rect = graphArea.getBoundingClientRect();
      const cx = e.clientX-rect.left, cy = e.clientY-rect.top;
      const x1=Math.min(cx,this._selBox.startX), y1=Math.min(cy,this._selBox.startY);
      const x2=Math.max(cx,this._selBox.startX), y2=Math.max(cy,this._selBox.startY);
      if (!e.ctrlKey && !e.metaKey) this.state.selectedNodes.clear();
      // Get all visible node positions
      const ids = [...this.state.nodes.keys()].filter(id => !this.state.hiddenNodes.has(id));
      const positions = this.network.getPositions(ids);
      ids.forEach(id => {
        const pos = positions[id];
        if (!pos) return;
        const dom = this.network.canvasToDOM(pos);
        if (dom.x >= x1 && dom.x <= x2 && dom.y >= y1 && dom.y <= y2) {
          this.state.selectedNodes.add(id);
        }
      });
      this.syncSelection();
    });

    // Ctrl+A: select all visible
    document.addEventListener('keydown', e => {
      const active = document.activeElement;
      const inInput = active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable);
      if ((e.ctrlKey || e.metaKey) && e.key === 'a' && !inInput) {
        e.preventDefault();
        this.state.selectedNodes.clear();
        this.state.nodes.forEach((_, id) => { if (!this.state.hiddenNodes.has(id)) this.state.selectedNodes.add(id); });
        this.syncSelection();
      }
      // Delete key: remove selected
      if (e.key === 'Delete' && !inInput && this.state.selectedNodes.size) {
        this._deleteSelected();
      }
    });
  }

  _bindControls() {
    document.getElementById('btn-fit').addEventListener('click', () =>
      this.network.fit({ animation:{ duration:400 } })
    );
    document.getElementById('btn-physics').addEventListener('click', () => {
      this._physicsOn = !this._physicsOn;
      this.network.setOptions({ physics:{ enabled: this._physicsOn } });
      document.getElementById('btn-physics').classList.toggle('active', this._physicsOn);
    });
    document.getElementById('btn-del-nodes').addEventListener('click', () => this._deleteSelected());
    document.getElementById('node-info-close').addEventListener('click', () =>
      document.getElementById('node-info').classList.add('hidden')
    );

    // Layout selector
    document.getElementById('graph-layout-select').addEventListener('change', e => {
      this._currentLayout = e.target.value;
      const options = this._getNetworkOptions();
      this.network.setOptions(options);
      // Update physics button state
      if (this._currentLayout.startsWith('hierarchical-')) {
        this._physicsOn = false;
        document.getElementById('btn-physics').classList.remove('active');
      }
      setTimeout(() => this.network.fit({ animation: { duration: 400 } }), 300);
    });

    // Shape selector
    document.getElementById('graph-shape-select').addEventListener('change', e => {
      this._currentShape = e.target.value;
      // Force re-render of all nodes with new shape
      this.sync();
    });
  }

  _deleteSelected() {
    if (!this.state.selectedNodes.size) return;
    if (!confirmDialog(`Delete ${this.state.selectedNodes.size} node(s)?`)) return;
    this.state.selectedNodes.forEach(id => {
      this.state.nodes.delete(id);
      const toRemove = [];
      this.state.edges.forEach((e, eid) => { if (e.from === id || e.to === id) toRemove.push(eid); });
      toRemove.forEach(eid => this.state.edges.delete(eid));
    });
    this.state.selectedNodes.clear();
    document.getElementById('node-info').classList.add('hidden');
    if (this.state.onDataChanged) this.state.onDataChanged();
  }

  // ── Node info panel ───────────────────────────────────────────────────
  _showNodeInfo(nodeId) {
    const node = this.state.nodes.get(nodeId);
    if (!node) return;
    const panel = document.getElementById('node-info');
    const body  = document.getElementById('node-info-body');
    document.getElementById('node-info-title').textContent = trunc(node.value, 26);
    panel.classList.remove('hidden');

    const c = typeColor(node.type);
    body.innerHTML = '';

    // Badge
    const badge = document.createElement('span'); badge.className = 'node-badge';
    badge.textContent = node.type;
    badge.style.cssText = `background:${c.raw}22;border:1px solid ${c.raw};color:${c.raw}`;
    body.appendChild(badge);

    // Value box
    const vbox = document.createElement('div'); vbox.className = 'node-value-box';
    const vtxt = document.createElement('span'); vtxt.className = 'node-value'; vtxt.textContent = node.value;
    const vacts = document.createElement('div'); vacts.className = 'node-value-actions';
    const cpyBtn = document.createElement('button'); cpyBtn.className = 'btn-icon'; cpyBtn.title = 'Copy';
    cpyBtn.textContent = '📋'; cpyBtn.addEventListener('click', () => copyText(node.value));
    const fullBtn = document.createElement('button'); fullBtn.className = 'btn-icon'; fullBtn.title = 'Show full';
    fullBtn.textContent = '⬜'; fullBtn.addEventListener('click', () => showFullText(node.type, node.value));
    vacts.append(cpyBtn, fullBtn); vbox.append(vtxt, vacts); body.appendChild(vbox);

    // Metadata table
    const meta = node.metadata || {};
    const metaKeys = Object.keys(meta);
    if (metaKeys.length) {
      const title = document.createElement('div'); title.className = 'meta-section-title'; title.textContent = 'Metadata';
      body.appendChild(title);
      const tbl = document.createElement('table'); tbl.className = 'meta-table';
      metaKeys.forEach(k => {
        const tr = document.createElement('tr');
        const td1 = document.createElement('td'); td1.textContent = k; td1.title = k;
        const td2 = document.createElement('td');
        const mv = document.createElement('span'); mv.className = 'meta-value';
        mv.title = 'Click to copy · Double-click for full text';
        mv.textContent = trunc(String(meta[k]), 55);
        mv.addEventListener('click', () => copyText(String(meta[k])));
        mv.addEventListener('dblclick', () => showFullText(k, String(meta[k])));
        td2.appendChild(mv); tr.append(td1, td2); tbl.appendChild(tr);
      });
      body.appendChild(tbl);
    }

    const actRow = document.createElement('div'); actRow.className = 'node-actions-row';
    const runBtn = this._mkBtn('⚡ Action → meta', 'btn btn-sm', () => {
      this.state.selectedNodes.clear();
      this.state.selectedNodes.add(nodeId);
      this.state.actionManager.openPalette();
    });
    const newNodesBtn = this._mkBtn('＋ → new nodes', 'btn btn-sm btn-success', () => this._doCreateNodes(nodeId));
    const fromMetaBtn = this._mkBtn('🌿 From metadata', 'btn btn-sm', () => this._doFromMeta(nodeId));
    actRow.append(runBtn, newNodesBtn, fromMetaBtn);

    // JSON selector button — only visible when node value is JSON
    if (looksLikeJson(node.value)) {
      const jsonSelBtn = this._mkBtn('🌲 JSON Selector', 'btn btn-sm', () => {
        // Use parseAndAdd so dedup, edges, and addMode are handled correctly
        openJsonSelectorFromNode(node.value, `[${node.type}] ${trunc(node.value,40)}`, async paths => {
          if (!paths.length) return;
          let data2;
          try { data2 = JSON.parse(node.value); } catch { toast('Invalid JSON', 'error'); return; }
          let created = 0;
          for (const path of paths) {
            const val = _evalJqPath(data2, path);
            const flat = Array.isArray(val) ? val : [val];
            for (const v of flat.filter(x => x !== null && x !== undefined)) {
              const typeName = path.replace(/\."|"|\.\[\]/g,'').replace(/[^a-zA-Z0-9_]/g,'_').replace(/^_+|_+$/g,'') || 'json_extract';
              const freshId = uuid();
              // Dedup check
              let dup = false;
              for (const ex of this.state.nodes.values()) {
                if (ex.type === typeName && ex.value === String(v)) { dup = true; if (this.state.addEdge) this.state.addEdge(nodeId, ex.id, path); break; }
              }
              if (!dup) {
                this.state.nodes.set(freshId, { id: freshId, label: trunc(String(v),40), value: String(v), type: typeName, metadata: {} });
                if (this.state.addEdge) this.state.addEdge(nodeId, freshId, path);
                created++;
              }
            }
          }
          if (this.state.onDataChanged) this.state.onDataChanged();
          toast(`Created ${created} node(s) from JSON`, 'success');
        });
      });
      actRow.appendChild(jsonSelBtn);
    }

    body.appendChild(actRow);
  }

  _mkBtn(label, cls, fn) {
    const b = document.createElement('button'); b.className = cls; b.textContent = label;
    b.addEventListener('click', fn); return b;
  }

  async _doCreateNodes(nodeId) {
    const action = await this.state.actionManager.pickAction();
    if (!action) return;
    await this.state.actionManager.runAndCreateNodes([nodeId], action);
  }

  async _doFromMeta(nodeId) {
    const node = this.state.nodes.get(nodeId);
    const pick = await showMetaPickModal(node);
    if (!pick) return;

    // First, parse to see what types are detected
    showSpinner('Detecting data types…');
    try {
      const res = await apiPost('/api/parse', { text: pick.value });
      hideSpinner();

      const detectedTypes = res.types || [];
      if (!detectedTypes.length) {
        toast('No parseable data types found in this metadata', 'warn');
        return;
      }

      // Show datatype selection modal
      const selection = await showDatatypeModal(detectedTypes);
      if (!selection) return;

      // Parse and add nodes, then filter by selected types
      showSpinner('Creating nodes…');
      const allNewIds = await this.state.parseAndAdd(pick.value, true, nodeId, pick.key);

      // Filter out nodes that don't match selected types
      const selectedTypeSet = new Set(selection.types);
      const keptIds = [];
      allNewIds.forEach(id => {
        const n = this.state.nodes.get(id);
        if (n && selectedTypeSet.has(n.type)) {
          keptIds.push(id);
        } else {
          // Remove unwanted node
          this.state.nodes.delete(id);
          // Remove edges to/from this node
          this.state.edges.forEach((e, eid) => {
            if (e.from === id || e.to === id) this.state.edges.delete(eid);
          });
        }
      });

      if (keptIds.length) {
        toast(`Created ${keptIds.length} node(s) from metadata`, 'success', 2000);
      } else {
        toast('No nodes created with selected types', 'info');
      }

      // Delete the originating node if requested
      if (selection.deleteOriginal) {
        this.state.nodes.delete(nodeId);
        this.state.selectedNodes.delete(nodeId);
        this.state.edges.forEach((e, eid) => {
          if (e.from === nodeId || e.to === nodeId) this.state.edges.delete(eid);
        });
        document.getElementById('node-info').classList.add('hidden');
      }

      if (this.state.onDataChanged) this.state.onDataChanged();
    } catch(e) {
      toast('Error: ' + e.message, 'error');
    } finally {
      hideSpinner();
    }
  }

  // ── Context menu ──────────────────────────────────────────────────────
  _showContextMenu(x, y, nodeId) {
    const menu = document.getElementById('ctx-menu');
    menu.innerHTML = '';
    menu.classList.remove('hidden');
    menu.style.left = x + 'px'; menu.style.top = y + 'px';
    // Adjust if off-screen
    requestAnimationFrame(() => {
      const r = menu.getBoundingClientRect();
      if (r.right > window.innerWidth)  menu.style.left = (x - r.width)  + 'px';
      if (r.bottom > window.innerHeight) menu.style.top = (y - r.height) + 'px';
    });

    const node = this.state.nodes.get(nodeId);
    const selCount = this.state.selectedNodes.size;

    const isJson = looksLikeJson(node.value);
    const items = [
      { icon:'📋', label: 'Copy value',       fn: () => copyText(node.value) },
      { icon:'⬜', label: 'Show full text',    fn: () => showFullText(node.type, node.value) },
      ...(isJson ? [{
        icon:'🌲', label: 'JSON Selector → new nodes',
        fn: () => this._doJsonSelector(nodeId),
      }] : []),
      { sep: true },
      { icon:'⚡', label: `Action → metadata${selCount>1?' ('+selCount+' nodes)':''}`,
        fn: () => this.state.actionManager.openPalette() },
      { icon:'＋', label: 'Action → new nodes',
        fn: () => this._doCreateNodes(nodeId) },
      { icon:'🌿', label: 'Create node from metadata',
        fn: () => this._doFromMeta(nodeId) },
      { sep: true },
      { icon:'✕', label: `Delete node${selCount>1?' ('+selCount+')':''}`,
        cls: 'danger', fn: () => this._deleteSelected() },
    ];

    items.forEach(it => {
      const li = document.createElement('li');
      if (it.sep) { li.className = 'sep'; }
      else {
        if (it.cls) li.classList.add(it.cls);
        const icon = document.createElement('span'); icon.textContent = it.icon || '';
        const lbl  = document.createElement('span'); lbl.textContent = it.label;
        li.append(icon, lbl);
        li.addEventListener('click', () => { menu.classList.add('hidden'); it.fn(); });
      }
      menu.appendChild(li);
    });

    const close = e => { if (!menu.contains(e.target)) { menu.classList.add('hidden'); document.removeEventListener('click', close); }};
    setTimeout(() => document.addEventListener('click', close), 10);
  }

  fitGraph() { this.network.fit({ animation:{ duration:500 } }); }
}

// ── Monkey-patch: add _doJsonSelector to GraphManager prototype ───────
GraphManager.prototype._doJsonSelector = function(nodeId) {
  const node = this.state.nodes.get(nodeId);
  if (!node || !looksLikeJson(node.value)) return;

  openJsonSelectorFromNode(
    node.value,
    `[${node.type}] ${trunc(node.value, 40)}`,
    (paths) => {
      if (!paths.length) return;
      let data;
      try { data = JSON.parse(node.value); } catch { toast('Invalid JSON', 'error'); return; }

      let created = 0;
      paths.forEach(path => {
        const val = _evalJqPath(data, path);
        const flat = Array.isArray(val) ? val : [val];
        flat.filter(v => v !== null && v !== undefined).forEach(v => {
          const freshId = uuid();
          // Derive a clean type name from the jq path
          const typeName = path.replace(/\.\"|\"|\[\]/g, '').replace(/[^a-zA-Z0-9_]/g, '_').replace(/^_+|_+$/g, '') || 'json_extract';
          this.state.nodes.set(freshId, {
            id: freshId, label: trunc(String(v), 40),
            value: String(v), type: typeName, metadata: {}
          });
          if (this.state.addEdge) this.state.addEdge(nodeId, freshId, path);
          created++;
        });
      });
      this.state.onDataChanged();
      toast(`Created ${created} node(s) from JSON paths`, 'success');
    }
  );
};

// ── Monkey-patch: add JSON selector button to _showNodeInfo ───────────
const _origShowNodeInfo = GraphManager.prototype._showNodeInfo;
GraphManager.prototype._showNodeInfo = function(nodeId) {
  _origShowNodeInfo.call(this, nodeId);

  const node = this.state.nodes.get(nodeId);
  if (!node || !looksLikeJson(node.value)) return;

  // Append JSON selector button to the action row already rendered
  const actRow = document.querySelector('#node-info-body .node-actions-row');
  if (!actRow) return;

  const jsonBtn = this._mkBtn('🌲 JSON paths', 'btn btn-sm', () => this._doJsonSelector(nodeId));
  jsonBtn.title = 'Open JSON field selector for this node';
  actRow.appendChild(jsonBtn);
};

// Helper: evaluate a jq path string against data (used in _doJsonSelector)
function _evalJqPath(data, path) {
  try {
    if (!path || path === '.') return data;
    let cur = [data];
    let rem = path.startsWith('.') ? path.slice(1) : path;

    while (rem.length > 0) {
      const next = [];
      if (rem.startsWith('"')) {
        const close = rem.indexOf('"', 1); if (close < 0) break;
        const k = rem.slice(1, close); rem = rem.slice(close + 1);
        const iterate = rem.startsWith('[]'); if (iterate) rem = rem.slice(2);
        if (rem.startsWith('.')) rem = rem.slice(1);
        cur.forEach(item => {
          const v = item?.[k];
          if (iterate) { if (Array.isArray(v)) v.forEach(el => next.push(el)); else if (v !== undefined) next.push(v); }
          else { if (v !== undefined) next.push(v); }
        });
      } else if (rem.startsWith('[]')) {
        rem = rem.slice(2); if (rem.startsWith('.')) rem = rem.slice(1);
        cur.forEach(item => { if (Array.isArray(item)) item.forEach(el => next.push(el)); else next.push(item); });
      } else if (rem.startsWith('[')) {
        const close = rem.indexOf(']'); if (close < 0) break;
        const sub = rem.slice(1, close); rem = rem.slice(close + 1);
        if (rem.startsWith('.')) rem = rem.slice(1);
        const num = Number(sub);
        cur.forEach(item => {
          if (Array.isArray(item)) {
            if (!isNaN(num)) next.push(item[num]);
            else item.forEach(el => { if (String(el) === sub) next.push(el); });
          } else if (item?.[sub] !== undefined) next.push(item[sub]);
        });
      } else {
        const m = rem.match(/^([^.["]+)/); if (!m) break;
        const k = m[1]; rem = rem.slice(k.length);
        const iterate = rem.startsWith('[]'); if (iterate) rem = rem.slice(2);
        if (rem.startsWith('.')) rem = rem.slice(1);
        cur.forEach(item => {
          const v = item?.[k];
          if (iterate) { if (Array.isArray(v)) v.forEach(el => next.push(el)); else if (v !== undefined) next.push(v); }
          else { if (v !== undefined) next.push(v); }
        });
      }
      cur = next;
    }
    return cur.length === 1 ? cur[0] : cur;
  } catch { return undefined; }
}