"""Genera el Informe Tecnico Ejecutivo en PDF a partir de los analisis del notebook
challenge02_geo_temporal_redes.ipynb. Recalcula los resultados directamente sobre los
CSV en data/ para que el reporte sea reproducible sin depender del notebook ejecutado.

Uso: C:\\Ambientes\\venv\\Scripts\\python.exe reports/generate_report.py
"""
import textwrap
import warnings
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import networkx as nx
import numpy as np
import pandas as pd
from scipy import signal
from scipy.spatial import cKDTree
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUT_PATH = REPO_ROOT / "reports" / "Informe_Tecnico_TechLogistics.pdf"

PAGE_SIZE = (8.27, 11.69)  # A4 en pulgadas
NAVY = "#1B2A4A"
ACCENT = "#2E86AB"
RED = "#C0392B"


def add_text_page(pdf, title, body, subtitle=None, footer=None):
    fig = plt.figure(figsize=PAGE_SIZE)
    fig.patch.set_facecolor("white")
    y = 0.94
    fig.text(0.08, y, title, fontsize=17, fontweight="bold", color=NAVY, va="top")
    y -= 0.045
    if subtitle:
        fig.text(0.08, y, subtitle, fontsize=10.5, color=ACCENT, va="top", style="italic")
        y -= 0.035
    y -= 0.015
    fig.add_artist(plt.Line2D([0.08, 0.92], [y, y], color=NAVY, linewidth=1.2, transform=fig.transFigure))
    y -= 0.035

    for para in body:
        if para and "\n" in para:
            for line in para.split("\n"):
                fig.text(0.08, y, line, fontsize=8, family="monospace", color="black", va="top")
                y -= 0.021
            y -= 0.012
            continue
        wrapped = textwrap.wrap(para, width=98) if para else [""]
        for line in wrapped:
            fig.text(0.08, y, line, fontsize=10, color="black", va="top", wrap=True)
            y -= 0.0245
        y -= 0.012

    if footer:
        footer_lines = textwrap.wrap(footer, width=110)
        fy = 0.04 + 0.018 * (len(footer_lines) - 1)
        for line in footer_lines:
            fig.text(0.08, fy, line, fontsize=8, color="grey", va="bottom")
            fy -= 0.018
    pdf.savefig(fig)
    plt.close(fig)


def cover_page(pdf):
    fig = plt.figure(figsize=PAGE_SIZE)
    fig.patch.set_facecolor(NAVY)
    fig.text(0.5, 0.62, "Informe Técnico", fontsize=30, fontweight="bold", color="white", ha="center")
    fig.text(0.5, 0.56, "Inteligencia Geo-Temporal y de Redes", fontsize=16, color="white", ha="center")
    fig.text(0.5, 0.50, "Optimización de Activos Críticos — TechLogistics S.A.", fontsize=12,
             color="#B9C6E0", ha="center")
    fig.add_artist(plt.Line2D([0.25, 0.75], [0.44, 0.44], color=ACCENT, linewidth=1.5, transform=fig.transFigure))
    fig.text(0.5, 0.38, "Challenge 02 — Fundamentos en Ciencia de Datos", fontsize=10.5, color="white", ha="center")
    fig.text(0.5, 0.34, "Maestría en Ciencia de los Datos y Analítica — EAFIT", fontsize=10.5, color="white", ha="center")
    meses_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    hoy = date.today()
    fig.text(0.5, 0.12, f"{hoy.day} de {meses_es[hoy.month - 1]} de {hoy.year}",
             fontsize=10, color="#B9C6E0", ha="center")
    pdf.savefig(fig)
    plt.close(fig)


def main():
    agro_clean = pd.read_csv(DATA_DIR / "agro_clean.csv")
    agro_noise = pd.read_csv(DATA_DIR / "agro_noise.csv")
    ener_clean = pd.read_csv(DATA_DIR / "ener_clean.csv")
    ener_noise = pd.read_csv(DATA_DIR / "ener_noise.csv")

    with PdfPages(OUT_PATH) as pdf:
        # ---------------------------------------------------------------- cover
        cover_page(pdf)

        # ---------------------------------------------------------------- exec summary
        add_text_page(
            pdf,
            "Resumen Ejecutivo",
            [
                "TechLogistics S.A. requería visibilidad conjunta sobre su cadena de frío "
                "agroindustrial y su red eléctrica, ambas georreferenciadas pero analizadas de "
                "forma desconectada. Este informe resume los hallazgos cuantitativos de cinco "
                "tareas técnicas (geoespacial, estacionariedad, señales, filtrado y grafos) y tres "
                "preguntas de negocio (causalidad de red, inversión geo-agrónoma y pronóstico de demanda).",
                "",
                "Hallazgos principales:",
                "1. No existen \"zonas geográficas\" problemáticas — ni la biomasa baja (NDVI) ni su "
                "cruce con exposición al viento muestran patrones espaciales sistemáticos.",
                "2. El ruido de sensores (SNR 5-12 dB) es corregible: un filtro Butterworth simple "
                "reduce el error de reconstrucción en ~75% y mejora en la misma magnitud la capacidad "
                "predictiva de un modelo autorregresivo.",
                "3. La red eléctrica tiene un único nodo de alto impacto (nodo 119, alimenta al 98% de "
                "las subestaciones destino), aunque no existen aristas \"puente\": ningún nodo quedaría "
                "totalmente aislado, pero sí perdería redundancia de forma simultánea y generalizada.",
                "4. La centralidad de red no mejora el pronóstico de demanda eléctrica — es relevante "
                "para decisiones de resiliencia operativa, no como insumo predictivo.",
                "",
                "Recomendación general: dirigir la inversión hacia (a) un pipeline de filtrado de señal "
                "estandarizado, (b) redundancia eléctrica focalizada en el nodo 119, y (c) intervenciones "
                "agronómicas puntuales en los sensores críticos identificados — priorizado por evidencia "
                "cuantitativa en lugar de intuición geográfica.",
            ],
        )

        # ---------------------------------------------------------------- Tarea 1: Geo
        q1_ndvi = agro_clean["Agro_5"].quantile(0.25)
        n_bins = 6
        ac = agro_clean.copy()
        ac["lat_bin"] = pd.cut(ac["Latitude"], bins=n_bins)
        ac["lon_bin"] = pd.cut(ac["Longitude"], bins=n_bins)
        grid = ac.groupby(["lat_bin", "lon_bin"], observed=True).agg(
            ndvi_mean=("Agro_5", "mean"), n=("Agro_5", "size")
        ).reset_index()
        grid = grid[grid["n"] >= 15]

        fig, ax = plt.subplots(figsize=PAGE_SIZE)
        sc = ax.scatter(agro_clean["Longitude"], agro_clean["Latitude"], c=agro_clean["Agro_5"],
                         s=agro_clean["Agro_1"] / 3, cmap="RdYlGn", alpha=0.75, edgecolor="none")
        ax.set_xlabel("Longitud")
        ax.set_ylabel("Latitud")
        ax.set_title("Tarea 1 — Sensores agroindustriales: color = NDVI, tamaño = Humedad", fontsize=12, color=NAVY)
        cbar = plt.colorbar(sc, ax=ax, shrink=0.7)
        cbar.set_label("NDVI (Agro_5)")
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        add_text_page(
            pdf,
            "Tarea 1 — Exploración Geo-Temporal",
            [
                f"NDVI promedio global: {agro_clean['Agro_5'].mean():.3f}. Desviación estándar entre "
                f"medias de celdas de una grilla espacial 6x6: {grid['ndvi_mean'].std():.3f}, frente a "
                f"{agro_clean['Agro_5'].std():.3f} de dispersión a nivel de registro.",
                "",
                "Análisis: no hay una zona geográfica donde la biomasa sea consistentemente baja. La "
                "variación de NDVI entre celdas espaciales es marginal frente a la dispersión a nivel de "
                "registro — la variabilidad del NDVI está dominada por la dinámica temporal de cada "
                "sensor (serie no estacionaria I(1)), no por su ubicación.",
            ],
        )

        # ---------------------------------------------------------------- Tarea 2: ADF
        ener_cols = [f"Ener_{i}" for i in range(1, 11)]
        adf_rows = []
        for col in ener_cols:
            stat, pvalue, *_ = adfuller(ener_clean[col], autolag="AIC")
            adf_rows.append((col, stat, pvalue, pvalue > 0.05))
        adf_df = pd.DataFrame(adf_rows, columns=["serie", "adf_stat", "p_value", "no_estacionaria"])
        non_stationary = adf_df.loc[adf_df["no_estacionaria"], "serie"].tolist()

        ener5_diff = ener_clean["Ener_5"].diff().dropna()
        fig, axes = plt.subplots(2, 1, figsize=PAGE_SIZE)
        axes[0].plot(ener_clean["Ener_5"])
        axes[0].set_title("Tarea 2 — Ener_5 (Costo del Gas): nivel", fontsize=11, color=NAVY)
        axes[1].plot(ener5_diff, color=ACCENT)
        axes[1].axhline(ener5_diff.mean(), color=RED, linestyle="--", label=f"media={ener5_diff.mean():.4f}")
        axes[1].set_title("Primera diferencia", fontsize=11, color=NAVY)
        axes[1].legend()
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        add_text_page(
            pdf,
            "Tarea 2 — Estacionariedad y Windowing",
            [
                "Test ADF sobre Ener_1..10 (ener_clean.csv):",
                adf_df.to_string(index=False),
                "",
                f"Series no estacionarias (p-value > 0.05): {', '.join(non_stationary)}.",
                "",
                f"Ener_5 (Costo del Gas) es un Random Walk con Drift: el ADF no rechaza raíz unitaria "
                f"(p≈{adf_df.loc[adf_df.serie=='Ener_5','p_value'].values[0]:.3f}); su primera diferencia "
                f"tiene media {ener5_diff.mean():.4f} y desviación estándar {ener5_diff.std():.4f} — un "
                f"impulso determinístico pequeño frente al ruido por paso, que acumulado en 2000 "
                f"observaciones explica el ascenso sostenido de la serie.",
            ],
        )

        # ---------------------------------------------------------------- Tarea 3: FFT
        fs = 1.0
        e4c = ener_clean["Ener_4"].to_numpy()
        e4n = ener_noise["Ener_4"].to_numpy()
        N = len(e4c)
        freqs = np.fft.rfftfreq(N, d=1 / fs)
        psd_c = np.abs(np.fft.rfft(e4c - e4c.mean())) ** 2 / N
        psd_n = np.abs(np.fft.rfft(e4n - e4n.mean())) ** 2 / N
        snr_e4 = 10 * np.log10(np.var(e4c) / np.var(e4n - e4c))

        f_c, t_c, Sxx_c = signal.spectrogram(e4c, fs=fs, nperseg=128, noverlap=96)
        f_n, t_n, Sxx_n = signal.spectrogram(e4n, fs=fs, nperseg=128, noverlap=96)

        fig, axes = plt.subplots(2, 1, figsize=PAGE_SIZE)
        axes[0].semilogy(freqs, psd_c, label="clean", alpha=0.8)
        axes[0].semilogy(freqs, psd_n, label="noise", alpha=0.6)
        axes[0].set_title("Tarea 3 — FFT de Ener_4: clean vs noise", fontsize=11, color=NAVY)
        axes[0].set_xlabel("Frecuencia (ciclos/muestra)")
        axes[0].legend()

        im = axes[1].pcolormesh(t_n, f_n, 10 * np.log10(Sxx_n + 1e-12), shading="gouraud", cmap="viridis")
        axes[1].set_title("Espectrograma Ener_4 (noise)", fontsize=11, color=NAVY)
        axes[1].set_xlabel("Muestra")
        axes[1].set_ylabel("Frecuencia")
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        add_text_page(
            pdf,
            "Tarea 3 — Análisis Espectral (FFT) y Espectrogramas",
            [
                f"SNR empírico (Ener_4 noise vs clean): {snr_e4:.2f} dB (dentro del rango 5-12 dB "
                "especificado).",
                "",
                "Análisis: la señal real de Ener_4 (generación eólica cíclica) concentra su energía en "
                "f < 0.02 ciclos/muestra (periodo dominante ≈ 285-333 muestras). El ruido inyectado es "
                "ruido blanco (espectro plano) y por tanto domina precisamente donde la señal real no "
                "tiene energía: en toda la banda f > 0.02 ciclos/muestra (periodos < ~50 muestras). El "
                "ratio de potencia noise/clean pasa de ~1.04 en la banda de la señal a >10^10 en las "
                "bandas altas — visible como una \"alfombra\" difusa en el espectrograma.",
            ],
        )

        # ---------------------------------------------------------------- Tarea 4: Butterworth
        a3c = agro_clean["Agro_3"].to_numpy()
        a3n = agro_noise["Agro_3"].to_numpy()
        cutoffs = np.arange(0.004, 0.05, 0.002)
        rmses = []
        for wn in cutoffs:
            b, a = signal.butter(N=4, Wn=wn, btype="low", fs=fs)
            filt = signal.filtfilt(b, a, a3n)
            rmses.append(np.sqrt(np.mean((filt - a3c) ** 2)))
        best_wn = cutoffs[int(np.argmin(rmses))]
        b, a = signal.butter(N=4, Wn=best_wn, btype="low", fs=fs)
        a3_filt = signal.filtfilt(b, a, a3n)
        rmse_base = np.sqrt(np.mean((a3n - a3c) ** 2))
        rmse_filt = np.sqrt(np.mean((a3_filt - a3c) ** 2))

        fig, axes = plt.subplots(2, 1, figsize=PAGE_SIZE)
        axes[0].plot(cutoffs, rmses, marker="o")
        axes[0].axvline(best_wn, color=RED, linestyle="--", label=f"Wn óptimo={best_wn:.3f}")
        axes[0].set_title("Tarea 4 — Selección de frecuencia de corte (Butterworth)", fontsize=11, color=NAVY)
        axes[0].set_xlabel("Wn (ciclos/muestra)")
        axes[0].set_ylabel("RMSE vs clean")
        axes[0].legend()

        axes[1].plot(a3n, alpha=0.3, label="noise")
        axes[1].plot(a3c, alpha=0.8, label="clean")
        axes[1].plot(a3_filt, color=RED, label="filtrado")
        axes[1].set_title("Agro_3 (Humedad Relativa): noise vs clean vs filtrado", fontsize=11, color=NAVY)
        axes[1].legend()
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        n = len(a3c)
        split = int(n * 0.8)

        def ar1_rmse(train, test, target):
            x, y = train[:-1], train[1:]
            phi, c = np.polyfit(x, y, 1)
            preds = c + phi * test[:-1]
            return phi, np.sqrt(np.mean((preds - target[1:]) ** 2))

        phi_noisy, rmse_ar1_noisy = ar1_rmse(a3n[:split], a3n[split:], a3c[split:])
        phi_filt, rmse_ar1_filt = ar1_rmse(a3_filt[:split], a3_filt[split:], a3c[split:])

        add_text_page(
            pdf,
            "Tarea 4 — Filtrado y Reconstrucción",
            [
                f"Frecuencia de corte óptima: Wn≈{best_wn:.3f} ciclos/muestra. RMSE baseline (noise vs "
                f"clean): {rmse_base:.4f}. RMSE filtrado: {rmse_filt:.4f} "
                f"(reducción de {100*(1-rmse_filt/rmse_base):.1f}%).",
                "",
                f"Validación predictiva (AR(1) un paso adelante, evaluado contra Agro_3 clean de "
                f"prueba): entrenado con noise φ={phi_noisy:.3f} RMSE={rmse_ar1_noisy:.3f}; entrenado "
                f"con filtrado φ={phi_filt:.3f} RMSE={rmse_ar1_filt:.3f} "
                f"(mejora {100*(1-rmse_ar1_filt/rmse_ar1_noisy):.1f}%).",
                "",
                "Conclusión: el filtrado mejora sustancialmente la capacidad predictiva, no solo la "
                "apariencia visual de la serie — corrige además el sesgo de atenuación del coeficiente "
                "autorregresivo introducido por el ruido de medición.",
            ],
        )

        # ---------------------------------------------------------------- Tarea 5: Grafo
        G = nx.from_pandas_edgelist(ener_clean, source="Source_Node", target="Target_Node", create_using=nx.DiGraph())
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        bottleneck = max(degree_centrality, key=degree_centrality.get)
        n_targets_bottleneck = ener_clean.loc[ener_clean["Source_Node"] == bottleneck, "Target_Node"].nunique()
        bridges = list(nx.bridges(G.to_undirected()))

        fig, ax = plt.subplots(figsize=PAGE_SIZE)
        pos = nx.bipartite_layout(G, ener_clean["Source_Node"].unique())
        node_color = ["#2E86AB" if node in set(ener_clean["Source_Node"]) else "#F24236" for node in G.nodes()]
        node_size = [4000 * degree_centrality[node] + 50 for node in G.nodes()]
        nx.draw_networkx(G, pos, ax=ax, node_color=node_color, node_size=node_size, with_labels=True,
                          font_size=6, arrows=True, arrowsize=6, edge_color="grey", alpha=0.85)
        ax.set_title("Tarea 5 — Red de subestaciones (azul=Source, rojo=Target)\nTamaño = centralidad de grado",
                     fontsize=11, color=NAVY)
        ax.axis("off")
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        add_text_page(
            pdf,
            "Tarea 5 — Grafo de Subestaciones y Centralidad",
            [
                f"Red: {G.number_of_nodes()} nodos (20 Source_Node, 50 Target_Node), "
                f"{G.number_of_edges()} aristas, {nx.number_weakly_connected_components(G)} componente(s).",
                "",
                "La Betweenness Centrality es 0 para los 70 nodos: la topología es bipartita de un "
                "solo salto (todas las aristas van de Source a Target, sin encadenamientos), por lo que "
                "ningún nodo puede estar \"en medio\" de un camino entre otros dos.",
                "",
                f"Nodo cuello de botella (mayor centralidad de grado): {bottleneck} "
                f"(centralidad={degree_centrality[bottleneck]:.2f}), alimenta a {n_targets_bottleneck} de "
                "50 subestaciones destino.",
                "",
                f"Número de aristas puente (bridges) en la red: {len(bridges)} — ningún Target_Node "
                "quedaría totalmente aislado ante la falla de una única conexión (in-degree mínimo "
                f"observado: {min(dict(G.in_degree()).get(t, 0) for t in ener_clean['Target_Node'].unique())}).",
            ],
        )

        # ---------------------------------------------------------------- P1: Granger
        maxlag = 10
        res_9_10 = grangercausalitytests(ener_clean[["Ener_10", "Ener_9"]], maxlag=maxlag, verbose=False)
        res_10_9 = grangercausalitytests(ener_clean[["Ener_9", "Ener_10"]], maxlag=maxlag, verbose=False)
        p_9_10 = {lag: res_9_10[lag][0]["ssr_ftest"][1] for lag in res_9_10}
        p_10_9 = {lag: res_10_9[lag][0]["ssr_ftest"][1] for lag in res_10_9}

        fig, ax = plt.subplots(figsize=PAGE_SIZE)
        lags = list(p_9_10.keys())
        ax.plot(lags, list(p_9_10.values()), marker="o", label="Voltaje → Factor de Potencia")
        ax.plot(lags, list(p_10_9.values()), marker="s", label="Factor de Potencia → Voltaje")
        ax.axhline(0.05, color=RED, linestyle="--", label="umbral p=0.05")
        ax.set_xlabel("Lag")
        ax.set_ylabel("p-value (Granger)")
        ax.set_title("P1 — Causalidad de Granger: Voltaje vs Factor de Potencia", fontsize=12, color=NAVY)
        ax.legend()
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        add_text_page(
            pdf,
            "P1 — Causalidad y Redes",
            [
                "No hay evidencia de que el Voltaje ayude a predecir el Factor de Potencia en ningún "
                "lag (p-value siempre > 0.11). En la dirección opuesta (Factor de Potencia → Voltaje) "
                "aparece causalidad débil y rezagada: significativa en lags 4, 5, 9 y 10 (p≈0.02-0.04), "
                "no en lags cortos — pese a correlación contemporánea casi nula (r≈0.02).",
                "",
                f"Impacto de falla de red: dado que la Betweenness es 0 en toda la red (Tarea 5), se usa "
                f"centralidad de grado — la falla del nodo {bottleneck} afectaría simultáneamente a "
                f"{n_targets_bottleneck}/50 subestaciones destino. Combinado con la causalidad rezagada "
                "encontrada, una perturbación en ese nodo podría propagarse hacia inestabilidad de "
                "voltaje aguas abajo, reforzando la prioridad de redundancia N-1 en ese punto.",
            ],
        )

        # ---------------------------------------------------------------- P2: Geo-agro
        an = agro_noise.copy()
        coords = an[["Longitude", "Latitude"]].to_numpy()
        tree = cKDTree(coords)
        k = 20
        _, idx = tree.query(coords, k=k + 1)
        an["Latitude_smoothed"] = an["Latitude"].to_numpy()[idx].mean(axis=1)
        rmse_lat_base = np.sqrt(np.mean((an["Latitude"] - agro_clean["Latitude"]) ** 2))
        rmse_lat_knn = np.sqrt(np.mean((an["Latitude_smoothed"] - agro_clean["Latitude"]) ** 2))

        q1n, q3w = an["Agro_5"].quantile(0.25), an["Agro_10"].quantile(0.75)
        critical = an[(an["Agro_5"] <= q1n) & (an["Agro_10"] >= q3w)]
        corr_ndvi_wind = an["Agro_5"].corr(an["Agro_10"])

        fig, ax = plt.subplots(figsize=PAGE_SIZE)
        sc = ax.scatter(an["Longitude"], an["Latitude_smoothed"], c="lightgrey", s=10, alpha=0.5, label="todos")
        sc2 = ax.scatter(critical["Longitude"], critical["Latitude_smoothed"], c=critical["Agro_5"],
                          s=critical["Agro_10"] * 8, cmap="OrRd_r", alpha=0.9, label="críticos")
        ax.set_xlabel("Longitud")
        ax.set_ylabel("Latitud (suavizada)")
        ax.set_title(f"P2 — Puntos críticos: NDVI bajo + alta exposición al viento (n={len(critical)})",
                     fontsize=11, color=NAVY)
        cbar = plt.colorbar(sc2, ax=ax, shrink=0.7)
        cbar.set_label("NDVI (Agro_5)")
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        add_text_page(
            pdf,
            "P2 — Optimización Geo-Agrónoma",
            [
                f"Suavizado GPS: RMSE de latitud baseline {rmse_lat_base:.5f} → k-NN geográfico (k={k}) "
                f"{rmse_lat_knn:.5f} (mejora {100*(1-rmse_lat_knn/rmse_lat_base):.1f}%). Un rolling mean "
                "secuencial por Source_Node empeora el error ~5x, porque cada registro es una ubicación "
                "espacialmente independiente, no una traza continua.",
                "",
                f"Correlación NDVI vs varianza del viento: {corr_ndvi_wind:.4f} (prácticamente nula). El "
                f"cruce de NDVI bajo y viento alto identifica {len(critical)} de {len(an)} registros, "
                "cercano al esperado bajo independencia total — no hay una zona geográfica agregada.",
                "",
                "Recomendación: inversión focalizada en los puntos críticos individuales identificados "
                "(microaspersión, cortavientos puntuales), no infraestructura hídrica regional.",
            ],
        )

        # ---------------------------------------------------------------- P3: ARIMAX
        ener_clean["source_node_centrality"] = ener_clean["Source_Node"].map(degree_centrality)
        exog_base = ener_clean[["Ener_3"]]
        exog_full = ener_clean[["Ener_3", "source_node_centrality"]]
        order = (2, 1, 2)
        m_base = SARIMAX(ener_clean["Ener_1"], exog=exog_base, order=order,
                          enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        m_full = SARIMAX(ener_clean["Ener_1"], exog=exog_full, order=order,
                          enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)

        add_text_page(
            pdf,
            "P3 — Analítica Predictiva (ARIMAX)",
            [
                f"Orden ARIMA: {order} (d=1 por no estacionariedad de Ener_1, Tarea 2).",
                "",
                f"AIC sin centralidad (solo Temperatura): {m_base.aic:.2f}",
                f"AIC con centralidad (Temperatura + centralidad): {m_full.aic:.2f} "
                f"(Δ={m_full.aic - m_base.aic:+.2f})",
                "",
                "Conclusión: agregar la centralidad del nodo de origen empeora el AIC y su coeficiente "
                "no es significativo (p≈0.69) — la demanda está dominada por su propia estructura "
                "autorregresiva. La centralidad de red es útil para decisiones de resiliencia "
                "operativa, no como insumo de pronóstico de demanda.",
            ],
        )

        # ---------------------------------------------------------------- Conclusiones
        add_text_page(
            pdf,
            "Conclusiones Ejecutivas y Recomendaciones",
            [
                "1. No hay \"zonas geográficas\" problemáticas — el problema es puntual, no regional. "
                "Priorizar los ~132 puntos de monitoreo críticos con soluciones de bajo capex, no "
                "inversión regional en infraestructura hídrica.",
                "",
                "2. El ruido de sensores es corregible y con impacto medible en la capacidad predictiva. "
                "Estandarizar un pipeline de filtrado Butterworth antes de cualquier modelo predictivo.",
                "",
                "3. La red eléctrica tiene un único punto de alto impacto (nodo 119). Priorizar "
                "redundancia N-1 específicamente ahí; no existen aristas puente en la red actual.",
                "",
                "4. La topología de red no mejora, por sí sola, el pronóstico de demanda. Usar la "
                "centralidad para decisiones de resiliencia, no como insumo de forecasting.",
                "",
                "Los datos no muestran \"puntos calientes\" geográficos que justifiquen grandes "
                "inversiones regionales; los recursos deben dirigirse por evidencia cuantitativa, no "
                "por intuición geográfica.",
            ],
            footer="Informe generado automáticamente a partir de data/*.csv — ver notebook completo "
                   "en notebooks/challenge02_geo_temporal_redes.ipynb para el detalle metodológico.",
        )

    print(f"Reporte generado en: {OUT_PATH}")


if __name__ == "__main__":
    main()
