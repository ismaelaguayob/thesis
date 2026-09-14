# Revisión de la tesis y factibilidad del análisis

> Registro histórico de la primera revisión, realizada con el DOCX sin comentarios. Para las decisiones vigentes, véase [Comentarios del DOCX y decisiones sobre el diseño](comentarios-docx-y-discusion-diseno.md). El autor indicó trabajar el manuscrito como texto final, mantener la formulación breve de variables y excluir de esta discusión el avance de validación y los plazos.

Revisión del 14 de septiembre de 2026. Se contrastaron `thesis.md`, `thesis 2.docx`, los dos QMD, el libro de códigos vigente, los Parquet del corpus, las sesiones manuales y los resultados guardados del piloto. Las propuestas de cambio del diseño que siguen quedan para discusión; las hipótesis del manuscrito conservan su formulación anterior.

## Correcciones aplicadas y comentarios pendientes

El DOCX entregado contiene cero comentarios de Word, cero anclas de comentarios y cero inserciones o eliminaciones con control de cambios. Su paquete tampoco contiene `word/comments.xml`. El cotejo del texto recuperado con el Markdown no permitió identificar observaciones de revisión incorporadas como párrafos. Por tanto, ninguna corrección se atribuye a comentarios del profesor. Para resolverlos hace falta acceder a la versión que los conserve.

Se aplicaron correcciones verificables en `thesis.md`:

- Se reemplazaron las 1.223 intervenciones del resumen por 1.096 intervenciones elegibles y 3.609 fragmentos, consistentes con los Parquet y la tabla 1.
- Se corrigieron la repetición «su su», «coidificará», una enumeración gramatical y un punto faltante.
- Se igualó el título de la sección 2.1 en el índice con el del cuerpo, se sustituyó el enlace residual de Google Docs a 4.3.2 y se eliminó un encabezado vacío.
- Se identificó el libro vigente, su enlace y sus 14 conceptos. El archivo se llama `codebook_v0.3.xlsx`, pero su versión interna es `0.4.0-pilot`.
- Se precisó que apoyo y rechazo se refieren a la proposición ancla de cada código. Se explicitó el sentido de conciencia de costos y se distinguió rechazo de ausencia de declaración.
- Se aclaró que la edad requiere cálculo y que el partido disponible es `current_party`, pendiente de comprobación histórica.
- Se retiró el umbral de confianza `<0.8`, que no corresponde a los campos disponibles. El piloto histórico carece de confianza numérica; el prompt en desarrollo propone niveles ordinales.
- Se distinguieron las pruebas de desarrollo de la evaluación independiente pendiente. Esta evaluación se ubicó antes del procesamiento completo, en coherencia con el criterio de escalamiento del propio manuscrito. Se explicitó *recall* entre las métricas previstas.

Las referencias bibliográficas y las formulaciones H1, Q2 y H3a–H3c permanecen intactas. El rótulo de Figura 1 sigue sin una figura en el Markdown: conviene resolverlo al cerrar el diseño, para que el diagrama represente la estrategia acordada. Los números de página del índice también deberán regenerarse al producir la versión final.

## Qué está disponible

Los conteos se recalcularon leyendo `data/proc_data/ley_*/coding_chunks_long.parquet`. Se contaron intervenciones únicas por `utterance_id` y documentos por `document_uri`.

| Ley | Discusiones | Intervenciones elegibles | Fragmentos |
|---|---:|---:|---:|
| 21.419 | 3 | 262 | 844 |
| 21.538 | 2 | 111 | 326 |
| 21.735 | 4 | 723 | 2.439 |
| Total | 9 | 1.096 | 3.609 |

Estos son tamaños del corpus de entrada. Incluyen participaciones procedimentales y votaciones que pueden resultar sin declaraciones codificables. El tamaño de la base sustantiva todavía está por establecer.

`proc.qmd` implementa extracción, normalización, identificación y segmentación, una ley por ejecución. La segmentación vigente es `coding-chunks-2.0.0`; los fragmentos observados tienen entre 5 y 194 palabras. La fusión final de fragmentos breves explica que se supere el objetivo inicial de 150. La metodología y su nota al pie ya describían correctamente esta regla.

`annotations.qmd` selecciona el 10% de las intervenciones por ley y sesión y procesa todos sus fragmentos. La selección por longitud es deliberadamente desproporcional. El reporte actual reutiliza el piloto guardado y mantiene las llamadas a la API desactivadas. Sus frecuencias describen las salidas del piloto; para estimar prevalencias del corpus habría que considerar el diseño de selección y la cobertura incompleta.

La app de validación contiene cinco sesiones completadas de calibración: 10, 40, 15, 20 y 20 unidades. Utilizan distintas versiones del instrumento y distintas unidades textuales. Su existencia acredita trabajo manual previo, pero no permite sumarlas como una única muestra independiente de evaluación del piloto actual.

El manifiesto `data/proc_data/llm_pilots/pilot_f3a69c2f81c587271ef5/manifest.json`, contrastado con los artefactos guardados, registra:

| Indicador | Resultado |
|---|---:|
| Intervenciones seleccionadas | 110 |
| Fragmentos enviados | 418 |
| Salidas estructuralmente válidas | 306, equivalentes a 73,2% |
| Salidas incompletas por límite de tokens | 109 |
| Salidas rechazadas por controles locales | 3 |
| Intervenciones con todos sus fragmentos válidos | 65 |
| Anotaciones producidas | 206 |
| Anotaciones de códigos vigentes | 178 |
| Propuestas de códigos para revisión | 28 |

Las métricas de precisión, sensibilidad, F1 y acuerdo independiente todavía no están disponibles. El generador de `features/discourse_network/` produce una red sintética para ilustración; no constituye un análisis empírico del corpus. Tampoco se encontró una base implementada de estrategias de legitimación en el flujo de anotación vigente.

## Desajustes entre hipótesis e instrumento

**Solidaridad.** El manuscrito formula expectativas sobre solidaridad en sentido amplio. El código vigente registra exclusivamente solidaridad intergeneracional y excluye transferencias dentro de una misma generación y menciones genéricas a fondos comunes. H3c incluye solidaridad focalizada y contributiva sin asegurar que corresponda a esa definición. Hay que optar entre acotar la expectativa o ampliar y volver a validar la medición. Cambiar únicamente el nombre del código dejaría el problema intacto.

**Sostenibilidad.** `conciencia_costos` es una proposición de restricción: apoyo significa afirmar que una expansión es demasiado costosa o insostenible. Rechazo puede significar defender la sostenibilidad de una reforma. Por eso, sumar sus apoyos a un repertorio favorable a la capitalización necesita examinar qué propuesta se limita y con qué justificación. Su postura positiva no equivale automáticamente a preservación.

**Necesidad y reciprocidad.** La necesidad puede justificar focalización compatible con cuentas individuales; la reciprocidad puede respaldar beneficios de un seguro social por años cotizados. La asignación de estos códigos a polos exclusivos debe ser una expectativa contrastable y admitir combinaciones que la contradigan.

**Categorías poco observadas.** El piloto produjo cero anotaciones de solidaridad intergeneracional y actitud, una de control y cuatro de reciprocidad. Estos conteos proceden de salidas incompletas y sin validación independiente: no prueban ausencia sustantiva. Sí obligan a revisar omisiones y fronteras antes de hacer depender H1 y H3 de esos códigos. Igualdad/universalismo y acuerdos/moderación tienen 33 y 34 anotaciones respectivamente, por lo que el instrumento también puede revelar ejes distintos de los previstos.

**Legitimación.** La sección de variables propone segmentos con varias estrategias; el modelo de Q2 requiere una estrategia principal por declaración. Falta especificar la relación entre esas unidades, implementar la tarea y validar la jerarquía principal/secundaria. A ello se añade la estimación de un multinomial con efectos de actor y sesión. Es una segunda línea de medición y análisis con una carga considerable.

## Qué comparación temporal permiten los datos

| Fecha en la Ley 21.735 | Cámara | Intervenciones elegibles | Fragmentos |
|---|---|---:|---:|
| 23-01-2024 | Diputadas y Diputados | 62 | 304 |
| 24-01-2024 | Diputadas y Diputados | 258 | 625 |
| 27-01-2025 | Senado | 209 | 788 |
| 29-01-2025 | Diputadas y Diputados | 194 | 722 |

La tramitación se denomina 2022–2025, pero el corpus en Sala del caso principal observa enero de 2024 y enero de 2025. Las leyes PGU aportan otros episodios; su incorporación no convierte este corpus en seguimiento continuo de una misma reforma desde 2022.

Al unir las dos discusiones de la Cámara de 2024 se identifican 109 personas con `speaker_bcn_id`; 94 también aparecen en la Cámara del 29 de enero de 2025. El cálculo excluye identificadores ausentes. Incluye cualquier intervención elegible, de modo que la cohorte con declaraciones normativas comparables será igual o menor. Los actores externos sin identificador BCN requieren una correspondencia separada.

Esta continuidad ofrece una comparación descriptiva dentro de la misma cámara. Comparar directamente la Cámara de 2024 con el Senado de 2025 confunde cambios temporales con composición institucional. Además, empezar a observar un concepto en un actor no permite saber por sí solo si lo adoptó entonces o si antes no tuvo ocasión de expresarlo.

## Propuesta de alcance para conversar

La opción más viable con lo implementado es concentrar la tesis en las coaliciones y los repertorios justificativos de la Ley 21.735, mantener la PGU como comparación secundaria y tratar la robustez ideacional como una interpretación a evaluar con evidencia acotada.

| Componente actual | Propuesta | Producto concreto |
|---|---|---|
| H1: dos polos e intermediación de centroizquierda | Conservar la expectativa de polarización; separar la intermediación como pregunta exploratoria | Matriz actor–concepto–postura, red y caracterización de agrupamientos |
| Q2: coalición y estrategias de legitimación | Retirar el multinomial del alcance mínimo; estudiar recursos de legitimación en una selección cualitativa si el tiempo lo permite | Análisis de pasajes contrastantes, sin estimación de prevalencias poblacionales |
| H3a: permanencia | Comparar cobertura y orientación de conceptos entre las dos ventanas de la Cámara | Tabla temporal con denominadores explícitos y lectura de pasajes |
| H3b: difusión | Reformular provisionalmente como cambios y alcance transversal del repertorio | Seguimiento de los actores con declaraciones codificadas en ambas ventanas |
| H3c: adaptación | Examinar cualitativamente combinaciones justificativas y condiciones expresas | Casos de condicionamiento, articulaciones alternativas y evidencia contraria |

Una pregunta central de trabajo sería: **¿Cómo se organizan las coaliciones discursivas y qué continuidades y cambios presentan sus justificaciones de la capitalización individual y la protección colectiva en los debates en Sala de la reforma previsional?** Esta formulación es una propuesta para discutir, no un reemplazo ya aplicado al manuscrito.

La expectativa de dos polos puede conservarse sin imponer dos grupos al algoritmo. Primero hay que construir las posiciones observadas, distinguir ausencia de postura y oposición, y comprobar si los agrupamientos dependen de pocas declaraciones o de actores particularmente activos. Las interpretaciones requieren volver a los pasajes originales.

La intermediación necesita una definición adicional: compartir argumentos de varios grupos, ocupar una posición estructural entre ellos y mediar políticamente son fenómenos distintos. La implementación estándar de *betweenness* ponderada de igraph exige pesos positivos interpretados como distancias; los pesos negativos de una red de conflicto requieren otro tratamiento explícito. La detección de comunidades con *spin-glass* admite pesos negativos mediante su implementación correspondiente. Estas restricciones se comprobaron en la documentación oficial de [betweenness](https://r.igraph.org/reference/betweenness.html) y [spin-glass](https://igraph.org/r/doc/cluster_spinglass.html). La elección final de representación sigue pendiente.

Con cuatro discusiones en el caso principal y una variable dependiente todavía sin medir, el multinomial cruzado resulta una apuesta costosa para el alcance mínimo. La recomendación de postergarlo se basa en ese estado del proyecto; no supone que todo modelo con pocas sesiones sea imposible.

## Orden de trabajo y tiempo por estimar

1. Acordar la correspondencia entre solidaridad, costos, reciprocidad y las expectativas teóricas. Congelar una versión del libro para evaluación.
2. Separar los casos usados para calibración de una muestra independiente. Incluir bloques sin declaraciones y categorías potencialmente omitidas. Medir por separado detección, concepto y postura; definir cómo se alinearán las anotaciones humanas y automáticas.
3. Resolver los fallos de salida en una prueba pequeña y medir el tiempo real de revisión humana. La confianza declarada por el modelo puede orientar la revisión, pero su relación con los aciertos debe comprobarse.
4. Completar la codificación del caso principal, conservando fallos como pendientes y adjudicando las ambigüedades que afecten las posiciones de la red.
5. Construir descriptivos y red empírica. Seleccionar pasajes que representen acuerdos, conflictos y excepciones a H1.
6. Evaluar la comparación temporal con la cohorte que efectivamente tenga declaraciones en ambas ventanas. Incorporar PGU y legitimación según el tiempo restante y su aporte al argumento.

La fecha límite y la dedicación semanal todavía no están informadas. Por eso no se fija un calendario ni se promete una duración. Una cuenta orientativa para la revisión manual es `fragmentos × proporción a revisar × minutos por fragmento / 60`, a la que deben sumarse calibración, adjudicación, análisis y escritura. Como ejemplo aritmético, revisar el 30% de los 2.439 fragmentos del caso principal a tres minutos por fragmento exigiría 36,6 horas. Esos porcentajes y tiempos son supuestos ilustrativos, no estimaciones del desempeño observado.

Si el tiempo disponible no alcanza para completar el corpus, la alternativa es acordar una muestra de intervenciones completas por sesión con criterios explícitos y limitar a ella las conclusiones. Seleccionar solamente pasajes favorables a las hipótesis no resolvería la factibilidad de forma defendible.

## Verificación y límites de esta revisión

Se recalcularon tamaños, fechas, longitudes y solapamiento de identificadores leyendo archivos locales; se inspeccionaron las definiciones y el contrato de anotación y se compararon las correcciones con el texto anterior. No se ejecutaron nuevas anotaciones ni se modificaron el corpus, el libro de códigos, los QMD o las referencias. Los textos de planificación anteriores del repositorio se usaron para identificar decisiones pendientes, sin tratarlos como evidencia de procedimientos ya realizados. Esta revisión no constituye una auditoría bibliográfica exhaustiva del marco teórico.
