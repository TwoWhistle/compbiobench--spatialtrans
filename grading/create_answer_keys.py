import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.metrics import (
    normalized_mutual_info_score,
    homogeneity_score,
    completeness_score,
)

Path("answer_keys").mkdir(exist_ok=True)


def round_float(x):
    return round(float(x), 3)


# ----------------------------
# Q1: clustering accuracy
# ----------------------------

ann = pd.read_csv("data/srt_accuracy_q1/dlpfc_151673_annotations.csv")
pred = pd.read_csv("data/srt_accuracy_q1/dlpfc_151673_predictions.csv")

merged = ann.merge(pred, on="spot_id", how="inner")

if len(merged) != len(ann):
    raise ValueError("Annotation and prediction files did not fully align.")

ground_truth = merged["ground_truth"].astype(str)

method_cols = [c for c in pred.columns if c != "spot_id"]

rows = []
for method in method_cols:
    y_pred = merged[method].astype(str)

    rows.append({
        "method": method,
        "nmi": normalized_mutual_info_score(ground_truth, y_pred),
        "homogeneity": homogeneity_score(ground_truth, y_pred),
        "completeness": completeness_score(ground_truth, y_pred),
    })

metrics = pd.DataFrame(rows).sort_values("nmi", ascending=False)

best = metrics.iloc[0]

q1_answer = {
    "question_id": "srt-accuracy-q1",
    "expected": {
        "best_method": str(best["method"]),
        "nmi": round_float(best["nmi"]),
        "homogeneity": round_float(best["homogeneity"]),
        "completeness": round_float(best["completeness"]),
        "method_ranking_by_nmi": metrics["method"].tolist(),
    },
    "all_method_metrics": [
        {
            "method": str(row["method"]),
            "nmi": round_float(row["nmi"]),
            "homogeneity": round_float(row["homogeneity"]),
            "completeness": round_float(row["completeness"]),
        }
        for _, row in metrics.iterrows()
    ],
}

with open("answer_keys/srt_accuracy_q1_answer.json", "w") as f:
    json.dump(q1_answer, f, indent=2)

metrics.to_csv("answer_keys/srt_accuracy_q1_metrics.csv", index=False)


# ----------------------------
# Q2: marker genes + Moran's I
# ----------------------------

expr = pd.read_csv("data/srt_marker_q1/expression_matrix_small.csv")
coords = pd.read_csv("data/srt_marker_q1/coordinates.csv")
labels = pd.read_csv("data/srt_marker_q1/domain_labels.csv")

df = labels.merge(coords, on="spot_id", how="inner").merge(expr, on="spot_id", how="inner")

if len(df) != len(labels):
    raise ValueError("Marker task files did not fully align.")

gene_cols = [c for c in expr.columns if c != "spot_id"]
domains = sorted(df["domain"].astype(str).unique())

# Build 6-nearest-neighbor graph using spatial coordinates.
xy = df[["x", "y"]].to_numpy(dtype=float)
tree = cKDTree(xy)

# k=7 because first neighbor is the point itself.
_, neighbor_idx = tree.query(xy, k=7)
neighbor_idx = neighbor_idx[:, 1:]

def morans_i(values, neighbor_idx):
    """
    Simple row-neighbor Moran's I for fixed kNN graph.
    W_ij = 1 if j is among i's six nearest neighbors.
    """
    x = np.asarray(values, dtype=float)
    n = len(x)
    x_bar = x.mean()
    z = x - x_bar

    denom = np.sum(z ** 2)
    if denom == 0:
        return np.nan

    numerator = 0.0
    w_sum = 0

    for i in range(n):
        js = neighbor_idx[i]
        numerator += np.sum(z[i] * z[js])
        w_sum += len(js)

    return (n / w_sum) * (numerator / denom)


marker_answer = {}

for domain in domains:
    in_domain = df["domain"].astype(str) == domain
    out_domain = ~in_domain

    mean_in = df.loc[in_domain, gene_cols].mean(axis=0)
    mean_out = df.loc[out_domain, gene_cols].mean(axis=0)

    diff = mean_in - mean_out
    top_gene = str(diff.sort_values(ascending=False).index[0])

    mi = morans_i(df[top_gene].to_numpy(dtype=float), neighbor_idx)

    marker_answer[domain] = {
        "top_marker_gene": top_gene,
        "morans_i": round_float(mi),
    }

q2_answer = {
    "question_id": "srt-marker-q1",
    "expected": marker_answer,
    "method_notes": {
        "marker_selection": "one-vs-rest mean expression difference",
        "spatial_graph": "6 nearest spatial neighbors using x,y coordinates",
        "morans_i": "row-neighbor Moran's I with binary kNN weights"
    }
}

with open("answer_keys/srt_marker_q1_answer.json", "w") as f:
    json.dump(q2_answer, f, indent=2)


print("Created answer keys:")
print("answer_keys/srt_accuracy_q1_answer.json")
print("answer_keys/srt_accuracy_q1_metrics.csv")
print("answer_keys/srt_marker_q1_answer.json")

print("\nQ1 expected:")
print(json.dumps(q1_answer["expected"], indent=2))

print("\nQ2 expected:")
print(json.dumps(q2_answer["expected"], indent=2))
