/* filters.js – filter pane, query builder, type legend */

const OPERATORS = [
  { value:'contains',     label:'contains' },
  { value:'not_contains', label:'!contains' },
  { value:'equals',       label:'equals' },
  { value:'starts_with',  label:'starts with' },
  { value:'ends_with',    label:'ends with' },
  { value:'regex',        label:'regex' },
];

class FilterManager {
  constructor(appState) {
    this.state = appState;
    // Filter groups: [{id, logic:'AND'|'OR', filters:[{id, field, op, value}]}]
    this.filterGroups = [];
    this.groupsLogic = 'AND'; // Logic between groups
    // text and csv parsers are too generic — hide by default
    this.hiddenTypes = new Set(['text', 'csv']);
    // _bindUI() called via init() from app.js DOMContentLoaded
  }

  init() {
    this._bindUI();
    // Start with one empty group
    if (!this.filterGroups.length) this.addGroup();
  }

  _bindUI() {
    document.getElementById('btn-add-filter').addEventListener('click', () => {
      // Add filter to the last group, or create new group if none exist
      if (!this.filterGroups.length) this.addGroup();
      this.addFilterToGroup(this.filterGroups[this.filterGroups.length - 1].id);
    });
    document.querySelectorAll('input[name="filter-logic"]').forEach(r =>
      r.addEventListener('change', e => { this.groupsLogic = e.target.value; this._apply(); })
    );
  }

  _fieldOptions() {
    const opts = [{ v:'value', l:'Value' }, { v:'type', l:'Type' }];
    const metaKeys = new Set();
    this.state.nodes.forEach(n => Object.keys(n.metadata || {}).forEach(k => metaKeys.add(k)));
    [...metaKeys].sort().forEach(k => opts.push({ v:`meta::${k}`, l:`Meta: ${k}` }));
    return opts;
  }

  addGroup(logic='AND') {
    const id = uuid();
    this.filterGroups.push({ id, logic, filters: [] });
    this._renderFilters();
  }

  removeGroup(groupId) {
    this.filterGroups = this.filterGroups.filter(g => g.id !== groupId);
    if (!this.filterGroups.length) this.addGroup(); // Always keep at least one group
    this._renderFilters();
    this._apply();
  }

  addFilterToGroup(groupId, field='value', op='contains', value='') {
    const group = this.filterGroups.find(g => g.id === groupId);
    if (!group) return;
    const id = uuid();
    group.filters.push({ id, field, op, value });
    this._renderFilters();
    // Focus new filter value input
    requestAnimationFrame(() => {
      const inp = document.querySelector(`[data-fid="${id}"] .filter-val`);
      if (inp) inp.focus();
    });
  }

  removeFilter(groupId, filterId) {
    const group = this.filterGroups.find(g => g.id === groupId);
    if (!group) return;
    group.filters = group.filters.filter(f => f.id !== filterId);
    this._renderFilters();
    this._apply();
  }

  _renderFilters() {
    const list = document.getElementById('filter-list');
    list.innerHTML = '';
    const fieldOpts = this._fieldOptions();

    this.filterGroups.forEach((group, groupIdx) => {
      // Group container
      const groupDiv = document.createElement('div');
      groupDiv.className = 'filter-group';
      groupDiv.dataset.gid = group.id;

      // Group header with logic selector and delete
      const groupHeader = document.createElement('div');
      groupHeader.className = 'filter-group-header';

      const groupLabel = document.createElement('span');
      groupLabel.className = 'filter-group-label';
      groupLabel.textContent = `Group ${groupIdx + 1}`;

      // Group logic (AND/OR within this group)
      const groupLogicWrap = document.createElement('div');
      groupLogicWrap.className = 'filter-group-logic';

      const andLabel = document.createElement('label');
      andLabel.className = 'radio-label';
      const andRadio = document.createElement('input');
      andRadio.type = 'radio';
      andRadio.name = `group-logic-${group.id}`;
      andRadio.value = 'AND';
      andRadio.checked = group.logic === 'AND';
      andRadio.addEventListener('change', () => { group.logic = 'AND'; this._apply(); });
      andLabel.append(andRadio, document.createTextNode(' AND'));

      const orLabel = document.createElement('label');
      orLabel.className = 'radio-label';
      const orRadio = document.createElement('input');
      orRadio.type = 'radio';
      orRadio.name = `group-logic-${group.id}`;
      orRadio.value = 'OR';
      orRadio.checked = group.logic === 'OR';
      orRadio.addEventListener('change', () => { group.logic = 'OR'; this._apply(); });
      orLabel.append(orRadio, document.createTextNode(' OR'));

      groupLogicWrap.append(andLabel, orLabel);

      // Group actions
      const groupActions = document.createElement('div');
      groupActions.className = 'filter-group-actions';

      const addFilterBtn = document.createElement('button');
      addFilterBtn.className = 'btn-icon';
      addFilterBtn.title = 'Add filter to this group';
      addFilterBtn.textContent = '＋';
      addFilterBtn.addEventListener('click', () => this.addFilterToGroup(group.id));

      const delGroupBtn = document.createElement('button');
      delGroupBtn.className = 'filter-del';
      delGroupBtn.title = 'Delete group';
      delGroupBtn.textContent = '✕';
      delGroupBtn.addEventListener('click', () => this.removeGroup(group.id));

      groupActions.append(addFilterBtn, delGroupBtn);
      groupHeader.append(groupLabel, groupLogicWrap, groupActions);

      // Filters in this group
      const filtersDiv = document.createElement('div');
      filtersDiv.className = 'filter-group-filters';

      group.filters.forEach(f => {
        const row = document.createElement('div');
        row.className = 'filter-row';
        row.dataset.fid = f.id;

        // Field
        const fsel = document.createElement('select');
        fsel.className = 'filter-select';
        fieldOpts.forEach(o => {
          const opt = document.createElement('option');
          opt.value = o.v;
          opt.textContent = o.l;
          if (o.v === f.field) opt.selected = true;
          fsel.appendChild(opt);
        });
        fsel.addEventListener('change', e => { f.field = e.target.value; this._apply(); });

        // Operator
        const osel = document.createElement('select');
        osel.className = 'filter-select';
        OPERATORS.forEach(o => {
          const opt = document.createElement('option');
          opt.value = o.value;
          opt.textContent = o.label;
          if (o.value === f.op) opt.selected = true;
          osel.appendChild(opt);
        });
        osel.addEventListener('change', e => { f.op = e.target.value; this._apply(); });

        // Delete
        const del = document.createElement('button');
        del.className = 'filter-del';
        del.textContent = '✕';
        del.type = 'button';
        del.addEventListener('click', () => this.removeFilter(group.id, f.id));

        // Value input
        const vinp = document.createElement('input');
        vinp.type = 'text';
        vinp.className = 'filter-val';
        vinp.value = f.value;
        vinp.placeholder = 'Filter value…';
        const _applyDebounced = debounce(() => this._apply(), 250);
        vinp.addEventListener('input', e => { f.value = e.target.value; _applyDebounced(); });

        const top = document.createElement('div');
        top.className = 'filter-row-top';
        top.append(fsel, osel, del);
        row.append(top, vinp);
        filtersDiv.appendChild(row);
      });

      groupDiv.append(groupHeader, filtersDiv);
      list.appendChild(groupDiv);

      // Add group operator between groups (except after last)
      if (groupIdx < this.filterGroups.length - 1) {
        const groupOp = document.createElement('div');
        groupOp.className = 'filter-group-operator';
        groupOp.textContent = this.groupsLogic;
        list.appendChild(groupOp);
      }
    });

    // Add group button at the bottom
    const addGroupBtn = document.createElement('button');
    addGroupBtn.className = 'btn btn-sm filter-add-group-btn';
    addGroupBtn.textContent = '＋ Add Group';
    addGroupBtn.addEventListener('click', () => this.addGroup());
    list.appendChild(addGroupBtn);
  }

  renderTypeLegend() {
    const el = document.getElementById('type-legend'); el.innerHTML = '';
    const counts = {};
    this.state.nodes.forEach(n => { counts[n.type] = (counts[n.type] || 0) + 1; });
    Object.keys(counts).sort().forEach(t => {
      const row = document.createElement('div');
      row.className = 'type-legend-row' + (this.hiddenTypes.has(t) ? ' hidden-type' : '');
      row.title = this.hiddenTypes.has(t) ? `Show "${t}"` : `Hide "${t}"`;
      const dot = document.createElement('div'); dot.className = 'type-dot'; dot.style.background = typeColor(t).raw;
      const lbl = document.createElement('span'); lbl.textContent = t;
      const cnt = document.createElement('span'); cnt.className = 'type-count'; cnt.textContent = counts[t];
      row.append(dot, lbl, cnt);
      row.addEventListener('click', () => {
        if (this.hiddenTypes.has(t)) this.hiddenTypes.delete(t); else this.hiddenTypes.add(t);
        this._apply(); this.renderTypeLegend();
      });
      el.appendChild(row);
    });
  }

  _testFilter(node, filter) {
    let hay = '';
    if      (filter.field === 'value') hay = node.value || '';
    else if (filter.field === 'type')  hay = node.type  || '';
    else if (filter.field.startsWith('meta::')) hay = String((node.metadata || {})[filter.field.slice(6)] ?? '');
    hay = hay.toLowerCase();
    const needle = (filter.value || '').toLowerCase();
    switch (filter.op) {
      case 'contains':     return hay.includes(needle);
      case 'not_contains': return !hay.includes(needle);
      case 'equals':       return hay === needle;
      case 'starts_with':  return hay.startsWith(needle);
      case 'ends_with':    return hay.endsWith(needle);
      case 'regex':
        try { return new RegExp(filter.value, 'i').test(hay); } catch { return false; }
      default: return true;
    }
  }

  _testNode(node) {
    if (this.hiddenTypes.has(node.type)) return false;

    // If no groups or all groups are empty, show all nodes
    const hasFilters = this.filterGroups.some(g => g.filters.length > 0);
    if (!hasFilters) return true;

    // Test each group
    const groupResults = this.filterGroups.map(group => {
      if (!group.filters.length) return true; // Empty group passes

      // Test filters within this group
      const filterResults = group.filters.map(f => this._testFilter(node, f));

      // Apply group's internal logic (AND/OR)
      return group.logic === 'AND'
        ? filterResults.every(Boolean)
        : filterResults.some(Boolean);
    });

    // Apply logic between groups
    return this.groupsLogic === 'AND'
      ? groupResults.every(Boolean)
      : groupResults.some(Boolean);
  }

  _apply() {
    this.state.hiddenNodes.clear();
    this.state.nodes.forEach((n, id) => { if (!this._testNode(n)) this.state.hiddenNodes.add(id); });
    this.state.hiddenNodes.forEach(id => this.state.selectedNodes.delete(id));
    if (this.state.onFilterChange) this.state.onFilterChange();
  }

  onNodesChanged() {
    this._renderFilters();
    this.renderTypeLegend();
    this._apply();
    this._renderUtilButtons();
  }

  _renderUtilButtons() {
    const panel = document.getElementById('filter-pane');
    let btns = document.getElementById('filter-util-btns');
    if (!btns) {
      btns = document.createElement('div');
      btns.id = 'filter-util-btns';
      btns.className = 'filter-util-btns';
      panel.appendChild(btns);
    }

    btns.innerHTML = '';

    const orphanBtn = document.createElement('button');
    orphanBtn.className = 'btn btn-sm btn-danger filter-util-btn';
    orphanBtn.title = 'Delete nodes with no edges';
    orphanBtn.textContent = '🗑 Delete orphan nodes';
    orphanBtn.addEventListener('click', () => {
      const connectedIds = new Set();
      this.state.edges.forEach(e => { connectedIds.add(e.from); connectedIds.add(e.to); });
      let removed = 0;
      for (const [id] of [...this.state.nodes]) {
        if (!connectedIds.has(id)) { this.state.nodes.delete(id); removed++; }
      }
      this.state.selectedNodes.forEach(id => { if (!this.state.nodes.has(id)) this.state.selectedNodes.delete(id); });
      toast(`Deleted ${removed} orphan node(s)`, removed ? 'success' : 'info');
      if (removed && this.state.onDataChanged) this.state.onDataChanged();
    });

    const noisyBtn = document.createElement('button');
    noisyBtn.className = 'btn btn-sm btn-danger filter-util-btn';
    noisyBtn.title = 'Delete generic text and CSV nodes';
    noisyBtn.textContent = '🗑 Delete text/CSV nodes';
    noisyBtn.addEventListener('click', () => {
      const NOISY_TYPES = new Set(['text', 'csv', 'filename']);
      let removed = 0;
      const toRemove = [];
      this.state.nodes.forEach((n, id) => { if (NOISY_TYPES.has(n.type)) toRemove.push(id); });
      toRemove.forEach(id => {
        this.state.nodes.delete(id);
        this.state.edges.forEach((e, eid) => { if (e.from === id || e.to === id) this.state.edges.delete(eid); });
        removed++;
      });
      this.state.selectedNodes.forEach(id => { if (!this.state.nodes.has(id)) this.state.selectedNodes.delete(id); });
      toast(`Deleted ${removed} text/CSV node(s)`, removed ? 'success' : 'info');
      if (removed && this.state.onDataChanged) this.state.onDataChanged();
    });

    btns.append(orphanBtn, noisyBtn);
  }
}