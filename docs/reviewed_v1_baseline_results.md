# Reviewed synthetic v1: traditional baselines

## Evaluation scope

TF-IDF + Logistic Regression and TF-IDF + Linear SVM use the existing reviewed v1 train/test assignments. The models fit on training data only; the validation split was reported but not used for model selection. Evaluation includes **10 test examples** from PA and PE. AP is excluded: only Anterior pituitary has accepted examples, so AP does not form a two-sense WSD task. The minimum training support was two examples per sense; each evaluated sense meets it.

| Abbreviation / sense | Train | Validation | Test |
|---|---:|---:|---:|
| AP — Anterior pituitary | 11 | 3 | 5 |
| AP — Anteroposterior | 0 | 0 | 0 |
| PA — Physician assistant | 5 | 2 | 2 |
| PA — Pulmonary artery | 3 | 2 | 1 |
| PE — Physical examination | 6 | 0 | 3 |
| PE — Pulmonary embolism | 9 | 2 | 4 |

The evaluated training subset has 23 examples and validation has 6. Per-class test support is small (1–4 examples), so metrics are descriptive and uncertain.

## Results

| Model | Test examples | Accuracy | Macro-F1 |
|---|---:|---:|---:|
| TF-IDF + Logistic Regression | 10 | 0.7000 | 0.5250 |
| TF-IDF + Linear SVM | 10 | 0.8000 | 0.6222 |

Per-class precision / recall / F1 (support):

| Class | Logistic Regression | Linear SVM |
|---|---|---|
| PA — Physician assistant | 0.667 / 1.000 / 0.800 (2) | 0.667 / 1.000 / 0.800 (2) |
| PA — Pulmonary artery | 0.000 / 0.000 / 0.000 (1) | 0.000 / 0.000 / 0.000 (1) |
| PE — Physical examination | 1.000 / 0.333 / 0.500 (3) | 1.000 / 0.667 / 0.800 (3) |
| PE — Pulmonary embolism | 0.667 / 1.000 / 0.800 (4) | 0.800 / 1.000 / 0.889 (4) |

Confusion matrices use this row and column order: PA Physician assistant, PA Pulmonary artery, PE Physical examination, PE Pulmonary embolism.

```text
Logistic Regression (true rows, predicted columns)
[[2, 0, 0, 0],
 [1, 0, 0, 0],
 [0, 0, 1, 2],
 [0, 0, 0, 4]]

Linear SVM (true rows, predicted columns)
[[2, 0, 0, 0],
 [1, 0, 0, 0],
 [0, 0, 2, 1],
 [0, 0, 0, 4]]
```

The SVM scores higher on this particular 10-example subset (8 correct versus 7), but this is too small to support a general performance claim. The original synthetic baseline used 36 test examples and included AP; it reported 0.9167 accuracy / 0.9161 macro-F1 for both models. Those figures are **not directly comparable**: reviewed v1 is a filtered AI-assisted subset with different class coverage, support, and evaluation scope. Neither result establishes clinical generalization.

## Reproducibility artifacts

- [Run configuration, class counts, and dataset hash](../outputs/reviewed_v1_traditional_baseline/run_config.json)
- [Summary metrics](../outputs/reviewed_v1_traditional_baseline/summary_metrics.json)
- [Logistic Regression metrics](../outputs/reviewed_v1_traditional_baseline/tfidf_logistic_regression_metrics.json)
- [Logistic Regression predictions](../outputs/reviewed_v1_traditional_baseline/tfidf_logistic_regression_test_predictions.jsonl)
- [Linear SVM metrics](../outputs/reviewed_v1_traditional_baseline/tfidf_linear_svm_metrics.json)
- [Linear SVM predictions](../outputs/reviewed_v1_traditional_baseline/tfidf_linear_svm_test_predictions.jsonl)
