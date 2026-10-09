# Interfaz de muestreo y validación manual

## Propósito

Esta aplicación local permite construir una muestra reproducible de las leyes 21.735, 21.419 y 21.538, juntas o por separado, y codificar declaraciones delimitadas por un *span* textual, su concepto y su orientación de apoyo o rechazo. La unidad textual que recibe la persona o el LLM es un bloque objetivo formado por uno o más párrafos de una misma intervención, acompañado por los bloques inmediatamente anterior y siguiente.

La aplicación no llama a OpenAI ni a ningún otro servicio externo. La clave de API no se carga ni se envía al navegador. La modalidad manual permite depurar el libro de códigos y producir una referencia humana. La opción **Revisión de anotaciones LLM** abre una modalidad diagnóstica separada que lee las respuestas guardadas en `output/annotations/`, muestra modelo, input, output y códigos destacados, y guarda los juicios humanos sin modificar esas respuestas (ver [Revisión de anotaciones LLM](#revisión-de-anotaciones-llm)). La generación de esas respuestas se documenta en [el pipeline de anotación](pipeline-anotacion-llm.md).

## Iniciar la aplicación

Desde la raíz del repositorio:

```bash
uv run python -m features.manual_validation
```

Luego abrir <http://127.0.0.1:8765>. Para usar otro puerto:

```bash
uv run python -m features.manual_validation --port 8877
```

Por defecto la aplicación lee `data/proc_data/ley_*/coding_chunks_long.parquet`. La copia antigua en la raíz de `proc_data` no se incorpora, para evitar duplicar la ley 21.735. Los resultados se guardan como un JSON por sesión en:

```text
output/validation/
```

La ruta del corpus, el XLSX editable, el JSON derivado y el output se pueden reemplazar mediante `--source`, `--codebook-workbook`, `--codebook-json` y `--output-dir`. `--source` acepta la carpeta que contiene las subcarpetas `ley_*` o un único Parquet; `--codebook` se conserva como alias de `--codebook-json`. Los umbrales de segmentación se leen de los Parquet.

### Probar una ley y después otra

1. En **Ley de la muestra**, elige **Ley 21.419**, configura unidad primaria, tamaño, semilla, estrategia y dimensiones, y pulsa **Crear muestra y comenzar**. Solo se sortean unidades de esa ley.
2. Guarda las decisiones y pulsa **Cambiar sesión** para volver al inicio. Elige **Ley 21.538** y crea otra muestra. Ambas sesiones quedan guardadas por separado.
3. Para una muestra conjunta, selecciona **Todas las leyes**. La estrategia estratificada distribuye la muestra proporcionalmente entre el cruce de las dimensiones seleccionadas; la aleatoria simple sortea sobre todas las unidades primarias disponibles.

Las sesiones nuevas registran la ley seleccionada, el boletín de cada bloque, las rutas y checksums de los Parquet utilizados, y el snapshot con hash de `PARTY_ALIGNMENT`. La lista para reanudar y la pantalla de codificación muestran la ley. Las sesiones anteriores de la ley 21.735 siguen disponibles con su libro de códigos original.

El enlace [comenzar con la ley 21.419](http://127.0.0.1:8765/?law=21419) deja esa opción seleccionada, sin crear una sesión. Para la ley 21.538 se puede usar `?law=21538`.

## Flujo de datos

El procesamiento que consume la aplicación queda dividido en dos capas explícitas:

1. `proc.qmd` construye el corpus analítico y escribe `data/proc_data/ley_<número>/coding_chunks_long.parquet`.
2. `features/manual_validation/run.py` genera el JSON del libro desde el XLSX y crea el servicio local.
3. `features/manual_validation/service.py` lee los bloques definitivos, deriva la alineación desde `party_at_date`, adjunta el contexto, filtra la ley seleccionada y realiza el muestreo.
4. En la codificación manual, el navegador recibe únicamente los bloques muestreados y el snapshot del libro. Los nombres, partidos, identificadores y género permanecen fuera del payload. La revisión LLM puede mostrar la alineación y las demás categorías de estrato para filtrar diagnósticos, pero no recibe el partido ni el nombre del hablante.

La app utiliza los IDs, offsets y reglas de segmentación ya materializados en los Parquet. No descarga datos ni vuelve a segmentar las intervenciones.

## Procedimiento de codificación

1. Crear una sesión indicando ley, unidad primaria, tamaño, semilla, estrategia y dimensiones de estratificación. El identificador del codificador es opcional.
2. Leer el bloque anterior y el siguiente solo como contexto.
3. Leer el bloque objetivo. La interfaz no muestra ni recibe el nombre, el identificador, el partido o el género del hablante.
4. Seleccionar con el cursor el fragmento mínimo que contiene una afirmación completa.
5. Asignar un concepto y marcar `Apoyo` o `Rechazo` frente a ese concepto.
6. Agregar la declaración. Un bloque puede tener varios spans, y un mismo span puede relacionarse con más de un concepto y con orientaciones opuestas. Los spans ya agregados aparecen destacados en amarillo sobre el texto objetivo.
7. Cuando un fragmento sea útil para la interpretación, usar **Guardar pasaje destacado**. El título y la nota opcional se añaden a `pasajes-destacados.md` con la fuente y la marca `Codificación ciega`; esta acción no altera la codificación ni revela resultados del modelo.
8. Si no hay ninguna posición previsional codificable cubierta por el libro cerrado, marcar `Sin declaraciones codificables`; no se proponen conceptos nuevos desde esta interfaz.
9. Marcar `No es posible resolver el bloque` cuando la evidencia o el contexto no permiten decidir. Debe seleccionarse además una flag explicativa; se guarda `resolution_status=unresolved`, `decision=null` y el bloque queda fuera de los denominadores.
10. Abrir `Comentario general y calidad` cuando el bloque completo requiera una observación. Las flags disponibles son `Voto`, `Procedimental`, `Texto demasiado breve`, `Texto truncado`, `Contexto insuficiente`, `Problema de segmentación` y `Otro problema`. Los bloques marcados como voto o procedimiento se conservan, pero quedan fuera de los porcentajes y métricas de anotación.
11. Guardar y avanzar. Las sesiones incompletas pueden retomarse desde la pantalla inicial.

Las estrategias de legitimación quedan deliberadamente fuera de este instrumento y deberán validarse con otra muestra.

## Muestreo

La estrategia recomendada es `stratified`. La unidad primaria predeterminada es
**bloque de párrafos**. La interfaz también permite escoger:

- **intervención completa** (`utterance`), que expande cada selección a todos sus bloques; o
- **bloque de párrafos** (`block`), útil para calibraciones acotadas.

Las dimensiones seleccionables son ley, cámara, alineación política, género, tipo de actor, documento y longitud. La alineación se deriva de `party_at_date`, obtenido por persona y fecha de discusión. `PARTY_ALIGNMENT`, leída desde `.env`, enumera explícitamente los partidos de izquierda, centro, derecha y `nonpartisan`; un partido no listado queda como `unclassified`, no como centro. Los resultados históricos `not_found` o `ambiguous` forman `Sin dato`, mientras las funciones para las que no corresponde afiliación forman `No aplica`; ninguno se imputa al centro.

El valor predeterminado es `ley × cámara × alineación × género`, con una muestra inicial de 180 bloques. El tipo de actor permanece disponible y puede anexarse por `unit_id` después de congelar la referencia ciega. La asignación reserva una unidad para cada estrato no vacío y distribuye los cupos restantes mediante mayores restos, en proporción a las unidades restantes de cada estrato. El JSON conserva población, muestra, probabilidad de inclusión y peso inverso por estrato. El tamaño elegido debe ser al menos igual al número de estratos no vacíos.

La semilla hace que el sorteo sea reproducible para un corpus idéntico. `random` implementa muestreo aleatorio simple y registra una probabilidad común. Los valores ausentes forman la categoría explícita `Sin dato`. La cámara se determina a nivel de documento a partir de las funciones parlamentarias; cuando esas funciones faltan en un tercer trámite, se hereda la cámara del primer trámite del mismo proyecto.

La aplicación consume los bloques ya finalizados por `proc.qmd`; no vuelve a filtrar ni segmentar durante el muestreo. Las votaciones presentes en ese corpus se clasifican manualmente con las flags `Voto` o `Procedimental` y se registran con `evaluation_included=false`.

El procesamiento usa 100 palabras como objetivo y 150 como límite inicial. Al absorber restos breves de ambos lados, un bloque puede superar ese límite hasta el margen permitido por el esquema `coding-chunks-2.1.0`; el corpus actual llega a 194 palabras. Las intervenciones completas desde cinco palabras pueden conservarse. La versión 2.1 añade afiliación histórica sin modificar estas reglas textuales. Los bloques adyacentes sirven como contexto y nunca cruzan de un documento o sesión a otro.

### Validación ciega: estratificación por concepto predicho

La estrategia **Por concepto predicho (validación ciega)** sortea bloques a partir de una ejecución LLM completa de `output/annotations/<run_id>/` (`results.parquet` y `annotations.parquet`). Solo aparecen las ejecuciones que cubren todos los bloques del corpus actual y no tienen anotaciones pendientes de revisión (`concept_status=review` o concepto nulo, posibles en pilotos con libro abierto). Una propuesta fuera del libro no es un concepto, así que esas ejecuciones se rechazan en vez de convertir el valor nulo en un estrato.

- **Estratos.** Cada bloque con anotaciones pertenece al estrato de su concepto predicho menos frecuente en la ejecución, de modo que los conceptos raros no quedan absorbidos por los frecuentes. Los bloques sin anotaciones forman dos estratos: «sin anotaciones» y «sin anotaciones, marcado como voto o procedimiento».
- **Asignación.** Se fija una cuota para cada estrato sin anotaciones. Cada concepto recibe un mínimo, o todos sus bloques si tiene menos. El resto del tamaño se reparte entre los conceptos en proporción a los bloques que les quedan. Valores iniciales: 15 por concepto, 50 sin anotaciones y 15 de voto o procedimiento.
- **Dimensiones secundarias.** Dentro de cada estrato, la selección es sistemática sobre el marco ordenado por las dimensiones marcadas (estratificación implícita). Así la muestra se reparte entre ellas sin exigir una celda por combinación. Si se desmarcan todas, la selección dentro de cada estrato es aleatoria simple; si el campo no se envía, se usan ley, cámara, alineación y género.
- **Exclusión.** Por defecto se excluyen los bloques ya vistos con el mismo libro de códigos (mismo sha256): los ítems abiertos o completados en sesiones manuales y los revisados en el diagnóstico LLM. Los ítems sorteados pero nunca abiertos no cuentan, y las rondas hechas con otra versión del libro pertenecen a iteraciones anteriores del instrumento y no excluyen nada. Un bloque actual se excluye si su texto se solapa con un bloque visto de la misma intervención; los ítems sin offsets excluyen la intervención completa. La sesión registra qué sesiones y ejecuciones se usaron y cuáles se omitieron.
- **Ciego.** Los estratos se calculan en el servidor. La pantalla de codificación no recibe el concepto predicho, el estrato ni la ejecución. El JSON de la sesión registra la ejecución, los hashes de sus Parquet, la regla del estrato, la población y la muestra por estrato, la probabilidad de inclusión y las exclusiones, para estimar precisión y sensibilidad ponderadas.

## Libro de códigos

La fuente editable activa es `features/codebook/codebook_v5.xlsx` (versión interna 0.5.1-candidate, 16 conceptos, cerrado). Las definiciones, criterios de inclusión y exclusión y proposiciones de orientación están en ese archivo; su historia, en [la secuencia de validación](secuencia-validacion-instrumento.md). Las versiones anteriores se conservan sin cambios para reconstruir las rondas de calibración.

El JSON `features/codebook/codebook_v5.json` es derivado y no se edita. Se genera o comprueba con:

```bash
uv run python -m features.manual_validation.generate_codebook_json
uv run python -m features.manual_validation.generate_codebook_json --check
```

La aplicación lo regenera antes de iniciar. `Apoyo` significa que el actor afirma la proposición de orientación; `Rechazo`, que la niega, refuta o declara inaplicable. La interfaz no permite proponer conceptos: una razón fuera de alcance no se fuerza dentro del libro. Los campos históricos `concept_status` y `proposed_concept` se conservan para leer rondas antiguas.

Al crear una sesión, la aplicación congela una copia íntegra del libro y su SHA-256. No se debe editar el libro de una sesión ya iniciada.

## Contrato del JSON

Cada archivo se denomina `validation_<timestamp UTC>_<sufijo>.json`. Incluye:

- versión del esquema (`manual-validation-2.6.0`);
- timestamps UTC y `America/Santiago` de creación, apertura, actualización y finalización;
- checksum y ruta del corpus;
- snapshot completo y checksum del libro de códigos;
- unidad primaria, estrategia, semilla, dimensiones, tamaño, tabla de estratos y probabilidades de muestreo;
- bloque objetivo, rango de párrafos, offsets y segmentos dentro de la intervención original, incluidos los subsegmentos de párrafos extensos, junto con ambos contextos adyacentes y sus checksums;
- estado de resolución, decisión, inclusión en la evaluación, motivos de exclusión y número de revisión de cada bloque;
- comentario general y flags de calidad de cada unidad;
- cero o más anotaciones con offsets exactos, texto, checksum, concepto, orientación, nota y timestamps.

Una anotación con concepto existente adopta esta forma abreviada:

```json
{
  "span": {
    "start_char": 18,
    "end_char": 64,
    "text": "fragmento exacto de la intervención"
  },
  "concept_status": "in_codebook",
  "concept_id": "solidaridad_intergeneracional",
  "proposed_concept": null,
  "stance": "support"
}
```

En las sesiones nuevas `concept_status` permanece en `in_codebook` y
`proposed_concept` en `null`; esos campos se conservan para leer rondas históricas.

Los offsets se validan en el servidor: el texto enviado debe coincidir carácter por carácter con `target_text[start_char:end_char]`. Este mismo contrato debe imponerse después a la respuesta estructurada del LLM. Cada unidad conserva `unit_id`, `utterance_id`, `paragraph_start`, `paragraph_end`, `paragraph_count`, `source_segments` y sus offsets de origen. Los metadatos de identidad pueden reincorporarse únicamente después de la anotación, mediante `utterance_id`, para construir la red discursiva sin exponerlos durante la decisión de codificación.

## Revisión de anotaciones LLM

```bash
uv run python -m features.manual_validation \
  --annotations-input-dir data/proc_data/annotations_inputs \
  --annotations-results-dir output/annotations
```

La opción **Revisión de anotaciones LLM** (o <http://127.0.0.1:8765/llm.html>) muestra modelo, esfuerzo, versión del libro, input y output completos, contexto, evidencia destacada y códigos. Se puede filtrar por ley, bloques sin revisión, remisión a revisión derivada por el programa, ausencia de declaraciones o incidencias de ejecución. Cada anotación y cada bloque se acepta, se marca para cambios o se descarta; los códigos no aceptados exigen una categoría (span, concepto, orientación, justificación, contexto, fuera de alcance, frontera del libro u otro) y un comentario.

Es una modalidad diagnóstica: el revisor ve la salida del modelo, por lo que no constituye validación ciega. Los juicios quedan en `output/annotation_reviews/<run_id>/<índice>.json`, con hash de la respuesta y control de revisión, sin modificar los resultados del LLM. `--reviews-dir` permite otra carpeta.

Con una sola codificadora no es posible estimar confiabilidad intercoder humana; sí estabilidad intracoder, recodificando sin consultar las respuestas previas un subconjunto aleatorio después de un intervalo.

## Pruebas

```bash
uv run python -m unittest discover -s tests -p 'test_manual_validation.py' -v
```

Las pruebas cubren filtros del corpus, retención de votaciones, formación de bloques, contextos adyacentes, sincronía XLSX→JSON, reproducibilidad del muestreo, ocultamiento de identidad, spans exactos, resaltado, múltiples declaraciones del libro cerrado, ausencia de declaraciones, flags, comentarios generales, timestamps, persistencia y endpoints HTTP.
