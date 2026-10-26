import csv

import pytest

from medsense.data.review_validation import summarize_review


FIELDS = ["example_id", "abbreviation", "reviewer_decision",
          "reviewer_revised_sense", "reviewer_comments"]


def make_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_summary_counts_pending_and_valid_decisions_by_abbreviation(tmp_path):
    path = tmp_path / "review.csv"
    make_csv(path, [
        {"example_id": "1", "abbreviation": "PE", "reviewer_decision": ""},
        {"example_id": "2", "abbreviation": "PE", "reviewer_decision": "accept"},
        {"example_id": "3", "abbreviation": "PA", "reviewer_decision": "reject"},
        {"example_id": "4", "abbreviation": "PA", "reviewer_decision": "revise",
         "reviewer_revised_sense": "Pulmonary artery", "reviewer_comments": "Context supports vessel."},
    ])

    summary = summarize_review(path)

    assert summary["counts"] == {"pending": 1, "accepted": 1, "rejected": 1, "revised": 1}
    assert summary["by_abbreviation"]["PE"]["pending"] == 1
    assert summary["by_abbreviation"]["PA"]["revised"] == 1


@pytest.mark.parametrize("row, message", [
    ({"reviewer_decision": "maybe"}, "invalid decision"),
    ({"reviewer_decision": "revise", "reviewer_revised_sense": "", "reviewer_comments": "because"},
     "reviewer_revised_sense"),
    ({"reviewer_decision": "revise", "reviewer_revised_sense": "new sense", "reviewer_comments": ""},
     "reviewer_comments"),
])
def test_invalid_decisions_and_incomplete_revisions_fail(tmp_path, row, message):
    path = tmp_path / "review.csv"
    make_csv(path, [{"example_id": "bad", "abbreviation": "PE", **row}])

    with pytest.raises(ValueError, match=message):
        summarize_review(path)
