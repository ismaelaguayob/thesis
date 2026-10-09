# Pipeline de anotación LLM

Cómo se prepararon, ejecutaron y validaron las anotaciones automáticas, y cómo
replicarlas. La cronología de pilotos y versiones del instrumento está en
[secuencia-validacion-instrumento.md](secuencia-validacion-instrumento.md).

## Requisitos y secretos

```bash
uv sync --locked          # dependencias exactas (uv.lock)
cp .env.example .env      # y completar las variables
```

| Variable | Uso | ¿Secreto? |
|---|---|---|
| `OPENAI_API_KEY` | Llamadas a OpenAI (censo Luna-6) | Sí |
| `AWS_BEDROCK_API_KEY` | Llamadas a Amazon Bedrock (réplica Haiku y lote Bedrock) | Sí |
| `AWS_BEDROCK_REGION` | Región de Bedrock para lotes nuevos (`us-west-2` por defecto) | No |
| `PARTY_ALIGNMENT`, `CENTER_LEFT_PARTIES` | Clasificación partidaria usada por `proc.qmd`, el muestreo y el análisis | No |
| `ANNOTATIONS_PROVIDER`, `ANNOTATIONS_MODEL`, `ANNOTATIONS_BEDROCK_MODEL_ID`, `REASONING_LEVEL`, `ANNOTATIONS_MAX_RETRIES`, `ANNOTATIONS_INCOMPLETE_MAX_OUTPUT_TOKENS` | Configuración de lotes **nuevos**; no afectan lotes ya congelados | No |

Las claves se leen solo desde `.env` o el entorno del proceso. No se guardan en
requests, manifiestos, HTML ni en el navegador. Preparar inputs, renderizar
`analysis.qmd` y abrir la app no usan ninguna clave.

## Etapas

1. **Corpus.** `proc.qmd` escribe `data/proc_data/ley_*/coding_chunks_long.parquet`.
2. **Instrumento.** El libro editable es `features/codebook/codebook_v5.xlsx`; su
   JSON se genera con `uv run python -m features.manual_validation.generate_codebook_json`.
   El prompt es `prompts/annotations_prompt_final.md`.
3. **Preparación (local).** `uv run python -m features.llm_annotations.prepare_all`
   congela un request por bloque en `data/proc_data/annotations_inputs/pilot_<hash>/`.
   El `<hash>` deriva de muestra, prompt, libro, configuración y código, de modo que
   cualquier cambio crea una ejecución nueva.
4. **Autorización.** Ninguna llamada ocurre sin una entrada en
   `data/proc_data/llm_pilots/api_policy.json` cuyo `run_id`, rutas absolutas de
   input y output, proveedor, modelo, esfuerzo y `max_calls` coincidan con la
   ejecución.
5. **Ejecución.** `run_annotations(input_run_dir, output_root=..., execute=True)`
   de `features/llm_annotations/pipeline.py` lee solo los inputs congelados y
   escribe en `output/annotations/<run_id>/`.
6. **Exportación.** `results.parquet`, `annotations.parquet` y `status.json` se
   derivan de `results/<índice>.json`.

## Contrato de respuesta

Responses API (OpenAI) o Messages API (Bedrock/Anthropic), con esquema JSON
estricto. Por bloque: decisión global, anotaciones, flags y confianza. Cada
anotación incluye cita literal del bloque objetivo, número de aparición,
concepto del libro cerrado, orientación (`support`/`oppose`), justificación de una
o dos oraciones y confianza. Los offsets se calculan localmente en puntos de
código Unicode y se validan con el mismo contrato de la app manual. El programa
deriva la remisión a revisión (confianza media o baja, flags, orientaciones
opuestas de un mismo concepto). La justificación no se trata como evidencia del
razonamiento interno ni la confianza como probabilidad calibrada. Los criterios
de evidencia y comprensibilidad de las explicaciones se inspiran en
[NISTIR 8312](https://doi.org/10.6028/NIST.IR.8312): una justificación plausible
puede ser incorrecta y no demuestra fidelidad al mecanismo del modelo.

## Reintentos y fallos

- Hasta cuatro reintentos (cinco intentos) para errores de transporte o API,
  respuestas `incomplete` e `invalid_output`, contados en un único límite.
- Si el motivo es `max_output_tokens`, el siguiente intento duplica el tope
  (Luna: 32.768 → 65.536; Haiku: 65.536 → 128.000).
- El estado `started` se guarda antes de cada envío. Un bloque interrumpido no se
  reenvía solo, porque la llamada pudo cobrarse; `--release-interrupted` lo
  libera con un *retry seed* que conserva el intento usado.
- Un error del servidor que llega en medio del streaming (Messages API) trae el
  estado HTTP 200 de la conexión y se reintenta como un 5xx. La primera versión
  del runner de Haiku no lo reintentaba; los cuatro bloques afectados se
  reabrieron con `--release-stream-errors`, que conserva el resultado fallido en
  `stream_errors/` y un *retry seed* con el intento usado.
- Solo `completed` contiene una decisión válida. Ningún otro estado equivale a
  «sin declaraciones».
- Un bloqueo de proceso impide ejecutar el mismo lote dos veces a la vez.

## Ejecuciones que respaldan los resultados

| Ejecución | Input congelado | Output | Comando |
|---|---|---|---|
| Censo Luna-6 (`gpt-6-luna`, `max`, OpenAI) | `pilot_d4e0291b4df3fc0f5343` | `output/annotations/openai_gpt6luna_20261002` | `python -m features.llm_annotations.complete_openai_census [--execute]` |
| Réplica Haiku 5.5 (`global.anthropic.claude-haiku-5-5`, `max`, Bedrock `us-west-2`) | `pilot_cc90579cd758717a60d7` | `output/annotations/bedrock_haiku55_20261008` | `python -m features.llm_annotations.anthropic_census [--prepare\|--execute\|--release-stream-errors]` |

La réplica deriva cada request de los requests congelados del censo y verifica su
hash; solo cambia el envoltorio de la API. Bedrock rechaza `maxItems` y `minimum`,
que se quitan solo del esquema enviado; la validación local aplica el esquema
completo. Cada output cierra con un manifiesto (`openai_census_manifest.json`,
`haiku_census_manifest.json`) que solo se escribe cuando los 3.609 bloques están
completos.

## Replicación

- **Sin llamadas.** Los resultados guardados bastan para el análisis y la
  validación: `analysis.qmd` solo lee `output/annotations/`.
- **Repetir una ejecución.** Usar el input congelado, no regenerarlo: los
  `coding_chunks_long.parquet` cambiaron después del censo y `prepare_all`
  produciría otros requests. Se ejecuta `run_annotations` sobre la carpeta de
  input existente con un `output_root` nuevo, tras agregar a `api_policy.json`
  una entrada con esas rutas absolutas (también hay que actualizarlas si cambia
  la máquina).
- **Alcance.** Los modelos no son deterministas (temperatura predeterminada y
  razonamiento variable), así que una repetición reproduce el procedimiento, no
  las salidas exactas. Los snapshots (`prompt.md`, `codebook.json`,
  `output_schema.json`, `pipeline.py`, `requests/`) y sus hashes en
  `manifest.json` permiten verificar que el instrumento es el mismo. La réplica
  de Haiku no guarda `requests/`: registra el hash de cada request derivado y
  depende de los requests del censo. No se deben editar.

## Verificación

```bash
uv run python -m unittest discover -s tests -q
```

Las pruebas cubren citas exactas y repetidas, Unicode, vocabulario cerrado,
decisiones incoherentes, ejecuciones sin API, reanudación y fallos de
generación. La validez estructural no evalúa la calidad sustantiva.
