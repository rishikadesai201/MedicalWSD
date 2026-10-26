# Existing notebook reference

The original `NLP (2).ipynb` is kept unchanged at the workspace root. It has nine cells and uses a Colab upload to extract `medical-wsd.zip`, loads the archived processed real WSD JSONL, fits Majority, TF-IDF + Logistic Regression, and a PennyLane variational classifier, prints overall and per-abbreviation metrics, and plots a comparison. Its saved outputs show 404 train / 91 test and 100% accuracy for the two trained models.

Those outputs are not reproducible from the ZIP's present processed real file (402/96/82) or the conflicting saved 91-row metrics. See [initial_audit.md](../docs/initial_audit.md) for the evidence and limitations. Do not edit the original notebook when building a corrected experiment.
