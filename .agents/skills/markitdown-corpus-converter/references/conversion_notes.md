# Conversion Notes

Create machine-readable Markdown derivatives for literature review work. Derivatives are analysis artifacts, not replacements for source PDFs/HTML files.

## Configuration

Read `literature-review.yaml`:

- `project.bib_path`: BibTeX export from Zotero.
- `paths.sources_dir`: source files to convert.
- `paths.machine_dir`: Markdown output directory.

## Metadata

Each converted Markdown file starts with a metadata block:

```yaml
---
source_path: sources/example.pdf
source_type: pdf
source_kind: journal_article
bib_key: Example2026
bib_entry_type: article
bib_title: Example Title
converter: markitdown
converted_at: ...
---
```

Use this metadata during synthesis for citation, source-kind handling, and traceability.

## Commands

```bash
python3 .agents/skills/markitdown-corpus-converter/scripts/convert_corpus.py
python3 .agents/skills/markitdown-corpus-converter/scripts/convert_pdf.py "sources/example.pdf"
python3 .agents/skills/markitdown-corpus-converter/scripts/convert_pdf.py "sources/example.pdf" --engine pdftotext --force
python3 .agents/skills/markitdown-corpus-converter/scripts/convert_corpus.py --pdf-engine pdftotext-layout --force
python3 .agents/skills/markitdown-corpus-converter/scripts/convert_html.py "sources/example.html"
```

Add `--force` only when the user wants to refresh existing outputs.

## Quality Notes

MarkItDown extraction can be noisy for scanned PDFs, tables, multi-column layouts, or reports with heavy figures. If MarkItDown fails or produces unusable text, retry PDFs with `--engine pdftotext` or `--engine pdftotext-layout`. These modes require Poppler's `pdftotext` command to be installed. Report noisy conversion and prefer trace anchors plus source metadata over unreliable page inference.
