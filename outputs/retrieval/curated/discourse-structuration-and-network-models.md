# Estructuración discursiva y modelos longitudinales de redes

Fecha de búsqueda y verificación: 29 de julio de 2026

## Propósito

Identificar fuentes que permitan fundamentar un diseño que:

1. codifica declaraciones como relaciones firmadas entre actores y conceptos;
2. identifica coaliciones a partir de congruencia y conflicto discursivo;
3. distingue la centralidad de un concepto de la posición positiva o negativa de los actores frente a él;
4. analiza la permanencia, difusión y adaptación de un vocabulario asociado a la capitalización individual; y
5. combina el análisis de redes con modelos para las estrategias de legitimación.

## Hallazgo principal

No existe una escala cuantitativa estándar de «estructuración discursiva» derivada de Hajer. Las aplicaciones de análisis argumentativo del discurso suelen establecerla mediante una reconstrucción cualitativa y temporal de *storylines*, coaliciones y vocabularios dominantes. Preguntan si una representación del problema se vuelve tan aceptada que actores rivales deben formular sus argumentos dentro de ella para resultar creíbles. La institucionalización se examina después y por separado, observando su incorporación a reglas, decisiones y prácticas.

El análisis de redes discursivas (DNA) permite medir rastros observables compatibles con ese proceso: cuántos y qué tipos de actores emplean un concepto; cuán integrado está en un conjunto coherente de conceptos; si atraviesa partidos o coaliciones; si actores inicialmente adversarios comienzan a adoptarlo o adaptarlo; y cómo cambia esa estructura en el tiempo. Sin embargo, centralidad o frecuencia, por sí solas, no demuestran el criterio hajeriano de estructuración.

La consecuencia para H3 es que puede evaluarse cuantitativamente, pero no conviene reducirla a un único índice. La opción más defendible es una batería de indicadores para permanencia, difusión y adaptación, complementada con una comprobación cualitativa de que actores reformistas deben justificar sus propuestas utilizando el vocabulario del paradigma de capitalización individual.

## Cómo se ha operacionalizado la estructuración

| Enfoque | Evidencia utilizada | Qué cuenta como estructuración | Implicación para la tesis |
|---|---|---|---|
| Análisis argumentativo del discurso | Documentos, entrevistas, observación y reconstrucción temporal de *storylines* | Una representación domina la conceptualización del problema y los argumentos considerados legítimos | Mantener una validación cualitativa de episodios y declaraciones, además de las métricas de red |
| Hegemonía de una coalición discursiva | Estabilidad de actores y marcos, congruencia interna, separación respecto de rivales, prominencia e integración de marcos | Una coalición presenta un vocabulario más coherente e integrado y domina los argumentos centrales | Traducir coherencia, alcance e integración a indicadores de la red, sin tratarlos como prueba aislada |
| Difusión entre grupos | Cobertura de actores, diversidad organizacional o partidaria y adopción por antiguos adversarios | El vocabulario desborda su coalición de origen y estructura argumentos de actores heterogéneos | Medir adopción, diversidad y migración de actores, no sólo frecuencia agregada |
| Trayectorias de marcos | Ventanas temporales, proyecciones de redes, distancia entre estados y suavizamiento temporal | Un marco emerge, se estabiliza, se difunde, se adapta, domina o declina en una trayectoria observable | Modelar H3 por etapas legislativas y comprobar robustez con ventanas temporales solapadas o suavizadas |
| Institucionalización | Cambios en normas, políticas, organizaciones y prácticas oficiales | El discurso queda sedimentado en arreglos institucionales | No confundirla con H3 si la hipótesis se refiere sólo a estructuración discursiva |

### Precedentes directos

- Funke, Huitema y Petersen (2022), *Impending doom or unnecessary panic?*, es el antecedente más directo para explicar cómo se lleva a la práctica el criterio de Hajer. Separa explícitamente estructuración e institucionalización, reconstruye *storylines* mediante documentos y entrevistas y advierte que Hajer no entrega una pauta operacional única. DOI: [10.1080/19460171.2022.2092523](https://doi.org/10.1080/19460171.2022.2092523).

- Kreiken y Arts (2024), *Disruptive data*, vincula *storylines* con actores para identificar coaliciones y estructuración. Usa codificación abierta y axial, documentos, 28 entrevistas, observación de negociaciones y validación con participantes. Los cambios en documentos oficiales se reservan para la institucionalización. DOI: [10.1016/j.gloenvcha.2024.102892](https://doi.org/10.1016/j.gloenvcha.2024.102892).

- Kaufmann y Wiering (2021), *The role of discourses in understanding institutional stability and change*, reconstruye longitudinalmente cómo ciertos discursos se vuelven más centrales y aceptados y distingue ese proceso de su sedimentación institucional. DOI: [10.1080/1523908X.2021.1935222](https://doi.org/10.1080/1523908X.2021.1935222).

- Leifeld y Haunss (2012), *Political discourse networks and the conflict over software patents in Europe*, ofrece el puente más claro hacia una operacionalización reticular. Caracteriza una coalición hegemónica por su estabilidad, congruencia, separación de rivales, coherencia e integración de marcos y dominio de los argumentos centrales. DOI: [10.1111/j.1475-6765.2011.02003.x](https://doi.org/10.1111/j.1475-6765.2011.02003.x).

## Modelos y técnicas utilizados en redes discursivas

| Familia | Unidad y pregunta | Ventaja | Limitación | Uso recomendado aquí |
|---|---|---|---|---|
| Cortes temporales de DNA | Redes actor–concepto o sus proyecciones en etapas o ventanas | Transparente, compatible con las hipótesis y con el tamaño habitual de una tesis | La elección de cortes puede alterar resultados; es principalmente descriptiva | Modelo principal para coaliciones y las tres dimensiones de H3 |
| Comunidades en redes firmadas | Congruencia menos conflicto entre actores | Reconoce simultáneamente acuerdo y desacuerdo | Louvain o Leiden estándar no están diseñados para pesos negativos | Usar un método de modularidad firmada, como *signed spin-glass*, o justificar una proyección sólo positiva |
| Trayectorias temporales suavizadas | Secuencia de redes solapadas ponderadas por cercanía temporal | Reduce saltos artificiales entre ventanas e identifica estados y transiciones | Requiere decisiones sobre ancho de ventana, kernel, distancia y número de estados | Análisis de robustez muy pertinente para H3 |
| Modelo de eventos relacionales (REM) | Evento ordenado actor → concepto/creencia, con signo y tiempo | Modela directamente adopción, persistencia, popularidad, homofilia, acercamiento y repulsión | Necesita tiempos fiables, muchos eventos y mayor complejidad computacional | Extensión inferencial si se quiere explicar la difusión o adopción en H3 |
| Modelo dinámico actor–red (DyNAM) | Evento bipartito actor–afirmación | Separa la tasa de participación —quién habla y cuánto— de la elección de una afirmación | Es avanzado y la aplicación publicada trabaja principalmente con apoyos | Alternativa al REM si resulta sustantivamente importante separar actividad de elección conceptual |
| ERGM | Una red estática o agregada | Contrasta mecanismos estructurales en una red | Pierde el orden de las declaraciones y puede confundir repetición con persistencia de lazos | No sería la primera opción para este corpus de eventos |
| TERGM o SAOM | Panel de redes discretas | Modelan formación y persistencia de lazos entre olas | Exigen olas comparables y están pensados para lazos con cierta duración | Sólo si los datos se redefinen como paneles estables; menos natural que REM/DyNAM |
| Modelo multinomial mixto | Fragmento o justificación, no la red | Permite explicar la estrategia de legitimación y controlar heterogeneidad por actor y sesión | No explica por sí mismo la evolución de la red | Mantenerlo para H2 como análisis separado y posterior a la identificación de coaliciones |

### Precedentes directos para los modelos

- Schaub (2021), *Public contestation over agricultural pollution*, aplica un diseño en dos etapas especialmente cercano al propuesto: primero identifica coaliciones mediante una red firmada de acuerdo menos desacuerdo y comunidades *spin-glass*; después analiza las estrategias narrativas de las coaliciones. También compara periodos, actividad, modularidad, densidad, tendencias y redes de coocurrencia. DOI: [10.1007/s11077-021-09439-x](https://doi.org/10.1007/s11077-021-09439-x).

- Haunss y Hollway (2023), *Multimodal mechanisms of political discourse dynamics*, desarrollan un DyNAM bipartito. Separan el proceso de tasa —qué actor interviene— del proceso de elección —qué afirmación apoya— y modelan atributos de los actores y dependencias endógenas. DOI: [10.1017/nws.2022.31](https://doi.org/10.1017/nws.2022.31).

- Leifeld y Brandenberger, *Endogenous Coalition Formation in Policy Debates*, modelan eventos actor–creencia firmados para explicar adopción mediante vinculación interna, puente hacia nuevas creencias y repulsión entre coaliciones. Es el antecedente más próximo si se desea probar si actores inicialmente reformistas adoptan conceptos asociados a la preservación. Preprint: [arXiv:1904.05327](https://arxiv.org/abs/1904.05327).

- Leifeld y Garic (2026), *Measuring Frame Evolution*, representan declaraciones con actor, concepto, calificador y tiempo, construyen redes temporales suavizadas mediante kernels y agrupan sus estados para recuperar trayectorias y fases discursivas. Es el antecedente más directo para la dimensión temporal de H3. DOI: [10.1111/jcms.70119](https://doi.org/10.1111/jcms.70119).

- Leifeld y Wong (2026), *Fully Bayesian estimation of temporal decay in ordinal relational event models*, estiman en lugar de fijar la vida media con que los eventos previos influyen en declaraciones posteriores. La aplicación corresponde, además, al debate de pensiones alemán. Es metodológicamente valioso, pero excesivo como requisito principal para esta tesis. DOI: [10.1016/j.csda.2026.108428](https://doi.org/10.1016/j.csda.2026.108428).

- Atikcan, Holzscheiter, Morin y Henrichsen (2026), *Tracing Frame Trajectories in Policy Debates*, ordenan la evolución en procesos como emergencia, multiplicación, difusión, dominio, marginación, contestación, polarización y desaparición. La tipología ayuda a precisar qué significa «adaptación» sin convertirla en un cambio inespecífico. DOI: [10.1111/jcms.70134](https://doi.org/10.1111/jcms.70134).

## Propuesta metodológica derivada para H3

### 1. Permanencia

Medir por concepto y periodo:

- cobertura: número de actores únicos que emplean el concepto, dividido por los actores discursivamente activos;
- fuerza positiva y negativa: número o peso normalizado de declaraciones con cada posición;
- persistencia: proporción de periodos o ventanas en que conserva presencia por encima de un umbral predefinido;
- rango y fuerza del nodo conceptual en la red de congruencia de conceptos;
- estabilidad de su pertenencia al núcleo conceptual de una coalición.

La fuerza es preferible a la centralidad de autovector como indicador principal. El autovector puede servir como sensibilidad, porque vuelve difícil distinguir popularidad propia de popularidad heredada de conceptos vecinos.

### 2. Difusión

Definir antes del análisis qué combinaciones constituyen una orientación reformista y cuáles una orientación de preservación. Después medir:

- diversidad partidaria y organizacional de los actores que usan positivamente cada concepto, mediante entropía o número efectivo de grupos;
- proporción de actores reformistas iniciales que más tarde emplean positivamente conceptos del polo de preservación;
- tiempo hasta la primera adopción y continuidad posterior de esa adopción;
- cambios de pertenencia o acercamiento de actores entre coaliciones;
- presencia del vocabulario de preservación en declaraciones donde el actor mantiene una posición negativa frente a la capitalización individual.

El último indicador es particularmente cercano al criterio de Hajer: el actor puede rechazar el arreglo institucional y, al mismo tiempo, formular su alternativa dentro del vocabulario que ese arreglo volvió legítimo.

### 3. Adaptación

Tratarla como cambio en combinaciones conceptuales, no sólo como crecimiento del número de nodos:

- coocurrencia condicionada de capitalización individual negativa con solidaridad positiva y sostenibilidad financiera positiva;
- fuerza normalizada de pares o tríadas conceptuales dentro de actor, sesión o ventana temporal;
- diversidad o «polinomia» de conceptos asociados a una posición frente a CARIN;
- aparición de nuevos conceptos inductivos y su incorporación estable al mismo paquete argumental;
- trayectoria temporal del paquete de conceptos mediante ventanas solapadas o suavizadas.

Una opción inferencial sencilla consiste en modelar la probabilidad de una posición positiva ante un concepto condicionado por periodo, coalición y posición frente a CARIN, con interceptos aleatorios cruzados de actor y sesión. El REM debe reservarse para una pregunta distinta y más ambiciosa: qué mecanismos hacen que un actor adopte una creencia después de observar eventos discursivos previos.

### Comprobación cualitativa mínima

Seleccionar episodios o declaraciones de actores reformistas que:

1. mantengan una posición negativa frente a CARIN;
2. incorporen conceptos previamente ligados a la coalición de preservación; y
3. los usen como condiciones de credibilidad o viabilidad de su propia propuesta.

La inspección debe determinar si se trata de estructuración, apropiación estratégica, polisemia o simple coincidencia léxica. Esto evita inferir una relación teórica fuerte sólo desde la topología.

## Recomendación de diseño

1. Mantener la declaración unitaria como `(actor, concepto, posición, tiempo)` y permitir varios fragmentos monofunción dentro de una intervención, sin multietiqueta de estrategia dentro de un mismo fragmento.
2. Construir la red bipartita firmada con CARIN y las categorías nacionales como nodos conceptuales.
3. Identificar dos coaliciones con una técnica compatible con redes firmadas. Si se utiliza Leiden, trabajar con una proyección no negativa o una formulación de modularidad firmada explícita.
4. Evaluar H3 mediante indicadores desglosados de permanencia, difusión y adaptación por etapas legislativas.
5. Añadir ventanas temporales solapadas o suavizadas como robustez frente a la elección de periodos.
6. Mantener el modelo multinomial mixto para estrategias como análisis posterior, con actor y sesión como interceptos aleatorios cruzados.
7. Incorporar REM o DyNAM sólo si se decide que H3 debe explicar mecanismos secuenciales de adopción y los registros poseen tiempo y orden suficientemente precisos.

## Clasificación de fuentes

### Core: incorporar al corpus

- Funke, Huitema y Petersen (2022): operacionalización directa de estructuración e institucionalización.
- Kreiken y Arts (2024): aplicación longitudinal, triangulación y validación de actores.
- Leifeld y Haunss (2012): medición de propiedades de una coalición discursiva hegemónica.
- Schaub (2021): separación entre formación de coaliciones y estrategias, con red firmada.
- Haunss y Hollway (2023): DyNAM para dinámica de discursos bipartitos.
- Leifeld y Brandenberger (preprint actualizado): REM firmado de adopción de creencias y formación de coaliciones.
- Leifeld y Garic (2026): trayectorias temporales suavizadas.
- Atikcan et al. (2026): tipología de trayectorias de marcos.

### Peripheral: útil como extensión o robustez

- Kaufmann y Wiering (2021): evidencia cualitativa longitudinal de estabilidad y cambio.
- Leifeld y Wong (2026): estimación bayesiana del decaimiento temporal en REM.
- Rinscheid et al. (2020), *Why do junctures become critical?*: cambios conjuntos de creencias comparados después de Fukushima. DOI: [10.1111/rego.12238](https://doi.org/10.1111/rego.12238).
- Fisher, Leifeld e Iwaki (2013), *Mapping the Ideological Networks of American Climate Politics*: matriz actor–posición, congruencia, densidad y agrupación jerárquica.

### Ya presentes en `references.bib`

- Hajer (1997), *The Politics of Environmental Discourse*.
- Leifeld (2013), *Reconceptualizing Major Policy Change in the Advocacy Coalition Framework*; aparece duplicado bajo dos claves BibTeX.
- Leifeld (2017), *Discourse Network Analysis: Policy Debates as Dynamic Networks*.
- Leifeld (2020), *Policy Debates and Discourse Network Analysis: A Research Agenda*.
- Lusher, Koskinen y Robins (2013), *Exponential Random Graph Models for Social Networks*.

No se encontraron coincidencias por título o DOI en `references.bib` para las fuentes clasificadas como Core.

### Excluidas o no priorizadas

- Resultados generales sobre ERGM/TERGM en comercio, transporte, salud o emisiones: emplean modelos de red pertinentes en abstracto, pero no representan declaraciones discursivas ni adopción de conceptos.
- Resultados de Semantic Scholar que confundieron a Maarten Hajer con autores homónimos: falsa coincidencia.
- *Tracing the Sources of Belief Contestation in Policy Debates*: presentación o manuscrito sin publicación revisada por pares verificada; no debe sostener una decisión central mientras no se confirme su estado.

## Actualización del ledger de búsqueda

Promovidos a términos activos:

- `discourse structuration`
- `discourse institutionalization`
- `signed discourse network`
- `frame trajectory`
- `relational event model`
- `dynamic network actor model`

Términos útiles para búsquedas futuras, todavía candidatos:

- `signed modularity`
- `kernel-smoothed network`
- `belief adoption`
- `storyline dominance`
- `frame co-optation`

Se descartaron durante la curación los términos genéricos recuperados automáticamente —por ejemplo, `network`, `temporal`, `structure`, `models` y `framework` sin calificadores— porque degradaron mucho la precisión.

## Trazabilidad

Resultados brutos y metadatos:

- `outputs/retrieval/intermediate/2026-07-29-133111-2026-07-29-discourse-structuration-network-models-openalex.md`
- `outputs/retrieval/intermediate/2026-07-29-133154-2026-07-29-longitudinal-discourse-network-models-semantic.md`
- `outputs/retrieval/intermediate/2026-07-29-133247-2026-07-29-key-method-papers-openalex.md`
- `outputs/retrieval/intermediate/2026-07-29-133341-2026-07-29-hajer-structuration-applications-openalex.md`

La selección final se verificó mediante DOI, páginas editoriales, repositorios institucionales y textos completos cuando estaban disponibles. Las puntuaciones automáticas de recuperación se usaron sólo para descubrimiento; la clasificación Core/Peripheral/Excluded corresponde a evaluación sustantiva.
