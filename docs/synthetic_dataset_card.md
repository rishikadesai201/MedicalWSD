# Synthetic dataset card

## Summary

This deterministic starter dataset contains 132 fictional, educational, clinical-style sentences covering three abbreviations and two senses each: PE (Pulmonary embolism / Physical examination), PA (Pulmonary artery / Physician assistant), and AP (Anteroposterior / Anterior pituitary). Each sentence has a literal target, Python Unicode code-point offsets with an end-exclusive end, a canonical gold sense, candidate senses, source reference URLs, generation method, difficulty tag, verification flag, group/template family ID, and split.

The abbreviations and candidate mappings were checked against MedlinePlus and the NCI SEER Training common-abbreviation resource. See [verified_senses.yaml](../data/terminology/verified_senses.yaml). In particular, AP's “Anterior pituitary” mapping is included because it appears in the cited abbreviation list; it is a narrow terminology challenge, not a claim that AP is universally preferred for that term.

## Generation and split design

Templates were authored as new educational examples and checked to ensure each row's single standalone target matches its abbreviation and its gold sense is in the reviewed candidate list. Examples are not copied from source pages or patient documents. No insufficient-context examples are included or assigned an invented gold sense.

Every template family is a group. A deterministic seeded, sense-stratified split assigns whole families to 6 train, 2 validation, and 3 test groups per sense. Two surface realizations are emitted per family. The test set therefore uses distinct template-family IDs from train and validation. Exact and case/whitespace-normalized duplicates are checked across the complete dataset.

## Intended use

The data supports pipeline development and a controlled preliminary comparison on these authored templates. It does not represent real clinical documentation, language prevalence, a representative abbreviation inventory, or independently annotated clinical text. The fixed test set is small (six examples per sense), so the scores are descriptive of this generator only and should not be generalized to other domains.

## Label status

`label_verified` is true because each example was manually authored for a terminology-reviewed candidate mapping and checked against its declared template label. This is an internal construction check; it is not annotation by multiple clinicians or independent adjudication. Template and sense choices can encode their own shortcuts.

## Ethical and privacy notes

Examples are synthetic, contain no patient data, and make no diagnostic or treatment recommendations. No external LLM or paid service is used.
