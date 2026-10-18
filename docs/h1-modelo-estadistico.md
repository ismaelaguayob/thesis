# Modelo estadístico de H1: resumen para revisión

Código: `procesamiento/resultados_h1.qmd`. Datos: `R/analysis_base.R`.

## Qué queremos estimar

Los parlamentarios justifican sus posiciones en el debate de la reforma de pensiones (Ley 21.735) con conceptos normativos de un libro de 16 códigos: necesidad material, propiedad de los fondos, etc. Cada intervención en Sala fue codificada por un LLM, con validación humana. Para cada concepto se registra si la intervención lo **apoya** y si lo **rechaza**. H1 predice que la derecha apoya más que la izquierda siete conceptos y la izquierda más que la derecha otros cinco, y que cada bloque rechaza más los conceptos del otro.

El estimando es, para cada concepto *c*, la diferencia derecha − izquierda en la probabilidad de que una intervención apoye (o rechace) *c*. H1 se contradice, concepto por concepto, si la diferencia es nula o tiene el signo opuesto al esperado.

## Datos y por qué un logit multinivel

- **Unidad:** intervención × concepto. Son 324 intervenciones sustantivas de 180 actores (izquierda 163, centro 29, derecha 132), cada una repetida para los 12 conceptos de H1: 3.888 filas.
- **Resultado binario:** apoyo sí o no; el rechazo va en un modelo aparte. Los eventos son poco frecuentes: entre 1 % y 50 % según el concepto y el bloque.
- **Dependencia:** un actor aporta varias intervenciones y cada intervención aparece 12 veces. Las observaciones no son independientes, y algunos actores hablan mucho más que otros. Por eso se usa un **intercepto aleatorio por actor**.

Especificación (modelo de apoyo):

```
apoyo ~ concepto * bloque + género + log_palabras + (1 | actor)
```

- **La interacción `concepto × bloque`** da a cada celda su propia log-odds. Codificación de tratamiento: referencias izquierda y el primer concepto.
- **`log_palabras`** es el logaritmo estandarizado de la longitud de la intervención: las más largas tienen más oportunidades de contener declaraciones.
- **Los ministros** (2 actores, 16 intervenciones, todos de izquierda) se incluyen en su bloque sin un control propio: un coeficiente estimado con dos actores aportaría poco y el intercepto por actor ya absorbe que intervengan más.
- **El modelo de rechazo** tiene la misma forma, pero solo con los 5 conceptos que tienen al menos 10 rechazos: 1.620 filas.

## El problema: separación

En varias celdas el resultado no varía. Por ejemplo, ninguna de las 163 intervenciones de izquierda apoya la capitalización individual. Con máxima verosimilitud (`lme4::glmer`), la verosimilitud sigue creciendo mientras la log-odds de esa celda tiende a −∞. Es separación cuasi completa, y la estimación resultante es inutilizable: −18 en escala logit, con error estándar 2.137. Esas celdas no se pueden eliminar sin perder justamente los contrastes más claros de H1.

## Estimador elegido: máxima verosimilitud penalizada (`blme::bglmer`)

`bglmer` (Chung et al., 2013) maximiza la verosimilitud del mismo GLMM multiplicada por un prior sobre los efectos fijos:
- normal(0, 10) para el intercepto;
- normal(0, 2,5) para los demás coeficientes.

**Qué implica:**
- **Es la moda de la posterior (MAP), no una inferencia bayesiana completa.** No hay MCMC. La aproximación de Laplace, los efectos aleatorios y los errores estándar son los de `glmer`. Equivale a una penalización de tipo ridge sobre los coeficientes, en la línea de Gelman et al. (2008) y de la corrección de Firth para la regresión logística.
- **El prior es débil en escala logit:** una desviación estándar de 2,5 admite razones de probabilidades de hasta unas 150 sin penalización fuerte. En las celdas con información suficiente casi no cambia las estimaciones. En las separadas, detiene el coeficiente en un valor finito: la probabilidad predicha de que la izquierda apoye la capitalización queda en cerca de 1 % en vez de 0.
- **Costo:** un sesgo hacia cero en las celdas separadas, es decir, contrastes algo más conservadores. Además, como el prior actúa sobre los coeficientes, su efecto depende de la codificación: las interacciones se miden respecto de la categoría de referencia.

Ambos modelos convergen sin avisos y no son singulares. La desviación estándar del intercepto por actor es 0,36 en el modelo de apoyo y 0,54 en el de rechazo.

## Qué se reporta

- **Probabilidades predichas** por concepto y bloque, con `marginaleffects`. Se promedian sobre las covariables observadas y se fija el efecto aleatorio en 0 (`re.form = NA`), es decir, corresponden a un actor típico.
- **Contrastes derecha − izquierda** por concepto, en puntos porcentuales.
- **Intervalos del 95 %** por simulación: 1.000 extracciones de los efectos fijos de una normal multivariada con la matriz de covarianza estimada. Así quedan dentro de [0, 1].
- **Tabla de razones de probabilidades** de ambos modelos en el anexo.
- **Sensibilidad:** el mismo modelo con las anotaciones de un segundo LLM.

## Preguntas para quien revise

1. **Prior.** ¿Es razonable normal(0, 2,5) con codificación de tratamiento, o conviene una codificación en desviaciones, o una t o Cauchy en vez de una normal? Propuesta: una sensibilidad con desviación estándar 5.
2. **Predicciones.** ¿Condicionales (actor típico) o marginales (integrando sobre el efecto aleatorio)? Con una desviación estándar del intercepto de 0,36 la diferencia es pequeña, pero conviene decidir cuál reportar.
3. **Estructura aleatoria.** Un solo intercepto por actor supone la misma propensión en todos los conceptos. ¿Habría que agregar actor × concepto, aunque probablemente quede singular?
4. **Intervalos.** La simulación ignora la incertidumbre de la varianza del efecto aleatorio. ¿Basta, o conviene un bootstrap paramétrico?
5. **Comparaciones múltiples.** Son 17 contrastes (12 de apoyo y 5 de rechazo) sin corrección. Se reportan los intervalos y la dirección, no un conteo de contrastes «significativos». ¿Es suficiente?
6. **Alternativa.** ¿Valdría la pena estimar el mismo modelo bayesiano completo (por ejemplo, con `brms`) como sensibilidad, o es innecesario para este propósito?

**Referencias.** Chung, Y., Rabe-Hesketh, S., Dorie, V., Gelman, A. y Liu, J. (2013). A nondegenerate penalized likelihood estimator for variance parameters in multilevel models. *Psychometrika, 78*(4). Gelman, A., Jakulin, A., Pittau, M. G. y Su, Y.-S. (2008). A weakly informative default prior distribution for logistic and other regression models. *Annals of Applied Statistics, 2*(4).
