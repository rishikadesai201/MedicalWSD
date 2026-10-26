"""JSONL loading and data-quality checks for normalized examples."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import re
from typing import Iterable

from .schema import Example


def load_jsonl(path: str | Path) -> list[dict]:
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_no}: {exc.msg}") from exc
    return rows


def validate_examples(examples: Iterable[Example]) -> dict:
    examples = list(examples)
    ids: Counter[str] = Counter()
    text_splits: dict[str, set[str]] = defaultdict(set)
    text_counts: Counter[str] = Counter()
    normalized_splits: dict[str, set[str]] = defaultdict(set)
    normalized_counts: Counter[str] = Counter()
    by_abbr_sense: Counter[tuple[str, str]] = Counter()
    by_abbr: Counter[str] = Counter()
    by_split: Counter[str] = Counter()
    by_source: Counter[str] = Counter()
    by_difficulty: Counter[str] = Counter()
    by_generation: Counter[str] = Counter()
    by_verification: Counter[str] = Counter()
    invalid: list[str] = []
    for example in examples:
        try:
            example.validate()
        except ValueError as exc:
            invalid.append(f"{example.example_id}: {exc}")
            continue
        ids[example.example_id] += 1
        text_splits[example.text].add(example.split)
        text_counts[example.text] += 1
        normalized = re.sub(r"\s+", " ", example.text).strip().casefold()
        normalized_splits[normalized].add(example.split)
        normalized_counts[normalized] += 1
        by_abbr_sense[(example.target_abbreviation, example.gold_sense)] += 1
        by_abbr[example.target_abbreviation] += 1
        by_split[example.split] += 1
        by_source[example.source_type] += 1
        by_difficulty[example.difficulty] += 1
        by_generation[example.generation_method] += 1
        by_verification["verified" if example.label_verified else "unverified"] += 1
    duplicate_texts = {text for text, count in text_counts.items() if count > 1}
    cross_split = {text for text in duplicate_texts if len(text_splits[text]) > 1}
    duplicate_normalized = {text for text, count in normalized_counts.items() if count > 1}
    cross_split_normalized = {text for text in duplicate_normalized if len(normalized_splits[text]) > 1}
    duplicates_by_abbr: Counter[str] = Counter(
        ex.target_abbreviation for ex in examples if ex.text in duplicate_texts
    )
    return {
        "n_examples": len(examples),
        "invalid_examples": invalid,
        "duplicate_id_count": sum(count - 1 for count in ids.values() if count > 1),
        "duplicate_text_count": sum(count - 1 for count in text_counts.values() if count > 1),
        "cross_split_duplicate_texts": len(cross_split),
        "normalized_duplicate_count": sum(count - 1 for count in normalized_counts.values() if count > 1),
        "cross_split_normalized_duplicate_texts": len(cross_split_normalized),
        "duplicate_rows_by_abbreviation": dict(duplicates_by_abbr),
        "examples_by_abbreviation_and_sense": {
            f"{abbr}::{sense}": count for (abbr, sense), count in sorted(by_abbr_sense.items())
        },
        "examples_by_abbreviation": dict(by_abbr),
        "examples_by_split": dict(by_split),
        "examples_by_source_type": dict(by_source),
        "examples_by_difficulty": dict(by_difficulty),
        "examples_by_generation_method": dict(by_generation),
        "label_verification_status": dict(by_verification),
    }
