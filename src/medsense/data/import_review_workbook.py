"""Import human decisions from the assisted Excel workbook to a new review CSV."""
import argparse
import csv
import json
import posixpath
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

from .review_validation import summarize_review_rows
from .validate_data import load_jsonl


OUTPUT_FIELDS = [
    "example_id", "abbreviation", "sentence", "target_span", "target_start", "target_end",
    "assigned_sense", "candidate_senses", "review_flags", "generation_method", "group_id",
    "difficulty", "source_type", "source_reference", "split", "label_verified",
    "reviewer_decision", "reviewer_revised_sense", "reviewer_comments",
]
REQUIRED_FIELDS = set(OUTPUT_FIELDS)
DEFAULT_DATASET = Path(__file__).resolve().parents[3] / "data/synthetic/verified_examples.jsonl"
NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "office_rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def _column_index(cell_reference):
    letters = re.match(r"[A-Z]+", cell_reference).group()
    index = 0
    for letter in letters:
        index = index * 26 + ord(letter) - ord("A") + 1
    return index - 1


def _workbook_rows(path, sheet_name):
    """Read cell values from a simple .xlsx sheet using the standard library."""
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}
        sheet = next((node for node in workbook.findall(".//main:sheet", NS)
                      if node.attrib["name"] == sheet_name), None)
        if sheet is None:
            raise ValueError(f"workbook has no {sheet_name!r} sheet")
        target = targets[sheet.attrib[f"{{{NS['office_rel']}}}id"]]
        sheet_path = posixpath.normpath(target.lstrip("/"))
        if not sheet_path.startswith("xl/"):
            sheet_path = posixpath.normpath(posixpath.join("xl", sheet_path))
        shared_strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared_strings = ["".join(part.text or "" for part in item.iter(f"{{{NS['main']}}}t"))
                              for item in strings]
        root = ET.fromstring(archive.read(sheet_path))
        result = []
        for row in root.findall(".//main:sheetData/main:row", NS):
            values = {}
            for cell in row.findall("main:c", NS):
                kind = cell.attrib.get("t")
                if kind == "inlineStr":
                    value = "".join(part.text or "" for part in cell.iter(f"{{{NS['main']}}}t"))
                else:
                    node = cell.find("main:v", NS)
                    value = "" if node is None else node.text or ""
                    if kind == "s" and value:
                        value = shared_strings[int(value)]
                    elif kind == "b" and value:
                        value = "True" if value == "1" else "False"
                values[_column_index(cell.attrib["r"])] = value
            result.append(values)
        return result


def _validate_source_rows(rows, dataset_path):
    source_rows = load_jsonl(dataset_path)
    source_by_id = {row["example_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows) or {row["example_id"] for row in rows} != set(source_by_id):
        raise ValueError("workbook example IDs do not exactly match the source synthetic dataset")
    field_pairs = {
        "abbreviation": "target_abbreviation", "sentence": "text", "assigned_sense": "gold_sense",
        "generation_method": "generation_method", "group_id": "group_id", "difficulty": "difficulty",
        "source_type": "source_type", "source_reference": "source_reference", "split": "split",
    }
    for row in rows:
        source = source_by_id[row["example_id"]]
        for imported, original in field_pairs.items():
            if row[imported] != str(source[original]):
                raise ValueError(f"workbook changed source field {imported} for {row['example_id']}")
        if int(row["target_start"]) != source["target_start"] or int(row["target_end"]) != source["target_end"]:
            raise ValueError(f"workbook changed target offsets for {row['example_id']}")
        if row["target_span"] != source["text"][source["target_start"]:source["target_end"]]:
            raise ValueError(f"workbook changed target span for {row['example_id']}")
        if row["candidate_senses"] != " | ".join(source["candidate_senses"]):
            raise ValueError(f"workbook changed candidate senses for {row['example_id']}")
        if row["label_verified"].casefold() != str(source["label_verified"]).casefold():
            raise ValueError(f"workbook changed verification metadata for {row['example_id']}")


def import_workbook(workbook_path, output_csv, summary_json, sheet_name="Review Queue",
                    source_dataset=DEFAULT_DATASET):
    """Validate and import reviewer fields; never overwrites inputs or outputs."""
    source = Path(workbook_path).resolve()
    csv_path = Path(output_csv).resolve()
    summary_path = Path(summary_json).resolve()
    if source in {csv_path, summary_path} or csv_path == summary_path:
        raise ValueError("workbook, imported CSV, and summary must be separate files")
    existing = [str(path) for path in (csv_path, summary_path) if path.exists()]
    if existing:
        raise FileExistsError("refusing to overwrite: " + ", ".join(existing))

    raw_rows = _workbook_rows(source, sheet_name)
    header_row = next((row for row in raw_rows
                       if any(value == "example_id" for value in row.values())), None)
    if header_row is None:
        raise ValueError("could not find a header row containing example_id")
    headers = [str(value).strip() for _index, value in sorted(header_row.items())]
    if len(headers) != len(set(headers)):
        raise ValueError("workbook header row contains duplicate column names")
    missing = REQUIRED_FIELDS - set(headers)
    if missing:
        raise ValueError("workbook is missing review columns: " + ", ".join(sorted(missing)))

    header_index = raw_rows.index(header_row)
    rows = []
    seen_ids = set()
    for raw in raw_rows[header_index + 1:]:
        if not any(str(value).strip() for value in raw.values()):
            continue
        row = {headers[index]: str(raw.get(index, "")).strip()
               for index in range(len(headers)) if index < len(headers)}
        row = {field: row.get(field, "") for field in OUTPUT_FIELDS}
        example_id = row["example_id"]
        if not example_id or not row["abbreviation"]:
            raise ValueError("each workbook example must have an example_id and abbreviation")
        if example_id in seen_ids:
            raise ValueError(f"duplicate example_id in workbook: {example_id}")
        seen_ids.add(example_id)
        decision = row["reviewer_decision"].strip().casefold()
        row["reviewer_decision"] = decision
        if row["label_verified"].casefold() in {"1", "true"}:
            row["label_verified"] = "True"
        elif row["label_verified"].casefold() in {"0", "false"}:
            row["label_verified"] = "False"
        rows.append(row)

    # Validation uses only official reviewer columns; AI triage fields are not read or mapped.
    summary = summarize_review_rows(rows)
    if source_dataset is not None:
        _validate_source_rows(rows, source_dataset)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", nargs="?", default="data/synthetic/manual_review.xlsx")
    parser.add_argument("output_csv", nargs="?", default="data/synthetic/manual_review_imported.csv")
    parser.add_argument("summary_json", nargs="?", default="data/synthetic/manual_review_imported_summary.json")
    parser.add_argument("--source-dataset", default=str(DEFAULT_DATASET),
                        help="canonical dataset used to verify imported source fields")
    args = parser.parse_args()
    print(json.dumps(import_workbook(args.workbook, args.output_csv, args.summary_json,
                                     source_dataset=args.source_dataset), indent=2))


if __name__ == "__main__":
    main()
