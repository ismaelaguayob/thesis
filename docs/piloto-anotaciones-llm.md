# Piloto de anotación LLM

El procedimiento completo, ejecutable por etapas, está en `annotations.qmd`.
El objetivo es depurar códigos y prompts mediante revisión diagnóstica con la
salida del modelo visible. Estas revisiones no constituyen validación humana ciega.

## Universo y muestra

- Fuente: los tres `data/proc_data/ley_*/coding_chunks_long.parquet` de la app.
- Universo elegible: 1.096 intervenciones, nueve sesiones, 3.609 bloques.
- Muestra histórica: 110 intervenciones (10,04%), 418 bloques, semilla `20260908`.
- El próximo piloto se prepara con el mismo diseño de la validación: cuotas
  proporcionales por `law_number × chamber × alignment × gender`, ajustadas a
  enteros por restos hasta `ceil(0.10 * N)`, con bloque como unidad primaria.
- Cada bloque sorteado es un objetivo. Sus contextos se mantienen desde el corpus
  completo, incluso si los bloques vecinos no fueron sorteados. Nunca cruzan de
  sesión.

El piloto histórico no usa el mismo diseño que la validación y se conserva solo
para diagnóstico del prompt. El próximo piloto usa bloque como unidad primaria y
conserva el estrato, la probabilidad y el peso calculados por el mismo selector de
la aplicación. Los conteos de códigos son descriptivos y no se interpretan como
prevalencias poblacionales ni como estimaciones de desempeño.

## Configuración y ejecución

`annotations.qmd` sigue fijado al piloto histórico
`pilot_f3a69c2f81c587271ef5`, con `EXECUTE_API=False`; el reporte nunca ejecuta la
API. La política autoriza solo lotes explícitos. Para autorizar uno se debe añadir
en `authorized_runs` una entrada cuyo ID,
directorio absoluto, modelo, esfuerzo y `max_calls` coincidan con el manifiesto;
si cualquiera difiere, el cliente no se crea. Renderizar el reporte histórico no
genera llamadas.

Instala las dependencias con `uv sync --locked` y dispone de Quarto CLI en el PATH.
La clave `OPENAI_API_KEY` debe estar en `.env` o en el entorno del proceso.
No se imprime ni se incluye en requests guardados, HTML o payloads del navegador.

```bash
# Solo carga resultados previos: no utiliza la clave ni llama a la API.
uv run quarto render annotations.qmd
```

Las variables `ANNOTATIONS_EXECUTE` y `ANNOTATIONS_PROMPT` no convierten este
reporte histórico en un ejecutor de nuevas variantes. Para preparar una nueva
muestra se usa `features.llm_annotations.pipeline.prepare_run`, con el servicio,
registros seleccionados, metadatos de muestreo, ruta del prompt y directorio de
salida. Sus valores predeterminados son `gpt-5.6-luna`, `effort="max"`,
`max_output_tokens=32768` y cuatro reintentos (cinco intentos totales).
`ANNOTATIONS_MODEL`, `ANNOTATIONS_MAX_RETRIES` y
`ANNOTATIONS_INCOMPLETE_MAX_OUTPUT_TOKENS` seleccionan desde `.env` el modelo,
entre cero y cuatro reintentos y el techo alternativo. Los valores efectivos
quedan congelados en el manifiesto. Preparar una ejecución es una operación local.
`run_annotations(run_dir, execute=True, limit=N)` solo genera si la política
permite esa ejecución; `limit=0` no envía nada y los límites negativos se rechazan.

La API usa Responses, `store=false` y esquema JSON estricto. El límite de salida
incluye razonamiento y texto visible. El piloto original utilizó `max` y 16.384
tokens: 109 respuestas se interrumpieron por agotamiento del límite. La
[guía de razonamiento de OpenAI](https://developers.openai.com/api/docs/guides/reasoning)
explica este comportamiento y recomienda reservar al menos 25.000 tokens al
comenzar a experimentar. El nuevo techo de 32.768 deja un margen adicional;
el modelo puede terminar antes. La [ficha de Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
admite esfuerzo `max` y hasta 128.000 tokens de salida. Estos ajustes reducen el
riesgo observado; ningún límite finito garantiza todas las respuestas futuras.

El SDK instalado es `openai==3.9.0`. El cliente usa un timeout de 600 segundos,
sin consulta previa al endpoint de modelos. El ejecutor aplica el número congelado
de reintentos como un único límite para fallos transitorios de conexión/API,
respuestas `incomplete` y salidas `invalid_output`. Solo se conserva la primera
salida válida; si se agota el límite, se descarta también el cuerpo del fallo final
y quedan únicamente su estado, diagnóstico, consumo y `attempt_count`. Un bloqueo
de proceso impide ejecutar el mismo lote simultáneamente. El estado `started` se
guarda antes de cada envío;
si el proceso se interrumpe, permanece visible y no se reenvía automáticamente.
Cuando el motivo de `incomplete` es `max_output_tokens`, el próximo intento duplica
el límite hasta `ANNOTATIONS_INCOMPLETE_MAX_OUTPUT_TOKENS` (65.536 por defecto).
Una ejecución sucesora puede continuar el contador sin copiar la respuesta errónea.

El documento desactiva el kernel persistente de Quarto para que cambios en las
variables de entorno se apliquen en cada renderizado. Si el entorno restringe las
carpetas de caché del usuario, asigna `UV_CACHE_DIR`, `IPYTHONDIR`,
`JUPYTER_CONFIG_DIR`, `JUPYTER_DATA_DIR`, `JUPYTER_RUNTIME_DIR`, `XDG_DATA_HOME`,
`XDG_CACHE_HOME` y `XDG_RUNTIME_DIR` a carpetas escribibles.

## Libro y prompt

`features/codebook/codebook_v0.3.xlsx` es la fuente editable vigente. Sus metadatos
internos declaran **0.4.0-pilot**, con 14 conceptos; el nombre del archivo se
conserva para compartir la misma configuración que la app. El JSON se sincroniza
mediante el conversor existente antes de cada preparación.

`prompts/annotations_pilot_v1_confidence.md` contiene las instrucciones activas y
editables. Cada ejecución
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

Cada ejecución nueva en `data/proc_data/annotations_inputs/pilot_<hash>/`
contiene:

- `manifest.json`: configuración, hashes, versiones de paquetes, tamaño y fecha.
- `sample.parquet`, `selected_blocks.parquet`, `strata.parquet`: muestra y cuotas
  de los nuevos pilotos; los artefactos históricos conservan sus nombres originales.
- `prompt.md`, `codebook.json`, `output_schema.json`: snapshots del instrumento.
- `pipeline.py`, `validation_contract.py`: snapshots de la implementación.
- `requests/00000.json`: request exacto sin autorización HTTP ni clave.
- `results/00000.json`: salida validada o, si falló, metadatos de diagnóstico y
  uso sin conservar el cuerpo erróneo.
- `results.parquet`, `annotations.parquet`, `status.json`: tablas y balance derivados.

Las tablas legibles se exportan además a `output/tables/annotations/` en CSV. El
piloto histórico permanece en `output/annotations/`. Solo `completed`
contiene una decisión estructuralmente validada. `invalid_output`, `incomplete`,
`error`, `transport_error`, `started` y `received` requieren inspección; `pending` significa
que no hay intento guardado. Ninguno equivale a `no_statements`.

Renderizar vuelve a leer resultados guardados y no reenvía intentos existentes,
incluso si fallaron. Esto evita repetir gasto automáticamente y permite estudiar
fallos del prompt. Si se modifica el prompt o programa, se crea una ejecución
nueva. No se deben editar manualmente los requests ni los snapshots congelados:
el procedimiento verifica sus hashes.

## Revisión en la app

```bash
uv run python -m features.manual_validation \
  --annotations-dir data/proc_data/annotations_inputs
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
