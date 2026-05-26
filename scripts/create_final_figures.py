from pathlib import Path
import json

import pandas as pd
import matplotlib.pyplot as plt

Path("figures/final").mkdir(parents=True, exist_ok=True)

# -------------------------
# Figure 1: DLPFC domains
# -------------------------
coords = pd.read_csv("data/srt_marker_q1/coordinates.csv")
labels = pd.read_csv("data/srt_marker_q1/domain_labels.csv")
df = coords.merge(labels, on="spot_id")

plt.figure(figsize=(6, 5))
for domain, sub in df.groupby("domain"):
    plt.scatter(sub["x"], sub["y"], s=8, label=domain)
plt.gca().invert_yaxis()
plt.title("DLPFC 151673 ground-truth cortical domains")
plt.xlabel("array_col")
plt.ylabel("array_row")
plt.legend(markerscale=2, bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
plt.tight_layout()
plt.savefig("figures/final/figure_1_dlpfc_ground_truth_domains.png", dpi=300)
plt.close()

# -------------------------
# Figure 2: Q1 NMI ranking
# -------------------------
q1_metrics = pd.read_csv("answer_keys/srt_accuracy_q1_metrics.csv")
q1_metrics = q1_metrics.sort_values("nmi", ascending=False)

plt.figure(figsize=(6, 4))
plt.bar(q1_metrics["method"], q1_metrics["nmi"])
plt.title("Q1: Clustering prediction performance by NMI")
plt.ylabel("NMI")
plt.xticks(rotation=30, ha="right")
plt.ylim(0, max(q1_metrics["nmi"]) * 1.2)
plt.tight_layout()
plt.savefig("figures/final/figure_2_q1_nmi_ranking.png", dpi=300)
plt.close()

# -------------------------
# Figure 3: Q3 metric tradeoff
# -------------------------
q3 = json.load(open("answer_keys/srt_noncontinuous_q1_answer.json"))["expected"]

tradeoff = pd.DataFrame([
    {
        "Method": "spatial_smooth_method",
        "Global NMI": q3["nmi_spatial_smooth_method"],
        "Rare-domain recall": q3["rare_domain_recall_spatial_smooth_method"],
    },
    {
        "Method": "expression_weighted_method",
        "Global NMI": q3["nmi_expression_weighted_method"],
        "Rare-domain recall": q3["rare_domain_recall_expression_weighted_method"],
    },
])

x = range(len(tradeoff))
width = 0.35

plt.figure(figsize=(7, 4))
plt.bar([i - width/2 for i in x], tradeoff["Global NMI"], width, label="Global NMI")
plt.bar([i + width/2 for i in x], tradeoff["Rare-domain recall"], width, label="Rare-domain recall")
plt.xticks(list(x), tradeoff["Method"], rotation=20, ha="right")
plt.ylabel("Score")
plt.title("Q3: Global accuracy can hide rare-domain failure")
plt.legend()
plt.tight_layout()
plt.savefig("figures/final/figure_3_q3_nmi_vs_rare_domain_recall.png", dpi=300)
plt.close()

# -------------------------
# Figure 4: Q3 spatial maps
# -------------------------
coords = pd.read_csv("data/srt_noncontinuous_q1/coordinates.csv")
gt = pd.read_csv("data/srt_noncontinuous_q1/ground_truth_domains.csv")
pred = pd.read_csv("data/srt_noncontinuous_q1/method_predictions.csv")

q3df = coords.merge(gt, on="spot_id").merge(pred, on="spot_id")

plots = [
    ("ground_truth", "Q3 synthetic ground truth"),
    ("spatial_smooth_method", "spatial_smooth_method"),
    ("expression_weighted_method", "expression_weighted_method"),
]

for col, title in plots:
    plt.figure(figsize=(6, 5))
    for label, sub in q3df.groupby(col):
        size = 18 if label == "rare_immune_islands" else 7
        plt.scatter(sub["x"], sub["y"], s=size, label=label)
    plt.gca().invert_yaxis()
    plt.title(title)
    plt.xlabel("array_col")
    plt.ylabel("array_row")
    plt.legend(markerscale=2, bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=7)
    plt.tight_layout()
    safe_col = col.replace("_", "-")
    plt.savefig(f"figures/final/figure_4_q3_spatial_map_{safe_col}.png", dpi=300)
    plt.close()

print("Created final figures:")
for path in sorted(Path("figures/final").glob("*.png")):
    print(" -", path)
