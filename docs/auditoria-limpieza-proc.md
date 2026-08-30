# Auditoría de limpieza de `proc.qmd` y sus artefactos

Fecha de revisión: 2026-08-29.

Esta auditoría distingue archivos obsoletos, diagnósticos reproducibles y cachés costosos. No se eliminó ningún archivo. Las recomendaciones se basan en los consumidores actuales del repositorio, el contenido de `proc.qmd` y la inspección de los Parquet vigentes.

## Archivos que se pueden borrar ahora

| Archivo o directorio | Evidencia | Recomendación |
|---|---|---|
| `data/proc_data/datos_bcn_akn_speech.json` | Tiene 31.243.083 bytes, fue producido por una versión antigua de `proc.qmd` y ya no es leído por el reporte, las pruebas ni la validación manual. | Borrar. Su reemplazo vigente es la secuencia reproducible que termina en `speech_df.parquet` y `speech_df_full.parquet`. |
| `data/proc_data/datos_normalizados.json` | Tiene 21.883.477 bytes. La exportación JSON dejó de formar parte del reporte; la normalización actual permanece en memoria y se materializa en Parquet. | Borrar. Entre ambos JSON obsoletos se liberan aproximadamente 50,7 MiB. |
| `data/proc_data/speaker_candidates_pending.parquet` | Contiene cero filas. Los 138 candidatos presentes en `speaker_candidates.parquet` aparecen como `resolved` en `output/tables/speaker_candidate_progress.csv`. | Borrar la copia actual. Si se refresca el corpus, `proc.qmd` puede regenerarla para detectar pendientes nuevos. |
| `scripts/__pycache__/`, `shared/__pycache__/` y sus carpetas vacías | Solo contienen bytecode ignorado por Git. Los módulos fuente ya fueron movidos a sus features. | Borrar localmente cuando quieras que desaparezcan físicamente `scripts/` y `shared/`. En el árbol versionado ya no forman parte de la estructura. |
| `.pytest_cache/`, `.quarto/quarto-session-temp*` y `.cache/literature-review/` | Son cachés locales regenerables. La caché bibliográfica inspeccionada ocupa cerca de 0,5 MiB. | Borrar cuando necesites despejar el workspace; no contienen resultados canónicos. |

## Duplicados que conviene simplificar en una segunda pasada

`proc.qmd` genera algunos diagnósticos en Parquet bajo `data/proc_data` y simultáneamente en CSV bajo `output/tables`. Ninguno de esos archivos se vuelve a leer en el pipeline actual; el cálculo posterior utiliza los dataframes en memoria.

| Diagnóstico | Copias actuales | Propuesta |
|---|---|---|
| Auditoría de identidades AKN | `speaker_identity_audit.parquet` y `speaker_identity_audit.csv` | Conservar el Parquet si se prevén cruces programáticos; conservar el CSV si prima la revisión manual. No hace falta mantener ambos indefinidamente. |
| Brechas de atributos parlamentarios | `parliamentarian_identity_gaps.parquet` y `parliamentarian_identity_gaps.csv` | Conservar el CSV en `output/tables`; el Parquet es prescindible mientras ningún proceso externo lo consuma. La tabla aún tiene 40 filas, por lo que el diagnóstico no está resuelto. |
| Reporte de calidad del corpus | `speech_quality_report.parquet` y `speech_quality_report.csv` | Conservar el CSV en `output/tables`; sigue mostrando una advertencia de contenido no resuelto en 2.4 y por eso el reporte mismo no es obsoleto. La copia Parquet sí es opcional. |

`speaker_candidates.parquet` también es un diagnóstico y no un insumo posterior, pero conviene conservarlo al menos hasta cerrar la depuración de identidades: documenta los 138 marcadores resueltos y permite auditar cómo se llegó al diccionario vigente.

## Elementos obsoletos o redundantes dentro de `proc.qmd`

1. **Ejemplos de diccionarios de `market_justice` y `political_justice`.** Presentan AFP, reparto y otros instrumentos como conceptos. Esa lógica contradice la decisión metodológica vigente de codificar justificaciones normativas y no nombres de políticas. Conviene retirar esos dos chunks y reemplazarlos, si se necesita un ejemplo, por una declaración codificada con el libro actual.

2. **Redacción tentativa del enfoque.** El resumen todavía dice que probablemente se usarán *discourse coalitions* y que la teoría auxiliar está por definir. Esa decisión ya fue tomada y existe un libro operacional v0.3.0-pilot; corresponde actualizar la prosa, no conservarla como incertidumbre abierta.

3. **Variables sin consumidores.** `import json`, `dict_normalized`, `candidates` y `dict_normalized_full` no intervienen en ninguna transformación, validación ni escritura posterior. Se pueden retirar sin alterar los outputs.

4. **Ejemplo estático de Jeannette Jara.** El bloque de diccionarios escrito a mano reproduce una estructura antigua y no prueba el dataframe vigente. Conviene sustituirlo por una vista derivada de `data_normalized_full` o eliminarlo si la ilustración ya no aporta al reporte.

5. **Encabezados vacíos al final.** Las secciones sobre comisiones técnicas, videos, ASR, matching e identificación no contienen procesamiento. Esa planificación ya está desarrollada en `docs/plan-implementacion-pipeline-audiovisual.md`; los encabezados se pueden retirar de `proc.qmd` para evitar la apariencia de pasos incompletos.

6. **Rama del mensaje inicial.** `data_message` solo produce `corpus_mensaje_inicial.parquet` y no alimenta el corpus de validación. No es obsoleta por contenido —el propio reporte atribuye alta relevancia al mensaje—, pero es una rama dormida. Si el mensaje no se analizará en la tesis, se pueden retirar ambos; si se analizará, deben conservarse y conectarse a una feature explícita.

7. **Materialización de `corpus_sala.parquet`.** El reporte continúa desde `data_analysis` en memoria, de modo que este Parquet no es indispensable para el render actual. Sin embargo, es un checkpoint pequeño y útil para depurar la extracción; lo conservaría hasta separar el procesamiento en un módulo Python.

## Archivos que deben conservarse

- `data/raw_data/`: es la capa de procedencia y no debe limpiarse como si fuera un resultado temporal.
- `data/proc_data/datos_bcn_akn.csv`: es el caché persistido que evita repetir la descarga y depuración lenta de BCN.
- `data/proc_data/corpus_manifest.csv`: define manualmente el corpus esperado y valida títulos y fechas.
- `data/proc_data/parliamentarians.parquet`: evita repetir el enriquecimiento remoto de aproximadamente una hora y se lee explícitamente al construir el corpus.
- `data/proc_data/speech_df.parquet`: es el corpus analítico consumido por la validación manual.
- `data/proc_data/speech_df_full.parquet`: conserva votaciones, preámbulos y texto excluido para trazabilidad y auditoría.
- `output/validation/`: contiene las rondas humanas y no es un caché regenerable.
- `data/codebook/`: conserva las versiones del instrumento y sus derivados sincronizados.

## Refactor posterior recomendado

El siguiente paso razonable es trasladar la lógica ejecutable de extracción y normalización a una feature `features/corpus_processing/`, dejando `proc.qmd` como reporte reproducible que importa funciones, presenta invariantes y muestra resultados. No lo hice en esta reorganización porque requiere decidir la interfaz entre etapas y probar la reconstrucción completa del corpus, mientras que el objetivo actual era mover los módulos existentes sin cambiar el comportamiento analítico.
