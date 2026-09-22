# Resolución manual de afiliaciones históricas

La tabla editable es
[`data/curation/party_at_date_overrides.csv`](../data/curation/party_at_date_overrides.csv).
Contiene una fila por persona, documento y fecha cuyo historial de militancia de
la BCN quedó sin resolver o cuya regla por tipo de actor debe corregirse. La clave
incluye `speaker`, de modo que también admite personas sin `person_href`. La extracción original en
`parliamentarian_affiliations.parquet` no se modifica.

Para conservar una fila pendiente, deje `resolution=pending`. Para incorporar
una decisión respaldada, use una de estas alternativas:

- `confirmed`: complete `party_at_date`, su enlace si existe, `evidence_url`,
  `evidence_note`, `reviewed_by` y `reviewed_at`.
- `nonpartisan`: complete los mismos campos y escriba exactamente
  `Independiente` en `party_at_date`.
- `unresolved`: documenta que se revisó pero que aún no hay evidencia suficiente;
  no cambia la tabla analítica.

Al renderizar `proc.qmd`, solo las dos primeras alternativas se aplican a filas
automáticas `unknown` o `not_applicable`. La salida conserva `manual_documented`, el método de
resolución y la URL de evidencia; no sustituye una afiliación histórica hallada
por la BCN.
