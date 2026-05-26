import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import normalized_mutual_info_score
from scipy.optimize import linear_sum_assignment

np.random.seed(123)

Path("data/srt_noncontinuous_q1").mkdir(parents=True, exist_ok=True)
Path("answer_keys").mkdir(exist_ok=True)

# Use real DLPFC coordinates from the marker task
coords = pd.read_csv("data/srt_marker_q1/coordinates.csv")
labels = pd.read_csv("data/srt_marker_q1/domain_labels.csv")

df = coords.merge(labels, on="spot_id", how="inner").copy()

# We will create a synthetic rare noncontinuous domain using real spatial coordinates.
# Pick several separated islands across the tissue coordinate plane.

island_centers = [
    (20, 20),
    (90, 20),
    (25, 70),
    (95, 75),
    (60, 50),
]

rare_ids = set()

for cx, cy in island_centers:
    d = np.sqrt((df["x"] - cx) ** 2 + (df["y"] - cy) ** 2)
    nearest = df.loc[d.sort_values().index[:18], "spot_id"]
    rare_ids.update(nearest.tolist())

# Limit rare domain to a controlled size
rare_ids = set(list(rare_ids)[:85])

df["ground_truth"] = df["domain"].astype(str)
df.loc[df["spot_id"].isin(rare_ids), "ground_truth"] = "rare_immune_islands"

# Method 1: spatial_smooth_method
# Mostly preserves large smooth cortical layers but washes out rare islands
df["spatial_smooth_method"] = df["domain"].astype(str)
df.loc[df["spot_id"].isin(rare_ids), "spatial_smooth_method"] = df.loc[
    df["spot_id"].isin(rare_ids), "domain"
].astype(str)

# Add mild noise to large domains
noise_mask = np.random.rand(len(df)) < 0.08
large_labels = sorted([x for x in df["domain"].astype(str).unique()])
for i in df.index[noise_mask]:
    current = df.at[i, "spatial_smooth_method"]
    choices = [x for x in large_labels if x != current]
    df.at[i, "spatial_smooth_method"] = np.random.choice(choices)

# Method 2: expression_weighted_method
# Recovers most rare islands but has more global label noise
df["expression_weighted_method"] = df["domain"].astype(str)

# Recover rare domain for most rare spots, miss some
rare_mask = df["spot_id"].isin(rare_ids)
rare_recover_mask = rare_mask & (np.random.rand(len(df)) < 0.82)
df.loc[rare_recover_mask, "expression_weighted_method"] = "rare_immune_islands"

# Rare spots not recovered keep their original domain
# Add more global noise to non-rare domains so global NMI is not trivially dominant
nonrare_mask = ~rare_mask
noise_mask2 = nonrare_mask & (np.random.rand(len(df)) < 0.16)
all_pred_labels = large_labels + ["rare_immune_islands"]

for i in df.index[noise_mask2]:
    current = df.at[i, "expression_weighted_method"]
    choices = [x for x in all_pred_labels if x != current]
    df.at[i, "expression_weighted_method"] = np.random.choice(choices)

# Save files
df[["spot_id", "x", "y"]].to_csv("data/srt_noncontinuous_q1/coordinates.csv", index=False)
df[["spot_id", "ground_truth"]].to_csv("data/srt_noncontinuous_q1/ground_truth_domains.csv", index=False)
df[["spot_id", "spatial_smooth_method", "expression_weighted_method"]].to_csv(
    "data/srt_noncontinuous_q1/method_predictions.csv", index=False
)

# Helper: optimally map predicted labels to true labels and compute recall for rare domain
def rare_domain_recall(y_true, y_pred, rare_label="rare_immune_islands"):
    y_true = np.asarray(y_true).astype(str)
    y_pred = np.asarray(y_pred).astype(str)

    true_labels = sorted(pd.unique(y_true))
    pred_labels = sorted(pd.unique(y_pred))

    confusion = np.zeros((len(true_labels), len(pred_labels)), dtype=int)
    true_index = {lab: i for i, lab in enumerate(true_labels)}
    pred_index = {lab: j for j, lab in enumerate(pred_labels)}

    for t, p in zip(y_true, y_pred):
        confusion[true_index[t], pred_index[p]] += 1

    # Maximize total matched cells
    row_ind, col_ind = linear_sum_assignment(-confusion)

    pred_to_true = {}
    for r, c in zip(row_ind, col_ind):
        pred_to_true[pred_labels[c]] = true_labels[r]

    mapped_pred = np.array([pred_to_true.get(p, "unmatched") for p in y_pred])

    rare_true = y_true == rare_label
    recovered = (mapped_pred == rare_label) & rare_true

    return recovered.sum() / rare_true.sum(), pred_to_true

y_true = df["ground_truth"].astype(str)

answer = {}
for method in ["spatial_smooth_method", "expression_weighted_method"]:
    y_pred = df[method].astype(str)
    nmi = normalized_mutual_info_score(y_true, y_pred)
    recall, mapping = rare_domain_recall(y_true, y_pred)

    answer[method] = {
        "nmi": round(float(nmi), 3),
        "rare_domain_recall": round(float(recall), 3),
        "mapping": mapping,
    }

q3_expected = {
    "question_id": "srt-noncontinuous-q1",
    "expected": {
        "nmi_spatial_smooth_method": answer["spatial_smooth_method"]["nmi"],
        "nmi_expression_weighted_method": answer["expression_weighted_method"]["nmi"],
        "rare_domain_recall_spatial_smooth_method": answer["spatial_smooth_method"]["rare_domain_recall"],
        "rare_domain_recall_expression_weighted_method": answer["expression_weighted_method"]["rare_domain_recall"],
        "better_method_for_rare_domain": "expression_weighted_method",
    },
    "notes": {
        "data_type": "synthetic rare noncontinuous domain generated using real DLPFC 151673 coordinates",
        "rare_domain_size": int((df["ground_truth"] == "rare_immune_islands").sum()),
        "total_spots": int(len(df)),
    },
}

with open("answer_keys/srt_noncontinuous_q1_answer.json", "w") as f:
    json.dump(q3_expected, f, indent=2)

print("Created Q3 files:")
print("data/srt_noncontinuous_q1/coordinates.csv")
print("data/srt_noncontinuous_q1/ground_truth_domains.csv")
print("data/srt_noncontinuous_q1/method_predictions.csv")
print("answer_keys/srt_noncontinuous_q1_answer.json")
print()
print(json.dumps(q3_expected, indent=2))
