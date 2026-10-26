# Initial repository audit

**Audit date:** 2026-10-26  
**Scope:** `NLP (2).ipynb`, `medical-wsd.zip`, and the starter files at the workspace root. The notebook has not been modified.

## Inventory and provenance

The workspace contains the original 9-cell notebook (45,022 bytes) and a 1,580,497-byte archive with 117 entries. The archive contains the project source, processed JSONL files, saved outputs, pickled Majority and TF-IDF artifacts, and dashboard/paper materials. It does **not** contain any nonempty `data/raw/` files or the MTSamples CSV used by `src/data/real_mtsamples_loader.py`. There is therefore no source file with which to verify the records labeled `domain: "clinical"`, and the documented MTSamples origin cannot be confirmed from this workspace alone. The archive's source code and processed derivatives are available for inspection; the derivatives are not substitutes for the missing source corpus.

The notebook has nine code cells. It uses a Colab upload to obtain `medical-wsd.zip`, extracts it, changes into `medical-wsd`, reads `data/processed/real_wsd_preprocessed.jsonl`, fits a per-abbreviation majority baseline, TF-IDF + Logistic Regression, and a PennyLane variational classifier, and reports accuracy/F1. It also prints per-abbreviation scores and plots a model comparison. Imports include Colab upload, Python JSON/ZIP utilities, NumPy, Matplotlib, and project model/metric modules. The notebook outputs claim 404 training and 91 test rows; abbreviation counts over the loaded file total 580, which implies there are validation rows in the 580 total.

The ZIP has reusable implementations for conservative whitespace preprocessing/context windows, a group-by-abbreviation majority baseline, TF-IDF word and character n-gram Logistic Regression, evaluation/calibration helpers, synthetic generation, and a PennyLane simulator classifier. The real MTSamples loader and terminology dictionary are present. The project README explicitly identifies the synthetic Transformer as trained from scratch and the real-clinical domain-transfer result as pending. The existing app and project outputs can be retained as references, but their saved outputs require provenance checks before being presented as current results.

## Schema and split inspection

The archived processed real file contains 580 rows with fields including `id`, `text`, `sentence`, surrounding sentence fields, `abbreviation`, `target_span`, `sense`, integer `label`, `num_candidates`, `candidate_senses`, `domain`, `specialty`, `source_doc_index`, `label_source`, `split`, and context windows. It is split as 402 train / 96 val / 82 test. These are not the notebook's displayed 404 train / 91 test counts. Its split labels are `val`, whereas the notebook selects `train` and `test`.

The archived synthetic file contains 1,440 rows (1,007 train / 216 val / 217 test), with 20 abbreviations. It is distinctly labeled `domain: "synthetic"`; it must not be described as real clinical data.

The real schema does not contain character offsets, a label-verification status, a generation method, or a standardized group identifier. `target_span` is a marker string, not an offset, and the real `text` values contain no `[ABBR]...[/ABBR]` marker. `context_1` is only the marker text; the sentence-based contexts do include the abbreviation, but target occurrence and repeated-mention handling are not explicitly represented. Integer sense labels are local to each abbreviation's `candidate_senses` list, so a global per-class precision/recall/F1 over integer IDs conflates different meanings. Accuracy across examples remains interpretable for the per-abbreviation classifiers; aggregate macro-F1 should instead be calculated per abbreviation and reported with a clearly defined aggregation.

The real loader assigns labels by sentence-local lexical rules and otherwise falls back to full-form mention anywhere in the source document. Of 580 processed rows, 531 are marked `label_source: "local"` and 49 `document_level`. The lexical patterns used to create local labels are also present in the sentence context supplied to models. This is a material weak-label/circular-cue risk: a model may learn the labeling rules rather than demonstrate generalizable human-annotated WSD. There is no annotation guide or evidence of independent manual adjudication in the archive.

The new schema adapter derives an offset only when exactly one standalone target mention occurs in the legacy `sentence`. On the archived 580-row file, it safely adapts 470 rows. Of 110 rejected rows, 74 have multiple standalone mentions with no occurrence index; 36 have no abbreviation mention in the annotated sentence, though the abbreviation is present in wider context. This is an explicit data-loss boundary until occurrence-level annotations are recovered; the adapter does not guess. On the 470 adapted sentence contexts, 251 rows are repeats beyond unique text strings and 102 text strings cross splits. A row-level reason report is in `outputs/legacy_audit/legacy_rejections.jsonl`; accepted offset checks are in `outputs/legacy_audit/legacy_accepted_span_audit.jsonl`.

## Leakage and class imbalance findings

An exact-text audit of the archived processed real file finds 327 repeated rows beyond unique text values and 113 distinct text strings appearing in more than one split. The source-document IDs do not cross splits, so the loader's intended document grouping check alone would not detect these repeated contexts when they occur in distinct source rows/documents. The preprocessing `check_leakage` routine claims to count cross-split duplicate texts, but the archived processed file still contains such overlap. Near-duplicate/template checks have not been run. This is sufficient to make reported held-out performance suspect pending deduplication/grouping and re-evaluation.

The archived real test split has only 82 rows and is highly skewed by abbreviation: AP 26, LAD 23, MS 10, AV 9, PE 5, CA 4, PDA 3, PA 2. Several abbreviations have only one observed training sense (for example CA and LAD), and the held-out labels for them cannot assess WSD across senses. The archived synthetic test split is also generated from templates, so template-family separation must be verified before using it for evaluation.

The notebook's stated 95.6% majority score corresponds to 87 correct of 91. In the notebook's own per-abbreviation printout, the majority model has macro-F1 1.0 for seven abbreviations and 0.357 for AV; this is consistent with a per-abbreviation majority predictor benefiting from highly skewed or single-sense training labels and should not be read as broad disambiguation ability. The exact dataset version that produced those outputs is not present. A saved metric JSON in the archive for a different 91-row run reports Majority accuracy 85.7%, Logistic Regression 95.6%, and quantum simulator 96.7%; another saved `model_comparison.json` pertains to 217 synthetic test examples. Those outputs are not the notebook's displayed 100% Logistic Regression and quantum results. Because the current processed real file has a different split/count, none of these artifacts can be joined to a single verified data/model run from the files available here.

The notebook's 100% values are therefore **observed saved outputs, not reproduced results**. They are not supported by the archived current processed data or its saved metric outputs. Plausible risks include stale notebook outputs, duplicated contexts across splits, weak labels derived from the same lexical cues used as features, and per-abbreviation sense spaces. The available evidence does not distinguish their contribution. The notebook and archived source scripts do not show a final-test tuning step, but the absence of exact run inputs and predictions prevents a complete split-contamination or tuning audit.

## Quantum comparison

The archived `QuantumVariationalWSD` uses PennyLane's `default.qubit` simulator, preceded by TF-IDF and TruncatedSVD and followed by a trainable variational circuit. It is a classical simulation of a small quantum circuit, not quantum-hardware inference. The method is reproducible in principle only with its exact data, dependency versions, seed, source version, and saved predictions. The archive contains no quantum model checkpoint or notebook prediction file. The standalone runner exists, but its outputs use a data version inconsistent with the processed JSONL included in the same archive. No evidence here establishes a quantum advantage or even a valid, repeatable paired comparison.

## Reproduction status and recommended corrections

The exact notebook run cannot currently be reproduced: the notebook output's 404/91 split is absent, the raw MTSamples CSV is absent, and archived processed files/results disagree on row counts and scores. The 580-row archived processed file does permit new exploratory experiments, but those would not reproduce the notebook run and should not be presented as such. Dependencies are installed locally, but an exact rerun needs the matching input data and versioned run artifacts first.

Recommended order:

1. Recover the exact source CSV or other source corpus, annotation protocol, data-preparation script/version, and the processed JSONL that produced 404/91. Record checksums and licenses.
2. Preserve the notebook unchanged and export a clean copy only if needed for review. Save model predictions and per-abbreviation confusion tables alongside every new score.
3. Reconcile row IDs/splits across the notebook, processed files, and result JSON. Fail closed when artifacts disagree.
4. Independently review weakly labeled examples, particularly the 49 document-level fallbacks and a stratified sample of local-rule labels. Keep weak labels distinct from verified labels.
5. Deduplicate or group exact and near-duplicate source/context families before split assignment, then report eligible class counts per abbreviation and split.
6. Recompute a per-abbreviation majority baseline and classical model on the same eligible examples. Report accuracy, macro-F1 per abbreviation, and an explicit aggregation; isolate one-sense-only abbreviations from WSD claims.
7. Treat the simulator as exploratory only; compare against classical models with identical data and document hardware, runtime, seed, and prediction artifacts.

This audit identifies serious provenance and evaluation risks; it does not assert that all reported results are false. The original source inputs needed to resolve the risks are missing.
