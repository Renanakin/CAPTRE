const state = {
  apiBase: 'http://127.0.0.1:8000/api/v1',
  tenantId: '',
  user: '',
  knownDocuments: []
};

const el = (id) => document.getElementById(id);

function pretty(data) {
  return JSON.stringify(data, null, 2);
}

async function api(path, options = {}) {
  const res = await fetch(`${state.apiBase}${path}`, options);
  const contentType = res.headers.get('content-type') || '';
  if (!res.ok) {
    const errBody = contentType.includes('application/json') ? await res.json() : await res.text();
    throw new Error(typeof errBody === 'string' ? errBody : pretty(errBody));
  }
  if (contentType.includes('application/json')) return res.json();
  return res;
}

function switchTab(tabName) {
  document.querySelectorAll('.tab').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  document.querySelectorAll('.tab-panel').forEach((panel) => {
    panel.classList.toggle('hidden', panel.dataset.panel !== tabName);
  });
}

function setOutput(targetId, payload) {
  el(targetId).textContent = typeof payload === 'string' ? payload : pretty(payload);
}

function renderSimpleList(containerId, items, mapItem) {
  const c = el(containerId);
  c.innerHTML = '';
  if (!items.length) {
    c.innerHTML = '<div class="item">Sin datos.</div>';
    return;
  }
  for (const item of items) {
    const d = document.createElement('div');
    d.className = 'item';
    d.innerHTML = mapItem(item);
    c.appendChild(d);
  }
}

async function refreshDashboard() {
  const pending = await api('/reviews/pending');
  const docs = [...state.knownDocuments].slice(-5).reverse();

  const kpis = [
    { label: 'Documentos en memoria', value: state.knownDocuments.length },
    { label: 'Pendientes revision', value: pending.total || 0 },
    { label: 'Tenant activo', value: state.tenantId || '-' },
    { label: 'Usuario activo', value: state.user || '-' }
  ];

  const grid = el('kpiGrid');
  grid.innerHTML = kpis
    .map((k) => `<div class="kpi"><div class="n">${k.value}</div><div class="l">${k.label}</div></div>`)
    .join('');

  renderSimpleList('dashboardDocs', docs, (d) => `
    <div><strong>${d.document_id}</strong></div>
    <div class="meta">${d.status || 'RECEIVED'}</div>
  `);
}

async function loadDocumentList() {
  renderSimpleList('documentsList', state.knownDocuments.slice().reverse(), (d) => `
    <div><strong>${d.document_id}</strong></div>
    <div class="meta">${d.status || 'RECEIVED'}</div>
    <button data-doc="${d.document_id}" class="secondary view-doc">Ver detalle</button>
  `);

  document.querySelectorAll('.view-doc').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.doc;
      try {
        const detail = await api(`/documents/${id}`);
        setOutput('documentDetail', detail);
      } catch (err) {
        setOutput('documentDetail', String(err));
      }
    });
  });
}

async function loadReviews() {
  const payload = await api('/reviews/pending');
  renderSimpleList('reviewsList', payload.items || [], (r) => `
    <div><strong>${r.document_id}</strong></div>
    <div class="meta">${r.reason || '-'} | ${r.updated_at || '-'}</div>
  `);
}

function bindEvents() {
  el('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    state.user = el('loginUser').value.trim();
    state.tenantId = el('loginTenant').value.trim();
    if (!state.user || !state.tenantId) return;
    el('sessionBadge').textContent = `${state.user} @ ${state.tenantId}`;
    el('loginScreen').classList.add('hidden');
    el('appScreen').classList.remove('hidden');
    await refreshDashboard();
  });

  el('tabBar').addEventListener('click', (e) => {
    const btn = e.target.closest('.tab');
    if (!btn) return;
    switchTab(btn.dataset.tab);
  });

  el('refreshAllBtn').addEventListener('click', async () => {
    await refreshDashboard();
    await loadDocumentList();
    await loadReviews();
  });

  el('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const f = el('uploadFile').files[0];
      if (!f) throw new Error('Selecciona un archivo');
      const fd = new FormData();
      fd.append('file', f);
      fd.append('tenant_id', state.tenantId);
      if (el('uploadResponsible').value) fd.append('responsible', el('uploadResponsible').value);
      if (el('uploadPeriod').value) fd.append('period', el('uploadPeriod').value);
      if (el('uploadCenterCost').value) fd.append('center_cost', el('uploadCenterCost').value);

      const up = await api('/documents/upload', { method: 'POST', body: fd });
      state.knownDocuments.push(up);
      setOutput('uploadResult', up);
      await refreshDashboard();
      await loadDocumentList();
    } catch (err) {
      setOutput('uploadResult', String(err));
    }
  });

  el('loadDocumentsBtn').addEventListener('click', loadDocumentList);
  el('loadReviewsBtn').addEventListener('click', loadReviews);

  el('reviewActionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const documentId = el('reviewDocId').value.trim();
      const decision = el('reviewDecision').value;
      const reviewerId = el('reviewerId').value.trim();
      const reason = el('reviewReason').value.trim();
      const payload = await api(`/reviews/${documentId}/${decision}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer_id: reviewerId, reason, overrides: {} })
      });
      setOutput('reviewResult', payload);
      await loadReviews();
    } catch (err) {
      setOutput('reviewResult', String(err));
    }
  });

  el('renditionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const payload = {
        tenant_id: state.tenantId,
        period: el('renditionPeriod').value.trim(),
        responsible: el('renditionResponsible').value.trim() || null,
        center_cost: el('renditionCenterCost').value.trim() || null,
        template_version: '01-rendicion-gastos-2025'
      };
      const generated = await api('/renditions/generate/by-filter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      setOutput('renditionResult', generated);

      renderSimpleList('renditionsHistory', [generated], (r) => `
        <div><strong>${r.rendition_id}</strong></div>
        <div class="meta">warnings=${r.warnings_count} | ${r.status}</div>
        <a href="${state.apiBase}/renditions/${r.rendition_id}/download" target="_blank" rel="noreferrer">Descargar XLSX</a>
      `);
    } catch (err) {
      setOutput('renditionResult', String(err));
    }
  });
}

bindEvents();
