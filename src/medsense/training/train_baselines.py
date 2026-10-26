"""Train baselines on training groups and evaluate once on held-out test groups."""
from collections import Counter
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
from medsense.models.baseline import MajorityBaseline, TfidfLinearSVM, TfidfLogisticRegression


def run_linear_svm(config_path="configs/baseline.yaml"):
    """Evaluate a fixed-config Linear SVM without rewriting existing artifacts."""
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    seed = int(cfg["seed"])
    dataset_quality = json.loads(Path(cfg["dataset_quality_report"]).read_text(encoding="utf-8"))
    random.seed(seed)
    np.random.seed(seed)
    examples = [Example.from_dict(row) for row in load_jsonl(cfg["dataset_path"])]
    validate_group_separation(examples)
    train = [ex for ex in examples if ex.split == cfg["train_split"]]
    validation = [ex for ex in examples if ex.split == cfg["validation_split"]]
    test = [ex for ex in examples if ex.split == cfg["test_split"]]
    if not train or not validation or not test:
        raise ValueError("training, validation, and test splits must be non-empty")
    if ({ex.group_id for ex in train} & {ex.group_id for ex in validation}
            or {ex.group_id for ex in train} & {ex.group_id for ex in test}
            or {ex.group_id for ex in validation} & {ex.group_id for ex in test}):
        raise ValueError("template group leakage between splits")
    if any(not ex.label_verified or ex.source_type != "synthetic" for ex in examples):
        raise ValueError("baseline input must contain only verified synthetic examples")

    model = TfidfLinearSVM(**cfg["tfidf"], **cfg["linear_svm"], seed=seed).fit(train)
    outputs = model.predict(test)
    metrics = evaluate_predictions(test, outputs)
    metrics.update({
        "model": "tfidf_linear_svm",
        "train_examples": len(train),
        "validation_examples_not_used_for_model_selection": len(validation),
        "seed": seed,
        "confidence_kind": "uncalibrated decision_function maximum",
    })
    outdir = Path(cfg["output_dir"])
    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / "tfidf_linear_svm_test_predictions.jsonl").open(
            "w", encoding="utf-8", newline="\n") as handle:
        for example, (predicted, score) in zip(test, outputs):
            handle.write(json.dumps({
                "example_id": example.example_id,
                "group_id": example.group_id,
                "target_abbreviation": example.target_abbreviation,
                "gold_sense": example.gold_sense,
                "predicted_sense": predicted,
                "score_uncalibrated": score,
                "correct": predicted == example.gold_sense,
                "split": example.split,
            }, ensure_ascii=False) + "\n")
    (outdir / "tfidf_linear_svm_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8")
    svm_config = {
        "model": "tfidf_linear_svm",
        "seed": seed,
        "data_seed": dataset_quality["seed"],
        "data_file": cfg["dataset_path"],
        "split_sizes": {split: sum(ex.split == split for ex in examples)
                        for split in [cfg["train_split"], cfg["validation_split"], cfg["test_split"]]},
        "tfidf": cfg["tfidf"],
        "linear_svm": cfg["linear_svm"],
        "validation_policy": "fixed configuration; validation not used for model selection",
        "test_policy": "single evaluation on the existing held-out test split",
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
    }
    (outdir / "tfidf_linear_svm_run_config.json").write_text(
        json.dumps(svm_config, indent=2), encoding="utf-8")
    return metrics


def run(config_path="configs/baseline.yaml"):
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    seed = int(cfg["seed"])
    dataset_quality = json.loads(Path(cfg["dataset_quality_report"]).read_text(encoding="utf-8"))
    random.seed(seed)
    np.random.seed(seed)
    examples = [Example.from_dict(row) for row in load_jsonl(cfg["dataset_path"])]
    validate_group_separation(examples)
    train = [ex for ex in examples if ex.split == cfg["train_split"]]
    validation = [ex for ex in examples if ex.split == cfg["validation_split"]]
    test = [ex for ex in examples if ex.split == cfg["test_split"]]
    if not train or not test:
        raise ValueError("training and test splits must both be non-empty")
    if len({ex.group_id for ex in train} & {ex.group_id for ex in test}):
        raise ValueError("template group leakage between train and test")
    if any(not ex.label_verified or ex.source_type != "synthetic" for ex in examples):
        raise ValueError("baseline input must contain only verified synthetic examples")

    models = {
        "majority": MajorityBaseline().fit(train),
        "tfidf_logistic_regression": TfidfLogisticRegression(
            **cfg["tfidf"], **cfg["logistic_regression"], seed=seed
        ).fit(train),
    }
    outdir = Path(cfg["output_dir"])
    outdir.mkdir(parents=True, exist_ok=True)
    run_config = {
        **cfg,
        "data_seed": dataset_quality["seed"],
        "data_file": cfg["dataset_path"],
        "group_counts_by_split": dict(Counter(ex.split for ex in examples)),
        "template_groups_by_split": {split: len({ex.group_id for ex in examples if ex.split == split})
                                     for split in ["train", "validation", "test"]},
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
        "metrics_policy": "fixed test split; no hyperparameter or threshold tuning",
    }
    (outdir / "run_config.json").write_text(json.dumps(run_config, indent=2), encoding="utf-8")

    results = {}
    for name, model in models.items():
        outputs = model.predict(test)
        metrics = evaluate_predictions(test, outputs)
        metrics.update({
            "model": name,
            "train_examples": len(train),
            "validation_examples_not_used_for_tuning": len(validation),
            "seed": seed,
            "confidence_kind": "majority frequency" if name == "majority" else "uncalibrated predict_proba maximum",
        })
        results[name] = metrics
        pred_path = outdir / f"{name}_test_predictions.jsonl"
        with pred_path.open("w", encoding="utf-8", newline="\n") as handle:
            for example, (predicted, score) in zip(test, outputs):
                handle.write(json.dumps({
                    "example_id": example.example_id,
                    "group_id": example.group_id,
                    "target_abbreviation": example.target_abbreviation,
                    "gold_sense": example.gold_sense,
                    "predicted_sense": predicted,
                    "score_uncalibrated": score,
                    "correct": predicted == example.gold_sense,
                    "split": example.split,
                }, ensure_ascii=False) + "\n")
        (outdir / f"{name}_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (outdir / "summary_metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--linear-svm", action="store_true",
                        help="run only the new Linear SVM baseline and preserve existing baseline outputs")
    args = parser.parse_args()
    result = run_linear_svm() if args.linear_svm else run()
    print(json.dumps(result, indent=2))
