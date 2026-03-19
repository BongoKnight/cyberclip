/* table.js – table view: sortable, resizable columns, expand-to-nodes */

class TableManager {
  constructor(appState) {
    this.state = appState;
    this.selectedColumn = null;
    this._sortCol   = null;   // column key being sorted
    this._sortDir   = 1;      // 1 = asc, -1 = desc
    this._colWidths = {};     // col key → px width
    this._bindUI();
  }

  // ── API: ordered visible node IDs matching current table display ───────
  // Used by ActionManager._executeBulkColumn to ensure results align correctly.
  getVisibleNodeIds() {
    const nodes = this._getSortedNodes().filter(n => !this.state.hiddenNodes.has(n.id));
    return nodes.map(n => n.id);
  }

  _getSortedNodes() {
    let nodes = [...this.state.nodes.values()];
    if (this._sortCol) {
      nodes.sort((a, b) => {
        const va = this._cellValue(a, this._sortCol).toLowerCase();
        const vb = this._cellValue(b, this._sortCol).toLowerCase();
        return va < vb ? -this._sortDir : va > vb ? this._sortDir : 0;
      });
    }
    return nodes;
  }

  _cellValue(node, col) {
    if (col === '__type__')  return node.type  || '';
    if (col === '__value__') return node.value || '';
    return String((node.metadata || {})[col] ?? '');
  }

  _bindUI() {
    document.getElementById('btn-col-action').addEventListener('click', () => {
      if (this.selectedColumn) this.state.actionManager.openPalette(this.selectedColumn);
    });
    document.getElementById('btn-del-col').addEventListener('click', () => {
      if (!this.selectedColumn || this.selectedColumn === '__type__' || this.selectedColumn === '__value__') return;
      if (!confirmDialog(`Delete column "${this.selectedColumn}"?`)) return;
      this.state.nodes.forEach(n => { delete n.metadata[this.selectedColumn]; });
      this.selectedColumn = null;
      if (this.state.onDataChanged) this.state.onDataChanged();
    });
    // Expand column → new nodes button
    document.getElementById('btn-expand-col').addEventListener('click', () => {
      if (!this.selectedColumn) return;
      this._expandColumnToNodes(this.selectedColumn);
    });
    document.getElementById('btn-copy-col').addEventListener('click', () => {
      if (!this.selectedColumn) return;
      this._copyColumn(this.selectedColumn);
    });
    // Export buttons
    document.getElementById('btn-export-csv').addEventListener('click', () => this._exportAsCSV());
    document.getElementById('btn-export-json').addEventListener('click', () => this._exportAsJSON());
  }

  _allColumns() {
    const cols = new Set();
    this.state.nodes.forEach(n => Object.keys(n.metadata || {}).forEach(k => cols.add(k)));
    return ['__type__', '__value__', ...Array.from(cols).sort()];
  }

  render() {
    const head = document.getElementById('table-head');
    const body = document.getElementById('table-body');
    const cols = this._allColumns();

    if (!this.state.nodes.size) {
      head.innerHTML = '';
      body.innerHTML = '<tr><td colspan="2" class="empty-state">No nodes yet — import some text to get started</td></tr>';
      document.getElementById('btn-col-action').classList.add('hidden');
      document.getElementById('btn-del-col').classList.add('hidden');
      document.getElementById('btn-expand-col').classList.add('hidden');
      document.getElementById('btn-copy-col').classList.add('hidden');
      document.getElementById('btn-export-csv').classList.add('hidden');
      document.getElementById('btn-export-json').classList.add('hidden');
      return;
    }

    // Show export buttons when there's data
    document.getElementById('btn-export-csv').classList.remove('hidden');
    document.getElementById('btn-export-json').classList.remove('hidden');

    // ── Header ─────────────────────────────────────────────────────────
    head.innerHTML = '';
    const tr = document.createElement('tr');

    cols.forEach((col, colIdx) => {
      const th = document.createElement('th');
      const labelText = col === '__type__' ? 'Type' : col === '__value__' ? 'Value' : col;
      th.dataset.col = col;
      th.classList.toggle('col-selected', col === this.selectedColumn);

      // Apply stored width
      if (this._colWidths[col]) th.style.width = this._colWidths[col] + 'px';

      // ── Content wrapper ──────────────────────────────────────────────
      const inner = document.createElement('div'); inner.className = 'th-inner';

      // Sort indicator
      const sortEl = document.createElement('span'); sortEl.className = 'col-sort-icon';
      if (this._sortCol === col) sortEl.textContent = this._sortDir === 1 ? ' ↑' : ' ↓';

      const lbl = document.createElement('span'); lbl.className = 'th-label'; lbl.textContent = labelText;
      lbl.appendChild(sortEl);

      // Delete button for meta cols
      if (col !== '__type__' && col !== '__value__') {
        const del = document.createElement('span'); del.className = 'col-del'; del.textContent = '✕'; del.title = `Delete column "${col}"`;
        del.addEventListener('click', e => {
          e.stopPropagation();
          if (!confirmDialog(`Delete column "${col}"?`)) return;
          this.state.nodes.forEach(n => { delete n.metadata[col]; });
          if (this.selectedColumn === col) this.selectedColumn = null;
          if (this.state.onDataChanged) this.state.onDataChanged();
        });
        inner.appendChild(del);
      }

      inner.prepend(lbl);
      th.appendChild(inner);

      // Click → sort (asc → desc → none)
      lbl.addEventListener('click', () => {
        if (this._sortCol === col) {
          if (this._sortDir === 1) { this._sortDir = -1; }
          else { this._sortCol = null; this._sortDir = 1; }
        } else { this._sortCol = col; this._sortDir = 1; }
        this._selectColumn(col, cols);
        this.render();
      });

      // Column select (on th click, not label)
      th.addEventListener('click', (e) => {
        if (e.target === th || e.target === inner) {
          this._selectColumn(col === this.selectedColumn ? null : col, cols);
        }
      });

      // ── Resize handle ─────────────────────────────────────────────────
      const handle = document.createElement('div'); handle.className = 'col-resize-handle';
      handle.addEventListener('mousedown', e => {
        e.stopPropagation();
        const startX = e.clientX;
        const startW = th.offsetWidth;
        const move = ev => {
          const newW = Math.max(60, startW + ev.clientX - startX);
          th.style.width = newW + 'px';
          this._colWidths[col] = newW;
          // Also resize all td cells in this column
          document.querySelectorAll(`#table-body td:nth-child(${colIdx + 1})`).forEach(td => { td.style.width = newW + 'px'; });
        };
        const up = () => { document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up); document.body.style.cursor = ''; };
        document.addEventListener('mousemove', move);
        document.addEventListener('mouseup', up);
        document.body.style.cursor = 'col-resize';
      });
      th.appendChild(handle);
      tr.appendChild(th);
    });
    head.appendChild(tr);

    // ── Body ───────────────────────────────────────────────────────────
    body.innerHTML = '';
    this._getSortedNodes().forEach(node => {
      const id = node.id;
      const row = document.createElement('tr');
      row.dataset.nid = id;
      row.classList.toggle('row-hidden', this.state.hiddenNodes.has(id));
      row.classList.toggle('row-selected', this.state.selectedNodes.has(id));
      row.addEventListener('click', e => {
        if (!e.ctrlKey && !e.metaKey) this.state.selectedNodes.clear();
        if (this.state.selectedNodes.has(id)) this.state.selectedNodes.delete(id);
        else this.state.selectedNodes.add(id);
        if (this.state.onSelectionChange) this.state.onSelectionChange();
      });

      cols.forEach((col, colIdx) => {
        const td = document.createElement('td');
        td.classList.toggle('col-selected', col === this.selectedColumn);
        if (this._colWidths[col]) td.style.width = this._colWidths[col] + 'px';

        const text = this._cellValue(node, col);
        const inner = document.createElement('div'); inner.className = 'td-inner';
        const span  = document.createElement('span'); span.className = 'td-value'; span.textContent = text; span.title = text.length > 60 ? text : '';

        // Copy btn
        const cpyBtn = document.createElement('button'); cpyBtn.className = 'td-copy-btn'; cpyBtn.textContent = '📋'; cpyBtn.title = 'Copy';
        cpyBtn.addEventListener('click', e => { e.stopPropagation(); copyText(text); });

        // Create new node from this cell value
        const newBtn = document.createElement('button'); newBtn.className = 'td-new-node-btn'; newBtn.title = 'Parse this value → new nodes';
        newBtn.textContent = '＋';
        newBtn.addEventListener('click', async e => {
          e.stopPropagation();
          if (!text) return;
          const edgeLabel = col === '__value__' ? 'value' : col;

          // For metadata columns, use datatype selection
          const isMetadataCol = col !== '__type__' && col !== '__value__';
          if (isMetadataCol && this.state.parseAndAddWithTypeSelection) {
            await this.state.parseAndAddWithTypeSelection(text, true, id, edgeLabel, false);
          } else {
            const newIds = await this.state.parseAndAdd(text, true, id, edgeLabel);
            if (newIds.length) toast(`Created ${newIds.length} node(s)`, 'success', 2000);
          }
        });

        span.addEventListener('click', e => {
          e.stopPropagation();
          if (text.length > 100) showFullText(col === '__value__' ? `${node.type}: value` : col, text);
          else copyText(text);
        });
        td.addEventListener('contextmenu', e => this._showCellContextMenu(e, text, col, id));

        inner.append(span, cpyBtn);
        if (col !== '__type__') inner.appendChild(newBtn);
        td.appendChild(inner);
        row.appendChild(td);
      });
      body.appendChild(row);
    });
  }

  _selectColumn(col, cols) {
    this.selectedColumn = col;
    // Update header
    document.querySelectorAll('#table-head th').forEach(th => th.classList.toggle('col-selected', th.dataset.col === col));
    // Update cells
    const allCols = cols || this._allColumns();
    document.querySelectorAll('#table-body tr').forEach(row => {
      row.querySelectorAll('td').forEach((td, i) => td.classList.toggle('col-selected', allCols[i] === col));
    });
    // Toolbar
    const hasMeta = col && col !== '__type__' && col !== '__value__';
    document.getElementById('btn-col-action').classList.toggle('hidden', !col);
    document.getElementById('btn-del-col').classList.toggle('hidden', !hasMeta);
    document.getElementById('btn-expand-col').classList.toggle('hidden', !col);
    document.getElementById('btn-copy-col').classList.toggle('hidden', !col);
  }

  // ── Expand entire column → parse each cell into new nodes ─────────────
  async _expandColumnToNodes(colKey) {
    const nodeIds = this.getVisibleNodeIds();
    const edgeLabel = colKey === '__value__' ? 'value' : colKey;
    showSpinner(`Expanding column "${colKey === '__value__' ? 'Value' : colKey}"…`);

    try {
      // Collect all non-empty values
      const valuesToParse = [];
      const sourceNodes = [];

      for (const id of nodeIds) {
        const node = this.state.nodes.get(id);
        if (!node) continue;
        const text = this._cellValue(node, colKey);
        if (!text) continue;
        valuesToParse.push(text);
        sourceNodes.push(id);
      }

      if (!valuesToParse.length) {
        toast('Column has no values to parse', 'warn');
        return;
      }

      // Bulk parse all values at once
      const res = await apiPost('/api/parse_bulk', { values: valuesToParse });

      if (res.error) {
        toast('Error: ' + res.error, 'error');
        return;
      }

      // Process results and create nodes
      let created = 0;
      res.results.forEach((result, idx) => {
        const sourceId = sourceNodes[idx];
        (result.nodes || []).forEach(n => {
          // Dedup by type+value
          let exists = false;
          for (const ex of this.state.nodes.values()) {
            if (ex.type === n.type && ex.value === n.value) {
              // Already exists: create edge to it
              if (this.state.addEdge) this.state.addEdge(sourceId, ex.id, edgeLabel);
              exists = true;
              break;
            }
          }
          if (!exists) {
            // Create new node
            const freshId = uuid();
            this.state.nodes.set(freshId, { ...n, id: freshId, metadata: n.metadata || {} });
            if (this.state.addEdge) this.state.addEdge(sourceId, freshId, edgeLabel);
            created++;
          }
        });
      });

      if (this.state.onDataChanged) this.state.onDataChanged();
      toast(`Expanded column → ${created} new node(s)`, 'success');
    } catch(e) {
      toast('Error: ' + e.message, 'error');
    } finally {
      hideSpinner();
    }
  }

  _copyColumn(colKey) {
    const vals = this.getVisibleNodeIds()
      .map(id => this._cellValue(this.state.nodes.get(id), colKey))
      .filter(v => v !== '');
    if (!vals.length) { toast('Column is empty', 'warn'); return; }
    copyText(vals.join('\n'));
    toast(`Copied ${vals.length} values`, 'success', 2000);
  }

  _showCellContextMenu(e, text, colKey, nodeId) {
    e.preventDefault();
    e.stopPropagation();
    let menu = document.getElementById('table-cell-ctx');
    if (!menu) {
      menu = document.createElement('ul');
      menu.id = 'table-cell-ctx';
      menu.className = 'ctx-menu hidden';
      document.body.appendChild(menu);
      document.addEventListener('click', () => menu.classList.add('hidden'));
    }
    menu.innerHTML = '';
    menu.classList.remove('hidden');
    // Position
    menu.style.left = e.clientX + 'px';
    menu.style.top  = e.clientY + 'px';
    requestAnimationFrame(() => {
      const r = menu.getBoundingClientRect();
      if (r.right  > window.innerWidth)  menu.style.left = (e.clientX - r.width)  + 'px';
      if (r.bottom > window.innerHeight) menu.style.top  = (e.clientY - r.height) + 'px';
    });

    const isMetadataCol = colKey !== '__type__' && colKey !== '__value__';
    const edgeLabel = colKey === '__value__' ? 'value' : colKey;

    const items = [
      { icon: '📋', label: 'Copy value', fn: () => copyText(text) },
      { icon: '🔍', label: 'Filter: contains this value', fn: () => {
          if (this.state.filterManager) {
            const lastGroup = this.state.filterManager.filterGroups[this.state.filterManager.filterGroups.length - 1];
            if (lastGroup) {
              this.state.filterManager.addFilterToGroup(
                lastGroup.id,
                colKey === '__type__' ? 'type' : colKey === '__value__' ? 'value' : `meta::${colKey}`,
                'contains',
                text
              );
            }
          }
        }
      },
      { icon: '🔎', label: 'Filter: equals this value', fn: () => {
          if (this.state.filterManager) {
            const lastGroup = this.state.filterManager.filterGroups[this.state.filterManager.filterGroups.length - 1];
            if (lastGroup) {
              this.state.filterManager.addFilterToGroup(
                lastGroup.id,
                colKey === '__type__' ? 'type' : colKey === '__value__' ? 'value' : `meta::${colKey}`,
                'equals',
                text
              );
            }
          }
        }
      },
      { icon: '🚫', label: 'Filter: exclude this value', fn: () => {
          if (this.state.filterManager) {
            const lastGroup = this.state.filterManager.filterGroups[this.state.filterManager.filterGroups.length - 1];
            if (lastGroup) {
              this.state.filterManager.addFilterToGroup(
                lastGroup.id,
                colKey === '__type__' ? 'type' : colKey === '__value__' ? 'value' : `meta::${colKey}`,
                'not_contains',
                text
              );
            }
          }
        }
      },
      { sep: true },
      { icon: '＋', label: 'Parse → new nodes', fn: async () => {
          if (!text) return;
          // For metadata columns, use datatype selection
          if (isMetadataCol && this.state.parseAndAddWithTypeSelection) {
            await this.state.parseAndAddWithTypeSelection(text, true, nodeId, edgeLabel, false);
          } else {
            const newIds = await this.state.parseAndAdd(text, true, nodeId, edgeLabel);
            if (newIds.length) toast(`Created ${newIds.length} node(s)`, 'success', 2000);
          }
        }
      },
    ];
    items.forEach(it => {
      const li = document.createElement('li');
      if (it.sep) { li.className = 'sep'; }
      else {
        const icon = document.createElement('span'); icon.textContent = it.icon;
        const lbl  = document.createElement('span'); lbl.textContent  = it.label;
        li.append(icon, lbl);
        li.addEventListener('click', () => { menu.classList.add('hidden'); it.fn(); });
      }
      menu.appendChild(li);
    });
    setTimeout(() => {
      const close = ev => { if (!menu.contains(ev.target)) { menu.classList.add('hidden'); document.removeEventListener('click', close); } };
      document.addEventListener('click', close);
    }, 10);
  }

  syncSelectionHighlight() {
    document.querySelectorAll('#table-body tr[data-nid]').forEach(tr =>
      tr.classList.toggle('row-selected', this.state.selectedNodes.has(tr.dataset.nid))
    );
  }

  syncHiddenRows() {
    document.querySelectorAll('#table-body tr[data-nid]').forEach(tr =>
      tr.classList.toggle('row-hidden', this.state.hiddenNodes.has(tr.dataset.nid))
    );
  }

  // ── Export table as CSV ───────────────────────────────────────────────
  _exportAsCSV() {
    const cols = this._allColumns();
    const nodeIds = this.getVisibleNodeIds();

    if (!nodeIds.length) {
      toast('No data to export', 'warn');
      return;
    }

    // CSV Header
    const header = cols.map(col => {
      const label = col === '__type__' ? 'Type' : col === '__value__' ? 'Value' : col;
      return this._escapeCSV(label);
    }).join(',');

    // CSV Rows
    const rows = nodeIds.map(id => {
      const node = this.state.nodes.get(id);
      return cols.map(col => {
        const value = this._cellValue(node, col);
        return this._escapeCSV(value);
      }).join(',');
    });

    const csv = [header, ...rows].join('\n');

    // Download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `cyberclip_table_${this._getTimestamp()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toast(`Exported ${nodeIds.length} row(s) as CSV`, 'success');
  }

  // ── Export table as JSON ──────────────────────────────────────────────
  _exportAsJSON() {
    const cols = this._allColumns();
    const nodeIds = this.getVisibleNodeIds();

    if (!nodeIds.length) {
      toast('No data to export', 'warn');
      return;
    }

    // Build JSON array of objects
    const data = nodeIds.map(id => {
      const node = this.state.nodes.get(id);
      const row = {};
      cols.forEach(col => {
        const key = col === '__type__' ? 'type' : col === '__value__' ? 'value' : col;
        row[key] = this._cellValue(node, col);
      });
      return row;
    });

    const json = JSON.stringify(data, null, 2);

    // Download
    const blob = new Blob([json], { type: 'application/json;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `cyberclip_table_${this._getTimestamp()}.json`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toast(`Exported ${nodeIds.length} row(s) as JSON`, 'success');
  }

  // ── Helper: escape CSV values ─────────────────────────────────────────
  _escapeCSV(value) {
    const str = String(value);
    // If contains comma, quote, or newline, wrap in quotes and escape quotes
    if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  }

  // ── Helper: timestamp for filenames ───────────────────────────────────
  _getTimestamp() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const min = String(now.getMinutes()).padStart(2, '0');
    const sec = String(now.getSeconds()).padStart(2, '0');
    return `${year}${month}${day}_${hour}${min}${sec}`;
  }
}