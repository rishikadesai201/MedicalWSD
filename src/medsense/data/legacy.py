"""Explicit adapter for records in the archived medical-wsd project format."""
import re
from typing import Any

from .schema import Example


class AmbiguousTargetError(ValueError):
    """Raised when a legacy record does not identify which mention is labeled."""


def legacy_to_example(row: dict[str, Any], archive_path: str = "medical-wsd.zip") -> Example:
    """Convert one record while retaining its label and marking it unverified.

    Legacy `target_span` is only the string ``[ABBR]X[/ABBR]`` and does not
    mark a location in `sentence`. Derive offsets only when exactly one
    standalone occurrence exists; never silently choose among repeated mentions.
    """
    text = row.get("sentence") or ""
    abbreviation = row.get("abbreviation") or ""
    spans = list(re.finditer(rf"(?<!\w){re.escape(abbreviation)}(?!\w)", text)) if abbreviation else []
    if len(spans) != 1:
        raise AmbiguousTargetError(
            f"legacy row {row.get('id', '<unknown>')} has {len(spans)} standalone "
            f"occurrences of {abbreviation!r}; occurrence-level annotation is required"
        )
    match = spans[0]
    split = {"val": "validation", "validation": "validation"}.get(
        row.get("split", "unassigned"), row.get("split", "unassigned")
    )
    if row.get("domain") == "synthetic":
        source_type = "synthetic"
        generation_method = "template_unreviewed"
        data_file = "synthetic_wsd_preprocessed.jsonl"
    else:
        # The archive says clinical/MTSamples, but its raw CSV is not included.
        source_type = "clinical_source_claim_unverified"
        data_file = "real_wsd_preprocessed.jsonl"
        generation_method = (
            "weak_label_local_rule" if row.get("label_source") == "local"
            else "weak_label_document_fallback"
        )
    doc_id = row.get("source_doc_index")
    example = Example(
        example_id=str(row.get("id", "")), text=text,
        target_abbreviation=abbreviation, target_start=match.start(),
        target_end=match.end(), gold_sense=str(row.get("sense", "")),
        specialty=str(row.get("specialty") or "unknown"),
        difficulty="unknown", source_type=source_type,
        source_reference=(f"{archive_path}#data/processed/{data_file}:"
                          f"row={row.get('id')};source_doc_index={doc_id}"),
        generation_method=generation_method,
        group_id=str(doc_id) if doc_id is not None else str(row.get("id", "unknown")),
        label_verified=False, split=split,
        original_label=row.get("label"),
        candidate_senses=tuple(row.get("candidate_senses", ())),
    )
    example.validate()
    return example
