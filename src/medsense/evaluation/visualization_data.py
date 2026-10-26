"""Load and validate saved reviewed-v1 evaluation outputs for the UI."""
import json
from collections import Counter
from pathlib import Path
import math

from medsense.data.schema import Example
from medsense.data.validate_data import load_jsonl


MODEL_NAMES = ("tfidf_logistic_regression", "tfidf_linear_svm")
DEFAULT_METRICS_DIR = Path("outputs/reviewed_v1_traditional_baseline")
DEFAULT_DATASET = Path("data/synthetic/reviewed_v1.jsonl")


class EvaluationArtifactsError(RuntimeError):
    """Raised when evaluation artifacts are missing or inconsistent."""


def _read_json(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvaluationArtifactsError(f"Required evaluation file is missing: {path}") from exc
    except (json.JSONDecodeError, OSError) as exc:
        raise EvaluationArtifactsError(f"Could not read evaluation file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationArtifactsError(f"Evaluation file must contain a JSON object: {path}")
    return value


def _read_predictions(path):
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError as exc:
        raise EvaluationArtifactsError(f"Required prediction file is missing: {path}") from exc
    except (json.JSONDecodeError, OSError) as exc:
        raise EvaluationArtifactsError(f"Could not read prediction file {path}: {exc}") from exc
    required = {"example_id", "group_id", "target_abbreviation", "gold_sense", "predicted_sense", "correct", "split"}
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise EvaluationArtifactsError(f"{path} row {index} must be a JSON object")
        missing = required - set(row)
        if missing:
            raise EvaluationArtifactsError(f"{path} row {index} is missing fields: {sorted(missing)}")
    return rows


def load_reviewed_evaluation(metrics_dir=DEFAULT_METRICS_DIR, dataset_path=DEFAULT_DATASET):
    metrics_dir = Path(metrics_dir)
    try:
        examples = [Example.from_dict(row) for row in load_jsonl(dataset_path)]
    except (FileNotFoundError, ValueError, TypeError) as exc:
        raise EvaluationArtifactsError(f"Could not load reviewed dataset {dataset_path}: {exc}") from exc
    if not examples:
        raise EvaluationArtifactsError(f"Reviewed dataset is empty: {dataset_path}")

    config = _read_json(metrics_dir / "run_config.json")
    eligible = config.get("eligible_abbreviations")
    if not isinstance(eligible, list) or not eligible:
        raise EvaluationArtifactsError("Run config is missing eligible_abbreviations")
    metrics = {}
    predictions = {}
    for name in MODEL_NAMES:
        metric = _read_json(metrics_dir / f"{name}_metrics.json")
        prediction_rows = _read_predictions(metrics_dir / f"{name}_test_predictions.jsonl")
        labels = metric.get("confusion_matrix_labels")
        matrix = metric.get("confusion_matrix")
        if (not isinstance(labels, list) or not labels or not isinstance(matrix, list)
                or len(matrix) != len(labels) or any(not isinstance(row, list) or len(row) != len(labels) for row in matrix)
                or not isinstance(metric.get("per_sense"), dict)):
            raise EvaluationArtifactsError(f"Malformed class metrics or confusion matrix for {name}")
        if metric.get("n_test") != len(prediction_rows) or metric.get("n_evaluated_examples") != len(prediction_rows):
            raise EvaluationArtifactsError(f"Saved test count does not match predictions for {name}")
        if any(row["split"] != "test" for row in prediction_rows):
            raise EvaluationArtifactsError(f"Non-test prediction found for {name}")
        if len({row["example_id"] for row in prediction_rows}) != len(prediction_rows):
            raise EvaluationArtifactsError(f"Duplicate example IDs in predictions for {name}")
        if list(metric["per_sense"]) != labels:
            raise EvaluationArtifactsError(f"Per-class metric labels disagree for {name}")
        if not isinstance(metric.get("accuracy"), (int, float)) or not isinstance(metric.get("macro_f1"), (int, float)):
            raise EvaluationArtifactsError(f"Accuracy or macro-F1 is missing for {name}")
        if (not math.isfinite(metric["accuracy"]) or not 0 <= metric["accuracy"] <= 1
                or not math.isfinite(metric["macro_f1"]) or not 0 <= metric["macro_f1"] <= 1):
            raise EvaluationArtifactsError(f"Accuracy or macro-F1 is out of range for {name}")
        for class_name, class_metrics in metric["per_sense"].items():
            if not isinstance(class_metrics, dict) or any(
                not isinstance(class_metrics.get(key), (int, float))
                or not math.isfinite(class_metrics[key]) or not 0 <= class_metrics[key] <= 1
                for key in ("precision", "recall", "f1")
            ):
                raise EvaluationArtifactsError(f"Malformed per-class metrics for {name}: {class_name}")
            if not isinstance(class_metrics.get("support"), int) or class_metrics["support"] < 0:
                raise EvaluationArtifactsError(f"Malformed per-class support for {name}: {class_name}")
        if any(not isinstance(cell, int) or cell < 0 for matrix_row in matrix for cell in matrix_row):
            raise EvaluationArtifactsError(f"Malformed confusion matrix values for {name}")
        expected_matrix = [[0 for _ in labels] for _ in labels]
        label_index = {label: index for index, label in enumerate(labels)}
        try:
            for row in prediction_rows:
                true_label = f"{row['target_abbreviation']}::{row['gold_sense']}"
                predicted_label = f"{row['target_abbreviation']}::{row['predicted_sense']}"
                expected_matrix[label_index[true_label]][label_index[predicted_label]] += 1
        except KeyError as exc:
            raise EvaluationArtifactsError(f"Prediction class is absent from saved metric labels for {name}") from exc
        if matrix != expected_matrix:
            raise EvaluationArtifactsError(f"Saved confusion matrix disagrees with predictions for {name}")
        if sum(sum(row) for row in matrix) != len(prediction_rows):
            raise EvaluationArtifactsError(f"Saved confusion matrix total disagrees with test size for {name}")
        for index, class_name in enumerate(labels):
            if sum(matrix[index]) != metric["per_sense"][class_name]["support"]:
                raise EvaluationArtifactsError(f"Confusion matrix support disagrees for {name}: {class_name}")
        expected_macro_f1 = sum(values["f1"] for values in metric["per_sense"].values()) / len(labels)
        if not math.isclose(metric["macro_f1"], expected_macro_f1, abs_tol=1e-12):
            raise EvaluationArtifactsError(f"Saved macro-F1 disagrees with per-class metrics for {name}")
        correct_count = sum(bool(row["correct"]) for row in prediction_rows)
        if not math.isclose(metric.get("accuracy", -1), correct_count / len(prediction_rows), abs_tol=1e-12):
            raise EvaluationArtifactsError(f"Saved accuracy disagrees with predictions for {name}")
        if any(bool(row["correct"]) != (row["gold_sense"] == row["predicted_sense"])
               for row in prediction_rows):
            raise EvaluationArtifactsError(f"Correctness flag disagrees with labels for {name}")
        metrics[name] = metric
        predictions[name] = prediction_rows

    baseline_ids = [row["example_id"] for row in predictions[MODEL_NAMES[0]]]
    baseline_labels = [(row["target_abbreviation"], row["gold_sense"]) for row in predictions[MODEL_NAMES[0]]]
    for name in MODEL_NAMES[1:]:
        if [row["example_id"] for row in predictions[name]] != baseline_ids:
            raise EvaluationArtifactsError("Model prediction files do not use the same test examples and order")
        if [(row["target_abbreviation"], row["gold_sense"]) for row in predictions[name]] != baseline_labels:
            raise EvaluationArtifactsError("Model prediction files disagree on test labels")
        if metrics[name]["confusion_matrix_labels"] != metrics[MODEL_NAMES[0]]["confusion_matrix_labels"]:
            raise EvaluationArtifactsError("Model metrics disagree on evaluated classes")

    dataset_test = [ex.example_id for ex in examples if ex.split == "test" and ex.target_abbreviation in eligible]
    if baseline_ids != dataset_test:
        raise EvaluationArtifactsError("Saved predictions do not match the eligible reviewed-v1 test rows")
    by_id = {ex.example_id: ex for ex in examples}
    for name, rows in predictions.items():
        for row in rows:
            source = by_id[row["example_id"]]
            if (row["target_abbreviation"] != source.target_abbreviation
                    or row["gold_sense"] != source.gold_sense or row["group_id"] != source.group_id):
                raise EvaluationArtifactsError(f"Prediction labels or group ID disagree with dataset: {row['example_id']}")
    dataset_counts = Counter()
    class_inventory = set()
    for example in examples:
        senses = example.candidate_senses or (example.gold_sense,)
        for sense in senses:
            key = (example.target_abbreviation, sense)
            class_inventory.add(key)
        dataset_counts[(example.target_abbreviation, example.gold_sense, example.split)] += 1
    composition = [
        {
            "class": f"{abbreviation} — {sense}",
            "abbreviation": abbreviation,
            "sense": sense,
            "train": dataset_counts[(abbreviation, sense, "train")],
            "validation": dataset_counts[(abbreviation, sense, "validation")],
            "test": dataset_counts[(abbreviation, sense, "test")],
        }
        for abbreviation, sense in sorted(class_inventory)
    ]
    errors = {
        name: [
            {
                **row,
                "text": by_id[row["example_id"]].text,
            }
            for row in rows if not row["correct"]
        ]
        for name, rows in predictions.items()
    }
    return {
        "run_config": config,
        "metrics": metrics,
        "predictions": predictions,
        "dataset_composition": composition,
        "prediction_errors": errors,
        "n_dataset_examples": len(examples),
        "n_test_examples": len(baseline_ids),
    }
