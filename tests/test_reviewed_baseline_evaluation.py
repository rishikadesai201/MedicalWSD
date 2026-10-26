import json
from pathlib import Path

from medsense.training.evaluate_reviewed_baselines import run_reviewed_baselines


ROOT = Path(__file__).resolve().parents[1]


def test_reviewed_baselines_exclude_ap_and_save_test_metrics(tmp_path):
    output = tmp_path / "reviewed_baseline"
    result = run_reviewed_baselines(
        dataset_path=ROOT / "data/synthetic/reviewed_v1.jsonl",
        output_dir=output,
        config_path=ROOT / "configs/baseline.yaml",
    )

    assert result["run_config"]["eligible_abbreviations"] == ["PA", "PE"]
    assert "AP" in result["run_config"]["excluded_abbreviations"]
    assert "AP::Anteroposterior" not in result["run_config"]["class_counts_by_split"]["train"]
    for model_name in ("tfidf_logistic_regression", "tfidf_linear_svm"):
        metrics = result["results"][model_name]
        predictions = [json.loads(line) for line in
                       (output / f"{model_name}_test_predictions.jsonl").read_text(encoding="utf-8").splitlines()]
        assert metrics["n_evaluated_examples"] == metrics["n_test"] == 10
        assert metrics["evaluated_abbreviations"] == ["PA", "PE"]
        assert len(metrics["per_sense"]) == len(metrics["confusion_matrix"]) == 4
        assert len(predictions) == 10
        assert {row["target_abbreviation"] for row in predictions} == {"PA", "PE"}
        assert all(row["split"] == "test" for row in predictions)
        assert (output / f"{model_name}_metrics.json").exists()
