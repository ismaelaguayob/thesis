# Material suplementario metodológico

Este documento detalla las reglas de codificación, construcción de redes y comparación estadística que respaldan la metodología de [la tesis](../thesis.md). La exposición principal presenta la secuencia del análisis y su relación con las hipótesis; este suplemento precisa las unidades, los denominadores, las fórmulas y los criterios de interpretación necesarios para reproducirlo.

## 1. Unidades y trazabilidad

| Unidad | Definición y función |
| --- | --- |
| Proyecto de ley | Proceso legislativo identificado por ley y boletín. La creación de la PGU, su ampliación y la reforma previsional se comparan separadamente. |
| Fase legislativa | Agrupación de discusiones según trámite y cámara. Organiza la comparación temporal dentro de la reforma. |
| Discusión en Sala | Documento del corpus identificado por `document_uri`, con fecha, cámara y trámite. |
| Intervención | Participación de un actor identificada por `utterance_id` dentro del documento. Es la unidad de los porcentajes de presencia y de los modelos logísticos. |
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

La clasificación en grupos políticos utiliza la afiliación correspondiente a la fecha del debate. `proc.qmd` enlaza `parliamentarian_affiliations.parquet` mediante documento y persona y conserva `party_at_date`, el estado del emparejamiento y la fuente; `current_party` permanece como dato de procedencia. `party_at_date_status` distingue afiliación encontrada, afiliación no aplicable para funciones institucionales o ejecutivas y afiliación desconocida. Solo las afiliaciones encontradas se convierten en `political_alignment`. Una configuración única y versionable, la variable de entorno `PARTY_ALIGNMENT` leída desde `.env`, enumera en formato JSON los partidos asignados a `left` y `right`; los partidos encontrados que no aparecen en esas listas forman la categoría residual de centro. Los estados desconocidos y no aplicables se conservan separados y no se imputan al centro. La misma definición se utiliza en los procedimientos analíticos y en el diseño de la validación manual, y cada sesión conserva las listas y su hash.

## 2. Libro de códigos y anotaciones

El libro reúne criterios CARIN, criterios contextuales y justificaciones distributivas e institucionales del caso chileno. `annotations.qmd` utiliza `features/codebook/codebook_v0.3.xlsx` y genera su representación JSON. Cada ejecución conserva una copia del instrumento y su hash; la versión interna del libro y su contenido identifican el instrumento aplicado.

La postura toma los valores `support` y `oppose` respecto de la proposición afirmativa definida en `orientation_anchor`. Por ejemplo, respaldar la ineficiencia y riesgo estatal significa aceptar que esos riesgos justifican limitar la administración estatal. La postura se refiere a esa proposición y se distingue del voto sobre la ley o del tono emocional del hablante.

### 2.1 Contrato de salida

El contrato ejecutable se define en `output_schema()` y `validate_output()` de `features/llm_annotations/pipeline.py`. El prompt activo se conserva en `prompts/annotations_pilot_v1_confidence.md` y se copia en cada ejecución. Sus campos principales son:

| Nivel | Campos | Función |
| --- | --- | --- |
| Bloque | `decision`, `decision_justification`, `annotations` | Distinguir declaraciones codificables de ausencia de declaraciones y justificar la decisión. |
| Bloque | `quality_flags`, `needs_human_review`, `limitations`, `decision_confidence` | Registrar problemas del texto, incertidumbre y remisión a revisión. |
| Anotación | `evidence_text`, `evidence_occurrence` | Identificar la cita literal y su aparición dentro del bloque. |
| Anotación | `concept_status`, `concept_id`, `proposed_concept` | Identificar un concepto del libro o una propuesta que requiere revisión. |
| Anotación | `stance`, `confidence` | Registrar orientación y confianza cualitativa. |
| Justificación | `criterion_reference`, `coding`, `stance`, `alternatives`, `context_evidence`, `uncertainty` | Explicar la regla aplicada, la postura, las alternativas descartadas y el contexto utilizado. |

`decision` admite `statements` y `no_statements`. La segunda opción exige una lista vacía de anotaciones. Una respuesta inválida o incompleta se conserva como incidencia de procesamiento; no equivale a ausencia de declaraciones.

Los niveles de confianza son `high`, `medium` y `low`. La confianza media o baja exige una explicación y revisión humana. Estos niveles representan una valoración del modelo y no una probabilidad calibrada de acierto.

### 2.2 Controles de consistencia y revisión

El programa comprueba que cada cita existe literalmente en el bloque objetivo, calcula sus offsets y valida la referencia al criterio del libro. Rechaza duplicaciones del mismo pasaje y concepto. Cuando un pasaje recibe varios conceptos, cada anotación sigue las mismas reglas de criterio, orientación y justificación que cualquier otra anotación; el esquema no incorpora un tratamiento especial para la multicodificación.

`concept_status=review` se reserva para una justificación explícita que no corresponde al libro. Exige `concept_id=null`, una propuesta conceptual y revisión humana. La duda entre dos códigos existentes se documenta en la justificación. Las propuestas nuevas deben adjudicarse antes de incorporarse a una red con un universo común de conceptos.

La referencia humana se codifica a ciegas y permanece inmutable durante la comparación principal. Después de calcularla, el mismo investigador revisa los bloques con discrepancias y registra una adjudicación separada como `resolved` o `unresolved`, con los pares concepto-postura finales y una razón. `resolution_status=unresolved` exige una incidencia que explique la insuficiencia y mantiene `decision=null`. Esos casos se distinguen de las decisiones negativas y se contabilizan como información faltante. Los bloques clasificados como votación o contenido procedimental también se excluyen de los denominadores de desempeño y de presencia. La base analítica utiliza la anotación adjudicada y mantiene las salidas automáticas y la referencia ciega para auditoría. La pestaña de revisión LLM pertenece al desarrollo del prompt y del libro y no sustituye esta comparación.

## 3. Validación y conservación de las ejecuciones

La validación distingue la identificación de declaraciones, la asignación de conceptos y la orientación frente a ellos. Randerson et al. (2025) y Angst et al. (2025) respaldan esta separación de tareas y la necesidad de contrastar la automatización con codificación humana.

Las rondas de calibración manual y los pilotos preceden a la evaluación de una muestra estratificada. El diseño predeterminado garantiza cobertura por ley y cámara e incorpora como dimensiones adicionales la alineación política —izquierda, derecha o centro— y el género. Las afiliaciones históricas desconocidas y los casos no aplicables permanecen en categorías explícitas. El tipo de actor se conserva para estudiar la distribución de los errores y puede incorporarse mediante cuotas marginales o análisis posterior. Antes del sorteo se revisan los tamaños de celda del cruce para evitar cuotas cero. La selección conserva la trazabilidad de cada fragmento. El estrato y la probabilidad de selección acompañan cada caso cuando las fracciones de muestreo difieren.

Se informarán precisión, sensibilidad y F1 por concepto y postura, matrices de confusión y kappa de Cohen. La comparación principal usa el bloque como unidad y contrasta los conjuntos de conceptos y posturas de la referencia humana ciega con la salida automática. Registra `concept_and_stance` cuando coinciden ambos componentes, `concept_only` cuando coinciden los conceptos y cambia alguna postura, y `divergent` cuando difieren los conjuntos conceptuales. Los conceptos propuestos fuera del libro se separan como `concept_review_required` y pasan a la cola de adjudicación; no cuentan como coincidencias vacías. Los fallos de ejecución se registran como `model_unavailable`. Esta comparación no utiliza el solapamiento de spans. Las decisiones de ausencia forman parte de la rejilla común solo cuando el bloque está resuelto e incluido en la evaluación.

Las comparaciones entre tareas y categorías informarán sus denominadores y el número de casos. Tras congelar la referencia ciega, los metadatos de muestreo se anexan por `unit_id` para describir la concentración de errores por ley, cámara, alineación política, género y tipo de actor; las proporciones ponderadas se calculan dentro de cada grupo. Se describirán también las modificaciones introducidas mediante adjudicación y la distribución de los casos irresolubles. La referencia ciega produce las métricas principales; las medidas recalculadas después de adjudicar discrepancias se presentan como análisis secundario. Al existir una sola persona codificadora, no se estima confiabilidad intercoder; puede evaluarse estabilidad intracoder mediante una recodificación diferida y ciega de un subconjunto.

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

H2 compara por separado las leyes 21.419, 21.538 y 21.735. H1a y H1b se aplican al conjunto de discusiones de la reforma 21.735. H3 distingue las siguientes ventanas dentro de esta reforma:

| Ventana | Cámara y fechas | Función |
| --- | --- | --- |
| Primer trámite | Cámara, 23 y 24 de enero de 2024 | Configuración inicial observada. |
| Segundo trámite | Senado, 27 de enero de 2025 | Configuración del debate en el Senado. |
| Tercer trámite | Cámara, 29 de enero de 2025 | Configuración final observada en la Cámara. |

H4 compara los actores comunes de la primera y tercera ventanas. Las diferencias entre Cámara y Senado describen composiciones del debate; el seguimiento individual corresponde a los participantes presentes en ambas ventanas de la Cámara.

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

La interpretación comparará conceptos y posturas dentro de cada comunidad y entre comunidades. Las etiquetas de preservación y transformación se asignarán según sus repertorios, después de estimar la partición. La identificación de dos grupos se acompañará por el examen de su contenido, porque la codificación de argumentos opuestos sobre un asunto puede favorecer la bipolarización (Leifeld, 2017).

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

Las diagonales y los vínculos de conceptos con norma cero se fijan en cero en ambas redes conceptuales. Las contribuciones de apoyo y rechazo se conservan para la interpretación, aunque se suman en el vínculo de congruencia. Esta red se utiliza para la intermediación de necesidad material en H1b. La proximidad entre dos conceptos significa que forman parte de repertorios de los mismos actores; la lectura textual determina si existe una relación argumental entre ellos.

### 6.3 Intermediación de actores y necesidad material

La intermediación de actores se calcula sobre \(G\), la red de coincidencias de postura. La intermediación conceptual se calcula sobre \(W^G\). En ambas, un peso positivo \(w\) se transforma en distancia \(1/w\); un peso cero representa ausencia de vínculo. Los pesos negativos de \(S\) no se utilizan como distancias ni se sustituyen por su valor absoluto.

Para un nodo \(v\), la intermediación suma la proporción de caminos mínimos entre otros pares de nodos que pasan por él (Freeman, 1977):

\[
B(v)=\sum_{i<j;\,i,j\ne v}\frac{\sigma_{ij}(v)}{\sigma_{ij}}.
\]

Los pares sin camino aportan cero. La normalización para una red no dirigida divide por \((n-1)(n-2)/2\), cuando \(n>2\); los nodos aislados tienen intermediación cero. Se informa el tamaño de la red al comparar ventanas.

Para H1b se compara la distribución de intermediación de parlamentarios de centroizquierda con la de los demás grupos, aunque la red de actores incluye también las otras funciones presentes en el debate. Necesidad material se compara con los demás conceptos y se examinan sus vínculos con los repertorios de ambos polos. La fuerza total, la densidad de la red y las conexiones efectivas entre coaliciones acompañan la interpretación: una proyección muy densa puede ofrecer escasa diferenciación mediante caminos mínimos. La lectura dirigida establece si la posición relacional corresponde a argumentos compartidos o a conexiones entre justificaciones diferentes.

## 7. Comparación entre proyectos y modelos de H2

El repertorio asociado a la capitalización individual se mantiene fijo durante las comparaciones:

| Concepto | Identificador |
| --- | --- |
| Propiedad individual de los fondos | `propiedad_individual_fondos` |
| Capitalización individual | `capitalizacion_individual` |
| Reciprocidad contributiva | `reciprocidad_contributiva` |
| Conciencia de costos | `conciencia_costos` |
| Ineficiencia y riesgo estatal | `ineficiencia_estado` |
| Previsión como mercado | `prevision_como_mercado` |

Para cada uno, H2 compara \(P_{uc}\), su frecuencia por ley y su centralidad en \(W^P\). Para necesidad material e igualdad/universalismo se analiza \(D_{uc+}\) y su cobertura entre grupos políticos. Los conceptos mantienen su identidad y se informan separadamente, sin agregarlos en una escala de justicia de mercado.

### 7.1 Especificación

Se estima un modelo logístico por concepto. La variable dependiente \(Y_{uc}\) es presencia para los seis conceptos del repertorio y apoyo para necesidad e igualdad/universalismo:

\[
\operatorname{logit}\Pr(Y_{uc}=1)=
\alpha_c+\beta_{c,L(u)}+\gamma_{c,G(u)}+
\delta_{c,L(u),G(u)}+\boldsymbol{\theta}_c^\top\mathbf{Z}_u+b_{a(u),c}.
\]

\(L\) representa la ley, \(G\) el grupo político y \(\delta\) su interacción. \(\mathbf Z\) contiene cámara, tipo de actor y longitud de la intervención. \(b_{a,c}\) es un intercepto aleatorio por actor, con distribución normal de media cero y varianza estimada, que recoge la dependencia de sus intervenciones. Cada modelo informará categorías de referencia, codificación de covariables y transformación utilizada para la longitud.

La unidad es la intervención y no cada etiqueta emitida por el LLM. La comparación se apoya en probabilidades predichas y contrastes entre leyes y grupos, con intervalos de incertidumbre y una misma distribución de covariables de ajuste cuando se estandaricen resultados. Las combinaciones sin observaciones se identificarán y no se interpretarán como comparaciones empíricas respaldadas por el corpus.

### 7.2 Diagnósticos e interpretación

Se examinarán cobertura de las celdas ley por grupo, variación de los resultados, convergencia, separación y varianza del efecto de actor. Si una categoría no permite estimar el modelo completo, se reportará su descripción y se documentará cualquier simplificación de la especificación. La comparación de varios conceptos conservará los tamaños de las diferencias y su incertidumbre; la interpretación conjunta no dependerá de seleccionar únicamente los resultados significativos.

Las nueve discusiones y las tres leyes delimitan el alcance del diseño. Las intervenciones repetidas no constituyen reformas independientes. El modelo estima asociaciones entre los proyectos observados, sin identificar un efecto general del carácter estructural de una reforma.

## 8. Persistencia y difusión

### 8.1 Persistencia en H3

Para los seis conceptos anteriores se compararán presencia, cobertura de apoyo, balance de posturas, fuerza y posición relativa en las tres ventanas de la reforma. Se conservarán las relaciones de reciprocidad, costos y justificaciones institucionales con propiedad y capitalización individual.

La continuidad de centralidad con rechazo sostenido se interpretará como persistencia del concepto en la controversia. La continuidad de apoyo informa sobre su aceptación. Las trayectorias pueden diferir entre componentes; se reportarán esas diferencias y sus argumentos, sin asignar un resultado único al conjunto por una suma arbitraria de indicadores.

La ausencia de significación estadística no demuestra estabilidad. La evaluación descriptiva informará magnitud y dirección de los cambios. Una prueba de equivalencia requeriría un margen sustantivo definido con anterioridad; las medidas descritas aquí no establecen ese margen ni constituyen por sí mismas una prueba de equivalencia.

### 8.2 Seguimiento de H4

La cohorte se define por la alineación con el repertorio de transformación en la primera ventana de la Cámara y se restringe a quienes también participan en la ventana final. Su composición inicial permanece fija. Los actores presentes solo en una ventana se describen en el alcance general, sin atribuirles una trayectoria individual observada.

Para cada concepto se distinguen: apoyo presente desde el inicio, aparición posterior de apoyo, cambio explícito de rechazo a apoyo y continuidad del rechazo. También se conserva la coexistencia de ambas posturas. La falta de expresión inicial no se transforma en rechazo. Se informarán el tamaño de la cohorte, sus oportunidades de intervención y la cobertura de cada concepto en los dos momentos.

La lectura de los pasajes establece si aparece una nueva justificación, si se reconoce una premisa antes cuestionada o si cambia la propuesta defendida. La nueva expresión de un concepto documenta un cambio en el repertorio observado; una interpretación de transmisión o cambio de creencia necesita evidencia adicional. Si los agrupamientos iniciales carecen de una correspondencia sustantiva con los perfiles teóricos, no se fuerza una cohorte reformista para contrastar la hipótesis.

## 9. Selección de pasajes e interpretación de la estructuración

La selección textual responde a resultados identificables: conceptos de alta centralidad, vínculos entre coaliciones, posiciones de intermediación y trayectorias de apoyo o rechazo. Incluye casos discrepantes y conserva los identificadores de actor, ley, fase, intervención y fragmento.

Cada lectura registra la proposición defendida, sus fundamentos, el arreglo distributivo que justifica y su relación con premisas de otros repertorios. El predominio requiere mostrar que esas premisas son reconocidas o condicionan propuestas rivales. La presencia de una palabra o la proximidad de dos conceptos en la red sirve para seleccionar evidencia; la interpretación descansa en el argumento completo.

Este procedimiento distingue conceptos centrales como objetos de controversia de principios aceptados como fundamentos de las propuestas. También examina si reciprocidad y restricciones de gasto sostienen la acumulación individual o arreglos colectivos, según sus relaciones con las demás justificaciones.

## 10. Registro reproducible

Las salidas del análisis conservarán:

- La versión del corpus, el libro, el prompt y las anotaciones adjudicadas, con sus identificadores y hashes.
- La tabla de grupos políticos, las ventanas temporales, las reglas de inclusión y los denominadores de cada comparación.
- Las matrices \(X^+\), \(X^-\), \(M\), \(G\), \(C\), \(S\), \(W^P\) y \(W^G\), con nodos identificados y la misma ordenación de conceptos.
- Las configuraciones y semillas de comunidades, las particiones obtenidas y sus diagnósticos de estabilidad.
- Las especificaciones de los modelos, muestras efectivas, diagnósticos, probabilidades y contrastes informados.
- Los pasajes seleccionados y las decisiones interpretativas que vinculan los patrones cuantitativos con los argumentos.

Las fuentes académicas citadas se encuentran en la bibliografía de la tesis. Las fórmulas de este suplemento explicitan las decisiones de este estudio sobre las relaciones descritas por el DNA; el registro de ejecución documentará su aplicación al corpus.
