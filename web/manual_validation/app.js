"use strict";

const state = {
  config: null,
  sessionId: null,
  session: null,
  index: 0,
  item: null,
  codebook: null,
  annotations: [],
  selection: null,
  dirty: false,
};

const elements = {};

function byId(id) {
  return document.getElementById(id);
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  let payload;
  try {
    payload = await response.json();
  } catch (_error) {
    payload = { error: `Respuesta HTTP ${response.status}` };
  }
  if (!response.ok) {
    throw new Error(payload.error || `Error HTTP ${response.status}`);
  }
  return payload;
}

function showToast(message, kind = "success") {
  elements.toast.textContent = message;
  elements.toast.classList.toggle("error", kind === "error");
  elements.toast.classList.remove("hidden");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => elements.toast.classList.add("hidden"), 3600);
}

function setBusy(button, busy, label) {
  if (busy) {
    button.dataset.originalLabel = button.textContent;
    button.textContent = label;
  } else if (button.dataset.originalLabel) {
    button.textContent = button.dataset.originalLabel;
  }
  button.disabled = busy;
}

function formatDateTime(value) {
  if (!value) return "sin fecha";
  const date = new Date(value);
  return Number.isNaN(date.valueOf())
    ? value
    : new Intl.DateTimeFormat("es-CL", {
        dateStyle: "medium",
        timeStyle: "short",
      }).format(date);
}

function showSetup() {
  elements.setupView.classList.remove("hidden");
  elements.codingView.classList.add("hidden");
  renderSessions(state.config?.sessions || []);
}

function showCoding() {
  elements.setupView.classList.add("hidden");
  elements.codingView.classList.remove("hidden");
}

function renderCorpusSummary() {
  const corpus = state.config.corpus;
  const codebook = state.config.codebook;
  elements.corpusSummary.textContent = [
    `${corpus.available_interventions} intervenciones disponibles`,
    `boletín ${state.config.bill_number}`,
    `${codebook.concepts.length} conceptos`,
    `libro ${codebook.version}`,
  ].join(" · ");
}

function renderSessions(sessions) {
  elements.sessionsList.replaceChildren();
  if (!sessions.length) {
    const empty = document.createElement("div");
    empty.className = "empty-sessions";
    empty.textContent = "Todavía no hay sesiones guardadas.";
    elements.sessionsList.append(empty);
    return;
  }
  sessions.forEach((session) => {
    const entry = document.createElement("article");
    entry.className = "session-entry";
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = session.pending
      ? `Reanudar · ${session.completed}/${session.sample_size}`
      : `Revisar sesión completa · ${session.sample_size}/${session.sample_size}`;
    button.addEventListener("click", () => {
      const index = session.next_pending_index ?? 0;
      resumeSession(session.session_id, index);
    });
    const meta = document.createElement("p");
    const coder = session.coder_id ? ` · ${session.coder_id}` : "";
    meta.textContent = `${formatDateTime(session.updated_at_utc)} · libro ${session.codebook_version}${coder}`;
    entry.append(button, meta);
    elements.sessionsList.append(entry);
  });
}

function renderConceptOptions() {
  const current = elements.conceptSelect.value;
  elements.conceptSelect.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Seleccionar…";
  elements.conceptSelect.append(placeholder);
  state.codebook.concepts.forEach((concept) => {
    const option = document.createElement("option");
    option.value = concept.id;
    option.textContent = concept.label;
    elements.conceptSelect.append(option);
  });
  const review = document.createElement("option");
  review.value = "__review__";
  review.textContent = "Revisar: concepto ausente del libro";
  elements.conceptSelect.append(review);
  if ([...elements.conceptSelect.options].some((option) => option.value === current)) {
    elements.conceptSelect.value = current;
  }
  renderConceptDefinition();
}

function renderCodebook() {
  elements.codebookList.replaceChildren();
  state.codebook.concepts.forEach((concept) => {
    const entry = document.createElement("article");
    entry.className = "codebook-entry";
    const label = document.createElement("strong");
    label.textContent = concept.label;
    const definition = document.createElement("p");
    definition.textContent = concept.definition;
    entry.append(label, definition);
    appendCriteria(entry, "Incluir", concept.include);
    appendCriteria(entry, "Excluir", concept.exclude);
    elements.codebookList.append(entry);
  });
}

function appendCriteria(container, heading, entries) {
  if (!Array.isArray(entries) || !entries.length) return;
  const title = document.createElement("span");
  title.className = "criteria-title";
  title.textContent = heading;
  const list = document.createElement("ul");
  entries.forEach((entry) => {
    const item = document.createElement("li");
    item.textContent = entry;
    list.append(item);
  });
  container.append(title, list);
}

function renderConceptDefinition() {
  const value = elements.conceptSelect.value;
  const isReview = value === "__review__";
  elements.proposedConceptLabel.classList.toggle("hidden", !isReview);
  elements.conceptDefinition.replaceChildren();
  if (isReview) {
    elements.conceptDefinition.textContent =
      "El span expresa una posición frente a un concepto que todavía no está en el libro de códigos.";
    return;
  }
  const concept = state.codebook?.concepts.find((item) => item.id === value);
  if (!concept) return;
  const definition = document.createElement("p");
  definition.textContent = concept.definition;
  elements.conceptDefinition.append(definition);
  appendCriteria(elements.conceptDefinition, "Incluir", concept.include);
  appendCriteria(elements.conceptDefinition, "Excluir", concept.exclude);
}

function annotationFromServer(annotation) {
  return {
    annotation_id: annotation.annotation_id,
    start_char: annotation.span.start_char,
    end_char: annotation.span.end_char,
    evidence_text: annotation.span.text,
    concept_status: annotation.concept_status,
    concept_id: annotation.concept_id,
    proposed_concept: annotation.proposed_concept || "",
    stance: annotation.stance,
    note: annotation.note || "",
    selected_at_client: annotation.selected_at_client || annotation.created_at_utc || null,
  };
}

function conceptLabel(annotation) {
  if (annotation.concept_status === "review") {
    return annotation.proposed_concept
      ? `Revisar: ${annotation.proposed_concept}`
      : "Revisar concepto ausente";
  }
  return (
    state.codebook.concepts.find((concept) => concept.id === annotation.concept_id)?.label ||
    annotation.concept_id
  );
}

function renderAnnotations() {
  elements.annotationsList.replaceChildren();
  elements.annotationCount.textContent = String(state.annotations.length);
  if (!state.annotations.length) {
    const empty = document.createElement("div");
    empty.className = "annotation-empty";
    empty.textContent = "Aún no hay declaraciones en esta intervención.";
    elements.annotationsList.append(empty);
  }
  state.annotations.forEach((annotation, index) => {
    const entry = document.createElement("article");
    entry.className = "annotation-entry";
    const quote = document.createElement("blockquote");
    quote.textContent = `“${annotation.evidence_text}”`;
    const meta = document.createElement("div");
    meta.className = "annotation-meta";

    const concept = document.createElement("span");
    concept.className = annotation.concept_status === "review" ? "review-tag" : "concept-tag";
    concept.textContent = conceptLabel(annotation);
    const stance = document.createElement("span");
    stance.className = annotation.stance === "support" ? "support-tag" : "oppose-tag";
    stance.textContent = annotation.stance === "support" ? "Apoyo" : "Rechazo";
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "delete-annotation";
    remove.textContent = "Eliminar";
    remove.setAttribute("aria-label", `Eliminar declaración ${index + 1}`);
    remove.addEventListener("click", () => {
      state.annotations.splice(index, 1);
      state.dirty = true;
      renderAnnotations();
      updateNoStatementsState();
    });
    meta.append(concept, stance, remove);
    entry.append(quote, meta);
    if (annotation.note) {
      const note = document.createElement("small");
      note.textContent = annotation.note;
      entry.append(note);
    }
    elements.annotationsList.append(entry);
  });
}

function renderProgress() {
  const total = state.session.sample_size;
  const completed = state.session.completed;
  elements.progressText.textContent = `Muestra ${state.index + 1} de ${total} · ${completed} guardadas`;
  elements.progressBar.style.width = `${total ? (completed / total) * 100 : 0}%`;
  elements.previousItem.disabled = state.index <= 0;
  elements.saveNext.textContent = state.index + 1 >= total ? "Guardar y finalizar" : "Guardar y siguiente";
}

function renderItem() {
  elements.previousText.textContent = state.item.has_previous
    ? state.item.previous_text
    : "Esta es la primera intervención disponible en el documento.";
  elements.targetText.textContent = state.item.target_text;
  elements.itemMetadata.replaceChildren();
  [state.item.date, state.item.constitutional_stage, `${state.item.n_words} palabras`]
    .filter(Boolean)
    .forEach((value) => {
      const chip = document.createElement("span");
      chip.textContent = value;
      elements.itemMetadata.append(chip);
    });
  state.annotations = (state.item.annotations || []).map(annotationFromServer);
  elements.noStatements.checked = state.item.decision === "no_statements";
  state.selection = null;
  state.dirty = false;
  elements.saveState.textContent = state.item.status === "completed" ? "Codificación guardada" : "Sin guardar";
  elements.selectionPreview.textContent = "Selecciona un span en la intervención objetivo.";
  elements.selectionPreview.classList.add("empty");
  elements.conceptSelect.value = "";
  elements.proposedConcept.value = "";
  elements.annotationNote.value = "";
  document.querySelectorAll('input[name="stance"]').forEach((input) => {
    input.checked = false;
  });
  renderConceptDefinition();
  renderAnnotations();
  updateNoStatementsState();
  renderProgress();
  elements.targetText.scrollTop = 0;
}

function updateNoStatementsState() {
  const hasAnnotations = state.annotations.length > 0;
  elements.noStatements.disabled = hasAnnotations;
  if (hasAnnotations) elements.noStatements.checked = false;
}

function getSelectionOffsets(container) {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0 || selection.isCollapsed) return null;
  const range = selection.getRangeAt(0);
  if (!container.contains(range.commonAncestorContainer)) return null;
  const prefix = range.cloneRange();
  prefix.selectNodeContents(container);
  prefix.setEnd(range.startContainer, range.startOffset);
  const start = prefix.toString().length;
  const evidence = range.toString();
  const end = start + evidence.length;
  if (!evidence.trim() || container.textContent.slice(start, end) !== evidence) return null;
  return { start_char: start, end_char: end, evidence_text: evidence };
}

function captureSelection() {
  const selected = getSelectionOffsets(elements.targetText);
  if (!selected) return;
  state.selection = selected;
  elements.selectionPreview.textContent = selected.evidence_text;
  elements.selectionPreview.classList.remove("empty");
}

function selectedStance() {
  return document.querySelector('input[name="stance"]:checked')?.value || "";
}

function createAnnotationId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  return `annotation_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

function addAnnotation() {
  if (!state.selection) {
    showToast("Selecciona primero un span en la intervención objetivo.", "error");
    return;
  }
  const conceptValue = elements.conceptSelect.value;
  const stance = selectedStance();
  if (!conceptValue) {
    showToast("Selecciona un concepto o la etiqueta Revisar.", "error");
    return;
  }
  if (!stance) {
    showToast("Selecciona apoyo o rechazo.", "error");
    return;
  }
  const conceptStatus = conceptValue === "__review__" ? "review" : "in_codebook";
  const annotation = {
    annotation_id: createAnnotationId(),
    ...state.selection,
    concept_status: conceptStatus,
    concept_id: conceptStatus === "in_codebook" ? conceptValue : null,
    proposed_concept: elements.proposedConcept.value.trim(),
    stance,
    note: elements.annotationNote.value.trim(),
    selected_at_client: new Date().toISOString(),
  };
  const duplicate = state.annotations.some(
    (item) =>
      item.start_char === annotation.start_char &&
      item.end_char === annotation.end_char &&
      item.concept_status === annotation.concept_status &&
      item.concept_id === annotation.concept_id &&
      item.proposed_concept === annotation.proposed_concept &&
      item.stance === annotation.stance,
  );
  if (duplicate) {
    showToast("Esa declaración ya está registrada.", "error");
    return;
  }
  state.annotations.push(annotation);
  state.dirty = true;
  state.selection = null;
  elements.selectionPreview.textContent = "Selecciona otro span o guarda la intervención.";
  elements.selectionPreview.classList.add("empty");
  elements.conceptSelect.value = "";
  elements.proposedConcept.value = "";
  elements.annotationNote.value = "";
  document.querySelectorAll('input[name="stance"]').forEach((input) => {
    input.checked = false;
  });
  renderConceptDefinition();
  renderAnnotations();
  updateNoStatementsState();
  window.getSelection()?.removeAllRanges();
}

function currentDecision() {
  if (state.annotations.length) return "statements";
  if (elements.noStatements.checked) return "no_statements";
  return null;
}

async function saveCurrent(advance) {
  const decision = currentDecision();
  if (!decision) {
    showToast("Agrega una declaración o marca Sin declaraciones codificables.", "error");
    return;
  }
  const button = advance ? elements.saveNext : elements.saveItem;
  setBusy(button, true, "Guardando…");
  elements.saveState.textContent = "Guardando";
  try {
    const result = await fetchJSON(
      `/api/sessions/${encodeURIComponent(state.sessionId)}/items/${state.index}`,
      {
        method: "PUT",
        body: JSON.stringify({ decision, annotations: state.annotations }),
      },
    );
    state.session = result.session;
    state.item = result.item;
    state.codebook = result.codebook;
    state.dirty = false;
    elements.saveState.textContent = "Guardado";
    if (advance && state.index + 1 < state.session.sample_size) {
      await loadItem(state.index + 1);
    } else {
      renderItem();
      showToast(
        state.session.pending === 0
          ? "Muestra completada. El JSON quedó guardado."
          : "Codificación guardada.",
      );
    }
    await refreshConfig();
  } catch (error) {
    elements.saveState.textContent = "Error al guardar";
    showToast(error.message, "error");
  } finally {
    setBusy(button, false, "");
  }
}

async function loadItem(index) {
  const result = await fetchJSON(
    `/api/sessions/${encodeURIComponent(state.sessionId)}/items/${index}`,
  );
  state.index = index;
  state.session = result.session;
  state.item = result.item;
  state.codebook = result.codebook;
  elements.sessionLabel.textContent = `Sesión ${state.session.session_id.slice(-8)} · libro ${state.session.codebook_version}`;
  renderConceptOptions();
  renderCodebook();
  renderItem();
}

async function resumeSession(sessionId, index) {
  try {
    state.sessionId = sessionId;
    await loadItem(index);
    showCoding();
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function refreshConfig() {
  state.config = await fetchJSON("/api/config");
  renderCorpusSummary();
  renderSessions(state.config.sessions);
}

async function createSession(event) {
  event.preventDefault();
  const button = elements.sessionForm.querySelector('button[type="submit"]');
  setBusy(button, true, "Creando muestra…");
  try {
    const summary = await fetchJSON("/api/sessions", {
      method: "POST",
      body: JSON.stringify({
        coder_id: elements.coderId.value.trim(),
        sample_size: Number(elements.sampleSize.value),
        seed: Number(elements.sampleSeed.value),
        strategy: elements.samplingStrategy.value,
      }),
    });
    await refreshConfig();
    await resumeSession(summary.session_id, summary.next_pending_index ?? 0);
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setBusy(button, false, "");
  }
}

function confirmDiscard() {
  return !state.dirty || window.confirm("Hay cambios sin guardar. ¿Quieres descartarlos?");
}

function bindEvents() {
  elements.sessionForm.addEventListener("submit", createSession);
  elements.conceptSelect.addEventListener("change", renderConceptDefinition);
  elements.addAnnotation.addEventListener("click", addAnnotation);
  elements.targetText.addEventListener("mouseup", captureSelection);
  elements.targetText.addEventListener("keyup", captureSelection);
  elements.saveItem.addEventListener("click", () => saveCurrent(false));
  elements.saveNext.addEventListener("click", () => saveCurrent(true));
  elements.previousItem.addEventListener("click", async () => {
    if (state.index > 0 && confirmDiscard()) await loadItem(state.index - 1);
  });
  elements.returnSetup.addEventListener("click", () => {
    if (confirmDiscard()) showSetup();
  });
  elements.noStatements.addEventListener("change", () => {
    if (elements.noStatements.checked && state.annotations.length) {
      elements.noStatements.checked = false;
      showToast("Elimina las declaraciones antes de marcar esta opción.", "error");
      return;
    }
    state.dirty = true;
  });
  window.addEventListener("beforeunload", (event) => {
    if (!state.dirty) return;
    event.preventDefault();
    event.returnValue = "";
  });
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter" && state.sessionId) {
      event.preventDefault();
      saveCurrent(true);
    }
  });
}

async function initialize() {
  [
    "setup-view",
    "coding-view",
    "session-form",
    "coder-id",
    "sample-size",
    "sample-seed",
    "sampling-strategy",
    "corpus-summary",
    "sessions-list",
    "session-label",
    "progress-text",
    "progress-bar",
    "return-setup",
    "previous-text",
    "target-text",
    "item-metadata",
    "previous-item",
    "save-item",
    "save-next",
    "save-state",
    "selection-preview",
    "concept-select",
    "concept-definition",
    "proposed-concept-label",
    "proposed-concept",
    "annotation-note",
    "add-annotation",
    "annotations-list",
    "annotation-count",
    "no-statements",
    "codebook-list",
    "toast",
  ].forEach((id) => {
    const key = id.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    elements[key] = byId(id);
  });
  bindEvents();
  try {
    await refreshConfig();
    elements.sampleSize.value = state.config.defaults.sample_size;
    elements.sampleSeed.value = state.config.defaults.seed;
    elements.samplingStrategy.value = state.config.defaults.strategy;
    showSetup();
  } catch (error) {
    showToast(error.message, "error");
    elements.corpusSummary.textContent = `No fue posible cargar la aplicación: ${error.message}`;
  }
}

document.addEventListener("DOMContentLoaded", initialize);
