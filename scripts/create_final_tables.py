import json
import pandas as pd
from pathlib import Path

Path("tables/final").mkdir(parents=True, exist_ok=True)

# Main benchmark question summary
question_summary = pd.DataFrame([
    {
        "Question": "Q1: srt-accuracy-q1",
        "Dataset": "DLPFC 151673",
        "Task": "Evaluate predicted spatial domains against cortical-layer annotations",
        "Main metric/output": "NMI, homogeneity, completeness, ranking",
        "Result": "Pass"
    },
    {
        "Question": "Q2: srt-marker-q1",
        "Dataset": "DLPFC 151673",
        "Task": "Identify domain marker genes and compute Moran's I",
        "Main metric/output": "Top marker genes, Moran's I",
        "Result": "Pass with numeric tolerance"
    },
    {
        "Question": "Q3: srt-noncontinuous-q1",
        "Dataset": "Real DLPFC coordinates + synthetic rare domain",
        "Task": "Compare global NMI versus rare-domain recovery",
        "Main metric/output": "Global NMI, rare-domain recall",
        "Result": "Pass"
    },
])

question_summary.to_csv("tables/final/table_1_question_summary.csv", index=False)

# Q1 metrics
q1 = json.load(open("answer_keys/srt_accuracy_q1_answer.json"))
q1_metrics = pd.DataFrame(q1["all_method_metrics"])
q1_metrics.to_csv("tables/final/table_2_q1_method_metrics.csv", index=False)

# Q2 marker genes
q2 = json.load(open("answer_keys/srt_marker_q1_answer.json"))["expected"]
q2_table = pd.DataFrame([
    {
        "Domain": domain,
        "Top marker gene": vals["top_marker_gene"],
        "Moran's I": vals["morans_i"]
    }
    for domain, vals in q2.items()
])
q2_table.to_csv("tables/final/table_3_q2_marker_genes.csv", index=False)

# Q3 metrics
q3 = json.load(open("answer_keys/srt_noncontinuous_q1_answer.json"))["expected"]
q3_table = pd.DataFrame([
    {
        "Method": "spatial_smooth_method",
        "Global NMI": q3["nmi_spatial_smooth_method"],
        "Rare-domain recall": q3["rare_domain_recall_spatial_smooth_method"],
        "Better for rare domain?": "No"
    },
    {
        "Method": "expression_weighted_method",
        "Global NMI": q3["nmi_expression_weighted_method"],
        "Rare-domain recall": q3["rare_domain_recall_expression_weighted_method"],
        "Better for rare domain?": "Yes"
    },
])
q3_table.to_csv("tables/final/table_4_q3_tradeoff.csv", index=False)

print("Created final tables:")
for path in sorted(Path("tables/final").glob("*.csv")):
    print(" -", path)
