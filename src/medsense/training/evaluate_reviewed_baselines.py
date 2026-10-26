"""Evaluate existing TF-IDF baselines on eligible classes in reviewed v1 data."""
from collections import Counter, defaultdict
import hashlib
import json
import platform
from pathlib import Path
import random

import numpy as np
import sklearn
import yaml

from medsense.data.schema import Example
from medsense.data.splits import validate_group_separation
from medsense.data.validate_data import load_jsonl
from medsense.evaluation.metrics import evaluate_predictions
from medsense.models.baseline import TfidfLinearSVM, TfidfLogisticRegression


MIN_TRAIN_EXAMPLES_PER_SENSE = 2


def _class_counts(examples):
    counts = defaultdict(Counter)
    for example in examples:
        counts[example.split][example.target_abbreviation, example.gold_sense] += 1
    return {
        split: {f"{abbr}::{sense}": n for (abbr, sense), n in sorted(counts[split].items())}
        for split in ("train", "validation", "test")
    }


def run_reviewed_baselines(
    dataset_path="data/synthetic/reviewed_v1.jsonl",
    output_dir="outputs/reviewed_v1_traditional_baseline",
    config_path="configs/baseline.yaml",
):
    """Fit only on eligible training classes and evaluate once on held-out test."""
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite output directory: {output}")
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    seed = int(cfg["seed"])
    random.seed(seed)
    np.random.seed(seed)

    examples = [Example.from_dict(row) for row in load_jsonl(dataset_path)]
    if not examples:
        raise ValueError("reviewed dataset is empty")
    validate_group_separation(examples)
    splits = {name: [ex for ex in examples if ex.split == name]
              for name in (cfg["train_split"], cfg["validation_split"], cfg["test_split"])}
    if any(not rows for rows in splits.values()):
        raise ValueError("reviewed dataset must have non-empty train, validation, and test splits")
    if ({ex.group_id for ex in splits["train"]} & {ex.group_id for ex in splits["validation"]}
            or {ex.group_id for ex in splits["train"]} & {ex.group_id for ex in splits["test"]}
            or {ex.group_id for ex in splits["validation"]} & {ex.group_id for ex in splits["test"]}):
        raise ValueError("template group leakage between splits")
    if any(ex.source_type != "synthetic" for ex in examples):
        raise ValueError("reviewed baseline input must contain synthetic examples only")

    by_abbr_split = {
        split: defaultdict(list) for split in splits
    }
    for split, rows in splits.items():
        for example in rows:
            by_abbr_split[split][example.target_abbreviation].append(example)
    abbreviations = sorted({ex.target_abbreviation for ex in examples})
    eligible, excluded = [], {}
    for abbreviation in abbreviations:
        train_rows = by_abbr_split["train"].get(abbreviation, [])
        test_rows = by_abbr_split["test"].get(abbreviation, [])
        train_counts = Counter(ex.gold_sense for ex in train_rows)
        test_senses = {ex.gold_sense for ex in test_rows}
        train_senses = set(train_counts)
        if (len(train_senses) >= 2 and len(test_senses) >= 2
                and test_senses <= train_senses
                and min(train_counts.values()) >= MIN_TRAIN_EXAMPLES_PER_SENSE):
            eligible.append(abbreviation)
        else:
            excluded[abbreviation] = (
                f"requires >=2 senses in train and test, test senses seen in train, and >="
                f"{MIN_TRAIN_EXAMPLES_PER_SENSE} train examples per sense; "
                f"train={dict(train_counts)}, test_senses={sorted(test_senses)}"
            )
    if not eligible:
        raise ValueError(f"no abbreviation meets reviewed baseline requirements: {excluded}")

    train = [ex for ex in splits["train"] if ex.target_abbreviation in eligible]
    test = [ex for ex in splits["test"] if ex.target_abbreviation in eligible]
    validation = splits["validation"]  # counted and reported; never used for tuning
    model_factories = {
        "tfidf_logistic_regression": lambda: TfidfLogisticRegression(
            **cfg["tfidf"], **cfg["logistic_regression"], seed=seed
        ),
        "tfidf_linear_svm": lambda: TfidfLinearSVM(
            **cfg["tfidf"], **cfg["linear_svm"], seed=seed
        ),
    }
    results, prediction_rows = {}, {}
    for name, make_model in model_factories.items():
        model = make_model().fit(train)
        outputs = model.predict(test)
        metrics = evaluate_predictions(test, outputs)
        metrics.update({
            "model": name,
            "n_evaluated_examples": len(test),
            "evaluated_abbreviations": eligible,
            "train_examples": len(train),
            "validation_examples_not_used_for_tuning": sum(
                ex.target_abbreviation in eligible for ex in validation
            ),
            "seed": seed,
            "confidence_kind": "uncalibrated predict_proba maximum" if name.endswith("regression")
                               else "uncalibrated decision_function maximum",
        })
        results[name] = metrics
        prediction_rows[name] = [
            {
                "example_id": ex.example_id,
                "group_id": ex.group_id,
                "target_abbreviation": ex.target_abbreviation,
                "gold_sense": ex.gold_sense,
                "original_label": ex.original_label,
                "predicted_sense": predicted,
                "score_uncalibrated": score,
                "correct": predicted == ex.gold_sense,
                "split": ex.split,
            }
            for ex, (predicted, score) in zip(test, outputs)
        ]

    counts = _class_counts(examples)
    dataset_hash = hashlib.sha256(Path(dataset_path).read_bytes()).hexdigest()
    run_config = {
        "dataset_path": str(dataset_path),
        "dataset_sha256": dataset_hash,
        "seed": seed,
        "tfidf": cfg["tfidf"],
        "logistic_regression": cfg["logistic_regression"],
        "linear_svm": cfg["linear_svm"],
        "class_counts_by_split": counts,
        "eligible_abbreviations": eligible,
        "excluded_abbreviations": excluded,
        "minimum_train_examples_per_sense": MIN_TRAIN_EXAMPLES_PER_SENSE,
        "validation_policy": "reported only; no model selection or tuning",
        "test_policy": "one evaluation on the existing held-out test split",
        "n_evaluated_examples": len(test),
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
    }

    output.mkdir(parents=True, exist_ok=False)
    (output / "run_config.json").write_text(json.dumps(run_config, indent=2) + "\n", encoding="utf-8")
    (output / "summary_metrics.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for name, metrics in results.items():
        (output / f"{name}_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        with (output / f"{name}_test_predictions.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
            for row in prediction_rows[name]:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"run_config": run_config, "results": results}


if __name__ == "__main__":
    print(json.dumps(run_reviewed_baselines(), indent=2))
