# Inputs de anotación LLM

Esta carpeta conserva los inputs procesados de las ejecuciones LLM: muestra,
requests congelados y snapshots del prompt, libro, esquema y código. Los
resultados correspondientes se escriben en
`output/annotations/<run_id>/`; el `run_id` común mantiene la trazabilidad sin
duplicar archivos.

Los intentos preparatorios, canaries y ejecuciones sustituidas no se conservan
aquí. Las decisiones de validación humana siguen escribiéndose en
`output/annotation_reviews/` y los artefactos del piloto histórico permanecen en
`output/annotations/` y `output/annotations_checks/`.
