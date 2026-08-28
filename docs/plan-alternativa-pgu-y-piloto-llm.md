# Plan de la alternativa PGU y piloto de anotación con LLM

**Versión:** 2026-08-21  
**Estado:** alternativa recomendada, pendiente de discusión con el profesor guía  
**Caso principal:** boletín 15480-13, Ley N.º 21.735  
**Caso comparativo propuesto:** boletín 14588-13, Ley N.º 21.419, Pensión Garantizada Universal  
**Estado de la pipeline audiovisual:** pausada para el corpus de la tesis

## 1. Decisión propuesta

La alternativa recomendada mantiene las discusiones en Sala de la Ley N.º 21.735 como corpus principal e incorpora la Historia de la Ley N.º 21.419 como antecedente comparativo para las hipótesis temporales. El diseño será asimétrico: la reforma de 2022-2025 sostendrá el análisis principal de coaliciones y estrategias de legitimación; la PGU aportará una línea de base para examinar permanencia, difusión y adaptación de los repertorios que legitiman la capitalización individual.

La pipeline audiovisual queda pausada. Su plan técnico se conserva en `docs/plan-implementacion-pipeline-audiovisual.md` para una posible extensión posterior. Esta decisión concentra el trabajo inmediato en cuatro tareas compatibles con cualquier resolución posterior sobre el corpus:

1. elaborar y probar el libro de códigos;
2. construir una muestra manual de referencia;
3. evaluar modelos locales de anotación;
4. fijar contratos de datos y criterios de aceptación.

La incorporación definitiva de la PGU se decidirá después de comprobar la disponibilidad y calidad de su corpus AKN y de discutir el alcance de la tesis con el profesor guía.

## 2. Justificación sustantiva

### 2.1 Dos episodios legislativos posteriores al estallido

Los casos representan dos modalidades de reforma previsional en el escenario político posterior al estallido social, los retiros de fondos y la pandemia.

| Dimensión | PGU, 2021-2022 | Reforma previsional, 2022-2025 |
|---|---|---|
| Gobierno | Sebastián Piñera | Gabriel Boric |
| Proyecto | Boletín 14588-13 | Boletín 15480-13 |
| Resultado | Ley N.º 21.419 | Ley N.º 21.735 |
| Alcance principal | Expansión del componente fiscal de pensiones | Modificación amplia de componentes contributivos y solidarios |
| Relación con la capitalización individual | Conserva la arquitectura contributiva y agrega una prestación financiada fiscalmente | Interviene la distribución de la cotización adicional y crea nuevos mecanismos solidarios |
| Tipo de conflicto esperado | Menor intensidad y mayor consenso | Mayor intensidad y negociación estructural |
| Función en el estudio | Antecedente temporal comparativo | Caso principal |

La variación entre los casos permite observar cómo los actores articulan solidaridad, necesidad, reciprocidad, propiedad, capitalización y sostenibilidad frente a reformas de distinta profundidad. La diferencia de alcance forma parte de la interpretación y debe registrarse como condición del diseño.

### 2.2 Alcance de la comparación

El estudio podrá describir continuidades y transformaciones discursivas entre dos momentos post-estallido. El diseño permite comparar repertorios, coaliciones partidarias y combinaciones conceptuales. Las diferencias observadas también pueden reflejar cambios en el objeto legislado, la composición del Congreso, el gobierno, la urgencia y la intensidad del conflicto. Por ello, el análisis utilizará lenguaje asociativo e interpretativo y evitará atribuir las diferencias a un efecto aislado del gobierno de Boric o del paso del tiempo.

La secuencia temporal es sustantivamente útil:

1. el debate de la PGU muestra cómo se justificó una expansión solidaria fiscal durante el final del gobierno de Piñera;
2. el inicio de la reforma de Boric muestra qué elementos de ese repertorio ya eran transversales;
3. las etapas de 2024 y 2025 muestran cómo esos elementos se conservaron, difundieron o recombinaron durante una negociación más profunda.

### 2.3 Contribución esperada

Este alcance puede reforzar el argumento de robustez ideacional al extender la observación a más de una tramitación. Como antecedente, la PGU ofrece un caso de acomodación solidaria compatible con la capitalización individual. La Ley N.º 21.735 somete ese arreglo a una presión reformista mayor. La continuidad de un núcleo justificativo entre ambos procesos aportaría evidencia de permanencia. Los cambios en su alcance partidario informarían la difusión. Las nuevas articulaciones entre solidaridad y restricciones contributivas, focalizadas o financieras informarían la adaptación.

## 3. Diseño analítico asimétrico

### 3.1 Distribución de las preguntas e hipótesis

| Componente | PGU | Ley N.º 21.735 |
|---|---|---|
| H1, estructura de coaliciones | Caracterización descriptiva si la densidad lo permite | Evaluación principal |
| Q2, estrategias de legitimación | Comparación secundaria | Modelamiento principal |
| H3a, permanencia | Línea de base | Continuidad entre casos y etapas internas |
| H3b, difusión | Identificación del alcance previo | Adopción posterior por actores o partidos |
| H3c, adaptación | Solidaridad fiscal y focalizada | Solidaridad contributiva negociada |

La asimetría evita exigir el mismo tamaño, densidad de red o nivel de conflicto a ambos procesos. El antecedente puede cumplir su función comparativa aunque su corpus resulte menor.

### 3.2 Reformulación provisional de H3

Las siguientes formulaciones sirven como insumo para la conversación con el profesor guía. Su redacción definitiva dependerá del inventario de la PGU y del solapamiento de actores.

**H3a. Permanencia:** El núcleo del repertorio que legitima la capitalización individual conservará su presencia, orientación favorable e integración relacional entre la tramitación de la PGU y la reforma previsional de 2022-2025, así como entre las etapas internas de esta última.

**H3b. Difusión:** Los componentes del repertorio de preservación que durante la discusión de la PGU se concentren en sus defensores iniciales ampliarán posteriormente su alcance entre actores y partidos orientados a transformar el sistema previsional.

**H3c. Adaptación:** El repertorio de preservación articulará la solidaridad con restricciones contributivas, focalizadas o financieras en ambos episodios, y diversificará esas articulaciones cuando la reforma de 2022-2025 cuestione directamente la estructura contributiva del sistema.

### 3.3 Gate específico para H3b

H3b requiere una definición longitudinal estable de los actores. El cambio de legislatura entre las dos leyes limita el seguimiento individual. El análisis seguirá esta jerarquía:

1. parlamentarios presentes en ambos corpus;
2. partidos o familias políticas con continuidad entre los procesos;
3. coaliciones discursivas estimadas por separado en cada caso.

Las comparaciones partidarias requieren la afiliación vigente en la fecha de cada intervención. La columna `current_party` del corpus actual representa la militancia observada durante la extracción y resulta inadecuada como variable longitudinal para 2021-2025. Antes de analizar H3b se construirá una tabla actor-partido-tiempo con fuente, fecha de inicio, fecha de término y estado de resolución. La militancia actual podrá conservarse como dato descriptivo separado.

Cuando el solapamiento individual resulte insuficiente, H3b se transformará en una pregunta exploratoria:

> **Q3b:** ¿Cómo varía el alcance partidario y organizacional del repertorio de preservación entre la discusión de la PGU y la reforma previsional de 2022-2025?

Los conceptos ya compartidos por sectores reformistas durante la PGU se clasificarán como alcance transversal previo. Esta regla impide atribuir a la tramitación de 2022-2025 una difusión ocurrida con anterioridad.

## 4. Corpus disponible y corpus por adquirir

### 4.1 Reforma previsional de 2022-2025

El archivo `data/speech_df.parquet` contiene cuatro discusiones en Sala:

| Fecha | Etapa | Filas totales de la vista analítica |
|---|---|---:|
| 2024-01-23 | Primer trámite, Cámara | 102 |
| 2024-01-24 | Primer trámite, Cámara | 342 |
| 2025-01-27 | Segundo trámite, Senado | 306 |
| 2025-01-29 | Tercer trámite, Cámara | 276 |

La vista contiene 1.026 filas: 774 intervenciones y 252 eventos de transcripción. Las intervenciones suman 1.433.393 caracteres y 239.464 palabras. Un total de 438 intervenciones supera las 75 palabras. Los turnos breves y procedimentales servirán como negativos informativos durante el piloto de relevancia.

Los textos presentan una distribución de extensión muy desigual. Treinta intervenciones superan 8.000 caracteres y la más larga alcanza 27.352. La pipeline de anotación deberá segmentar las intervenciones largas sin perder su `utterance_id`, orden, hablante ni contexto documental.

### 4.2 PGU

La fuente propuesta es la Historia de la Ley N.º 21.419, originada en el [boletín 14588-13](https://www.camara.cl/legislacion/proyectosdeley/tramitacion.aspx?prmBOLETIN=14588-13&prmID=15069). La ficha de [Ley Chile](https://www.bcn.cl/leychile/navegar?idNorma=1171923&idParte=&idVersion=2022-05-26) vincula la ley con su Historia de la Ley.

La adquisición seguirá el mismo contrato utilizado para el boletín 15480-13:

1. consultar la Historia de la Ley mediante `bcn-scraper`;
2. construir un manifiesto explícito de documentos;
3. identificar las discusiones en Sala;
4. comprobar que cada documento corresponde al boletín 14588-13;
5. extraer intervenciones y eventos de transcripción;
6. resolver actores con `PersonaBCN` y preservar los IDs AKN locales como procedencia;
7. resolver la afiliación partidaria vigente en la fecha de cada intervención;
8. producir reportes de cobertura, identidad, duplicación y pérdidas;
9. calcular sesiones, intervenciones, actores, partidos, palabras y caracteres;
10. revisar una muestra para determinar relevancia sustantiva y comparabilidad conceptual.

### 4.3 Gate de admisión de la PGU

La PGU ingresará al corpus comparativo cuando cumpla las siguientes condiciones:

- existe una Historia de la Ley AKN recuperable y trazable;
- el manifiesto identifica de manera inequívoca las discusiones parlamentarias;
- la extracción conserva el orden y la atribución de las intervenciones;
- el corpus incluye más de un sector político y contenido sustantivo sobre pensiones;
- aparecen conceptos relevantes para el libro de códigos común;
- la cobertura permite al menos una comparación descriptiva por etapa o cámara.

Una tramitación breve y consensual seguirá siendo útil para H3a y H3c. La estimación de coaliciones en la PGU quedará condicionada por la densidad observada. El documento de decisión registrará estas dos posibilidades antes de modificar `thesis.md`.

## 5. Cambios previstos en la tesis

La incorporación de la PGU requiere ajustes concentrados. El marco de justicia social, merecimiento, legitimación y robustez ideacional puede conservar su estructura general.

### 5.1 Resumen e introducción

- presentar la Ley N.º 21.735 como caso principal;
- describir la PGU como antecedente temporal comparativo;
- reemplazar la afirmación de 92 sesiones por el número efectivo de documentos incorporados;
- delimitar el universo como discurso parlamentario en Sala;
- presentar ambos procesos como episodios post-estallido bajo gobiernos y reformas de distinto alcance.

### 5.2 Antecedentes conceptuales y empíricos

- agregar un apartado breve sobre la PGU;
- explicar la solidaridad fiscal y focalizada como una modalidad de adaptación institucional;
- derivar las expectativas comparativas de H3 a partir de esa trayectoria;
- mantener las diferencias de diseño previsional como condición de alcance.

### 5.3 Pregunta e hipótesis

- conservar H1 y Q2 centradas en la reforma de 2022-2025;
- ampliar H3a y H3c a la comparación entre procesos;
- decidir H3b según el solapamiento de actores y partidos;
- distinguir cambio temporal, diferencia de gobierno y diferencia de profundidad reformista.

### 5.4 Metodología

- agregar una justificación de selección de casos;
- documentar las fuentes AKN y el manifiesto de cada ley;
- definir `bill_number` y `legislative_process_id` en cada declaración;
- modelar la afiliación partidaria como atributo temporal y conservar su fuente;
- modelar el caso o proceso como predictor cuando corresponda;
- informar comparaciones dentro de cada proceso y entre procesos por separado;
- actualizar la estrategia de muestreo manual para incluir ambos corpus después de admitir la PGU.

### 5.5 Resultados y discusión

- presentar primero la estructura del caso principal;
- utilizar la PGU como línea de base para H3;
- informar los patrones comparables y las diferencias de alcance;
- discutir composición legislativa, urgencia y profundidad de la reforma como explicaciones alternativas.

## 6. Trabajo que puede comenzar antes de decidir sobre la PGU

La anotación con LLM puede pilotearse inmediatamente con la reforma actual. El trabajo inicial es reutilizable bajo las tres opciones de corpus consideradas. Esta fase desarrollará el instrumento de medición y evaluará la capacidad de modelos locales para aplicarlo. La decisión sobre PGU modifica la población a codificar, mientras el contrato de anotación, el libro de códigos y las métricas permanecen.

Las cuatro sesiones ofrecen suficiente heterogeneidad para una primera evaluación:

- Cámara y Senado;
- tres etapas constitucionales;
- intervenciones parlamentarias, ministeriales y procedimentales;
- textos breves y extensos;
- posiciones políticas diversas;
- intervenciones etiquetadas, texto recuperado por regex y una sesión reconstruida mediante fallback XML.

La prioridad inmediata es producir una versión operativa del libro de códigos. La inferencia masiva comenzará después de fijar definiciones, criterios de inclusión, ejemplos positivos, contraejemplos y reglas de ambigüedad.

## 7. Objetivos del piloto LLM

La prueba debe responder cinco preguntas:

1. ¿Puede distinguir intervenciones sustantivas de contenido procedimental?
2. ¿Identifica declaraciones completas y recupera evidencia textual exacta?
3. ¿Asigna los conceptos del libro de códigos con precisión suficiente?
4. ¿Determina correctamente la orientación de cada actor frente al concepto?
5. ¿Distingue la presencia de legitimación y sus estrategias principales y secundarias?

Cada tarea se evaluará por separado. Esta separación permitirá localizar errores y evitar que una salida final aparentemente plausible oculte fallos en la extracción, la postura o la estrategia.

Esta fase inicial cubrirá inferencia y evaluación. El ajuste fino de modelos queda fuera de su alcance. La necesidad de entrenamiento se evaluará después de agotar mejoras en el libro de códigos, la segmentación, el prompt, el esquema de salida y la selección del modelo.

## 8. Unidad de entrada y segmentación

### 8.1 Filtro inicial

La entrada principal incluirá filas con:

```text
kind == "participation"
bill_number == "15480-13"
section_name != "Votacion"
is_preamble == false
```

Los eventos de transcripción se conservarán para reconstruir contexto y se excluirán de la clasificación sustantiva. Las interrupciones con hablante se mantendrán como una categoría diferenciada durante el piloto.

### 8.2 Unidad contextual

Una intervención completa será la unidad documental primaria. El registro de muestreo y auditoría incluirá:

```text
utterance_id
document_uri
utterance_order
date
constitutional_stage
speaker_id
speaker
role
party_at_date
gender
content
previous_context_optional
next_context_optional
```

El payload primario para el modelo ocultará `speaker_id`, nombre, partido y género. Estos atributos se utilizarán para muestreo, evaluación de sesgos y análisis posterior. La entrada de inferencia contendrá el texto objetivo con una etiqueta neutra de hablante y, cuando el experimento lo requiera, el rol institucional y contexto adyacente claramente separado. Una ablación comparará inferencia sin contexto, con contexto y con rol para medir su aporte y sus posibles sesgos.

A partir de cada intervención se extraerán cero, una o varias declaraciones. Cada declaración deberá vincular un concepto, una orientación y una evidencia textual atribuible al hablante objetivo.

### 8.3 Intervenciones largas

Las intervenciones que excedan el presupuesto de contexto se dividirán en límites de párrafo. Cada fragmento conservará `utterance_id` y recibirá un `chunk_id`. La reconstrucción posterior:

1. unirá declaraciones partidas por el límite del fragmento;
2. deduplicará evidencias solapadas;
3. preservará los offsets respecto del texto original;
4. marcará los casos cuya interpretación dependa de un fragmento anterior o posterior.

El tamaño de chunk se fijará después de seleccionar el tokenizer y el modelo. Los límites se expresarán en tokens y se registrarán en la configuración de cada ejecución.

## 9. Contrato de salida

La inferencia producirá JSON validable. Una estructura provisional es:

```json
{
  "schema_version": "0.1.0",
  "utterance_id": "...",
  "chunk_id": "...",
  "substantive_relevance": "relevant|procedural|uncertain",
  "statements": [
    {
      "statement_id": "...",
      "evidence_text": "...",
      "start_char": 0,
      "end_char": 120,
      "concept_id": "...",
      "stance": "support|oppose|ambivalent|uncertain",
      "explicit_legitimation": true,
      "primary_strategy": "moralization|rationalization|narrativization|normalization|authorization|null",
      "secondary_strategy": "...|null",
      "ambiguity_reasons": [],
      "requires_human_review": false
    }
  ],
  "record_warnings": []
}
```

La evidencia deberá ser una subcadena exacta del texto de entrada. Un validador calculará los offsets y rechazará evidencia inventada o normalizada por el modelo. El esquema conservará estados `uncertain` y `requires_human_review`; la pipeline evitará convertir la incertidumbre en una categoría sustantiva.

Cada ejecución registrará además:

```text
run_id
model_id
model_revision
tokenizer_revision
prompt_version
codebook_version
schema_version
generation_parameters
software_environment
started_at
completed_at
input_checksum
output_checksum
```

## 10. Libro de códigos y muestra manual

### 10.1 Libro de códigos v0.1

Cada concepto debe especificar:

- definición conceptual;
- criterio de inclusión;
- criterio de exclusión;
- unidad mínima de evidencia;
- reglas para apoyo, rechazo y ambivalencia;
- ejemplos positivos;
- contraejemplos cercanos;
- relación con otros conceptos;
- condiciones que exigen revisión manual.

Las estrategias de legitimación se documentarán en una sección separada. La extracción de conceptos y la clasificación de estrategias usarán prompts distintos durante el primer piloto.

### 10.2 Micro-piloto manual

El micro-piloto tendrá entre 30 y 40 intervenciones, distribuidas entre las cuatro sesiones. Incluirá:

- intervenciones sustantivas largas;
- intervenciones sustantivas breves;
- intervenciones procedimentales;
- actores de distintos partidos y roles;
- ejemplos con varios conceptos;
- casos ambiguos y desacuerdos dentro de una misma intervención.

Esta muestra servirá para medir tiempo de anotación, corregir definiciones y comprobar el esquema. Sus resultados pertenecen al desarrollo y no se utilizarán como evaluación final.

### 10.3 Desarrollo y evaluación

Después del micro-piloto se construirán dos conjuntos separados:

- **desarrollo:** 60 a 80 intervenciones para ajustar prompts y reglas;
- **evaluación ciega:** 80 a 120 intervenciones estratificadas, reservadas hasta congelar el sistema;
- **diagnóstico de categorías raras:** muestra dirigida adicional, informada por separado y excluida de las métricas agregadas representativas.

Los rangos se ajustarán a partir del tiempo real de anotación. La muestra de evaluación se estratificará por sesión, cámara, etapa, partido o bloque, género, tipo de actor, longitud y tipo de intervención. Las decisiones de muestreo y las semillas se conservarán en un manifiesto.

### 10.4 Fiabilidad de la referencia humana

Una sola persona realizará la anotación. Las métricas modelo-humano evaluarán concordancia con la referencia elaborada por el investigador; no representan fiabilidad entre codificadores humanos. Una submuestra podrá anotarse nuevamente tras un intervalo y sin consultar la primera decisión para estimar estabilidad intracodificador. Los desacuerdos se adjudicarán y documentarán antes de cerrar el gold standard.

## 11. Evaluación

### 11.1 Métricas por tarea

| Tarea | Métricas principales |
|---|---|
| Relevancia sustantiva | precisión, sensibilidad, F1, matriz de confusión |
| Extracción de declaración | coincidencia exacta y solapamiento de spans |
| Concepto | precisión, sensibilidad y F1 micro, macro y por categoría |
| Orientación | exactitud y F1 por clase, condicionadas a concepto correcto |
| Legitimación explícita | precisión, sensibilidad y F1 |
| Estrategia principal | exactitud, macro-F1 y matriz de confusión |
| Estrategia secundaria | precisión y sensibilidad multilabel |
| Ambigüedad | sensibilidad para casos que requieren revisión |
| Validez estructural | porcentaje de JSON válido y evidencia textual verificable |

La kappa de Cohen podrá informarse como medida complementaria de concordancia modelo-humano. Su interpretación indicará explícitamente que uno de los codificadores es un sistema automatizado.

### 11.2 Criterios provisionales de aceptación

Los umbrales se fijarán antes de abrir la evaluación ciega. Como punto de partida:

- JSON válido y evidencia exacta: al menos 99 %;
- relevancia sustantiva: F1 de al menos 0,90;
- combinación concepto-orientación: precisión de al menos 0,90 para aceptación automática;
- legitimación explícita: F1 de al menos 0,80;
- estrategia principal: macro-F1 de al menos 0,75;
- derivación a revisión: sensibilidad de al menos 0,90 en los casos ambiguos del gold standard.

Las categorías que queden bajo el umbral seguirán una de tres rutas: revisión manual completa, fusión conceptualmente justificada con otra categoría o exclusión del análisis confirmatorio. Los umbrales no se reajustarán después de observar los resultados finales.

### 11.3 Análisis de errores

Los errores se clasificarán por:

- confusión entre conceptos próximos;
- pérdida de negación o atribución;
- interpretación de citas de terceros como postura del hablante;
- dependencia del contexto anterior;
- segmentación defectuosa;
- múltiples declaraciones fusionadas;
- legitimación implícita clasificada como explícita;
- confusión entre estrategia principal y secundaria;
- sesgo por partido, género, cámara, rol o longitud.

El análisis de errores guiará la revisión del instrumento. La evaluación final permanecerá cerrada durante ese ajuste.

## 12. Ejecución en el clúster

### 12.1 Factibilidad

Antuco dispone de dos AMD Instinct MI210 con 64 GB de VRAM por GPU, 512 GB de RAM y ROCm 7.2.3 según la información disponible. Este hardware es suficiente para inferencia local con modelos instructivos de tamaño pequeño y mediano. Un modelo de 8 a 14 mil millones de parámetros debería caber holgadamente en una GPU con precisión adecuada. Los modelos cercanos a 30 mil millones requerirán cuantización, paralelismo entre las dos GPU o una configuración conservadora del contexto.

Las intervenciones actuales contienen aproximadamente 1,43 millones de caracteres. Su costo de inferencia es pequeño respecto de la capacidad del nodo. La anotación manual, la definición del libro de códigos y el análisis de errores probablemente determinarán el calendario.

### 12.2 Entorno separado

El `pyproject.toml` de la tesis exige Python 3.14 y el repositorio `reportes-congreso-imfd` fija dependencias orientadas a ASR, incluida una versión específica de PyTorch. La inferencia ROCm conviene en un entorno Python 3.11 o 3.12 separado y validado en Antuco.

La organización recomendada es un paquete independiente, con nombre provisional `congreso-discurso-llm`, que contenga:

```text
src/discourse_coding/
  schema.py
  sampling.py
  segmentation.py
  prompts.py
  inference.py
  validation.py
  merge.py
  evaluation.py
scripts/
  build_sample.py
  run_inference.py
  evaluate_run.py
configs/
  codebook/
  prompts/
  models/
  slurm/
tests/
```

El paquete leerá `speech_df.parquet` como entrada y escribirá artefactos versionados que luego se incorporarán a la tesis. La ubicación definitiva puede decidirse después de la reunión; el prototipo debe evitar dependencias con la pipeline audiovisual.

### 12.3 Spike técnico en Antuco

El primer trabajo en GPU comprobará:

1. acceso a la GPU solicitado explícitamente mediante SLURM;
2. disponibilidad de PyTorch con HIP y ROCm;
3. carga del tokenizer y de un modelo pequeño;
4. generación de un JSON válido para cinco intervenciones;
5. uso de VRAM, tiempo por token y utilización de GPU;
6. escritura atómica y reanudación desde checkpoint.

El nombre exacto de la partición, el tipo GRES y las restricciones del nodo se consultarán con `sfree` y `scontrol` antes de fijar el script. Los trabajos respetarán el límite de 24 horas y guardarán resultados por lote.

### 12.4 Estrategia de modelos

La evaluación comparativa inicial incluirá:

- un modelo instructivo multilingüe de 8 a 14 mil millones de parámetros;
- un segundo modelo de otra familia o de mayor tamaño;
- la misma versión del libro de códigos, prompt, esquema y muestra;
- inferencia determinista o de baja temperatura;
- una repetición de la muestra de evaluación para medir estabilidad.

Durante el spike, cada GPU puede ejecutar un modelo independiente. Esta configuración ofrece una comparación rápida y evita introducir paralelismo distribuido antes de demostrar que aporta una mejora necesaria. Los nombres y revisiones se congelarán después de verificar compatibilidad real con ROCm.

### 12.5 Almacenamiento

| Ubicación | Contenido |
|---|---|
| `home` | código, configuraciones pequeñas y scripts SLURM |
| `workspace` de Antuco | pesos, caché del modelo, dataset activo y salidas temporales de inferencia |
| `scratch` | checkpoints transferibles, logs y ejecuciones intermedias |
| `archive` | gold standard, outputs finales, manifiestos y entorno reproducible |

Los pesos regenerables pueden eliminarse al cerrar el experimento. Los prompts, el libro de códigos, las muestras, los outputs finales y los checksums deben conservarse.

## 13. Pipeline del piloto

```text
speech_df.parquet
  -> filtro de intervenciones
  -> muestra estratificada
  -> anotación humana de desarrollo
  -> libro de códigos v0.1
  -> segmentación y contexto
  -> inferencia local
  -> validación JSON y evidencia
  -> unión y deduplicación de statements
  -> comparación con referencia humana
  -> análisis de errores
  -> revisión de código y prompt
  -> congelamiento
  -> evaluación ciega
  -> decisión de escalamiento
```

Cada lote será idempotente. Una ejecución reanudada omitirá registros válidos ya procesados y conservará los intentos fallidos para auditoría.

## 14. Entregables

### 14.1 Antes de la reunión con el profesor guía

1. este documento de alternativa;
2. inventario técnico del corpus actual;
3. borrador de libro de códigos v0.1;
4. esquema JSON de anotación;
5. muestra de 30 a 40 intervenciones;
6. estimación del tiempo manual por intervención;
7. si el entorno del clúster está disponible, smoke test con cinco intervenciones.

### 14.2 Después de la decisión sobre PGU

1. inventario del boletín 14588-13;
2. informe de comparabilidad entre leyes;
3. decisión documentada sobre H3b;
4. actualización del muestreo para ambos corpus;
5. revisión del resumen, la pregunta, H3 y métodos en `thesis.md`;
6. corrida formal de desarrollo y evaluación ciega.

## 15. Gates de decisión

### Gate P0. Empezar el piloto LLM

**Estado:** habilitado.

Requisitos disponibles:

- corpus textual procesado;
- IDs estables de intervención y actor;
- texto público sin tratamiento biométrico;
- cuatro sesiones y variación suficiente para un piloto;
- hardware local de inferencia disponible en el clúster.

### Gate P1. Congelar el libro de códigos

Requiere:

- micro-piloto manual completado;
- definiciones, inclusiones, exclusiones y ambigüedades revisadas;
- tiempo de anotación medido;
- categorías raras identificadas;
- esquema JSON validado.

### Gate P2. Escalar la anotación de la reforma actual

Requiere:

- evaluación ciega completada;
- umbrales fijados previamente y satisfechos;
- sesgos y errores críticos examinados;
- política de revisión humana definida;
- modelo, prompt y código congelados.

### Gate P3. Incorporar la PGU

Requiere:

- admisión técnica del corpus AKN;
- acuerdo sustantivo con el profesor guía;
- formulación final de H3;
- libro de códigos aplicable a ambos casos;
- muestra manual ampliada con ejemplos de la PGU.

### Gate P4. Reabrir videos

Los videos permanecen fuera del corpus central durante esta fase. Su reapertura requiere una decisión ética, tiempo reservado y una justificación que compense el costo de atribución de hablantes.

## 16. Riesgos y mitigaciones

| Riesgo | Consecuencia | Mitigación |
|---|---|---|
| Libro de códigos inmaduro | Métricas inestables y categorías cambiantes | micro-piloto antes de inferencia masiva |
| PGU demasiado consensual | red poco densa | usarla como línea de base descriptiva para H3a y H3c |
| Cambio de legislatura | seguimiento individual incompleto | comparar partidos y analizar actores solapados por separado |
| Uso de militancia actual | clasificación partidaria anacrónica | construir afiliación actor-partido-tiempo con fuentes y vigencias |
| Diferencia de alcance entre leyes | confusión entre tiempo y tipo de reforma | diseño asimétrico y explicación de alternativas |
| Intervenciones muy largas | truncamiento y pérdida de contexto | segmentación por párrafos, solapamiento y merge trazable |
| Modelo genera evidencia inexistente | declaraciones sin trazabilidad | coincidencia exacta y validación de offsets |
| Clases raras | métricas agregadas engañosas | métricas por clase y muestra diagnóstica separada |
| Ajuste al conjunto de evaluación | sobreestimación del desempeño | evaluación ciega congelada |
| Dependencias ROCm | retraso técnico | entorno separado y spike con modelo pequeño |
| Metadatos políticos en el prompt | clasificación guiada por estereotipos partidarios | ocultar identidad, partido y género en la inferencia primaria |
| Revisión manual excesiva | pérdida de tiempo disponible | medir carga en el micro-piloto y priorizar errores que afectan aristas |

## 17. Recomendación operativa

El piloto LLM puede comenzar con la reforma actual antes de resolver la incorporación de la PGU. La secuencia recomendada es:

1. construir el libro de códigos v0.1;
2. seleccionar y anotar manualmente 30 a 40 intervenciones;
3. implementar el esquema y sus validadores;
4. ejecutar un smoke test local en Antuco;
5. comparar dos modelos sobre la muestra de desarrollo;
6. llevar a la reunión resultados de factibilidad, tiempo manual y errores observados;
7. decidir después de la reunión si se extrae y admite la PGU;
8. congelar el instrumento antes de la evaluación final.

Esta ruta produce avances útiles para cualquier decisión posterior. También reduce el riesgo de dedicar recursos a una anotación masiva antes de estabilizar la medición.
