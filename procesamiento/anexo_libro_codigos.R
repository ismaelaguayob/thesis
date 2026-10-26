# Tabla del libro de códigos para el Anexo 1, en formato APA 7.
# Usa el snapshot del libro enviado a los modelos en la corrida de entrada del
# censo (el mismo que lee R/analysis_base.R). Las reglas de inclusión y
# exclusión quedan en el libro completo; la tabla muestra lo que el lector
# necesita para interpretar los resultados: concepto, definición y postura de
# apoyo.
# Uso, desde la raíz del proyecto: Rscript procesamiento/anexo_libro_codigos.R

pacman::p_load(jsonlite, dplyr, purrr, tibble, flextable, officer)
source("R/apa7_word_table.R")

CODEBOOK_PATH <- "data/proc_data/annotations_inputs/pilot_d4e0291b4df3fc0f5343/codebook.json"
OUTPUT_PATH <- "output/tables/anexo_libro_codigos.docx"
# Conceptos excluidos de los análisis por la regla de inclusión (sección 5.1).
EXCLUDED <- c("identidad", "control_responsabilidad_individual")
FAMILY_ORDER <- c(
  "CARIN" = "Criterios de merecimiento (CARIN)",
  "Criterio contextual" = "Criterios contextuales",
  "Justificación distributiva del caso" = "Justificaciones distributivas del caso",
  "Justificación institucional del caso" = "Justificaciones institucionales del caso",
  "Justificación procedimental del caso" = "Justificación procedimental del caso"
)

codebook <- fromJSON(CODEBOOK_PATH, simplifyVector = FALSE)
concepts <- map_dfr(codebook$concepts, \(x) tibble(
  id = x$id, family = x$family, label = x$label,
  definition = x$definition, anchor = x$orientation_anchor
))
stopifnot(nrow(concepts) == 16L, all(concepts$family %in% names(FAMILY_ORDER)),
          all(EXCLUDED %in% concepts$id))

rows <- concepts |>
  mutate(family = factor(family, levels = names(FAMILY_ORDER)),
         label = if_else(id %in% EXCLUDED, paste0(label, "*"), label)) |>
  arrange(family) |>
  group_by(family) |>
  group_modify(\(d, g) bind_rows(
    tibble(label = FAMILY_ORDER[[as.character(g$family)]], definition = "", anchor = ""),
    select(d, label, definition, anchor))) |>
  ungroup() |>
  select(label, definition, anchor)

export_apa7_word_table(
  rows, OUTPUT_PATH,
  "Conceptos del libro de códigos",
  note = paste(
    "La postura de apoyo corresponde a la orientación del concepto: una declaración",
    "lo apoya cuando afirma esa proposición y lo rechaza cuando la niega o la critica.",
    "Las reglas de inclusión y exclusión de cada concepto se presentan en el libro de",
    "códigos completo, enlazado en este anexo.",
    "* Concepto excluido de los análisis porque su concordancia con la referencia",
    "humana no alcanzó el umbral (sección 5.1)."),
  table_number = 3L, body_font_size = 10, left_columns = 3L,
  header_labels = c("Concepto", "Definición", "Postura de apoyo"),
  column_widths = c(1.5, 2.8, 2.0),
  section_rows = which(rows$definition == ""))
message("Tabla escrita en ", OUTPUT_PATH)
