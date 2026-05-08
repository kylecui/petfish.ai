#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EV_PATTERN = re.compile(r"\bEV-\d+\b")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _load_ledger_ids(ledger_path: Path) -> tuple[set[str], list[str]]:
    evidence_ids: set[str] = set()
    errors: list[str] = []

    try:
        with ledger_path.open("r", encoding="utf-8") as f:
            for line_no, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(f"Ledger line {line_no}: invalid JSON ({exc.msg})")
                    continue

                if not isinstance(entry, dict):
                    errors.append(f"Ledger line {line_no}: entry must be an object")
                    continue

                evidence_id = entry.get("evidence_id")
                if isinstance(evidence_id, str) and EV_PATTERN.fullmatch(evidence_id):
                    evidence_ids.add(evidence_id)
                else:
                    errors.append(
                        f"Ledger line {line_no}: missing/invalid evidence_id (expected EV-XXXXXX)"
                    )
    except FileNotFoundError:
        errors.append("Ledger file not found")
    except OSError as exc:
        errors.append(f"Unable to read ledger file: {exc}")

    return evidence_ids, errors


def _split_sections(markdown: str) -> list[tuple[str, str]]:
    lines = markdown.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_heading = "<document>"
    current_body: list[str] = []

    for line in lines:
        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            sections.append((current_heading, current_body))
            current_heading = heading_match.group(2).strip()
            current_body = []
        else:
            current_body.append(line)

    sections.append((current_heading, current_body))
    return [(heading, "\n".join(body).strip()) for heading, body in sections]


def _looks_like_claim(paragraph: str) -> bool:
    text = paragraph.strip()
    if not text:
        return False
    if text.startswith("-") or text.startswith("*"):
        return False
    if text.startswith("```"):
        return False
    words = re.findall(r"\b\w+\b", text)
    if len(words) < 6:
        return False
    return any(ch in text for ch in (".", "!", "?", "：", ":"))


def evaluate_report(report_path: Path, ledger_path: Path) -> tuple[dict[str, Any], int]:
    ledger_ids, ledger_errors = _load_ledger_ids(ledger_path)

    if ledger_errors:
        result = {
            "status": "fail",
            "total_evidence_refs": 0,
            "valid_refs": 0,
            "invalid_refs": [],
            "sections_without_evidence": [],
            "grade": "F",
            "notes": "; ".join(ledger_errors),
        }
        return result, 1

    try:
        report_text = report_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        result = {
            "status": "fail",
            "total_evidence_refs": 0,
            "valid_refs": 0,
            "invalid_refs": [],
            "sections_without_evidence": [],
            "grade": "F",
            "notes": "Report file not found",
        }
        return result, 1
    except OSError as exc:
        result = {
            "status": "fail",
            "total_evidence_refs": 0,
            "valid_refs": 0,
            "invalid_refs": [],
            "sections_without_evidence": [],
            "grade": "F",
            "notes": f"Unable to read report file: {exc}",
        }
        return result, 1

    refs = EV_PATTERN.findall(report_text)
    total_evidence_refs = len(refs)
    valid_ref_set = {ref for ref in refs if ref in ledger_ids}
    invalid_ref_set = {ref for ref in refs if ref not in ledger_ids}

    sections = _split_sections(report_text)
    claim_sections = 0
    referenced_claim_sections = 0
    sections_without_evidence: list[str] = []

    for heading, body in sections:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        claim_paragraphs = [p for p in paragraphs if _looks_like_claim(p)]
        if not claim_paragraphs:
            continue

        claim_sections += 1
        has_evidence_in_section = any(EV_PATTERN.search(p) for p in claim_paragraphs)
        if has_evidence_in_section:
            referenced_claim_sections += 1
        else:
            sections_without_evidence.append(heading)

    if total_evidence_refs == 0:
        grade = "F"
    else:
        coverage = (
            (referenced_claim_sections / claim_sections) if claim_sections > 0 else 0.0
        )
        if not invalid_ref_set and coverage == 1.0:
            grade = "A"
        elif not invalid_ref_set and coverage > 0.8:
            grade = "B"
        elif coverage > 0.6:
            grade = "C"
        else:
            grade = "D"

    status = "pass" if grade in {"A", "B"} else "fail"
    notes = (
        f"claim_sections={claim_sections}, referenced_claim_sections={referenced_claim_sections}, "
        f"coverage={(referenced_claim_sections / claim_sections * 100):.1f}%"
        if claim_sections > 0
        else "No detectable claim sections found; grading based on evidence references only."
    )

    result = {
        "status": status,
        "total_evidence_refs": total_evidence_refs,
        "valid_refs": sum(1 for ref in refs if ref in ledger_ids),
        "invalid_refs": sorted(invalid_ref_set),
        "sections_without_evidence": sections_without_evidence,
        "grade": grade,
        "notes": notes,
    }
    return result, (0 if status == "pass" else 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run quality gates on a research report using evidence ledger references."
    )
    parser.add_argument("--report", required=True, help="Path to report markdown file")
    parser.add_argument(
        "--ledger", required=True, help="Path to evidence-ledger.jsonl file"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result, code = evaluate_report(Path(args.report), Path(args.ledger))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
