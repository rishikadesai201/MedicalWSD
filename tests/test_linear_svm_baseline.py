import json
from pathlib import Path

import yaml

from medsense.training.train_baselines import run_linear_svm


ROOT = Path(__file__).resolve().parents[1]


def test_linear_svm_evaluates_existing_split_and_saves_predictions(tmp_path):
    config = yaml.safe_load((ROOT / "configs/baseline.yaml").read_text(encoding="utf-8"))
    config["dataset_path"] = str(ROOT / config["dataset_path"])
    config["dataset_quality_report"] = str(ROOT / config["dataset_quality_report"])
    config["output_dir"] = str(tmp_path)
    config_path = tmp_path / "baseline.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    metrics = run_linear_svm(config_path)
    rows = [json.loads(line) for line in
            (tmp_path / "tfidf_linear_svm_test_predictions.jsonl").read_text(encoding="utf-8").splitlines()]
    saved_metrics = json.loads((tmp_path / "tfidf_linear_svm_metrics.json").read_text(encoding="utf-8"))
    run_config = json.loads((tmp_path / "tfidf_linear_svm_run_config.json").read_text(encoding="utf-8"))

    assert len(rows) == metrics["n_test"] == 36
    assert {row["split"] for row in rows} == {"test"}
    assert saved_metrics == metrics
    assert len(metrics["per_sense"]) == 6
    assert len(metrics["confusion_matrix"]) == 6
    assert all(len(row) == 6 for row in metrics["confusion_matrix"])
    assert run_config["split_sizes"] == {"train": 72, "validation": 24, "test": 36}
    assert "not used for model selection" in run_config["validation_policy"]
