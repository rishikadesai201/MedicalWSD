"""Streamlit demo and reviewed-v1 evaluation dashboard."""
from pathlib import Path
import sys

# Streamlit runs app.py from the repository root, which does not put this
# src-layout package on sys.path unless the project was installed first.
PROJECT_SRC = Path(__file__).resolve().parent / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

import streamlit as st

from medsense.evaluation.visualization_data import (
    EvaluationArtifactsError,
    MODEL_NAMES,
    load_reviewed_evaluation,
)
from medsense.inference import ModelUnavailableError, predict_sentence


st.set_page_config(
    page_title="MedSense AI — Medical Abbreviation Disambiguation",
    page_icon="🩺",
    layout="wide",
)
st.markdown(
    """
    <style>
    .block-container {max-width: 1200px; padding-top: 2rem; padding-bottom: 3rem;}
    .eyebrow {color: #147d72; font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;}
    .hero {background: linear-gradient(135deg, #eef8f6, #f6f9fc); border: 1px solid #dcebe8;
           border-radius: 18px; padding: 1.25rem 1.5rem; margin-bottom: 1.1rem;}
    .hero h1 {font-size: 2rem; line-height: 1.2;}
    .note {background: #f6f9fc; border: 1px solid #e3eaf0; border-radius: 12px; padding: 1rem 1.1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero"><div class="eyebrow">Academic research prototype</div>'
    '<h1 style="margin:.35rem 0 .4rem">MedSense AI — Medical Abbreviation Disambiguation</h1>'
    '<div style="color:#52616b">Traditional baseline preview and held-out evaluation</div></div>',
    unsafe_allow_html=True,
)
st.warning(
    "Academic research prototype only. This is not a clinical decision-support tool and must not be used "
    "to make diagnosis or treatment decisions. Model output is not medically verified information."
)
st.info(
    "The reviewed dataset is a small, AI-assisted synthetic subset, not an independently medically validated "
    "clinical benchmark. AP is excluded from the current two-sense evaluation because no AP Anteroposterior "
    "examples were accepted."
)

predict_tab, results_tab = st.tabs(["Disambiguate", "Results & Visualizations"])

with predict_tab:
    st.subheader("Try a sentence")
    abbreviation = st.text_input(
        "Abbreviation",
        max_chars=12,
        help="Enter an abbreviation manually. Predictions are currently supported only for PE and PA.",
    )
    st.caption("The saved inference model currently supports PE and PA. AP and other terms are not supported for prediction.")
    with st.form("disambiguation_form"):
        sentence = st.text_area(
            "Clinical-style sentence",
            placeholder="Paste one sentence containing a single PE or PA target occurrence.",
            height=125,
        )
        submitted = st.form_submit_button("Disambiguate", type="primary", use_container_width=True)

    if submitted:
        try:
            result = predict_sentence(sentence, abbreviation)
        except ValueError as exc:
            st.error(str(exc))
        except ModelUnavailableError as exc:
            st.error(f"Inference unavailable. {exc}")
        except Exception as exc:
            st.error(f"The model could not complete this request: {exc}")
        else:
            st.success(f"Predicted sense: **{result['predicted_sense']}**")
            st.metric("Uncalibrated SVM decision margin", f"{result['score']:.3f}")
            st.caption("The decision margin is not a probability and is not calibrated as confidence.")
            st.markdown(
                '<div class="note"><strong>How to read this result</strong><br>'
                "The TF-IDF Linear SVM selects a supported sense using learned word n-gram boundaries. "
                "This model output is not a medical explanation or verification.</div>",
                unsafe_allow_html=True,
            )
    st.caption(
        "Inference model: reviewed-v1 TF-IDF + Linear SVM, fitted on the training split only. "
        "It supports PA and PE; AP is not part of two-sense inference."
    )

with results_tab:
    st.subheader("Results & Visualizations")
    st.caption(
        "All charts below read the saved reviewed-v1 test metrics, predictions, and dataset. "
        "The evaluated test set has 10 examples and is separate from model training."
    )
    try:
        dashboard = load_reviewed_evaluation()
    except EvaluationArtifactsError as exc:
        st.warning(f"Evaluation visualizations are unavailable: {exc}")
    else:
        metrics = dashboard["metrics"]
        summary_columns = st.columns(6)
        summary_columns[0].metric("Evaluation dataset", "Reviewed v1")
        summary_columns[1].metric("Held-out test rows", dashboard["n_test_examples"])
        summary_columns[2].metric("Logistic Regression accuracy", f"{metrics[MODEL_NAMES[0]]['accuracy']:.3f}")
        summary_columns[3].metric("Logistic Regression macro-F1", f"{metrics[MODEL_NAMES[0]]['macro_f1']:.3f}")
        summary_columns[4].metric("Linear SVM accuracy", f"{metrics[MODEL_NAMES[1]]['accuracy']:.3f}")
        summary_columns[5].metric("Linear SVM macro-F1", f"{metrics[MODEL_NAMES[1]]['macro_f1']:.3f}")

        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError as exc:
            st.warning(f"Charts need the existing UI extra (Matplotlib): {exc}")
        else:
            st.markdown("#### Model comparison")
            model_labels = ["TF-IDF + Logistic Regression", "TF-IDF + Linear SVM"]
            positions = np.arange(len(model_labels))
            width = 0.34
            fig, ax = plt.subplots(figsize=(8, 4.2))
            ax.bar(positions - width / 2, [metrics[name]["accuracy"] for name in MODEL_NAMES],
                   width, label="Accuracy", color="#147d72")
            ax.bar(positions + width / 2, [metrics[name]["macro_f1"] for name in MODEL_NAMES],
                   width, label="Macro-F1", color="#7a91bd")
            ax.set_xticks(positions, model_labels)
            ax.set_ylim(0, 1.05)
            ax.set_ylabel("Score")
            ax.set_title("Reviewed-v1 held-out test metrics")
            ax.legend(frameon=False)
            ax.grid(axis="y", alpha=.2)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            st.markdown("#### Confusion matrices")
            st.caption("Rows are true labels; columns are predicted labels. Counts come from saved test metrics.")
            for name, label in zip(MODEL_NAMES, model_labels):
                metric = metrics[name]
                fig, ax = plt.subplots(figsize=(8, 5.2))
                matrix = np.asarray(metric["confusion_matrix"])
                image = ax.imshow(matrix, cmap="Blues")
                ax.set_xticks(range(len(metric["confusion_matrix_labels"])),
                              metric["confusion_matrix_labels"], rotation=28, ha="right")
                ax.set_yticks(range(len(metric["confusion_matrix_labels"])),
                              metric["confusion_matrix_labels"])
                ax.set_xlabel("Predicted class")
                ax.set_ylabel("True class")
                ax.set_title(f"{label} — test confusion matrix")
                for i in range(matrix.shape[0]):
                    for j in range(matrix.shape[1]):
                        ax.text(j, i, str(matrix[i, j]), ha="center", va="center",
                                color="white" if matrix[i, j] > matrix.max() / 2 else "#18242d")
                fig.colorbar(image, ax=ax, label="Examples")
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

            st.markdown("#### Per-class precision, recall, and F1")
            first_metrics = metrics[MODEL_NAMES[0]]["per_sense"]
            classes = list(first_metrics)
            class_positions = np.arange(len(classes))
            width = .24
            fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)
            for ax, name, label in zip(axes, MODEL_NAMES, model_labels):
                class_metrics = metrics[name]["per_sense"]
                for offset, measure, color in [(-width, "precision", "#147d72"),
                                               (0, "recall", "#7a91bd"),
                                               (width, "f1", "#e4a54f")]:
                    values = [class_metrics[class_name][measure] for class_name in classes]
                    ax.bar(class_positions + offset, values, width, label=measure.title(), color=color)
                ax.set_xticks(class_positions, classes, rotation=22, ha="right")
                ax.set_ylim(0, 1.05)
                ax.set_title(label)
                ax.grid(axis="y", alpha=.2)
            axes[0].set_ylabel("Score")
            axes[1].legend(frameon=False, ncols=3)
            fig.suptitle("Per-class metrics on eligible PA and PE senses")
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            st.markdown("#### Accepted dataset composition by split")
            composition = dashboard["dataset_composition"]
            class_labels = [row["class"] for row in composition]
            fig, ax = plt.subplots(figsize=(10, max(4.2, .45 * len(composition))))
            left = np.zeros(len(composition))
            for split, color in [("train", "#147d72"), ("validation", "#7a91bd"), ("test", "#e4a54f")]:
                values = np.asarray([row[split] for row in composition])
                ax.barh(class_labels, values, left=left, label=split.title(), color=color)
                left += values
            ax.set_xlabel("Accepted examples")
            ax.set_title("Reviewed-v1 dataset examples (split counts, not evaluation scores)")
            ax.legend(frameon=False, ncols=3)
            ax.grid(axis="x", alpha=.2)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.dataframe(composition, use_container_width=True, hide_index=True)

            st.markdown("#### Test prediction breakdown")
            breakdown = []
            for name, label in zip(MODEL_NAMES, model_labels):
                rows = dashboard["predictions"][name]
                breakdown.append({"Model": label,
                                  "Correct": sum(bool(row["correct"]) for row in rows),
                                  "Incorrect": sum(not bool(row["correct"]) for row in rows)})
            fig, ax = plt.subplots(figsize=(7.5, 3.8))
            x = np.arange(len(breakdown))
            ax.bar(x, [row["Correct"] for row in breakdown], label="Correct", color="#147d72")
            ax.bar(x, [row["Incorrect"] for row in breakdown],
                   bottom=[row["Correct"] for row in breakdown], label="Incorrect", color="#d77968")
            ax.set_xticks(x, [row["Model"] for row in breakdown])
            ax.set_ylabel("Test examples")
            ax.set_title(f"Correct vs incorrect predictions (n={dashboard['n_test_examples']})")
            ax.legend(frameon=False)
            ax.grid(axis="y", alpha=.2)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            mistakes = [
                {"Model": label, "Abbreviation": row["target_abbreviation"], "Sentence": row["text"],
                 "True sense": row["gold_sense"], "Predicted sense": row["predicted_sense"]}
                for name, label in zip(MODEL_NAMES, model_labels)
                for row in dashboard["prediction_errors"][name]
            ]
            if mistakes:
                st.markdown("##### Misclassified held-out examples")
                st.dataframe(mistakes, use_container_width=True, hide_index=True)
            else:
                st.caption("No errors are present in the saved test predictions.")

        st.caption(
            "The 10-example test set is small and comes from a filtered, AI-assisted synthetic dataset. "
            "These results are not clinically validated and do not establish broad generalization. "
            "Historical baseline results are not mixed into these charts."
        )
