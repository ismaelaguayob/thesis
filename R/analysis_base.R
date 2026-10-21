# Base analítica compartida por los reportes de resultados (secciones 5.2–5.8).
# Construye intervenciones y declaraciones a partir de un censo de anotaciones,
# para que todos los análisis se repitan igual con Luna-6 y con Haiku 5.5.

LUNA_RUN_DIR <- "output/annotations/openai_gpt6luna_20261002"
HAIKU_RUN_DIR <- "output/annotations/bedrock_haiku55_20261008"
CODEBOOK_PATH <- "data/proc_data/annotations_inputs/pilot_d4e0291b4df3fc0f5343/codebook.json"

# Adjudicación humana de postura (docs/decisiones-validacion.md, sección 5).
STANCE_ADJUDICATION_DIR <- "output/stance_adjudication"

# Regla de inclusión de la sección 5.1: todo el IC 95 % del alfa con Luna < 0,667.
EXCLUDED_CONCEPTS <- c("identidad", "control_responsabilidad_individual")

LAW_LABELS <- c("21419" = "Ley 21.419", "21538" = "Ley 21.538",
                "21735" = "Ley 21.735")
# Ventanas de la reforma (suplemento, sección 4.3).
PHASE_LABELS <- c("2024-01-23" = "Cámara 2024", "2024-01-24" = "Cámara 2024",
                  "2025-01-27" = "Senado 2025", "2025-01-29" = "Cámara 2025")

CONCEPT_SHORT <- c(
  capitalizacion_individual = "Capitalización individual",
  propiedad_individual_fondos = "Propiedad de los fondos",
  reciprocidad_contributiva = "Reciprocidad contributiva",
  control_responsabilidad_individual = "Control individual",
  actitud = "Actitud", identidad = "Identidad",
  necesidad_material = "Necesidad material",
  igualdad_universalismo = "Igualdad y universalismo",
  conciencia_costos = "Conciencia de costos",
  solidaridad_previsional_colectiva = "Solidaridad colectiva",
  solidaridad_intergeneracional = "Solidaridad intergeneracional",
  libertad_eleccion_previsional = "Libertad de elección",
  ineficiencia_estado = "Ineficiencia y riesgo estatal",
  prevision_como_mercado = "Previsión como mercado",
  ilegitimidad_origen_dictatorial = "Origen dictatorial",
  acuerdos_moderacion = "Acuerdos y moderación"
)

read_codebook_concepts <- function(path = CODEBOOK_PATH) {
  codebook <- jsonlite::fromJSON(path)
  tibble::as_tibble(codebook$concepts) |>
    dplyr::transmute(concept_id = id, concept = unname(CONCEPT_SHORT[id]),
                     family) |>
    dplyr::mutate(analyzed = !concept_id %in% EXCLUDED_CONCEPTS)
}

# Metadatos de bloques y actores desde el procesamiento de cada ley.
read_block_metadata <- function(laws = names(LAW_LABELS)) {
  purrr::map(laws, \(law) {
    arrow::read_parquet(sprintf("data/proc_data/ley_%s/coding_chunks_long.parquet", law)) |>
      dplyr::transmute(
        unit_id = as.character(unit_id), law_number = law,
        document_uri = as.character(document_uri),
        utterance_id = as.character(utterance_id),
        date = as.character(date), constitutional_stage,
        utterance_words = source_utterance_n_words,
        speaker_id = as.character(speaker_id),
        # `name` viene del registro BCN; los actores externos solo tienen `speaker`.
        speaker_name = dplyr::coalesce(name, speaker), role,
        gender, party = political_group_party,
        group_source = political_group_source,
        alignment = political_alignment
      )
  }) |>
    purrr::list_rbind()
}

# Decisiones de la adjudicación de postura para un censo. Solo existen para el
# censo principal; devuelve una tabla vacía si el censo no tiene una cola.
read_stance_adjudication <- function(run_dir, root = STANCE_ADJUDICATION_DIR) {
  empty <- tibble::tibble(unit_id = character(), concept_id = character(),
                          decision = character(), rule = character())
  queues <- Sys.glob(file.path(root, "*", "queue.json"))
  queues <- queues[purrr::map_lgl(queues, \(q)
    identical(jsonlite::fromJSON(q)$sources$primary_run, basename(run_dir)))]
  if (!length(queues)) return(empty)
  if (length(queues) > 1) stop("Hay más de una cola de adjudicación para ", run_dir)
  files <- Sys.glob(file.path(dirname(queues), "decisions", "*.json"))
  if (!length(files)) return(empty)
  purrr::map(files, \(f) {
    d <- jsonlite::fromJSON(f)
    tibble::tibble(unit_id = d$unit_id, concept_id = d$concept_id,
                   decision = d$decision, rule = d$rule)
  }) |>
    purrr::list_rbind()
}

# Reemplaza las posturas adjudicadas de cada bloque × concepto: «both» deja apoyo
# y rechazo, «concept_absent» elimina el concepto y «unresolved» conserva la
# anotación original.
apply_stance_adjudication <- function(annotations, adjudication) {
  decided <- dplyr::filter(adjudication, decision != "unresolved")
  if (!nrow(decided)) return(annotations)
  replacement <- decided |>
    dplyr::filter(decision != "concept_absent") |>
    dplyr::mutate(stance = dplyr::case_when(
      decision == "both" ~ list(c("support", "oppose")),
      TRUE ~ as.list(decision))) |>
    tidyr::unnest(stance) |>
    dplyr::select(unit_id, concept_id, stance)
  annotations |>
    dplyr::select(unit_id, concept_id, stance) |>
    dplyr::anti_join(decided, by = c("unit_id", "concept_id")) |>
    dplyr::bind_rows(replacement)
}

# Devuelve una lista con:
# - blocks: un bloque por fila, con su estado y si es sustantivo (tiene
#   declaraciones o no está marcado como votación ni procedimiento);
# - interventions: una intervención por fila, con su actor y si es sustantiva;
# - claims: D_ucs, una fila por intervención sustantiva × concepto × postura,
#   con la postura adjudicada cuando existe una decisión humana;
# - adjudication: las decisiones aplicadas (vacía si no hay o si adjudicate = FALSE).
load_analysis_base <- function(run_dir = LUNA_RUN_DIR,
                               excluded = EXCLUDED_CONCEPTS,
                               adjudicate = TRUE) {
  results <- arrow::read_parquet(file.path(run_dir, "results.parquet")) |>
    dplyr::mutate(unit_id = as.character(unit_id))
  annotations <- arrow::read_parquet(file.path(run_dir, "annotations.parquet")) |>
    dplyr::mutate(unit_id = as.character(unit_id))
  metadata <- read_block_metadata()

  stopifnot(nrow(results) == nrow(metadata),
            !anyDuplicated(results$unit_id), !anyDuplicated(metadata$unit_id),
            setequal(results$unit_id, metadata$unit_id),
            all(results$status == "completed"),
            all(annotations$unit_id %in% results$unit_id),
            all(annotations$stance %in% c("support", "oppose")))

  adjudication <- read_stance_adjudication(run_dir)
  if (!adjudicate) adjudication <- adjudication[0, ]
  annotations <- apply_stance_adjudication(annotations, adjudication)

  flags <- dplyr::coalesce(results$quality_flags, "")
  blocks <- metadata |>
    dplyr::inner_join(
      results |>
        dplyr::transmute(unit_id,
                         statements = decision == "statements",
                         vote = stringr::str_detect(flags, '"vote"'),
                         procedural = stringr::str_detect(flags, '"procedural"')),
      by = "unit_id") |>
    # `vote` también marca justificaciones de voto: un bloque con declaraciones
    # es sustantivo aunque anuncie o justifique un voto.
    dplyr::mutate(substantive = statements | !(vote | procedural))

  key <- c("law_number", "document_uri", "utterance_id")
  interventions <- blocks |>
    dplyr::group_by(dplyr::across(dplyr::all_of(key))) |>
    dplyr::summarise(
      dplyr::across(c(date, constitutional_stage, utterance_words, speaker_id,
                      speaker_name, role, gender, party, group_source,
                      alignment), dplyr::first),
      n_metadata = dplyr::n_distinct(speaker_id, utterance_words),
      substantive = any(substantive),
      excluded_reason = dplyr::case_when(
        any(substantive) ~ NA_character_,
        any(vote) & any(procedural) ~ "votación y procedimiento",
        any(vote) ~ "votación",
        TRUE ~ "procedimiento"),
      .groups = "drop") |>
    dplyr::mutate(law = factor(LAW_LABELS[law_number], levels = LAW_LABELS),
                  debate = factor(dplyr::if_else(law_number == "21735",
                                                 "Reforma", "PGU"),
                                  levels = c("PGU", "Reforma")),
                  phase = factor(PHASE_LABELS[date], levels = unique(PHASE_LABELS)))
  stopifnot(all(interventions$n_metadata == 1L))
  interventions <- dplyr::select(interventions, -n_metadata)

  claims <- annotations |>
    dplyr::filter(!concept_id %in% excluded) |>
    dplyr::select(unit_id, concept_id, stance) |>
    dplyr::inner_join(blocks |>
                        dplyr::filter(substantive) |>
                        dplyr::select(unit_id, dplyr::all_of(key)),
                      by = "unit_id") |>
    dplyr::distinct(dplyr::across(dplyr::all_of(key)), concept_id, stance)

  list(blocks = blocks, interventions = interventions, claims = claims,
       adjudication = adjudication, run_dir = run_dir)
}
