import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_imported_review_csv_covers_dataset_and_preserves_source_labels():
    dataset = [
        json.loads(line)
        for line in (ROOT / "data/synthetic/verified_examples.jsonl")
        .read_text(encoding="utf-8").splitlines()
    ]
    with (ROOT / "data/synthetic/manual_review_imported_run4.csv").open(
            encoding="utf-8-sig", newline="") as handle:
        review_rows = list(csv.DictReader(handle))

    assert len(review_rows) == len(dataset) == 132
    assert {row["example_id"] for row in review_rows} == {row["example_id"] for row in dataset}
    assert Counter(row["abbreviation"] for row in review_rows) == {"PE": 44, "PA": 44, "AP": 44}
    assert Counter(row["reviewer_decision"] for row in review_rows) == {"accept": 58, "reject": 74}
    source_by_id = {row["example_id"]: row for row in dataset}
    for review in review_rows:
        source = source_by_id[review["example_id"]]
        start, end = int(review["target_start"]), int(review["target_end"])
        assert review["sentence"] == source["text"]
        assert review["sentence"][start:end] == review["target_span"] == source["target_abbreviation"]
        assert review["assigned_sense"] == source["gold_sense"]
        assert review["reviewer_decision"] in {"accept", "reject", "revise"}
        if review["reviewer_decision"] == "revise":
            assert review["reviewer_revised_sense"].strip()
            assert review["reviewer_comments"].strip()
