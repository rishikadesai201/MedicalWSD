# MedSense AI

MedSense AI is a research project scaffold for studying medical abbreviation word-sense disambiguation and generalization across text domains. The supplied original notebook and `medical-wsd.zip` are preserved at the workspace root. The ZIP contains project source, processed JSONL datasets, saved metrics, and some model artifacts, but not the source MTSamples CSV. Its current data and metric files disagree with the notebook outputs, and its “real” labels are automatically weak-labeled. See the audit before treating those archived results as evidence. This repo now includes a separate, newly evaluated synthetic-template baseline; it does not present a trained clinical system.

## Setup

Use Python 3.11 or newer in a virtual environment, then install the pinned dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Current status

- Audit findings: [docs/initial_audit.md](docs/initial_audit.md)
- Dataset schema and core utilities: `src/medsense`
- The original bundle is preserved as `medical-wsd.zip`; its processed-data and saved-result provenance limitations are documented in the audit.
- The new adapter preserves source labels, marks them unverified, standardizes split naming, and refuses ambiguous target offsets.
- Deterministic synthetic data uses three reviewed abbreviations (PE, PA, AP), with two documented senses each. All examples are fictional educational text, never patient records.
- Preliminary results are limited to held-out synthetic template families; they do not establish generalization to clinical records.

## Generate data and run the preliminary baseline

After installation, run:

```powershell
medsense audit-legacy
medsense generate-synthetic
medsense train-baselines
python -m pytest -q
```

The generator writes the small checked-in JSONL dataset and its quality report. The baseline uses training groups only and evaluates once on separately assigned template families; validation data is not used to tune these initial settings. Metrics, predictions, and the run configuration are saved under `outputs/baseline/`.

Terminology references and caveats are listed in [data/terminology/verified_senses.yaml](data/terminology/verified_senses.yaml) and [the dataset card](docs/synthetic_dataset_card.md). Legacy-data findings are in [docs/legacy_data_audit.md](docs/legacy_data_audit.md).

Use `pytest` to run the starter utility tests. Do not interpret the schema smoke fixtures as a medical dataset.

## Streamlit demo

Install the existing UI extra (Streamlit and Matplotlib are already declared), fit the versioned inference artifact from the reviewed-v1 training split, then run the app:

```powershell
python -m pip install -e ".[ui]"
python -m medsense.training.train_inference_model
streamlit run app.py
```

The new Linear SVM artifact and reproducibility metadata are saved under `outputs/reviewed_v1_inference_v1/`. Training uses only the reviewed-v1 `train` split (23 examples); it never fits or selects on validation/test data, and it refuses to overwrite an existing artifact directory. It supports PA and PE. AP is excluded because only Anterior pituitary remains in the reviewed data.

The **Results & Visualizations** tab reads the saved reviewed-v1 evaluation files under `outputs/reviewed_v1_traditional_baseline/`: model comparison, separate confusion matrices, per-class precision/recall/F1, dataset class/split composition, prediction correctness, and an error table. It shows the 10-example test size and separates evaluation results from the new inference artifact. Missing or malformed evaluation files produce an explanatory message instead of fabricated charts.

The reviewed dataset is a small AI-assisted synthetic subset, not independently medically validated clinical text. Its 10-example test results are descriptive only and are not directly comparable to the original baseline. The SVM score is an uncalibrated decision margin, not a confidence probability. No clinical accuracy or generalization claim is supported. If the saved model artifact is unavailable, the app disables prediction and reports the missing artifact.
