# Interfaz de muestreo y validación manual

## Propósito

Esta aplicación local permite construir una muestra reproducible del corpus del boletín 15480-13 y codificarla siguiendo la misma unidad de análisis que utilizará posteriormente el LLM: una declaración delimitada por un *span* textual, su concepto y su orientación de apoyo o rechazo.

La aplicación no llama a OpenAI ni a ningún otro servicio externo. La clave de API no se carga ni se envía al navegador. Su objetivo es depurar el libro de códigos y producir una referencia humana antes de diseñar el prompt y evaluar las anotaciones automáticas.

## Iniciar la aplicación

Desde la raíz del repositorio:

```bash
uv run python scripts/run_manual_validation.py
```

Luego abrir <http://127.0.0.1:8765>. Para usar otro puerto:

```bash
uv run python scripts/run_manual_validation.py --port 8877
```

Por defecto la aplicación busca primero `data/proc_data/speech_df.parquet` y luego `data/speech_df.parquet`. Los resultados se guardan como un JSON por sesión en:

```text
data/proc_data/validation/
```

La ruta del corpus, el libro de códigos, el output y el boletín también se pueden reemplazar mediante `--source`, `--codebook`, `--output-dir` y `--bill-number`.

## Procedimiento de codificación

1. Crear una sesión indicando tamaño, semilla y estrategia de muestreo. El identificador del codificador es opcional.
2. Leer la intervención anterior solo como contexto.
3. Leer la intervención objetivo. La interfaz no muestra ni recibe el nombre, el identificador, el partido o el género del hablante.
4. Seleccionar con el cursor el fragmento mínimo que contiene una afirmación completa.
5. Asignar un concepto y marcar `Apoyo` o `Rechazo` frente a ese concepto.
6. Usar `Revisar: concepto ausente del libro` cuando la declaración sí tenga un objeto conceptual, pero este todavía no esté contemplado. El nombre tentativo y la nota son opcionales, aunque resultan útiles al depurar el libro.
7. Agregar la declaración. Una intervención puede tener varios spans, y un mismo span puede relacionarse con más de un concepto.
8. Si no hay ninguna posición previsional codificable, marcar `Sin declaraciones codificables`. Esta opción no debe utilizarse cuando existe una declaración cuyo concepto falta: para ese caso corresponde `Revisar`.
9. Guardar y avanzar. Las sesiones incompletas pueden retomarse desde la pantalla inicial.

Las estrategias de legitimación quedan deliberadamente fuera de este instrumento y deberán validarse con otra muestra.

## Muestreo

La estrategia recomendada es `stratified`. Forma estratos al cruzar:

- documento o sesión (`document_uri`);
- longitud de la intervención: hasta 75 palabras, entre 76 y 500, y más de 500.

Luego recorre los estratos en rondas hasta completar el tamaño solicitado. Esto evita que las sesiones más extensas monopolicen una muestra piloto y asegura alguna variación de longitud. La semilla hace que el sorteo sea reproducible para un corpus idéntico. `random` implementa un muestreo aleatorio simple como alternativa.

Antes del muestreo se mantienen solo filas `kind = participation` del boletín elegido y, cuando existe la columna, `analysis_included = true`. También se excluyen preámbulos, secciones de votación y contenidos vacíos. La intervención anterior corresponde a la participación precedente dentro del mismo documento filtrado; nunca cruza de una sesión a otra.

## Libro de códigos

La versión inicial está en `config/codebook_v0.1.json`. Sus diez conceptos se derivan del planteamiento actual de la tesis:

- capitalización individual;
- propiedad individual de los fondos;
- reciprocidad contributiva;
- control y responsabilidad individual;
- actitud del beneficiario;
- identidad y pertenencia grupal;
- sostenibilidad financiera;
- solidaridad;
- suficiencia de las pensiones;
- necesidad material.

Esta versión es un borrador de arranque, no un instrumento cerrado. Cada concepto contiene definición y criterios de inclusión y exclusión. Para depurarlo:

1. terminar una muestra pequeña;
2. revisar en el JSON los registros `concept_status = review`, además de notas y desacuerdos conceptuales observados;
3. modificar definiciones o agregar conceptos en una copia nueva, por ejemplo `codebook_v0.2.json`;
4. incrementar `version` y ejecutar una sesión nueva pasando `--codebook config/codebook_v0.2.json`.

No se debe editar el libro incorporado dentro de una sesión ya iniciada. Al crearla, la aplicación congela una copia íntegra del libro y su SHA-256, lo que permite reconstruir exactamente los criterios disponibles para cada decisión.

## Contrato del JSON

Cada archivo se denomina `validation_<timestamp UTC>_<sufijo>.json`. Incluye:

- versión del esquema (`manual-validation-1.0.0`);
- timestamps UTC y `America/Santiago` de creación, apertura, actualización y finalización;
- checksum y ruta del corpus;
- snapshot completo y checksum del libro de códigos;
- estrategia, semilla, tamaño y estrato de muestreo;
- texto objetivo y contexto anterior, con sus checksums;
- estado, decisión y número de revisión de cada intervención;
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
  "concept_id": "solidaridad",
  "proposed_concept": null,
  "stance": "support"
}
```

Una declaración que requiere ampliar el libro usa `concept_status = review`, `concept_id = null` y, opcionalmente, `proposed_concept`.

Los offsets se validan en el servidor: el texto enviado debe coincidir carácter por carácter con `target_text[start_char:end_char]`. Este mismo contrato debe imponerse después a la respuesta estructurada del LLM. Los metadatos de identidad pueden reincorporarse únicamente después de la anotación, mediante `utterance_id`, para construir la red discursiva sin exponerlos durante la decisión de codificación.

## Secuencia recomendada para el piloto

1. **Calibración cognitiva:** 15–20 intervenciones para identificar conceptos faltantes, spans demasiado amplios y reglas ambiguas. No usar esta tanda para estimar desempeño.
2. **Depuración v0.2:** revisar todos los casos `review`, consolidar conceptos equivalentes y agregar ejemplos positivos y negativos.
3. **Piloto humano:** una muestra nueva de 40–60 intervenciones, conservada como referencia independiente.
4. **Prompt del LLM:** entregar solo la intervención anterior, la intervención objetivo y el mismo snapshot del libro; exigir el mismo esquema de spans, conceptos y orientación.
5. **Evaluación:** comparar primero detección de declaraciones y offsets; luego concepto y orientación, reportando métricas por concepto y no solo un promedio global.

Con una sola codificadora no es posible estimar confiabilidad intercoder humana. Sí es posible documentar estabilidad intracoder: volver a codificar, sin consultar las respuestas previas, un subconjunto aleatorio de la muestra después de un intervalo y comparar ambas rondas.

## Pruebas

```bash
uv run python -m unittest discover -s tests -p 'test_manual_validation.py' -v
```

Las pruebas cubren filtros del corpus, contexto anterior, reproducibilidad del muestreo, ocultamiento de identidad, spans exactos, múltiples declaraciones, `review`, ausencia de declaraciones, timestamps, persistencia y endpoints HTTP.
