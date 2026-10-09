## Organización del repositorio

- `data/raw_data/`: fuentes originales descargadas o recopiladas.
- `data/proc_data/`: datos transformados que alimentan los análisis y aplicaciones.
- `features/codebook/`: versiones editables XLSX del libro de códigos y sus JSON derivados.
- `features/manual_validation/`: backend, conversor del libro, comando y frontend de la validación manual.
- `features/discourse_network/`: generación de productos ilustrativos de redes discursivas.
- `output/figures/`, `output/tables/` y `output/validation/`: resultados producidos por el proyecto.
- `_output/`: sitio HTML generado por Quarto; replica únicamente los recursos necesarios para publicar el reporte.
- `review-workspace/`: revisión bibliográfica local; no se versiona.

## Anotación LLM

Los bloques del corpus se anotan con un LLM sobre inputs congelados: un request
por bloque, con el prompt [`prompts/annotations_prompt_final.md`](prompts/annotations_prompt_final.md)
y el libro `features/codebook/codebook_v5.xlsx` (versión interna
`0.5.1-candidate`). Los resultados que respaldan el análisis son el censo de
Luna-6 (`output/annotations/openai_gpt6luna_20261002`) y su réplica con Claude
Haiku 5.5 (`output/annotations/bedrock_haiku55_20261008`). El
[pipeline de anotación](docs/pipeline-anotacion-llm.md) explica preparación,
autorización, ejecución, variables de `.env` y replicación; la
[secuencia de validación](docs/secuencia-validacion-instrumento.md) resume los
pilotos y versiones del instrumento.

```bash
uv sync --locked
# Preparar un input con todos los bloques materializados, sin llamadas a la API:
uv run python -m features.llm_annotations.prepare_all
# Revisar modelo, input, output, códigos destacados y justificaciones:
uv run python -m features.manual_validation
```

Las llamadas exigen una autorización explícita por `run_id` en
`data/proc_data/llm_pilots/api_policy.json`. Abre la opción **Revisión de
anotaciones LLM** en <http://127.0.0.1:8765> o entra directamente en
<http://127.0.0.1:8765/llm.html>. Los inputs de cada ejecución quedan en
`data/proc_data/annotations_inputs/` y sus resultados en `output/annotations/`;
los juicios diagnósticos se guardan por separado en `output/annotation_reviews/`.

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

El [manifiesto de auditoría del primer piloto](data/proc_data/llm_pilots/audits/pilot_f3a69c2f81c587271ef5/manifest.json) resume tokens confirmados y métricas. La política `data/proc_data/llm_pilots/api_policy.json` limita las llamadas a ejecuciones autorizadas explícitamente.
