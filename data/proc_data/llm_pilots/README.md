# Pruebas de anotación LLM

Esta carpeta contiene datos derivados y manifiestos para pruebas de prompts.
No forma parte de los corpus `ley_*` que consume la app manual.

- `api_policy.json`: llamadas de anotación desactivadas por instrucción del usuario.
- `pilot_f3a69c2f81c587271ef5/manifest.json`: consumo confirmado y métricas del primer piloto.
- `pilot_f3a69c2f81c587271ef5/response_ledger.parquet`: una fila por respuesta persistida, con tokens, IDs y hashes.
- Los demás Parquet de esa carpeta contienen cobertura y conteos por concepto.

Se regeneran sin API mediante `uv run quarto render annotations.qmd`.
El manifiesto distingue consumo registrado de consumo facturado desconocido y
validez estructural de exactitud sustantiva. Los resultados originales permanecen
en `output/annotations/` y la prueba inicial en `output/annotations_checks/`.
