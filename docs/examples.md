### Necesidad, Luna marca referencia no:

- no habrá ninguna posibilidad de aumentar la PGU a 250.000 pesos. El egoísmo de quienes voten en contra condenará a las personas mayores, principalmente mujeres, a seguir arreglándoselas como puedan.

- No puedo votar en contra de que se mejoren las pensiones de aquellos que reciben la PGU o que tienen hoy malas pensiones

- La creación de la PGU mejoró las tasas de reemplazo en los tres quintiles más vulnerables de la población y, sin duda, su aumento es una gran noticia.

- debe ser capaz de eliminar el riesgo de pobreza en la vejez

Pienso que más que no haya política, hay una relajación del término. En otros casos, yo fui demasiado estricto aplicando el concepto.


### Solidaridad, Luna no marca

Me confunde esto...

- instalar en el debate público una visión distinta que se funda en el destino personal no puede entenderse si no es en una relación con los otros y en el destino colectivo: sin solidaridad y sin cooperación no hay desarrollo posible ni sostenible.

Esto puede ser un error mio:

Es ideológico, en primer lugar, porque se trata de dar un primer paso hacia un sistema más justo o con vías a la solidaridad previsional.

- Hubiera preferido que los seis puntos, que serán aportados por los empleadores, fueran a solidaridad, a verdadera seguridad social, como sucede en las democracias sólidas, en las que se entiende que la solidaridad es uno de los mejores valores del ser humano.

Diría que a veces fui muy relajado con mi interpretación. En otras, Luna no percibió el criterio normativo presente. Creo que hay evidencia para decir que tener un LLM como segundo codificador, independientemente del grado de acuerdo, es útil para encontrar puntos ciegos y problemas del esquema de codificación que antes quizás no podrían verse, lo añadiría a la discusión.

---

## Revisión de los 109 desacuerdos (Claude)

Revisé todos los desacuerdos de Luna en los cinco conceptos críticos
(`output/validation/desacuerdos_luna_conceptos_criticos.csv`). Abajo, los
patrones que concentran la mayoría de los casos y los ejemplos que mejor los
ilustran. Los marcados con ★ son los que propondría para el paper. Las lecturas
son interpretaciones mías para que decidas; el número de bloque es el de la app.

### Patrón 1. Necesidad material: el diagnóstico se lee como justificación

La mayoría de los 28 casos en que Luna asigna necesidad y la referencia no son
diagnósticos genéricos («las pensiones son bajas», «no alcanzan para llegar a fin
de mes») que el modelo lee como un criterio de asignación por necesidad. Calza
con tu nota sobre la «relajación del término». Es el error de frontera típico.

★ **Bloque 232, Ley 21.735.** El diagnóstico aparece como concesión en un
discurso cuyo argumento es otro:

> «Sin duda, las pensiones hoy son bajas y hay que mejorarlas, pero este acuerdo
> entre una izquierda que quiere destruir las AFP, pero les regala 1.800 millones
> de dólares, y una derecha que dice defender la Constitución, pero que le mete la
> mano en el bolsillo a los trabajadores pasando a llevar el derecho a propiedad,
> es algo realmente digno de Ripley.»

- Referencia: acuerdos y moderación (rechazo).
- Luna: además, necesidad material (apoyo), a partir de «las pensiones hoy son
  bajas y hay que mejorarlas».
- Lectura: la frase concede un diagnóstico compartido antes de criticar el
  acuerdo; no usa la necesidad para justificar a quién proteger. Es llamativo
  porque una cláusula concesiva basta para que el modelo vea un criterio.

Otros del mismo tipo: bloque 6 («en Chile las pensiones no son adecuadas por
diversos factores y debemos remediar esto»), 329 («Lo que le importa a la gente
es llegar a fin de mes») y 360 (el que anotaste).

### Patrón 2. Necesidad material: a veces el error es de la referencia

En una minoría, la lectura de Luna parece correcta y la referencia demasiado
estricta, como anotaste.

★ **Bloque 51, Ley 21.538.**

> «si le vamos a garantizar a los mayores 65 años y a personas con discapacidad,
> que tienen adicionalmente incluso gastos mayores que los que tienen los adultos
> mayores sin discapacidad, me parece que se hace urgente, a lo mejor, hacer una
> versión 4.0, en la que se integre a la PGU a las personas con discapacidad.»

- Referencia: igualdad y universalismo.
- Luna: necesidad material.
- Lectura: los «gastos mayores» de un grupo se usan como razón para extenderle la
  protección, que es casi la definición del criterio de necesidad. Sirve para
  mostrar que el desacuerdo no siempre es error del modelo.

Del mismo tipo: bloque 288 (ampliar el pilar solidario «del 60 al 80 por ciento
de la población de menores recursos») y 24 (la PGU y los «tres quintiles más
vulnerables»).

### Patrón 3. Solidaridad: la palabra frente a la idea

Es el patrón más interesante narrativamente. La referencia tiende a codificar
solidaridad cuando aparece la palabra, aunque designe un mecanismo; Luna la
codifica cuando aparece la idea de un deber compartido, aunque no se nombre. El
libro 0.5.1 excluye explícitamente las menciones retóricas de «solidaridad» y el
mecanismo por sí solo, así que en varios casos Luna aplica la regla con más
literalidad que la referencia.

★ **La palabra sin la idea (la referencia codifica, Luna no).**

> Bloque 39: «casi dieciocho años han tenido que volver a pasar para que el
> Presidente Boric logre incorporar la solidaridad como elemento para la
> seguridad social.»

> Bloque 92: «un sistema de pensiones que incorpora, además de la capitalización
> individual, un componente solidario que permitirá mejorar las pensiones de forma
> inmediata»

Ambos nombran la solidaridad como componente institucional, sin formular un
deber.

★ **La idea sin la palabra (Luna codifica, la referencia no).**

> Bloque 16: «la sociedad no puede seguir solo con la ley de la selva, con el
> “ráscate con tus propias uñas”. Por eso se crea un seguro social»

> Bloque 125: «Acá no podemos ser egoístas con aquellas personas que ganan 100.000
> pesos mensuales de jubilación»

Ninguno dice «solidaridad», pero ambos rechazan que cada uno se arregle solo y
exigen apoyo mutuo. Este par muestra bien tu reflexión sobre el LLM como segundo
codificador que revela puntos ciegos.

Hay también omisiones genuinas del modelo, como el bloque 93 (el que anotaste:
«sin solidaridad y sin cooperación no hay desarrollo posible ni sostenible») o el
244 («Es inmoral pretender financiar la solidaridad con cargo a los propios
trabajadores»), donde hay un juicio normativo explícito.

### Patrón 4. Confusión entre las dos solidaridades

★ **Bloque 75, Ley 21.735.**

> «el otro 3 por ciento financiará un seguro social que permitirá hacer realidad
> ese concepto de “hoy por ti, mañana por mí”.»

- Referencia: solidaridad intergeneracional.
- Luna: solidaridad como deber colectivo.
- Lectura: «hoy por ti, mañana por mí» puede leerse como reciprocidad entre
  personas o entre generaciones. Es un ejemplo limpio de confusión entre
  conceptos vecinos, que aparece como un falso positivo en uno y una omisión en
  otro.

### Patrón 5. Solidaridad intergeneracional: el rechazo al reparto

Casi todos los casos en que Luna asigna solidaridad intergeneracional y la
referencia no son rechazos al «reparto» que Luna codifica como oposición al
concepto.

**Bloque 301, Ley 21.735.**

> «Así nos alejamos directamente de los sistemas de reparto que tan mal le han
> hecho al mundo.»

- Referencia: acuerdos y capitalización individual.
- Luna: además, solidaridad intergeneracional (rechazo).
- Lectura: es la misma frontera entre mecanismo y justificación, pero en el polo
  opuesto: el reparto es un mecanismo, y rechazarlo no equivale necesariamente a
  rechazar el deber entre generaciones. Del mismo tipo: bloques 12, 269 y 271.

### Patrón 6. Igualdad: la descripción de una política se lee como justificación

Muchos de los 30 desacuerdos de igualdad tratan de la compensación a las mujeres
por su mayor expectativa de vida. Según tu criterio, la diferencia está en si el
fragmento formula una razón normativa o solo describe la política.

★ **Argumento normativo frente a descripción.**

> Bloque 246 (la referencia codifica igualdad, Luna no): «las mujeres tendrán en
> régimen una pensión igual a la de los hombres»

> Bloque 270 (Luna codifica igualdad, la referencia no): «esta reforma se hace
> cargo de este problema incorporando elementos para equilibrar el desbalance que
> se produce por estos elementos, mediante una compensación económica mensual para
> aquellas mujeres»

- Lectura (tuya): el bloque 246 sostiene un argumento normativo (pensiones
  iguales entre mujeres y hombres), mientras el 270 describe el mecanismo de una
  política. Luna omite el primero y codifica el segundo.
- Es el mismo error de frontera que en necesidad material: tomar la descripción
  de una política o un diagnóstico por una justificación.

### Patrón 7. Conciencia de costos: la refutación escueta

Varios casos en que Luna asigna costos son afirmaciones escuetas de que el
proyecto está financiado, que Luna codifica como rechazo de su inviabilidad.

**Bloque 152, Ley 21.419.** «no es cierto lo que dice; el proyecto está
financiado.» La referencia no lo codificó; la regla del libro (`oppose` =
refutación de la inviabilidad) admite la lectura de Luna. A la inversa, Luna omite
preguntas por el costo sin una afirmación explícita, como el bloque 258 («¿Cuánto
cuesta esta Pensión Garantizada Universal? Cuesta 3.200 millones de dólares… Es un
paso muy muy exigente»).

### Propuesta para el paper

Si caben dos ejemplos en el texto principal:

1. **Bloque 232** (necesidad material, error de frontera): concreta el patrón más
   frecuente en una sola cita.
2. **El par 39 y 16** (solidaridad, la palabra frente a la idea): muestra que
   parte del desacuerdo viene de la referencia y conecta con tu reflexión sobre el
   LLM como segundo codificador, que puede desarrollarse en la discusión.

Si cabe un tercero, el **par 246 y 270** (igualdad), como segundo caso de
descripción leída como justificación; en el texto se resume sin cita.
