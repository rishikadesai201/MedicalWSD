from pathlib import Path

import pytest

from medsense.inference import (
    ModelUnavailableError,
    load_predictor,
    predict_sentence,
    validate_request,
)
from medsense.training.train_inference_model import train_inference_model


ROOT = Path(__file__).resolve().parents[1]


def test_request_validation_handles_empty_missing_and_unsupported_inputs():
    assert validate_request("  ", "PE") == "Enter a sentence to disambiguate."
    assert "not present" in validate_request("CT was reviewed today.", "PE")
    assert "more than once" in validate_request("PE and later PE are both mentioned.", "PE")
    assert "not in the current abbreviation inventory" in validate_request(
        "The XYZ finding was noted.", "XYZ"
    )
    assert "AP is excluded" in validate_request("AP view was acquired.", "AP")
    assert validate_request("The PE subsection is listed.", "PE") is None


def test_missing_saved_model_returns_clear_loading_error(tmp_path):
    with pytest.raises(ModelUnavailableError, match="No saved reviewed-v1 model"):
        load_predictor("tfidf_linear_svm", tmp_path)


def test_prediction_wrapper_uses_model_output_and_margin_label():
    class FakePredictor:
        def predict_one(self, example):
            assert example == {
                "text": "PE was listed after a clot was seen.",
                "target_abbreviation": "PE",
            }
            return "Pulmonary embolism", 0.73

    result = predict_sentence(
        "PE was listed after a clot was seen.",
        "PE",
        "tfidf_linear_svm",
        predictor_loader=lambda name: FakePredictor(),
    )
    assert result == {
        "predicted_sense": "Pulmonary embolism",
        "score": 0.73,
        "score_kind": "uncalibrated decision margin; not a probability",
    }


def test_saved_training_artifact_loads_and_predicts_supported_senses(tmp_path):
    artifact_dir = tmp_path / "reviewed_v1_model"
    metadata = train_inference_model(
        dataset_path=ROOT / "data/synthetic/reviewed_v1.jsonl",
        output_dir=artifact_dir,
        config_path=ROOT / "configs/baseline.yaml",
    )
    model = load_predictor("tfidf_linear_svm", artifact_dir)
    result = predict_sentence(
        "The echo report records PA pressure near the right ventricle.",
        "PA",
        predictor_loader=lambda _name: model,
    )

    assert set(metadata["supported_abbreviations_and_senses"]) == {"PA", "PE"}
    assert "AP" in metadata["excluded_abbreviations"]
    assert metadata["validation_or_test_used_for_training_or_selection"] is False
    assert result["predicted_sense"] in metadata["supported_abbreviations_and_senses"]["PA"]
    assert result["score_kind"].startswith("uncalibrated decision margin")
