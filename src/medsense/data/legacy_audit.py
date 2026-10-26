"""Row-level audit of the archived processed clinical-claim file."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import zipfile

from .legacy import AmbiguousTargetError, legacy_to_example

ARCHIVE_MEMBER = "medical-wsd/data/processed/real_wsd_preprocessed.jsonl"


def audit_legacy_archive(archive: str | Path, output_dir: str | Path) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        rows = [json.loads(line) for line in bundle.read(ARCHIVE_MEMBER).decode("utf-8").splitlines() if line.strip()]

    accepted, rejected = [], []
    reason_counts: Counter[str] = Counter()
    for row in rows:
        try:
            example = legacy_to_example(row)
            span_ok = example.text[example.target_start:example.target_end] == example.target_abbreviation
            candidate_ok = example.gold_sense in example.candidate_senses
            label_index = example.original_label
            label_index_ok = (
                isinstance(label_index, int)
                and 0 <= label_index < len(example.candidate_senses)
                and example.candidate_senses[label_index] == example.gold_sense
            )
            candidate_count_ok = row.get("num_candidates") == len(example.candidate_senses)
            accepted.append({
                "example_id": example.example_id,
                "abbreviation": example.target_abbreviation,
                "target_start": example.target_start,
                "target_end": example.target_end,
                "span_verified": span_ok,
                "gold_sense": example.gold_sense,
                "candidate_mapping_valid": candidate_ok,
                "original_label_index": label_index,
                "label_index_matches_gold_sense": label_index_ok,
                "num_candidates_matches_list": candidate_count_ok,
                "label_verified": example.label_verified,
                "weak_label_source": row.get("label_source", "unknown"),
                "split": example.split,
                "group_id": example.group_id,
            })
        except AmbiguousTargetError as exc:
            target_count = int(str(exc).split(" has ", 1)[1].split(" standalone", 1)[0])
            abbreviation = row.get("abbreviation") or ""
            sentence = row.get("sentence") or ""
            full_text = row.get("text") or ""
            insensitive_count = len(list(re.finditer(
                rf"(?<!\w){re.escape(abbreviation)}(?!\w)", sentence, re.IGNORECASE
            ))) if abbreviation else 0
            context_count = len(list(re.finditer(
                rf"(?<!\w){re.escape(abbreviation)}(?!\w)", full_text
            ))) if abbreviation else 0
            if target_count > 1:
                reason = "multiple_target_mentions_no_occurrence_index"
            elif insensitive_count:
                reason = "target_case_mismatch_in_sentence"
            elif context_count:
                reason = "target_only_in_surrounding_context_not_sentence"
            else:
                reason = "target_missing_from_sentence_and_context"
            reason_counts[reason] += 1
            rejected.append({
                "example_id": str(row.get("id", "")),
                "abbreviation": abbreviation,
                "split": row.get("split"),
                "reason_code": reason,
                "reason": str(exc),
                "standalone_occurrence_count": target_count,
                "case_insensitive_sentence_occurrences": insensitive_count,
                "full_context_occurrences": context_count,
                "legacy_target_span_is_location": False,
                "label_source": row.get("label_source", "unknown"),
            })

    per_abbr = defaultdict(Counter)
    per_sense = defaultdict(Counter)
    for row in accepted:
        per_abbr[row["abbreviation"]]["accepted"] += 1
        per_abbr[row["abbreviation"]][row["weak_label_source"]] += 1
        per_sense[f"{row['abbreviation']}::{row['gold_sense']}"][row["weak_label_source"]] += 1
    summary = {
        "archive_member": ARCHIVE_MEMBER,
        "total_records": len(rows),
        "accepted_records": len(accepted),
        "rejected_records": len(rejected),
        "rejections_by_reason": dict(reason_counts),
        "accepted_target_spans_verified": sum(r["span_verified"] for r in accepted),
        "accepted_candidate_mappings_valid": sum(r["candidate_mapping_valid"] for r in accepted),
        "accepted_integer_label_indices_match_sense": sum(r["label_index_matches_gold_sense"] for r in accepted),
        "accepted_candidate_counts_match_lists": sum(r["num_candidates_matches_list"] for r in accepted),
        "accepted_labels_independently_confirmed": sum(r["label_verified"] for r in accepted),
        "accepted_labels_unverified": sum(not r["label_verified"] for r in accepted),
        "accepted_weak_label_sources": {
            "local_rule": sum(r["weak_label_source"] == "local" for r in accepted),
            "document_level_fallback": sum(r["weak_label_source"] == "document_level" for r in accepted),
            "other_or_missing": sum(r["weak_label_source"] not in {"local", "document_level"} for r in accepted),
        },
        "accepted_by_abbreviation": {k: dict(v) for k, v in sorted(per_abbr.items())},
        "accepted_by_abbreviation_sense_and_label_source": {k: dict(v) for k, v in sorted(per_sense.items())},
        "notes": [
            "All accepted label_verified values are false; no row is independently confirmed.",
            "Span validation confirms only the unique literal abbreviation offsets, not semantic correctness of the gold label.",
            "Raw source CSV is absent, so source provenance and weak-label rules cannot be independently validated.",
        ],
        "preliminary_experiment_assessment": {
            "valid_for_primary_wsd_performance_claims": False,
            "valid_for_software_pipeline_smoke_tests": True,
            "valid_for_descriptive_weak_label_analysis": True,
            "reason": "No independently reviewed gold labels; 113 exact full-context duplicates cross splits in the unadapted file; raw source corpus is absent; some abbreviations have one observed training sense.",
        },
    }
    _write_jsonl(output_dir / "legacy_accepted_span_audit.jsonl", accepted)
    _write_jsonl(output_dir / "legacy_rejections.jsonl", rejected)
    (output_dir / "legacy_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
