# Evaluación y revisión iterativa del libro de códigos

## Propósito y alcance

Este reporte documenta la evaluación manual y la revisión del libro de códigos utilizado para identificar justificaciones normativas en el debate legislativo sobre la reforma previsional chilena. El proceso tuvo carácter de calibración: buscó precisar el objeto teórico, detectar categorías ausentes, establecer fronteras entre conceptos y ajustar la unidad textual antes de la codificación principal. Las frecuencias informadas describen este proceso y no constituyen estimaciones de prevalencia ni de confiabilidad.

El instrumento adopta la variante del análisis de redes discursivas orientada a *discourse coalitions*. En esta variante se codifican las justificaciones que sostienen una posición respecto de un asunto, mientras que la operacionalización de *advocacy coalitions* suele representar posiciones sobre varios instrumentos de política [@leifeld_discourse_2017]. Por esta razón, una preferencia institucional o un diagnóstico factual ingresa al libro únicamente cuando funciona como razón para justificar una distribución, un derecho o un diseño previsional.

## Estrategia de evaluación

La versión inicial combinó los cinco criterios CARIN, control, actitud, reciprocidad, identidad y necesidad, con conceptos específicos del caso chileno. La revisión siguió una estrategia deductiva-inductiva de análisis de contenido dirigido. Laenen et al. aplican los criterios CARIN definidos previamente y mantienen abierta la identificación de justificaciones contextuales, entre ellas igualdad o universalismo y conciencia de costos [@laenen_why_2019]. Este diseño permitió conservar un núcleo teórico comparable y revisar inductivamente los argumentos que el esquema inicial no representaba adecuadamente.

Cada unidad se codificó mediante uno o más fragmentos textuales exactos, un concepto y una orientación de `Apoyo` o `Rechazo`. La orientación se determinó frente a la proposición ancla de cada código, por lo que no equivale al apoyo u oposición general a la reforma. La opción `Revisar` se reservó para justificaciones normativas explícitas ausentes del instrumento. Después de cada ronda, estos casos, las notas de codificación y los problemas de segmentación se agruparon y evaluaron según tres condiciones: recurrencia en más de una declaración, frontera operacional distinguible y relevancia para la formación de coaliciones discursivas. Los candidatos poco frecuentes se conservaron como observaciones para rondas posteriores.

## Rondas de calibración manual

Entre el 24 y el 30 de agosto de 2026 se completaron tres sesiones, que sumaron 65 unidades y 76 anotaciones. Cada sesión conservó una copia del libro aplicado y su checksum.

| Ronda | Libro aplicado | Unidades | Anotaciones | Apoyo / rechazo | En `Revisar` | Unidades sin declaración |
|---|---:|---:|---:|---:|---:|---:|
| 1. Calibración inicial | 0.1.1-draft, 10 conceptos | 10 | 26 | 13 / 13 | 7 | 4 |
| 2. Piloto ampliado | 0.2.2-pilot, 11 conceptos | 40 | 35 | 23 / 12 | 8 | 20 |
| 3. Comprobación focalizada | 0.3.0-pilot, 13 conceptos | 15 | 15 | 12 / 3 | 3 | 4 |

La primera ronda mostró que `suficiencia_pensiones` expresaba un resultado deseable o un diagnóstico y carecía de una regla clara para decidir orientación. También reveló argumentos sobre igualdad, universalidad y administración estatal que el libro inicial no cubría. El uso de intervenciones completas produjo unidades de hasta 1.956 palabras, lo cual dificultaba la identificación de declaraciones y hacía poco comparable la tarea humana con la futura clasificación automatizada.

La segunda ronda confirmó la utilidad de trabajar con párrafos y contexto adyacente. Sus casos en revisión mostraron recurrencia de tres líneas argumentales: la previsión entendida como mercado o negocio, la ilegitimidad asociada al origen dictatorial del sistema y la defensa del destino individual de las cotizaciones. También permitió precisar la frontera entre capitalización individual y reciprocidad contributiva. Los argumentos aislados sobre progresividad o regresividad de las cargas se mantuvieron fuera del libro por su baja recurrencia.

La tercera ronda produjo tres formulaciones convergentes sobre el valor democrático de los acuerdos, el compromiso y la moderación. Esta recurrencia justificó incorporar `acuerdos_moderacion`. La misma ronda registró un problema de segmentación en un bloque extenso, a partir del cual se estableció un máximo estricto de 150 palabras.

## Modificaciones conceptuales

La revisión partió de diez conceptos iniciales y culminó en una versión 0.4.0-pilot de catorce conceptos. Las principales decisiones fueron las siguientes:

| Decisión | Resultado operacional |
|---|---|
| Retiro de suficiencia de las pensiones | Se excluyó como código porque describe un nivel de resultado. La privación que justifica aumentar prestaciones se codifica como necesidad; una regla de cobertura o trato común se codifica como igualdad o universalismo. |
| Reformulación de sostenibilidad financiera | Se reemplazó por `conciencia_costos`, entendida como restricción de gasto. `Apoyo` afirma que una reforma es demasiado costosa, carece de financiamiento sostenible o excede la capacidad fiscal; `Rechazo` refuta esa restricción. |
| Delimitación de solidaridad | Se restringió a `solidaridad_intergeneracional`: responsabilidad, transferencias o distribución de riesgos entre cohortes activas y jubiladas. Las transferencias intrageneracionales se asignan según necesidad, igualdad o reciprocidad. |
| Reincorporación de capitalización individual | Se conservó como regla de autofinanciamiento: las cotizaciones ingresan a cuentas individuales para financiar la pensión de su titular. Las menciones descriptivas al sistema AFP quedan excluidas. |
| Ampliación de reciprocidad contributiva | El trabajo, las cotizaciones y el esfuerzo contributivo pueden generar un título moral para recibir, conservar o controlar recursos y protección previsional. Esta definición recoge el sentido de haber ganado el derecho a recibir apoyo propio del criterio de reciprocidad [@oorschot_who_2000]. |
| Conservación de propiedad individual | Se mantuvo como categoría empírica diferenciada, centrada en titularidad, control, heredabilidad o apropiación de los fondos. Su vínculo con *entitlement* constituye una interpretación teórica: el saldo acumulado puede operar como estatus adquirido que fundamenta un título sobre recursos [@hulle_measuring_2018]. |
| Nuevos criterios contextuales | Se añadieron `igualdad_universalismo` y `conciencia_costos`, siguiendo las justificaciones contextuales observadas por Laenen et al. [@laenen_why_2019]. |
| Nuevas justificaciones institucionales | Se añadieron `ineficiencia_estado`, `prevision_como_mercado` e `ilegitimidad_origen_dictatorial`. Las comisiones abusivas se integraron en previsión como mercado cuando expresan extracción o lucro privado. |
| Nueva justificación procedimental | `acuerdos_moderacion` registra que el compromiso entre posiciones contrapuestas, los acuerdos amplios o la moderación otorgan valor y legitimidad democrática a una reforma. |

La versión resultante contiene cinco criterios CARIN; dos criterios contextuales, igualdad o universalismo y conciencia de costos; tres justificaciones distributivas específicas, capitalización individual, propiedad individual y solidaridad intergeneracional; tres justificaciones institucionales, ineficiencia estatal, previsión como mercado e ilegitimidad del origen dictatorial; y una justificación procedimental, acuerdos y moderación.

Dos reglas transversales resuelven ambigüedades frecuentes. Primero, la codificación múltiple está permitida cuando un pasaje formula razones diferenciables. Por ejemplo, la defensa del destino de una cotización en la cuenta propia expresa capitalización; la afirmación de que el esfuerzo del trabajador le concede un título moral sobre ese aporte expresa reciprocidad. Segundo, los criterios CARIN pueden inferirse desde afirmaciones sobre una política cuando el vínculo justificativo es explícito. Una denuncia de pensiones miserables que fundamenta ayuda estatal expresa necesidad, aunque la oración describa el resultado de una política y no caracterice directamente a un grupo beneficiario.

## Ajustes operacionales y trazabilidad

La evaluación conceptual se acompañó de cambios en la herramienta de validación. La unidad presentada pasó de una intervención completa a un bloque de uno o más párrafos, acompañado por los bloques anterior y siguiente como contexto. Se descartan unidades residuales menores de cinco palabras. Los párrafos con menos de 50 palabras se agregan preferentemente al bloque anterior o se acumulan hacia un objetivo de 100 palabras. El máximo de 150 palabras es estricto; los párrafos que lo exceden se dividen primero por oraciones y, si resulta necesario, por límites de palabras.

La interfaz resalta en amarillo los fragmentos ya anotados, permite múltiples declaraciones por bloque e incorpora comentarios generales y flags de calidad para votos, contenido procedimental, texto breve o truncado, contexto insuficiente y problemas de segmentación. Los votos y pasajes procedimentales permanecen disponibles para clasificación manual y se marcan como unidades sin declaraciones cuando carecen de contenido sustantivo.

El libro editable se mantiene en formato XLSX y el JSON consumido por la aplicación se genera desde ese archivo. Cada sesión congela la versión completa del instrumento, su checksum, la fuente del corpus, los bloques de contexto, los offsets de los fragmentos y las decisiones de codificación. Esta arquitectura permite reconstruir qué definiciones estaban disponibles en cada ronda y evita que una modificación posterior altere retrospectivamente los resultados guardados.

## Estado del instrumento y próximos controles

La versión 0.4.0-pilot constituye el instrumento conceptual resultante de la calibración. El corpus procesado cumple actualmente el rango de 5 a 150 palabras por unidad y la implementación cuenta con pruebas automatizadas para segmentación, muestreo, persistencia, offsets, comentarios y sincronización entre XLSX y JSON.

El proceso fue realizado por una sola persona codificadora y todavía no permite estimar confiabilidad intercoder. Antes de la codificación principal se recomienda recodificar, después de un intervalo y sin consultar las decisiones previas, un subconjunto aleatorio para evaluar estabilidad intracoder. La evaluación posterior del modelo deberá utilizar una muestra distinta de la empleada para ajustar el libro y reportar por separado detección de declaraciones, delimitación de spans, asignación conceptual y orientación.

Permanecen abiertas tres decisiones que requieren mayor evidencia empírica: una posible separación entre igualdad y universalismo, una eventual capa paralela para premisas cognitivas y la distinción entre acuerdos o moderación y argumentos de responsividad democrática. Hasta comprobar su recurrencia, estos casos deben conservarse mediante `Revisar` y notas de adjudicación.
