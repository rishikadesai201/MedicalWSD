"""Deterministic, source-documented synthetic example generation."""
from collections import Counter
import json
from pathlib import Path
import random
import re

import yaml

from .schema import Example
from .splits import assign_group_splits, validate_group_separation
from .templates import TEMPLATE_FAMILIES
from .validate_data import validate_examples


def generate(config_path: str | Path = "configs/synthetic.yaml") -> tuple[list[Example], dict]:
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    terminology_path = Path(config["terminology_path"])
    terminology = yaml.safe_load(terminology_path.read_text(encoding="utf-8"))["abbreviations"]
    seed = int(config["seed"])
    per_template = int(config["variants_per_template"])
    if per_template < 1:
        raise ValueError("variants_per_template must be positive")

    families = []
    for template in TEMPLATE_FAMILIES:
        abbr, sense = template["abbr"], template["sense"]
        if abbr not in terminology:
            raise ValueError(f"template abbreviation {abbr!r} is not terminology-reviewed")
        sense_rows = terminology[abbr]["senses"]
        matching = [item for item in sense_rows if item["gold_sense"] == sense]
        if len(matching) != 1 or matching[0].get("verification_status") != "terminology_verified":
            raise ValueError(f"template label {abbr}::{sense} lacks one verified terminology mapping")
        if len(template["texts"]) < per_template:
            raise ValueError(f"template {template['family']} has fewer variants than configured")
        families.append({
            "group_id": f"{abbr.lower()}-{template['family']}",
            "target_abbreviation": abbr,
            "gold_sense": sense,
            "template": template,
        })

    splits = {str(k): int(v) for k, v in config["split_template_families"].items()}
    assignment = assign_group_splits(families, splits, seed)
    rng = random.Random(seed)
    examples = []
    for family in sorted(families, key=lambda row: row["group_id"]):
        template = family["template"]
        abbr, sense, group_id = family["target_abbreviation"], family["gold_sense"], family["group_id"]
        term = next(item for item in terminology[abbr]["senses"] if item["gold_sense"] == sense)
        texts = list(template["texts"])
        rng.shuffle(texts)
        split = assignment[group_id]
        for variant_index, text in enumerate(texts[:per_template]):
            matches = list(re.finditer(rf"(?<!\w){re.escape(abbr)}(?!\w)", text))
            if len(matches) != 1:
                raise ValueError(f"template {template['family']} must contain exactly one standalone {abbr}")
            match = matches[0]
            example = Example(
                example_id=f"syn-{group_id}-{variant_index + 1}",
                text=text,
                target_abbreviation=abbr,
                target_start=match.start(),
                target_end=match.end(),
                gold_sense=sense,
                specialty="synthetic_mixed_context",
                difficulty=template["difficulty"],
                source_type="synthetic",
                source_reference="; ".join(ref["url"] for ref in term["references"]),
                generation_method="deterministic_template_v1",
                group_id=group_id,
                label_verified=True,
                split=split,
                candidate_senses=tuple(item["gold_sense"] for item in terminology[abbr]["senses"]),
            )
            example.validate()
            examples.append(example)

    examples.sort(key=lambda ex: ex.example_id)
    validate_group_separation(examples)
    quality = validate_examples(examples)
    quality.update({
        "dataset_label": config.get("dataset_label", "synthetic"),
        "seed": seed,
        "variants_per_template": per_template,
        "template_families": len(families),
        "template_families_by_split": dict(Counter(assignment.values())),
        "group_split_leakage": False,
        "invalid_target_span_count": sum(bool(item) for item in quality["invalid_examples"]),
        "label_validation": "all gold senses resolve to terminology_verified entries; examples are synthetic and not patient data",
        "insufficient_context_examples": 0,
        "insufficient_context_policy": "excluded; no gold sense is assigned without context",
    })
    if quality["invalid_examples"] or quality["duplicate_id_count"] or quality["duplicate_text_count"]:
        raise ValueError(f"generated dataset failed validation: {quality}")
    if quality["cross_split_normalized_duplicate_texts"]:
        raise ValueError("generated dataset has normalized duplicate text across splits")

    output_path = Path(config["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for example in examples:
            handle.write(json.dumps(example.to_dict(), ensure_ascii=False) + "\n")
    report_path = Path(config["quality_report_path"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(quality, indent=2, ensure_ascii=False), encoding="utf-8")
    return examples, quality


if __name__ == "__main__":
    generated, report = generate()
    print(json.dumps({"examples": len(generated), "quality": report}, indent=2))
