from pathlib import Path

from medsense.data.legacy_audit import audit_legacy_archive


ROOT = Path(__file__).resolve().parents[1]


def test_archived_legacy_rows_have_row_level_audit(tmp_path):
    summary = audit_legacy_archive(ROOT / "medical-wsd.zip", tmp_path)
    assert summary["total_records"] == 580
    assert summary["accepted_records"] == 470
    assert summary["rejected_records"] == 110
    assert summary["rejections_by_reason"] == {
        "target_only_in_surrounding_context_not_sentence": 36,
        "multiple_target_mentions_no_occurrence_index": 74,
    }
    assert summary["accepted_target_spans_verified"] == 470
    assert summary["accepted_candidate_mappings_valid"] == 470
    assert summary["accepted_integer_label_indices_match_sense"] == 470
    assert summary["accepted_candidate_counts_match_lists"] == 470
    assert summary["accepted_labels_independently_confirmed"] == 0
    assert summary["accepted_weak_label_sources"] == {
        "local_rule": 443, "document_level_fallback": 27, "other_or_missing": 0
    }
    rejected = (tmp_path / "legacy_rejections.jsonl").read_text(encoding="utf-8").splitlines()
    accepted = (tmp_path / "legacy_accepted_span_audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(rejected) == 110
    assert len(accepted) == 470
