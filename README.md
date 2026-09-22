## Organización del repositorio

- `data/raw_data/`: fuentes originales descargadas o recopiladas.
- `data/proc_data/`: datos transformados que alimentan los análisis y aplicaciones.
- `features/codebook/`: versiones editables XLSX del libro de códigos y sus JSON derivados.
- `features/manual_validation/`: backend, conversor del libro, comando y frontend de la validación manual.
- `features/discourse_network/`: generación de productos ilustrativos de redes discursivas.
- `output/figures/`, `output/tables/` y `output/validation/`: resultados producidos por el proyecto.
- `_output/`: sitio HTML generado por Quarto; replica únicamente los recursos necesarios para publicar el reporte.
- `review-workspace/`: configuración, búsquedas, textos convertidos y notas de la revisión bibliográfica.

## Piloto de anotación LLM

`annotations.qmd` sortea el 10% de los bloques elegibles por ley y sesión,
reutiliza el contexto y los controles de la app manual y anota cada bloque objetivo.
Las ejecuciones nuevas usan por defecto `gpt-5.6-luna`, esfuerzo `max` y hasta
cinco intentos totales; `ANNOTATIONS_MODEL` y `ANNOTATIONS_MAX_RETRIES` permiten
escoger el modelo y entre cero y cuatro reintentos desde `.env`. Si una respuesta
agota el límite de salida, el siguiente intento duplica su holgura hasta
`ANNOTATIONS_INCOMPLETE_MAX_OUTPUT_TOKENS` (65.536 por defecto). La configuración
efectiva queda congelada en cada manifiesto. El prompt activo se edita en
[`prompts/annotations_pilot_v1_confidence.md`](prompts/annotations_pilot_v1_confidence.md).
El XLSX vigente es `features/codebook/codebook_v5.xlsx` (versión interna
`0.5.0-candidate`), cerrado para el chequeo final previo a la codificación ciega.

```bash
uv sync --locked
# Renderizar usando solamente resultados guardados:
uv run quarto render annotations.qmd
# Preparar inputs de un piloto nuevo, sin llamadas a la API:
ANNOTATIONS_PREPARE_INPUTS=1 uv run quarto render annotations.qmd
# El reporte no ejecuta la API; las llamadas exigen autorización por run_id.
# Revisar modelo, input, output, códigos destacados y justificaciones:
uv run python -m features.manual_validation
```

Se necesita Quarto CLI en el PATH. Abre la opción **Revisión de anotaciones LLM**
en <http://127.0.0.1:8765> o entra directamente en
<http://127.0.0.1:8765/llm.html>. Los inputs de cada ejecución nueva quedan en
`data/proc_data/annotations_inputs/` y sus resultados en `output/annotations/`.
El piloto histórico autocontenido permanece también bajo `output/annotations/`;
los juicios diagnósticos se guardan por separado en `output/annotation_reviews/`.
La [guía del piloto](docs/piloto-anotaciones-llm.md)
explica ejecución, variantes y límites de interpretación.

La variable `PARTY_ALIGNMENT` de `.env` contiene cuatro listas explícitas:
`left`, `center`, `right` y `nonpartisan`. El procesamiento y la validación
manual usan la misma definición; un partido no enumerado queda como
`unclassified`, nunca se imputa a `centro`. Copia el formato de `.env.example`
al configurar un entorno nuevo.

Las afiliaciones históricas sin resultado automático se revisan en
[`data/curation/party_at_date_overrides.csv`](data/curation/party_at_date_overrides.csv).
Una fila `confirmed` o `nonpartisan` exige partido, URL y nota de evidencia,
persona revisora y fecha; las filas `pending` no alteran el corpus. El
procesamiento conserva la extracción de BCN y aplica estas decisiones solo a la
tabla derivada de discursos.

El [manifiesto del análisis del piloto](data/proc_data/llm_pilots/pilot_f3a69c2f81c587271ef5/manifest.json) resume tokens confirmados y métricas. La política `data/proc_data/llm_pilots/api_policy.json` limita las llamadas a ejecuciones autorizadas explícitamente.
