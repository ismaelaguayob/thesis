# Secuencia de validación y cambios del instrumento

Registro cronológico de la calibración del libro, los pilotos con LLM y los
cambios de prompt. La ejecución y replicación se documentan en
[pipeline-anotacion-llm.md](pipeline-anotacion-llm.md). Las revisiones previas a
la validación ciega fueron de calibración o diagnóstico: el codificador veía la
salida del modelo o ajustaba el libro con los mismos casos. Sus conteos no
estiman prevalencia, confiabilidad ni desempeño.

## 1. Calibración manual del libro (24 ago – 3 sep 2026)

Codificación humana sin modelo en la app de validación. Cada sesión congela el
libro aplicado y su checksum (`output/validation/`).

| Fecha | Libro aplicado | Unidad | Unidades | Anotaciones | Resultado |
|---|---|---|---:|---:|---|
| 24–25 ago | 0.1.1-draft (10) | Intervención completa, ley 21.735 | 10 | 26 | Se retira `suficiencia_pensiones`; faltan igualdad, universalidad y administración estatal; unidades de hasta 1.956 palabras. |
| 28 ago | 0.2.2-pilot (11) | Párrafo | 40 | 35 | Recurren previsión como mercado, origen dictatorial y destino individual de las cotizaciones; se separa capitalización de reciprocidad. |
| 30–31 ago | 0.3.0-pilot (13) | Bloque de párrafos | 15 | 15 | Tres casos convergentes justifican `acuerdos_moderacion`; máximo estricto de 150 palabras. |
| 3 sep | 0.4.0-pilot (14) | Bloque, ley 21.419 | 20 | 6 | Aplicación a las otras dos leyes sin nuevos conceptos. |
| 3 sep | 0.4.0-pilot (14) | Bloque, ley 21.538 | 20 | 10 | Ídem. |

Cambios del libro hasta la 0.4.0-pilot:

- `suficiencia_pensiones` se elimina: la privación pasa a necesidad y la regla
  de cobertura o trato común, a igualdad y universalismo.
- `sostenibilidad_financiera` se reemplaza por `conciencia_costos`
  (restricción de gasto; `oppose` = refutación de la inviabilidad).
- `solidaridad` se restringe a `solidaridad_intergeneracional` (relación
  explícita entre cohortes activas y jubiladas).
- `capitalizacion_individual` se acota a la regla de autofinanciamiento;
  `reciprocidad_contributiva` se amplía al esfuerzo como título para recibir,
  conservar o controlar recursos.
- Se agregan `igualdad_universalismo`, `conciencia_costos`, `ineficiencia_estado`,
  `prevision_como_mercado`, `ilegitimidad_origen_dictatorial` y
  `acuerdos_moderacion`. Las comisiones abusivas se integran en previsión como
  mercado.

Criterio para incorporar un concepto: recurrencia en más de una declaración,
frontera operacional distinguible y relevancia para las coaliciones discursivas.
Quedan fuera progresividad tributaria, inversión social y una capa de premisas
cognitivas.

Segmentación resultante: bloques de 5 a 150 palabras; párrafos de menos de 50
palabras se unen al anterior o se acumulan hacia 100; los que exceden 150 se
dividen por oraciones y, en último caso, por palabras. Contexto: bloque anterior
y siguiente de la misma sesión.

## 2. Pilotos con LLM y revisión diagnóstica (8–22 sep 2026)

Todos los pilotos usan Responses API, esfuerzo `max`, `store=false` y esquema
JSON estricto. Cada ejecución congela prompt, libro, esquema y requests.

### Piloto 1 — `pilot_f3a69c2f81c587271ef5` (8 sep)

- Modelo `gpt-5.6-luna`, tope de 16.384 tokens, libro 0.4.0-pilot, prompt
  `annotations_pilot.md` (explicación estructurada por anotación: referencia al
  criterio, codificación, postura, alternativas, evidencia de contexto,
  incertidumbre).
- Muestra: 110 intervenciones (10,04 %), 418 bloques, semilla 20260908,
  estratos ley × sesión.
- Resultado: 306 completas, 109 `incomplete` por agotar el tope y 3 inválidas.
  Revisión diagnóstica de 3 bloques.
- Cobertura: solo 65 de las 110 intervenciones sorteadas quedaron con todos sus
  bloques válidos, de modo que la muestra efectiva no alcanzó el 10 %. La ley
  21.735 concentró la mayor fracción de fallos.
- Consumo: 5,83 millones de tokens registrados, incluida una prueba inicial. El
  97 % de la salida fue razonamiento y el 42 % del consumo del piloto se asoció
  a respuestas sin salida válida. Es el total de las respuestas guardadas, no una
  conciliación de la facturación.
- Longitud: la mediana fue de 117 palabras en los bloques incompletos y de 95 en
  los completos. Es solo un diagnóstico descriptivo, sin efecto causal
  demostrado.
- Anotaciones: 206 (182 `support`, 24 `oppose`), con 28 propuestas de conceptos
  nuevos. El modelo pidió revisión en 102 bloques.
- Inspección dirigida de inputs y outputs (no aleatoria). Los números son de
  bloque en la app; `sample_index` = número − 1.

  | Bloques | Hallazgo | Cambio derivado |
  |:--|:--|:--|
  | 3 y 5 | `igualdad_universalismo` y `necesidad_material` asignados a descripciones de objetivos y requisitos de la PGU | Exigir un criterio normativo ligado a una decisión distributiva; el nombre «Universal» o una regla de focalización no bastan |
  | 11 y 73 | Nombrar una fuente de financiamiento se leyó como rechazo de la falta de sostenibilidad | Distinguir financiamiento descriptivo de defensa fiscal normativa; exigir refutación para `oppose` |
  | 17 | Un mismo fragmento apoya necesidad material y rechaza igualdad, aunque podía ser una sola defensa de focalización | Precisar cuándo un contraste justifica dos códigos |
  | 42 y 232 | Mención descriptiva de acuerdos y explicación técnica del reparto de cotizaciones, correctamente sin códigos | Usarlos como ejemplos negativos de la frontera |
  | 58 | La cita alteró mayúsculas y omitió «Honestamente» | Copiar subcadenas literales; mantener el control local |
  | 143 | El mismo span y la misma propuesta de concepto, repetidos | Exigir unicidad por cita, aparición y concepto |
  | 148 | «Hay que ser didácticos» propuesto como principio previsional | Delimitar `review` a fundamentos previsionales |
  | 241 | Rechazo de responsabilidad por no cotizar junto con apoyo al trabajo de crianza | Revisar si reciprocidad cubre el trabajo no remunerado |
  | 390 | Referencia a `include:4` en un concepto con tres inclusiones | Restringir referencias válidas; mantener el rechazo local |

  Estos casos pasaron a formar parte del conjunto de desarrollo del prompt. Los
  detalles están en `_output/annotations.html`, la última versión del reporte
  del piloto, y en `data/proc_data/llm_pilots/audits/pilot_f3a69c2f81c587271ef5/`.
- Cambios: tope a 32.768 (con reintento a 65.536 ante `max_output_tokens`);
  bloque como unidad primaria y estratos ley × cámara × alineamiento × género;
  prompt `annotations_pilot_v1_confidence.md` con sección de confianza
  (14–18 sep).

### Piloto 2 — `pilot_bbf87273f96292ef3d66` (21 sep)

- `gpt-5.6-luna`, 32.768 tokens, libro 0.4.0-pilot, prompt v1 con confianza.
- Muestra: 361 bloques (10 % de 3.609), semilla 20260908.
- Resultado: 360 completas y 1 inválida.
- Revisión diagnóstica no ciega (21–22 sep) de 174 bloques: 285 juicios sobre
  anotaciones, 211 aceptadas, 23 con cambios y 51 descartadas.
- Cambios (commit `4510158c`):
  - **Libro 0.5.0-candidate (16 conceptos, cerrado).** Se agregan
    `solidaridad_previsional_colectiva` (recursos o riesgos compartidos sin
    relación generacional explícita, incluido el financiamiento tripartito
    presentado como responsabilidad compartida) y `libertad_eleccion_previsional`.
    Se delimitan control, identidad, igualdad y universalismo, y conciencia de
    costos.
  - **Prompt.** La explicación pasa a una justificación de una o dos oraciones; se
    eliminan alternativas, evidencia de contexto e incertidumbre; la remisión a
    revisión la decide el programa.
  - **App.** Más categorías de error y registro de pasajes destacados.

### Piloto 3 — `pilot_54f649d0ea784cb2ef65` (22 sep)

- `gpt-5.6-luna`, 32.768 tokens, libro 0.5.0-candidate.
- Muestra: 361 bloques nuevos, semilla 20260922, excluidos los de pilotos
  previos (2.867 elegibles).
- Resultado: 361 completas. La revisión diagnóstica no dejó archivos de juicio.
- Cambios (commit `671cc1d5`):
  - **Libro 0.5.1-candidate.** La solidaridad colectiva se redefine como
    **solidaridad como deber colectivo**: exige un deber normativo de apoyo mutuo
    o de compartir sacrificios, cargas, recursos o riesgos. Excluye seguro
    social, fondo común, reparto, redistribución, financiamiento tripartito,
    impuestos o aporte estatal descritos o defendidos sin ese deber, y las
    menciones retóricas de «solidaridad». Se ajustan las exclusiones de
    solidaridad intergeneracional para remitir a este concepto.
  - **Prompt `annotations_prompt_final.md`.** Agrega un glosario de siglas (PGU,
    APV, SIS, DIPRECA, CAPREDENA, AFP) y la regla «codifica la justificación
    normativa, no el mecanismo».
  - Se preparó un cuarto input con este libro (`pilot_1550932658f0ee074d7b`) que
    fue reemplazado por el censo y no se conserva.

## 3. Instrumento congelado y censo

- Libro `features/codebook/codebook_v5.xlsx`, versión 0.5.1-candidate, 16
  conceptos (JSON sha256 `5d80a96f…`).
- Prompt `prompts/annotations_prompt_final.md` (sha256 `fa80e6d2…`).
- Censo de 3.609 bloques con `gpt-6-luna`, esfuerzo `max`
  (`pilot_d4e0291b4df3fc0f5343`). El 22 sep quedaron 2.813 respuestas por el
  límite de gasto de OpenAI; los 796 restantes se completaron en Bedrock
  (`pilot_46d9e036e93e09278292`). El 2 oct se completaron también en OpenAI
  (`output/annotations/openai_gpt6luna_20261002`), de modo que el censo usado
  proviene de un solo proveedor.
- Réplica con `claude-haiku-5-5` en Bedrock (8–9 oct;
  `output/annotations/bedrock_haiku55_20261008`), con los mismos requests
  congelados y topes de 65.536 y 128.000 tokens.

El instrumento no se modificó después del censo.

## 4. Validación ciega (pendiente de métricas)
