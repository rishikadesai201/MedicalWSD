"""Validated example representation; offsets use Python Unicode code points, end-exclusive."""
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Example:
    example_id: str
    text: str
    target_abbreviation: str
    target_start: int
    target_end: int
    gold_sense: str
    specialty: str = "unknown"
    difficulty: str = "unknown"
    source_type: str = "unknown"
    source_reference: str = "unknown"
    generation_method: str = "unknown"
    group_id: str = "unknown"
    label_verified: bool = False
    split: str = "unassigned"
    original_label: int | str | None = None
    candidate_senses: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.example_id.strip() or not self.text:
            raise ValueError("example_id and text must be non-empty")
        if not self.target_abbreviation:
            raise ValueError("target_abbreviation must be non-empty")
        if not (0 <= self.target_start < self.target_end <= len(self.text)):
            raise ValueError("target offsets must be a valid end-exclusive span")
        if self.text[self.target_start:self.target_end] != self.target_abbreviation:
            raise ValueError("target span does not match target_abbreviation")
        if not self.gold_sense:
            raise ValueError("gold_sense must be non-empty")
        if self.split not in {"unassigned", "train", "validation", "test"}:
            raise ValueError(f"unsupported split: {self.split}")
        if self.candidate_senses and self.gold_sense not in self.candidate_senses:
            raise ValueError("gold_sense is absent from candidate_senses")

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Example":
        values = dict(row)
        if "candidate_senses" in values:
            values["candidate_senses"] = tuple(values["candidate_senses"])
        obj = cls(**values)
        obj.validate()
        return obj

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)
