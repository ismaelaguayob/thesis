# Material suplementario metodológico

Versión de trabajo 0.1  
Estado: documento acumulativo en desarrollo

## Propósito

Este suplemento conserva las decisiones operativas y técnicas que respaldan la metodología de la tesis, pero cuyo detalle interrumpiría la exposición sociológica del manuscrito principal. La primera versión reúne la codificación de estrategias de legitimación a nivel de declaración, el contrato de salida esperado del LLM, el tratamiento de casos ambiguos y las decisiones preliminares para la medición de H1 y H3.

El documento se ampliará a medida que avancen el libro de códigos, el piloto y el procesamiento. Los umbrales de aceptación, los ejemplos empíricos definitivos y las versiones completas de los prompts se fijarán después del piloto.

## 1. Jerarquía de unidades

1. **Etapa legislativa:** periodo institucional al que pertenece cada sesión.
2. **Sesión:** evento legislativo identificado de manera única y realizado en una fecha-hora específica.
3. **Intervención:** turno de habla de un actor dentro de una sesión. Es la unidad textual de entrada, conserva el orden interno del discurso y funciona como ventana de coocurrencia para H3c.
4. **Declaración DNA:** afirmación unitaria que vincula actor, concepto y posición. Es la unidad de codificación y análisis de Q2.
5. **Evidencia textual:** pasaje con offsets que respalda una etiqueta. Se conserva para trazabilidad y revisión, pero no genera una fila ni una unidad analítica independiente.

Una intervención puede contener varias declaraciones. Cada declaración puede no contener una legitimación explícita, contener una sola estrategia o combinar una estrategia principal y una secundaria.

## 2. Estructura de la codificación

### 2.1 Campos mínimos

| Campo | Tipo | Regla |
|---|---|---|
| `session_id` | identificador | Identifica una sesión única. |
| `session_datetime` | fecha-hora | Fecha y hora de realización de la sesión. |
| `legislative_stage` | categoría | Etapa legislativa a la que pertenece la sesión. |
| `intervention_id` | identificador | Turno de habla dentro de la sesión. |
| `intervention_order` | entero | Orden de la intervención; sólo trazabilidad. |
| `declaration_id` | identificador | Declaración DNA única. |
| `actor_id` | identificador | Actor que formula la declaración. |
| `concept` | categoría | Concepto del libro de códigos. |
| `position` | binaria | Apoyo o rechazo frente al concepto. |
| `explicit_condition` | binaria | Indica si la afirmación supedita el acceso, el monto o el diseño de una prestación a un requisito. |
| `condition_basis` | categoría o nulo | Concepto del libro de códigos que fundamenta la condición; durante el piloto admite la marca provisional `condicionalidad_no_CARIN`. |
| `provisional_condition_subtype` | texto o nulo | Descripción normalizada de una condición aún no cubierta por el libro de códigos; sólo se utiliza en el piloto. |
| `explicit_legitimation` | binaria | Indica si existe al menos un fundamento explícito de legitimación. |
| `primary_strategy` | categoría o nulo | Estrategia que sostiene el vínculo justificativo central. |
| `primary_evidence` | texto y offsets o nulo | Evidencia que respalda la estrategia principal. |
| `secondary_strategy` | categoría o nulo | Estrategia adicional, distinta de la principal. |
| `secondary_evidence` | texto y offsets o nulo | Evidencia que respalda la estrategia secundaria. |
| `ambiguity_flag` | binaria | Indica si la clasificación requiere revisión manual. |
| `ambiguity_reasons` | lista | Motivos normalizados de ambigüedad. |
| `candidate_strategies` | lista | Alternativas plausibles detectadas antes de la revisión. |
| `review_status` | categoría | `automatic`, `manually_resolved` o `unresolved`. |
| `review_notes` | texto o nulo | Justificación de la adjudicación manual. |

Durante el piloto se aplicarán tres restricciones adicionales: si `explicit_condition = 0`, `condition_basis` y `provisional_condition_subtype` serán nulos; si `condition_basis = condicionalidad_no_CARIN`, deberá completarse `provisional_condition_subtype` y activarse la revisión manual; y esta marca provisional deberá resolverse antes de fijar el libro de códigos para el procesamiento completo.

### 2.2 Categorías de estrategia

Las estrategias posibles son:

- `moralization`
- `rationalization`
- `narrativization`
- `normalization`
- `authorization`

`No explicit legitimation` no constituye una sexta estrategia. Cuando `explicit_legitimation = 0`, las estrategias principal y secundaria deben ser nulas por diseño.

## 3. Distinción entre estrategia principal y secundaria

### 3.1 Estrategia principal

La estrategia principal es el recurso que sostiene de manera más directa el vínculo entre:

1. la posición sustantiva expresada en la declaración; y
2. la pretensión de que esa posición es válida, aceptable, necesaria o legítima.

Para identificarla se utilizará la siguiente pregunta contrafactual:

> Si se retirara este recurso de la declaración, ¿se perdería el fundamento central mediante el cual la posición se presenta como aceptable?

Si la respuesta es afirmativa, el recurso es candidato a estrategia principal.

### 3.2 Estrategia secundaria

La estrategia secundaria es un fundamento adicional e identificable que complementa o refuerza la estrategia principal, pero cuya eliminación no destruye el vínculo justificativo central.

La secundaria:

- debe pertenecer a una categoría distinta de la principal;
- debe contar con evidencia textual propia;
- no se asigna sólo porque aparezca una palabra asociada a otra categoría;
- no se asigna cuando la segunda categoría sea apenas una interpretación implícita del codificador;
- nunca genera una fila adicional en la base principal.

### 3.3 Criterios que no determinan primacía

No se elegirá la estrategia principal por:

- aparecer primero en la declaración;
- ocupar una mayor extensión textual;
- contener más palabras clave;
- coincidir con la categoría más frecuente del actor o de su coalición;
- ajustarse mejor a una expectativa teórica de Q2.

La clasificación debe depender de la función justificativa desempeñada en la declaración concreta.

### 3.4 Configuraciones permitidas

| Configuración | Codificación |
|---|---|
| 1:0 | `explicit_legitimation = 0`; principal y secundaria nulas. |
| 1:1 | Una estrategia principal; secundaria nula. |
| 1:2 | Una estrategia principal y una secundaria distinta. |
| Jerarquía irresoluble | Se registran las candidatas, se marca ambigüedad y se deriva a revisión. |

## 4. Casos ambiguos

### 4.1 Motivos normalizados

Un caso se marcará como ambiguo cuando ocurra al menos una de las siguientes situaciones:

- `tie_between_strategies`: dos estrategias parecen igualmente centrales;
- `insufficient_evidence`: el fundamento es demasiado implícito para sostener una etiqueta;
- `category_boundary`: la evidencia se ubica en el límite entre dos definiciones;
- `context_dependency`: la clasificación depende de texto que no forma parte de la declaración;
- `outside_codebook`: existe un recurso justificativo que no corresponde claramente a las categorías;
- `conflicting_evidence`: distintas partes de la declaración conducen a decisiones incompatibles.

La ausencia de legitimación explícita no es, por sí sola, una ambigüedad.

### 4.2 Procedimiento de revisión

1. El LLM entrega las categorías candidatas, sus evidencias y el motivo de ambigüedad.
2. El revisor examina la declaración dentro de la intervención completa.
3. Si la evidencia pertenece a la misma intervención y revela que los límites de la declaración fueron demasiado estrechos, éstos pueden corregirse dejando registro del cambio.
4. El revisor aplica nuevamente la prueba del fundamento central.
5. El resultado se registra como `manually_resolved` o `unresolved`.
6. Los casos irresolubles no reciben una categoría sustantiva forzada y no ingresan al multinomial principal.

Durante la validación, una parte de los casos ambiguos será codificada independientemente antes de la adjudicación. Esto permitirá evaluar si la distinción principal-secundaria es reproducible y no sólo si el LLM coincide con una única decisión del investigador.

## 5. Contrato preliminar de salida del prompt

El prompt deberá solicitar una salida estructurada equivalente a la siguiente:

```json
{
  "declaration_id": "string",
  "explicit_legitimation": true,
  "primary_strategy": "rationalization",
  "primary_evidence": {
    "text": "string",
    "start_char": 0,
    "end_char": 0
  },
  "secondary_strategy": "authorization",
  "secondary_evidence": {
    "text": "string",
    "start_char": 0,
    "end_char": 0
  },
  "ambiguity_flag": false,
  "ambiguity_reasons": [],
  "candidate_strategies": [],
  "requires_manual_review": false,
  "decision_rationale": "string"
}
```

### 5.1 Restricciones de consistencia

- Si `explicit_legitimation = false`, ambas estrategias y ambas evidencias deben ser nulas.
- Si existe una estrategia principal, debe existir evidencia principal.
- La estrategia secundaria es opcional y debe diferir de la principal.
- Si existe una estrategia secundaria, debe existir evidencia secundaria.
- No pueden asignarse más de dos estrategias.
- Si el modelo no puede jerarquizar las candidatas con evidencia suficiente, debe activar `ambiguity_flag` y `requires_manual_review`.
- La explicación no puede incorporar información que no esté en la intervención entregada como contexto.
- El modelo no puede crear categorías nuevas durante la codificación principal.

## 6. Secuencia preliminar del prompt

La instrucción se organizará en pasos:

1. Identificar la proposición y la posición ya codificadas en la declaración.
2. Determinar si la declaración ofrece una razón explícita para considerar válida o aceptable esa posición.
3. Identificar todas las estrategias plausibles utilizando las definiciones y ejemplos del libro de códigos.
4. Aplicar la prueba contrafactual del fundamento central para elegir una principal.
5. Registrar una secundaria sólo cuando exista un segundo fundamento explícito e independiente.
6. Citar evidencia textual y offsets para cada etiqueta.
7. Marcar ambigüedad cuando la jerarquía o la categoría no pueda decidirse de manera fundada.
8. Verificar las restricciones de consistencia antes de entregar el JSON.

El prompt definitivo incluirá ejemplos positivos, negativos y fronterizos provenientes del piloto. Los ejemplos no se seleccionarán sólo por claridad; deberán incluir casos difíciles y desacuerdos reales.

## 7. Plan de validación

### 7.1 Tareas evaluadas por separado

1. Extracción de la declaración y el concepto.
2. Clasificación de la posición.
3. Detección de legitimación explícita.
4. Clasificación de la estrategia principal.
5. Detección de una estrategia secundaria.
6. Clasificación de la estrategia secundaria, condicionada a su presencia.
7. Derivación de casos ambiguos.
8. Concordancia exacta del registro completo.

### 7.2 Resultados que se informarán

- precisión, sensibilidad y F1 por tarea y categoría;
- macro-F1 para evitar que las categorías frecuentes oculten un bajo desempeño en las infrecuentes;
- kappa de Cohen para las decisiones categóricas;
- matrices de confusión para estrategia principal y secundaria;
- concordancia exacta del registro completo;
- proporción de registros derivados a revisión;
- motivos de ambigüedad y tasa de resolución manual;
- desempeño de los casos aceptados automáticamente frente al desempeño total después de la adjudicación.

Los umbrales de aceptación se fijarán antes de procesar el corpus completo, utilizando los resultados del piloto y la frecuencia observada de cada categoría.

### 7.3 Diagnóstico de ambigüedad

La ambigüedad es un atributo del proceso de medición y no una estrategia sustantiva. Se comprobará si los casos derivados a revisión se concentran por:

- estrategia candidata;
- etapa legislativa;
- tipo de instancia;
- tipo de actor;
- partido;
- género;
- coalición discursiva, una vez estimadas las comunidades.

Una concentración sistemática indicaría que el instrumento o el prompt funciona de manera desigual para ciertos lenguajes o actores y requeriría revisión antes de interpretar Q2.

## 8. Especificación analítica de Q2

### 8.1 Modelo principal

- Unidad: declaración.
- Universo: declaraciones con legitimación explícita y estrategia principal resuelta.
- Resultado: estrategia principal, con cinco categorías mutuamente excluyentes.
- Predictores fijos: coalición, partido, tipo de actor y etapa legislativa.
- Posibles interacciones: se incorporarán sólo cuando respondan a una comparación temporal sustantiva, especialmente coalición por etapa.
- Interceptos aleatorios cruzados: actor y sesión.

La sesión se identifica por su fecha-hora y representa el contexto compartido de las declaraciones producidas en ese evento. La intervención no se incorpora como efecto aleatorio en la especificación principal porque la declaración es la unidad de Q2 y no existen filas separadas por evidencia justificativa.

### 8.2 Declaraciones sin legitimación explícita

Se informará su proporción por coalición. Si el piloto muestra que no son infrecuentes, se añadirá un modelo binario complementario para estimar la probabilidad de que una declaración contenga alguna legitimación explícita. El punto de corte para adoptar este modelo se fijará antes del procesamiento completo.

### 8.3 Estrategias secundarias

Las estrategias secundarias se analizarán mediante:

- una tabla de combinaciones principal-secundaria;
- su frecuencia por coalición y etapa;
- una sensibilidad basada en la presencia de cada estrategia como principal o secundaria, sin duplicar declaraciones.

No se interpretará la secundaria como una segunda observación independiente.

### 8.4 Sensibilidad a la adjudicación

El modelo principal incluirá los casos resueltos manualmente. Como sensibilidad, se repetirá excluyendo todas las declaraciones inicialmente marcadas como ambiguas. Los casos irresolubles se contabilizarán y caracterizarán, pero permanecerán fuera del multinomial.

## 9. Próximas ampliaciones

Las siguientes versiones del suplemento incorporarán gradualmente:

- definiciones completas y ejemplos fronterizos del libro de códigos;
- versiones numeradas de los prompts;
- fórmulas de proyección y normalización de las redes de congruencia y conflicto;
- detalles del algoritmo de comunidades con relaciones positivas y negativas;
- especificaciones y diagnósticos de los modelos multinivel;
- operacionalización completa de H3a, H3b y H3c;
- registro de cambios introducidos después del piloto.

## 10. Decisión pendiente: intermediación entre coaliciones

La detección de comunidades utilizará la red completa de congruencia y conflicto mediante una implementación que considere relaciones positivas y negativas. Permanece pendiente definir la medida con la que se evaluará si los actores de centroizquierda conectan ambos polos.

### 10.1 Problema de la especificación actual

La centralidad de intermediación estándar se basa en caminos mínimos. Si se calcula sin pesos, utiliza sólo la presencia de las aristas e ignora su signo y magnitud. Las semejanzas firmadas tampoco pueden incorporarse directamente como distancias: los vínculos negativos no representan caminos de conexión y una mayor congruencia positiva debería implicar una distancia menor, no mayor.

Por lo tanto, no se calculará la intermediación directamente sobre los pesos firmados ni sobre sus valores absolutos.

### 10.2 Alternativas bajo evaluación

1. **Intermediación ponderada sobre la subred de congruencia positiva.** Se conservarían sólo los vínculos positivos y su fuerza se transformaría en distancia. Mantiene una medida conocida y requiere un cambio metodológico acotado, pero no incorpora directamente los vínculos negativos y puede discriminar poco si la proyección es muy densa.
2. **Coeficiente de participación sobre vínculos positivos.** Evaluaría si la fuerza positiva de cada actor se distribuye entre comunidades. Se ajusta directamente a la idea de conexión intercomunitaria, pero depende de la partición detectada y debe acompañarse por la fuerza total para evitar considerar como mediador a un actor con vínculos equilibrados pero débiles.
3. **Congruencia directa con ambos polos.** Compararía la semejanza de cada actor con los perfiles de preservación y transformación. Es sustantivamente transparente, pero exige construir una medida específica y evitar circularidad entre la definición de los polos y la evaluación de los actores.

### 10.3 Criterio provisional de mínima complejidad

La opción provisional es conservar la centralidad de intermediación, calculándola sólo sobre la subred de congruencia positiva y transformando fuerza en distancia. La red completa de congruencia y conflicto se mantendría para detectar las comunidades. Después se comprobaría descriptivamente que los actores con mayor intermediación tienen vínculos positivos con ambos polos.

Antes de cerrar esta decisión, el piloto deberá examinar:

- si la intermediación presenta variación suficiente;
- si está dominada por la frecuencia de intervención o la fuerza total;
- si los actores mejor posicionados se conectan efectivamente con ambas comunidades;
- y si la densidad de la proyección vuelve la medida poco informativa.

El coeficiente de participación o la congruencia directa se incorporarían sólo si estos diagnósticos muestran que la intermediación positiva no representa adecuadamente la posición mediadora postulada en H1.

## 11. Núcleo teórico y seguimiento temporal de H3

### 11.1 Separación entre perfiles teóricos y comunidades empíricas

H3a y H3b utilizarán un núcleo de preservación definido antes del análisis principal:

- capitalización individual positiva;
- propiedad individual positiva;
- reciprocidad contributiva positiva;
- control positivo;
- sostenibilidad financiera positiva.

En esta lista, *reciprocidad contributiva* reemplaza a *correspondencia contributiva* para mantener la categoría teórica del marco CARIN. *Control positivo* designa el respaldo a utilizar la responsabilidad atribuida a las personas por su situación previsional como criterio distributivo. Las reglas precisas de inclusión y exclusión de cada concepto-postura se fijarán en el libro de códigos antes del procesamiento completo.

La condicionalidad no integrará el núcleo como concepto unitario. Durante el piloto se registrará como una propiedad de la declaración y su fundamento se codificará, cuando sea posible, mediante los criterios CARIN. Una condición contributiva puede expresar reciprocidad; una exigencia asociada a la responsabilidad por la propia situación puede expresar control; y una focalización basada en insuficiencia material puede expresar necesidad. Por ello, *focalización no CARIN* no se utilizará como categoría general.

Cuando una declaración establezca explícitamente una condición pero su fundamento no pueda asignarse justificadamente a un criterio existente, se activará la marca provisional `condicionalidad_no_CARIN` y se conservará una descripción breve de su subtipo. Esta marca servirá para reunir y comparar casos durante el piloto; no se incorporará automáticamente como nodo de la red ni como componente de H3. Sólo un patrón recurrente, internamente coherente y teóricamente interpretable dará lugar a una nueva categoría en el libro de códigos antes del procesamiento completo.

Las comunidades se detectarán sin imponerles inicialmente las etiquetas de preservación o transformación. Después se compararán sus perfiles con el núcleo anterior y con el perfil teórico de transformación. Los conceptos compartidos, inesperados o aparentemente contradictorios se conservarán como resultados y no se incorporarán automáticamente a la definición de ninguno de los perfiles.

Esta separación evita que la comunidad empírica utilizada para clasificar a los actores determine también qué conceptos contarán posteriormente como evidencia de permanencia o difusión.

### 11.2 H3a: permanencia

La permanencia se evaluará exclusivamente sobre el núcleo teórico fijo. Para cada componente se observarán:

- cobertura entre actores activos;
- balance entre apoyo y rechazo;
- fuerza de las conexiones con los demás componentes del núcleo.

Las conexiones entre el núcleo y solidaridad positiva se reservarán para H3c. Otros conceptos empíricamente relevantes podrán describirse, pero no se sumarán como indicadores de H3a.

### 11.3 H3b: cohorte inicial y movimiento de actores

La primera detección de comunidades se conservará como referencia para identificar la cohorte inicialmente orientada a la transformación. Fijar esa clasificación permite responder una pregunta direccional: si quienes partieron más alejados del núcleo de preservación comienzan posteriormente a utilizarlo.

Esta fijación no supone que la pertenencia sea inmutable. Las comunidades se volverán a estimar en cada etapa y el movimiento de los actores se informará como resultado complementario. La distinción es:

- **cohorte inicial fija:** define desde dónde se evalúa la trayectoria;
- **pertenencia dinámica:** describe hacia dónde se desplazan los actores;
- **núcleo teórico fijo:** define qué contenidos se transfieren.

La difusión se observará en los actores activos de la cohorte inicial mediante el uso posterior de conceptos-postura del núcleo, su amplitud dentro de éste y la diversidad partidaria y organizacional alcanzada. El criterio mínimo para distinguir una adopción sustantiva de una mención aislada se fijará después del piloto y antes del procesamiento completo.

Los actores que aparezcan por primera vez después de la etapa inicial no integrarán la cohorte direccional principal, porque no existe una posición inicial observada. Su uso del núcleo se reportará separadamente como expansión de alcance.

Si la primera etapa no produce comunidades claramente alineables con los perfiles teóricos, no se forzarán las etiquetas de preservación y transformación. En ese escenario deberá revisarse la operacionalización direccional de H3b y evaluarse una clasificación basada en el alineamiento inicial de cada actor con los perfiles teóricos.

### 11.4 H3c: adaptación

Solidaridad positiva no formará parte por sí sola del núcleo de preservación. H3c evaluará su articulación, dentro de una misma intervención, con restricciones contributivas, focalizadas o financieras. Estas restricciones se identificarán por el contenido sustantivo de las declaraciones y no por la marca residual `condicionalidad_no_CARIN`. Esto permite distinguir:

- solidaridad positiva no condicionada;
- solidaridad incorporada bajo restricciones compatibles con el núcleo de preservación;
- y conceptos compartidos desde la primera etapa que no representan cambio temporal.
