import json
from pathlib import Path

TOL = 0.01

PROJECT = Path(".")
RUNS_DIR = PROJECT / "runs"
ANSWER_DIR = PROJECT / "answer_keys"

def load_json(path):
    with open(path) as f:
        return json.load(f)

def parse_answer(result_json):
    result = load_json(result_json)
    answer_str = result["output"]["answer"]
    return json.loads(answer_str)

def latest_run_dir():
    runs = sorted(
        [p for p in RUNS_DIR.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if not runs:
        raise FileNotFoundError("No run folders found in runs/. Copy benchmark run folders into runs/ first.")
    return runs[0]

def approx_equal(a, b, tol=TOL):
    return abs(float(a) - float(b)) <= tol

def grade_q1(run_dir):
    qid = "srt-accuracy-q1"
    result_path = run_dir / "questions" / qid / "result.json"
    if not result_path.exists():
        return {"question_id": qid, "status": "missing"}

    pred = parse_answer(result_path)
    key = load_json(ANSWER_DIR / "srt_accuracy_q1_answer.json")["expected"]

    checks = {
        "best_method": pred.get("best_method") == key["best_method"],
        "nmi": approx_equal(pred.get("nmi"), key["nmi"], 0.001),
        "homogeneity": approx_equal(pred.get("homogeneity"), key["homogeneity"], 0.001),
        "completeness": approx_equal(pred.get("completeness"), key["completeness"], 0.001),
        "method_ranking_by_nmi": pred.get("method_ranking_by_nmi") == key["method_ranking_by_nmi"],
    }

    return {
        "question_id": qid,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "predicted": pred,
        "expected": key,
    }

def grade_q2(run_dir):
    qid = "srt-marker-q1"
    result_path = run_dir / "questions" / qid / "result.json"
    if not result_path.exists():
        return {"question_id": qid, "status": "missing"}

    pred = parse_answer(result_path)
    key = load_json(ANSWER_DIR / "srt_marker_q1_answer.json")["expected"]

    checks = {}
    for domain, expected_vals in key.items():
        if domain not in pred:
            checks[domain] = {
                "present": False,
                "marker_gene": False,
                "morans_i_within_tolerance": False,
            }
            continue

        checks[domain] = {
            "present": True,
            "marker_gene": pred[domain].get("top_marker_gene") == expected_vals["top_marker_gene"],
            "morans_i_within_tolerance": approx_equal(
                pred[domain].get("morans_i"),
                expected_vals["morans_i"],
                TOL
            ),
        }

    all_pass = all(
        domain_checks["present"]
        and domain_checks["marker_gene"]
        and domain_checks["morans_i_within_tolerance"]
        for domain_checks in checks.values()
    )

    exact_morans = {
        domain: pred.get(domain, {}).get("morans_i") == key[domain]["morans_i"]
        for domain in key
    }

    return {
        "question_id": qid,
        "status": "pass_with_tolerance" if all_pass else "fail",
        "checks": checks,
        "exact_morans_i_match": exact_morans,
        "predicted": pred,
        "expected": key,
        "tolerance": TOL,
    }

def grade_q3(run_dir):
    qid = "srt-noncontinuous-q1"
    result_path = run_dir / "questions" / qid / "result.json"
    if not result_path.exists():
        return {"question_id": qid, "status": "missing"}

    pred = parse_answer(result_path)
    key = load_json(ANSWER_DIR / "srt_noncontinuous_q1_answer.json")["expected"]

    checks = {
        "nmi_spatial_smooth_method": approx_equal(
            pred.get("nmi_spatial_smooth_method"),
            key["nmi_spatial_smooth_method"],
            0.001
        ),
        "nmi_expression_weighted_method": approx_equal(
            pred.get("nmi_expression_weighted_method"),
            key["nmi_expression_weighted_method"],
            0.001
        ),
        "rare_domain_recall_spatial_smooth_method": approx_equal(
            pred.get("rare_domain_recall_spatial_smooth_method"),
            key["rare_domain_recall_spatial_smooth_method"],
            0.001
        ),
        "rare_domain_recall_expression_weighted_method": approx_equal(
            pred.get("rare_domain_recall_expression_weighted_method"),
            key["rare_domain_recall_expression_weighted_method"],
            0.001
        ),
        "better_method_for_rare_domain": pred.get("better_method_for_rare_domain") == key["better_method_for_rare_domain"],
    }

    return {
        "question_id": qid,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "predicted": pred,
        "expected": key,
    }

def main():
    run_dir = latest_run_dir()
    print(f"Grading run: {run_dir}")

    results = [
        grade_q1(run_dir),
        grade_q2(run_dir),
        grade_q3(run_dir),
    ]

    print("\nSummary:")
    for r in results:
        print(f"- {r['question_id']}: {r['status']}")

    out_path = PROJECT / "reports" / "grading_summary_latest.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(
            {
                "run_dir": str(run_dir),
                "numeric_tolerance": TOL,
                "results": results,
            },
            f,
            indent=2
        )

    print(f"\nWrote detailed grading summary to: {out_path}")

    print("\nDetailed checks:")
    for r in results:
        print(f"\n{r['question_id']} — {r['status']}")
        if "checks" in r:
            print(json.dumps(r["checks"], indent=2))

if __name__ == "__main__":
    main()
