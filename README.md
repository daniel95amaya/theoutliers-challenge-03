# Challenge 02 — Inteligencia Geo-Temporal y de Redes

**TechLogistics S.A. — Optimización de Activos Críticos**
Maestría en Ciencia de los Datos y Analítica · EAFIT · Periodo 2026-1
Docente: Jorge Iván Padilla-Buriticá

## Briefing de negocio

TechLogistics S.A. (ficticia) enfrenta un problema de visibilidad: los datos de la cadena
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
├── docs/                # PDFs del enunciado, checklist de entrega y diccionario de datos
├── notebooks/           # notebook principal del análisis
├── reports/             # informe técnico ejecutivo (PDF) para la junta directiva
├── requirements.txt
└── .gitignore
```

## Cómo ejecutar

> **Nota:** el `.venv` no vive dentro de esta carpeta porque la ruta del proyecto (anidada en
> OneDrive, con nombres largos en español) supera el límite de longitud de ruta de Windows y
> rompe la instalación de paquetes. En su lugar se usa el entorno compartido `C:\Ambientes\venv`.

```bash
# Instalar dependencias en el entorno compartido
C:\Ambientes\venv\Scripts\python.exe -m pip install -r requirements.txt

# Registrar el kernel de Jupyter (una sola vez)
C:\Ambientes\venv\Scripts\python.exe -m ipykernel install --user --name=theoutliers-challenge-03 --display-name "Python (theoutliers-challenge-03)"

# Abrir el notebook (selecciona el kernel "Python (theoutliers-challenge-03)")
C:\Ambientes\venv\Scripts\jupyter.exe notebook notebooks/challenge02_geo_temporal_redes.ipynb
```

## Checklist de entrega (`docs/Lecture_03_checklist.pdf`)

- [x] Repositorio en GitHub con historial de commits progresivo
- [x] Notebook (.ipynb) documentado — cada celda de código precedida por Markdown explicativo
- [x] Informe Técnico (PDF) que responde las preguntas de negocio con evidencia gráfica (`reports/Informe_Tecnico_TechLogistics.pdf`)

**Hitos técnicos:**

- [x] Series de Tiempo: test ADF, diferenciación I(1) antes de ARIMA
- [x] Procesamiento de Señales: FFT/espectrograma, filtro Butterworth/media móvil
- [x] Grafos: centralidad de grado y betweenness, nodo crítico identificado
- [x] Geoespacial: mapa `scatter_mapbox` relacionando ubicación y variables del sensor

**Preguntas de negocio (Fase 4):**

- [x] P1 — Causalidad de Granger (Factor de Potencia vs. Voltaje) e impacto de falla del nodo crítico
- [x] P2 — Optimización geo-agrónoma e inversión en infraestructura hídrica
- [x] P3 — ARIMAX de demanda energética con centralidad de nodo como exógena

**Plazo de entrega:** 07 de febrero de 2026 (23:59 COT).

## Repositorio en GitHub

Ya publicado en [github.com/daniel95amaya/theoutliers-challenge-03](https://github.com/daniel95amaya/theoutliers-challenge-03).

Pasos seguidos (sin GitHub CLI, que no estaba instalado): se creó el repo vacío manualmente en
github.com (sin README/licencia inicial), se agregó como remoto y se hizo el push inicial:

```bash
git remote add origin https://github.com/daniel95amaya/theoutliers-challenge-03.git
git push -u origin main
```
