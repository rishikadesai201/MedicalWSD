import json
from pathlib import Path

import pytest
import yaml

from medsense.data.schema import Example
from medsense.data.splits import assign_group_splits, validate_group_separation
from medsense.data.synthetic_generator import generate


ROOT = Path(__file__).resolve().parents[1]


def test_group_split_assigns_whole_families_deterministically():
    rows = [
        {"group_id": f"g{i}", "target_abbreviation": "PE", "gold_sense": "embolism"}
        for i in range(6)
    ]
    first = assign_group_splits(rows, {"train": 3, "validation": 1, "test": 2}, seed=3)
    second = assign_group_splits(rows, {"train": 3, "validation": 1, "test": 2}, seed=3)
    assert first == second
    assert {split: list(first.values()).count(split) for split in set(first.values())} == {
        "train": 3, "validation": 1, "test": 2
    }


def test_group_split_rejects_inconsistent_stratum_counts():
    rows = [{"group_id": "g", "target_abbreviation": "PE", "gold_sense": "embolism"}]
    with pytest.raises(ValueError, match="has 1 groups"):
        assign_group_splits(rows, {"train": 1, "test": 1}, seed=0)


def test_generated_data_has_valid_labels_offsets_and_no_split_leakage(tmp_path):
    config = yaml.safe_load((ROOT / "configs/synthetic.yaml").read_text(encoding="utf-8"))
    config["terminology_path"] = str(ROOT / config["terminology_path"])
    config["output_path"] = str(tmp_path / "examples.jsonl")
    config["quality_report_path"] = str(tmp_path / "quality.json")
    config_path = tmp_path / "synthetic.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    examples, report = generate(config_path)
    regenerated, report_again = generate(config_path)
    assert [ex.to_dict() for ex in regenerated] == [ex.to_dict() for ex in examples]
    assert report_again == report
    assert len(examples) == 132
    assert all(ex.label_verified and ex.source_type == "synthetic" for ex in examples)
    assert all(ex.text[ex.target_start:ex.target_end] == ex.target_abbreviation for ex in examples)
    assert all(ex.gold_sense in ex.candidate_senses for ex in examples)
    assert report["invalid_target_span_count"] == 0
    assert report["duplicate_text_count"] == 0
    assert report["cross_split_normalized_duplicate_texts"] == 0
    validate_group_separation(examples)
    assert report["examples_by_split"] == {"test": 36, "train": 72, "validation": 24}
    assert len([ex for ex in examples if ex.split == "test"]) == 36
    saved = [json.loads(line) for line in (tmp_path / "examples.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(saved) == len(examples)


def test_template_groups_never_span_splits(tmp_path):
    config = yaml.safe_load((ROOT / "configs/synthetic.yaml").read_text(encoding="utf-8"))
    config["terminology_path"] = str(ROOT / config["terminology_path"])
    config["output_path"] = str(tmp_path / "examples.jsonl")
    config["quality_report_path"] = str(tmp_path / "quality.json")
    path = tmp_path / "synthetic.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    examples, _ = generate(path)
    group_to_splits = {}
    for ex in examples:
        group_to_splits.setdefault(ex.group_id, set()).add(ex.split)
    assert all(len(splits) == 1 for splits in group_to_splits.values())
