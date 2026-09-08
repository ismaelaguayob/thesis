'use strict';
const $ = (id) => document.getElementById(id);
const reviewState = { runId: null, items: [], filtered: [], index: null, data: null, dirty: false };
const verdictLabels = { accepted: 'Aceptar', needs_changes: 'Requiere cambios', discard: 'Descartar' };
const issueLabels = { span: 'Span', concept: 'Código', stance: 'Orientación', omission: 'Omisión', justification: 'Justificación', context: 'Contexto', segmentation: 'Segmentación', other: 'Otro' };
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
function discardChanges() { return !reviewState.dirty || window.confirm('Hay cambios sin guardar. ¿Quieres descartarlos?'); }
function verdictSelect(value) {
  const select = node('select');
  select.required = true;
  select.add(new Option('Seleccionar…', ''));
  Object.entries(verdictLabels).forEach(([key, label]) => select.add(new Option(label, key)));
  select.value = value || '';
  select.addEventListener('change', () => { reviewState.dirty = true; });
  return select;
}
function codeInfo(annotation) {
  const concepts = reviewState.data.codebook.concepts;
  const index = concepts.findIndex(c => c.id === annotation.concept_id);
  return { color: `llm-color-${index < 0 ? 14 : index}`, code: annotation.concept_id || 'review',
    label: index < 0 ? `Revisar: ${annotation.proposed_concept || 'concepto ausente'}` : concepts[index].label };
}
function focusAnnotation(id) {
  const target = document.getElementById(`annotation-${id}`);
  if (target) { target.scrollIntoView({ behavior: 'smooth', block: 'center' }); target.focus({ preventScroll: true }); }
}
function renderHighlight(text, annotations) {
  // Backend offsets count Unicode code points, not JavaScript UTF-16 code units.
  const chars = Array.from(text);
  const points = new Set([0, chars.length]);
  annotations.forEach(a => { points.add(a.span.start_char); points.add(a.span.end_char); });
  const boundaries = [...points].sort((a, b) => a - b);
  const fragment = document.createDocumentFragment();
  for (let i = 0; i + 1 < boundaries.length; i++) {
    const [start, end] = [boundaries[i], boundaries[i + 1]];
    const covering = annotations.filter(a => a.span.start_char <= start && a.span.end_char >= end);
    const value = chars.slice(start, end).join('');
    if (!covering.length) { fragment.append(document.createTextNode(value)); continue; }
    const mark = node('mark', value, `llm-mark ${codeInfo(covering[0]).color}`);
    const label = covering.map(a => `${codeInfo(a).code} · ${a.stance === 'support' ? 'Apoyo' : 'Rechazo'}`).join(' / ');
    mark.title = label;
    mark.setAttribute('aria-label', `${value}. ${label}`);
    mark.setAttribute('role', 'button'); mark.tabIndex = 0;
    mark.dataset.overlap = String(covering.length > 1);
    mark.addEventListener('click', () => focusAnnotation(covering[0].annotation_id));
    mark.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); focusAnnotation(covering[0].annotation_id); } });
    fragment.append(mark);
  }
  $('target-text').replaceChildren(fragment);
  $('code-legend').replaceChildren();
  annotations.forEach((a, i) => {
    const info = codeInfo(a);
    const button = node('button', `${i + 1}. ${info.code} · ${a.stance === 'support' ? 'Apoyo' : 'Rechazo'}`, info.color);
    button.type = 'button'; button.title = info.label;
    button.addEventListener('click', () => focusAnnotation(a.annotation_id));
    $('code-legend').append(button);
  });
}
function renderAnnotations(annotations, saved) {
  $('annotations').replaceChildren();
  if (!annotations.length) $('annotations').append(node('p', 'Sin spans válidos. Revisa la decisión global y posibles omisiones.'));
  annotations.forEach((a, i) => {
    const section = node('article', null, 'llm-annotation');
    section.id = `annotation-${a.annotation_id}`; section.tabIndex = -1;
    section.dataset.annotationId = a.annotation_id;
    const info = codeInfo(a), j = a.justification;
    section.append(node('span', `${i + 1}. ${info.code}`, `llm-code ${info.color}`));
    section.append(node('h3', `${info.label} · ${a.stance === 'support' ? 'Apoyo' : 'Rechazo'}`));
    section.append(node('blockquote', a.span.text));
    const concept = reviewState.data.codebook.concepts.find(c => c.id === a.concept_id);
    let rule = j.criterion_reference;
    if (concept) rule += ': ' + (j.criterion_reference.startsWith('include:')
      ? concept.include[Number(j.criterion_reference.split(':')[1]) - 1] : concept[j.criterion_reference]);
    section.append(node('p', `Criterio: ${rule}`));
    section.append(node('p', `Código: ${j.coding}`), node('p', `Orientación: ${j.stance}`));
    j.alternatives.forEach(alt => section.append(node('p', `Alternativa ${alt.concept_id}: ${alt.reason}`)));
    j.context_evidence.forEach(context => section.append(node('p', `Contexto ${context.source === 'previous_context' ? 'anterior' : 'siguiente'}: “${context.text}”`)));
    if (j.uncertainty) section.append(node('p', `Ambigüedad: ${j.uncertainty}`));
    const old = saved.find(entry => entry.annotation_id === a.annotation_id);
    const label = node('label', `Juicio sobre la anotación ${i + 1}`);
    label.append(verdictSelect(old?.verdict)); section.append(label);
    const noteLabel = node('label', 'Comentario o código propuesto');
    const note = node('textarea'); note.rows = 2; note.maxLength = 2000; note.value = old?.note || '';
    note.addEventListener('input', () => { reviewState.dirty = true; });
    noteLabel.append(note); section.append(noteLabel);
    $('annotations').append(section);
  });
}
function renderItem() {
  const { item, request, result, codebook, manifest, review } = reviewState.data;
  const output = result?.normalized;
  const annotations = output?.annotations || [];
  const response = result?.response;
  const usage = response?.usage;
  $('model-meta').textContent = [
    `Modelo solicitado: ${request.body.model}`, `Modelo devuelto: ${response?.model || 'sin respuesta'}`,
    `Esfuerzo: ${request.body.reasoning.effort}`, `Libro: ${codebook.version}`,
    `Estado: ${result?.status || 'pending'}`, `Prompt: ${manifest.spec.prompt_sha256.slice(0, 12)}`,
    usage ? `Tokens: ${usage.input_tokens} entrada / ${usage.output_tokens} salida` : '',
  ].filter(Boolean).join(' · ');
  ['previous', 'next'].forEach(side => {
    const context = item[`${side}_context`];
    $(`${side}-text`).textContent = context?.content || 'No hay contexto disponible en esta sesión.';
    $(`${side}-relation`).textContent = context ? (context.same_utterance ? 'Misma intervención' : 'Otra intervención') : '';
  });
  $('target-meta').textContent = `Ley ${item.law_number} · sesión ${item.document_uri.split('/').pop()} · ${item.date} · párrafos ${item.paragraph_start}–${item.paragraph_end} · ${item.n_words} palabras`;
  renderHighlight(item.content, annotations);
  $('raw-input').textContent = JSON.stringify(request.body, null, 2);
  $('raw-output').textContent = result?.output_text || 'Todavía no hay texto de salida.';
  $('raw-response').textContent = JSON.stringify(response, null, 2);
  $('decision').textContent = output ? (output.decision === 'statements' ? `${annotations.length} declaraciones` : 'Sin declaraciones codificables') : 'Sin decisión validada';
  $('decision-justification').textContent = output?.decision_justification || '';
  $('limitations').textContent = output?.limitations ? `Límites: ${output.limitations}` : '';
  $('flags').textContent = [output?.needs_human_review ? 'El modelo solicita revisión humana.' : '', ...(output?.quality_flags || [])].filter(Boolean).join(' · ');
  $('execution-errors').textContent = (result?.validation_errors || []).join('\n');
  renderAnnotations(annotations, review?.annotations || []);
  $('codebook').replaceChildren();
  codebook.concepts.forEach(c => {
    const details = node('details'); details.append(node('summary', `${c.id} · ${c.label}`));
    details.append(node('p', c.definition), node('p', `Ancla: ${c.orientation_anchor || ''}`));
    for (const [key, label] of [['include', 'Incluir'], ['exclude', 'Excluir']]) {
      details.append(node('h3', label)); const list = node('ol');
      (c[key] || []).forEach(text => list.append(node('li', text))); details.append(list);
    }
    $('codebook').append(details);
  });
  $('verdict').value = review?.verdict || '';
  $('reviewer').value = review?.reviewer || sessionStorage.getItem('llm-reviewer') || '';
  $('review-note').value = review?.note || '';
  $('issues').querySelectorAll('input').forEach(input => { input.checked = (review?.issues || []).includes(input.value); });
  $('save-status').textContent = review ? `Revisión guardada · versión ${review.revision}` : 'Sin revisión guardada';
  $('save').disabled = !result;
  reviewState.dirty = false;
  const position = reviewState.filtered.findIndex(row => row.sample_index === reviewState.index);
  $('position').textContent = `Bloque ${reviewState.index + 1} de ${manifest.sample_size} · ${position + 1} de ${reviewState.filtered.length} en el filtro`;
  $('previous').disabled = position <= 0;
  $('next').disabled = position < 0 || position >= reviewState.filtered.length - 1;
  $('review-workspace').classList.remove('hidden');
}
async function loadItem(index) {
  reviewState.data = await api(`/api/llm/runs/${reviewState.runId}/items/${index}`);
  reviewState.index = index; $('item-select').value = String(index); renderItem();
}
async function applyFilters() {
  const law = $('law-filter').value, filter = $('item-filter').value;
  reviewState.filtered = reviewState.items.filter(item => (law === 'all' || item.law_number === law) && (
    filter === 'all' || (filter === 'unreviewed' && !item.review_verdict) ||
    (filter === 'flagged' && item.needs_human_review) || (filter === 'no_statements' && item.decision === 'no_statements') ||
    (filter === 'errors' && !['pending', 'completed'].includes(item.status))));
  $('item-select').replaceChildren();
  reviewState.filtered.forEach(item => $('item-select').add(new Option(
    `${item.sample_index + 1} · Ley ${item.law_number} · sesión ${item.session} · ${item.n_annotations} spans · ${item.review_verdict || item.status}`, String(item.sample_index))));
  const selected = reviewState.filtered.find(i => i.sample_index === reviewState.index) || reviewState.filtered[0];
  $('empty-state').classList.toggle('hidden', Boolean(selected));
  if (selected) await loadItem(selected.sample_index);
  else { $('review-workspace').classList.add('hidden'); $('empty-state').textContent = 'No hay bloques que cumplan este filtro.'; }
}
async function loadRun() {
  reviewState.runId = $('run-select').value;
  if (!reviewState.runId) return;
  const data = await api(`/api/llm/runs/${reviewState.runId}/items`);
  reviewState.items = data.items;
  $('run-summary').textContent = `${data.manifest.run_id} · ${data.manifest.spec.sampling.selected_interventions} intervenciones · ${data.items.length} bloques · ${data.items.filter(i => i.review_verdict).length} revisados`;
  const previousLaw = $('law-filter').value;
  $('law-filter').replaceChildren(new Option('Todas las leyes', 'all'));
  [...new Set(data.items.map(i => i.law_number))].sort().forEach(law => $('law-filter').add(new Option(`Ley ${law}`, law)));
  $('law-filter').value = previousLaw; if (!$('law-filter').value) $('law-filter').value = 'all';
  await applyFilters();
}
async function refresh() {
  const { runs } = await api('/api/llm/runs');
  const previous = $('run-select').value;
  $('run-select').replaceChildren();
  runs.forEach(run => $('run-select').add(new Option(`${run.model} · ${run.reasoning_effort} · ${run.created_at_utc.slice(0, 16)} · ${run.prompt_sha256.slice(0, 8)} · ${run.attempted}/${run.sample_size}`, run.run_id)));
  if (runs.some(r => r.run_id === previous)) $('run-select').value = previous;
  if (runs.length) await loadRun();
  else { $('empty-state').classList.remove('hidden'); $('empty-state').textContent = 'No hay ejecuciones todavía. Genera el piloto desde annotations.qmd.'; }
}
async function saveReview(event) {
  event.preventDefault();
  if (!$('review-form').reportValidity()) return;
  const annotations = [...$('annotations').querySelectorAll('[data-annotation-id]')].map(element => ({
    annotation_id: element.dataset.annotationId, verdict: element.querySelector('select').value,
    note: element.querySelector('textarea').value.trim(),
  }));
  if (annotations.some(a => !a.verdict)) { notify('Selecciona un juicio para cada anotación.', true); return; }
  $('save').disabled = true;
  try {
    const body = { result_sha256: reviewState.data.result_sha256, revision: reviewState.data.review?.revision || 0,
      reviewer: $('reviewer').value.trim(), verdict: $('verdict').value, note: $('review-note').value.trim(),
      issues: [...$('issues').querySelectorAll('input:checked')].map(i => i.value), annotations };
    const data = await api(`/api/llm/runs/${reviewState.runId}/items/${reviewState.index}/review`, { method: 'PUT', body: JSON.stringify(body) });
    reviewState.data.review = data.review; reviewState.dirty = false;
    sessionStorage.setItem('llm-reviewer', body.reviewer);
    $('save-status').textContent = `Guardada · versión ${data.review.revision}`;
    notify('Revisión guardada; la salida original se conserva.');
    const current = reviewState.items.find(i => i.sample_index === reviewState.index);
    if (current) current.review_verdict = body.verdict;
  } catch (error) { notify(error.message, true); }
  finally { $('save').disabled = false; }
}
function guarded(action) { return async () => { try { if (discardChanges()) await action(); } catch (error) { notify(error.message, true); } }; }
document.addEventListener('DOMContentLoaded', async () => {
  Object.entries(issueLabels).forEach(([key, text]) => { const label = node('label', null, 'quality-flag-option'); const input = node('input'); input.type = 'checkbox'; input.value = key; label.append(input, node('span', text)); $('issues').append(label); });
  $('review-form').addEventListener('submit', saveReview);
  $('review-form').addEventListener('input', () => { reviewState.dirty = true; });
  $('review-form').addEventListener('change', () => { reviewState.dirty = true; });
  $('run-select').addEventListener('change', guarded(loadRun));
  ['law-filter', 'item-filter'].forEach(id => $(id).addEventListener('change', guarded(applyFilters)));
  $('item-select').addEventListener('change', guarded(() => loadItem(Number($('item-select').value))));
  $('refresh').addEventListener('click', guarded(refresh));
  for (const [id, direction] of [['previous', -1], ['next', 1]]) $(id).addEventListener('click', guarded(() => {
    const position = reviewState.filtered.findIndex(i => i.sample_index === reviewState.index);
    const item = reviewState.filtered[position + direction]; if (item) return loadItem(item.sample_index);
  }));
  window.addEventListener('beforeunload', e => { if (reviewState.dirty) { e.preventDefault(); e.returnValue = ''; } });
  try { await refresh(); } catch (error) { notify(error.message, true); }
});
