# Plan de implementación técnica de la pipeline audiovisual legislativa

**Versión:** 2026-08-21  
**Estado:** diseño condicionado, con identificación biométrica suspendida  
**Repositorio de implementación previsto:** `../../CENIA/reportes-congreso-imfd` desde la raíz de la tesis  
**Proyecto de ley principal:** boletín 15480-13, Ley N.º 21.735

## 1. Propósito y decisión pendiente

La pipeline debe convertir grabaciones de sesiones legislativas en turnos de habla trazables, delimitados temporalmente y atribuidos a actores. El producto analítico alimentaría la extracción de declaraciones para análisis de redes discursivas.

El diseño privilegia la precisión de la atribución. Una identidad errónea modifica las aristas actor-concepto y puede alterar la estructura de las coaliciones. Los casos inciertos conservarán un identificador `unknown` estable.

La tesis todavía carece de autorización o exención del Comité de Ética de la Investigación de FACSO. Por esta razón se aplican dos gates:

- **Gate E0, vigente:** se permite trabajar con manifiestos, medios públicos, ASR, diarización intrasesión, OCR y hablantes seudónimos. Queda suspendida la creación de nuevas plantillas vocales persistentes vinculadas a personas.
- **Gate E1:** la identificación biométrica entre sesiones se habilitará después de obtener una autorización, modificación o exención escrita que cubra el tratamiento, almacenamiento, retención y eventual eliminación de embeddings de voz.

El CEI debe determinar si corresponde evaluación o exención. Los lineamientos ANID contemplan posibles exenciones para investigación con registros públicos e identidades de personas que ejercen cargos públicamente reconocidos, y asignan al comité la decisión final. La Ley 21.719, con vigencia desde el 1 de diciembre de 2026, incluye la voz entre los datos biométricos cuando un tratamiento técnico permite la identificación única.

Referencias institucionales:

- [Evaluación de proyectos del CEI FACSO](https://facso.uchile.cl/facultad/comites/comite-de-etica-de-la-investigacion/evaluacion-de-proyectos-)
- [Lineamientos ANID para investigación en Ciencias Sociales y Humanidades](https://facso.uchile.cl/dam/jcr%3A6e883914-4e8b-4ec7-b4c9-3680ec781d35/Lineamientos-evaluacion-etica_Cs_Sociales_-_ANID_2022.pdf)
- [Ley 21.719 sobre protección y tratamiento de datos personales](https://www.bcn.cl/leychile/Navegar?idNorma=1209272&idParte=10527471&idVersion=2026-12-01)

## 2. Alcance

### 2.1 Cobertura institucional

El universo previsto comprende:

- Cámara de Diputadas y Diputados, Comisión de Trabajo: 32 sesiones esperadas.
- Cámara de Diputadas y Diputados, Comisión de Hacienda: 6 jornadas esperadas.
- Senado, Comisión de Trabajo y Previsión Social: 41 sesiones registradas.
- Senado, Comisión de Hacienda: 9 sesiones registradas.

El universo preliminar suma 88 sesiones técnicas. Cada relación entre sesión documental y grabación debe verificarse porque una sesión puede tener varias partes y una grabación puede cubrir más de una jornada.

### 2.2 Contenido incluido

Se incluirán los intervalos en que se discute el boletín 15480-13. Una sesión dedicada enteramente al proyecto podrá declararse `full_session`. Las sesiones multitemáticas tendrán uno o más intervalos `bill_segment`.

La salida analítica incluirá:

- turnos de habla con timestamps de inicio y término;
- texto del turno;
- cluster de hablante intrasesión;
- identidad del actor cuando exista evidencia suficiente y autorización aplicable;
- tipo de actor: parlamentario, Ejecutivo, invitado, organización o desconocido;
- evidencia y versión del procedimiento de atribución;
- cámara, comisión, sesión, etapa y fecha.

### 2.3 Contenido excluido

Quedan fuera de la salida analítica principal:

- timestamps por palabra;
- aplausos y eventos ambientales;
- solapamientos sin contenido inteligible;
- intervenciones fuera de micrófono que el ASR no pueda recuperar;
- scores técnicos en la tabla de análisis;
- intervalos de otros proyectos de ley.

Los scores de matching, márgenes entre candidatos y diagnósticos permanecerán en tablas internas de control de calidad.

## 3. Principios de diseño

1. **Trazabilidad:** cada turno debe remontarse a una sesión, archivo, checksum e intervalo.
2. **Idempotencia:** repetir una etapa con los mismos insumos y configuración debe reutilizar resultados válidos.
3. **Checkpoints:** cada sesión y etapa tendrá un estado persistente compatible con el límite de 24 horas de SLURM.
4. **Identidad canónica:** los parlamentarios usarán `PersonaBCN`. Los IDs locales de Akoma Ntoso se conservarán únicamente como procedencia.
5. **Identificación abierta:** una persona ausente del registro debe poder quedar como `unknown`.
6. **Separación de tareas:** ASR, diarización, reconciliación de clusters e identificación se evaluarán por separado.
7. **Revisión dirigida:** la intervención manual se concentrará en asociaciones ambiguas, límites del boletín, piloto y atribuciones inciertas.
8. **Versionamiento:** código, modelos, prompts, configuraciones y correcciones manuales tendrán versiones registradas.

## 4. Arquitectura propuesta

El código existente se generalizará en el repositorio `reportes-congreso-imfd`. La estructura objetivo es:

```text
src/congreso_media/
  cli.py
  config.py
  manifest/
    schema.py
    store.py
    validation.py
  sources/
    senado.py
    camara.py
    attendance.py
  media/
    download.py
    probe.py
    audio.py
    frames.py
  scope/
    bill_segments.py
    keywords.py
  asr/
    base.py
    whisper.py
    vibevoice.py
  diarization/
    base.py
    pyannote.py
    reconcile.py
  identity/
    registry.py
    enrollment.py
    candidates.py
    matching.py
    calibration.py
  review/
    label_studio.py
    contact_sheets.py
    adjudication.py
  export/
    turns.py
    dna_input.py
    provenance.py
```

Los módulos actuales de `senado_scraping` y `diputados_scraping` se reutilizarán durante la migración. Los scripts de `scripts/` actuarán como comandos delgados que llaman a funciones de `src/`.

## 5. Contratos de datos

### 5.1 `sessions.parquet`

Una fila representa una sesión documental esperada.

```text
session_id
chamber
commission
session_date
start_time_expected
session_kind
legislative_stage
bill_number
source_page_url
citation_url
report_document_uri
attendance_source
manifest_status
review_status
```

`session_id` debe ser estable y legible:

```text
camara__trabajo__2023-01-10__special__am
senado__hacienda__2025-01-22__pm
```

### 5.2 `media_assets.parquet`

Una fila representa un archivo o stream vinculado a una sesión.

```text
asset_id
session_id
source_url
resolved_media_url
media_kind
part_number
duration_sec
bytes
sha256
ffprobe_json_path
downloaded_at
validation_status
local_path
```

### 5.3 `attendance.parquet`

```text
session_id
actor_id
actor_name
actor_type
attendance_role
replacement_for
valid_from
valid_to
source_url
resolution_status
```

Los parlamentarios se expresarán como `bcn:<PersonaBCN>`. Invitados y organizaciones usarán `ext:<uuid>`. La identificación pendiente usará `unk:<session_id>:<cluster_id>`.

### 5.4 `bill_segments.parquet`

```text
session_id
segment_id
start_ms
end_ms
scope_status
scope_evidence
review_status
```

### 5.5 `turns.parquet`

```text
turn_id
session_id
asset_id
segment_id
start_ms
end_ms
text
speaker_cluster_id
actor_id
actor_type
identity_status
attendance_status
asr_run_id
diarization_run_id
identity_run_id
manual_revision_status
```

### 5.6 Tablas internas de control

```text
asr_runs.parquet
diarization_runs.parquet
speaker_candidates.parquet
identity_scores.parquet
manual_decisions.parquet
pipeline_events.parquet
```

Estas tablas deben conservar modelos, revisiones, configuraciones, errores y duración de los trabajos.

## 6. Etapas de implementación

## Fase 0. Decisión, ética e inventario

### Tareas

1. Consultar al CEI si corresponde exención, evaluación expedita o modificación.
2. Especificar la finalidad del matching de voz, acceso, retención, eliminación y publicación.
3. Inventariar los embeddings `.pt` y clips de referencia ya existentes.
4. Restringir el acceso al inventario existente y registrar quién puede leerlo.
5. Suspender nuevas incorporaciones al registro de voces durante Gate E0.
6. Decidir si el video forma parte del corpus de la tesis o queda como extensión futura.

### Entregables

- registro de decisión ética;
- inventario de datos biométricos existentes;
- plan de gestión y eliminación;
- decisión `continue`, `defer` o `discard_for_thesis`.

### Criterio de salida

La pipeline biométrica avanza cuando existe una determinación escrita y el plan de datos cumple sus condiciones.

## Fase 1. Consolidación del repositorio

### Tareas

1. Separar dependencias de scraping, ASR ROCm, ASR CUDA y anotación.
2. Evitar que el entorno AMD instale paquetes CUDA de NVIDIA.
3. Añadir `requests-mock` y demás dependencias de test faltantes.
4. Introducir configuración por YAML con rutas fuera de `home`.
5. Migrar funciones comunes de descarga, naming, `ffprobe` y manifiestos a `congreso_media`.
6. Mantener adaptadores de compatibilidad para los scripts actuales.

### Entregables

- entornos bloqueados y documentados;
- suite de tests ejecutable;
- CLI inicial;
- configuración de desarrollo, Antuco y Llaima.

### Criterio de salida

Los tests unitarios pasan en CPU y los smoke tests de ambos entornos GPU terminan dentro de la cola `debug`.

## Fase 2. Manifiesto audiovisual

### Senado

1. Importar las URLs documentadas en `videos.md`.
2. Resolver el MP4 o registrar el tipo alternativo de fuente.
3. Detectar duplicados por URL, ID de video y checksum.
4. Vincular asistencia por fecha y duración.
5. Marcar asociaciones ambiguas para revisión.

### Cámara

1. Parsear las fechas consignadas en los informes de Trabajo y Hacienda.
2. Crear el ledger de 38 sesiones esperadas.
3. Enumerar páginas `citacion_detalle.aspx` de las comisiones.
4. Enumerar candidatos del archivo de televisión por fecha.
5. Resolver la URL directa del MP4.
6. Calcular un score de vinculación con fecha, comisión, jornada, título y duración.
7. Enviar empates y faltantes a revisión manual.

### Estados permitidos

```text
confirmed
probable
ambiguous
missing_video
missing_citation
excluded
```

### Criterio de salida

Cada sesión esperada tiene un video confirmado, una ambigüedad visible, una exclusión justificada o un estado de ausencia documentado.

## Fase 3. Adquisición y normalización de medios

### Tareas automatizadas

1. Descargar con archivo temporal `.part`.
2. Validar respuesta HTTP, tamaño y duración.
3. Calcular SHA-256.
4. Guardar salida completa de `ffprobe`.
5. Extraer audio FLAC o WAV mono de 16 kHz.
6. Generar keyframes en cambios de escena y alrededor de nombres en pantalla.
7. Registrar todos los artefactos en `media_assets`.

### Formatos

- MP4 como fuente temporal.
- FLAC mono de 16 kHz como audio canónico cuando permita simplificar almacenamiento.
- WAV mono de 16 kHz como entrada cuando un modelo lo requiera.
- JPEG o WebP para keyframes de revisión.

### Criterio de salida

El audio reproduce la duración del medio dentro de una tolerancia definida, el checksum está registrado y la extracción puede repetirse desde la fuente.

## Fase 4. Delimitación del boletín

### Tareas

1. Ejecutar un ASR preliminar sobre la sesión completa.
2. Detectar menciones a `15480-13` y vocabulario específico de la reforma.
3. Combinar las detecciones con agenda, informe y acta.
4. Proponer intervalos contiguos.
5. Declarar `full_session` cuando toda la grabación corresponde al proyecto.
6. Revisar manualmente límites ambiguos.

### Criterio de salida

Cada medio tiene intervalos revisados o evidencia suficiente para considerarlo completo.

## Fase 5. Spike de modelos

### Entorno principal

- Nodo Antuco.
- 2 AMD Instinct MI210 de 64 GB.
- ROCm 7.2.3.
- Un job por GPU.

### Modelos candidatos

- Whisper large-v3-turbo para ASR principal.
- Whisper large-v3 como referencia de calidad.
- pyannote Community-1 para diarización, sujeto a compatibilidad ROCm.
- VibeVoice-ASR-7B como baseline conjunto, sujeto a compatibilidad local.

### Fallback

Llaima, con A40 de 48 GB, se usará cuando una dependencia solo funcione de manera confiable con CUDA.

### Diseño del benchmark

Seleccionar 20 minutos de cuatro condiciones:

- Senado con audio limpio;
- Senado con invitados;
- Cámara con cambios frecuentes de hablante;
- audio difícil o sesión remota.

Medir:

- tiempo de procesamiento por hora de audio;
- memoria GPU máxima;
- fallos y compatibilidad;
- calidad descriptiva del texto;
- pureza y fragmentación de clusters;
- facilidad de alineación ASR-diarización.

### Criterio de salida

Se elige un stack reproducible que cabe en una GPU, completa una unidad de trabajo dentro de 24 horas y produce artefactos alineables.

## Fase 6. ASR, diarización y continuidad de clusters

### ASR

1. Procesar los intervalos del boletín.
2. Conservar timestamps de segmento.
3. Utilizar hotwords con nombres y términos previsionales cuando el modelo lo permita.
4. Guardar salida nativa y salida normalizada.

### Diarización

1. Estimar actividad de voz y clusters locales.
2. Utilizar asistencia para informar límites plausibles de hablantes, sin forzar el número exacto.
3. Excluir solapamientos no inteligibles de la salida analítica.

### Reconciliación entre chunks

1. Extraer varias muestras limpias por cluster.
2. Comparar clusters de chunks solapados.
3. Unir clusters según similitud, continuidad temporal y evidencia del solapamiento.
4. Resolver conflictos con clustering a nivel de sesión.
5. Asignar un `speaker_cluster_id` único por sesión.

Los IDs de diarización por chunk son temporales. La salida final conserva clusters a nivel de sesión.

### Criterio de salida

El piloto alcanza al menos 95 % de pureza dentro de los clusters evaluados y conserva todos los turnos sustantivos identificables.

## Fase 7. Registro de actores y firmas vocales

**Esta fase requiere Gate E1.**

### Registro de identidades

Cada parlamentario se vinculará a su `PersonaBCN`. El registro debe reflejar el período de servicio y evitar listas basadas únicamente en la composición de 2026.

```text
actor_id
canonical_name
actor_type
service_period_start
service_period_end
source_clip_id
source_url
start_ms
end_ms
embedding_model
model_revision
human_validated
quality_flags
retention_status
```

### Construcción de referencias

1. Validar manualmente la identidad del clip.
2. Extraer varios segmentos sin mezcla de voces.
3. Registrar procedencia y calidad de cada segmento.
4. Calcular embeddings por segmento.
5. Agregar referencias de manera robusta.
6. Conservar las muestras por separado para auditoría durante el período aprobado.

Una firma validada podrá reutilizarse. Una persona puede necesitar referencias adicionales cuando cambien micrófono, modalidad o calidad acústica.

## Fase 8. Identificación abierta de hablantes

**Esta fase requiere Gate E1.**

### Generación de candidatos

El conjunto por sesión reunirá:

- asistencia confirmada;
- reemplazos con rangos horarios;
- miembros oficiales de la comisión;
- ministros e invitados informados;
- actores detectados por OCR o presentación verbal.

### Regla de matching

La decisión combinará:

- score del primer candidato;
- margen entre primer y segundo candidato;
- consistencia entre segmentos del cluster;
- asistencia y rango horario;
- evidencia de nombre en pantalla;
- atribuciones manuales previas.

El umbral fijo actual de 0,57 se reemplazará por parámetros calibrados con ground truth local.

### Estados de identidad

```text
auto_accepted
human_confirmed
unknown_low_score
unknown_low_margin
unknown_not_in_registry
conflict_attendance
conflict_visual
```

### Criterios de aceptación del piloto

- precisión de al menos 97 % entre identidades autoaceptadas;
- error de identidad inferior a 2 % de la duración atribuida;
- reporte separado de cobertura y desconocidos;
- revisión de todos los conflictos y de una muestra de aceptaciones.

## Fase 9. Revisión humana

### Interfaz

Adaptar el flujo actual de Label Studio para mostrar:

- video o audio sincronizado;
- turno y cluster;
- candidatos ordenados;
- score y margen internos;
- asistencia;
- keyframes y OCR;
- opción de identidad nueva o `unknown`;
- historial de decisiones.

### Trabajo manual esperado

- resolver relaciones sesión-video ambiguas;
- confirmar límites del boletín;
- anotar el piloto;
- validar nuevas referencias vocales después de Gate E1;
- revisar scores bajos, márgenes estrechos y contradicciones;
- auditar una muestra aleatoria.

La corrección exhaustiva del texto queda fuera del procedimiento. El investigador podrá corregir errores que cambien el sentido de una declaración o impidan aplicar el libro de códigos.

## Fase 10. Procesamiento masivo

### Unidad de trabajo

Una tarea de SLURM procesa una sesión y una etapa. Los jobs independientes permiten usar ambas MI210 y reanudar fallos.

### Estados por sesión

```text
manifest_validated
media_downloaded
audio_validated
scope_validated
asr_completed
diarization_completed
clusters_reconciled
identity_completed
review_completed
exported
```

### Estrategia SLURM

- `debug`, una hora: instalación, smoke tests y profiling.
- `regular`, 24 horas: procesamiento por sesión.
- un job por GPU;
- job arrays con concurrencia limitada por capacidad del nodo;
- checkpoints después de cada etapa;
- logs separados por job y sesión;
- copia atómica de resultados al almacenamiento compartido.

## Fase 11. Exportación al análisis

### Transformaciones

1. Ordenar turnos por sesión y tiempo.
2. Normalizar espacios y artefactos del ASR.
3. Mantener el texto literal y una versión corregida cuando exista revisión.
4. Excluir eventos ambientales.
5. Conservar `unknown` estables.
6. Vincular actores con metadatos históricos.
7. Exportar a un esquema análogo a `speech_df`.

### Artefactos finales

```text
sessions.parquet
attendance.parquet
bill_segments.parquet
turns.parquet
actors.parquet
pipeline_provenance.json
quality_report.csv
manual_decisions.parquet
```

### Criterio de salida

Cada turno utilizado en DNA posee fuente, sesión, intervalo, texto, actor o `unknown`, y versiones de los modelos que lo produjeron.

## 7. Almacenamiento y ciclo de vida

| Espacio | Uso previsto |
|---|---|
| `home`, 50 GB | código, configuraciones y archivos pequeños |
| `scratch`, 500 GB | staging compartido, medios e intermedios regenerables |
| `workspace`, 200 GB por nodo | modelos, audio y procesamiento activo de alto I/O |
| `archive`, 200 GB | manifiestos, resultados finales, métricas y artefactos aprobados |

### Flujo de archivos

1. Descargar o copiar el medio a `scratch`.
2. Preparar entradas y pesos en `$WORKSPACE` del nodo asignado.
3. Procesar localmente en `$WORKSPACE`.
4. Copiar resultados completos a `scratch` con nombre temporal.
5. Renombrar al nombre definitivo después de validar integridad.
6. Consolidar en `archive` los resultados que deben preservarse.
7. Limpiar workspace e intermedios regenerables.

Las cachés de Hugging Face, PyTorch y modelos deben apuntar a `workspace` o `scratch`. El `home` no debe almacenar pesos ni medios.

### Eliminación de medios

El MP4 puede eliminarse después de verificar:

- URL y fecha de recuperación;
- checksum, tamaño y duración;
- audio extraído;
- keyframes requeridos;
- resultados de ASR y diarización;
- posibilidad técnica y jurídica de volver a descargar.

La retención de embeddings y clips de referencia seguirá la determinación del CEI.

## 8. Verificación y tests

### Tests unitarios

- parsing de fechas y jornadas;
- generación estable de IDs;
- resolución de URLs;
- detección de duplicados;
- validación de esquemas;
- cálculo de checksums;
- parsing de SRT y JSON;
- alineación de timestamps;
- reglas de estados y checkpoints;
- generación de candidatos por asistencia.

### Tests de integración

- una sesión Senado completa;
- una sesión Cámara completa;
- una sesión con varias partes;
- una sesión multitemática;
- un video faltante;
- dos sesiones en la misma fecha;
- reanudación después de un fallo simulado.

### Evaluación metodológica

- muestra manual separada para desarrollo y evaluación final;
- métricas de diarización y atribución por duración;
- precisión, sensibilidad y F1 de identidad;
- tasa y composición de `unknown`;
- errores por cámara, actor, modalidad y calidad de audio;
- sensibilidad de la red discursiva a identidades inciertas.

Las preanotaciones automáticas no cuentan como ground truth. Una anotación validada debe registrar autor, fecha, estado y cambios respecto de la predicción.

## 9. Reproducibilidad y publicación

Se conservarán:

- commit del código;
- configuración completa;
- revisión exacta de cada modelo;
- versiones de ROCm, driver, PyTorch y dependencias;
- manifests, checksums y estados de exclusión;
- selección y protocolo del piloto;
- instrucciones de anotación;
- decisiones manuales;
- métricas por etapa;
- declaración ética o exención;
- declaración de disponibilidad de datos.

La publicación puede compartir código, esquemas, configuración, resultados derivados y una muestra permitida. La disponibilidad de audio, video, clips y embeddings dependerá de derechos de uso y condiciones éticas.

## 10. Matriz de automatización

| Etapa | Automatización | Revisión humana |
|---|---:|---:|
| Extraer sesiones esperadas | alta | fechas ambiguas |
| Resolver video y ficha | alta | empates y faltantes |
| Descargar y validar | alta | fallos excepcionales |
| Delimitar boletín | media | límites dudosos |
| ASR | alta | muestra de evaluación |
| Diarización | alta | piloto y clusters problemáticos |
| Reconciliar chunks | alta | conflictos del piloto |
| Construir firmas | media | cada nueva identidad |
| Identificar actores | alta | casos inciertos |
| Corregir transcripción | baja | errores sustantivos |
| Exportar | alta | auditoría final |

## 11. Riesgos y mitigaciones

| Riesgo | Consecuencia | Mitigación |
|---|---|---|
| Falta de autorización CEI | bloqueo de identificación biométrica y publicación | solicitar determinación escrita y mantener Gate E0 |
| Archivo histórico de Cámara incompleto | sesiones sin medio | ledger de sesiones esperadas y faltantes explícitos |
| pyannote falla en ROCm | retraso de diarización | fallback CUDA en Llaima |
| VibeVoice depende de CUDA o endpoint externo | falta de reproducibilidad | modelo local modular como ruta principal |
| IDs cambian entre chunks | hablantes fragmentados | reconciliación a nivel de sesión |
| Umbral de matching sin calibrar | atribuciones falsas | ground truth local, score y margen |
| Padrón de 2026 aplicado a sesiones históricas | candidatos incorrectos | registro por período y `PersonaBCN` |
| Jobs exceden 24 horas | resultados perdidos | unidad por sesión, checkpoints e idempotencia |
| Saturación de `home` | bloqueo de acceso al cluster | cachés y medios fuera de `home` |
| Revisión manual crece sin control | incumplimiento de plazos | política conservadora de `unknown` y revisión dirigida |

## 12. Gates de decisión para la tesis

### Opción A. Descartar video del corpus central

Acciones:

1. Actualizar `thesis.md` para declarar cuatro sesiones de Sala.
2. Reformular el alcance como discurso parlamentario plenario.
3. Ajustar hipótesis temporales y modelos que dependen de 92 sesiones.
4. Conservar este plan como extensión futura.
5. Inventariar y gestionar los embeddings ya producidos según la respuesta del CEI.

Esta opción concentra el trabajo de 2026 en libro de códigos, validación LLM, anotación, indicadores y escritura.

### Opción B. Mantener un piloto audiovisual metodológico

Acciones:

1. Seleccionar cuatro sesiones.
2. Ejecutar ASR y diarización bajo Gate E0.
3. Medir costo y calidad.
4. Excluir los resultados del corpus principal mientras la identidad permanezca incompleta.
5. Presentar el piloto como prueba de factibilidad futura, sujeto a evaluación ética.

### Opción C. Incorporar las 88 sesiones

Prerrequisitos:

- determinación CEI compatible con identificación de hablantes;
- manifiesto Cámara completo;
- piloto con precisión de identidad suficiente;
- tiempo reservado para revisión;
- congelamiento del libro de códigos y de la validación LLM sin competir por los mismos plazos.

## 13. Estimación de esfuerzo si se reactiva

| Bloque | Duración activa estimada |
|---|---:|
| Consolidación de entornos y tests | 3 a 5 días |
| Manifiesto histórico de Cámara y Senado | 4 a 8 días |
| Spike de modelos | 2 a 4 días |
| Piloto y anotación | 5 a 8 días |
| Registro de voces y calibración | 5 a 10 días después de Gate E1 |
| Procesamiento masivo | 5 a 10 días de calendario |
| Revisión y exportación | 5 a 10 días |

La ruta completa requiere aproximadamente cuatro a siete semanas de trabajo activo, además del tiempo de respuesta ética. Las estimaciones deben actualizarse con el piloto.

## 14. Recomendación operativa actual

La ausencia de autorización CEI y la carga restante de la tesis favorecen la **Opción A** para el corpus principal. La **Opción B** conserva valor si el piloto sirve como contribución metodológica independiente y no retrasa el libro de códigos, los experimentos con LLM y la validación manual.

La **Opción C** debe reabrirse después de contar con una resolución ética y tiempo suficiente para validar atribuciones. El manifiesto y la arquitectura aquí definidos permiten retomar el trabajo sin convertir el prototipo actual en evidencia analítica prematura.
