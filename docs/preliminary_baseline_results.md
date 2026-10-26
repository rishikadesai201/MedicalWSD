# Preliminary synthetic baseline results

**Run seed:** 20261026 (data grouping and model configuration)  
**Dataset:** 132 authored synthetic examples; 72 train, 24 validation, 36 test  
**Test design:** 18 held-out template families, two variants per family; six test rows per canonical sense. Groups do not overlap. Validation was not used for tuning.

| Model | Accuracy | Macro-F1 |
|---|---:|---:|
| Per-abbreviation majority | 0.5000 | 0.3333 |
| TF-IDF word unigram/bigram + per-abbreviation Logistic Regression | 0.9167 | 0.9161 |
| TF-IDF word unigram/bigram + per-abbreviation Linear SVM | 0.9167 | 0.9161 |

TF-IDF + Logistic Regression gets all 24 AP and PA examples correct. For PE, it gets 4/6 Physical examination examples and 5/6 Pulmonary embolism examples correct. The three errors are two Physical examination templates predicted as Pulmonary embolism and one Pulmonary embolism template predicted as Physical examination. The corresponding per-sense precision, recall, F1 and six-class confusion matrix are in the saved metrics JSON.

The Linear SVM has the same measured accuracy, macro-F1, per-sense metrics, and predictions as Logistic Regression on this test set (zero prediction disagreements). It therefore does not outperform Logistic Regression in this run. SVM parameters were fixed in advance; the validation split was not used for model selection, and neither model was tuned on the test split.

These are actual outputs from the code and data in this repository, not reported notebook results. They are a small controlled sanity check: the model is evaluated on separate authored template families, but the task's narrow sense inventory and template language remain artificial. No claim of clinical accuracy or real cross-domain generalization follows from these scores.

Artifacts:

- [Summary metrics](../outputs/baseline/summary_metrics.json)
- [Run configuration and library versions](../outputs/baseline/run_config.json)
- [Majority per-example predictions](../outputs/baseline/majority_test_predictions.jsonl)
- [Logistic Regression per-example predictions](../outputs/baseline/tfidf_logistic_regression_test_predictions.jsonl)
- [Linear SVM metrics](../outputs/baseline/tfidf_linear_svm_metrics.json)
- [Linear SVM per-example predictions](../outputs/baseline/tfidf_linear_svm_test_predictions.jsonl)
- [Linear SVM run configuration](../outputs/baseline/tfidf_linear_svm_run_config.json)
- [Synthetic dataset quality report](../data/synthetic/quality_report.json)
