# Synthetic dataset manual review guide

Review the separate [132-row review CSV](../data/synthetic/manual_review.csv). It includes the original sentence, literal target and end-exclusive Python character offsets, assigned sense, candidate senses, template group, generation method, difficulty, source metadata, and split. The prefilled `review_flags` are triage prompts, not confirmed errors. Eight rows are flagged for possible context ambiguity, limited context, or artificial/meta wording. Please review all rows, including unflagged ones.

## Inventory

| Abbreviation | Sense | Rows |
|---|---|---:|
| PE | Pulmonary embolism | 22 |
| PE | Physical examination | 22 |
| PA | Pulmonary artery | 22 |
| PA | Physician assistant | 22 |
| AP | Anteroposterior | 22 |
| AP | Anterior pituitary | 22 |
| **Total** |  | **132** |

There are 44 examples per abbreviation (PE 44, PA 44, AP 44). The terminology mappings have reference citations, but **the example labels and sentences have not been independently medically adjudicated**. `label_verified` records the existing internal construction/terminology check, not an independent clinical review. In particular, please assess whether AP is an acceptable abbreviation for “Anterior pituitary” in these contexts; the dataset documentation already identifies this as a narrow terminology case.

## How to record a decision

Use `reviewer_decision` for one of:

- `accept`: the sentence supports the assigned sense and is suitable for this dataset.
- `reject`: the example should be excluded (for example, it is unclear, unnatural, or cannot be labeled reliably). Explain why in `reviewer_comments`.
- `revise`: the example can be retained with a different sense or corrected interpretation. Enter the proposed sense in `reviewer_revised_sense` and explain the evidence in `reviewer_comments`.

Do not edit the assigned sense, sentence, offsets, or any source dataset columns. Record proposed changes only in the reviewer fields. Keep this completed CSV as a separate, versioned review artifact; apply accepted changes to a new dataset version only after review decisions are resolved and documented. Leave a field blank when the reviewer has not assessed it.

## Validate and summarize decisions

After editing a copy of the review CSV, validate it and write a separate JSON summary with:

```powershell
$env:PYTHONPATH = "src"
python -m medsense.data.review_validation data/synthetic/manual_review.csv data/synthetic/manual_review_summary.json
```

Blank decisions count as pending. Invalid decisions stop summary generation. A `revise` decision requires both `reviewer_revised_sense` and `reviewer_comments`. The utility does not infer labels or modify the review CSV.

For the assisted Excel workbook, import only the official reviewer columns to a new CSV and summary:

```powershell
$env:PYTHONPATH = "src"
python -m medsense.data.import_review_workbook data/synthetic/manual_review.xlsx data/synthetic/manual_review_imported.csv data/synthetic/manual_review_imported_summary.json
```

The importer validates decisions before writing, verifies that example IDs, labels, spans, splits, and source metadata still match the canonical synthetic dataset, refuses to overwrite existing outputs, and excludes `AI_triage_suggestion` and `AI_triage_reason` from the official review CSV. A blank reviewer decision remains pending regardless of any AI suggestion.
