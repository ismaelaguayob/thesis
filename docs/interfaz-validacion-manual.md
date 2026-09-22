# Interfaz de muestreo y validación manual

## Propósito

Esta aplicación local permite construir una muestra reproducible de las leyes 21.735, 21.419 y 21.538, juntas o por separado, y codificar declaraciones delimitadas por un *span* textual, su concepto y su orientación de apoyo o rechazo. La unidad textual que recibe la persona o el LLM es un bloque objetivo formado por uno o más párrafos de una misma intervención, acompañado por los bloques inmediatamente anterior y siguiente.

La aplicación no llama a OpenAI ni a ningún otro servicio externo. La clave de API no se carga ni se envía al navegador. La modalidad manual permite depurar el libro de códigos y producir una referencia humana. La opción **Revisión de anotaciones LLM** abre una modalidad diagnóstica separada que lee las respuestas generadas desde `annotations.qmd`, muestra modelo, input, output y códigos destacados, y guarda los juicios humanos sin modificar esas respuestas. Consulta [la guía del piloto](piloto-anotaciones-llm.md).

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

El valor predeterminado es `ley × cámara × alineación × género`. El tipo de actor permanece disponible y puede anexarse por `unit_id` después de congelar la referencia ciega. La asignación es proporcional mediante mayores restos y el JSON conserva población, muestra, probabilidad de inclusión y peso inverso por estrato. Antes del sorteo definitivo debe comprobarse que el tamaño elegido no produzca estratos con cuota cero.

La semilla hace que el sorteo sea reproducible para un corpus idéntico. `random` implementa muestreo aleatorio simple y registra una probabilidad común. Los valores ausentes forman la categoría explícita `Sin dato`. La cámara se determina a nivel de documento a partir de las funciones parlamentarias; cuando esas funciones faltan en un tercer trámite, se hereda la cámara del primer trámite del mismo proyecto.

La aplicación consume los bloques ya finalizados por `proc.qmd`; no vuelve a filtrar ni segmentar durante el muestreo. Las votaciones presentes en ese corpus se clasifican manualmente con las flags `Voto` o `Procedimental` y se registran con `evaluation_included=false`.

El procesamiento usa 100 palabras como objetivo y 150 como límite inicial. Al absorber restos breves de ambos lados, un bloque puede superar ese límite hasta el margen permitido por el esquema `coding-chunks-2.1.0`; el corpus actual llega a 194 palabras. Las intervenciones completas desde cinco palabras pueden conservarse. La versión 2.1 añade afiliación histórica sin modificar estas reglas textuales. Los bloques adyacentes sirven como contexto y nunca cruzan de un documento o sesión a otro.

## Libro de códigos

La fuente editable activa está en `features/codebook/codebook_v5.xlsx`. Las versiones anteriores se conservan sin cambios para reconstruir las rondas de calibración. Todas contienen las hojas `README`, `Metadatos` y `Conceptos`.

La versión conceptual 0.5.0 está diseñada para analizar *discourse coalitions*. Sus conceptos representan justificaciones normativas empleadas para apoyar o rechazar una posición previsional. Una descripción factual, un diagnóstico o una preferencia por un instrumento que carezca de justificación se marca como `Sin declaraciones codificables`.

Los dieciséis conceptos activos son:

- capitalización individual como regla de autofinanciamiento;
- propiedad individual de los fondos;
- reciprocidad contributiva;
- control y responsabilidad individual;
- actitud del beneficiario;
- identidad y pertenencia grupal;
- necesidad material;
- igualdad y universalismo;
- conciencia de costos;
- solidaridad previsional colectiva;
- solidaridad intergeneracional;
- libertad de elección previsional;
- ineficiencia y riesgo estatal;
- previsión como mercado, negocio e incentivos;
- ilegitimidad del origen dictatorial;
- acuerdos y moderación democrática.

`Suficiencia de las pensiones` se retiró porque describía un resultado deseable o un diagnóstico. `Capitalización individual` se reincorpora con una frontera estricta: codifica que las cotizaciones deben ingresar a cuentas individuales y financiar la pensión de su titular. La mención descriptiva al sistema AFP sigue fuera.

`Reciprocidad contributiva` abarca el título moral que el trabajo, las cotizaciones o el esfuerzo contributivo pueden generar para recibir, conservar o controlar recursos y protección previsional. Por ello, “quien cotizó más debe recibir más” y “no es justo hacer solidaridad con el esfuerzo de los trabajadores” expresan reciprocidad. La capitalización identifica la regla institucional sobre el destino individual del aporte; reciprocidad identifica el merecimiento derivado del aporte. Ambos códigos pueden coexistir cuando una declaración formula las dos proposiciones.

`Conciencia de costos como restricción de gasto` se activa cuando la inviabilidad financiera de la reforma se usa como argumento: que no se puede financiar, carece de una fuente sostenible o excede la capacidad fiscal. Por tanto, `Apoyo` corresponde a afirmar esa restricción y `Rechazo` a refutarla sosteniendo que la medida sí está financiada, es sostenible o cabe dentro de la capacidad fiscal. Las menciones neutrales a montos o fuentes quedan fuera, sin excluir refutaciones negativas explícitas.

Una afirmación sobre la sostenibilidad financiera presente o futura puede codificarse aunque no incluya montos, siempre que funcione como razón para limitar, rechazar o defender la reforma. Esta regla conserva como válida la codificación realizada en el ítem 13 de la ronda anterior.

`Solidaridad previsional colectiva` registra recursos o riesgos compartidos mediante redistribución, seguro social o financiamiento común sin una relación generacional explícita. `Solidaridad intergeneracional` se reserva para responsabilidades, transferencias o riesgos entre cohortes activas y jubiladas. La mención retórica de solidaridad o de un fondo común no basta para ninguno de los dos códigos.

`Libertad de elección previsional` registra la autonomía para escoger administradora, alternativa previsional o destino institucional de cotizaciones obligatorias. No equivale a propiedad de los fondos, autofinanciamiento individual, competencia de mercado ni responsabilidad por las consecuencias de una conducta controlable.

`Previsión como mercado, negocio e incentivos` reúne defensas y críticas de la competencia, inversión financiera, rentabilidad privada, lucro e incentivos de mercado. Incluye el argumento de que un beneficio reduce trabajo, productividad, ahorro o formalidad. Las comisiones abusivas se codifican aquí cuando funcionan como crítica a una extracción o ganancia privada; un porcentaje descriptivo de comisión queda fuera.

`Ilegitimidad del origen dictatorial` registra argumentos que vinculan el origen autoritario, coercitivo o engañoso del sistema con su legitimidad actual. Las fechas históricas y las críticas contemporáneas sin ese vínculo se excluyen.

`Acuerdos y moderación democrática` registra la valoración normativa del compromiso entre posiciones contrapuestas, la política de los acuerdos y el rechazo de extremos o maximalismos como bases de una reforma legítima. No incluye la mera existencia de una negociación, la eficacia técnica de un sistema mixto ni las apelaciones a preferencias ciudadanas, consulta o mayoría que no expresan compromiso entre posiciones. Estas últimas se mantienen como posible candidato inductivo de responsividad democrática.

El JSON `features/codebook/codebook_v5.json` es un archivo derivado y no debe editarse directamente. Se genera o comprueba con:

```bash
uv run python -m features.manual_validation.generate_codebook_json
uv run python -m features.manual_validation.generate_codebook_json --check
```

La aplicación ejecuta la generación automáticamente antes de iniciar. Cada concepto contiene familia, base teórica, definición, proposición de orientación y criterios de inclusión y exclusión. `Apoyo` significa que el actor afirma la proposición de orientación; `Rechazo` significa que la niega, refuta o declara inaplicable.

El instrumento está cerrado. La interfaz de codificación ya no ofrece la opción
de proponer categorías: se usan exclusivamente los conceptos del libro y una
razón fuera de alcance no se fuerza dentro de ellos. Los campos históricos de
estado conceptual se conservan en el archivo para compatibilidad, pero las
anotaciones nuevas quedan fijadas como `in_codebook`.

No se debe editar el libro incorporado dentro de una sesión ya iniciada. Al crearla, la aplicación congela una copia íntegra del libro y su SHA-256, lo que permite reconstruir exactamente los criterios disponibles para cada decisión.

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

## Secuencia recomendada para el piloto

1. **Chequeo de cierre:** inspeccionar una muestra breve de casos remitidos a revisión, especialmente confianza baja, fronteras del libro y orientaciones opuestas del mismo concepto.
2. **Codificación ciega:** iniciar una muestra nueva sin consultar respuestas del piloto y conservarla como referencia independiente.
3. **Control de estabilidad:** volver a codificar un subconjunto aleatorio después de un intervalo, sin consultar la primera decisión.
4. **Prompt del LLM:** entregar el bloque anterior, el bloque objetivo, el bloque siguiente y el mismo snapshot del libro; exigir el mismo esquema de spans, conceptos y orientación.
5. **Evaluación:** comparar primero detección de declaraciones y offsets; luego concepto y orientación, reportando métricas por concepto y no solo un promedio global.

Con una sola codificadora no es posible estimar confiabilidad intercoder humana. Sí es posible documentar estabilidad intracoder: volver a codificar, sin consultar las respuestas previas, un subconjunto aleatorio de la muestra después de un intervalo y comparar ambas rondas.

## Pruebas

```bash
uv run python -m unittest discover -s tests -p 'test_manual_validation.py' -v
```

Las pruebas cubren filtros del corpus, retención de votaciones, formación de bloques, contextos adyacentes, sincronía XLSX→JSON, reproducibilidad del muestreo, ocultamiento de identidad, spans exactos, resaltado, múltiples declaraciones del libro cerrado, ausencia de declaraciones, flags, comentarios generales, timestamps, persistencia y endpoints HTTP.
