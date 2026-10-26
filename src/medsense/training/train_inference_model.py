"""Fit and save the reviewed-v1 Linear SVM from training rows only."""
from collections import Counter, defaultdict
import hashlib
import json
import platform
from pathlib import Path

import joblib
import sklearn
import yaml

from medsense.data.schema import Example
from medsense.data.splits import validate_group_separation
from medsense.data.validate_data import load_jsonl
from medsense.models.baseline import TfidfLinearSVM


DEFAULT_DATASET = "data/synthetic/reviewed_v1.jsonl"
DEFAULT_OUTPUT_DIR = "outputs/reviewed_v1_inference_v1"
MODEL_VERSION = "reviewed-v1-tfidf-linear-svm-1"
MIN_TRAIN_EXAMPLES_PER_SENSE = 2


def train_inference_model(
    dataset_path=DEFAULT_DATASET,
    output_dir=DEFAULT_OUTPUT_DIR,
    config_path="configs/baseline.yaml",
):
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite versioned artifact directory: {output}")
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    examples = [Example.from_dict(row) for row in load_jsonl(dataset_path)]
    if not examples:
        raise ValueError("reviewed dataset is empty")
    validate_group_separation(examples)
    training = [row for row in examples if row.split == cfg["train_split"]]
    if not training:
        raise ValueError("reviewed dataset has no training examples")

    by_abbreviation = defaultdict(list)
    for row in training:
        by_abbreviation[row.target_abbreviation].append(row)
    supported_counts = {}
    excluded = {}
    for abbreviation, rows in sorted(by_abbreviation.items()):
        sense_counts = Counter(row.gold_sense for row in rows)
        if len(sense_counts) < 2 or min(sense_counts.values()) < MIN_TRAIN_EXAMPLES_PER_SENSE:
            excluded[abbreviation] = (
                "fewer than two represented training senses or fewer than "
                f"{MIN_TRAIN_EXAMPLES_PER_SENSE} training examples per sense: {dict(sense_counts)}"
            )
        else:
            supported_counts[abbreviation] = dict(sorted(sense_counts.items()))
    if not supported_counts:
        raise ValueError(f"training data lacks minimum class support: {excluded}")
    if any(row.source_type != "synthetic" for row in training):
        raise ValueError("inference model training accepts synthetic reviewed examples only")

    eligible_training = [row for row in training if row.target_abbreviation in supported_counts]
    model = TfidfLinearSVM(**cfg["tfidf"], **cfg["linear_svm"], seed=int(cfg["seed"]))
    model.fit(eligible_training)
    supported_senses = {
        abbreviation: [str(sense) for sense in fitted[1].classes_]
        for abbreviation, fitted in sorted(model.models.items())
    }
    training_payload = "\n".join(
        json.dumps(row.to_dict(), sort_keys=True, ensure_ascii=False) for row in eligible_training
    ) + "\n"
    metadata = {
        "artifact_format_version": 1,
        "model_version": MODEL_VERSION,
        "algorithm": "TF-IDF word unigram/bigram + per-abbreviation LinearSVC",
        "model_file": "tfidf_linear_svm.joblib",
        "training_data_reference": str(dataset_path),
        "training_split": cfg["train_split"],
        "training_data_sha256": hashlib.sha256(training_payload.encode("utf-8")).hexdigest(),
        "training_example_count": len(eligible_training),
        "training_example_ids": [row.example_id for row in eligible_training],
        "training_group_count": len({row.group_id for row in eligible_training}),
        "class_counts_by_abbreviation_and_sense": supported_counts,
        "supported_abbreviations_and_senses": supported_senses,
        "excluded_abbreviations": excluded,
        "ap_policy": "AP excluded because reviewed-v1 training contains only Anterior pituitary",
        "minimum_training_examples_per_sense": MIN_TRAIN_EXAMPLES_PER_SENSE,
        "tfidf": cfg["tfidf"],
        "linear_svm": cfg["linear_svm"],
        "seed": int(cfg["seed"]),
        "validation_or_test_used_for_training_or_selection": False,
        "score_kind": "uncalibrated decision margin; not a probability",
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
    }

    output.mkdir(parents=True, exist_ok=False)
    joblib.dump(model, output / metadata["model_file"])
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (output / "training_config.json").write_text(json.dumps({
        "dataset_path": str(dataset_path),
        "training_split": cfg["train_split"],
        "seed": int(cfg["seed"]),
        "tfidf": cfg["tfidf"],
        "linear_svm": cfg["linear_svm"],
        "minimum_training_examples_per_sense": MIN_TRAIN_EXAMPLES_PER_SENSE,
        "validation_or_test_used_for_training_or_selection": False,
    }, indent=2) + "\n", encoding="utf-8")
    return metadata


if __name__ == "__main__":
    print(json.dumps(train_inference_model(), indent=2))
