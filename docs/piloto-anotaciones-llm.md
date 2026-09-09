# Piloto de anotación LLM

El procedimiento completo, ejecutable por etapas, está en `annotations.qmd`.
El objetivo es depurar códigos y prompts mediante revisión diagnóstica con la
salida del modelo visible. Estas revisiones no constituyen validación humana ciega.

## Universo y muestra

- Fuente: los tres `data/proc_data/ley_*/coding_chunks_long.parquet` de la app.
- Universo elegible: 1.096 intervenciones, nueve sesiones, 3.609 bloques.
- Muestra: 110 intervenciones (10,04%), 418 bloques, semilla `20260908`.
- Cuotas proporcionales por `law_number × document_uri`, ajustadas a enteros por
  restos hasta `ceil(0.10 * N)`, con un mínimo de una intervención por sesión.
- Dentro de cada cuota: `sample_records` de la app con rondas por longitud,
  aplicada al total de palabras de la intervención: ≤75, 76–500 y >500.
- Expansión: todos los bloques de cada intervención sorteada. Los contextos se
  mantienen desde el corpus completo, incluso si la intervención vecina no fue
  sorteada. Nunca cruzan de sesión.

La app manual sorteaba **bloques** por sesión y longitud. Este piloto adapta la
unidad del sorteo a **intervenciones**, como exige el 10%, y agrega cuotas
proporcionales por ley y sesión. El sorteo interior por longitud es equilibrado y
no proporcional. Los conteos de códigos son descriptivos de este piloto y no se
interpretan como prevalencias poblacionales ni como estimaciones de desempeño.

## Configuración y ejecución

**Estado actual:** el usuario detuvo el gasto de API. `annotations.qmd` está fijado
a `pilot_f3a69c2f81c587271ef5`, con `EXECUTE_API=False`, y la política
`data/proc_data/llm_pilots/api_policy.json` bloquea llamadas del ejecutor. Los
comandos de generación siguientes documentan el procedimiento original y no
reactivan la API en esta versión. El reporte se renderiza completamente sin API.

Instala las dependencias con `uv sync --locked` y dispone de Quarto CLI en el PATH.
La clave `OPENAI_API_KEY` debe estar en `.env` o en el entorno del proceso.
No se imprime ni se incluye en requests guardados, HTML o payloads del navegador.

```bash
# Solo carga resultados previos: no utiliza la clave ni llama a la API.
uv run quarto render annotations.qmd

# Ejecuta todos los bloques sin intento guardado.
ANNOTATIONS_EXECUTE=1 uv run quarto render annotations.qmd

# Prueba inicial con el primer bloque pendiente.
ANNOTATIONS_EXECUTE=1 ANNOTATIONS_LIMIT=1 uv run quarto render annotations.qmd

# Variante: la misma muestra y un nuevo prompt manual.
ANNOTATIONS_PROMPT=prompts/mi_variante.md ANNOTATIONS_EXECUTE=1 uv run quarto render annotations.qmd
```

`ANNOTATIONS_WORKERS` fija la concurrencia (6 por defecto, máximo 16).
`ANNOTATIONS_LIMIT` limita solicitudes pendientes, no el tamaño de la muestra.
La API usa Responses con `gpt-5.6-luna`, `reasoning.effort=max`, `store=false`,
esquema JSON estricto y máximo de 16.384 tokens de salida por bloque, incluido el
razonamiento. No hay sustitución automática de modelo ni `temperature` o semilla
de generación. El muestreo es determinista; una nueva generación puede variar.
El proceso consulta acceso al modelo antes de solicitar anotaciones. Cada llamada
puede aplicar hasta dos reintentos del SDK ante errores transitorios.

El documento desactiva el kernel persistente de Quarto para que cambios en las
variables de entorno se apliquen en cada renderizado. Si el entorno restringe las
carpetas de caché del usuario, asigna `UV_CACHE_DIR`, `IPYTHONDIR`,
`JUPYTER_CONFIG_DIR`, `JUPYTER_DATA_DIR`, `JUPYTER_RUNTIME_DIR`, `XDG_DATA_HOME`,
`XDG_CACHE_HOME` y `XDG_RUNTIME_DIR` a carpetas escribibles.

## Libro y prompt

`data/codebook/codebook_v0.3.xlsx` es la fuente editable vigente. Sus metadatos
internos declaran **0.4.0-pilot**, con 14 conceptos; el nombre del archivo se
conserva para compartir la misma configuración que la app. El JSON se sincroniza
mediante el conversor existente antes de cada preparación.

`prompts/annotations_pilot.md` contiene las instrucciones editables. Cada ejecución
congela el prompt y el libro completos. Un ID derivado de hashes separa variantes
de prompt, libro, muestra, configuración y programa. Cambiar el código del
procedimiento también crea otra ejecución, sin sobrescribir la original.

## Contrato de respuesta y explicación

El modelo devuelve decisión global, anotaciones, flags, límites y necesidad de
revisión humana. Cada declaración incluye cita exacta, número de aparición,
concepto, orientación y justificación. Los offsets se calculan localmente, en
caracteres Unicode, y se validan mediante el contrato de la app manual. La vista
usa puntos de código Unicode al destacar texto, incluso si hay caracteres fuera
del plano básico como emojis.

Las justificaciones contienen criterio específico del libro (`definition`,
`orientation_anchor` o `include:N`), fundamento del código y orientación,
alternativas relevantes, citas de contexto utilizadas y ambigüedades. `review`
se reserva para un concepto normativo ausente del libro. La duda entre conceptos
existentes se registra como incertidumbre y necesidad de revisión.

La explicación aplica criterios de evidencia y comprensibilidad inspirados en
[NISTIR 8312](https://doi.org/10.6028/NIST.IR.8312). Una justificación generada puede
ser plausible e incorrecta; no demuestra fidelidad al mecanismo interno del modelo.
No se solicitan cadenas de pensamiento ni se trata la incertidumbre declarada
como una probabilidad calibrada.

## Artefactos y fallos

Cada `output/annotations/pilot_<hash>/` contiene:

- `manifest.json`: configuración, hashes, versiones de paquetes, tamaño y fecha.
- `sample.parquet`, `selected_utterances.parquet`, `strata.parquet`: muestra y cuotas.
- `prompt.md`, `codebook.json`, `output_schema.json`: snapshots del instrumento.
- `pipeline.py`, `validation_contract.py`: snapshots de la implementación.
- `requests/00000.json`: request exacto sin autorización HTTP ni clave.
- `results/00000.json`: respuesta íntegra, texto de salida, validación y uso de tokens.
- `results.parquet`, `annotations.parquet`, `status.json`: tablas y balance derivados.

Las tablas legibles se exportan además a `output/tables/annotations/` en CSV.
Las respuestas recibidas se guardan antes de normalizarlas. Solo `completed`
contiene una decisión estructuralmente validada. `invalid_output`, `incomplete`,
`error`, `transport_error` y `received` requieren inspección; `pending` significa
que no hay intento guardado. Ninguno equivale a `no_statements`.

Renderizar vuelve a leer resultados guardados y no reenvía intentos existentes,
incluso si fallaron. Esto evita repetir gasto automáticamente y permite estudiar
fallos del prompt. Si se modifica el prompt o programa, se crea una ejecución
nueva. No se deben editar manualmente los requests ni los snapshots congelados:
el procedimiento verifica sus hashes.

## Revisión en la app

```bash
uv run python -m features.manual_validation
```

Entra en **Revisión de anotaciones LLM**. Puedes filtrar por ley, bloques sin
revisión, necesidad de revisión señalada por el modelo, ausencia de declaraciones
o incidencias de ejecución. El botón Actualizar incorpora respuestas nuevas si
el piloto sigue ejecutándose.

La vista presenta modelo solicitado/devuelto, esfuerzo, versión del libro,
input/output completos, contexto, evidencia destacada y código. Los spans
solapados conservan todos sus códigos en la leyenda y en las tarjetas de
justificación. Cada anotación y cada bloque se acepta, marca para cambios o
descarta. La corrección propuesta se escribe en el comentario. Las omisiones se
registran como problema del bloque. Para aceptar un bloque deben aceptarse sus
anotaciones; una salida inválida no se puede aceptar como válida.

Los juicios quedan en `output/annotation_reviews/<run_id>/<índice>.json`, con hash
de la respuesta, identificador opcional del revisor y control de revisión para
rechazar cambios obsoletos. No alteran los resultados del LLM ni las sesiones
manuales anteriores. Los argumentos `--annotations-dir` y `--reviews-dir` permiten
usar otras carpetas, por ejemplo para pruebas de interfaz.

## Verificación

```bash
uv run python -m unittest discover -s tests -q
```

Las pruebas del piloto comprueban cuotas, citas exactas y repetidas, Unicode,
criterios inexistentes, contexto inventado, decisiones incoherentes, conceptos
nuevos, exclusión de identidad en el input, ejecuciones sin API, reanudación,
fallos de generación, variantes de prompt y persistencia de revisiones sin
modificar respuestas. La validez estructural no evalúa la calidad sustantiva.

## Balance y manifiesto offline

El balance de la ejecución está al final de `annotations.qmd` y en su HTML.
`data/proc_data/llm_pilots/pilot_f3a69c2f81c587271ef5/manifest.json` registra consumo
confirmado, cobertura y métricas con sus denominadores. Los Parquet de la misma
carpeta permiten auditar cada respuesta y las tablas derivadas. El total incluye
la prueba inicial archivada; no presupone que intentos sin respuesta persistida
tengan consumo cero. No contiene una estimación de precisión, recall ni F1.
