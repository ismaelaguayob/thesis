# Adapted from the repeated flextable style in
# q4zeu-osfstorage-Replication_Materials-archive/6-pisa-dimensionality-comparison.R.
# This helper only exports a Word table.
export_apa7_word_table <- function(data, path, title, note = NULL,
                                   table_number = 1L, left_columns = 1L,
                                   max_width = 7.5) {
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
    flextable::fontsize(size = 9, part = "body") |>
    flextable::fontsize(size = 10, part = "header") |>
    flextable::padding(padding = 3, part = "all") |>
    flextable::align(align = "center", part = "header") |>
    flextable::align(j = seq_len(left_columns), align = "left", part = "body") |>
    flextable::align(j = seq.int(left_columns + 1L, ncol(data)),
                     align = "center", part = "body") |>
    flextable::autofit() |>
    flextable::fit_to_width(max_width = max_width)

  if (!is.null(note)) {
    ft <- flextable::italic(ft, part = "footer") |>
      flextable::fontsize(size = 9, part = "footer")
  }

  doc <- officer::read_docx()
  doc <- officer::body_add_fpar(
    doc,
    officer::fpar(
      officer::ftext(paste("Tabla", table_number),
                     prop = officer::fp_text(font.family = "Times New Roman",
                                             font.size = 11, bold = TRUE)),
      fp_p = officer::fp_par(keep_with_next = TRUE)
    )
  )
  doc <- officer::body_add_fpar(
    doc,
    officer::fpar(
      officer::ftext(title,
                     prop = officer::fp_text(font.family = "Times New Roman",
                                             font.size = 11, italic = TRUE)),
      fp_p = officer::fp_par(keep_with_next = TRUE)
    )
  )
  doc <- flextable::body_add_flextable(doc, ft)
  print(doc, target = path)
  invisible(path)
}
