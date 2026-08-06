# Challenge 03 — Inteligencia Geo-Temporal y de Redes

**TechLogistics S.A. — Optimización de Activos Críticos**
Maestría en Ciencia de los Datos y Analítica · EAFIT · Periodo 2026-2
Docente: Jorge Iván Padilla-Buriticá

**Integrantes del equipo:**
 
| Nombre completo | Cédula         |
| --------------- | -------------- |
| Daniel Amaya Yepes      | 1037646508 |
| Daniel Santiago Cadavid      | 1000646110 |
| Luis Camilo Valencia      | 1037670493 |

## Briefing de negocio

TechLogistics S.A. enfrenta un problema de visibilidad: los datos de la cadena
de frío (agroindustria) y de la red eléctrica están georreferenciados pero desconectados.
Este proyecto busca responder, para la junta directiva:

1. **Grafos** — ¿Cómo se propaga el ruido en la red de sensores/subestaciones?
2. **Geoespacial** — ¿Dónde se localizan los puntos críticos (biomasa baja, anomalías térmicas)?
3. **Series de tiempo** — ¿Cuál es el pronóstico de carga (demanda energética)?

El análisis sigue la metodología CRISP-DM y cubre cuatro fases: comprensión geo-temporal
de los datos, procesamiento de señales, análisis de grafos/topología, y modelado con
recomendaciones de negocio (ver `docs/Lecture_03_Challenge.pdf`).

## Datasets

| Archivo | Descripción |
|---|---|
| `data/agro_clean.csv` / `agro_noise.csv` | Monitoreo agroindustrial (2000 registros, 14 columnas): variables hídricas (Agro_1-3), radiación PAR (Agro_4), índices bióticos NDVI/biomasa I(1) (Agro_5-7), suelo/viento estacionarias (Agro_8-10), coordenadas (oriente antioqueño) y topología de red mesh (`Source_Node`/`Target_Node`). |
| `data/ener_clean.csv` / `ener_noise.csv` | Red eléctrica nacional (2000 registros, 14 columnas): mercado spot demanda/precio/temperatura (Ener_1-3), generación eólica cíclica (Ener_4), factores macro I(1) costo de gas/CO2 (Ener_5-7), calidad de potencia estacionaria frecuencia/voltaje/factor de potencia (Ener_8-10), coordenadas de subestaciones y topología (`Source_Node`/`Target_Node`). |

Diccionario completo de variables en `docs/Lecture_03_dictionary.pdf`. Las versiones
`*_noise` inyectan AWGN (ruido blanco temporal, SNR 5–15 dB) y jitter GPS geoespacial sobre
las versiones `*_clean`.

## Estructura del repositorio

```
├── data/                # los 4 CSV (clean/noise de agro y energía)
├── docs/                # PDFs del enunciado, checklist de entrega, diccionario de datos y declaración de uso ético de IA
├── notebooks/           # notebook principal del análisis
├── reports/             # informe técnico ejecutivo (PDF) para la junta directiva
├── requirements.txt
└── .gitignore
```

## Cómo ejecutar

```bash
# Instalar dependencias en el entorno compartido
python.exe -m pip install -r requirements.txt

# Registrar el kernel de Jupyter (una sola vez)
python.exe -m ipykernel install --user --name=theoutliers-challenge-03 --display-name "Python (theoutliers-challenge-03)"

# Abrir el notebook (selecciona el kernel "Python (theoutliers-challenge-03)")
jupyter.exe notebook notebooks/challenge03_geo_temporal_redes.ipynb
```

## Conclusiones Ejecutivas y Recomendaciones

_Síntesis para la junta directiva de TechLogistics S.A.: hallazgos clave de geoespacial, señales, grafos y modelado, y recomendaciones accionables._

**1. No hay "zonas geográficas" problemáticas, el problema es puntual, no regional.**
Tanto la biomasa baja (NDVI, Tarea 1) como el cruce NDVI/exposición al viento (P2) muestran
que la ubicación **no** explica la variabilidad observada (variación entre celdas
espaciales ≈0.047 frente a ≈0.38 a nivel de registro; correlación NDVI-viento ≈ -0.0007).
**Recomendación:** descartar inversión regional en infraestructura hídrica; priorizar los
~132 puntos de monitoreo individuales identificados que combinan NDVI bajo y alta
exposición al viento, con soluciones puntuales de bajo capex (microaspersión, cortavientos).

**2. El ruido de sensores es corregible y con impacto medible en la capacidad predictiva.**
El ruido inyectado (SNR 5–12 dB) es ruido blanco que se concentra fuera de la banda del
ciclo real de la señal (`f > 0.02` ciclos/muestra, Tarea 3). Un filtro Butterworth simple
(orden 4, `Wn≈0.01`) reduce el RMSE en ~75% y mejora en la misma magnitud el error de un
pronóstico AR(1) evaluado contra la verdad de terreno (Tarea 4). **Recomendación:**
estandarizar un pipeline de filtrado paso-bajo antes de cualquier modelo predictivo que
consuma estas variables, especialmente humedad relativa (`Agro_3`) y variables similares.

**3. La red eléctrica tiene un único punto de alto impacto: el nodo 119.**
La red de subestaciones es bipartita de un solo salto (20 `Source_Node` → 50
`Target_Node`, sin encadenamientos), por lo que la Betweenness Centrality no discrimina
(es 0 para los 70 nodos). Por centralidad de grado, el nodo **119** alimenta a 49 de las 50
subestaciones destino. El análisis de bridges muestra que **no existen
aristas puente** en la red (todo `Target_Node` tiene ≥13 fuentes posibles), por lo que
ningún `Target_Node` quedaría totalmente aislado, pero sí perdería capacidad/redundancia
de forma simultánea y generalizada si el nodo 119 fallara. Además, existe evidencia de
causalidad de Granger rezagada (Factor de Potencia → Voltaje, lags 4–10), por lo que una
perturbación en el nodo 119 podría propagarse con rezago hacia inestabilidad de voltaje.
**Recomendación:** priorizar redundancia N-1 (fuente de respaldo) específicamente en el
nodo 119 antes que en cualquier otro punto de la topología.

**4. La topología de red no mejora, por sí sola, el pronóstico de demanda.**
Incluir la centralidad del nodo de origen como exógena en el ARIMAX de `Ener_1` empeora el
AIC (+1.95) y su coeficiente no es significativo (P3). **Recomendación:** mantener el
modelo de demanda simple (autorregresivo + temperatura); usar la centralidad de red para
decisiones de **resiliencia operativa** (dónde invertir en redundancia), no como insumo de
pronóstico de demanda.

**Resumen para la junta:** los datos no muestran "puntos calientes" geográficos que
justifiquen grandes inversiones regionales; los recursos deben dirigirse a (a) un pipeline
de filtrado de señal estandarizado, (b) redundancia eléctrica focalizada en el nodo 119, y
(c) soluciones agronómicas puntuales en los ~132 sensores críticos identificados.
Todo priorizado por evidencia cuantitativa, no por intuición geográfica.

Detalle metodológico completo en `notebooks/` y en el informe técnico
(`reports/Informe_Tecnico_TechLogistics.pdf`).

## Uso ético de IA

Este proyecto se apoyó en un asistente de IA (Claude Code) para la implementación técnica.
El equipo revisó, cuestionó y solicitó ajustes sobre cada resultado antes de aceptarlo — el
detalle de este proceso y el alcance del uso de IA está documentado en
[`docs/Declaracion_Uso_IA.md`](docs/Declaracion_Uso_IA.md).