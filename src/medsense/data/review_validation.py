"""Validate manual-review decisions and write a separate aggregate summary."""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path


DECISIONS = {"accept", "reject", "revise"}
REQUIRED_COLUMNS = {
    "example_id", "abbreviation", "reviewer_decision",
    "reviewer_revised_sense", "reviewer_comments",
}


def summarize_review(csv_path):
    """Validate decisions and return counts without changing the review CSV."""
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"review CSV is missing columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    return summarize_review_rows(rows)


def summarize_review_rows(rows):
    counts = Counter()
    by_abbreviation = defaultdict(Counter)
    errors = []
    for line_number, row in enumerate(rows, start=2):
        decision = (row.get("reviewer_decision") or "").strip().casefold()
        if not decision:
            status = "pending"
        elif decision not in DECISIONS:
            errors.append(f"row {line_number} ({row['example_id']}): invalid decision {decision!r}")
            continue
        else:
            status = {"accept": "accepted", "reject": "rejected", "revise": "revised"}[decision]
            if decision == "revise":
                if not (row.get("reviewer_revised_sense") or "").strip():
                    errors.append(f"row {line_number} ({row['example_id']}): revise requires reviewer_revised_sense")
                if not (row.get("reviewer_comments") or "").strip():
                    errors.append(f"row {line_number} ({row['example_id']}): revise requires reviewer_comments")
        counts[status] += 1
        by_abbreviation[row["abbreviation"]][status] += 1

    if errors:
        raise ValueError("Invalid review entries:\n" + "\n".join(errors))

    statuses = ("pending", "accepted", "rejected", "revised")
    return {
        "total": len(rows),
        "counts": {status: counts[status] for status in statuses},
        "by_abbreviation": {
            abbreviation: {
                **{status: by_abbreviation[abbreviation][status] for status in statuses},
                "total": sum(by_abbreviation[abbreviation].values()),
            }
            for abbreviation in sorted(by_abbreviation)
        },
    }


def write_summary(csv_path, output_path):
    source = Path(csv_path).resolve()
    output = Path(output_path).resolve()
    if source == output:
        raise ValueError("summary output must be separate from the review CSV")
    summary = summarize_review(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_csv", nargs="?", default="data/synthetic/manual_review.csv")
    parser.add_argument("summary_json", nargs="?", default="data/synthetic/manual_review_summary.json")
    args = parser.parse_args()
    print(json.dumps(write_summary(args.review_csv, args.summary_json), indent=2))


if __name__ == "__main__":
    main()
