# Auditoría técnica unificada posterior al pull

Fecha de actualización: 19 de septiembre de 2026
Código remoto integrado: `919760b` (`correcciones afiliaciones`)

## Alcance y método

Esta revisión sustituye la auditoría anterior. Se examinó el código posterior al
`git pull --rebase --autostash` y se conciliaron sus cambios con el trabajo local.
La nueva auditoría cubrió `proc.qmd`, `annotations.qmd`, las features de anotación,
evaluación y validación manual, la procedencia de afiliaciones en el repositorio
hermano `bcn-scraper` y los Parquet de las tres leyes.

Antigravity revisó el delta técnico de la tesis y OpenCode la procedencia de las
afiliaciones. Trabajaron sobre copias acotadas y no editaron los repositorios. Todos
los hallazgos aquí incluidos se contrastaron después con el código y los datos.

## Resultado ejecutivo

El pull resuelve una parte sustantiva del principal problema anterior. El corpus
ahora contiene `party_at_date`, estados explícitos de resolución y esquema
`coding-chunks-2.1.0`. La alineación ya no deriva de `current_party`, sino de la
afiliación coincidente con la fecha del debate. Los casos sin cobertura y aquellos
donde la afiliación no aplica quedan fuera de centro.

La estratificación predeterminada para validación manual queda como
`ley × cámara × alineación × género`. El tipo de actor sigue disponible como
dimensión diagnóstica u optativa. La definición izquierda/derecha se carga desde
`.env`, y su snapshot y hash quedan registrados en nuevas sesiones y runs.

El principal problema crítico vigente es que la política de uso de API sigue siendo
*fail-open*.

## Problemas anteriores resueltos

- `proc.qmd` usa `party_at_date` y `party_at_date_status`.
- Solo `matched` recibe izquierda, derecha o centro; `unknown` se conserva como
  `Sin dato` y `not_applicable` como `No aplica`.
- Ejecutivo y autoridades de cámara no reciben alineación partidaria, incluso si un
  artefacto antiguo contiene un partido.
- Validación manual, evaluación LLM y documentación usan `alignment` en la
  estratificación principal.
- Los merges de afiliación validan cardinalidad; `LAW_NUMBER` se obtiene del entorno
  y se valida; nuevos runs y sesiones congelan la definición de alineación.

## Hallazgos vigentes

### P0-1. Política de API *fail-open*

En `features/llm_annotations/pipeline.py`, la política solo se valida cuando
`execute=True` y el archivo existe. Si falta `api_policy.json`, la ejecución puede
continuar sin ese control.

**Acción:** con `execute=True`, exigir archivo existente, JSON válido y autorización
explícita del run, modelo, esfuerzo y límite antes de crear el cliente.

### P1-1. Artefactos pendientes de regeneración

La precedencia de roles ya está corregida en `proc.qmd`, pero el Parquet actual de la
ley 21.419 contiene 87 bloques de tres actores con rol ministerial y
`party_at_date_status=matched`. Las otras leyes no presentan el caso. La interfaz
quedó blindada para clasificarlos como `No aplica`, pero el corpus debe regenerarse.

### P1-2. Actualizaciones perdidas en validación manual

`ValidationService.save_item` hace lectura-modificación-escritura del JSON completo
bajo `ThreadingHTTPServer`, sin revisión optimista ni bloqueo compartido. Dos pestañas
pueden partir de la misma versión y la última escritura sobrescribir la primera.

**Acción:** ETag o versión por ítem, HTTP 409 y bloqueo por archivo o almacenamiento
transaccional.

### P1-3. Diseños de muestreo divergentes

`annotations.qmd` mantiene su propio muestreo por
`law_number × document_uri`; la interfaz manual usa por defecto
`law_number × chamber × alignment × gender`. La diferencia puede ser intencional, pero no está
formalizada como dos diseños con universos, probabilidades y estimandos distintos.

### P1-4. Estado mutable en `annotations.qmd`

El documento conserva resultados históricos y reutiliza nombres como `results`,
`valid_blocks` y `complete_utterances`. Al reactivar ejecución, una edición puede
mezclar objetos del piloto anterior y del run nuevo. Deben separarse espacios de
nombres y construir el manifiesto desde una especificación inmutable.

### P1-5. Escrituras Parquet no atómicas

Algunas salidas se escriben directamente al destino. Una interrupción puede dejar
un archivo parcial o datos y manifiesto incoherentes. Debe usarse temporal, validación
y reemplazo atómico, publicando el manifiesto al final.

### Hallazgos P2

- El run de anotación no registra explícitamente versión de chunks y todos los
  umbrales de segmentación.
- `SEED + stratum_index` hace depender la muestra del orden de estratos; la semilla
  debe derivarse de una clave canónica.
- Hay controles de integridad basados en `assert` y un render tolerante a errores.
- El merge de `corpus_manifest` en `proc.qmd` aún no declara `validate=`.
- Siguen vigentes en el scraper la decodificación frágil con `unicode_escape`, la
  selección de `results[0]`, `errors="ignore"`, construcción manual de ciertas URLs
  y posibles colisiones de IDs externos. El fallback de `current_party` tampoco es
  cronológico, aunque ya no alimenta la alineación downstream.

## Estado de artefactos

| Ley | Filas | matched | unknown | no aplica | Izq. | Centro | Der. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 21.419 | 844 | 793 | 22 | 29 | 244 | 231 | 318 |
| 21.538 | 326 | 295 | 0 | 31 | 88 | 76 | 131 |
| 21.735 | 2.439 | 2.133 | 29 | 277 | 560 | 812 | 761 |

Los conteos izquierda/centro/derecha incluyen solo afiliaciones `matched`; `Sin dato`
y `No aplica` permanecen separados.

## Conciliaciones realizadas

- La evaluación todavía usaba `party`; se migró a `alignment` y se añadió prueba.
- La precedencia de rol podía asignar partido a ministros; se corrigió en
  procesamiento y se añadió una defensa en la interfaz.
- La tesis y el anexo metodológico ahora describen afiliación histórica y la nueva
  estratificación de forma consistente.
- Los filtros que invalidan runs antiguos al cambiar el hash de fuentes se trataron
  correctamente como control de seguridad, no como defecto.

## Verificación

- Tesis: **65 pruebas aprobadas**.
- `bcn-scraper`: **73 pruebas aprobadas** con `uv run pytest -q`.
- `git diff --check`: aprobado.
- La copia local auditada del scraper no era la versión más reciente que contiene el
  CLI de afiliaciones; por ello no se infieren defectos de reproducibilidad del CLI.
- No hubo llamadas LLM pagadas ni envío del corpus a los agentes delegados.

## Orden recomendado

1. Regenerar los tres corpus con la versión actualizada del CLI y verificar los 87
   bloques indicados.
2. Hacer que la política de API falle cerrada.
3. Añadir control de concurrencia a sesiones manuales.
4. Unificar o formalizar los dos diseños de muestreo.
5. Hacer atómicas las salidas y endurecer contratos de QMD/run.
