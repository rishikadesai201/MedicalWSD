"""Metrics for the fixed synthetic held-out test set."""
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


def evaluate_predictions(examples, predictions):
    if len(examples) != len(predictions):
        raise ValueError("prediction count must match examples")
    labels = sorted({(row.target_abbreviation, row.gold_sense) for row in examples})
    class_names = [f"{abbr}::{sense}" for abbr, sense in labels]
    y_true = [f"{row.target_abbreviation}::{row.gold_sense}" for row in examples]
    y_pred = [f"{row.target_abbreviation}::{pred}" for row, (pred, _score) in zip(examples, predictions)]
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=class_names, zero_division=0
    )
    per_sense = {
        name: {"precision": float(p), "recall": float(r), "f1": float(f), "support": int(n)}
        for name, p, r, f, n in zip(class_names, precision, recall, f1, support)
    }
    matrix = confusion_matrix(y_true, y_pred, labels=class_names)
    return {
        "n_test": len(examples),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(sum(f1) / len(f1)) if len(f1) else 0.0,
        "per_sense": per_sense,
        "confusion_matrix_labels": class_names,
        "confusion_matrix": matrix.tolist(),
    }
