# Interfaz de muestreo y validación manual

## Propósito

Esta aplicación local permite construir una muestra reproducible del corpus del boletín 15480-13 y codificar declaraciones delimitadas por un *span* textual, su concepto y su orientación de apoyo o rechazo. La unidad textual que recibe la persona o el LLM es un bloque objetivo formado por uno o más párrafos de una misma intervención, acompañado por los bloques inmediatamente anterior y siguiente.

La aplicación no llama a OpenAI ni a ningún otro servicio externo. La clave de API no se carga ni se envía al navegador. Su objetivo es depurar el libro de códigos y producir una referencia humana antes de diseñar el prompt y evaluar las anotaciones automáticas.

## Iniciar la aplicación

Desde la raíz del repositorio:

```bash
uv run python -m features.manual_validation
```

Luego abrir <http://127.0.0.1:8765>. Para usar otro puerto:

```bash
uv run python -m features.manual_validation --port 8877
```

Por defecto la aplicación consume `data/proc_data/speech_df.parquet`. Los resultados se guardan como un JSON por sesión en:

```text
output/validation/
```

La ruta del corpus, el XLSX editable, el JSON derivado, el output, el boletín y los umbrales también se pueden reemplazar mediante `--source`, `--codebook-workbook`, `--codebook-json`, `--output-dir`, `--bill-number`, `--min-words`, `--short-paragraph-words`, `--target-block-words` y `--max-block-words`. `--codebook` se conserva como alias de `--codebook-json`.

## Flujo de datos

El procesamiento que consume la aplicación queda dividido en dos capas explícitas:

1. `proc.qmd` construye el corpus analítico y escribe `data/proc_data/speech_df.parquet`.
2. `features/manual_validation/run.py` genera el JSON del libro desde el XLSX y crea el servicio local.
3. `features/manual_validation/service.py` lee el parquet, aplica los filtros de participación, construye los bloques de párrafos, adjunta el contexto y realiza el muestreo.
4. El navegador recibe únicamente las unidades muestreadas y el snapshot del libro. Los nombres, partidos, identificadores y género de los hablantes permanecen fuera del payload.

La transformación específica de la aplicación está en Python y se prueba de manera independiente. El parquet conserva sus intervenciones originales, lo que permite cambiar la regla de segmentación sin regenerar ni sobrescribir el corpus.

## Procedimiento de codificación

1. Crear una sesión indicando tamaño, semilla y estrategia de muestreo. El identificador del codificador es opcional.
2. Leer el bloque anterior y el siguiente solo como contexto.
3. Leer el bloque objetivo. La interfaz no muestra ni recibe el nombre, el identificador, el partido o el género del hablante.
4. Seleccionar con el cursor el fragmento mínimo que contiene una afirmación completa.
5. Asignar un concepto y marcar `Apoyo` o `Rechazo` frente a ese concepto.
6. Usar `Revisar: justificación ausente del libro` cuando la declaración exprese una justificación normativa que todavía no esté contemplada. El nombre tentativo y la nota son opcionales, aunque resultan útiles al depurar el libro.
7. Agregar la declaración. Un bloque puede tener varios spans, y un mismo span puede relacionarse con más de un concepto. Los spans ya agregados o guardados aparecen destacados en amarillo sobre el texto objetivo.
8. Si no hay ninguna posición previsional codificable, marcar `Sin declaraciones codificables`. Esta opción no debe utilizarse cuando existe una declaración cuyo concepto falta: para ese caso corresponde `Revisar`.
9. Abrir `Comentario general y calidad` cuando el bloque completo requiera una observación. Las flags disponibles son `Voto`, `Procedimental`, `Texto demasiado breve`, `Texto truncado`, `Contexto insuficiente`, `Problema de segmentación` y `Otro problema`.
10. Guardar y avanzar. Las sesiones incompletas pueden retomarse desde la pantalla inicial.

Las estrategias de legitimación quedan deliberadamente fuera de este instrumento y deberán validarse con otra muestra.

## Muestreo

La estrategia recomendada es `stratified`. Forma estratos al cruzar:

- documento o sesión (`document_uri`);
- longitud del bloque: hasta 75 palabras, entre 76 y 500, y más de 500.

Luego recorre los estratos en rondas hasta completar el tamaño solicitado. Esto evita que las sesiones más extensas monopolicen una muestra piloto y asegura alguna variación de longitud. La semilla hace que el sorteo sea reproducible para un corpus idéntico. `random` implementa un muestreo aleatorio simple como alternativa.

Antes del muestreo se mantienen solo filas `kind = participation` del boletín elegido. Cuando existe la columna, se exige `analysis_included = true`, con una excepción explícita para las secciones `Votacion`, que el procesamiento anterior había marcado como excluidas. También se excluyen preámbulos y contenidos vacíos. Las secciones de votación permanecen así en el universo y se clasifican manualmente con las flags `Voto` o `Procedimental` cuando carecen de discurso sustantivo.

Cada intervención se separa en los párrafos delimitados por saltos de línea. Un párrafo con 50 palabras o más forma por defecto su propio bloque. Los párrafos menores de 50 palabras se agregan preferentemente al bloque anterior de la misma intervención mientras el resultado no exceda 150 palabras; así, enumeraciones y precisiones breves permanecen con la proposición que desarrollan. Cuando no existe un bloque anterior compatible, se acumulan hacia una extensión objetivo de 100 palabras.

El máximo de 150 palabras es estricto. Un párrafo que por sí solo lo excede se divide primero por límites de oración y, únicamente si una oración continúa siendo demasiado larga, por un límite entre palabras. Un residuo breve solo se agrega a otro bloque cuando la suma respeta el máximo; en caso contrario permanece separado. Las intervenciones completas con menos de 50 palabras pueden conservarse como una unidad, mientras el umbral residual de cinco palabras descarta unidades extremadamente breves. Los bloques adyacentes sirven como contexto y nunca cruzan de un documento o sesión a otro.

## Libro de códigos

La fuente editable activa está en `data/codebook/codebook_v0.3.xlsx`. Las versiones 0.1 y 0.2 se conservan sin cambios para reconstruir las rondas anteriores. Todas contienen las hojas `README`, `Metadatos` y `Conceptos`.

La versión conceptual 0.4.0 está diseñada para analizar *discourse coalitions*. Sus conceptos representan justificaciones normativas empleadas para apoyar o rechazar una posición previsional. Una descripción factual, un diagnóstico o una preferencia por un instrumento que carezca de justificación se marca como `Sin declaraciones codificables`.

Los catorce conceptos activos son:

- capitalización individual como regla de autofinanciamiento;
- propiedad individual de los fondos;
- reciprocidad contributiva;
- control y responsabilidad individual;
- actitud del beneficiario;
- identidad y pertenencia grupal;
- necesidad material;
- igualdad y universalismo;
- conciencia de costos;
- solidaridad intergeneracional;
- ineficiencia y riesgo estatal;
- previsión como mercado, negocio e incentivos;
- ilegitimidad del origen dictatorial;
- acuerdos y moderación democrática.

`Suficiencia de las pensiones` se retiró porque describía un resultado deseable o un diagnóstico. `Capitalización individual` se reincorpora con una frontera estricta: codifica que las cotizaciones deben ingresar a cuentas individuales y financiar la pensión de su titular. La mención descriptiva al sistema AFP sigue fuera.

`Reciprocidad contributiva` no se limita al monto o al acceso al beneficio. El trabajo, las cotizaciones o el esfuerzo contributivo pueden generar un título moral para recibir, conservar o controlar recursos y protección previsional. Por ello, “quien cotizó más debe recibir más” y “no es justo hacer solidaridad con el esfuerzo de los trabajadores” expresan reciprocidad. La capitalización identifica la regla institucional sobre el destino individual del aporte; reciprocidad identifica el merecimiento derivado del aporte. Ambos códigos pueden coexistir cuando una declaración formula las dos proposiciones.

`Conciencia de costos como restricción de gasto` reemplazó a `Sostenibilidad financiera`. Su proposición de orientación afirma que una reforma o expansión previsional es demasiado costosa, carece de financiamiento sostenible o excede la capacidad fiscal del Estado. Por tanto, `Apoyo` corresponde a afirmar esa restricción y `Rechazo` a sostener que la medida es sostenible, está bien financiada o cabe dentro de la capacidad fiscal.

Una afirmación sobre la sostenibilidad financiera presente o futura puede codificarse aunque no incluya montos, siempre que funcione como razón para limitar, rechazar o defender la reforma. Esta regla conserva como válida la codificación realizada en el ítem 13 de la ronda anterior.

`Solidaridad intergeneracional` registra la responsabilidad compartida entre cohortes activas y jubiladas. Incluye transferencias o distribución de riesgos entre generaciones y sus refutaciones explícitas. Las transferencias intrageneracionales, las compensaciones de género y los argumentos de igualdad, universalidad o necesidad se asignan a su criterio específico cuando el texto no afirma una relación entre generaciones. La mención aislada de un mecanismo solidario o un fondo común tampoco basta para aplicar el código.

`Previsión como mercado, negocio e incentivos` reúne defensas y críticas de la competencia, inversión financiera, rentabilidad privada, lucro e incentivos de mercado. Incluye el argumento de que un beneficio reduce trabajo, productividad, ahorro o formalidad. Las comisiones abusivas se codifican aquí cuando funcionan como crítica a una extracción o ganancia privada; un porcentaje descriptivo de comisión queda fuera.

`Ilegitimidad del origen dictatorial` registra argumentos que vinculan el origen autoritario, coercitivo o engañoso del sistema con su legitimidad actual. Las fechas históricas y las críticas contemporáneas sin ese vínculo se excluyen.

`Acuerdos y moderación democrática` registra la valoración normativa del compromiso entre posiciones contrapuestas, la política de los acuerdos y el rechazo de extremos o maximalismos como bases de una reforma legítima. No incluye la mera existencia de una negociación, la eficacia técnica de un sistema mixto ni las apelaciones a preferencias ciudadanas, consulta o mayoría que no expresan compromiso entre posiciones. Estas últimas se mantienen como posible candidato inductivo de responsividad democrática.

No se añadió un código de progresividad tributaria debido a su baja recurrencia. Un nuevo caso puede registrarse con nota o `Revisar` para evaluar su repetición en una ronda posterior.

El JSON `data/codebook/codebook_v0.3.json` es un archivo derivado y no debe editarse directamente. Se genera o comprueba con:

```bash
uv run python -m features.manual_validation.generate_codebook_json
uv run python -m features.manual_validation.generate_codebook_json --check
```

La aplicación ejecuta la generación automáticamente antes de iniciar. Cada concepto contiene familia, base teórica, definición, proposición de orientación y criterios de inclusión y exclusión. `Apoyo` significa que el actor afirma la proposición de orientación; `Rechazo` significa que la niega, refuta o declara inaplicable.

La inducción se mantiene dentro del objeto teórico. `Revisar` se utiliza cuando el párrafo expresa una justificación normativa explícita que falta en el libro. El codificador propone un nombre y deja una nota. Las propuestas se agrupan después de terminar la ronda y un nuevo código se incorpora únicamente cuando presenta recurrencia y alcance distinguible. Para depurar el instrumento:

1. terminar una muestra pequeña;
2. revisar en el JSON los registros `concept_status = review`, además de notas y desacuerdos conceptuales observados;
3. modificar definiciones o agregar conceptos en una copia versionada del XLSX;
4. incrementar `version`, generar el JSON correspondiente y ejecutar una sesión nueva.

No se debe editar el libro incorporado dentro de una sesión ya iniciada. Al crearla, la aplicación congela una copia íntegra del libro y su SHA-256, lo que permite reconstruir exactamente los criterios disponibles para cada decisión.

## Contrato del JSON

Cada archivo se denomina `validation_<timestamp UTC>_<sufijo>.json`. Incluye:

- versión del esquema (`manual-validation-2.2.0`);
- timestamps UTC y `America/Santiago` de creación, apertura, actualización y finalización;
- checksum y ruta del corpus;
- snapshot completo y checksum del libro de códigos;
- estrategia, semilla, tamaño y estrato de muestreo;
- bloque objetivo, rango de párrafos, offsets y segmentos dentro de la intervención original —incluidos subsegmentos cuando un párrafo excede el máximo—, junto con ambos contextos adyacentes y sus checksums;
- estado, decisión y número de revisión de cada intervención;
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

Una declaración que requiere ampliar el libro usa `concept_status = review`, `concept_id = null` y, opcionalmente, `proposed_concept`.

Los offsets se validan en el servidor: el texto enviado debe coincidir carácter por carácter con `target_text[start_char:end_char]`. Este mismo contrato debe imponerse después a la respuesta estructurada del LLM. Cada unidad conserva `unit_id`, `utterance_id`, `paragraph_start`, `paragraph_end`, `paragraph_count`, `source_segments` y sus offsets de origen. Los metadatos de identidad pueden reincorporarse únicamente después de la anotación, mediante `utterance_id`, para construir la red discursiva sin exponerlos durante la decisión de codificación.

## Secuencia recomendada para el piloto

1. **Calibración cognitiva:** 15–20 intervenciones para identificar conceptos faltantes, spans demasiado amplios y reglas ambiguas. No usar esta tanda para estimar desempeño.
2. **Depuración v0.3:** revisar todos los casos `review`, consolidar conceptos equivalentes y agregar ejemplos positivos y negativos.
3. **Piloto humano:** una muestra nueva de 40–60 intervenciones, conservada como referencia independiente.
4. **Prompt del LLM:** entregar el bloque anterior, el bloque objetivo, el bloque siguiente y el mismo snapshot del libro; exigir el mismo esquema de spans, conceptos y orientación.
5. **Evaluación:** comparar primero detección de declaraciones y offsets; luego concepto y orientación, reportando métricas por concepto y no solo un promedio global.

Con una sola codificadora no es posible estimar confiabilidad intercoder humana. Sí es posible documentar estabilidad intracoder: volver a codificar, sin consultar las respuestas previas, un subconjunto aleatorio de la muestra después de un intervalo y comparar ambas rondas.

## Pruebas

```bash
uv run python -m unittest discover -s tests -p 'test_manual_validation.py' -v
```

Las pruebas cubren filtros del corpus, retención de votaciones, formación de bloques, contextos adyacentes, sincronía XLSX→JSON, reproducibilidad del muestreo, ocultamiento de identidad, spans exactos, resaltado, múltiples declaraciones, `review`, ausencia de declaraciones, flags, comentarios generales, timestamps, persistencia y endpoints HTTP.
