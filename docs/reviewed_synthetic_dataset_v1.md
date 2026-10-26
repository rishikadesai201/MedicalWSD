# MedSense AI reviewed synthetic dataset v1

## Provenance and review status

This version was built from the 132-row assisted review workbook through the review importer. Official decisions came only from `reviewer_decision`, `reviewer_revised_sense`, and `reviewer_comments`; AI triage suggestions were not treated as decisions. The workbook records AI-assisted review. The decisions do not establish medical validation or independent clinical adjudication.

| Decision | Count |
|---|---:|
| Accepted and included | 58 |
| Revised and included | 0 |
| Rejected and excluded | 74 |
| Pending | 0 |
| **Total reviewed** | **132** |

| Abbreviation | Accepted | Revised | Rejected | Included |
|---|---:|---:|---:|---:|
| AP | 19 | 0 | 25 | 19 |
| PA | 15 | 0 | 29 | 15 |
| PE | 24 | 0 | 20 | 24 |

No gold labels changed in this version. Every included record stores its original assigned sense in `original_label` for traceability; `gold_sense` remains that same sense. Rejected rows are excluded. The original synthetic dataset and its split assignments were not changed.

## Dataset and split checks

The separate [reviewed dataset](../data/synthetic/reviewed_v1.jsonl) contains **58** examples: 34 train, 9 validation, and 15 test. All three original split names remain present. Its 43 retained template groups stay within their original split; there is no template-family leakage. Schema, target-span, duplicate-ID, and duplicate-text checks passed.

Sense counts in the included data:

| Abbreviation | Sense | Count |
|---|---|---:|
| AP | Anterior pituitary | 19 |
| AP | Anteroposterior | 0 |
| PA | Physician assistant | 9 |
| PA | Pulmonary artery | 6 |
| PE | Physical examination | 9 |
| PE | Pulmonary embolism | 15 |

Filtering leaves AP Anteroposterior with no examples and leaves only Anterior pituitary in AP training. Thus the existing per-abbreviation two-sense baseline cannot be fit for AP on this version, and six-sense baseline metrics would not be comparable. PA and PE retain both senses in training. The splits are group-safe, but sense coverage is incomplete for model re-evaluation.

This is a small, synthetic, AI-assisted reviewed set. It is not independently medically validated, does not represent clinical documentation, and does not support real clinical generalization claims.
