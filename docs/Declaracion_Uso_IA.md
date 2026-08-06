# Declaración de Uso Ético y Transparente de IA

**Proyecto:** Challenge 03 — Inteligencia Geo-Temporal y de Redes (TechLogistics S.A.)
**Curso:** Análisis de Datos Avanzado — Maestría en Ciencia de los Datos y Analítica, EAFIT
**Herramienta utilizada:** Claude Code (Anthropic), como asistente de programación conversacional.

## Alcance del uso de IA

El equipo utilizó Claude Code como herramienta de apoyo para:

- Generar y depurar código Python (pandas, scipy, statsmodels, NetworkX, Plotly, matplotlib).
- Redactar borradores de las celdas de análisis y del informe técnico en PDF.
- Automatizar tareas repetitivas: ejecución del notebook de punta a punta, generación de
  figuras, y patching de celdas del `.ipynb`.

La IA **no** tomó decisiones de negocio ni definió por sí sola las conclusiones o
recomendaciones del proyecto: cada hallazgo fue generado a partir de cálculos verificables
sobre los datos (`data/*.csv`) y quedó sujeto a la revisión del equipo antes de aceptarse.

## Revisión y control por parte del equipo

Cada entregable producido con asistencia de IA fue revisado, cuestionado y ajustado por el
equipo antes de darlo por definitivo.

## Validación de los resultados analíticos

Los hallazgos cuantitativos (tests ADF, causalidad de Granger, centralidad de grafos, RMSE
de filtrado, comparaciones de AIC, etc.) fueron generados ejecutando código directamente
sobre los datasets del proyecto — no fueron redactados a priori por la IA y luego
"acomodados" a los datos. El equipo revisó que las cifras reportadas en el notebook, en el
`README.md` y en el informe técnico PDF fueran consistentes entre sí y correspondieran a
salidas reales de ejecución, no a estimaciones o suposiciones del modelo de lenguaje.

## Responsabilidad

El equipo asume la responsabilidad completa sobre el contenido técnico, las conclusiones y
las recomendaciones de negocio presentadas en este proyecto. El uso de IA se declara aquí de
forma explícita en cumplimiento de los principios de integridad académica y transparencia
exigidos por la Maestría en Ciencia de los Datos y Analítica de la Universidad EAFIT.
