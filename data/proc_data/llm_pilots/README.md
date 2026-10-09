# Pruebas de anotación LLM

Esta carpeta contiene datos derivados y manifiestos para pruebas de prompts.
No forma parte de los corpus `ley_*` que consume la app manual.

- `api_policy.json`: autorización explícita y acotada por ejecución, modelo, esfuerzo y máximo de llamadas.
- `audits/pilot_f3a69c2f81c587271ef5/manifest.json`: consumo confirmado y métricas del primer piloto.
- `audits/pilot_f3a69c2f81c587271ef5/response_ledger.parquet`: una fila por respuesta persistida, con tokens, IDs y hashes.
- Los demás Parquet de esa carpeta contienen cobertura, diagnósticos de longitud y conteos por concepto.

Los generó sin API el reporte `annotations.qmd`, eliminado el 2026-10-09 porque
ya no se usaba; su última versión renderizada sigue en `_output/annotations.html`
y sus hallazgos están en `docs/secuencia-validacion-instrumento.md`.
El manifiesto distingue consumo registrado de consumo facturado desconocido y
validez estructural de exactitud sustantiva. Los resultados originales permanecen
en `output/annotations/` y la prueba inicial en `output/annotations_checks/`.
