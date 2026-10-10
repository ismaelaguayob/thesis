# Decisiones sobre la validación de las anotaciones LLM

Registro de las decisiones sobre métricas, selección de modelo y reporte de la
validación (`validation.qmd`), tomadas después de completar los censos de
Luna-6 y Haiku 5.5. Restricciones de partida (9 oct 2026): no se modifica el
libro de códigos ni se ejecuta otra iteración de anotación, por tiempo y costo.
La metodología del material suplementario puede ajustarse, porque no contempla
el uso ni la comparación de más de un modelo.

Estado: **decidido**, **en discusión**, **registrado** (pendiente de ejecución) o **ejecutado**.

## 1. Procedimiento de cálculo de métricas — decidido

### Comparación con la literatura

Los resultados son comparables con los de los dos estudios de referencia, de modo
que no hay indicios de un error de cálculo.

| | Unidad y tarea | Métrica principal | Resultado |
|---|---|---|---|
| Dunivin (2025) | 111 pasajes, 9 códigos, un prompt por código; libro ajustado sobre el mismo conjunto | κ de Cohen | GPT-4: media 0,68 (0,30–1,00); humano–humano 0,78 |
| Bosley (2025) | 119 discursos, 7 dimensiones ordinales del DQI, 50 ejemplos en el prompt | α ordinal | Media 0,65 (0,27–1,00) |
| Este estudio | 352 bloques no vistos, 16 conceptos en un solo prompt, sin ejemplos | α nominal | Agregado 0,68 (Luna) y 0,69 (Haiku); media por concepto 0,67 y 0,67 (0,44–0,90) |

Las condiciones de Dunivin favorecen valores altos: evalúa sobre el mismo
conjunto con el que ajustó el libro (lo reconoce como riesgo de sobreajuste) y
presenta un código por prompt. Además dispone de una línea de base humano–humano
(0,78), que aquí no existe porque hay una sola persona codificadora.

### Decidido

- **Krippendorff (nominal) es el coeficiente de concordancia principal.** Coincide
  con Cohen en todos los casos (diferencias ≤ 0,002), admite tres codificadores y
  es el coeficiente que usa Bosley. Cohen, Fleiss y el AC1 de Gwet pasan al
  material suplementario como análisis de sensibilidad.
- **Las métricas son sin ponderar, sin versión ponderada.** La confiabilidad se
  calcula sobre la muestra codificada, como en Dunivin y Bosley, y la muestra se
  diseñó para reunir casos suficientes de cada concepto; ponderar amplificaría
  problemas propios de pocos bloques con pesos altos. No se reportan métricas
  ponderadas ni en el material suplementario, por consistencia con esta decisión.

- **Sin % de coincidencia en el texto principal.** Precisión, sensibilidad y F1
  ya describen cuánto de lo que asigna el modelo es correcto, cuánto de la
  referencia recupera y el equilibrio entre ambas. La coincidencia total sobre
  bloque × concepto (0,95 en ambos modelos) se compara mal con un codificador que
  no asigna nada (0,92) y no agrega información. F1 se presenta como acuerdo
  específico positivo, 2a/(2a + b + c), con el que es matemáticamente idéntico.
  Las variantes de coincidencia (total, con postura, solo donde algún codificador
  asignó el concepto y bloques con el mismo conjunto) quedan, a lo sumo, en el
  material suplementario.
- **La asimetría entre ausencias y presencias es un hallazgo que se destaca.** El
  acuerdo específico negativo es 0,97 y el positivo (F1) 0,71: los modelos casi no
  atribuyen conceptos donde la referencia no ve ninguno, pero coinciden menos sobre
  cuál concepto corresponde cuando hay una justificación normativa, o la pasan por
  alto. El texto principal lo resume en una frase con ambos valores. El AC1 de
  Gwet (0,94), en el suplemento, se lee como expresión de esa asimetría: su
  corrección por azar supone poco acuerdo esperado cuando un concepto es raro (cada
  concepto aparece en el 8 % de los bloques), de modo que queda cerca de la
  coincidencia observada. No indica un desempeño superior al de Dunivin, cuyo κ
  medio es igual (0,68) con códigos más frecuentes.

### Métricas que se reportan (decidido)

- **Texto principal: α de Krippendorff y F1.** F0,5 deja de reportarse, también en
  el material suplementario: es una métrica de nicho y su argumento (un concepto
  atribuido de más crea vínculos inexistentes en la red) pierde peso porque los
  modelos casi no atribuyen conceptos donde no hay ninguno. La sección 3.1 del
  material suplementario, que fija un umbral de F0,5, debe actualizarse.
- **Precisión, sensibilidad y análisis por grupo pasan al material
  suplementario.** Los análisis por ley, género y alineación política usan solo
  las métricas principales (α y F1). El texto principal nombra, con sus cifras, los
  dos patrones de error que solo se ven con precisión y sensibilidad: necesidad
  material se atribuye de más (baja precisión) y solidaridad como deber colectivo
  se omite (baja sensibilidad, sobre todo en Luna). También resume en una frase la
  conclusión por grupo político, porque omisiones no aleatorias por grupo
  sesgarían la red. Ambos remiten al suplemento, donde los análisis por grupo se
  presentan en gráficos (decidido: suplemento más una frase en el texto
  principal).
- **Material suplementario: una tabla por concepto** con precisión,
  sensibilidad, AC1 de Gwet y kappa de Cohen (pares) o de Fleiss (tres
  codificadores).

## 2. Filtrado y decisión de modelo — decidido

### Decidido

- **La codificación humana es una referencia humana ciega, no un *gold
  standard*.** La realizó una sola persona durante el pilotaje del instrumento
  (libro y prompt). En consecuencia, precisión, sensibilidad y F1 se leen como
  acuerdo con la referencia y no como exactitud: parte de los desacuerdos pueden
  ser errores de la referencia.
- **Concordancia por pares en el texto principal; los tres codificadores en el
  suplemento.**
  - Humano–Luna y humano–Haiku: concordancia entre una persona y el instrumento
    aplicado por cada modelo.
  - Luna–Haiku: estabilidad del instrumento entre modelos (α 0,82 en la tarea de
    concepto).
  - El α y el kappa de Fleiss de los tres juntos (0,73) van al suplemento. Indican
    un acuerdo general bueno, pero los modelos no son codificadores
    independientes (comparten prompt y libro y concuerdan más entre sí que con la
    referencia), por lo que su acuerdo mutuo eleva el valor conjunto.
- **Se declara la limitación de contar con una sola persona codificadora.** No hay
  una línea de base humano–humano comparable a la de Dunivin (0,78), de modo que
  no se puede separar cuánto del desacuerdo humano–modelo proviene de la
  ambigüedad del libro.

- **Un modelo principal para todo el corpus; el otro reproduce los análisis más
  importantes en el material suplementario.** No se elige modelo por concepto: en
  12 de 15 conceptos la diferencia de α entre Luna y Haiku está dentro del ruido
  (remuestreo de bloques, 2.000 réplicas), y elegir el mayor sobreestimaría el
  desempeño porque se usaría la misma muestra para elegir y para reportar. Solo
  tres conceptos difieren con claridad: igualdad y universalismo (Haiku +0,16),
  necesidad material (Luna +0,11) y conciencia de costos (Luna +0,12, en el
  límite). Qué modelo es el principal se decide aparte; en el agregado empatan
  (α medio por concepto 0,665 y 0,673).

- **Luna-6 es el modelo principal; Haiku 5.5 reproduce los análisis más
  importantes en el material suplementario.** En el agregado no difieren (α
  0,683 y 0,693; diferencia +0,010, IC 95 % −0,018 a 0,038). Luna es mejor en
  necesidad material (+0,11), el concepto central de H1b; además, la muestra de
  validación se estratificó con sus predicciones y fue el modelo de los pilotos.
  Haiku es mejor en igualdad y universalismo (+0,16), que se muestra en la
  reproducción.
- **Regla de inclusión de conceptos: se excluye un concepto solo si todo su
  intervalo de confianza de α (remuestreo de bloques, 95 %) queda bajo 0,667.**
  Con Luna se excluyen identidad y control y responsabilidad individual (ambos con
  IC hasta 0,66 en `validation.qmd`), que no sostienen hipótesis. Control es un
  caso fronterizo: en un remuestreo exploratorio previo su límite superior fue
  0,67, así que su resultado depende del ruido del remuestreo; se adopta el del
  reporte, que es reproducible con semilla fija. La regla es indulgente con los
  conceptos con pocos casos, porque tienen intervalos más anchos, y así se
  declara.
- **Las convenciones de Krippendorff (0,80 y 0,667) orientan la interpretación,
  pero no son una regla vinculante.** La cautela se acentúa en los conceptos con
  pocos casos y α bajo (por ejemplo, control y responsabilidad individual, n = 14,
  α 0,44). Necesidad material, uno de los conceptos más frecuentes (n = 47) y
  cercano al umbral (α 0,66), sostiene las afirmaciones de H1b.
- **Sin diagnóstico sistemático de errores.** Por tiempo, no se clasifican todos
  los desacuerdos. En los conceptos críticos (necesidad material, igualdad y
  universalismo, conciencia de costos, solidaridad intergeneracional y solidaridad
  como deber colectivo) se muestran ejemplos que distinguen errores de frontera
  (el concepto se menciona sin justificar un arreglo institucional) de
  codificaciones equivocadas. Son ejemplos ilustrativos, no una estimación de la
  frecuencia de cada tipo de error.

## 3. Cambios en el reporte — ejecutado

- **Decidido: los 7 bloques codificados como votación o procedimiento entran en
  todas las métricas de validación (359 bloques).** En los 7, la referencia y
  ambos modelos coinciden en que no hay conceptos (Luna también los marca como
  votación o procedimiento); son acuerdos genuinos y el α cambia en +0,001. El
  bloque irresoluble queda fuera como dato faltante, porque no tiene decisión
  humana. La sección 2.2 del material suplementario debe precisar que estos
  bloques entran en la validación, pero siguen fuera de los denominadores de
  presencia del análisis.
- **Decidido: el bloque irresoluble (`utt_64ff6ddecbcb4b9266c9::p0001`) se
  mantiene como tal.** Es una intervención de 16 palabras cortada por una
  interrupción, marcada como `too_short` y `segmentation_problem`. El contexto
  anterior permitía leerla como libertad de elección, como hicieron ambos modelos,
  pero recodificarla después de ver sus salidas rompería la ceguera de la
  referencia. El efecto es nulo (α global de Luna 0,684 fuera y 0,685
  recodificado).
- Mostrar los análisis por ley, género y alineación política en gráficos (por
  ejemplo, de líneas o de puntos con errores estándar), probando varias formas. La
  comparación es dentro de cada modelo entre grupos, no entre modelos, y los
  gráficos deben destacarlo.
