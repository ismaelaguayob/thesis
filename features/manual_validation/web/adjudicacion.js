'use strict';
const $ = (id) => document.getElementById(id);
const state = { items: [], filtered: [], position: null, data: null, dirty: false };
const stanceLabels = { support: 'Apoyo', oppose: 'Rechazo' };
const decisionLabels = {
  support: 'Apoyo', oppose: 'Rechazo', both: 'Apoyo y rechazo',
  concept_absent: 'No corresponde', unresolved: 'Sin resolver',
};

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text != null) element.textContent = text;
  if (className) element.className = className;
  return element;
}
async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json' } });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || `HTTP ${response.status}`);
  return body;
}
function notify(message, error = false) {
  $('toast').textContent = message;
  $('toast').classList.toggle('error', error);
  $('toast').classList.remove('hidden');
  clearTimeout(notify.timer);
  notify.timer = setTimeout(() => $('toast').classList.add('hidden'), 5000);
}
function discardChanges() {
  return !state.dirty || window.confirm('Hay cambios sin guardar. ¿Quieres descartarlos?');
}

function renderTarget(text, codings) {
  // Offsets count Unicode code points, as in the rest of the application.
  const chars = Array.from(text);
  const spans = codings.flatMap(c => c.annotations.map(a => ({ ...a, label: c.label })));
  const points = new Set([0, chars.length]);
  spans.forEach(s => { points.add(s.start_char); points.add(s.end_char); });
  const bounds = [...points].sort((a, b) => a - b);
  const fragment = document.createDocumentFragment();
  for (let i = 0; i + 1 < bounds.length; i++) {
    const [start, end] = [bounds[i], bounds[i + 1]];
    const value = chars.slice(start, end).join('');
    const labels = [...new Set(spans.filter(s => s.start_char <= start && s.end_char >= end).map(s => s.label))].sort();
    if (!labels.length) { fragment.append(document.createTextNode(value)); continue; }
    const mark = node('mark', value, labels.length > 1 ? 'adj-mark-ab' : `adj-mark-${labels[0].toLowerCase()}`);
    mark.title = `Evidencia de ${labels.join(' y ')}`;
    fragment.append(mark);
  }
  $('target-text').replaceChildren(fragment);
}

function renderCodings(codings) {
  $('codings').replaceChildren();
  codings.forEach(coding => {
    const section = node('article', null, 'adj-coding');
    const title = node('h3');
    title.append(node('span', null, `adj-swatch ${coding.label.toLowerCase()}`), `Codificación ${coding.label}`);
    section.append(title);
    if (!coding.annotations.length) {
      section.append(node('p', 'No codificó este concepto en el bloque.'));
    }
    coding.annotations.forEach(a => {
      // En la segunda ronda la postura de los modelos se oculta.
      if (a.stance) section.append(node('p', stanceLabels[a.stance] || a.stance, 'adj-stance'));
      section.append(node('blockquote', a.text));
      if (a.justification) section.append(node('p', `Justificación: ${a.justification}`));
      if (a.confidence) section.append(node('p', `Confianza: ${a.confidence}`));
    });
    $('codings').append(section);
  });
}

function renderItem() {
  const d = state.data;
  $('position').textContent = `Caso ${state.position + 1} de ${state.filtered.length} (n.º ${d.case_index + 1} de ${d.n_cases})`;
  $('target-meta').textContent = `Ley ${d.law_number} · sesión ${d.session}`;
  $('previous-text').textContent = d.previous_text || '(sin bloque anterior)';
  $('next-text').textContent = d.next_text || '(sin bloque siguiente)';
  renderTarget(d.target_text, d.codings);
  $('concept-label').textContent = d.concept.label;
  $('concept-definition').textContent = d.concept.definition || '';
  $('concept-anchor').textContent = d.concept.orientation_anchor || '';
  const criteria = $('concept-criteria');
  criteria.replaceChildren();
  [['Incluye', d.concept.include], ['Excluye', d.concept.exclude]].forEach(([title, list]) => {
    if (!list || !list.length) return;
    criteria.append(node('h3', title));
    const ul = node('ul');
    list.forEach(entry => ul.append(node('li', entry)));
    criteria.append(ul);
  });
  renderCodings(d.codings);
  const saved = d.decision;
  document.querySelectorAll('input[name="decision"]').forEach(input => { input.checked = saved?.decision === input.value; });
  $('note').value = saved?.note || '';
  if (saved?.reviewer) $('reviewer').value = saved.reviewer;
  $('save-status').textContent = saved ? `Guardado (revisión ${saved.revision})` : 'Sin decisión';
  $('previous').disabled = state.position === 0;
  $('next').disabled = state.position >= state.filtered.length - 1;
  state.dirty = false;
}

async function loadPosition(position) {
  state.position = position;
  const item = state.filtered[position];
  $('case-select').value = String(item.case_index);
  state.data = await api(`/api/stance/items/${item.case_index}`);
  renderItem();
}

function applyFilters(keepIndex = null) {
  const status = $('status-filter').value;
  const concept = $('concept-filter').value;
  state.filtered = state.items.filter(item =>
    (concept === 'all' || item.concept_id === concept)
    && (status === 'all' || (status === 'pending' ? !item.decision : Boolean(item.decision))));
  const select = $('case-select');
  select.replaceChildren();
  state.filtered.forEach(item => select.add(new Option(
    `${item.case_index + 1}. ${item.concept_label} · Ley ${item.law_number}${item.decision ? ` · ${decisionLabels[item.decision]}` : ''}`,
    String(item.case_index))));
  const decided = state.items.filter(item => item.decision).length;
  $('queue-summary').textContent = `${decided} de ${state.items.length} casos adjudicados`;
  const empty = !state.filtered.length;
  $('empty-state').classList.toggle('hidden', !empty);
  $('workspace').classList.toggle('hidden', empty);
  if (empty) {
    $('empty-state').textContent = status === 'pending' ? 'No quedan casos pendientes con este filtro.' : 'No hay casos con este filtro.';
    return null;
  }
  const position = keepIndex == null ? 0 : Math.max(0, state.filtered.findIndex(item => item.case_index === keepIndex));
  return loadPosition(position);
}

async function refresh(keepIndex = null) {
  const data = await api('/api/stance/items');
  state.items = data.items;
  const concepts = [...new Map(data.items.map(item => [item.concept_id, item.concept_label])).entries()];
  const select = $('concept-filter');
  const current = select.value;
  select.replaceChildren(new Option('Todos', 'all'));
  concepts.forEach(([id, label]) => select.add(new Option(label, id)));
  select.value = concepts.some(([id]) => id === current) ? current : 'all';
  await applyFilters(keepIndex);
}

async function save(event) {
  event.preventDefault();
  const choice = document.querySelector('input[name="decision"]:checked');
  if (!choice) { notify('Selecciona una decisión', true); return; }
  const index = state.data.case_index;
  await api(`/api/stance/items/${index}`, {
    method: 'PUT',
    body: JSON.stringify({ decision: choice.value, note: $('note').value,
      reviewer: $('reviewer').value, revision: state.data.decision?.revision || 0 }),
  });
  state.dirty = false;
  notify('Decisión guardada');
  const nextPending = state.items.find(item => !item.decision && item.case_index > index);
  await refresh(nextPending ? nextPending.case_index : index);
}

function guarded(action) {
  return async () => { try { if (discardChanges()) await action(); } catch (error) { notify(error.message, true); } };
}
document.addEventListener('DOMContentLoaded', () => {
  $('decision-form').addEventListener('input', () => { state.dirty = true; });
  $('decision-form').addEventListener('submit', event => save(event).catch(error => notify(error.message, true)));
  $('status-filter').addEventListener('change', guarded(() => applyFilters()));
  $('concept-filter').addEventListener('change', guarded(() => applyFilters()));
  $('refresh').addEventListener('click', guarded(() => refresh(state.data?.case_index ?? null)));
  $('case-select').addEventListener('change', guarded(() => loadPosition(
    state.filtered.findIndex(item => String(item.case_index) === $('case-select').value))));
  $('previous').addEventListener('click', guarded(() => loadPosition(state.position - 1)));
  $('next').addEventListener('click', guarded(() => loadPosition(state.position + 1)));
  refresh().catch(error => notify(error.message, true));
});
