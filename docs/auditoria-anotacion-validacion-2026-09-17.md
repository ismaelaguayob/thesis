# Auditoría de anotación, prompts y validación manual

Fecha: 17 de septiembre de 2026

## Alcance y criterio de revisión

La auditoría contrasta los scripts de `features/llm_annotations`, la aplicación de
`features/manual_validation`, los prompts, `annotations.qmd`, las sesiones y
ejecuciones guardadas, y las pruebas con el diseño declarado en
`material-suplementario-metodologico.md` y `thesis.md`.

Se revisaron cuatro condiciones principales:

1. correspondencia entre unidades de muestreo, codificación y análisis;
2. separación entre ausencia, fallo, ambigüedad y adjudicación;
3. posibilidad de estimar detección, concepto y postura contra una referencia
   humana independiente;
4. trazabilidad del corpus, instrumento, ejecución y decisiones humanas.

## Síntesis

El piloto LLM histórico sirve como conjunto de desarrollo y está descrito con
límites adecuados. Sus 418 bloques contienen 306 salidas válidas, 109 respuestas
incompletas y 3 salidas inválidas. Solo 65 de las 110 intervenciones seleccionadas
tienen todos sus bloques válidos. Las revisiones visibles del modelo son
diagnósticas y alcanzan tres bloques. Estas cifras impiden usar ese piloto como
codificación definitiva o evaluación de desempeño, una limitación que
`annotations.qmd` ya reconoce.

La principal brecha encontrada estaba en la validación definitiva. El flujo manual
sorteaba bloques por documento y longitud. El diseño exige seleccionar
intervenciones por ley, cámara, partido, género y tipo de actor, conservar todos
sus fragmentos y registrar probabilidades de inclusión. La revisión diagnóstica
del LLM tampoco permite registrar una omisión cuando el modelo ya encontró algún
código, ni producir correcciones adjudicadas en campos estructurados. En su estado
anterior, el sistema no podía calcular de forma válida la sensibilidad anunciada ni
construir la base adjudicada descrita en la metodología.

## Estado de las correcciones técnicas

Después de esta auditoría se aplicaron las correcciones técnicas en el código
vigente. La aplicación manual usa el esquema `manual-validation-2.5.0` y permite
seleccionar intervenciones completas o bloques. La estrategia estratificada ofrece
ley, cámara, partido o afiliación disponible, género, tipo de actor, documento y
longitud; registra población, muestra, probabilidad de inclusión y peso, y expande
cada intervención seleccionada a todos sus bloques. La codificación permanece
ciega a las categorías personales. La pestaña diagnóstica LLM permite filtrar por
las mismas categorías sin mostrar la identidad del hablante.

También se promovió `prompts/annotations_pilot_v1_confidence.md` como prompt
predeterminado, se alinearon sus reglas condicionales con el validador, se exigió
una propuesta no vacía para `review`, se rechazaron duplicados semánticos, se
volvieron obligatorias las anclas de orientación y se incorporaron los snapshots
de código al control de integridad. La selección manual ahora cuenta puntos de
código Unicode tanto en el navegador como en Python. Las rutas del libro, la
versión del esquema y la descripción del límite flexible fueron actualizadas en
la documentación y las pruebas.

Los hallazgos 2 y 3 siguen pendientes porque requieren decisiones sustantivas:
el esquema de adjudicación de omisiones y correcciones, y el tratamiento de casos
irresolubles frente a `no_statements`. También queda por acordar la tabla histórica
de afiliaciones que sustituirá el campo disponible `current_party`, y si la
multicodificación de un mismo span debe exigir una justificación estructurada.
Estos puntos deben resolverse antes de calcular sensibilidad, F1 o una base
adjudicada definitiva. Las descripciones siguientes conservan el diagnóstico
anterior a las correcciones para documentar por qué se realizaron.

## Hallazgos que bloquean la evaluación definitiva

### 1. La aplicación manual no implementa la muestra de evaluación declarada

**Evidencia.** El suplemento exige una muestra por ley, cámara, partido, género y
tipo de actor, seleccionada por intervención y acompañada por el estrato y la
probabilidad de inclusión (`material-suplementario-metodologico.md`, líneas
69-77). El servicio forma estratos `document_uri × length_bin` y sortea bloques
(`features/manual_validation/service.py`, líneas 440-484 y 658-767). Antes de
muestrear, elimina de sus registros `role`, `gender` y `current_party`, junto con
los identificadores del actor (líneas 368-418).

La ocultación de identidad durante la codificación es adecuada para reducir
sesgos. El sorteo debe ocurrir antes de ese ocultamiento, en una tabla de
intervenciones que contenga las variables de estratificación. El flujo actual no
ofrece una ruta para importar una selección ya fijada y mostrar todos los bloques
de cada intervención.

**Consecuencia.** Las sesiones actuales sirven para calibración del instrumento.
No representan la referencia humana estratificada descrita en la tesis. Las cinco
sesiones guardadas contienen 105 unidades. Las 95 unidades con el identificador
vigente `unit_id` incluyen solo siete que coinciden con el piloto LLM. La
comparación alineada necesaria para precisión, sensibilidad, F1 y kappa todavía
no existe.

**Corrección.** Crear un preparador de muestras de evaluación que:

- trabaje sobre una fila por `law_number × document_uri × utterance_id`;
- estratifique con las variables declaradas y una regla explícita para datos
  faltantes;
- guarde `N_h`, `n_h` y la probabilidad de inclusión de cada intervención;
- expanda cada intervención seleccionada a todos sus bloques;
- entregue a la interfaz una sesión congelada que omita los atributos del actor
  en la pantalla de codificación.

### 2. La revisión diagnóstica no permite medir omisiones en bloques parcialmente detectados

**Evidencia.** Cuando una respuesta del LLM contiene anotaciones, la interfaz solo
envía juicios sobre esas anotaciones y fuerza `issues=[]`
(`features/manual_validation/web/llm.js`, líneas 225-247). El servidor rechaza
problemas generales en esa modalidad (`features/llm_annotations/review.py`, líneas
122-149). Por tanto, `omission` solo puede registrarse cuando el modelo devolvió
cero códigos. El bloque queda marcado como `review_complete` cuando se juzgaron
todos los códigos que el modelo sí emitió, aunque falte una declaración (líneas
49-81).

Los comentarios de `needs_changes` conservan texto libre, pero no almacenan el
span, concepto y postura corregidos. Tampoco existe una tabla de anotaciones
adjudicadas vinculada de forma estructurada a la anotación automática original.

**Consecuencia.** La revisión puede describir falsos positivos y errores entre
los códigos observados. No puede estimar falsos negativos de forma completa,
separar detección de concepto y postura, ni generar la base adjudicada requerida
por el suplemento. La sensibilidad y el F1 quedarían sesgados al alza si se
derivaran de estos juicios.

**Corrección.** Añadir una decisión de detección a nivel de bloque para todos los
casos, permitir anotaciones humanas nuevas para las omisiones y guardar
correcciones estructuradas de span, concepto y postura. La adjudicación debe tener
estados `resolved` y `unresolved`, conservar el resultado automático y registrar
el vínculo entre ambos.

### 3. Los casos sin evidencia suficiente pueden cerrarse como ausencias

**Evidencia.** La modalidad manual solo admite `statements` y `no_statements`.
Cualquier combinación de flags se guarda con `status="completed"`
(`features/manual_validation/service.py`, líneas 909-971). No existe un estado de
decisión irresoluble. Cinco registros guardados combinan `no_statements` con
`too_short`, `truncated` u `other` en las sesiones del 3 de septiembre.

El contrato LLM permite correctamente una decisión de baja confianza que requiere
revisión. Sin una capa posterior de adjudicación, esa fila sigue exportada como
`decision="no_statements"`. Según el suplemento, una adjudicación
irresoluble cuenta como información faltante; la ausencia exige una intervención
completa sin decisiones pendientes (líneas 67 y 119).

**Consecuencia.** Un análisis que interprete toda decisión `no_statements` como
ausencia incorporará falsos ceros a los denominadores. La interfaz manual ofrece
un riesgo mayor porque no guarda una señal estructurada de revisión pendiente.

**Corrección.** Incorporar un estado `unresolved` o `unknown` y derivar
`known_absence` únicamente después de comprobar que todos los bloques de la
intervención fueron procesados y adjudicados. Las flags que afectan la
interpretación deben impedir el cierre como ausencia hasta resolver el caso.

## Hallazgos de prioridad alta

### 4. El prompt predeterminado y el contrato vigente pertenecen a versiones distintas

`output_schema()` exige `confidence` por anotación y `decision_confidence` por
bloque (`features/llm_annotations/pipeline.py`, líneas 63-94). La tabla del
suplemento atribuye estos campos al prompt `prompts/annotations_pilot.md`. Ese archivo breve
no define los tres niveles ni sus condiciones de revisión. Las instrucciones
completas están en `prompts/annotations_pilot_v1_confidence.md`, que
`annotations.qmd` todavía denomina versión en desarrollo y no usa como valor
predeterminado (líneas 38-49 y 342-365).

El esquema estricto obliga a emitir los campos, aunque no comunica su significado
metodológico. Esto puede producir confianza arbitraria o salidas rechazadas por
las reglas locales que exigen explicación y revisión para niveles medios o bajos.
La comprobación de cinco bloques que usó el prompt detallado terminó con cinco
salidas válidas, pero su tamaño no permite estimar calidad.

**Corrección.** Promover el prompt detallado a versión activa, fijar una versión
explícita en su nombre y hacer que todo nuevo preparador use esa ruta. Una prueba
de contrato debe comprobar que el prompt activo documenta cada campo y cada regla
condicional aplicada por `validate_output()`.

### 5. El contrato manual acepta registros que el suplemento declara inválidos

La normalización manual admite `concept_status="review"` con
`proposed_concept` vacío (`features/manual_validation/service.py`, líneas
865-907). Tres propuestas vacías aparecen en las sesiones antiguas. La guía de la
interfaz también presenta el nombre como opcional (`docs/interfaz-validacion-manual.md`,
líneas 52-62 y 170-173). Esta opcionalidad contradice la exigencia de una
propuesta conceptual del suplemento.

El guardado manual comprueba IDs de anotación únicos, pero no rechaza dos IDs con
el mismo span y concepto (líneas 944-957). También permite varios conceptos sobre
el mismo span sin exigir un fundamento diferenciable; la nota es opcional. Las
sesiones actuales no contienen duplicados semánticos, de modo que este es un
riesgo del contrato y no una corrupción observada.

**Corrección.** Exigir una propuesta con nombre y proposición de orientación para
`review`, rechazar la identidad semántica duplicada y solicitar una nota
justificativa cuando el mismo span reciba varios conceptos.

### 6. Faltan reglas ejecutables para asegurar la orientación y la revisión humana

`load_codebook()` requiere ID, etiqueta y definición, pero acepta conceptos sin
`orientation_anchor` (`features/manual_validation/service.py`, líneas 128-174).
La interfaz permitiría entonces asignar apoyo o rechazo sin una proposición de
referencia. El libro actual sí contiene anclas para sus catorce conceptos.

En la salida LLM, el prompt detallado exige revisión cuando una flag de calidad
afecta la interpretación y exige describir `other` en `limitations`. El validador
solo deriva la revisión desde la confianza media o baja y desde conceptos nuevos
(`features/llm_annotations/pipeline.py`, líneas 185-249). También admite flags
duplicadas y limpia silenciosamente `proposed_concept` cuando el concepto ya está
en el libro.

**Corrección.** Validar anclas no vacías al cargar el libro y trasladar al contrato
ejecutable todas las condiciones del prompt que cambian el tratamiento analítico
del caso.

## Hallazgos de prioridad media

### 7. Las probabilidades del sorteo por longitud no acompañan cada caso

El piloto LLM distribuye cuotas por ley y sesión y luego equilibra grupos de
longitud mediante rondas. Este segundo paso produce fracciones diferentes dentro
de una misma sesión. En la ejecución guardada, las fracciones por sesión y grupo
de longitud varían aproximadamente entre 4,95 % y 33,33 %. El manifiesto conserva
la fracción de la sesión, pero no `N_h`, `n_h` y la probabilidad para estos grupos.

`annotations.qmd` indica correctamente que los conteos del piloto no estiman
prevalencias. Por ello, la ejecución histórica sigue siendo válida como desarrollo.
No debe reutilizarse como muestra de evaluación ni para estimar frecuencias sin
reconstruir las probabilidades reales.

### 8. Los snapshots de código no están incluidos en la verificación de artefactos

`prepare_run()` incorpora los hashes del ejecutor y del contrato en la
especificación y copia `pipeline.py` y `validation_contract.py`. El campo
`artifact_sha256` del manifiesto excluye esas dos copias
(`features/llm_annotations/pipeline.py`, líneas 111-181). Las tablas
`selected_utterances.parquet` y `strata.parquet` se agregan después desde
`annotations.qmd` y tampoco integran ese manifiesto.

La configuración puede identificarse mediante los hashes originales, pero una
edición posterior de las copias presentadas como congeladas no se detecta. Esto
contradice la verificación descrita en `docs/piloto-anotaciones-llm.md`.

**Corrección.** Incluir todos los snapshots y tablas de selección en el manifiesto,
verificarlos antes de exportar y emitir un manifiesto de cierre para los resultados
y adjudicaciones.

### 9. Documentación y pruebas apuntan a rutas y versiones antiguas

La fuente vigente está en `features/codebook/`, mientras `README.md`,
`docs/interfaz-validacion-manual.md` y `tests/test_codebook_workbook.py` aún usan
`data/codebook/`. La guía manual declara el esquema 2.2.0 y un máximo estricto de
150 palabras; el servicio usa 2.4.0 y el corpus 2.0 admite el máximo flexible
descrito en el suplemento. `annotations.qmd` afirma que la tesis todavía menciona
un umbral de confianza numérico, pero la versión actual de `thesis.md` ya usa
confianza media o baja.

La ejecución de pruebas produjo 43 pruebas aprobadas y 3 errores. Los tres errores
provienen de las rutas antiguas del libro en `test_codebook_workbook.py`; las 23
pruebas LLM, 16 de validación manual y 4 de segmentación aprobaron por separado.

**Corrección.** Actualizar rutas, versiones y reglas de segmentación; convertir la
verificación completa en una condición previa para preparar nuevas ejecuciones.

### 10. La interfaz manual y el servidor usan unidades Unicode distintas

La selección manual calcula offsets con longitudes UTF-16 del navegador
(`features/manual_validation/web/app.js`, líneas 429-442). El servidor valida con
índices de puntos de código de Python. La vista de revisión LLM ya usa
`Array.from()` para resolver esta diferencia. Los 3.609 bloques actuales no
contienen caracteres fuera del plano multilingüe básico, por lo que no se observó
impacto en este corpus. Un corpus futuro con emojis u otros caracteres
suplementarios produciría spans desplazados o rechazados.

## Orden recomendado de corrección

1. Implementar la muestra humana por intervención y sus probabilidades.
2. Diseñar el esquema humano y de adjudicación con omisiones, correcciones y casos
   irresolubles en campos estructurados.
3. Alinear el prompt activo con el esquema de confianza y endurecer las
   validaciones cruzadas.
4. Corregir el contrato manual para propuestas, duplicados y multicodificación.
5. Cerrar la trazabilidad de artefactos y reparar documentación y pruebas.
6. Ejecutar una calibración nueva y reservar otra muestra ciega para evaluación.

Hasta completar los dos primeros pasos, las salidas existentes deben mantenerse
como datos de desarrollo y calibración. No sustentan todavía las métricas de
desempeño ni la base adjudicada que requiere el análisis sustantivo.
