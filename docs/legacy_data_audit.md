# Legacy processed-data audit

The original archive and notebook remain unchanged. This audit reads the archive member `medical-wsd/data/processed/real_wsd_preprocessed.jsonl`; it does not have the source CSV and therefore does not validate the claimed source provenance.

## Row-level outcome

All 580 records were checked with the legacy adapter. It accepts only a unique, standalone, exact-case abbreviation occurrence in the annotated sentence and verifies the end-exclusive offsets by slicing the original sentence.

| Outcome | Rows | Finding |
|---|---:|---|
| Accepted with exact target offset | 470 | All 470 spans equal the abbreviation; all 470 gold senses are present in the candidate list, integer label index, and candidate count matches the source fields. |
| Rejected: repeated target | 74 | Multiple standalone mentions occur in the sentence, but `target_span` is only a generic marker and gives no occurrence index. |
| Rejected: target not in annotated sentence | 36 | No exact standalone mention occurs in `sentence`; the abbreviation occurs elsewhere in the wider context. |

The rejected report has one row per rejection, with ID, abbreviation, split, reason code, exact occurrence counts, and original label-source status. The accepted report has one row per accepted example with offsets and candidate mapping checks. Neither report includes source text.

- [Rejection report](../outputs/legacy_audit/legacy_rejections.jsonl)
- [Accepted span audit](../outputs/legacy_audit/legacy_accepted_span_audit.jsonl)
- [Machine-readable summary](../outputs/legacy_audit/legacy_audit_summary.json)

## Label status

No labels are independently confirmed. Among the 470 accepted records, 443 use the archived sentence-local lexical rules and 27 use document-level full-form fallback. In all 470, the integer label index points to the stored gold sense in the candidate list, and `num_candidates` matches the list length. The adapter retains the label but sets `label_verified: false`. Internal index consistency does not establish that the sense label is semantically correct. The rule-based labels are especially unsuitable as independent test truth because the same lexical evidence appears in the model context.

## Preliminary experiment suitability

The processed set can support pipeline smoke tests and descriptive analysis of the old weak-label process. It cannot support primary WSD performance claims at present: the source CSV and annotation protocol are absent, none of the labels is independently reviewed, exact full-context duplicates cross splits, the label-generation patterns overlap model features, and several abbreviations have only one training sense. Even a de-duplicated model run on these labels would remain a weak-label diagnostic rather than an independent evaluation.
