# Workspace de revisión bibliográfica

Esta carpeta reúne los archivos de trabajo asociados a `literature-source-retrieval` y a la revisión de literatura. `references.bib` permanece en la raíz porque es la bibliografía canónica compartida por la tesis y los documentos Quarto.

- `literature-review.yaml`: configuración operativa del proyecto de búsqueda.
- `literature-keywords.yaml`: memoria acumulativa de términos activos, candidatos y rechazados.
- `retrieval/intermediate/`: resultados crudos o normalizados de cada consulta.
- `retrieval/curated/`: mapas de candidatos y productos de curaduría.
- `machine-readable/`: conversiones de fuentes para lectura y síntesis.
- `analysis/intermediate/`: fichas y notas analíticas por fuente.
- `tools/`: utilidades locales antiguas conservadas por trazabilidad; la skill instalada contiene actualmente el runtime operativo.

La configuración se comprueba desde la raíz del repositorio con:

```bash
python /home/ismaelaguayob/.codex/skills/literature-source-retrieval/scripts/doctor_retrieval_config.py --config review-workspace/literature-review.yaml
```
