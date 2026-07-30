# Prompt para resumir fuentes en NotebookLM

## Instrucciones de uso

Usar este prompt con **una fuente por vez**. Selecciona únicamente el documento que quieres resumir. Guarda cada respuesta como un archivo Markdown independiente en `analysis/intermediate/`.

Nombre sugerido: `<primer-autor>_<año>_<titulo-corto>.md`.

## Prompt

```text
Resume la fuente seleccionada siguiendo exactamente la estructura indicada abajo.

Trabaja únicamente con el contenido del documento. No agregues conocimiento externo ni completes información ausente. Si un dato no aparece o no puede verificarse, escribe “No informado”. Distingue cuidadosamente entre lo que los autores proponen, los resultados que encuentran y las interpretaciones que ofrecen.

Escribe en español y conserva los conceptos importantes en su idioma original entre paréntesis cuando sea útil.

# Resumen de fuente: [título]

## 1. Objetivo y pregunta de investigación

Explica brevemente:

- qué problema estudia la fuente;
- cuál es su pregunta u objetivo principal;
- qué busca explicar o comprender.

## 2. Argumento central

Resume en uno o dos párrafos la tesis o explicación principal de los autores. No confundas el argumento con los antecedentes generales del artículo.

## 3. Conceptos principales

Enumera y define brevemente los conceptos que la fuente utiliza realmente. No introduzcas conceptos que no aparezcan en el documento.

## 4. Datos y método

Indica:

- Países o casos estudiados:
- Periodo estudiado:
- tipo y cantidad de datos o documentos analizados;
- actores o población estudiada;
- método de selección de casos o datos;
- método de análisis;
- diseño comparativo o temporal, si corresponde.

No confundas las fuentes de datos con el método de análisis.

## 5. Resultados principales

Presenta entre 3 y 6 resultados. Para cada uno incluye:

1. el hallazgo;
2. la evidencia utilizada para sostenerlo;
3. la página o sección donde aparece.

Señala si algo es un resultado empírico directo o una interpretación de los autores.

## 6. Conclusiones de los autores

Resume qué concluyen los autores, qué aporte atribuyen al estudio y hasta dónde consideran que pueden generalizar sus resultados.

## 7. Limitaciones y preguntas abiertas

Incluye:

- limitaciones reconocidas por los autores;
- explicaciones alternativas que permanezcan abiertas;
- aspectos que el estudio no permite afirmar;
- preguntas que podrían investigarse posteriormente.

## 8. Posible utilidad para la tesis

Sin realizar un análisis profundo, indica brevemente si la fuente podría aportar evidencia para alguna de estas secciones:

- 1.1: justicia de mercado, justicia política y economías morales;
- 2.1: robustez ideacional y persistencia institucional;
- 2.2: discurso, coaliciones, poder y hegemonía;
- 2.3: estrategias de legitimación, tecnocracia y experticia.

Para cada sección pertinente, explica en una o dos oraciones qué resultado o concepto de la fuente podría ser útil. Si no existe una conexión clara, no la fuerces.

## 9. Pasajes útiles para revisión

Selecciona entre 3 y 5 pasajes breves especialmente importantes. Para cada uno incluye:

- un extracto de máximo 20 palabras;
- página o sección;
- una frase que explique qué contiene el pasaje.

Prioriza pasajes que expresen el argumento central, describan el método o presenten un resultado importante. Si no puedes comprobar la ubicación exacta, indícalo.

## 10. Resumen breve

Cierra con un resumen de 100–150 palabras que integre objetivo, método, principal resultado y contribución del estudio.
```

## Repregunta opcional

Si la respuesta no identifica bien la evidencia o las páginas, utiliza:

```text
Revisa el resumen anterior y completa únicamente las páginas o secciones que respaldan el argumento, el método y los resultados principales. No agregues nuevas interpretaciones ni información externa. Si no puedes localizar una afirmación en la fuente, señálala como no verificada.
```
