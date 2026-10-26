import pytest

from medsense.data.legacy import AmbiguousTargetError, legacy_to_example
from medsense.data.preprocess import extract_context, find_target_spans, mark_target
from medsense.data.schema import Example
from medsense.data.splits import validate_group_separation
from medsense.data.validate_data import validate_examples


def make_example(text="At follow-up, MS was stable.", start=14, end=16, **kwargs):
    values = dict(
        example_id="ex-1", text=text, target_abbreviation="MS",
        target_start=start, target_end=end, gold_sense="Multiple Sclerosis",
        candidate_senses=("Multiple Sclerosis", "Mental Status"), split="train",
        group_id="group-a",
    )
    values.update(kwargs)
    return Example(**values)


def test_offsets_are_end_exclusive_and_validated():
    example = make_example()
    example.validate()
    with pytest.raises(ValueError, match="does not match"):
        make_example(start=16, end=18).validate()
    with pytest.raises(ValueError, match="valid end-exclusive"):
        make_example(start=-1, end=1).validate()


@pytest.mark.parametrize("text", ["MS was noted.", "No MS.", "No finding."])
def test_target_search_handles_edges_and_missing(text):
    spans = find_target_spans(text, "MS")
    if text == "No finding.":
        assert spans == []
    elif text.startswith("MS"):
        assert spans == [(0, 2)]
    else:
        assert spans == [(3, 5)]


def test_repeated_target_spans_are_all_returned_and_mark_uses_annotated_one():
    text = "MS stable; MS reviewed."
    spans = find_target_spans(text, "MS")
    assert spans == [(0, 2), (11, 13)]
    example = Example("e", text, "MS", 11, 13, "Multiple Sclerosis")
    assert mark_target(example) == "MS stable; [TGT]MS[/TGT] reviewed."


def test_context_preserves_punctuation_and_negation():
    example = Example("e", "No fever; MS?", "MS", 10, 12, "Mental Status")
    context = extract_context(example, radius=20)
    assert context.target == "MS"
    assert "No fever; " in context.left
    assert context.right == "?"


def test_group_overlap_is_rejected():
    first = make_example()
    second = make_example(example_id="ex-2", split="test")
    with pytest.raises(ValueError, match="group leakage"):
        validate_group_separation([first, second])


def test_quality_report_counts_cross_split_duplicates():
    first = make_example()
    second = make_example(example_id="ex-2", split="test")
    report = validate_examples([first, second])
    assert report["duplicate_text_count"] == 1
    assert report["cross_split_duplicate_texts"] == 1
    assert report["invalid_examples"] == []


def test_legacy_adapter_preserves_label_but_marks_it_unverified():
    row = {
        "id": 4, "sentence": "MS assessment completed.", "abbreviation": "MS",
        "sense": "Mental Status", "label": 1,
        "candidate_senses": ["Multiple Sclerosis", "Mental Status"],
        "split": "val", "domain": "clinical", "label_source": "local",
        "source_doc_index": 9,
    }
    example = legacy_to_example(row)
    assert example.gold_sense == "Mental Status"
    assert example.original_label == 1
    assert example.split == "validation"
    assert example.label_verified is False
    assert example.generation_method == "weak_label_local_rule"


def test_legacy_adapter_refuses_repeated_unmarked_target():
    row = {"id": 5, "sentence": "MS and MS.", "abbreviation": "MS", "sense": "x"}
    with pytest.raises(AmbiguousTargetError):
        legacy_to_example(row)
