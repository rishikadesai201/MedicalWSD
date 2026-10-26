import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_error_report_matches_saved_baseline_predictions():
    artifact_dir = ROOT / "outputs/baseline"
    dataset = {
        row["example_id"]: row
        for row in map(json.loads, (ROOT / "data/synthetic/verified_examples.jsonl")
                       .read_text(encoding="utf-8").splitlines())
    }
    errors = {}
    for model in ("tfidf_logistic_regression", "tfidf_linear_svm"):
        predictions = [
            json.loads(line)
            for line in (artifact_dir / f"{model}_test_predictions.jsonl")
            .read_text(encoding="utf-8").splitlines()
        ]
        errors[model] = {row["example_id"]: row for row in predictions if not row["correct"]}

    assert len(errors["tfidf_logistic_regression"]) == 3
    assert errors["tfidf_logistic_regression"].keys() == errors["tfidf_linear_svm"].keys()
    report = (ROOT / "docs/baseline_error_analysis.md").read_text(encoding="utf-8")
    for example_id, prediction in errors["tfidf_logistic_regression"].items():
        assert dataset[example_id]["text"] in report
        assert prediction["gold_sense"] in report
        assert prediction["predicted_sense"] in report
