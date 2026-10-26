"""Conservative target/context utilities that preserve punctuation and negation."""
from dataclasses import dataclass
from .schema import Example


@dataclass(frozen=True)
class TargetContext:
    left: str
    target: str
    right: str


def extract_context(example: Example, radius: int = 160) -> TargetContext:
    example.validate()
    if radius < 0:
        raise ValueError("radius must be non-negative")
    start = max(0, example.target_start - radius)
    end = min(len(example.text), example.target_end + radius)
    return TargetContext(example.text[start:example.target_start],
                         example.text[example.target_start:example.target_end],
                         example.text[example.target_end:end])


def mark_target(example: Example, left: str = "[TGT]", right: str = "[/TGT]") -> str:
    example.validate()
    return (example.text[:example.target_start] + left +
            example.text[example.target_start:example.target_end] + right +
            example.text[example.target_end:])


def find_target_spans(text: str, abbreviation: str) -> list[tuple[int, int]]:
    """Return all literal, case-sensitive mentions; callers must resolve ambiguity."""
    if not text or not abbreviation:
        return []
    spans, pos = [], 0
    while True:
        pos = text.find(abbreviation, pos)
        if pos < 0:
            return spans
        spans.append((pos, pos + len(abbreviation)))
        pos += len(abbreviation)
