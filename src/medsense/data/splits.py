"""Group-safe split validation."""
from collections.abc import Iterable
from collections import defaultdict
import random

from .schema import Example


def validate_group_separation(examples: Iterable[Example]) -> None:
    groups: dict[str, set[str]] = defaultdict(set)
    for example in examples:
        example.validate()
        if example.split != "unassigned" and example.group_id != "unknown":
            groups[example.group_id].add(example.split)
    leaking = sorted(group for group, splits in groups.items() if len(splits) > 1)
    if leaking:
        raise ValueError(f"group leakage across splits: {leaking}")


def assign_group_splits(template_groups: list[dict], counts: dict[str, int], seed: int) -> dict[str, str]:
    """Assign whole template families to splits, stratified by abbreviation+sense.

    Each input is a template family with `group_id`, `target_abbreviation`, and
    `gold_sense`. Counts specify the number of distinct families per stratum.
    """
    if not counts or any(n < 0 for n in counts.values()):
        raise ValueError("split counts must be non-negative")
    if len({row["group_id"] for row in template_groups}) != len(template_groups):
        raise ValueError("template group IDs must be unique")
    strata: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in template_groups:
        strata[(row["target_abbreviation"], row["gold_sense"])].append(row["group_id"])
    assignment: dict[str, str] = {}
    rng = random.Random(seed)
    for stratum, group_ids in sorted(strata.items()):
        if sum(counts.values()) != len(group_ids):
            raise ValueError(
                f"split counts sum to {sum(counts.values())}, but stratum {stratum} "
                f"has {len(group_ids)} groups"
            )
        rng.shuffle(group_ids)
        cursor = 0
        for split, count in counts.items():
            for group_id in group_ids[cursor:cursor + count]:
                assignment[group_id] = split
            cursor += count
    return assignment
