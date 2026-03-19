/* app.js – main application controller */

const AppState = {
  nodes:         new Map(),   // frontendId → node
  edges:         new Map(),   // edgeId → {id, from, to, label}
  selectedNodes: new Set(),
  hiddenNodes:   new Set(),
  onDataChanged:     null,
  onFilterChange:    null,
  onSelectionChange: null,
  actionManager: null, graphManager: null, tableManager: null, filterManager: null,
  parseAndAdd: null,
  addEdge: null,
};

document.addEventListener('DOMContentLoaded', () => {
  const filterMgr = new FilterManager(AppState);
  const actionMgr = new ActionManager(AppState);
  const graphMgr  = new GraphManager(AppState);
  const tableMgr  = new TableManager(AppState);

  filterMgr.init();   // bind UI events now that DOM is ready
  AppState.actionManager = actionMgr;
  AppState.graphManager  = graphMgr;
  AppState.tableManager  = tableMgr;
  AppState.filterManager = filterMgr;

  // ── Callbacks ──────────────────────────────────────────────────────────
  AppState.onDataChanged = () => {
    filterMgr.onNodesChanged();
    graphMgr.sync();
    tableMgr.render();
  };
  AppState.onFilterChange = () => { graphMgr.sync(); tableMgr.syncHiddenRows(); };
  AppState.onSelectionChange = () => { graphMgr.syncSelection(); tableMgr.syncSelectionHighlight(); };

  // ── Helper: add an edge (deduped) ─────────────────────────────────────
  AppState.addEdge = (fromId, toId, label = '') => {
    // Dedup: skip if same from→to already exists
    for (const e of AppState.edges.values()) {
      if (e.from === fromId && e.to === toId) return;
    }
    const eid = uuid();
    AppState.edges.set(eid, { id: eid, from: fromId, to: toId, label });
  };

  // ── Parse text → add nodes/edges ──────────────────────────────────────
  // FIX: always generate fresh UUID on frontend; never use server-provided ids
  // (server resets nid=0 each call, causing Map key collisions in add mode)
  AppState.parseAndAdd = async (text, addMode = false, sourceNodeId = null, edgeLabel = null) => {
    if (!text?.trim()) return [];
    showSpinner('Parsing…');
    try {
      const res = await apiPost('/api/parse', { text });
      if (!addMode) {
        AppState.nodes.clear(); AppState.edges.clear(); AppState.selectedNodes.clear();
      }
      const newIds = [];
      (res.nodes || []).forEach(n => {
        // Dedup by type+value
        for (const ex of AppState.nodes.values()) {
          if (ex.type === n.type && ex.value === n.value) {
            // Already exists: still create edge to it if needed
            if (sourceNodeId) AppState.addEdge(sourceNodeId, ex.id, edgeLabel || n.type);
            return;
          }
        }
        // Always assign a fresh UUID – prevents server-id collisions
        const freshId = uuid();
        AppState.nodes.set(freshId, { ...n, id: freshId, metadata: n.metadata || {} });
        if (sourceNodeId) AppState.addEdge(sourceNodeId, freshId, edgeLabel || n.type);
        newIds.push(freshId);
      });
      // Edges from server (only used in non-add mode root parse)
      if (!addMode && !sourceNodeId) {
        (res.edges || []).forEach(e => {
          const eid = uuid();
          AppState.edges.set(eid, { id: eid, from: e.from, to: e.to, label: e.label || '' });
        });
      }
      AppState.onDataChanged();
      // Only auto-fit on fresh graph load, not on incremental additions
      if (!addMode) setTimeout(() => graphMgr.fitGraph(), 350);
      return newIds;
    } catch(e) {
      toast('Parse error: ' + e.message, 'error');
      return [];
    } finally { hideSpinner(); }
  };

  // Parse with datatype selection modal
  AppState.parseAndAddWithTypeSelection = async (text, addMode = false, sourceNodeId = null, edgeLabel = null, deleteOriginal = false) => {
    if (!text?.trim()) return [];

    // First detect types
    showSpinner('Detecting data types…');
    try {
      const res = await apiPost('/api/parse', { text });
      hideSpinner();

      const detectedTypes = res.types || [];
      if (!detectedTypes.length) {
        toast('No parseable data types found', 'warn');
        return [];
      }

      // Show datatype selection modal
      const selection = await showDatatypeModal(detectedTypes);
      if (!selection) return [];

      // Parse and add nodes
      showSpinner('Creating nodes…');
      const allNewIds = await AppState.parseAndAdd(text, addMode, sourceNodeId, edgeLabel);

      // Filter by selected types
      const selectedTypeSet = new Set(selection.types);
      const keptIds = [];
      allNewIds.forEach(id => {
        const n = AppState.nodes.get(id);
        if (n && selectedTypeSet.has(n.type)) {
          keptIds.push(id);
        } else {
          // Remove unwanted node
          AppState.nodes.delete(id);
          // Remove edges to/from this node
          AppState.edges.forEach((e, eid) => {
            if (e.from === id || e.to === id) AppState.edges.delete(eid);
          });
        }
      });

      if (keptIds.length) {
        toast(`Created ${keptIds.length} node(s)`, 'success', 2000);
      } else {
        toast('No nodes created with selected types', 'info');
      }

      // Delete original node if requested
      if (deleteOriginal && sourceNodeId) {
        AppState.nodes.delete(sourceNodeId);
        AppState.selectedNodes.delete(sourceNodeId);
        AppState.edges.forEach((e, eid) => {
          if (e.from === sourceNodeId || e.to === sourceNodeId) AppState.edges.delete(eid);
        });
      }

      AppState.onDataChanged();
      return keptIds;
    } catch(e) {
      toast('Error: ' + e.message, 'error');
      return [];
    } finally {
      hideSpinner();
    }
  };

  // Bulk parse multiple values (for column operations)
  AppState.parseBulk = async (values, sourceNodeIds, edgeLabel) => {
    if (!values || !values.length) return 0;

    showSpinner(`Parsing ${values.length} values…`);
    try {
      const res = await apiPost('/api/parse_bulk', { values });

      if (res.error) {
        toast('Error: ' + res.error, 'error');
        return 0;
      }

      let created = 0;
      res.results.forEach((result, idx) => {
        const sourceId = sourceNodeIds ? sourceNodeIds[idx] : null;
        (result.nodes || []).forEach(n => {
          // Dedup by type+value
          let exists = false;
          for (const ex of AppState.nodes.values()) {
            if (ex.type === n.type && ex.value === n.value) {
              // Already exists: create edge to it if needed
              if (sourceId && AppState.addEdge) AppState.addEdge(sourceId, ex.id, edgeLabel || n.type);
              exists = true;
              break;
            }
          }
          if (!exists) {
            // Create new node
            const freshId = uuid();
            AppState.nodes.set(freshId, { ...n, id: freshId, metadata: n.metadata || {} });
            if (sourceId && AppState.addEdge) AppState.addEdge(sourceId, freshId, edgeLabel || n.type);
            created++;
          }
        });
      });

      AppState.onDataChanged();
      return created;
    } catch(e) {
      toast('Error: ' + e.message, 'error');
      return 0;
    } finally {
      hideSpinner();
    }
  };

  // ── Import modal ──────────────────────────────────────────────────────
  document.getElementById('btn-import').addEventListener('click', () => {
    openModal('import-modal');
    setTimeout(() => document.getElementById('import-text').focus(), 80);
  });
  document.getElementById('btn-import-submit').addEventListener('click', async () => {
    const text = document.getElementById('import-text').value.trim();
    if (!text) { toast('Enter some text first', 'warn'); return; }
    const addMode = document.getElementById('import-add-mode').checked;
    closeModal('import-modal');
    await AppState.parseAndAdd(text, addMode, null);
  });
  document.getElementById('import-text').addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey))
      document.getElementById('btn-import-submit').click();
  });

  // JSON Selector from import
  document.getElementById('btn-import-json-sel').addEventListener('click', () => {
    const text = document.getElementById('import-text').value.trim();
    if (!text) { toast('Enter JSON text first', 'warn'); return; }
    if (!looksLikeJson(text)) { toast('Text does not look like JSON', 'warn'); return; }
    let data;
    try { data = JSON.parse(text); } catch(e) { toast('Invalid JSON: ' + e.message, 'error'); return; }
    openJsonSelectorModal(data, async (paths) => {
      if (!paths.length) return;
      const addMode = document.getElementById('import-add-mode').checked;
      const extracted = _extractByPaths(data, paths);
      if (!addMode) { AppState.nodes.clear(); AppState.edges.clear(); AppState.selectedNodes.clear(); }
      extracted.forEach(({ path, value }) => {
        const id = uuid();
        const typeName = path.replace(/\.\"|\"|\[\]/g, '').replace(/[^a-zA-Z0-9_]/g, '_').replace(/^_+|_+$/g,'') || 'json_extract';
        AppState.nodes.set(id, { id, label: trunc(String(value), 40), value: String(value), type: typeName, metadata: {} });
      });
      AppState.onDataChanged();
      closeModal('import-modal');
      toast(`Extracted ${extracted.length} value(s)`, 'success');
      setTimeout(() => graphMgr.fitGraph(), 350);
    });
  });

  // ── Clear ──────────────────────────────────────────────────────────────
  document.getElementById('btn-clear-graph').addEventListener('click', () => {
    if (!AppState.nodes.size || confirmDialog('Clear all nodes?')) {
      AppState.nodes.clear(); AppState.edges.clear(); AppState.selectedNodes.clear();
      document.getElementById('node-info').classList.add('hidden');
      AppState.onDataChanged();
    }
  });

  // ── Keyboard shortcuts ─────────────────────────────────────────────────
  document.addEventListener('keydown', e => {
    const inInput = ['INPUT','TEXTAREA'].includes(document.activeElement?.tagName);
    if ((e.ctrlKey || e.metaKey) && e.key === 'k' && !inInput) { e.preventDefault(); actionMgr.openPalette(); }
    if ((e.ctrlKey || e.metaKey) && e.key === 'i' && !inInput) {
      e.preventDefault();
      openModal('import-modal');
      setTimeout(() => document.getElementById('import-text').focus(), 80);
    }
  });

  document.addEventListener('click', () => document.getElementById('ctx-menu').classList.add('hidden'));

  // ── Resizable panes ───────────────────────────────────────────────────
  _initResizable(document.getElementById('v-divider'), document.getElementById('filter-pane'), 'width', 140, 440, 'col-resize');
  _initResizable(document.getElementById('h-divider'), document.getElementById('table-area'), 'height_inv', 60, 600, 'row-resize');

  // ── Bootstrap ─────────────────────────────────────────────────────────
  (async () => {
    try {
      await actionMgr.loadActions();
      toast(`Ready — ${actionMgr.allActions.length} actions loaded`, 'success', 2500);
    } catch(e) { toast('Error loading actions: ' + e.message, 'error'); }
  })();
});

// ── Pane resize ────────────────────────────────────────────────────────────
function _initResizable(divider, target, prop, min, max, cursor) {
  let dragging = false, startCoord = 0, startSize = 0;
  divider.addEventListener('mousedown', e => {
    dragging = true;
    startCoord = prop.startsWith('height') ? e.clientY : e.clientX;
    startSize  = prop.startsWith('height') ? target.offsetHeight : target.offsetWidth;
    document.body.style.cursor = cursor;
    divider.classList.add('active');
  });
  document.addEventListener('mousemove', e => {
    if (!dragging) return;
    let delta = prop.startsWith('height') ? e.clientY - startCoord : e.clientX - startCoord;
    if (prop === 'height_inv') delta = -delta;
    const v = Math.max(min, Math.min(max, startSize + delta));
    target.style[prop === 'width' ? 'width' : 'height'] = v + 'px';
  });
  document.addEventListener('mouseup', () => {
    if (dragging) { dragging = false; document.body.style.cursor = ''; divider.classList.remove('active'); }
  });
}

// ── jq path extractor (used for JSON selector → nodes) ────────────────────
function _extractByPaths(data, paths) {
  const results = [];
  const seen = new Set();
  paths.forEach(path => {
    try {
      const val = _jqGet(data, path);
      const flat = Array.isArray(val) ? val : [val];
      flat.forEach(v => {
        if (v === null || v === undefined) return;
        const s = String(v);
        if (!seen.has(path + ':' + s)) { seen.add(path + ':' + s); results.push({ path, value: s }); }
      });
    } catch {}
  });
  return results;
}

function _jqGet(data, path) {
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
        if (Array.isArray(item)) { if (!isNaN(num)) next.push(item[num]); else item.forEach(el => { if (String(el) === sub) next.push(el); }); }
        else if (item?.[sub] !== undefined) next.push(item[sub]);
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
}