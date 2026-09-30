# Material suplementario metodológico

Este documento detalla las reglas de codificación, construcción de redes y comparación estadística que respaldan la metodología de [la tesis](../thesis.md). La exposición principal presenta la secuencia del análisis y su relación con las hipótesis; este suplemento precisa las unidades, los denominadores, las fórmulas y los criterios de interpretación necesarios para reproducirlo.

## 1. Unidades y trazabilidad

| Unidad | Definición y función |
| --- | --- |
| Proyecto de ley | Proceso legislativo identificado por ley y boletín. La creación de la PGU, su ampliación y la reforma previsional se comparan separadamente. |
| Fase legislativa | Agrupación de discusiones según trámite y cámara. Organiza la comparación temporal dentro de la reforma. |
| Discusión en Sala | Documento del corpus identificado por `document_uri`, con fecha, cámara y trámite. |
| Intervención | Participación de un actor identificada por `utterance_id` dentro del documento. Es la unidad de los porcentajes de presencia y de la densidad normativa. |
| Fragmento | Bloque de texto identificado por `unit_id`, que recibe el LLM junto con su contexto adyacente. Una intervención puede dividirse en varios fragmentos. |
| Declaración codificada | Afirmación que vincula un concepto con una postura y conserva su evidencia textual. Constituye la observación básica del DNA. |
| Evidencia | Cita literal y posiciones dentro del fragmento que respaldan la anotación. Un mismo pasaje puede sustentar conceptos diferentes. |

La identificación completa de una intervención combina ley, documento e identificador de intervención. Las anotaciones se identifican por ejecución, fragmento y `annotation_id`, ya que este último puede repetirse en otros fragmentos. Los metadatos del actor proceden del corpus y se incorporan mediante estas claves; el modelo no infiere partido, género ni ideología a partir del discurso.

### 1.1 Segmentación y contexto

`proc.qmd` conserva los textos y metadatos de las intervenciones y genera los bloques de codificación. La segmentación parte de párrafos; divide los extensos por oraciones y, cuando es necesario, por límites entre palabras. Agrupa segmentos breves dentro de la misma intervención, con un objetivo de 100 palabras y un máximo inicial de 150. Los bloques inferiores a 50 palabras se unen al vecino más corto; esta operación puede superar el máximo inicial. Se conservan intervenciones completas de entre 5 y 49 palabras. El corpus descrito en la tesis contiene fragmentos de entre 5 y 194 palabras.

Cada bloque mantiene su posición en la intervención y la correspondencia con los segmentos originales. El contexto anterior y posterior puede pertenecer a otro hablante; se utiliza para interpretar referencias o negaciones, pero la evidencia codificada debe estar en el bloque objetivo. Los offsets de las anotaciones se refieren al texto de ese bloque. La reconstrucción de la ubicación en la intervención debe utilizar la correspondencia de segmentos conservada por el procesamiento.

### 1.2 Metadatos conservados

| Información | Campos del procesamiento |
| --- | --- |
| Proyecto y documento | `law_number`, `document_uri`, `bill_number` |
| Fecha y trámite | `date`, `constitutional_stage`, `regulatory_stage` |
| Intervención y orden | `utterance_id`, `utterance_order` |
| Fragmento y procedencia textual | `unit_id`, `chunk_id`, `source_start_char`, `source_end_char`, `source_segments_json` |
| Actor | `speaker_id`, `speaker_bcn_id`, nombre y función del hablante |
| Características políticas y personales | `party_at_date`, estado y fuente de la afiliación histórica, `political_alignment`, género y fecha de nacimiento disponibles en los metadatos |

La clasificación en grupos políticos utiliza la afiliación correspondiente a la fecha del debate. `proc.qmd` enlaza `parliamentarian_affiliations.parquet` mediante documento y persona y conserva `party_at_date`, el estado del emparejamiento y la fuente; `current_party` permanece como dato de procedencia. `party_at_date_status` distingue afiliación encontrada, afiliación no aplicable para funciones institucionales o ejecutivas y afiliación desconocida. Solo las afiliaciones encontradas se convierten en `political_alignment`. Una configuración única y versionable, la variable de entorno `PARTY_ALIGNMENT` leída desde `.env`, enumera en formato JSON los partidos asignados a `left`, `center`, `right` y `nonpartisan`; los partidos encontrados que no aparecen en esas listas quedan como `unclassified`. Los estados desconocidos y no aplicables se conservan separados y no se imputan al centro.

Los parlamentarios independientes se asignan al grupo político de la bancada que integran en la fecha del debate o, en su defecto, del pacto electoral por el que fueron electos. La asignación se registra, con su fuente, en `data/curation/independent_bloc_assignments.csv`, una fila por persona y discusión. `party_at_date` conserva la militancia histórica («Independiente»); el grupo asignado se guarda en `political_group_party`, junto con `political_group_source` (`party`, `independent_bancada`, `independent_quota`, `independent_none` o `independent_pending`) y su evidencia. `political_alignment` y la estratificación de la validación se derivan de `political_group_party`. Solo quienes carecen de bancada y de pacto identificables permanecen como `nonpartisan`.

Las bancadas se asignan con estas reglas:

1. Un comité de un solo partido e independientes se asigna a ese partido.
2. Un comité mixto de varios partidos se asigna al partido del cupo cuando este lo integra. Si no lo integra y todos sus partidos comparten alineación, se asigna al primer partido nombrado. En los demás casos se asigna a «Independiente».
3. Un comité formado solo por independientes se asigna a «Independiente».
4. Sin bancada documentada en la fecha se usa el partido del cupo, salvo que la evidencia muestre que la persona había dejado la bancada de ese partido; en ese caso se clasifica como `nonpartisan`.

Los integrantes del Ejecutivo se clasifican por su militancia en la fecha. Los independientes del Ejecutivo, que no tienen bancada ni cupo, se asignan al partido con el que una fuente documenta una cercanía explícita (`cercania`, registrado como `independent_affinity`); la asignación no afirma militancia. Sin cercanía documentada permanecen como `nonpartisan`. En los análisis y en la validación, su alineación se deriva igual que la de los parlamentarios; el tipo de actor se conserva por separado.

Cuando la BCN registra como independiente a una persona que, según otras fuentes, militaba en la fecha, la militancia no se corrige: la discrepancia se anota y el grupo se asigna por su bancada. Las autoridades de las cámaras mantienen su función como tipo de actor. La centroizquierda comprende a los partidos ex concertacionistas (PPD, PR, PS y DC), al Partido Liberal y a los independientes asignados a sus bancadas o pactos.

La misma definición se utiliza en los procedimientos analíticos y en el diseño de la validación manual, y cada sesión conserva las listas y su hash.

## 2. Libro de códigos y anotaciones

El libro reúne 16 conceptos en cinco familias: criterios CARIN, criterios contextuales, justificaciones distributivas del caso, justificaciones institucionales del caso y una justificación procedimental. Esta última, acuerdos y moderación democrática, surgió inductivamente durante la segunda validación manual del pilotaje. No es un criterio distributivo ni de merecimiento, y los análisis la identifican como una familia distinta. `annotations.qmd` utiliza `features/codebook/codebook_v5.xlsx` y genera su representación JSON. Cada ejecución conserva una copia del instrumento y su hash; la versión interna del libro y su contenido identifican el instrumento aplicado.

La versión v5 es el instrumento definitivo y queda cerrada antes de la codificación del corpus y de la validación ciega. Solo se reabre bajo la condición definida en la sección 3.1; en ese caso, la nueva versión se aplica a todo el corpus y se valida con una nueva muestra.

La postura toma los valores `support` y `oppose` respecto de la proposición afirmativa definida en `orientation_anchor`. Por ejemplo, respaldar la ineficiencia y riesgo estatal significa aceptar que esos riesgos justifican limitar la administración estatal. La postura se refiere a esa proposición y se distingue del voto sobre la ley o del tono emocional del hablante.

### 2.1 Contrato de salida

El contrato ejecutable se define en `output_schema()` y `validate_output()` de `features/llm_annotations/pipeline.py`. El prompt activo se conserva en `prompts/annotations_pilot_v1_confidence.md` y se copia en cada ejecución. Sus campos principales son:

| Nivel | Campos | Función |
| --- | --- | --- |
| Bloque | `decision`, `annotations` | Distinguir declaraciones codificables de ausencia de declaraciones. |
| Bloque | `quality_flags`, `decision_confidence` | Registrar problemas del texto y confianza en la decisión. |
| Anotación | `evidence_text`, `evidence_occurrence` | Identificar la cita literal y su aparición dentro del bloque. |
| Anotación | `concept_id` | Identificar exclusivamente un concepto del libro cerrado. |
| Anotación | `stance`, `confidence` | Registrar orientación y confianza cualitativa. |
| Anotación | `justification` | Explicar brevemente la asignación del concepto y su orientación. |

`decision` admite `statements` y `no_statements`. La segunda opción exige una lista vacía de anotaciones. Una respuesta inválida o incompleta se conserva como incidencia de procesamiento; no equivale a ausencia de declaraciones.

Los niveles de confianza son `high`, `medium` y `low`. La confianza media o baja remite automáticamente el caso a revisión humana. Estos niveles representan una valoración del modelo y no una probabilidad calibrada de acierto.

### 2.2 Controles de consistencia y revisión

El programa comprueba que cada cita existe literalmente en el bloque objetivo, calcula sus offsets y valida que el concepto pertenezca al libro cerrado. Rechaza duplicaciones del mismo pasaje, concepto y orientación. Cuando un pasaje recibe varios conceptos, cada anotación sigue las mismas reglas de alcance, orientación y justificación que cualquier otra anotación. Si un concepto aparece con `support` y `oppose` dentro del mismo bloque, ambas codificaciones se conservan y el programa remite el caso a revisión humana sin solicitar esa decisión al modelo.

El contrato ya no admite conceptos propuestos. `needs_human_review`, `review_reasons` y los campos de compatibilidad `concept_status=in_codebook` y `proposed_concept=null` se agregan localmente a la representación normalizada; no forman parte de la respuesta solicitada al modelo.

La referencia humana se codifica a ciegas y permanece inmutable durante la comparación principal. Después de calcularla, el mismo investigador revisa los bloques con discrepancias y registra una adjudicación separada como `resolved` o `unresolved`, con los pares concepto-postura finales y una razón. `resolution_status=unresolved` exige una incidencia que explique la insuficiencia y mantiene `decision=null`. Esos casos se distinguen de las decisiones negativas y se contabilizan como información faltante. Los bloques clasificados como votación o contenido procedimental también se excluyen de los denominadores de desempeño y de presencia. La base analítica utiliza la anotación adjudicada y mantiene las salidas automáticas y la referencia ciega para auditoría. La pestaña de revisión LLM pertenece al desarrollo del prompt y del libro y no sustituye esta comparación.

### 2.3 Codificación complementaria de necesidad y reciprocidad (condicional)

Este procedimiento es condicional: se realizará si el calendario lo permite y, en ese caso, sus resultados se reportarán como análisis exploratorio, separados del contraste de hipótesis.

Necesidad material y reciprocidad contributiva no registran rechazos en la codificación preliminar: su postura casi no varía y no distingue coaliciones. Para examinar si el consenso sobre el criterio encubre desacuerdos sobre su traducción institucional, sus declaraciones adjudicadas reciben una codificación complementaria del arreglo previsional que justifican. Las categorías son cuenta individual, seguro social o fondo solidario, pensión no contributiva, compensaciones o bonificaciones y otro o indeterminado.

La codificación usa la cita, el bloque y su contexto ya registrados, y no modifica el concepto ni la postura de la anotación original. Se ejecuta después de la adjudicación del corpus, con un esquema de salida propio que conserva `annotation_id`, `unit_id` y la ejecución de origen. Su validación sigue las reglas de la sección 3 sobre una submuestra ciega de estas declaraciones.

## 3. Validación y conservación de las ejecuciones

La validación distingue la identificación de declaraciones, la asignación de conceptos y la orientación frente a ellos. Randerson et al. (2025) y Angst et al. (2025) respaldan esta separación de tareas y la necesidad de contrastar la automatización con codificación humana.

Las rondas de calibración manual y los pilotos preceden a la evaluación de una muestra estratificada. La muestra se estratifica en primer lugar por concepto asignado por el modelo, con una cuota mínima para cada concepto que permita estimar su precisión; los conceptos infrecuentes se incluyen completos cuando no alcanzan esa cuota. Incorpora además un estrato de bloques elegibles sin anotaciones para estimar la sensibilidad, es decir, las declaraciones omitidas por el modelo. Dentro de estos estratos, el diseño garantiza cobertura por ley y cámara e incorpora como dimensiones adicionales la alineación política —izquierda, centro, derecha, `nonpartisan`, `unclassified`, `Sin dato` o `No aplica`— y el género. Las afiliaciones históricas desconocidas y los casos no aplicables permanecen en categorías explícitas. El tipo de actor se conserva para estudiar la distribución de los errores y puede incorporarse mediante cuotas marginales o análisis posterior. Antes del sorteo se revisan los tamaños de celda del cruce para evitar cuotas cero. La selección conserva la trazabilidad de cada fragmento. El estrato y la probabilidad de selección acompañan cada caso cuando las fracciones de muestreo difieren.

Se informarán precisión, sensibilidad y F1 por concepto y postura, matrices de confusión y kappa de Cohen. La comparación principal usa el bloque como unidad y contrasta los conjuntos de conceptos y posturas de la referencia humana ciega con la salida automática. Registra `concept_and_stance` cuando coinciden ambos componentes, `concept_only` cuando coinciden los conceptos y cambia alguna postura, y `divergent` cuando difieren los conjuntos conceptuales. El estado `concept_review_required` se conserva solo para leer rondas históricas con propuestas fuera del libro; no se genera en la codificación cerrada. Los fallos de ejecución se registran como `model_unavailable`. Esta comparación no utiliza el solapamiento de spans. Las decisiones de ausencia forman parte de la rejilla común solo cuando el bloque está resuelto e incluido en la evaluación.

Las comparaciones entre tareas y categorías informarán sus denominadores y el número de casos. Tras congelar la referencia ciega, los metadatos de muestreo se anexan por `unit_id` para describir la concentración de errores por ley, cámara, alineación política, género y tipo de actor; las proporciones ponderadas se calculan dentro de cada grupo. Se describirán también las modificaciones introducidas mediante adjudicación y la distribución de los casos irresolubles. La referencia ciega produce las métricas principales; las medidas recalculadas después de adjudicar discrepancias se presentan como análisis secundario. Al existir una sola persona codificadora, no se estima confiabilidad intercoder; puede evaluarse estabilidad intracoder mediante una recodificación diferida y ciega de un subconjunto. Si una segunda persona codifica una submuestra, se informará además la concordancia entre personas.

### 3.1 Umbrales y congelamiento

Los umbrales se fijan antes de codificar la referencia ciega: F1 ≥ 0,70 por concepto y concordancia de postura ≥ 0,80 entre los bloques con coincidencia conceptual. Los conceptos bajo el umbral se reportan con su desempeño; sus resultados se describen, pero no sostienen por sí solos el contraste de una hipótesis. El libro se reabre solo si alguno de los conceptos que definen los repertorios de H1a y H3 —propiedad individual, capitalización individual, reciprocidad contributiva, conciencia de costos, ineficiencia y riesgo estatal, previsión como mercado, igualdad o universalismo y solidaridad intergeneracional— no alcanza el umbral y el examen de las discrepancias atribuye el error a la definición y no al modelo.

### 3.2 Comparación de modelos (condicional)

Este procedimiento es condicional: se realizará si el calendario lo permite. Si no se realiza, el corpus se codifica con el modelo utilizado en los pilotos y se informa su desempeño frente a la referencia ciega.

La muestra de validación se codifica también con modelos alternativos, con el mismo libro, el mismo prompt y el mismo esquema de salida. La comparación usa la misma referencia ciega y las mismas métricas. El modelo que se aplica al corpus completo se selecciona según el F1 macro de conceptos y la concordancia de postura, antes de examinar resultados sustantivos con cualquiera de ellos. Si otro modelo se aplica al corpus completo, sus resultados se presentan como análisis de sensibilidad y no sustituyen la selección.

### 3.3 Registro de las ejecuciones

Cada ejecución registra el modelo, la configuración, la muestra, el prompt, el esquema de salida y los hashes del corpus, del código y del libro. `results.parquet` conserva decisiones e incidencias por bloque; `annotations.parquet` conserva las anotaciones y sus evidencias. La validez del formato de salida y la exhaustividad de una ejecución se describen separadamente de su concordancia con la codificación humana.

## 4. Agregación y denominadores

### 4.1 Conteo dentro de las intervenciones

Sea \(u\) una intervención, \(c\) un concepto y \(s\in\{+,-\}\) una postura. Se define:

\[
D_{ucs}=\mathbf{1}\{\text{existe al menos una declaración adjudicada de }c\text{ con postura }s\text{ en }u\}.
\]

Una repetición del mismo concepto y postura en varios fragmentos de la intervención mantiene \(D_{ucs}=1\). Otra intervención del mismo actor genera otra observación. El apoyo y el rechazo pueden coexistir dentro de una intervención cuando distintos pasajes sustentan cada postura.

La presencia del concepto con independencia de su orientación es:

\[
P_{uc}=\max(D_{uc+},D_{uc-}).
\]

Así, una intervención que contiene apoyo y rechazo cuenta una vez para presencia y una vez en cada postura para los conteos desagregados. La suma de porcentajes de apoyo y rechazo puede superar el porcentaje de presencia.

### 4.2 Frecuencias y cobertura

Para una ventana \(t\), sea \(U_t\) el conjunto de intervenciones analizadas y \(A_t\) el conjunto de sus actores. Se calcularán:

\[
f_{cts}=\frac{\sum_{u\in U_t}D_{ucs}}{|U_t|},
\qquad
p_{ct}=\frac{\sum_{u\in U_t}P_{uc}}{|U_t|}.
\]

\(f_{cts}\) representa la proporción de intervenciones con una postura y \(p_{ct}\), la proporción que menciona el concepto. Para describir la extensión entre personas se utilizará:

\[
a_{cts}=\frac{\left|\left\{a\in A_t:\sum_{u\in U_t:a(u)=a}D_{ucs}>0\right\}\right|}{|A_t|}.
\]

La cobertura cuenta personas para describir alcance. Las demás medidas conservan todas sus intervenciones. Un actor puede contribuir a las coberturas de todas las fases en que participa y a ambas posturas cuando expresa posiciones diferentes.

Los denominadores incluyen intervenciones analizadas sin declaraciones normativas. Los errores de ejecución, las adjudicaciones irresolubles, las votaciones y los bloques procedimentales no se convierten en ceros y quedan fuera de los porcentajes. La presencia está establecida cuando existe evidencia adjudicada; la ausencia requiere que la intervención esté completamente revisada o procesada con salidas válidas, sin decisiones pendientes y con al menos un bloque analíticamente elegible. Se informarán por separado los casos cuyo estado impida establecerla. Cuando existan datos faltantes, cada proporción utilizará las intervenciones o actores con estado conocido para el concepto y la postura correspondientes, e informará ese denominador efectivo.

El balance de posturas se describirá mediante las dos frecuencias y, cuando se sintetice, mediante \(f_{ct+}-f_{ct-}\). Multiplicado por 100, este balance expresa diferencias en puntos porcentuales; no mide intensidad individual de una creencia.

### 4.3 Ventanas de comparación

H2 compara por separado las leyes 21.419, 21.538 y 21.735. H1a y H1b se aplican al conjunto de discusiones de la reforma 21.735; la detección de coaliciones se repite por ventana como análisis de sensibilidad. H3 distingue las siguientes ventanas dentro de esta reforma:

| Ventana | Cámara y fechas | Función |
| --- | --- | --- |
| Primer trámite | Cámara, 23 y 24 de enero de 2024 | Configuración inicial observada. |
| Segundo trámite | Senado, 27 de enero de 2025 | Configuración del debate en el Senado. |
| Tercer trámite | Cámara, 29 de enero de 2025 | Configuración final observada en la Cámara. |

Las diferencias entre Cámara y Senado describen composiciones del debate, no trayectorias individuales.

## 5. Redes de actores y detección de coaliciones

### 5.1 Matrices de afiliación

Para cada ventana se construyen dos matrices de frecuencias:

\[
X^s_{ac,t}=\sum_{u\in U_t:a(u)=a}D_{ucs}.
\]

Cada celda cuenta intervenciones del actor con una postura ante un concepto. La deduplicación dentro de la intervención evita que la segmentación o la repetición inmediata multipliquen artificialmente una afirmación. La acumulación entre intervenciones conserva su reiteración discursiva.

### 5.2 Congruencia y conflicto normalizados

Se utiliza un denominador común basado en la norma del perfil completo de cada actor:

\[
n_{a,t}=\sqrt{\sum_c\left[(X^+_{ac,t})^2+(X^-_{ac,t})^2\right]}.
\]

Para dos actores distintos:

\[
G_{ab,t}=\frac{\sum_c\left[X^+_{ac,t}X^+_{bc,t}+X^-_{ac,t}X^-_{bc,t}\right]}{n_{a,t}n_{b,t}},
\]

\[
C_{ab,t}=\frac{\sum_c\left[X^+_{ac,t}X^-_{bc,t}+X^-_{ac,t}X^+_{bc,t}\right]}{n_{a,t}n_{b,t}},
\qquad S_{ab,t}=G_{ab,t}-C_{ab,t}.
\]

\(G\) compara posturas coincidentes y \(C\) compara el perfil de un actor con el del otro tras intercambiar apoyo y rechazo. Ambas son semejanzas coseno entre vectores no negativos; \(S\) expresa el saldo entre congruencia y conflicto. Se eliminan las diagonales. Los actores sin declaraciones codificadas tienen norma cero y se mantienen en los descriptivos del corpus, pero carecen de perfil para calcular estas semejanzas.

Leifeld (2017) desarrolla las proyecciones de congruencia y conflicto, las normalizaciones de perfiles y la resta entre ambas redes. La aplicación a frecuencias de intervenciones es la especificación adoptada aquí. La normalización es invariante a multiplicar todo el perfil de un actor por una constante: reduce el efecto de su volumen total de participación, aunque conserva las diferencias en el énfasis relativo de sus conceptos.

Un valor \(S_{ab,t}=0\) puede resultar de ausencia de coincidencias o de un equilibrio entre congruencia y conflicto. Por ello, se conservan \(G\) y \(C\) para interpretar los vínculos y se utiliza \(S\) para detectar comunidades.

### 5.3 Comunidades y estabilidad

Se aplicará *signed spin-glass* a \(S\), conservando pesos positivos y negativos, siguiendo el uso de redes con signo en Schaub (2021). En `igraph`, la implementación que admite pesos negativos se identifica como `neg`; el parámetro `spins` fija un máximo de grupos posibles, no su número observado. Se registrarán implementación, versión, máximo de grupos, parámetros de resolución, temperaturas, enfriamiento y semillas. Véase la [documentación oficial de `cluster_spinglass`](https://r.igraph.org/reference/cluster_spinglass.html).

Las repeticiones con distintas semillas conservarán sus particiones y valores de ajuste. Se describirán la frecuencia de las soluciones y la proporción de ejecuciones en que cada par de actores queda en la misma comunidad. Los nodos aislados se reportarán sin atribuirles una coalición sustantiva. Si la red se analiza por componentes conectados, la partición y sus parámetros se conservarán por componente y las etiquetas no se equipararán automáticamente entre componentes o ventanas.

La interpretación comparará conceptos y posturas dentro de cada comunidad y entre comunidades. Las etiquetas de preservación y transformación se asignarán según sus repertorios, después de estimar la partición. La identificación de dos grupos se acompañará por el examen de su contenido, porque la codificación de argumentos opuestos sobre un asunto puede favorecer la bipolarización (Leifeld, 2017). Las comunidades que no correspondan a los polos esperados se etiquetarán según sus conceptos distintivos y se analizarán de forma exploratoria, separadas del contraste de H1a.

### 5.4 Análisis de sensibilidad

La partición principal agrega las tres ventanas de la reforma. Se repetirá con las mismas especificaciones en dos variantes:

| Variante | Construcción | Pregunta |
| --- | --- | --- |
| Por ventana | \(S_{ab,t}\) calculada por separado para cada trámite de la sección 4.3 | ¿Las coaliciones dependen de agregar declaraciones de distintas fases? |
| Sin concepto procedimental | \(X^+\) y \(X^-\) sin `acuerdos_moderacion` antes de normalizar | ¿Las coaliciones se sostienen en justificaciones sustantivas o en el valor atribuido al compromiso? |

Las particiones se comparan con la principal mediante la proporción de pares de actores que permanecen juntos o separados y la información mutua normalizada, calculadas sobre los actores presentes en ambas redes. En las ventanas, los actores tienen menos declaraciones y las particiones pueden ser menos estables; se informarán el número de actores con perfil y la frecuencia de cada solución entre semillas. Las etiquetas de comunidades no se equiparan automáticamente entre variantes: la correspondencia se establece por solapamiento de miembros y por repertorio.

## 6. Redes de conceptos y centralidad

### 6.1 Presencia conceptual

Se construye la matriz de frecuencias sin distinguir postura:

\[
M_{ac,t}=\sum_{u\in U_t:a(u)=a}P_{uc}.
\]

Esta matriz se obtiene directamente de \(P\), no de la suma de \(X^+\) y \(X^-\), para contar una sola vez las intervenciones que contienen ambas posturas. Dos conceptos se conectan según la semejanza de sus perfiles entre actores:

\[
W^{P}_{cd,t}=\frac{\sum_aM_{ac,t}M_{ad,t}}
{\sqrt{\sum_a M_{ac,t}^2}\sqrt{\sum_a M_{ad,t}^2}},\qquad c\ne d.
\]

La fuerza del concepto es \(k_{c,t}=\sum_{d\ne c}W^{P}_{cd,t}\). Se compara su posición relativa entre conceptos y entre ventanas, utilizando el mismo universo del libro. Los conceptos ausentes tienen norma cero: sus vínculos se fijan en cero y mantienen fuerza cero; los empates conservan la misma posición. Se presentan las frecuencias junto con la centralidad, ya que una semejanza elevada entre perfiles escasos no equivale a una presencia extendida.

La red incorpora apoyos y rechazos. La centralidad indica integración en los repertorios del debate, mientras las posturas muestran cómo se disputa el concepto. Esta distinción recoge el tratamiento de relaciones de afiliación y de centralidad conceptual de Leifeld y Haunss (2012).

### 6.2 Congruencia conceptual

La red de congruencia conecta conceptos usados por un mismo actor con la misma orientación. Se calcula:

\[
W^{G}_{cd,t}=\frac{\sum_a\left[X^+_{ac,t}X^+_{ad,t}+X^-_{ac,t}X^-_{ad,t}\right]}
{\sqrt{\sum_a\left[(X^+_{ac,t})^2+(X^-_{ac,t})^2\right]}
 \sqrt{\sum_a\left[(X^+_{ad,t})^2+(X^-_{ad,t})^2\right]}},\qquad c\ne d.
\]

Las diagonales y los vínculos de conceptos con norma cero se fijan en cero en ambas redes conceptuales. Las contribuciones de apoyo y rechazo se conservan para la interpretación, aunque se suman en el vínculo de congruencia. La proximidad entre dos conceptos significa que forman parte de repertorios de los mismos actores; la lectura textual determina si existe una relación argumental entre ellos.

### 6.3 Congruencia conceptual por coalición

Para comparar cómo cada coalición articula los mismos criterios, la red de congruencia se estima dentro de cada comunidad \(k\) de la partición principal, con nodos distintos para cada combinación de concepto y postura, \((c,s)\). Sea \(A_k\) el conjunto de actores de la comunidad y \(B^s_{ac}=\mathbf 1\{X^s_{ac}>0\}\). El vínculo entre dos posiciones es:

\[
W^{k}_{(c,s),(d,r)}=\frac{1}{|A_k|}\sum_{a\in A_k}B^s_{ac}\,B^r_{ad},\qquad (c,s)\ne(d,r).
\]

\(W^k\) expresa la proporción de actores de la coalición que sostienen ambas posiciones. La normalización por el tamaño de la comunidad permite comparar coaliciones de distinto tamaño. A diferencia de \(W^G\), esta red conserva la dirección de cada posición: un rechazo conjunto a capitalización individual y previsión como mercado no se confunde con un apoyo conjunto. También admite vínculos entre posiciones de signo distinto, que muestran qué criterios se apoyan junto con qué rechazos.

Las posiciones sostenidas por menos del 10 % de los actores de la comunidad se omiten de la visualización, pero se conservan en las matrices. Las tres redes se representan con la misma disposición de nodos, fijada sobre la unión de sus posiciones, para que las diferencias correspondan a los vínculos y no a la ubicación. Se acompañan de una tabla con los cinco pares más frecuentes de cada coalición. El concepto procedimental se distingue visualmente de los criterios de justicia.

### 6.4 Participación transversal de actores y conceptos

H1b se evalúa mediante el coeficiente de participación (Guimerà & Nunes Amaral, 2005), que mide si los vínculos de un nodo se distribuyen entre varias comunidades o se concentran en una. Para los actores se aplica en su forma original, sobre los vínculos de la red de congruencia; para los conceptos se adapta a sus vínculos de apoyo con actores y se corrige por el tamaño de las comunidades. Se sustituye la intermediación por caminos mínimos porque, en la proyección densa de 16 conceptos, un concepto apoyado por casi todos los actores se conecta directamente con los demás y obtiene una intermediación baja por construcción.

Para un concepto \(c\), sea \(n_k\) el número de actores con perfil en la comunidad \(k\) y \(r_{ck}\) la proporción de ellos que lo apoyan. Para corregir las diferencias de tamaño entre comunidades se usa \(q_{ck}=r_{ck}/\sum_{k'}r_{ck'}\), y:

\[
P_c=\frac{1-\sum_{k=1}^{K}q_{ck}^2}{1-1/K}.
\]

\(P_c\) vale 1 cuando el apoyo se reparte de igual forma entre las \(K\) comunidades y 0 cuando procede de una sola. Se calcula por separado para el rechazo cuando el concepto registra oposición. Se informan también \(r_{ck}\) y el número de apoyos, porque un concepto con escasos apoyos repartidos puede alcanzar un valor alto.

Para un actor \(a\) de la comunidad \(k(a)\), sea \(g_{a\ell}=\sum_{b\in\ell,\,b\ne a}G_{ab}\) la suma de sus vínculos de congruencia hacia la comunidad \(\ell\) y \(g_a=\sum_\ell g_{a\ell}\). Se calculan:

\[
P_a=\frac{1-\sum_{\ell}(g_{a\ell}/g_a)^2}{1-1/K},
\qquad
E_a=1-\frac{g_{a,k(a)}}{g_a}.
\]

\(E_a\) es la proporción de congruencia dirigida fuera de la propia comunidad. Como las comunidades se estiman sobre \(S\), la posición de un actor en su comunidad y su participación no son independientes; por ello, la comparación entre centroizquierda y los demás grupos se acompaña de la distribución de la centroizquierda entre comunidades. Los actores sin perfil quedan fuera.

Para H1b se compara la distribución de \(P_a\) y \(E_a\) de los parlamentarios de centroizquierda con la de los demás grupos, y \(P_c\) de necesidad material con la de los demás conceptos. Un valor alto de \(P_c\) puede corresponder a un puente entre repertorios o a un terreno común aceptado por todas las coaliciones. La distinción se establece con la red de 6.3 y la lectura dirigida: un puente se vincula con posiciones distintivas de varias coaliciones, mientras que un terreno común se combina con repertorios que siguen siendo opuestos.

## 7. Comparación entre proyectos: polarización en H2

H2 compara la reforma 21.735, que disputa el destino de las cotizaciones, con los debates de la PGU, que tratan una prestación no contributiva sin alterar la cuenta individual. Cada componente de la hipótesis se traduce en una pregunta y una medida, calculada por separado para cada ley \(L\) con las unidades y denominadores de la sección 4:

| Componente de H2 | Pregunta | Medida | Se espera en la 21.735 |
| --- | --- | --- | --- |
| Posturas divididas | ¿Qué parte de las declaraciones contradice la postura mayoritaria sobre su concepto? | Índice de disputa \(D_L\) (7.1) | Mayor que en las leyes de la PGU |
| Conflicto entre actores | ¿Qué parte de las semejanzas entre perfiles de actores corresponde a posturas opuestas? | Proporción de conflicto \(R_L\) (7.1) | Mayor que en las leyes de la PGU |
| Intensidad de la defensa | ¿Cuántas justificaciones normativas formula la derecha por intervención? | Densidad normativa \(\rho_{GL}\) (7.2) | Mayor que la de la derecha en las leyes de la PGU |

Cada medida se informa con su intervalo de remuestreo (7.3). H2 se considera respaldada en la medida en que las tres comparaciones apunten en la dirección esperada; se reporta cada una por separado y no se combinan en un índice. La presencia de propiedad y capitalización individual se describe como contraste, advirtiendo que su menor presencia en los debates de la PGU responde en parte a la materia de esos proyectos.

### 7.1 Polarización

**Índice de disputa.** Para cada concepto y ley, sean \(n^+_{cL}=\sum_{u\in U_L}D_{uc+}\) y \(n^-_{cL}=\sum_{u\in U_L}D_{uc-}\) las intervenciones con apoyo y con rechazo. El índice de la ley es la proporción de todas las declaraciones con postura que están en la postura minoritaria de su concepto:

\[
D_L=\frac{\sum_c \min\left(n^+_{cL},\,n^-_{cL}\right)}{\sum_c \left(n^+_{cL}+n^-_{cL}\right)}.
\]

\(D_L\) vale 0 cuando cada concepto recibe una sola postura y se acerca a 0,5 cuando todos se dividen por mitades. Pondera cada concepto por su número de declaraciones, de modo que no depende de umbrales ni del número de conceptos presentes en cada ley. Un recuento de conceptos disputados sí dependería de ese número: en la codificación preliminar, solo 4 conceptos de la Ley 21.538 reúnen 10 o más declaraciones con postura, frente a 14 en la Ley 21.735. Como descripción, se informa para cada concepto su proporción minoritaria \(m_{cL}=\min(n^+_{cL},n^-_{cL})/(n^+_{cL}+n^-_{cL})\), que muestra qué conceptos concentran la disputa.

**Conflicto entre actores.** Con las matrices de la sección 5 calculadas por ley, se define la proporción de conflicto:

\[
R_L=\frac{\sum_{a<b}C_{ab,L}}{\sum_{a<b}\left(G_{ab,L}+C_{ab,L}\right)}.
\]

\(D_L\) mide la disputa en las declaraciones; \(R_L\), en las relaciones entre actores. Pueden divergir: un concepto disputado por pocos actores muy activos eleva \(D_L\) más que \(R_L\). \(R_L\) se informa junto con el número de actores con perfil de cada ley, porque los debates de la PGU tienen redes más pequeñas.

### 7.2 Intensidad normativa

Para cada ley y grupo político \(G\), la densidad normativa es el número de pares concepto-postura por intervención sustantiva:

\[
\rho_{GL}=\frac{\sum_{u\in U_{GL}}\sum_{c,s}D_{ucs}}{|U_{GL}|}.
\]

La comparación principal es la derecha en la 21.735 frente a la derecha en las leyes de la PGU. Se desagrega por familia del libro de códigos para distinguir si una mayor densidad procede de criterios de merecimiento, de justificaciones institucionales del caso —propiedad individual, capitalización individual, ineficiencia y riesgo estatal, previsión como mercado y libertad de elección— o del concepto procedimental. Como el libro solo registra justificaciones normativas, \(\rho\) mide la frecuencia con que se justifican posiciones, no la carga emocional del discurso.

### 7.3 Incertidumbre e interpretación

Los intervalos se estiman mediante remuestreo de actores con reemplazo dentro de cada ley, conservando todas las intervenciones del actor seleccionado. Así se respeta la dependencia entre intervenciones de una misma persona. Se usan 2.000 réplicas e intervalos percentiles al 95 %. En \(R_L\), cada réplica recalcula las matrices con los actores remuestreados. Las diferencias entre leyes se estiman como la diferencia de cada medida dentro de réplicas independientes de ambas leyes.

Las nueve discusiones y las tres leyes delimitan el alcance del diseño. Las diferencias entre leyes describen los procesos observados y no identifican un efecto general del carácter estructural de una reforma. La comparación informa magnitudes y direcciones; la interpretación conjunta no depende de seleccionar las diferencias con intervalos que excluyen cero.

## 8. Persistencia y análisis exploratorio

### 8.1 Persistencia en H3

Para los seis conceptos del repertorio asociado a la capitalización individual —propiedad individual de los fondos, capitalización individual, reciprocidad contributiva, conciencia de costos, ineficiencia y riesgo estatal y previsión como mercado— se compararán presencia, cobertura de apoyo, balance de posturas, fuerza y posición relativa en las tres ventanas de la reforma. Se conservarán las relaciones de reciprocidad, costos y justificaciones institucionales con propiedad y capitalización individual.

La continuidad de centralidad con rechazo sostenido se interpretará como persistencia del concepto en la controversia. La continuidad de apoyo informa sobre su aceptación. Las trayectorias pueden diferir entre componentes; se reportarán esas diferencias y sus argumentos, sin asignar un resultado único al conjunto por una suma arbitraria de indicadores.

La ausencia de significación estadística no demuestra estabilidad. La evaluación descriptiva informará magnitud y dirección de los cambios. Una prueba de equivalencia requeriría un margen sustantivo definido con anterioridad; las medidas descritas aquí no establecen ese margen ni constituyen por sí mismas una prueba de equivalencia.

### 8.2 Coaliciones no anticipadas

Las comunidades que no corresponden a los polos de H1a se examinan después del contraste de H1b, como análisis exploratorio. Esta sección se formuló después de los resultados preliminares y se reporta como tal. Para cada una se describen su composición por grupo político, ventana y tipo de actor; sus conceptos y posturas distintivos, en comparación con las demás comunidades; su red de congruencia de la sección 6.3; y su estabilidad en las variantes de la sección 5.4.

La lectura de pasajes establece si sus miembros reconocen premisas del repertorio asociado a la capitalización individual, si las combinan con justificaciones de transformación o si justifican la reforma principalmente por el valor del compromiso. Sus resultados se interpretan como hallazgos descriptivos que orientan la discusión, no como contraste de una expectativa previa.

## 9. Selección de pasajes e interpretación de la estructuración

La selección textual responde a resultados identificables: conceptos de alta centralidad, vínculos entre coaliciones, posiciones de participación transversal, pares distintivos de las redes por coalición y trayectorias de apoyo o rechazo. Incluye casos discrepantes y conserva los identificadores de actor, ley, fase, intervención y fragmento.

Cada lectura registra la proposición defendida, sus fundamentos, el arreglo distributivo que justifica y su relación con premisas de otros repertorios. El predominio requiere mostrar que esas premisas son reconocidas o condicionan propuestas rivales. La presencia de una palabra o la proximidad de dos conceptos en la red sirve para seleccionar evidencia; la interpretación descansa en el argumento completo.

Este procedimiento distingue conceptos centrales como objetos de controversia de principios aceptados como fundamentos de las propuestas. También examina si reciprocidad y restricciones de gasto sostienen la acumulación individual o arreglos colectivos, según sus relaciones con las demás justificaciones y, si se realiza, la codificación complementaria de la sección 2.3.

## 10. Registro reproducible

Las salidas del análisis conservarán:

- La versión del corpus, el libro, el prompt y las anotaciones adjudicadas, con sus identificadores y hashes.
- La tabla de grupos políticos, las ventanas temporales, las reglas de inclusión y los denominadores de cada comparación.
- Las matrices \(X^+\), \(X^-\), \(M\), \(G\), \(C\), \(S\), \(W^P\), \(W^G\) y \(W^k\), con nodos identificados y la misma ordenación de conceptos.
- Las configuraciones y semillas de comunidades, las particiones obtenidas, sus diagnósticos de estabilidad y las particiones de las variantes de sensibilidad.
- Los coeficientes de participación de actores y conceptos, y las medidas de disputa, conflicto y densidad de H2 con sus réplicas de remuestreo.
- Los umbrales de validación aplicados y, si se realiza la comparación de modelos, las métricas de cada modelo y la regla de selección.
- Si se realiza, la codificación complementaria de necesidad y reciprocidad, con su ejecución y validación.
- Los pasajes seleccionados y las decisiones interpretativas que vinculan los patrones cuantitativos con los argumentos.

Las fuentes académicas citadas se encuentran en la bibliografía de la tesis. Las fórmulas de este suplemento explicitan las decisiones de este estudio sobre las relaciones descritas por el DNA; el registro de ejecución documentará su aplicación al corpus.
