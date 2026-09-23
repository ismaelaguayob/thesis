# Adapted from the repeated flextable style in
# q4zeu-osfstorage-Replication_Materials-archive/6-pisa-dimensionality-comparison.R.
# This helper only exports a Word table.
export_apa7_word_table <- function(data, path, title, note = NULL,
                                   table_number = 1L, left_columns = 1L,
                                   max_width = 7.5, rich_cells = NULL,
                                   landscape = FALSE, column_widths = NULL,
                                   body_font_size = 12, cell_padding = 3) {
  ft <- flextable::flextable(data)
  if (!is.null(note)) {
    ft <- flextable::add_footer_lines(ft, values = paste0("Nota. ", note))
  }

  ft <- flextable::border_remove(ft) |>
    flextable::hline_top(border = officer::fp_border(width = 2), part = "all") |>
    flextable::hline_bottom(border = officer::fp_border(width = 2), part = "all") |>
    flextable::hline(i = 1, border = officer::fp_border(width = 1.5),
                     part = "header") |>
    flextable::bold(part = "header") |>
    flextable::font(fontname = "Times New Roman", part = "all") |>
    flextable::fontsize(size = body_font_size, part = "all") |>
    flextable::padding(padding = cell_padding, part = "all") |>
    flextable::align(align = "center", part = "header") |>
    flextable::align(j = seq_len(left_columns), align = "left", part = "body") |>
    flextable::align(j = seq.int(left_columns + 1L, ncol(data)),
                     align = "center", part = "body") |>
    flextable::autofit() |>
    flextable::fit_to_width(max_width = max_width) |>
    flextable::set_table_properties(
      opts_word = list(split = FALSE, repeat_headers = TRUE)
    )

  if (!is.null(column_widths)) {
    stopifnot(length(column_widths) == ncol(data))
    ft <- flextable::width(ft, j = seq_along(column_widths),
                           width = column_widths)
  }

  if (!is.null(note)) {
    ft <- flextable::italic(ft, part = "footer")
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
