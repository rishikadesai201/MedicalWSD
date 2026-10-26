import json
from pathlib import Path

import pytest

from medsense.evaluation.visualization_data import (
    EvaluationArtifactsError,
    MODEL_NAMES,
    load_reviewed_evaluation,
)


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_data_uses_saved_metrics_predictions_and_reviewed_dataset():
    result = load_reviewed_evaluation(
        ROOT / "outputs/reviewed_v1_traditional_baseline",
        ROOT / "data/synthetic/reviewed_v1.jsonl",
    )
    saved_summary = json.loads((ROOT / "outputs/reviewed_v1_traditional_baseline/summary_metrics.json")
                              .read_text(encoding="utf-8"))
    assert result["n_test_examples"] == 10
    assert result["metrics"] == saved_summary
    assert result["metrics"][MODEL_NAMES[0]]["accuracy"] == 0.7
    assert result["metrics"][MODEL_NAMES[1]]["accuracy"] == 0.8
    assert len(result["predictions"][MODEL_NAMES[0]]) == 10
    assert any(row["class"] == "AP — Anteroposterior" and row["train"] + row["validation"] + row["test"] == 0
               for row in result["dataset_composition"])
    assert result["prediction_errors"][MODEL_NAMES[0]]


def test_dashboard_reports_missing_and_malformed_artifacts(tmp_path):
    with pytest.raises(EvaluationArtifactsError, match="missing"):
        load_reviewed_evaluation(tmp_path, ROOT / "data/synthetic/reviewed_v1.jsonl")

    (tmp_path / "run_config.json").write_text("[]", encoding="utf-8")
    with pytest.raises(EvaluationArtifactsError, match="JSON object"):
        load_reviewed_evaluation(tmp_path, ROOT / "data/synthetic/reviewed_v1.jsonl")
