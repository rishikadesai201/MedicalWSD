import csv
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import pytest

from medsense.data.import_review_workbook import OUTPUT_FIELDS, import_workbook


WORKBOOK_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def cell_ref(index, row):
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row}"


def write_workbook(path, rows):
    headers = OUTPUT_FIELDS + ["AI_triage_suggestion", "AI_triage_reason"]
    all_rows = [headers] + rows
    sheet = ET.Element(f"{{{WORKBOOK_NS}}}worksheet")
    sheet_data = ET.SubElement(sheet, f"{{{WORKBOOK_NS}}}sheetData")
    for row_number, values in enumerate(all_rows, 1):
        row = ET.SubElement(sheet_data, f"{{{WORKBOOK_NS}}}row", r=str(row_number))
        for col_index, header in enumerate(headers, 1):
            value = values.get(header, "") if row_number > 1 else header
            cell = ET.SubElement(row, f"{{{WORKBOOK_NS}}}c", r=cell_ref(col_index, row_number), t="inlineStr")
            inline = ET.SubElement(cell, f"{{{WORKBOOK_NS}}}is")
            ET.SubElement(inline, f"{{{WORKBOOK_NS}}}t").text = str(value)
    workbook = (f'<workbook xmlns="{WORKBOOK_NS}" xmlns:r="{OFFICE_REL_NS}">'
                '<sheets><sheet name="Review Queue" sheetId="1" r:id="rId1"/></sheets></workbook>')
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels",
                         f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                         '<Relationship Id="rId1" Target="worksheets/sheet1.xml" '
                         'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>'
                         '</Relationships>')
        archive.writestr("xl/worksheets/sheet1.xml", ET.tostring(sheet, encoding="unicode"))


def row(example_id, abbr, decision="", revised="", comments="", ai="reject"):
    return {
        "example_id": example_id, "abbreviation": abbr, "sentence": f"Example {example_id}",
        "target_span": abbr, "target_start": "0", "target_end": str(len(abbr)),
        "assigned_sense": "Original sense", "candidate_senses": "Original sense | Other sense",
        "review_flags": "", "generation_method": "review_fixture", "group_id": f"g-{example_id}",
        "difficulty": "clear", "source_type": "synthetic", "source_reference": "fixture",
        "split": "test", "label_verified": "True", "reviewer_decision": decision,
        "reviewer_revised_sense": revised, "reviewer_comments": comments,
        "AI_triage_suggestion": ai, "AI_triage_reason": "AI suggestion only",
    }


def test_imports_valid_decisions_and_keeps_ai_triage_separate(tmp_path):
    workbook = tmp_path / "manual_review.xlsx"
    output = tmp_path / "imported.csv"
    summary_path = tmp_path / "summary.json"
    write_workbook(workbook, [
        row("a", "PE", "accept"),
        row("b", "PE", "reject"),
        row("c", "PA", "revise", "Pulmonary artery", "Reviewer correction."),
        row("d", "PA", "", ai="accept"),
    ])

    summary = import_workbook(workbook, output, summary_path, source_dataset=None)

    with output.open(encoding="utf-8-sig", newline="") as handle:
        imported = list(csv.DictReader(handle))
    assert summary["counts"] == {"pending": 1, "accepted": 1, "rejected": 1, "revised": 1}
    assert summary["by_abbreviation"]["PA"]["pending"] == 1
    assert imported[3]["reviewer_decision"] == ""
    assert "AI_triage_suggestion" not in imported[3]
    assert list(imported[0]) == OUTPUT_FIELDS
    assert json.loads(summary_path.read_text(encoding="utf-8")) == summary


@pytest.mark.parametrize("entry, message", [
    (row("bad", "PE", "maybe"), "invalid decision"),
    (row("bad", "PE", "revise", "", "comment"), "reviewer_revised_sense"),
    (row("bad", "PE", "revise", "New sense", ""), "reviewer_comments"),
])
def test_import_rejects_invalid_or_incomplete_decisions(tmp_path, entry, message):
    workbook = tmp_path / "manual_review.xlsx"
    output = tmp_path / "imported.csv"
    summary = tmp_path / "summary.json"
    write_workbook(workbook, [entry])

    with pytest.raises(ValueError, match=message):
        import_workbook(workbook, output, summary, source_dataset=None)
    assert not output.exists()
    assert not summary.exists()
