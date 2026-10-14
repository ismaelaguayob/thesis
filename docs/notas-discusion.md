# Notas para la discusión

Ideas que pertenecen a la discusión y no a resultados. Se agregan a medida que
aparecen.

## Validación de la codificación asistida por LLM

- **Comparación con la literatura.** La concordancia con la referencia (α 0,68
  con Luna y 0,69 con Haiku; media por concepto 0,67) es del mismo orden que la
  de estudios comparables: κ medio de 0,68 con GPT-4 en Dunivin (2025) y α
  ordinal medio de 0,65 en Bosley (2025).
- **Las condiciones de esos estudios favorecen valores altos.** Dunivin ajustó el
  libro sobre el mismo conjunto con que evaluó (reconoce el riesgo de
  sobreajuste) y presentó un código por prompt. Bosley usó 50 ejemplos en el
  prompt. Esta validación usa fragmentos nunca vistos durante el desarrollo del
  instrumento, un solo prompt con 16 conceptos y ningún ejemplo.
- **Contexto distinto.** La validación es en español, sobre debates
  legislativos chilenos en un sistema multipartidista. Los estudios de referencia
  trabajan en inglés (Dunivin con prensa estadounidense; Bosley con el Congreso
  de Estados Unidos, bipartidista).
- **Sin línea de base humana.** Dunivin compara con la concordancia entre sus
  dos codificadores (0,78); aquí hay una sola persona codificadora, así que no se
  sabe cuánto del desacuerdo humano–modelo proviene de la ambigüedad del propio
  libro.
- **El acuerdo entre modelos no prueba validez.** Luna y Haiku concuerdan más
  entre sí (0,82) que con la referencia: indica estabilidad del instrumento,
  pero los modelos comparten prompt y libro, y pueden compartir errores.
- **Asimetría.** Acuerdo casi perfecto en las ausencias (0,97) y moderado en las
  presencias (0,71). Hill et al. (2026) encuentran el mismo patrón con
  prevalencias similares (κ 0,34 y AC1 0,92 con 7,8 % de prevalencia). El riesgo
  para la red no es que el modelo invente justificaciones donde no hay nada, sino
  la confusión entre conceptos y la frontera entre descripción y justificación
  normativa.
- **Contextos fuera del Norte Global y no anglófonos.** Otros estudios han
  registrado sesgos en la codificación con LLM fuera de los contextos en que
  suelen evaluarse. Ashwin et al. (2025), con entrevistas a refugiados rohinyás y
  comunidades de acogida en Bangladés, encuentran que los errores de los modelos
  no son aleatorios respecto de las características de las personas
  entrevistadas. Este estudio examina esa posibilidad (concordancia por ley,
  género y alineación política) y no encuentra que los errores se concentren en un
  grupo. Para el término: «contextos no WEIRD» (Henrich et al., 2010; no está en el `.bib`) es preciso,
  pero quizás demasiado técnico; «fuera del Norte Global y del mundo anglófono»
  puede leerse mejor. Pendiente: buscar referencias sobre el desempeño de los LLM
  en español o en otras lenguas distintas del inglés; en el `.bib` solo está
  Ashwin et al.
- **El LLM como segundo codificador que revela puntos ciegos.** Más allá del
  grado de acuerdo, los desacuerdos mostraron problemas del instrumento y de la
  propia referencia: en necesidad material, la referencia fue a veces demasiado
  estricta (por ejemplo, una extensión de la PGU justificada por los «gastos
  mayores» de las personas con discapacidad); en solidaridad, la referencia
  codificó la palabra aunque designara un mecanismo, mientras el modelo codificó
  la idea de un deber compartido aunque no se nombrara («ráscate con tus propias
  uñas»). En igualdad y en necesidad material, en cambio, el modelo tomó
  descripciones de políticas o diagnósticos por justificaciones. Ver
  `docs/examples.md`.
