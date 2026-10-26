# Baseline test error analysis

This report reuses the saved predictions for the 36-example synthetic test split and joins them to the saved examples for sentence text. No model was retrained. Both prediction files contain the same three errors, so the error overlap is **3/3**; neither model has a unique error on this split.

## Errors by abbreviation and sense

All errors are for **PE**. For each row, the indicated true sense was predicted as the listed sense by both models.

| True sense | Predicted sense | Count | Test sentence |
|---|---|---:|---|
| Physical examination | Pulmonary embolism | 1 | “The clinical worksheet puts auscultation notes in the PE subsection.” |
| Physical examination | Pulmonary embolism | 1 | “A staging vignette places clinical examination findings in the PE section.” |
| Pulmonary embolism | Physical examination | 1 | “The PE discussion follows the note about a deep-vein thrombus and chest imaging.” |

The first two rows together are two errors with the same true/predicted sense pair. No AP or PA test example was misclassified.

## Observed patterns

- The most frequent confusion is **Physical examination → Pulmonary embolism** (2 examples).
- The reverse confusion, **Pulmonary embolism → Physical examination**, occurs once.
- These are the only confusion patterns in either model's errors. The sentences above describe the examples; this small synthetic test set does not support a broader linguistic or medical explanation.

## Artifacts

- [Logistic Regression predictions](../outputs/baseline/tfidf_logistic_regression_test_predictions.jsonl)
- [Linear SVM predictions](../outputs/baseline/tfidf_linear_svm_test_predictions.jsonl)
- [Synthetic examples](../data/synthetic/verified_examples.jsonl)
