# Corrección de agotamiento de tokens en anotaciones

Fecha: 2026-09-14. SDK instalado y probado: `openai==3.9.0`.

## Diagnóstico

El piloto `pilot_f3a69c2f81c587271ef5` contiene 418 resultados: 306 válidos, 109 incompletos
por `incomplete_details.reason="max_output_tokens"` y tres salidas inválidas
(cita no literal, span/concepto duplicado y referencia inexistente).
Los 109 casos agotaron 16.384 tokens de salida; 104 no produjeron texto visible.
El esfuerzo configurado era `max`.

La [documentación de razonamiento de OpenAI](https://developers.openai.com/api/docs/guides/reasoning)
explica que `max_output_tokens` incluye razonamiento y salida visible, que el
límite puede agotarse antes de producir texto y recomienda un margen inicial de
al menos 25.000 tokens. La [referencia Python de Responses](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
y los tipos instalados del SDK respaldan el uso de `reasoning.effort`,
`max_output_tokens`, `status`, `incomplete_details` y `usage`.
La [ficha de Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
confirma soporte para `max` y un máximo de 128.000 tokens de salida.

## Cambios aplicados

- Nuevas ejecuciones: Luna `max` y `max_output_tokens=32768` por defecto.
- Cliente con `max_retries=0`, timeout de 600 segundos y sin consulta previa
  al endpoint de modelos. Cada bloque admite un solo intento HTTP.
- Intentos reservados como `started` antes del envío y bloqueo por proceso para
  evitar duplicar un lote. Reanudar conserva los intentos incompletos o inciertos.
- Causas de interrupción y errores de API exportadas en columnas separadas.
  Una respuesta incompleta sigue excluida de las anotaciones válidas.
- Autorización excepcional limitada a cinco bloques de una ejecución concreta;
  retirada después de las cinco llamadas. La política global sigue desactivada.

## Comprobación real

Ejecución: `pilot_7f524bf859ccaf5b362b`. Se utilizaron los mismos objetivos, contextos y libro
congelados del piloto, con el prompt nuevo de confianza y el esquema actual.
La selección dirigida cubrió tres leyes, bloques largos y breves, y respuestas
históricas vacías y parciales. Los números de bloque empiezan en uno.

| Bloque original | Ley | Palabras | Salida anterior | Salida nueva | Razonamiento nuevo | Estado |
|---:|---|---:|---:|---:|---:|---|
| 21 | 21419 | 192 | 16384 | 945 | 584 | completed |
| 124 | 21538 | 68 | 16384 | 356 | 263 | completed |
| 228 | 21735 | 181 | 16384 | 496 | 161 | completed |
| 343 | 21735 | 54 | 16384 | 164 | 79 | completed |
| 85 | 21419 | 60 | 16384 | 104 | 23 | completed |

Las cinco respuestas pasaron el esquema JSON y la validación local de evidencia,
referencias y confianza. Se obtuvieron dos anotaciones y tres decisiones válidas
`no_statements`. Consumo confirmado: **40,002 tokens de entrada,
2,065 de salida, de los cuales 1,110
fueron de razonamiento; 42,067 tokens totales**.

Los resultados completos, requests, snapshots y comparación están en
[`pilot_7f524bf859ccaf5b362b`](../output/annotations_checks/pilot_7f524bf859ccaf5b362b/token_check_summary.json).
Los Parquet `results.parquet`, `annotations.parquet` y `comparison.parquet`
conservan datos y confianza; sus CSV se encuentran en
[`output/tables/annotations`](../output/tables/annotations/).
Las respuestas del piloto original no se modificaron.

## Alcance y verificación local

La prueba confirma resolución técnica en cinco casos antes interrumpidos.
Se cambiaron conjuntamente esfuerzo, techo, prompt y esquema: esta comparación
no permite atribuir la mejora a un único cambio ni medir precisión sustantiva.
Ningún techo finito elimina por completo el riesgo de truncamiento. El ejecutor
conserva la causa exacta si reaparece y evita reintentos con gasto no autorizado.
Los tres errores históricos de contenido siguen requiriendo validación local;
aumentar el límite no corrige automáticamente esas asignaciones.

Pasaron 23 pruebas de anotaciones y auditoría. La suite completa ejecutó 46:
43 pasaron y tres fallaron por archivos ausentes en `data/codebook/`
(`codebook_v0.1.xlsx`, `codebook_v0.2.xlsx`, `codebook_v0.3.xlsx`). Esas rutas
pertenecen a pruebas del libro y no se alteraron en esta corrección.

**Actualización del 17 de septiembre de 2026.** Las pruebas del libro ahora usan
`features/codebook/`, su ubicación vigente. La suite completa actual contiene 52
pruebas y todas pasan. El conteo anterior se conserva para documentar el estado
de esta comprobación en la fecha en que se realizó.

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m unittest tests.test_llm_annotations tests.test_llm_audit -q
```
