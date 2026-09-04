# Auditoría técnica y hoja de ruta

Estado de `proc.qmd`, sus artefactos y `../bcn-scraper`. Las tareas pendientes están ordenadas de menor a mayor complejidad.

## Resuelto

- Los refrescos costosos de Historia de la Ley y parlamentarios siguen con `eval: false`; el procesamiento sobre caché renderiza en unos 8 segundos.
- `data/proc_data/corpus_manifest.csv` declara las cuatro discusiones en Sala y, por separado, el mensaje inicial. Informes y oficios no entran al corpus discursivo.
- **Auditoría de identidades:** los `perN`/`PersonaAutN` son locales al documento, no IDs de persona. En 487 referencias AKN, 137 IDs locales se reutilizan para personas distintas y 109 personas estables cambian de ID entre documentos. No hay un ID local ambiguo dentro de un mismo AKN ni un `speaker_href` con nombres incompatibles. El cruce queda en `speaker_identity_audit.parquet/csv`.
- La resolución usa `override por documento → href estable de Persona BCN → nombre completo del preámbulo → registro AKN del corpus → manual/regex`. Los alias del Senado ya no se propagan a diputados homónimos de 3.1 (`ARAYA`, `MOREIRA`, `OSSANDÓN`, `GUZMÁN`, etc.). Se corrigió además “Miguel Landeros Perki?” a **Miguel Landeros Perkic** en la salida.
- **Punto 6:** los 138 apellidos/marcadores están resueltos; 13 representan legítimamente a más de una persona según documento u ocurrencia. `speaker_candidates_pending.parquet` tiene cero filas y el reporte ya no confunde homónimos resueltos con conflictos.
- **Punto 5:** 3.1 se recupera desde `xml_content`, sin usar `lost_akn.xml`. El fragmento BCN ya corresponde al boletín 15480-13 en Orden del Día y el parser separa `Discusion` de `Votacion`. La discusión aporta 196 intervenciones, 69.282 palabras y 131 personas; la votación queda solo en `speech_df_full`.
- La cobertura de 3.1 es exacta: 2.765 párrafos útiles de origen, 2.765 observados, sin pérdidas ni duplicados. `speech_df.parquet` conserva 774 intervenciones y 252 eventos de transcripción (1.026 filas); `speech_df_full.parquet` tiene 1.499 filas e incorpora además preámbulos, texto no resuelto y votación para auditoría.
- **Identificadores y orden (punto 7):** `speaker_id` es canónico (`PersonaBCN<id>` o `PersonaExt<n>`), `speaker_bcn_id` guarda el número BCN y `speaker_local_id(s)`/`speaker_local_refs` preservan los IDs AKN locales con su documento. `utterance_id` es único y compartido entre vistas; `utterance_order` mantiene la secuencia, incluidos aplausos y manifestaciones. No se separaron eventos e intervenciones en tablas distintas: `speech_df` es la vista analítica de una única tabla base.
- **Punto 4:** el reporte de calidad controla también las fases del fallback, IDs estables y unicidad de unidades. `1.1`, `1.12`, `1.13` y `3.1` pasan; `2.4` conserva una advertencia procedimental conocida. `bcn-scraper` pasa 72 tests.

## Pendientes
