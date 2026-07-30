# Material suplementario metodológico

Versión de trabajo 0.1  
Estado: documento acumulativo en desarrollo

## Propósito

Este suplemento conserva las decisiones operativas y técnicas que respaldan la metodología de la tesis, pero cuyo detalle interrumpiría la exposición sociológica del manuscrito principal. La primera versión se concentra en la codificación de estrategias de legitimación a nivel de declaración, el contrato de salida esperado del LLM y el tratamiento de casos ambiguos.

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
