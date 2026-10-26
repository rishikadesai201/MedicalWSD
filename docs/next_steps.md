# MedSense AI: synthetic pipeline review

## Findings

- The synthetic set contains 132 examples: 22 for each of six senses across PE, PA, and AP (44 per abbreviation). The terminology file defines two senses per abbreviation and marks them terminology-verified. Each example has a verified label, deterministic template generation method, difficulty, group ID, and end-exclusive target offsets.
- The quality report records zero invalid spans, exact or normalized duplicate texts, or group split leakage. Its 66 template families are assigned as 36 train, 12 validation, and 18 test families (72/24/36 examples); each family stays within one split. This supports a preliminary **synthetic-only** experiment on held-out template families. The small, authored template set does not establish clinical generalization.
- No insufficient-context examples are mixed into the supervised set. The generator resolves labels against the terminology file and assigns offsets from the generated target occurrence.
- Saved test metrics report majority baseline accuracy 0.500 and macro-F1 0.333; TF-IDF + Logistic Regression accuracy 0.917 and macro-F1 0.916. The latter has 4/6 accuracy for PE Physical examination and 5/6 for PE Pulmonary embolism; the other four senses score 6/6. These are the existing saved results, not a new run. The test set has six examples per sense, so the estimates are small and template-dependent.
- This review made no data, generator, model, or artifact changes. The legacy processed corpus remains separate; its weak labels should not be pooled with these verified synthetic labels.

## Tests and review limits

`python -m pytest -q`: **15 passed**. No confirmed implementation defect was found that warranted a code change. The terminology mappings have cited reference entries, but this pass did not independently adjudicate clinical appropriateness of every sense or authored sentence. Saved metrics were read without rerunning evaluation, preserving baseline artifacts.

## Next task

Create an independently labeled clinical benchmark with reviewed abbreviation spans and senses, then evaluate it separately from synthetic data before making any clinical generalization claim.
