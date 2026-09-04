# Auditoría de las codificaciones de las leyes 21.419 y 21.538

Fecha: 3 de septiembre de 2026. La revisión comprende las **40 unidades completadas y sus 16 anotaciones**. Las recomendaciones de recodificación son propuestas para adjudicación; las decisiones humanas y el libro de códigos se conservaron intactos.

La revisión encuentra dos asignaciones claramente incompatibles con las definiciones, varios límites conceptuales por precisar y fragmentos breves generados por el máximo estricto de palabras. A petición del investigador, se implementó un máximo flexible y se comprobó su efecto con los datos locales de las tres leyes. No se repitieron descargas ni se hicieron llamadas de codificación a LLMs.

## Fuentes y criterio de revisión

Se examinaron completas las dos sesiones, incluidos spans, orientaciones, notas, flags y bloques de contexto:

- [Sesión de la ley 21.419](../output/validation/validation_20260903T201432999213Z_1e8a5130.json): 20 unidades, 5 con declaraciones y 6 anotaciones.
- [Sesión de la ley 21.538](../output/validation/validation_20260903T203413684795Z_a63b3b9d.json): 20 unidades, 8 con declaraciones y 10 anotaciones.

Ambas usan el mismo snapshot del libro **0.4.0-pilot**, de 14 conceptos, aunque el archivo editable/derivado se llama `codebook_v0.3`. Se tomó como referencia el contenido guardado en las sesiones, cuyo SHA-256 es `b0b5a39cea7e55d7cde39e7cfcdf67d86b827370818b4475800e147f1ec16c8e`.

Se contrastaron los textos con `speech_df.parquet`, `speech_df_full.parquet` y, para investigar interrupciones y procedencia, el AKN ya descargado. Los 40 targets coinciden con los bloques originales y los 16 spans coinciden con sus offsets. Los problemas señalados abajo son de delimitación, atribución o aplicación conceptual; no se detectó corrupción de esas evidencias.

La numeración **21419-01** o **21538-17** identifica la posición, empezando en 1, en la sesión correspondiente. La [tabla completa de 40 unidades](../output/tables/auditoria_codificaciones_21419_21538/revision_40_unidades.csv) conserva textos y contexto; la [tabla de 16 anotaciones](../output/tables/auditoria_codificaciones_21419_21538/revision_16_anotaciones.csv) permite revisar cada evidencia seleccionada.

Las muestras tienen 20 unidades por ley, con estratificación por documento y longitud y semilla 20260824. Esta auditoría cualitativa identifica casos problemáticos; no estima una tasa de error del corpus ni acuerdo entre codificadores. Los cálculos de segmentación sí abarcan todos los bloques de cada ley.

## Decisiones prioritarias para el libro de códigos

| Prioridad | Hallazgo | Casos | Recomendación |
|---|---|---|---|
| Alta | Diálogo y acuerdos codificados como origen dictatorial | 21419-08 | Cambiar a `acuerdos_moderacion/support`; la evidencia no trata del origen de las AFP. |
| Alta | Diagnóstico de salarios y precariedad interpretado como responsabilidad individual | 21419-07 | Retirar esa asignación: falta una conducta controlable o una regla de merecimiento individual. |
| Alta | Posibles omisiones de argumentos financieros | 21419-04 y 05; revisar también 02 | Precisar el proyecto y momento evaluados y aplicar consistentemente la inclusión de suficiencia de financiamiento. |
| Alta | Orientación incierta al citar costos | 21538-04 | Separar voz citada, concesión del hablante y rechazo de la restricción. Apoyar expansión no implica automáticamente `oppose`. |
| Alta | Focalización usada como evidencia de necesidad | 21538-18 | Exigir privación o necesidad como razón de protección; el corte del 10 % más rico no basta. |
| Alta | Varias razones dentro de una declaración | 21538-17 | Revisar necesidad material omitida y adjudicar las fronteras de ciudadanía, identidad y reciprocidad por impuestos. |
| Alta | Exclusión temática registrada como ausencia de argumentos | 21419-17, comparado con 21538-17 | Distinguir `fuera_de_alcance` de `sin_declaraciones` y documentar un criterio consistente de inclusión. |
| Media | Toda crítica a AFP asimilada a capitalización individual | 21419-12 y 21538-07 | Exigir referencia al mecanismo de ahorro individual; registrar argumentos institucionales generales para revisión. |
| Media | Ampliación de cobertura y universalismo se usan con umbrales distintos | 21538-08, 10, 12, 14 y 18 | Distinguir descripción de cobertura, valoración de inclusión y justificación explícita por igualdad o derechos. |
| Media | Acceso efectivo a prestaciones con difícil encaje | 21538-06 | Registrar el candidato y contrastarlo con otros casos antes de ampliar o añadir conceptos. |

### Reglas operativas propuestas

**Unidad de evidencia.** Seleccionar el fragmento mínimo que conserve la razón y la medida o juicio que justifica. Cuando la conclusión sea compartida por dos razones, puede aparecer en ambos spans. Una referencia como «lo que implica» requiere incluir su antecedente o vincularlo explícitamente. El contexto puede resolver referentes y atribución; no debería convertir una afirmación que solo aparece en un vecino en una declaración del target.

**Voz y orientación.** Codificar la posición propia del actor. Una cita de un adversario o una explicación de la ministra necesita aceptación o rechazo reconocible. Para `conciencia_costos`, registrar también el objeto y el momento: proyecto inicial sin financiamiento, proyecto final financiado o futura ampliación. La redacción actual mezcla una proposición sobre suficiencia financiera con la función normativa de restringir gasto; conviene aclarar ambas y añadir ejemplos de concesión parcial.

**Descripción y valoración.** Una cifra de cobertura, una norma informada o una preferencia general por mejorar pensiones no activan automáticamente un código. Para `igualdad_universalismo`, la definición debe resolver expresamente si valorar la incorporación de excluidos es suficiente, aunque no se nombre un derecho universal. Si se acepta ese criterio, aplicarlo también a ejemplos equivalentes y conservar un contraejemplo técnico.

**Necesidad y focalización.** Exigir pobreza, vulnerabilidad, privación o necesidades básicas usadas como razón para proteger. Describir un requisito administrativo de ingresos no acredita esa razón. El caso 21538-18 y el contraste con 21538-17 ofrecen un par útil para entrenamiento.

**Identidad y reciprocidad.** Aclarar cuándo «son chilenos» expresa pertenencia de grupo y cuándo formula ciudadanía como derecho general. Resolver si contribuciones mediante impuestos entran en reciprocidad y bajo qué conexión explícita con merecimiento. Una lista de características del beneficiario no justifica aplicar todos los conceptos disponibles.

**Ausencia, exclusión y vacío conceptual.** Separar tres resultados: ausencia de argumento normativo pertinente; argumento fuera del alcance definido; argumento pertinente sin concepto adecuado. En la app ya se pueden proponer conceptos en revisión, pero la exclusión temática necesita una decisión distinguible. Las pensiones de reparación y la inclusión de Dipreca/Capredena deben someterse al mismo criterio de alcance. Los candidatos sobre mandato ciudadano, seguridad social y acceso efectivo deben acumular evidencia antes de incorporarse al libro.

## Segmentación: diagnóstico y cambio aplicado

El algoritmo anterior cortaba con máximo estricto de 150 palabras y solo añadía un fragmento breve al vecino cuando cabía bajo ese máximo. Eso dejaba restos que podían tener sentido al lado de la intervención, pero quedaban como unidades independientes.

| Situación en la versión 1.0.0 | Ley 21.419 | Ley 21.538 |
|---|---:|---:|
| Bloques totales | 881 | 333 |
| Bloques de menos de 50 palabras | 141 | 36 |
| De ellos, intervenciones completas | 104 | 29 |
| De ellos, fragmentos dentro de intervenciones largas | 37 | 7 |
| Bloques de menos de 20 palabras | 79 | 23 |
| Fragmentos breves que cabían con un vecino completo bajo 150 | 0 | 0 |

Los 177 bloques breves incluyen 133 intervenciones completas y 44 fragmentos de intervenciones largas. La restricción estricta explica por qué esos fragmentos no se habían unido: ninguna unión íntegra con el vecino de la misma intervención cabía bajo 150 palabras. Se comprobó, por ejemplo, que era posible redistribuir párrafos en 21419-12 y 14; la preferencia posterior por reducir llamadas llevó a implementar la fusión con máximo flexible.

La versión **coding-chunks-2.0.0** mantiene el corte inicial de 150 y luego une cada bloque de menos de 50 palabras con el vecino más corto de la misma intervención. En caso de empate elige el anterior. Conserva el orden, el texto y la procedencia de cada segmento. Una intervención completa de menos de 50 palabras permanece independiente, y el filtro de 5 palabras se aplica después de la fusión. De esta manera se recuperan también cierres breves que antes se descartaban.

| Ley | Bloques antes | Bloques después | Reducción | Máximo observado después |
|---|---:|---:|---:|---:|
| 21.419 | 881 | 844 | 37 (4,20 %) | 194 palabras |
| 21.538 | 333 | 326 | 7 (2,10 %) | 174 palabras |
| 21.735 | 2.553 | 2.439 | 114 (4,47 %) | 194 palabras |
| Total | 3.767 | 3.609 | 158 (4,19 %) | 194 palabras |

Quedan **cero fragmentos de menos de 50 palabras dentro de intervenciones largas** en las tres leyes. Las 158 llamadas evitables suponen una llamada por bloque; no equivalen necesariamente al mismo porcentaje de reducción de tokens o costo. Se conservan todas las palabras de las intervenciones retenidas, incluidos cuatro términos antes descartados en la ley 21.419 y seis en la 21.735. No se alteraron las anotaciones humanas.

### Los ocho bloques breves de las muestras

| Caso | Longitud original | Diagnóstico | Resultado de la nueva regla |
|---|---:|---|---|
| 21419-11 | 18 | Intervención procedimental completa | Permanece separada. |
| 21419-12 | 33 | Fragmento entre bloques de 121 y 138 palabras | Se une al anterior: 154. |
| 21419-14 | 13 | Cierre interrumpido, con bloque anterior de 141 | Se une al anterior: 154; persiste el corte que ya está en la fuente. |
| 21419-16 | 9 | Encabezado de votación separado de la nómina | Se une al siguiente: 159. |
| 21419-19 | 14 | Cola de nómina y nombre partido | Se une al anterior: 164. |
| 21538-09 | 5 | Encabezado de votación aislado | Se une al siguiente: 155. |
| 21538-11 | 5 | Intervención procedimental completa | Permanece separada. |
| 21538-16 | 11 | Intervención procedimental completa | Permanece separada. |

### Problemas que requieren otro tratamiento

**Nóminas y procedimientos.** Las listas nominales pueden seguir cortándose dentro de un nombre cuando sus bloques son largos, como en 21419-06, 21419-13 y 21538-20. Para reducir llamadas adicionales conviene identificar registros de votación y procedimientos en una etapa explícita, conservándolos como negativos de control en la validación. La presencia de «voto a favor» en un discurso argumentado no justifica excluirlo. No se añadió ese filtro en este cambio.

**Interrupciones omitidas del contexto.** En 21419-14, el AKN local ya termina «sobre todo…» en el párrafo `akn697505-ds6-ds10-ds11-ds34-p554`; después la presidencia anuncia el fin del tiempo. Ese anuncio queda en `speech_df_full` como preámbulo excluido. En 21538-05, «Una carta.» es una intervención independiente de dos palabras que queda fuera por el mínimo. Mostrar eventos e intervenciones omitidas en el contexto ayudaría a distinguir interrupción, continuación y pérdida de texto. Suprimir esos turnos como unidades codificables no debería borrar la información contextual.

**Continuidad del actor.** Para 21538-02 ambos vecinos son del mismo actor y la misma intervención. El backend envía `previous_same_utterance` y `next_same_utterance`, pero la interfaz todavía no los presenta. Además, mismo actor y misma intervención son relaciones distintas: en 21538-05 el actor retoma después de una interrupción con otro `utterance_id`. Se recomienda mostrar ambas relaciones de forma anónima. Esta mejora de contexto queda pendiente.

**Debate conjunto de dos boletines.** En el documento AKN `698998`, la fuente anuncia tratamiento conjunto de la PGU, boletín 14588-13, y las exenciones tributarias, boletín 14763-05. Las unidades 21419-13 y 16 pertenecen a una votación de este último dentro del mismo contenedor de proyecto. Conviene conservar los boletines debatidos y el objeto concreto de cada votación; no hay base para interpretar su presencia como una descarga ajena al debate o eliminarla automáticamente.

Los [extractos del AKN local](../output/tables/auditoria_codificaciones_21419_21538/evidencia_akn.json) conservan los identificadores y textos que permiten comprobar la interrupción y el debate conjunto.

## Revisión individual: ley 21.419

### 21419-01 · Compatible con el libro

Unidad `utt_37aa049c0111f0e26ebc::p0003` · 98 palabras · Registro: `no_statements`.

Se elogia el financiamiento estatal no contributivo como avance. Falta una razón distributiva específica para asignar un concepto. El aporte del Estado por sí mismo no demuestra solidaridad intergeneracional. Los argumentos sobre acuerdo y universalidad están en los vecinos. Mantener `no_statements` es defendible.

### 21419-02 · Revisar alcance y posible omisión

Unidad `utt_1dbe6f2dc32ba8e1c8bb::p0001-p0003` · 133 palabras · Registro: `no_statements`.

El compromiso social y el mandato electoral se invocan para aprobar la reforma. Hay argumentación normativa con un encaje débil en el libro; conviene registrarla para revisión conceptual. El mandato de mayoría no equivale a moderación y compromiso. La objeción «no hay financiamiento» recibe una respuesta favorable al proyecto; `conciencia_costos/oppose` es una posibilidad dependiente del contexto. Las fuentes concretas de recursos aparecen en el siguiente bloque.

### 21419-03 · Dos anotaciones compatibles; mejorar evidencia

Unidad `utt_5116533e3611e77af149::p0001-p0003` · 126 palabras · Registro: `necesidad_material/support`; `capitalizacion_individual/oppose`.

1. Mantener `necesidad_material/support`: pobreza y miseria justifican mejorar pensiones.
2. Mantener `capitalizacion_individual/oppose`: se afirma expresamente la insuficiencia del ahorro individual para asegurar pensiones dignas.

El cierre «Por eso, siempre es necesario un aporte fiscal adicional para mejorar las pensiones» completa la conexión con la propuesta. Puede incorporarse a ambos spans, conservando dos razones diferenciadas.

### 21419-04 · Posible omisión financiera; prioridad alta

Unidad `utt_b99b67d3e9ccc449ff45::p0001` · 112 palabras · Registro: `no_statements`.

El actor sostiene que tenía razón al exigir ingresos permanentes y que el proyecto finalmente los obtuvo. Revisar `conciencia_costos`: la inclusión de refutaciones por financiamiento disponible hace plausible `oppose` para el proyecto actual, mientras la crítica al diseño inicial apunta a `support` en otro momento. Hay que fijar el referente temporal antes de adjudicar. El monto aislado no es la razón para proponer esta revisión.

### 21419-05 · Posible omisión financiera; prioridad alta

Unidad `utt_760c32fa86a5d52dc3e4::p0012-p0013` · 98 palabras · Registro: `no_statements`.

Se valora haber conseguido el financiamiento que faltaba y se rebate que estuviera asegurado inicialmente. Es candidato a `conciencia_costos` por la inclusión explícita de suficiencia financiera. Separar la evaluación del proyecto aprobado del requisito de nuevos recursos para una PGU futura de 250 mil. La crítica a capitalización individual aparece en el bloque siguiente y necesita su propia evidencia.

### 21419-06 · Lista de votación con nombre partido

Unidad `utt_b21d793054a79b4d5568::p0005s001` · 150 palabras · Registro: `no_statements`.

Mantener `no_statements` y `vote`. El corte separa «Marzán» de «Pinto, Carolina». Es un efecto de dividir nóminas por palabras, que no se resuelve enteramente fusionando residuos breves cuando ambos bloques son largos. Requiere clasificar y segmentar este tipo de registro.

### 21419-07 · Asignación incompatible; prioridad alta

Unidad `utt_8b0ee42a34638e95e7ef::p0011` · 54 palabras · Registro: `control_responsabilidad_individual/oppose`.

Retirar `control_responsabilidad_individual/oppose` de esta evidencia. La nota humana interpreta responsabilidad del contribuyente, pero el target discute salarios y precariedad como explicaciones de pensiones bajas. No se formula una conducta controlable ni un merecimiento individual. El libro excluye ese tipo de diagnóstico estructural. La crítica institucional del contexto necesita otra evidencia y no obliga a sustituir automáticamente el código.

### 21419-08 · Concepto equivocado; prioridad alta

Unidad `utt_ebf7e3744ad319130b60::p0015-p0016` · 95 palabras · Registro: `ilegitimidad_origen_dictatorial/support`.

Cambiar `ilegitimidad_origen_dictatorial/support` por `acuerdos_moderacion/support`. El fragmento invoca el poder del diálogo y los buenos resultados de ponerse de acuerdo. No ofrece ninguna razón sobre el origen autoritario del sistema previsional. Parece un error de selección del concepto.

### 21419-09 · Anuncio y resultado de votación

Unidad `utt_d14a80167cb6070db781::p0001-p0003` · 51 palabras · Registro: `no_statements`.

Mantener `no_statements` y `vote`. La unidad anuncia la votación y registra sus resultados. El acto de votar no equivale a una justificación normativa del voto.

### 21419-10 · Discusión procedimental

Unidad `utt_2fd7397f6f75a08e9a2a::p0005-p0006` · 63 palabras · Registro: `no_statements`.

Mantener `no_statements` y `procedural`. Se discute admisibilidad y cómo resolver el desacuerdo de procedimiento. La apelación al buen espíritu no alcanza el criterio de compromiso amplio usado para legitimar una reforma.

### 21419-11 · Intervención breve completa

Unidad `utt_65794d6d971ec4de9dca::p0001` · 18 palabras · Registro: `no_statements`.

La petición de terminar el turno es procedimental. Ser «justos con todos» se refiere al tiempo de palabra, fuera del objeto previsional de igualdad. Las 18 palabras son la intervención completa; sus vecinos son otros turnos y actores. Se conserva separada. `too_short` describe longitud, pero no demuestra un fallo de segmentación.

### 21419-12 · Crítica a AFP con concepto demasiado amplio

Unidad `utt_12936eced6d4067f7002::p0005` · 33 palabras · Registro: `capitalizacion_individual/oppose`.

Revisar `capitalizacion_individual/oppose`: defender el esfuerzo de «No más AFP» no identifica por sí mismo la regla de ahorro individual o autofinanciamiento requerida. Puede registrarse como argumento sobre mandato ciudadano o cambio institucional pendiente de delimitación. El fragmento de 33 palabras se une al anterior de 121, quedando en 154. La mejora de contexto no valida automáticamente la asignación original.

### 21419-13 · Nómina y procedencia por precisar

Unidad `utt_5228501d1f6af06fbf94::p0003s003-p0004` · 85 palabras · Registro: `no_statements`.

Mantener `no_statements` y `vote`. El inicio «Antonio» continúa el nombre del bloque previo. Persiste el corte entre bloques largos. Corresponde a la votación de exenciones tributarias también observada en 21419-16, dentro de un debate conjunto con la PGU. Hay que distinguir el objeto de la votación de los proyectos tratados en la sesión.

### 21419-14 · Aislamiento corregido e interrupción original

Unidad `utt_aae16cfc24f46ded2c70::p0007` · 13 palabras · Registro: `no_statements`.

Mantener `no_statements` en la unidad original: el motivo anunciado tras «sobre todo» queda inconcluso. Las 13 palabras se unen al bloque anterior de 141. El AKN ya contiene ese final, seguido de un anuncio de término del tiempo. La fusión mejora el contexto, pero no permite completar la razón interrumpida. Mostrar el evento de presidencia resolvería parte de la incertidumbre.

### 21419-15 · Código adecuado; span dependiente

Unidad `utt_774559cd67c438850a30::p0002` · 71 palabras · Registro: `igualdad_universalismo/support`.

Mantener `igualdad_universalismo/support`. El reconocimiento de derechos de ciudadanía respalda el código. Ampliar el inicio del span hasta «Pasar a una pensión garantizada universal» permitiría conservar el antecedente de «lo que implica» y unir el cambio defendido con su justificación.

### 21419-16 · Encabezado de votación aislado

Unidad `utt_5228501d1f6af06fbf94::p0001-p0002` · 9 palabras · Registro: `no_statements`.

Mantener `no_statements` y `vote`. El contexto identifica la votación de exenciones tributarias. Las 9 palabras del encabezado se unen a la nómina siguiente de 150, dando 159. Es un registro de votación, sin argumento normativo del hablante.

### 21419-17 · Exclusión temática distinta de ausencia

Unidad `utt_34dec9d9e6eae9ed12df::p0015-p0017` · 107 palabras · Registro: `no_statements`.

Tu comentario deja fuera de la tesis las pensiones de reparación. El texto sí argumenta normativamente por daño y justicia reparadora. Conviene registrar `fuera_de_alcance` y explicar por qué esta exclusión de beneficiarios queda fuera mientras Dipreca/Capredena entra en 21538-17. El concepto de origen dictatorial trata de la legitimidad fundacional de AFP; no abarca toda referencia a víctimas de la dictadura.

### 21419-18 · Valoración general de la gestión

Unidad `utt_b9341b57a7bc037f529c::p0005` · 68 palabras · Registro: `no_statements`.

Mantener `no_statements` es defendible. Se elogia perseverancia gubernamental e importancia de la reforma sin una razón específica del libro en el target. La colaboración opositora aparece antes y las necesidades materiales después. Esas evidencias conservan su propia ubicación.

### 21419-19 · Cola de nómina

Unidad `utt_05443dabe786db4fee5a::p0005s002` · 14 palabras · Registro: `no_statements`.

Mantener `no_statements` y `vote`. Las 14 palabras se unen al bloque anterior de 150, dando 164. Esta fusión repara el nombre «Mix Jiménez», antes partido entre los dos bloques.

### 21419-20 · Agradecimiento a autoridades

Unidad `utt_30bcedbb4dd0ba022ce5::p0004` · 59 palabras · Registro: `no_statements`.

Mantener `no_statements`. Se agradecen sensibilidad y gestión de ministros. `actitud` se refiere al beneficiario como merecedor de protección; `ineficiencia_estado`, a la administración de fondos previsionales. Los elogios no activan esas categorías.

## Revisión individual: ley 21.538

### 21538-01 · Comparación de género bien fundamentada

Unidad `utt_c40042f779ebe8138259::p0006` · 108 palabras · Registro: `igualdad_universalismo/support`.

Mantener `igualdad_universalismo/support`. Se propone anticipar el beneficio para corregir una brecha entre mujeres y hombres que trabajaron en condiciones comparables. La comparación y la medida correctiva aparecen juntas. El trabajo cumple una función comparativa y no exige añadir reciprocidad.

### 21538-02 · Contexto y umbral normativo por aclarar

Unidad `utt_ac5d6be4b0a3b9d49fd2::p0011` · 72 palabras · Registro: `no_statements`.

El target resume universalización y financiamiento de una reforma futura. Bajo la exigencia de justificación explícita, `no_statements` es defendible. Para costos hay que distinguir una condición descriptiva de financiamiento de una razón para restringir expansión. Las afirmaciones de ciudadanía como derecho están en el siguiente bloque. Tu duda sobre el actor es pertinente: ambos vecinos son de la misma intervención y actor, información que falta presentar en la interfaz.

### 21538-03 · Distribución del tiempo de palabra

Unidad `utt_f61b5bad10326b62c018::p0001` · 51 palabras · Registro: `no_statements`.

Mantener `no_statements`. La unidad explica quiénes podrán intervenir por las restricciones de tiempo. Añadir `procedural` haría consistente el registro de flags con casos equivalentes.

### 21538-04 · Orientación de costos ambigua

Unidad `utt_0942156d65780aaac72d::p0006` · 71 palabras · Registro: `conciencia_costos/oppose`.

Revisar `conciencia_costos/oppose`. El actor cita a la ministra y concede que la explicación es entendible financieramente, aunque duda de su razonabilidad. La incorporación gradual de mujeres se propone después. Ese apoyo a expandir cobertura no determina por sí solo rechazo de la razón de costos. No cambiar automáticamente a `support`: adjudicar la voz, la concesión y la justificación que se acepta o rebate.

### 21538-05 · Descripción operativa con interrupción oculta

Unidad `utt_b0d02f6f538c59874a61::p0032` · 78 palabras · Registro: `no_statements`.

Mantener `no_statements` es defendible: se explica la actualización automática de solicitudes rechazadas sin una razón distributiva explícita. Después del cierre «pero...» aparece «Una carta.», intervención independiente de dos palabras excluida por el mínimo. Luego retoma el actor original con otro `utterance_id`. El contexto basado solo en bloques codificables oculta el intercambio.

### 21538-06 · Posible vacío sobre acceso efectivo

Unidad `utt_e1a3192cd687754b80cb::p0003` · 56 palabras · Registro: `no_statements`.

Se solicita difusión porque hay personas sin ayuda que no saben postular. Conviene registrar el argumento para revisar acceso efectivo a prestaciones, según el umbral de normatividad adoptado. No encaja directamente en `ineficiencia_estado`, que trata de administrar fondos. Contrastar con el vecino de 21538-08 que defiende recepción automática como derecho, antes de crear o ampliar una categoría.

### 21538-07 · Crítica institucional demasiado general para capitalización

Unidad `utt_5df9b3e4079cda4206fd::p0001-p0004` · 127 palabras · Registro: `capitalizacion_individual/oppose`.

Revisar `capitalizacion_individual/oppose`. La evidencia reclama un verdadero sistema de seguridad social y una reforma profunda, sin nombrar ahorro propio, cuentas individuales o autofinanciamiento. Registrar el argumento institucional para evaluar cobertura conceptual. La mención a la transición democrática tampoco basta para asignar origen dictatorial.

### 21538-08 · Contraste técnico para la regla de universalismo

Unidad `utt_b1a554e83bfa8e2aad15::p0006` · 57 palabras · Registro: `no_statements`.

Mantener `no_statements` bajo una exigencia de razón normativa identificable. Se comparan umbrales de ingreso y se propone trabajar la diferencia. Contrastar con la valoración de inclusión en 12 y 14. Las justificaciones por derechos del contexto siguiente deben conservar su propia evidencia.

### 21538-09 · Encabezado breve de votación

Unidad `utt_fe7234a44c91cc4364e2::p0001-p0002` · 5 palabras · Registro: `no_statements`.

Mantener `no_statements` y `vote`. Las 5 palabras se unen a la nómina siguiente de 150, dando 155. Es uno de los residuos que producía el máximo estricto.

### 21538-10 · Atribución del discurso de informante

Unidad `utt_d0b889a2d0191fecf912::p0005-p0006` · 93 palabras · Registro: `no_statements`.

Se informa el contenido legal de instrumentos de focalización iguales para la ciudadanía. `no_statements` es defendible si se exige adhesión argumentada del actor. El libro debe explicitar si informar una regla distributiva basta para codificar una posición propia; una norma citada y una justificación asumida pueden coincidir, pero necesitan distinguirse.

### 21538-11 · Acuerdo procedimental en un turno completo

Unidad `utt_6bb7528fedab2e4d0bcf::p0001` · 5 palabras · Registro: `no_statements`.

Mantener `no_statements`. «Es un acuerdo de Comités» constata un procedimiento y no activa `acuerdos_moderacion`. Las 5 palabras constituyen la intervención completa, separada de otros turnos y actores. Añadir `procedural`.

### 21538-12 · Inclusión valorada como fin

Unidad `utt_0942156d65780aaac72d::p0010` · 52 palabras · Registro: `igualdad_universalismo/support`.

Mantener provisionalmente `igualdad_universalismo/support` si la valoración positiva de incorporar excluidos se admite como razón suficiente. Aquí se califica como buena noticia el aumento de cobertura, aunque no se nombre un derecho universal. Añadir esa regla y un contraejemplo descriptivo como 21538-08 o 10. No hace falta exigir literalmente la palabra igualdad.

### 21538-13 · Necesidad material explícita

Unidad `utt_24076c18c3fdcff954ca::p0002` · 111 palabras · Registro: `necesidad_material/support`.

Mantener `necesidad_material/support`: corregir pensiones de miseria y asegurar un mínimo de dignidad justifican aprobar el proyecto. Puede ampliarse el span para incorporar la conclusión «por ello hoy es vital» aprobarlo. La mención de AFP no fundamenta por sí sola capitalización individual. La pobreza de las mujeres en el resto del target refuerza la misma familia de razones.

### 21538-14 · Dos razones con distinta fuerza de encaje

Unidad `utt_cbd165e541e063cf008c::p0001-p0004` · 137 palabras · Registro: `acuerdos_moderacion/support`; `igualdad_universalismo/support`.

1. Mantener `acuerdos_moderacion/support`: se conecta la construcción de acuerdos con la posibilidad de aprobar la PGU. El espacio inicial del span es una limpieza menor.
2. `igualdad_universalismo/support` es defendible con la regla de inclusión propuesta para 21538-12. El juicio «vale la pena» permite distinguirlo de una simple descripción de cobertura.

### 21538-15 · Cifras y efectividad administrativa

Unidad `utt_902ee03ebf7e32198b3f::p0003` · 107 palabras · Registro: `no_statements`.

Mantener `no_statements`. Se informa incorporación al pago y se valora efectividad administrativa, sin legitimar al Estado como administrador de fondos. El lenguaje de derechos sociales está en el bloque previo.

### 21538-16 · Intervención breve sobre el orden de la sesión

Unidad `utt_5a9e5255e01e1acea9c9::p0001` · 11 palabras · Registro: `no_statements`.

Mantener `no_statements` y añadir `procedural`. Las 11 palabras sobre el acuerdo relativo al proyecto de salud son el turno completo. Sus vecinos son otros turnos y actores. La regla nueva conserva esa separación; la brevedad no acredita un error de chunking.

### 21538-17 · Varias razones y omisión probable

Unidad `utt_a13cd7a8f252721eae47::p0004-p0005` · 52 palabras · Registro: `igualdad_universalismo/support`.

Mantener `igualdad_universalismo/support` como lectura defendible de corregir la exclusión de Dipreca/Capredena. Revisar la adición de `necesidad_material/support`: «padecen pobreza» es una razón expresa para incluirlos. «Pagaron impuestos» requiere resolver el alcance de reciprocidad y «son chilenos», la frontera entre identidad y ciudadanía universal. No añadir mecánicamente todas las categorías. Revisar también la coherencia de alcance con 21419-17.

### 21538-18 · Doble codificación insuficientemente sustentada

Unidad `utt_8f0f0c34eaba2b5f9365::p0003-p0004` · 137 palabras · Registro: `igualdad_universalismo/support`; `necesidad_material/support`.

1. Revisar `igualdad_universalismo/support` con el criterio acordado para 12 y 14. La formulación es principalmente técnica y remite a un acuerdo previo; el respaldo normativo se ve mejor en el contexto anterior.
2. Retirar o dejar en revisión `necesidad_material/support`. La nota equipara excluir al 10 % más rico con necesidad, pero el libro excluye la focalización meramente administrativa. La privación y los gastos aparecen en el siguiente bloque, fuera del span.

Ambas anotaciones seleccionan casi el mismo texto. Compartir evidencia es admisible cuando hay dos razones independientes; este caso necesita demostrar la segunda.

### 21538-19 · Preferencia general por corregir el sistema

Unidad `utt_f3ddaf7e7f9689a46adb::p0008-p0010` · 96 palabras · Registro: `no_statements`.

Mantener `no_statements`. Se apoya corregir un problema técnico y seguir mejorando las pensiones sin identificar una razón específica del libro. Votar a favor no sustituye la justificación requerida.

### 21538-20 · Nómina con corte dentro de un nombre

Unidad `utt_0deedd57a4d8e7017f09::p0003s001` · 150 palabras · Registro: `no_statements`.

Mantener `no_statements` y `vote`. Se separa «Muñoz» de «González, Francesca». La nueva regla absorbe el encabezado breve anterior, pero persiste el corte interno entre bloques largos. Conviene tratar las nóminas como registros de votación y decidir explícitamente su inclusión en las llamadas al LLM.

## Trazabilidad y verificación

El [diagnóstico reproducible](../output/tables/auditoria_codificaciones_21419_21538/diagnostico.py) utiliza solo los archivos locales y las celdas de segmentación de `proc.qmd`. Los [insumos y hashes](../output/tables/auditoria_codificaciones_21419_21538/metrics.json), el [inventario de bloques breves](../output/tables/auditoria_codificaciones_21419_21538/short_chunks.csv) y la [comparación de versiones](../output/tables/auditoria_codificaciones_21419_21538/new_metrics.json) documentan los resultados. El [mapeo de unidades](../output/tables/auditoria_codificaciones_21419_21538/unit_mapping.csv) relaciona los 3.767 bloques anteriores con sus nuevos bloques mediante procedencia y hashes.

Antes de sustituir los corpus activos se conserva, dentro de la carpeta de cada ley, `coding_chunks_long.coding-chunks-1.0.0.parquet`. Las sesiones humanas conservan sus textos y spans originales; el mapeo no transfiere automáticamente las anotaciones. Se comprobó la apertura de los 40 casos contra el servicio actualizado utilizando copias temporales de las sesiones. Las pruebas de segmentación comprueban restos iniciales, intermedios y finales, conservación de palabras y hashes de procedencia; la app admite ambas versiones de corpus.

Los ajustes al libro, las recodificaciones propuestas, la clasificación de nóminas y la presentación del contexto quedan para adjudicación e implementación posterior. El cambio aplicado en esta revisión es la fusión de fragmentos breves y su compatibilidad con la app.
