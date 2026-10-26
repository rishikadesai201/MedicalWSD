"""Safe inference helpers for the Streamlit demo."""
from pathlib import Path
import json
import re


MODEL_FILES = {
    "tfidf_linear_svm": "tfidf_linear_svm.joblib",
}
EVALUATED_ABBREVIATIONS = {"PA", "PE"}
ABBREVIATION_SENSES = {
    "PE": ("Physical examination", "Pulmonary embolism"),
    "PA": ("Physician assistant", "Pulmonary artery"),
    "AP": ("Anteroposterior", "Anterior pituitary"),
}
DEFAULT_ARTIFACT_DIR = Path("outputs/reviewed_v1_inference_v1")
EXPECTED_MODEL_VERSION = "reviewed-v1-tfidf-linear-svm-1"


class ModelUnavailableError(RuntimeError):
    """Raised when no compatible, saved estimator can support inference."""


def validate_request(sentence, abbreviation):
    if not sentence or not sentence.strip():
        return "Enter a sentence to disambiguate."
    abbreviation = (abbreviation or "").strip().upper()
    if not abbreviation:
        return "Select or enter an abbreviation."
    if abbreviation not in ABBREVIATION_SENSES:
        return f"{abbreviation} is not in the current abbreviation inventory."
    if abbreviation not in EVALUATED_ABBREVIATIONS:
        return "AP is excluded from the current two-sense evaluation because no AP Anteroposterior examples were accepted."
    pattern = rf"(?<![A-Za-z0-9]){re.escape(abbreviation)}(?![A-Za-z0-9])"
    occurrences = list(re.finditer(pattern, sentence, flags=re.IGNORECASE))
    if not occurrences:
        return f"The selected abbreviation {abbreviation} is not present as a standalone token in the sentence."
    if len(occurrences) > 1:
        return f"The selected abbreviation {abbreviation} occurs more than once; enter a sentence with one target occurrence."
    return None


def load_predictor(model_name, artifact_dir=DEFAULT_ARTIFACT_DIR):
    if model_name not in MODEL_FILES:
        raise ModelUnavailableError(f"Unsupported model choice: {model_name}")
    artifact_dir = Path(artifact_dir)
    path = artifact_dir / MODEL_FILES[model_name]
    metadata_path = artifact_dir / "metadata.json"
    if not path.is_file():
        raise ModelUnavailableError(
            f"No saved reviewed-v1 model is available at {path}."
        )
    if not metadata_path.is_file():
        raise ModelUnavailableError(f"Model metadata is missing: {metadata_path}.")
    try:
        import joblib

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("model_version") != EXPECTED_MODEL_VERSION:
            raise ValueError("model version does not match the expected reviewed-v1 artifact")
        predictor = joblib.load(path)
    except Exception as exc:
        raise ModelUnavailableError(f"Could not load saved model at {path}: {exc}") from exc
    from medsense.models.baseline import TfidfLinearSVM

    if not isinstance(predictor, TfidfLinearSVM):
        raise ModelUnavailableError(f"Saved model at {path} is not a compatible TF-IDF Linear SVM.")
    metadata_senses = metadata.get("supported_abbreviations_and_senses", {})
    model_senses = {
        abbreviation: [str(sense) for sense in fitted[1].classes_]
        for abbreviation, fitted in sorted(predictor.models.items())
    }
    if (set(metadata_senses) != set(predictor.models) or "AP" in predictor.models
            or metadata_senses != model_senses):
        raise ModelUnavailableError("Saved model and metadata disagree about supported abbreviations.")
    return predictor


def predict_sentence(sentence, abbreviation, model_name="tfidf_linear_svm", *, predictor_loader=load_predictor):
    issue = validate_request(sentence, abbreviation)
    if issue:
        raise ValueError(issue)
    abbreviation = abbreviation.strip().upper()
    predictor = predictor_loader(model_name)
    predicted_sense, score = predictor.predict_one({
        "text": sentence,
        "target_abbreviation": abbreviation,
    })
    return {
        "predicted_sense": predicted_sense,
        "score": float(score),
        "score_kind": "uncalibrated decision margin; not a probability",
    }
