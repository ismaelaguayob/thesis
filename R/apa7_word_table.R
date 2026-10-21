# Adapted from the repeated flextable style in
# q4zeu-osfstorage-Replication_Materials-archive/6-pisa-dimensionality-comparison.R.
# This helper only exports a Word table.
export_apa7_word_table <- function(data, path, title, note = NULL,
                                   table_number = 1L, left_columns = 1L,
                                   max_width = NULL, rich_cells = NULL,
                                   landscape = FALSE, column_widths = NULL,
                                   body_font_size = 12, cell_padding = 3,
                                   header_labels = NULL, header_groups = NULL,
                                   section_rows = NULL, merge_cells = NULL) {
  # header_labels: etiquetas visibles de las columnas (permite repetirlas).
  # header_groups: fila superior que agrupa columnas, p. ej.
  #   c(" " = 1, "Apoyo" = 3, "Rechazo" = 3).
  # section_rows: filas del cuerpo que funcionan como títulos de panel o de
  #   grupo; se combinan a lo ancho de la tabla y van en cursiva.
  # merge_cells: lista de list(rows = , columns = ) para combinar celdas
  #   horizontalmente; el valor debe estar en la primera columna del grupo.
  ft <- flextable::flextable(data)
  if (!is.null(header_labels)) {
    stopifnot(length(header_labels) == ncol(data))
    ft <- flextable::set_header_labels(ft, values = stats::setNames(
      as.list(header_labels), names(data)))
  }
  if (!is.null(header_groups)) {
    stopifnot(sum(header_groups) == ncol(data))
    ft <- flextable::add_header_row(ft, values = names(header_groups),
                                    colwidths = unname(header_groups))
  }
  if (!is.null(note)) {
    # APA 7: only the label "Nota." is italic; the note text is regular.
    ft <- flextable::add_footer_lines(
      ft, values = flextable::as_paragraph(flextable::as_i("Nota."), paste0(" ", note))
    )
  }

  # APA 7: líneas sobre y bajo el encabezado y al final del cuerpo; la nota
  # queda sin borde.
  ft <- flextable::border_remove(ft) |>
    flextable::hline_top(border = officer::fp_border(width = 2), part = "header") |>
    flextable::hline_bottom(border = officer::fp_border(width = 1.5), part = "header") |>
    flextable::hline_bottom(border = officer::fp_border(width = 2), part = "body") |>
    flextable::bold(part = "header") |>
    flextable::font(fontname = "Times New Roman", part = "all") |>
    flextable::fontsize(size = body_font_size, part = "all") |>
    flextable::padding(padding = cell_padding, part = "all") |>
    flextable::align(align = "center", part = "header") |>
    flextable::align(j = seq_len(left_columns), align = "left", part = "body") |>
    flextable::align(j = seq.int(left_columns + 1L, ncol(data)),
                     align = "center", part = "body") |>
    flextable::autofit() |>
    flextable::set_table_properties(
      opts_word = list(split = FALSE, repeat_headers = TRUE)
    )

  if (!is.null(header_groups)) {
    # Línea corta bajo cada etiqueta de grupo con más de una columna.
    ends <- cumsum(header_groups)
    starts <- ends - header_groups + 1
    for (k in which(header_groups > 1 & trimws(names(header_groups)) != "")) {
      ft <- flextable::hline(ft, i = 1, j = starts[k]:ends[k],
                             border = officer::fp_border(width = 1), part = "header")
    }
  }
  for (cells in merge_cells) {
    for (i in cells$rows) {
      ft <- flextable::merge_at(ft, i = i, j = cells$columns, part = "body")
    }
  }
  for (i in section_rows) {
    ft <- flextable::merge_at(ft, i = i, j = seq_len(ncol(data)), part = "body") |>
      flextable::italic(i = i, part = "body") |>
      flextable::align(i = i, align = "left", part = "body")
  }

  # Scale column widths instead of fit_to_width(), which shrinks the font.
  # Text keeps body_font_size and wraps inside the narrower columns. Default
  # widths are the usable width of an A4 page with the margins set below.
  if (is.null(max_width)) max_width <- if (landscape) 10.2 else 6.3
  # Measure header and body only: the long footer note would widen column 1.
  widths <- pmax(flextable::dim_pretty(ft, part = "header")$widths,
                 flextable::dim_pretty(ft, part = "body")$widths)
  ft <- flextable::width(ft, width = widths * min(1, max_width / sum(widths)))

  if (!is.null(column_widths)) {
    stopifnot(length(column_widths) == ncol(data))
    ft <- flextable::width(ft, j = seq_along(column_widths),
                           width = column_widths)
  }


  if (!is.null(rich_cells)) {
    for (k in seq_len(nrow(rich_cells))) {
      cell <- rich_cells[k, ]
      ft <- flextable::compose(
        ft, i = cell$row, j = cell$column,
        value = flextable::as_paragraph(
          flextable::as_chunk(cell$positive,
                              props = officer::fp_text(
                                font.family = "Times New Roman",
                                font.size = body_font_size,
                                bold = cell$bold_positive)),
          flextable::as_chunk("\n"),
          flextable::as_chunk(cell$negative,
                              props = officer::fp_text(
                                font.family = "Times New Roman",
                                font.size = body_font_size,
                                bold = cell$bold_negative))
        )
      )
    }
  }

  doc <- officer::read_docx()
  if (landscape) {
    doc <- officer::body_set_default_section(
      doc, value = officer::prop_section(
        page_size = officer::page_size(orient = "landscape"),
        page_margins = officer::page_mar(top = 0.45, bottom = 0.45,
                                         left = 0.7, right = 0.7)
      )
    )
  }
  doc <- officer::body_add_fpar(
    doc,
    officer::fpar(
      officer::ftext(paste("Tabla", table_number),
                     prop = officer::fp_text(font.family = "Times New Roman",
                                             font.size = body_font_size,
                                             bold = TRUE)),
      fp_p = officer::fp_par(keep_with_next = TRUE)
    )
  )
  doc <- officer::body_add_fpar(
    doc,
    officer::fpar(
      officer::ftext(title,
                     prop = officer::fp_text(font.family = "Times New Roman",
                                             font.size = body_font_size,
                                             italic = TRUE)),
      fp_p = officer::fp_par(keep_with_next = TRUE)
    )
  )
  doc <- flextable::body_add_flextable(doc, ft)
  print(doc, target = path)
  invisible(path)
}
