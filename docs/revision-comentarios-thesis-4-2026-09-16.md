# Revisión de los comentarios de thesis-4(1).docx

La revisión utiliza la versión actual de `thesis.md` y los seis comentarios de Ismael Aguayo en `thesis-4(1).docx`. Se extrajeron las anotaciones de `word/comments.xml` y se vincularon con sus rangos en `word/document.xml`. El DOCX permanece intacto; la edición corresponde al Markdown. Se preservaron los cambios de redacción del autor y la ampliación de H1b a necesidad material y de H2 al repertorio asociado a la capitalización individual.

## Tratamiento de los comentarios

| ID | Solicitud | Resolución |
| --- | --- | --- |
| 0 | Dar prioridad a la detección de comunidades en la tabla de H1a. | Aplicada. La tabla comienza con detección de comunidades y el segundo paso describe el procedimiento. |
| 1 | Presentar el análisis de forma secuencial. | Aplicada. La sección 4.3.2 desarrolla siete pasos y cierra con la interpretación de la estructuración. |
| 2 | Limitar la unicidad a cada intervención; conservar nuevas participaciones del mismo actor. | Aplicada al conteo y a las matrices ponderadas. La presencia general cuenta una vez cada concepto por intervención; las posturas conservan una observación por intervención, concepto y orientación. Las intervenciones posteriores se acumulan. La cobertura de actores se conserva como proporción de personas por fase, sin eliminar intervenciones de la base. Una persona puede figurar en todas las fases en que participa. |
| 3 | Añadir necesidad como intermediación en la red de congruencia conceptual. | Aplicada. H1b distingue actores y conceptos, y la metodología examina necesidad material frente a los otros conceptos, sus conexiones con ambos repertorios y sus usos argumentales. |
| 4 | Reconocer centralidad incluso cuando un concepto recibe una connotación negativa. | Aplicada. La red de presencia conceptual reúne menciones de cualquier orientación. La red de congruencia conserva las posturas para estudiar intermediación. Centralidad, respaldo y predominio se interpretan separadamente. |
| 5 | Cuestionar la factibilidad y el aporte de H4 sobre difusión individual. | Pendiente de decisión. Se conserva la hipótesis y su contenido sustantivo, con redacción secuencial, mientras se decide si retirarla e incorporar el alcance entre coaliciones en H3. Se solicitó esa preferencia durante la revisión. |

## Decisiones y cambios pendientes

1. **Tratamiento de H4.** La alternativa recomendada es retirar la expectativa de adopción individual e incorporar a H3 la distribución del repertorio entre coaliciones en cada fase. Esto permite examinar alcance transversal sin exigir una conversión discursiva de los mismos actores. La posibilidad de que una hipótesis resulte refutada no es por sí sola motivo para retirarla; el problema relevante es su aporte y la capacidad de distinguir cambios de postura de cambios en las oportunidades de expresión. Si se adopta la alternativa, deben ajustarse de manera conjunta resumen, pregunta, referencias a difusión en la introducción y la sección 2.2, H4 y metodología. No se hizo esa sustitución sin resolver la decisión.
2. **Criterio de persistencia de H3.** Las medidas y fases están definidas, pero falta precisar qué magnitud de cambio permitiría sostener que se mantiene cobertura o centralidad, y cómo interpretar trayectorias divergentes de los seis componentes. Conviene resolver si se busca una prueba con un margen sustantivo de estabilidad previamente definido o una evaluación descriptiva de continuidad, pérdida y controversia. No se inventó un umbral ni un índice agregado.
3. **Clasificación política.** La comparación de centroizquierda con otros grupos requiere un listado explícito de partidos e independientes según la fecha de la intervención. La afiliación disponible aporta la base, pero la regla de agrupación analítica debe documentarse.
4. **Estructura del cierre del manuscrito.** La introducción asigna la sección 5 a resultados y vuelve a asignar la sección 5 a discusión. Corresponde decidir si se separarán resultados, discusión y limitaciones o se combinarán algunos de estos componentes antes de fijar la numeración. La Figura 1 conserva un título sin una figura asociada. Ambos puntos se mantienen fuera de la reescritura metodológica solicitada y requieren cierre editorial.

## Ajustes de coherencia realizados

Se añadieron los dos componentes de H1b a la tabla y a sus menciones en introducción y resumen. La nueva red de centralidad utiliza conceptos completos, sin fragmentarlos en nodos de apoyo y rechazo. Los modelos de H2 corresponden a sus dos resultados: presencia de los conceptos del repertorio de capitalización individual y apoyo a necesidad e igualdad/universalismo. La frase metodológica de la introducción refleja presencia y apoyo.

La normalización pasó de Jaccard sobre conjuntos binarios de actores a similitud coseno sobre perfiles con frecuencias de intervenciones. Esta elección conserva la reiteración entre intervenciones solicitada en el comentario 2. En la red de actores, se calcula congruencia entre orientaciones coincidentes y conflicto entre orientaciones opuestas, con el mismo denominador basado en las normas de los perfiles; la diferencia produce la red con signo. En la red de presencia conceptual se compara el perfil de frecuencias de cada concepto entre actores, sumando presencia de cualquier orientación una sola vez por intervención. En la red de congruencia conceptual se conservan las dimensiones de apoyo y rechazo por actor. Las redes describen proximidad entre repertorios; la relación argumental se comprueba en el texto. Estas son decisiones operativas del diseño, no resultados empíricos.

Se sustituyó el umbral numérico de confianza `<0.8` por confianza media o baja, en concordancia con las categorías `high`, `medium` y `low` y la remisión a revisión humana que establece `features/llm_annotations/pipeline.py`. Se corrigió «coidificará» y se retiró un encabezado vacío. No se modificaron el codebook, los QMD, el código de procesamiento ni `Tesis.bib`.

## Evidencia metodológica consultada

- `leifeld_discourse_2017`, adjunto Zotero `YZVLEP9H`, texto local `.zotero-ft-cache`: proyecciones de congruencia y conflicto, y sección «Normalization of Discourse Networks», pp. 12–14 del texto extraído. Sustenta la distinción entre coincidencias y oposiciones, las semejanzas normalizadas y la resta del conflicto a la congruencia. La aplicación de coseno a las frecuencias conservadas es la elección de esta revisión.
- Leifeld y Haunss (2012), adjunto `2A793MIA`, texto local `.zotero-ft-cache`, apartado de redes de congruencia conceptual: dos conceptos se conectan cuando un actor los usa con igual orientación. La anotación de su figura de afiliación suma declaraciones positivas y negativas en la centralidad. Esto respalda distinguir presencia y orientación.
- Schaub (2021), adjunto `E4K4X34B`, texto local `.zotero-ft-cache`: procedimiento de detección de comunidades mediante *spin-glass*, citado ya en el manuscrito. Se conserva el método y se destaca su función en H1a.

Los identificadores de adjuntos están registrados en el archivo actual `Tesis.bib`; sus textos se leyeron en `/home/ismael.aguayo/Zotero/storage/`. Las conclusiones de esta revisión se refieren al diseño y a la correspondencia entre comentarios y manuscrito, sin estimar resultados de las hipótesis.
