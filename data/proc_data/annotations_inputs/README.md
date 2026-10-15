# Inputs de anotación LLM

Esta carpeta conserva los inputs procesados de las ejecuciones LLM: muestra,
requests congelados y snapshots del prompt, libro, esquema y código. Los
resultados correspondientes se escriben en
`output/annotations/<run_id>/`; el `run_id` común mantiene la trazabilidad sin
duplicar archivos.

Solo se conservan los inputs de los dos censos definitivos: `pilot_d4e0291b…`
(Luna-6) y `pilot_cc90579…` (réplica Haiku). Los intentos preparatorios, pilotos
y ejecuciones sustituidas se eliminaron; su registro está en
`data/proc_data/llm_pilots/`, `output/annotation_reviews/` y
`docs/secuencia-validacion-instrumento.md`.
