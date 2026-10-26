import csv
import json
from collections import Counter
from pathlib import Path

from medsense.data.schema import Example
from medsense.data.splits import validate_group_separation


ROOT = Path(__file__).resolve().parents[1]


def test_reviewed_dataset_includes_only_accepted_rows_and_preserves_traceability():
    source = {
        row["example_id"]: row
        for row in map(json.loads, (ROOT / "data/synthetic/verified_examples.jsonl")
                       .read_text(encoding="utf-8").splitlines())
    }
    with (ROOT / "data/synthetic/manual_review_imported_run4.csv").open(
            encoding="utf-8-sig", newline="") as handle:
        decisions = {row["example_id"]: row for row in csv.DictReader(handle)}
    rows = [
        Example.from_dict(json.loads(line))
        for line in (ROOT / "data/synthetic/reviewed_v1.jsonl").read_text(encoding="utf-8").splitlines()
    ]

    assert len(rows) == 58
    assert len({row.example_id for row in rows}) == len(rows)
    assert all(decisions[row.example_id]["reviewer_decision"] in {"accept", "revise"} for row in rows)
    assert Counter(row.split for row in rows) == {"train": 34, "validation": 9, "test": 15}
    assert all(row.original_label == source[row.example_id]["gold_sense"] for row in rows)
    assert all(row.text == source[row.example_id]["text"] for row in rows)
    assert all(row.text[row.target_start:row.target_end] == row.target_abbreviation for row in rows)
    validate_group_separation(rows)
