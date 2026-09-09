# Repositorio para desarrollo de tesis

Este repositorio incluirá todos los procesamientos, análisis y escritura para el desarrollo de mi tesis de pregrado, como tesista del Fondecyt Regular N°1250518. Se seguirá riguosamente una metodología reproducible bajo los lineamientos de la ciencia abierta.

El *outline* de mi tesis se encuentra en [este link](https://ismaelaguayob.github.io/thesis/thesis).

## Organización del repositorio

- `data/raw_data/`: fuentes originales descargadas o recopiladas.
- `data/proc_data/`: datos transformados que alimentan los análisis y aplicaciones.
- `data/codebook/`: versiones editables XLSX del libro de códigos y sus JSON derivados.
- `features/manual_validation/`: backend, conversor del libro, comando y frontend de la validación manual.
- `features/discourse_network/`: generación de productos ilustrativos de redes discursivas.
- `output/figures/`, `output/tables/` y `output/validation/`: resultados producidos por el proyecto.
- `_output/`: sitio HTML generado por Quarto; replica únicamente los recursos necesarios para publicar el reporte.
- `review-workspace/`: configuración, búsquedas, textos convertidos y notas de la revisión bibliográfica.

## Piloto de anotación LLM

`annotations.qmd` sortea el 10% de las intervenciones elegibles por ley y sesión,
reutiliza el contexto y los controles de la app manual y anota todos sus bloques
con `gpt-5.6-luna`, esfuerzo `max`. El prompt se edita en
[`prompts/annotations_pilot.md`](prompts/annotations_pilot.md). El XLSX vigente es
`data/codebook/codebook_v0.3.xlsx` (versión interna `0.4.0-pilot`).

```bash
uv sync --locked
# Renderizar usando solamente resultados guardados:
uv run quarto render annotations.qmd
# La generación está desactivada por instrucción del usuario;
# este reporte analiza la ejecución guardada sin nuevas llamadas.
# Revisar modelo, input, output, códigos destacados y justificaciones:
uv run python -m features.manual_validation
```

Se necesita Quarto CLI en el PATH. Abre la opción **Revisión de anotaciones LLM**
en <http://127.0.0.1:8765> o entra directamente en
<http://127.0.0.1:8765/llm.html>. Los resultados originales están en
`output/annotations/`; los juicios diagnósticos se guardan por separado en
`output/annotation_reviews/`. La [guía del piloto](docs/piloto-anotaciones-llm.md)
explica ejecución, variantes y límites de interpretación.

El [manifiesto del análisis del piloto](data/proc_data/llm_pilots/pilot_f3a69c2f81c587271ef5/manifest.json) resume tokens confirmados y métricas. La política `data/proc_data/llm_pilots/api_policy.json` bloquea nuevas llamadas.
