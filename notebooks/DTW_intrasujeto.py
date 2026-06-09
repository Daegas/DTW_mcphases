# ============================================================
# Evaluación de estrategias de normalización para DTW
# ============================================================
# 🤖 Hecho con IA completamente, basado en prueba y error hecha DTW.ipynb 
# Motivación: Comparación clara para reporte
# Objetivo:
# Determinar cómo afecta la normalización de las señales a la
# estructura de similitud entre sujetos y a los resultados del
# clustering basado en Dynamic Time Warping (DTW).
#
# Se comparan tres enfoques:
#
# 1. raw
#    Se utilizan las señales originales sin transformación.
#    La distancia DTW refleja tanto diferencias de magnitud
#    como de dinámica temporal.
#
# 2. subject_zscore
#    Cada señal se estandariza dentro de cada sujeto.
#    Se eliminan diferencias de nivel y amplitud entre sujetos,
#    permitiendo comparar principalmente la forma y sincronización
#    temporal de las señales.
#
# 3. global_zscore
#    Cada señal se estandariza utilizando la media y desviación
#    estándar de toda la cohorte.
#    Se conservan diferencias entre sujetos, pero todas las
#    variables contribuyen de manera comparable a la distancia.
#
# Para cada estrategia se:
#   - Calcula la matriz de distancias DTW multivariada.
#   - Aplica clustering jerárquico (average y complete linkage).
#   - Evalúa la calidad de los clusters mediante silhouette score.
#   - Analiza la distribución de tamaños de los clusters.
#
# El objetivo final es identificar la estrategia de
# preprocesamiento que produce resultados más interpretables
# y coherentes con la pregunta biológica del estudio.
# ============================================================

import numpy as np
import pandas as pd

from dtaidistance import dtw_ndim
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from pathlib import Path
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.cluster.hierarchy import dendrogram

from sklearn.manifold import TSNE
import umap


# ============================================================
# CONFIG
# ============================================================
# Columnas de señales fisiológicas disponibles
SIGNAL_COLS = ['movement_pct', 'rhr_value', 'hr_pc1', 'hr_pc2', 'hr_pc3',
               'lh', 'estrogen', 'wtmp_pc1', 'wtmp_pc2', 'wtmp_pc3']
MV_SIGNALS = SIGNAL_COLS
LINKAGES = ["average", "complete"]


load_dotenv()

DATA_PATH = Path(os.getenv("DATA_PATH"))
OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH"))

print(DATA_PATH)
print(f"Data path: {DATA_PATH}")
print(f"Output path: {OUTPUT_PATH}")


# ============================================================
# Data
# ============================================================

# ── Carga ─────────────────────────────────────────────────────────────────────
df_clean = pd.read_csv(OUTPUT_PATH / "df_clean_final.csv")



print(f'Shape: {df_clean.shape}')
print(f'Sujetos: {df_clean["id"].nunique()}')
print(f'Días por sujeto (mediana): {df_clean.groupby("id")["day_in_study"].count().median()}')
print(df_clean.head())
print(df_clean[["wtmp_pc1"]].isna().sum())

# ============================================================
# FUNCIONES
# ============================================================

def build_series_dict(df, signals, mode="raw"):
    """
    mode:
        raw              -> datos crudos
        subject_zscore   -> estandarización por sujeto
        global_zscore    -> estandarización global por variable
    """

    df_work = df.copy()

    # --------------------------------------------------------
    # Opción C
    # --------------------------------------------------------
    if mode == "global_zscore":

        for sig in signals:
            scaler = StandardScaler()
            df_work[sig] = scaler.fit_transform(df_work[[sig]])

    subjects = sorted(df_work["id"].unique())

    series_dict = {}

    for sid in subjects:

        sub = (
            df_work[df_work["id"] == sid]
            .sort_values("day_in_study")
        )

        arr = []

        for sig in signals:

            vals = sub[sig].values.astype(float)

            # ------------------------------------------------
            # Opción A
            # ------------------------------------------------
            if mode == "subject_zscore":

                mu = vals.mean()
                sd = vals.std()

                vals = (vals - mu) / (sd + 1e-8)

            arr.append(vals)

        series_dict[sid] = np.column_stack(arr)

    return series_dict


def compute_dtw_matrix(series_dict):

    subjects = list(series_dict.keys())
    n = len(subjects)

    D = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):

            d = dtw_ndim.distance(
                series_dict[subjects[i]].astype(np.double),
                series_dict[subjects[j]].astype(np.double)
            )

            D[i, j] = d
            D[j, i] = d

    return D, subjects


def evaluate_clustering(dtw_matrix, subjects, linkage_method):

    condensed = squareform(dtw_matrix)

    Z = linkage(
        condensed,
        method=linkage_method
    )

    sil_scores = {}

    n = len(dtw_matrix)

    for k in range(2, min(10, n)):

        labels = fcluster(
            Z,
            k,
            criterion="maxclust"
        )

        sil_scores[k] = silhouette_score(
            dtw_matrix,
            labels,
            metric="precomputed"
        )

    k_opt = max(sil_scores, key=sil_scores.get)

    labels = fcluster(
        Z,
        k_opt,
        criterion="maxclust"
    )

    cluster_sizes = (
        pd.Series(labels)
        .value_counts()
        .sort_index()
        .to_dict()
    )

    cluster_map = pd.DataFrame({
        "id": subjects,
        "cluster": labels
    })

    counts = cluster_map["cluster"].value_counts()

    small_clusters = counts[counts <= 2].index

    if len(small_clusters) > 0:
        print("\nPosibles outliers:")
        print(
            cluster_map[
                cluster_map["cluster"].isin(small_clusters)
            ]
        )

    return {
        "k_opt": k_opt,
        "best_silhouette": sil_scores[k_opt],
        "cluster_sizes": cluster_sizes,
        "all_scores": sil_scores,
        "labels": labels,
        "Z": Z
    }

def save_dendrogram(
    Z,
    subjects,
    silhouette,
    mode,
    linkage_method,
    output_dir
):

    plt.figure(figsize=(14, 6))

    dendrogram(
        Z,
        labels=subjects,
        leaf_rotation=90
    )

    plt.title(
        f"Dendrogram\n"
        f"{mode} | {linkage_method} | "
        f"silhouette={silhouette:.3f}"
    )

    plt.tight_layout()

    plt.savefig(
        output_dir /
        f"comp_dendograma_{mode}_{linkage_method}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_umap(
    dtw_matrix,
    labels,
    mode,
    linkage_method,
    output_dir
):

    reducer = umap.UMAP(
        metric="precomputed",
        random_state=42,
        n_neighbors=min(10, len(labels)-1)
    )

    emb = reducer.fit_transform(dtw_matrix)

    plt.figure(figsize=(8,6))

    sns.scatterplot(
        x=emb[:,0],
        y=emb[:,1],
        hue=labels,
        palette="tab10"
    )

    plt.title(
        f"UMAP\n"
        f"{mode} | {linkage_method}"
    )

    plt.tight_layout()

    plt.savefig(
        output_dir /
        f"comp_umap_{mode}_{linkage_method}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_tsne(
    dtw_matrix,
    labels,
    mode,
    linkage_method,
    output_dir
):

    tsne = TSNE(
        n_components=2,
        metric="precomputed",
        init="random",      # <- importante
        perplexity=min(10, len(labels)-1),
        random_state=42
    )

    emb = tsne.fit_transform(dtw_matrix)

    plt.figure(figsize=(8,6))

    sns.scatterplot(
        x=emb[:,0],
        y=emb[:,1],
        hue=labels,
        palette="tab10"
    )

    plt.title(
        f"t-SNE\n"
        f"{mode} | {linkage_method}"
    )

    plt.tight_layout()

    plt.savefig(
        output_dir /
        f"comp_tsne_{mode}_{linkage_method}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ============================================================
# EXPERIMENTO
# ============================================================

results = []

for mode in [
    "raw",
    "subject_zscore",
    "global_zscore"
]:

    print("\n" + "=" * 60)
    print(f"MODE: {mode}")
    print("=" * 60)

    series_dict = build_series_dict(
        df_clean,
        MV_SIGNALS,
        mode=mode
    )

    dtw_matrix, subjects = compute_dtw_matrix(
        series_dict
    )

    upper = dtw_matrix[
        np.triu_indices_from(
            dtw_matrix,
            k=1
        )
    ]

    print("\nDTW distribution")
    print(pd.Series(upper).describe())

    for linkage_method in LINKAGES:

        res = evaluate_clustering(
            dtw_matrix,
            subjects,
            linkage_method
        )

        print(f"\nLinkage: {linkage_method}")
        print(f"k óptimo: {res['k_opt']}")
        print(
            f"silhouette: "
            f"{res['best_silhouette']:.4f}"
        )
        print(
            f"clusters: "
            f"{res['cluster_sizes']}"
        )

        save_dendrogram(
            Z=res["Z"],
            subjects=subjects,
            silhouette=res["best_silhouette"],
            mode=mode,
            linkage_method=linkage_method,
            output_dir=OUTPUT_PATH
        )

        save_umap(
            dtw_matrix=dtw_matrix,
            labels=res["labels"],
            mode=mode,
            linkage_method=linkage_method,
            output_dir=OUTPUT_PATH
        )

        save_tsne(
            dtw_matrix=dtw_matrix,
            labels=res["labels"],
            mode=mode,
            linkage_method=linkage_method,
            output_dir=OUTPUT_PATH
        )

        results.append({
            "mode": mode,
            "linkage": linkage_method,
            "k_opt": res["k_opt"],
            "silhouette": res["best_silhouette"],
            "cluster_sizes": str(res["cluster_sizes"])
        })

# ============================================================
# RESUMEN FINAL
# ============================================================

results_df = pd.DataFrame(results)

print("\n")
print("=" * 60)
print("RESUMEN")
print("=" * 60)

print(
    results_df.sort_values(
        "silhouette",
        ascending=False
    )
)
