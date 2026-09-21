# Inputs de anotación LLM

Esta carpeta conserva únicamente la ejecución canónica vigente del segundo
piloto. Cada ejecución es autocontenida: incluye la muestra procesada, los
requests congelados, snapshots del prompt, libro, esquema y código, y los
resultados necesarios para reanudar o revisar el lote sin separar su
trazabilidad.

Los intentos preparatorios, canaries y ejecuciones sustituidas no se conservan
aquí. Las decisiones de validación humana siguen escribiéndose en
`output/annotation_reviews/` y los artefactos del piloto histórico permanecen en
`output/annotations/` y `output/annotations_checks/`.
