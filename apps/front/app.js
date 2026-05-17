const STORAGE_KEY = 'captre.console.state.v1';
const TOKEN_KEY = 'captre.console.tokens.v1';

const state = {
  apiBase: 'http://127.0.0.1:8000/api/v1',
  user: null,
  tokens: null,
  documents: [],
  uploadQueue: [],
  reviews: [],
  renditions: [],
  audit: [],
  health: {},
  route: 'dashboard',
  selectedReviewId: null,
  demoMode: false
};

const pageMeta = {
  dashboard: ['Inicio / Dashboard', 'Dashboard operacional'],
  documents: ['Documentos / Centro documental', 'Centro documental'],
  upload: ['Documentos / Carga', 'Carga documental avanzada'],
  reviews: ['Revision / Inteligente', 'Revision inteligente'],
  renditions: ['Rendiciones / Studio', 'Rendition Studio'],
  audit: ['Auditoria / Trazabilidad', 'Auditoria'],
  observability: ['Operacion / Observabilidad', 'Observabilidad'],
  settings: ['Sistema / Configuracion', 'Configuracion']
};

const routesByRole = {
  admin: ['dashboard', 'documents', 'upload', 'reviews', 'renditions', 'audit', 'observability', 'settings'],
  contador: ['dashboard', 'documents', 'upload', 'reviews', 'renditions', 'audit', 'observability'],
  ejecutivo: ['dashboard', 'documents', 'upload', 'renditions', 'observability'],
  auditor: ['dashboard', 'reviews', 'audit', 'observability']
};

const $ = (id) => document.getElementById(id);
const cloneTemplate = (id) => $(id).content.cloneNode(true);
const nowIso = () => new Date().toISOString();
const currentCompany = () => state.user?.company_id || $('loginTenant')?.value?.trim() || 'demo-company';
const role = () => state.user?.role || 'contador';

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function pretty(data) {
  return JSON.stringify(data, null, 2);
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    apiBase: state.apiBase,
    user: state.user,
    documents: state.documents,
    renditions: state.renditions,
    audit: state.audit,
    demoMode: state.demoMode
  }));
  if (state.tokens) localStorage.setItem(TOKEN_KEY, JSON.stringify(state.tokens));
}

function restore() {
  const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  const tokens = JSON.parse(localStorage.getItem(TOKEN_KEY) || 'null');
  Object.assign(state, {
    apiBase: saved.apiBase || state.apiBase,
    user: saved.user || null,
    documents: saved.documents || [],
    renditions: saved.renditions || [],
    audit: saved.audit || [],
    demoMode: Boolean(saved.demoMode),
    tokens
  });
}

function addAudit(action, resource, detail = '') {
  state.audit.unshift({
    at: nowIso(),
    user: state.user?.username || 'demo-user',
    role: role(),
    company: currentCompany(),
    action,
    resource,
    detail
  });
  state.audit = state.audit.slice(0, 100);
  persist();
}

function toast(message, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = message;
  $('toastRegion')?.appendChild(t);
  window.setTimeout(() => t.remove(), 4200);
}

async function api(path, options = {}, retry = true) {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (state.tokens?.access_token) headers.set('Authorization', `Bearer ${state.tokens.access_token}`);
  const res = await fetch(`${state.apiBase}${path}`, { ...options, headers });

  if (res.status === 401 && retry && state.tokens?.refresh_token) {
    const refreshed = await refreshToken();
    if (refreshed) return api(path, options, false);
  }

  const contentType = res.headers.get('content-type') || '';
  if (!res.ok) {
    const errBody = contentType.includes('application/json') ? await res.json() : await res.text();
    const detail = typeof errBody === 'string' ? errBody : errBody.detail || pretty(errBody);
    throw new Error(detail);
  }
  if (contentType.includes('application/json')) return res.json();
  return res;
}

async function refreshToken() {
  try {
    const payload = await fetch(`${state.apiBase}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: state.tokens.refresh_token })
    });
    if (!payload.ok) return false;
    state.tokens = await payload.json();
    persist();
    return true;
  } catch {
    return false;
  }
}

function normalizeDocument(raw, fileName = '') {
  const fields = raw.extracted_fields || raw.fields || raw.data || {};
  const confidence = Number(raw.confidence_score ?? raw.confidence ?? raw.ocr_confidence ?? fields.confidence ?? 0);
  return {
    id: raw.document_id || raw.id || `local-${crypto.randomUUID()}`,
    fileName: raw.original_filename || raw.filename || fileName || raw.file_name || 'documento',
    supplier: fields.supplier || fields.vendor || fields.provider || fields.emisor || raw.supplier || 'Por confirmar',
    issueDate: fields.issue_date || fields.date || raw.issue_date || '-',
    total: fields.total || fields.amount || raw.total || '-',
    currency: fields.currency || raw.currency || 'CLP',
    status: raw.status || 'RECEIVED',
    confidence: confidence > 1 ? confidence : Math.round(confidence * 100),
    responsible: raw.responsible || fields.responsible || '-',
    centerCost: raw.center_cost || fields.center_cost || '-',
    period: raw.period || fields.period || '-',
    raw,
    createdAt: raw.created_at || nowIso(),
    updatedAt: raw.updated_at || nowIso()
  };
}

function upsertDocument(doc) {
  const normalized = normalizeDocument(doc);
  const index = state.documents.findIndex((item) => item.id === normalized.id);
  if (index >= 0) state.documents[index] = { ...state.documents[index], ...normalized };
  else state.documents.unshift(normalized);
  persist();
}

function statusBadge(status) {
  const normalized = String(status || 'RECEIVED').toUpperCase();
  const cls = normalized.includes('REJECT') ? 'danger' : normalized.includes('REVIEW') || normalized.includes('WARN') ? 'warning' : normalized.includes('APPROV') || normalized.includes('COMPLET') ? 'success' : 'info';
  return `<span class="badge ${cls}">${escapeHtml(normalized)}</span>`;
}

function confidenceBadge(value) {
  const n = Number(value || 0);
  const cls = n >= 90 ? 'success' : n >= 75 ? 'warning' : 'danger';
  return `<span class="badge ${cls}">${Number.isFinite(n) && n > 0 ? `${n}%` : 'N/D'}</span>`;
}

function mountApp() {
  $('loginScreen').classList.add('hidden');
  $('appScreen').classList.remove('hidden');
  $('sessionUser').textContent = state.user?.username || 'demo-user';
  $('sessionCompany').textContent = currentCompany();
  $('roleBadge').textContent = role();
  $('roleBadge').className = `badge ${role() === 'auditor' ? 'warning' : 'success'}`;
  configureNavByRole();
  renderRoute(state.route || 'dashboard');
}

function configureNavByRole() {
  const allowed = routesByRole[role()] || routesByRole.contador;
  document.querySelectorAll('.nav-item').forEach((btn) => {
    btn.classList.toggle('hidden', !allowed.includes(btn.dataset.route));
  });
  if (!allowed.includes(state.route)) state.route = allowed[0] || 'dashboard';
}

function renderRoute(routeName) {
  const allowed = routesByRole[role()] || routesByRole.contador;
  if (!allowed.includes(routeName)) {
    toast('Ruta no permitida por rol', 'error');
    routeName = allowed[0] || 'dashboard';
  }
  state.route = routeName;
  window.location.hash = routeName;
  const [crumb, title] = pageMeta[routeName] || pageMeta.dashboard;
  $('breadcrumb').textContent = crumb;
  $('pageTitle').textContent = title;
  document.querySelectorAll('.nav-item').forEach((btn) => btn.classList.toggle('active', btn.dataset.route === routeName));
  $('pageHost').innerHTML = '';
  $('pageHost').appendChild(cloneTemplate(`${routeName}Template`));

  const renderers = {
    dashboard: renderDashboard,
    documents: renderDocuments,
    upload: renderUpload,
    reviews: renderReviews,
    renditions: renderRenditions,
    audit: renderAudit,
    observability: renderObservability,
    settings: renderSettings
  };
  renderers[routeName]?.();
  bindRouteJumps();
  persist();
}

function bindRouteJumps() {
  document.querySelectorAll('[data-route-jump]').forEach((btn) => {
    btn.addEventListener('click', () => renderRoute(btn.dataset.routeJump));
  });
}

function table(headers, rows) {
  if (!rows.length) return '<div class="empty-state"><strong>Sin datos</strong><span>No hay registros para mostrar.</span></div>';
  return `<table class="data-table"><thead><tr>${headers.map((h) => `<th>${escapeHtml(h)}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table>`;
}

function renderDashboard() {
  const pendingCount = state.reviews.length;
  const processed = state.documents.filter((d) => ['PROCESSED', 'COMPLETED', 'APPROVED'].includes(String(d.status).toUpperCase())).length;
  const metrics = { uploaded: state.documents.length, processed, pending: pendingCount, renditions: state.renditions.length };
  Object.entries(metrics).forEach(([key, value]) => {
    const target = document.querySelector(`[data-metric="${key}"]`);
    if (target) target.textContent = value;
  });

  const max = Math.max(state.documents.length, 1);
  const pipeline = [
    ['Recibido', state.documents.length],
    ['OCR/IA', processed],
    ['Revision', pendingCount],
    ['Aprobado', state.documents.filter((d) => String(d.status).toUpperCase().includes('APPROV')).length]
  ];
  $('pipelineBars').innerHTML = pipeline.map(([label, value]) => `
    <div class="pipeline-row"><span>${label}</span><div class="pipeline-track"><div class="pipeline-fill" style="width:${Math.min(100, (value / max) * 100)}%"></div></div><strong>${value}</strong></div>
  `).join('');

  const lowConfidence = state.documents.filter((d) => Number(d.confidence) && Number(d.confidence) < 80).length;
  const warnings = [
    [`${lowConfidence} documentos con baja confianza`, lowConfidence ? 'warn' : 'ok'],
    [`${pendingCount} revisiones pendientes`, pendingCount ? 'warn' : 'ok'],
    [`${state.health.readiness?.status || 'readiness pendiente'}`, state.health.readiness?.ok ? 'ok' : 'warn']
  ];
  $('riskList').innerHTML = warnings.map(([text, kind]) => `<div class="risk-item"><span class="status-dot ${kind}"></span>${escapeHtml(text)}</div>`).join('');

  const rows = state.documents.slice(0, 6).map((d) => `
    <tr><td class="mono">${escapeHtml(d.id)}</td><td>${escapeHtml(d.supplier)}</td><td>${escapeHtml(d.total)} ${escapeHtml(d.currency)}</td><td>${confidenceBadge(d.confidence)}</td><td>${statusBadge(d.status)}</td><td><button class="btn ghost small" data-open-doc="${escapeHtml(d.id)}">Abrir</button></td></tr>
  `);
  $('recentDocuments').innerHTML = table(['ID', 'Proveedor', 'Total', 'Confianza', 'Estado', 'Accion'], rows);
  document.querySelectorAll('[data-open-doc]').forEach((btn) => btn.addEventListener('click', () => { renderRoute('documents'); window.setTimeout(() => openDocumentDetail(btn.dataset.openDoc), 0); }));
}

function filteredDocuments() {
  const query = ($('documentSearch')?.value || $('globalSearch')?.value || '').toLowerCase();
  const status = $('documentStatusFilter')?.value || 'all';
  return state.documents.filter((doc) => {
    const haystack = `${doc.id} ${doc.fileName} ${doc.supplier} ${doc.status} ${doc.total}`.toLowerCase();
    return (!query || haystack.includes(query)) && (status === 'all' || String(doc.status).toUpperCase() === status.toUpperCase());
  });
}

function renderDocuments() {
  const draw = () => {
    const rows = filteredDocuments().map((d) => `
      <tr>
        <td><strong>${escapeHtml(d.fileName)}</strong><br><span class="muted mono">${escapeHtml(d.id)}</span></td>
        <td>${escapeHtml(d.supplier)}</td><td>${escapeHtml(d.issueDate)}</td><td>${escapeHtml(d.total)} ${escapeHtml(d.currency)}</td>
        <td>${confidenceBadge(d.confidence)}</td><td>${statusBadge(d.status)}</td>
        <td><button class="btn ghost small" data-open-doc="${escapeHtml(d.id)}">Ver</button> <button class="btn secondary small" data-process-doc="${escapeHtml(d.id)}">Procesar</button></td>
      </tr>`);
    $('documentsTable').innerHTML = table(['Archivo', 'Proveedor', 'Fecha', 'Total', 'Conf.', 'Estado', 'Acciones'], rows);
    document.querySelectorAll('[data-open-doc]').forEach((btn) => btn.addEventListener('click', () => openDocumentDetail(btn.dataset.openDoc)));
    document.querySelectorAll('[data-process-doc]').forEach((btn) => btn.addEventListener('click', () => processDocument(btn.dataset.processDoc)));
  };
  $('documentSearch').addEventListener('input', draw);
  $('documentStatusFilter').addEventListener('change', draw);
  $('exportDocumentsBtn').addEventListener('click', exportDocumentsCsv);
  draw();
}

async function openDocumentDetail(id) {
  const panel = $('documentDetailPanel');
  panel.classList.remove('hidden');
  panel.innerHTML = '<div class="empty-state"><strong>Cargando detalle...</strong></div>';
  let doc = state.documents.find((d) => d.id === id);
  try {
    const detail = await api(`/documents/${encodeURIComponent(id)}`);
    upsertDocument(detail);
    doc = state.documents.find((d) => d.id === id) || normalizeDocument(detail);
    addAudit('DOCUMENT_VIEWED', id, 'Detalle cargado desde API');
  } catch (err) {
    toast(`Detalle local: ${err.message}`, 'error');
  }
  if (!doc) return;
  panel.innerHTML = `
    <div class="panel-heading"><div><p class="eyebrow">Detalle documental</p><h3>${escapeHtml(doc.fileName)}</h3></div><div>${statusBadge(doc.status)} ${confidenceBadge(doc.confidence)}</div></div>
    <div class="document-detail-grid">
      <div class="document-preview"><div><strong>Preview documental</strong><p class="muted">${escapeHtml(doc.fileName)}</p><p class="mono">${escapeHtml(doc.id)}</p></div></div>
      <div class="detail-fields">
        ${detailField('Proveedor', doc.supplier)}${detailField('Fecha', doc.issueDate)}${detailField('Total', `${doc.total} ${doc.currency}`)}${detailField('Responsable', doc.responsible)}${detailField('Centro costo', doc.centerCost)}${detailField('Periodo', doc.period)}
        <div class="action-row"><button class="btn primary" data-route-jump="reviews">Enviar a revision</button><button class="btn secondary" data-process-doc="${escapeHtml(doc.id)}">Reprocesar</button></div>
      </div>
    </div>
    <pre class="output-json">${escapeHtml(pretty(doc.raw || doc))}</pre>`;
  bindRouteJumps();
  panel.querySelector('[data-process-doc]')?.addEventListener('click', () => processDocument(doc.id));
}

function detailField(label, value) {
  return `<div class="detail-field"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value || '-')}</strong></div>`;
}

async function processDocument(id) {
  try {
    const payload = await api(`/documents/${encodeURIComponent(id)}/process`, { method: 'POST' });
    upsertDocument(payload);
    addAudit('DOCUMENT_PROCESSED', id, 'Proceso solicitado desde consola');
    toast('Documento procesado');
    renderRoute('documents');
  } catch (err) {
    toast(`No se pudo procesar: ${err.message}`, 'error');
  }
}

function exportDocumentsCsv() {
  const rows = [['id', 'fileName', 'supplier', 'issueDate', 'total', 'currency', 'confidence', 'status'], ...filteredDocuments().map((d) => [d.id, d.fileName, d.supplier, d.issueDate, d.total, d.currency, d.confidence, d.status])];
  const csv = rows.map((r) => r.map((v) => `"${String(v ?? '').replaceAll('"', '""')}"`).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `captre-documentos-${Date.now()}.csv`; a.click(); URL.revokeObjectURL(url);
  addAudit('DOCUMENTS_EXPORTED', 'documents.csv', `${filteredDocuments().length} filas`);
}

function renderUpload() {
  const dropZone = $('dropZone');
  const fileInput = $('uploadFile');
  const addFiles = (files) => {
    for (const file of files) {
      const valid = ['application/pdf', 'image/png', 'image/jpeg'].includes(file.type);
      state.uploadQueue.push({ id: crypto.randomUUID(), file, name: file.name, size: file.size, type: file.type, status: valid ? 'READY' : 'INVALID', message: valid ? 'Listo para subir' : 'Formato no permitido' });
    }
    drawUploadQueue();
  };
  fileInput.addEventListener('change', () => addFiles(fileInput.files));
  ['dragenter', 'dragover'].forEach((evt) => dropZone.addEventListener(evt, (e) => { e.preventDefault(); dropZone.classList.add('dragging'); }));
  ['dragleave', 'drop'].forEach((evt) => dropZone.addEventListener(evt, (e) => { e.preventDefault(); dropZone.classList.remove('dragging'); }));
  dropZone.addEventListener('drop', (e) => addFiles(e.dataTransfer.files));
  $('uploadForm').addEventListener('submit', uploadQueuedFiles);
  drawUploadQueue();
}

function drawUploadQueue() {
  const target = $('uploadQueue');
  if (!target) return;
  if (!state.uploadQueue.length) {
    target.innerHTML = '<div class="empty-state"><strong>Cola vacia</strong><span>Agrega PDF o imagenes para comenzar.</span></div>';
    return;
  }
  target.innerHTML = state.uploadQueue.map((item) => `<div class="queue-item"><div><strong>${escapeHtml(item.name)}</strong><div class="queue-meta">${statusBadge(item.status)}<span class="badge neutral">${Math.round(item.size / 1024)} KB</span><span class="muted">${escapeHtml(item.message)}</span></div></div></div>`).join('');
}

async function uploadQueuedFiles(e) {
  e.preventDefault();
  for (const item of state.uploadQueue.filter((q) => q.status === 'READY' || q.status === 'ERROR')) {
    item.status = 'UPLOADING'; item.message = 'Subiendo a API'; drawUploadQueue();
    try {
      const fd = new FormData();
      fd.append('file', item.file);
      fd.append('tenant_id', currentCompany());
      if ($('uploadResponsible').value) fd.append('responsible', $('uploadResponsible').value);
      if ($('uploadPeriod').value) fd.append('period', $('uploadPeriod').value);
      if ($('uploadCenterCost').value) fd.append('center_cost', $('uploadCenterCost').value);
      const payload = await api('/documents/upload', { method: 'POST', body: fd });
      upsertDocument({ ...payload, original_filename: item.name, responsible: $('uploadResponsible').value, period: $('uploadPeriod').value, center_cost: $('uploadCenterCost').value });
      item.status = 'DONE'; item.message = 'Recibido y registrado';
      addAudit('DOCUMENT_UPLOADED', payload.document_id || item.name, item.name);
      toast(`${item.name} cargado`);
    } catch (err) {
      item.status = 'ERROR'; item.message = err.message;
      toast(`Error subiendo ${item.name}: ${err.message}`, 'error');
    }
    drawUploadQueue();
  }
  persist();
}

async function renderReviews() {
  $('loadReviewsBtn').addEventListener('click', loadReviews);
  await loadReviews();
}

async function loadReviews() {
  try {
    const payload = await api('/reviews/pending');
    state.reviews = payload.items || [];
    addAudit('REVIEWS_LOADED', 'reviews/pending', `${state.reviews.length} pendientes`);
  } catch (err) {
    toast(`Usando cola local: ${err.message}`, 'error');
    state.reviews = state.reviews.length ? state.reviews : state.documents.filter((d) => String(d.status).toUpperCase().includes('REVIEW')).map((d) => ({ document_id: d.id, reason: 'Confianza o regla requiere revision', updated_at: d.updatedAt }));
  }
  drawReviews();
}

function drawReviews() {
  const target = $('reviewsQueue');
  if (!target) return;
  if (!state.reviews.length) {
    target.innerHTML = '<div class="empty-state"><strong>Sin pendientes</strong><span>No hay documentos en revision.</span></div>';
    return;
  }
  target.innerHTML = state.reviews.map((r) => `<div class="review-item ${state.selectedReviewId === r.document_id ? 'active' : ''}" data-review-id="${escapeHtml(r.document_id)}"><strong>${escapeHtml(r.document_id)}</strong><span class="muted">${escapeHtml(r.reason || 'Revision requerida')}</span><div class="queue-meta"><span class="badge warning">Prioridad</span><span class="mono muted">${escapeHtml(r.updated_at || '-')}</span></div></div>`).join('');
  document.querySelectorAll('[data-review-id]').forEach((item) => item.addEventListener('click', () => openReview(item.dataset.reviewId)));
}

async function openReview(id) {
  state.selectedReviewId = id;
  drawReviews();
  const panel = $('reviewDecisionPanel');
  panel.innerHTML = '<div class="empty-state"><strong>Cargando revision...</strong></div>';
  let detail = state.reviews.find((r) => r.document_id === id) || { document_id: id };
  try {
    detail = await api(`/reviews/${encodeURIComponent(id)}`);
    addAudit('REVIEW_VIEWED', id, 'Detalle revision cargado');
  } catch (err) {
    toast(`Detalle local: ${err.message}`, 'error');
  }
  const documentDetail = detail.document || state.documents.find((d) => d.id === id) || {};
  const reasons = detail.warnings || detail.reasons || [detail.reason || 'Revision requerida por politica de confianza o reglas contables'];
  panel.innerHTML = `
    <div class="panel-heading"><div><p class="eyebrow">Decision asistida</p><h3>${escapeHtml(id)}</h3></div>${statusBadge(documentDetail.status || 'REVIEW_REQUIRED')}</div>
    <div class="decision-grid">
      <div><h4>Motivos</h4><ul class="reason-list">${reasons.map((r) => `<li>${escapeHtml(typeof r === 'string' ? r : pretty(r))}</li>`).join('')}</ul></div>
      <div><h4>Datos extraidos</h4><div class="detail-fields">${detailField('Proveedor', documentDetail.supplier || documentDetail.provider || '-')} ${detailField('Total', documentDetail.total || '-')} ${detailField('Confianza', documentDetail.confidence || documentDetail.confidence_score || '-')}</div></div>
    </div>
    <form id="reviewActionForm" class="page-stack">
      <div class="form-grid"><label>Reviewer<input id="reviewerId" value="${escapeHtml(state.user?.username || 'reviewer-ui')}" required /></label><label>Motivo<input id="reviewReason" value="Validado desde RendiFlow IA" required /></label></div>
      <div class="action-row"><button class="btn primary" data-decision="approve" type="submit">Aprobar</button><button class="btn danger" data-decision="reject" type="submit">Rechazar</button><button class="btn ghost" data-overrides="true" type="button">Guardar overrides</button></div>
    </form>
    <pre class="output-json">${escapeHtml(pretty(detail))}</pre>`;
  let decision = 'approve';
  panel.querySelectorAll('[data-decision]').forEach((btn) => btn.addEventListener('click', () => { decision = btn.dataset.decision; }));
  $('reviewActionForm').addEventListener('submit', (e) => submitReviewAction(e, id, decision));
  panel.querySelector('[data-overrides]')?.addEventListener('click', () => submitOverrides(id));
}

async function submitReviewAction(e, id, decision) {
  e.preventDefault();
  try {
    const payload = await api(`/reviews/${encodeURIComponent(id)}/${decision}`, {
      method: 'POST',
      body: JSON.stringify({ reviewer_id: $('reviewerId').value, reason: $('reviewReason').value, overrides: {} })
    });
    addAudit(`REVIEW_${decision.toUpperCase()}`, id, $('reviewReason').value);
    toast(`Revision ${decision === 'approve' ? 'aprobada' : 'rechazada'}`);
    upsertDocument(payload.document || { document_id: id, status: decision === 'approve' ? 'APPROVED' : 'REJECTED' });
    await loadReviews();
  } catch (err) {
    toast(`No se pudo resolver: ${err.message}`, 'error');
  }
}

async function submitOverrides(id) {
  try {
    await api(`/reviews/${encodeURIComponent(id)}/overrides`, {
      method: 'POST',
      body: JSON.stringify({ reviewer_id: $('reviewerId').value, reason: $('reviewReason').value, overrides: {} })
    });
    addAudit('REVIEW_OVERRIDES', id, $('reviewReason').value);
    toast('Overrides guardados');
  } catch (err) {
    toast(`No se pudo guardar overrides: ${err.message}`, 'error');
  }
}

function renderRenditions() {
  $('renditionForm').addEventListener('submit', generateRendition);
  drawRenditionHistory();
  drawRenditionPreview();
}

function drawRenditionPreview() {
  const docs = state.documents.filter((d) => ['APPROVED', 'COMPLETED', 'PROCESSED'].includes(String(d.status).toUpperCase())).slice(0, 8);
  $('renditionPreview').innerHTML = `<div class="data-table-wrap">${table(['Documento', 'Proveedor', 'Total', 'Estado'], docs.map((d) => `<tr><td class="mono">${escapeHtml(d.id)}</td><td>${escapeHtml(d.supplier)}</td><td>${escapeHtml(d.total)} ${escapeHtml(d.currency)}</td><td>${statusBadge(d.status)}</td></tr>`))}</div>`;
}

async function generateRendition(e) {
  e.preventDefault();
  const request = {
    tenant_id: currentCompany(),
    period: $('renditionPeriod').value,
    responsible: $('renditionResponsible').value || null,
    center_cost: $('renditionCenterCost').value || null,
    template_version: '01-rendicion-gastos-2025'
  };
  if (state.demoMode) {
    const local = { rendition_id: `local-${crypto.randomUUID()}`, ...request, status: 'LOCAL_PREVIEW', warnings_count: 0, created_at: nowIso() };
    state.renditions.unshift(local);
    addAudit('RENDITION_PREVIEW_LOCAL', local.rendition_id, 'Modo demo: generacion local sin llamada API');
    persist();
    drawRenditionHistory();
    toast('Rendicion local generada en modo demo', 'success');
    return;
  }
  try {
    const payload = await api('/renditions/generate/by-filter', { method: 'POST', body: JSON.stringify(request) });
    state.renditions.unshift(payload);
    addAudit('RENDITION_GENERATED', payload.rendition_id || 'rendition', request.period);
    toast('Rendicion generada');
  } catch (err) {
    if (String(err.message || '').toLowerCase().includes('no documents found for provided filters')) {
      const local = { rendition_id: `local-${crypto.randomUUID()}`, ...request, status: 'EMPTY_RESULT', warnings_count: 0, created_at: nowIso() };
      state.renditions.unshift(local);
      addAudit('RENDITION_EMPTY_RESULT', local.rendition_id, 'Sin documentos para filtros indicados');
      toast('No hay documentos para esos filtros', 'error');
      persist();
      drawRenditionHistory();
      return;
    }
    const local = { rendition_id: `local-${crypto.randomUUID()}`, ...request, status: 'LOCAL_PREVIEW', warnings_count: 0, created_at: nowIso() };
    state.renditions.unshift(local);
    addAudit('RENDITION_PREVIEW_LOCAL', local.rendition_id, err.message);
    toast(`Rendicion local creada: ${err.message}`, 'error');
  }
  persist();
  drawRenditionHistory();
}

function drawRenditionHistory() {
  const rows = state.renditions.map((r) => `<tr><td class="mono">${escapeHtml(r.rendition_id)}</td><td>${escapeHtml(r.period)}</td><td>${escapeHtml(r.documents_count || r.document_count || '-')}</td><td>${escapeHtml(r.warnings_count ?? 0)}</td><td>${statusBadge(r.status || 'GENERATED')}</td><td><button class="btn ghost small" data-download-rendition="${escapeHtml(r.rendition_id)}">Descargar</button></td></tr>`);
  $('renditionsHistory').innerHTML = table(['ID', 'Periodo', 'Docs', 'Warnings', 'Estado', 'Acciones'], rows);
  document.querySelectorAll('[data-download-rendition]').forEach((btn) => btn.addEventListener('click', () => downloadRendition(btn.dataset.downloadRendition)));
}

async function downloadRendition(id) {
  try {
    const response = await api(`/renditions/${encodeURIComponent(id)}/download`, {}, false);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `rendition_${id}.xlsx`; a.click(); URL.revokeObjectURL(url);
    addAudit('RENDITION_DOWNLOADED', id, 'XLSX descargado');
  } catch (err) {
    toast(`No se pudo descargar: ${err.message}`, 'error');
  }
}

function renderAudit() {
  const draw = () => {
    const rows = state.audit.map((a) => `<tr><td class="mono">${escapeHtml(a.at)}</td><td>${escapeHtml(a.user)}</td><td>${escapeHtml(a.action)}</td><td class="mono">${escapeHtml(a.resource)}</td><td>${escapeHtml(a.company)}</td><td>${escapeHtml(a.detail)}</td></tr>`);
    $('auditTable').innerHTML = table(['Fecha', 'Usuario', 'Accion', 'Recurso', 'Empresa', 'Detalle'], rows);
  };
  $('clearAuditBtn').addEventListener('click', () => { state.audit = []; persist(); draw(); });
  draw();
}

async function renderObservability() {
  $('runHealthBtn').addEventListener('click', runHealthChecks);
  await runHealthChecks();
}

async function runHealthChecks() {
  const checks = ['health', 'liveness', 'readiness'];
  const results = {};
  for (const check of checks) {
    try {
      const payload = await api(`/${check}`, {}, false);
      results[check] = { ok: true, status: payload.status || 'ok', payload };
    } catch (err) {
      results[check] = { ok: false, status: err.message, payload: null };
    }
  }
  state.health = results;
  persist();
  if ($('healthGrid')) {
    $('healthGrid').innerHTML = checks.map((check) => `<div class="health-card"><span class="status-dot ${results[check].ok ? 'ok' : 'fail'}"></span><strong>${check}</strong><p class="muted">${escapeHtml(results[check].status)}</p></div>`).join('');
  }
  if ($('diagnosticOutput')) {
    $('diagnosticOutput').textContent = pretty({ apiBase: state.apiBase, company: currentCompany(), role: role(), checks: results });
  }
  addAudit('OBSERVABILITY_CHECKED', 'health-suite', checks.map((c) => `${c}:${results[c].ok ? 'ok' : 'fail'}`).join(','));
}

function renderSettings() {
  $('settingsContent').innerHTML = [
    ['Empresa activa', currentCompany()],
    ['Rol operativo', role()],
    ['API base', state.apiBase],
    ['Rutas permitidas', (routesByRole[role()] || []).join(', ')],
    ['Politica UI', 'Rutas protegidas, feedback visual, auditoria local y manejo de errores legible']
  ].map(([label, value]) => `<div class="setting-row"><strong>${escapeHtml(label)}</strong><span class="muted">${escapeHtml(value)}</span></div>`).join('');
}

function bindGlobalEvents() {
  $('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    state.apiBase = $('apiBaseInput').value.replace(/\/$/, '');
    $('loginMessage').textContent = 'Validando credenciales...';
    try {
      const tokens = await fetch(`${state.apiBase}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: $('loginUser').value.trim(), password: $('loginPassword').value })
      }).then(async (res) => {
        if (!res.ok) throw new Error(await res.text());
        return res.json();
      });
      state.tokens = tokens;
      const me = await api('/auth/me');
      state.user = me;
      state.demoMode = false;
      addAudit('AUTH_LOGIN', me.username, 'Login API exitoso');
      persist();
      mountApp();
      toast('Sesion iniciada');
    } catch (err) {
      $('loginMessage').textContent = `No fue posible autenticar: ${err.message}`;
    }
  });

  $('demoLoginBtn').addEventListener('click', () => {
    state.apiBase = $('apiBaseInput').value.replace(/\/$/, '');
    state.tokens = null;
    state.user = { user_id: 'demo', username: $('loginUser').value.trim() || 'demo@captre.local', role: 'contador', company_id: $('loginTenant').value.trim() || 'demo-company' };
    state.demoMode = true;
    seedDemoData();
    addAudit('AUTH_DEMO_LOGIN', state.user.username, 'Modo demo activado');
    persist();
    mountApp();
    toast('Modo demo activado');
  });

  $('sideNav').addEventListener('click', (e) => {
    const btn = e.target.closest('.nav-item');
    if (!btn) return;
    renderRoute(btn.dataset.route);
    $('appScreen').querySelector('.sidebar').classList.remove('open');
  });
  $('refreshAllBtn').addEventListener('click', refreshCurrentData);
  $('logoutBtn').addEventListener('click', logout);
  $('mobileMenuBtn').addEventListener('click', () => $('appScreen').querySelector('.sidebar').classList.toggle('open'));
  $('globalSearch').addEventListener('keydown', (e) => { if (e.key === 'Enter') renderRoute('documents'); });
  window.addEventListener('hashchange', () => {
    const route = window.location.hash.replace('#', '');
    if (route && route !== state.route) renderRoute(route);
  });
}

async function refreshCurrentData() {
  if (state.route === 'reviews') await loadReviews();
  else if (state.route === 'observability') await runHealthChecks();
  else {
    await Promise.allSettled([loadReviews(), runHealthChecks()]);
    renderRoute(state.route);
  }
  toast('Datos actualizados');
}

function logout() {
  addAudit('AUTH_LOGOUT', state.user?.username || 'unknown', 'Sesion cerrada');
  state.user = null;
  state.tokens = null;
  state.demoMode = false;
  localStorage.removeItem(TOKEN_KEY);
  persist();
  $('appScreen').classList.add('hidden');
  $('loginScreen').classList.remove('hidden');
}

function seedDemoData() {
  if (state.documents.length) return;
  state.documents = [
    normalizeDocument({ document_id: 'DOC-901', original_filename: 'factura_901.pdf', status: 'REVIEW_REQUIRED', confidence_score: 0.72, extracted_fields: { supplier: 'ACME Ltda', issue_date: '2026-05-16', total: '$980.000', currency: 'CLP', responsible: 'Ana', center_cost: 'FINANZAS', period: '2026-05' } }),
    normalizeDocument({ document_id: 'DOC-899', original_filename: 'invoice_global.pdf', status: 'WARNING', confidence_score: 0.81, extracted_fields: { supplier: 'Global Inc', issue_date: '2026-05-15', total: 'USD 120', currency: 'USD', responsible: 'Carlos', center_cost: 'OPS', period: '2026-05' } }),
    normalizeDocument({ document_id: 'DOC-870', original_filename: 'boleta_870.jpg', status: 'APPROVED', confidence_score: 0.98, extracted_fields: { supplier: 'Demo SpA', issue_date: '2026-05-14', total: '$45.900', currency: 'CLP', responsible: 'Ana', center_cost: 'VENTAS', period: '2026-05' } })
  ];
  state.reviews = [
    { document_id: 'DOC-901', reason: 'Confianza OCR baja y proveedor requiere confirmacion', updated_at: nowIso() },
    { document_id: 'DOC-899', reason: 'Moneda internacional requiere validacion contable', updated_at: nowIso() }
  ];
}

restore();
bindGlobalEvents();
if (state.user) mountApp();
