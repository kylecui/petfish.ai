#!/usr/bin/env python3
"""
PEtFiSh Evaluation Framework — Shared Eval Harness

Loads a JSONL dataset, invokes a module's classify() function for each entry,
computes precision, recall, F1, and accuracy, then outputs a pass/fail table
plus summary statistics.

Usage:
    python run_eval.py --dataset ../datasets/gateway-topic-drift.jsonl --module gateway
    python run_eval.py --dataset ../datasets/skill-sense.jsonl --module skill_sense
    python run_eval.py --dataset ../datasets/cost-routing.jsonl --module cost_routing
    python run_eval.py --dataset ../datasets/failure-signal.jsonl --module failure_signal

Design:
    - stdlib only (no external dependencies)
    - Module imports are dynamic: `from modules.<name>_eval import classify`
    - Each module must expose: classify(entry: dict) -> dict
    - The harness auto-detects whether the task is multi-class or binary
      based on the presence of `expected_detect` in the dataset.
"""

import argparse
import json
import importlib
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_binary_metrics(
    y_true: list[bool], y_pred: list[bool], labels: list[str] | None = None
) -> dict[str, Any]:
    """Compute precision, recall, F1, accuracy for binary classification."""
    tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
    fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)
    tn = sum(1 for t, p in zip(y_true, y_pred) if not t and not p)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0

    per_class = {}
    if labels:
        pos_label = labels[0] if labels else "positive"
        neg_label = labels[1] if len(labels) > 1 else "negative"
        per_class[pos_label] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(y_true)}
        neg_precision = tn / (tn + fn) if (tn + fn) > 0 else 0.0
        neg_recall = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        neg_f1 = 2 * neg_precision * neg_recall / (neg_precision + neg_recall) if (neg_precision + neg_recall) > 0 else 0.0
        per_class[neg_label] = {"precision": neg_precision, "recall": neg_recall, "f1": neg_f1, "support": sum(1 for t in y_true if not t)}

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "per_class": per_class,
    }


def compute_multiclass_metrics(
    y_true: list[str], y_pred: list[str]
) -> dict[str, Any]:
    """Compute per-class + macro/micro/weighted averages for multiclass."""
    classes = sorted(set(y_true) | set(y_pred))
    per_class: dict[str, dict] = {}

    for cls in classes:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p == cls)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != cls and p == cls)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p != cls)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        per_class[cls] = {
            "precision": precision, "recall": recall, "f1": f1,
            "support": sum(1 for t in y_true if t == cls),
        }

    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true) if y_true else 0.0

    # macro average
    macro_p = sum(v["precision"] for v in per_class.values()) / len(per_class) if per_class else 0.0
    macro_r = sum(v["recall"] for v in per_class.values()) / len(per_class) if per_class else 0.0
    macro_f1 = 2 * macro_p * macro_r / (macro_p + macro_r) if (macro_p + macro_r) > 0 else 0.0

    # weighted average
    total = len(y_true)
    weighted_p = sum(v["precision"] * v["support"] for v in per_class.values()) / total if total else 0.0
    weighted_r = sum(v["recall"] * v["support"] for v in per_class.values()) / total if total else 0.0
    weighted_f1 = 2 * weighted_p * weighted_r / (weighted_p + weighted_r) if (weighted_p + weighted_r) > 0 else 0.0

    return {
        "accuracy": accuracy,
        "macro_avg": {"precision": macro_p, "recall": macro_r, "f1": macro_f1},
        "weighted_avg": {"precision": weighted_p, "recall": weighted_r, "f1": weighted_f1},
        "per_class": per_class,
    }


# ---------------------------------------------------------------------------
# Table formatting
# ---------------------------------------------------------------------------

def _col_widths(rows: list[list[str]], headers: list[str]) -> list[int]:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    return widths


def _pad(row: list[str], widths: list[int]) -> str:
    return " | ".join(c.ljust(w) for c, w in zip(row, widths))


def format_summary_binary(metrics: dict, labels: list[str]) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("EVALUATION SUMMARY (Binary)")
    lines.append("=" * 60)
    pos_label = labels[0] if labels else "positive"
    lines.append(f"  Accuracy:  {metrics['accuracy']:.4f}")
    lines.append(f"  Precision: {metrics['precision']:.4f}  (class: {pos_label})")
    lines.append(f"  Recall:    {metrics['recall']:.4f}  (class: {pos_label})")
    lines.append(f"  F1 Score:  {metrics['f1']:.4f}")
    lines.append(f"  TP={metrics['tp']}  FP={metrics['fp']}  FN={metrics['fn']}  TN={metrics['tn']}")
    lines.append("")
    lines.append("Per-class:")
    headers = ["Class", "Precision", "Recall", "F1", "Support"]
    rows = []
    for cls, m in metrics.get("per_class", {}).items():
        rows.append([cls, f"{m['precision']:.4f}", f"{m['recall']:.4f}", f"{m['f1']:.4f}", str(m['support'])])
    widths = _col_widths(rows, headers)
    lines.append(_pad(headers, widths))
    lines.append("-+-".join("-" * w for w in widths))
    for row in rows:
        lines.append(_pad(row, widths))
    return "\n".join(lines)


def format_summary_multiclass(metrics: dict) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("EVALUATION SUMMARY (Multi-class)")
    lines.append("=" * 60)
    lines.append(f"  Accuracy:      {metrics['accuracy']:.4f}")
    lines.append(f"  Macro Avg F1:  {metrics['macro_avg']['f1']:.4f}")
    lines.append(f"  Weighted Avg F1: {metrics['weighted_avg']['f1']:.4f}")
    lines.append("")
    lines.append("Per-class:")
    headers = ["Class", "Precision", "Recall", "F1", "Support"]
    rows = []
    for cls, m in sorted(metrics.get("per_class", {}).items()):
        rows.append([cls, f"{m['precision']:.4f}", f"{m['recall']:.4f}", f"{m['f1']:.4f}", str(m['support'])])
    widths = _col_widths(rows, headers)
    lines.append(_pad(headers, widths))
    lines.append("-+-".join("-" * w for w in widths))
    for row in rows:
        lines.append(_pad(row, widths))
    return "\n".join(lines)


def format_entry_table(entries: list[dict], is_binary: bool) -> str:
    """Format per-entry pass/fail table."""
    if is_binary:
        headers = ["#", "User Message", "Expected", "Predicted", "Result"]
    else:
        headers = ["#", "User Message", "Expected", "Predicted", "Result"]

    rows = []
    for i, e in enumerate(entries):
        msg = e.get("user_message", e.get("previous_assistant_output", ""))
        # Truncate long messages
        display = msg[:60] + "..." if len(msg) > 60 else msg
        expected = str(e.get("_expected", ""))
        predicted = str(e.get("_predicted", ""))
        result = "PASS" if e.get("_correct", False) else "FAIL"
        rows.append([str(i + 1), display, expected, predicted, result])

    widths = _col_widths(rows, headers)
    lines = []
    lines.append("-" * 100)
    lines.append("PER-ENTRY RESULTS")
    lines.append("-" * 100)
    lines.append(_pad(headers, widths))
    lines.append("-+-".join("-" * w for w in widths))
    for row in rows:
        lines.append(_pad(row, widths))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def load_dataset(path: Path) -> list[dict]:
    """Load a JSONL dataset file."""
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            entries.append(json.loads(line))
    return entries


def resolve_module(module_name: str):
    """Import a module from the modules/ package.

    Runs from benchmarks/scripts/ — expects modules/<name>_eval.py.
    """
    try:
        mod = importlib.import_module(f"modules.{module_name}_eval")
        return mod
    except ImportError as e:
        print(f"ERROR: Cannot import modules.{module_name}_eval: {e}", file=sys.stderr)
        print("Make sure modules/ is in the Python path and contains <name>_eval.py", file=sys.stderr)
        sys.exit(1)


def detect_task_type(entries: list[dict]) -> tuple[bool, str, str]:
    """Detect whether this is binary or multi-class.

    Returns (is_binary, true_key, pred_key).
    """
    if not entries:
        return True, "expected_detect", "predicted_detect"

    first = entries[0]
    if "expected_detect" in first:
        # Binary: expected_detect is bool
        return True, "expected_detect", "predicted_detect"
    elif "expected_signal" in first:
        # Binary with named signal
        return True, "expected_detect", "predicted_detect"
    elif "expected_relation" in first:
        return False, "expected_relation", "predicted_relation"
    elif "expected_skill" in first:
        # Mixed: skill names (multi-class for detection) + null for no-skill
        return False, "expected_skill", "predicted_skill"
    elif "expected_tier" in first:
        return False, "expected_tier", "predicted_tier"
    else:
        return False, "expected", "predicted"


def main():
    parser = argparse.ArgumentParser(
        description="PEtFiSh Eval Harness — run benchmark datasets against eval modules"
    )
    parser.add_argument(
        "--dataset", required=True, type=str, help="Path to JSONL dataset file"
    )
    parser.add_argument(
        "--module", required=True, type=str,
        help="Module name (e.g. gateway, skill_sense, cost_routing, failure_signal)"
    )
    parser.add_argument(
        "--no-table", action="store_true", help="Skip per-entry pass/fail table"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output metrics as JSON"
    )
    args = parser.parse_args()

    # Resolve dataset path
    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        # Relative to cwd
        dataset_path = Path.cwd() / dataset_path
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found: {dataset_path}", file=sys.stderr)
        sys.exit(1)

    # Load dataset
    entries = load_dataset(dataset_path)
    if not entries:
        print("ERROR: Empty dataset", file=sys.stderr)
        sys.exit(1)

    # Import module
    mod = resolve_module(args.module)
    classify = getattr(mod, "classify", None)
    if classify is None:
        print(f"ERROR: Module modules.{args.module}_eval must expose classify(entry) -> dict", file=sys.stderr)
        sys.exit(1)

    # Detect task type
    is_binary, true_key, pred_key = detect_task_type(entries)

    # Run classification
    y_true: list[Any] = []
    y_pred: list[Any] = []

    for entry in entries:
        result = classify(entry)

        if is_binary:
            expected = entry.get(true_key)
            predicted = result.get(pred_key)
            y_true.append(bool(expected))
            y_pred.append(bool(predicted))
        else:
            expected = entry.get(true_key)
            predicted = result.get(pred_key)
            y_true.append(str(expected) if expected is not None else "none")
            y_pred.append(str(predicted) if predicted is not None else "none")

        entry["_expected"] = expected
        entry["_predicted"] = predicted
        entry["_correct"] = (bool(expected) == bool(predicted)) if is_binary else (str(expected or "none") == str(predicted or "none"))

    # Compute metrics
    if is_binary:
        labels = ["positive", "negative"]
        if "expected_skill" in entries[0]:
            labels = ["detected", "not_detected"]
        elif "expected_signal" in entries[0]:
            labels = ["signal_detected", "no_signal"]
        metrics = compute_binary_metrics(y_true, y_pred, labels)
        summary = format_summary_binary(metrics, labels)
    else:
        metrics = compute_multiclass_metrics(y_true, y_pred)
        summary = format_summary_multiclass(metrics)

    # Output
    if args.json:
        output = {
            "dataset": str(dataset_path),
            "module": args.module,
            "task_type": "binary" if is_binary else "multiclass",
            "num_entries": len(entries),
            "metrics": metrics,
            "entries": [
                {
                    "message": e.get("user_message", e.get("previous_assistant_output", "")),
                    "expected": e.get("_expected"),
                    "predicted": e.get("_predicted"),
                    "correct": e.get("_correct"),
                }
                for e in entries
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"\nDataset: {dataset_path}")
    print(f"Module:  {args.module}")
    print(f"Entries: {len(entries)}")
    print(f"Type:    {'binary' if is_binary else 'multi-class'}")

    if not args.no_table:
        print(format_entry_table(entries, is_binary))

    print()
    print(summary)

    # Exit code: 0 if all pass, 1 otherwise
    failures = sum(1 for e in entries if not e.get("_correct", False))
    if failures > 0:
        print(f"\n{failures}/{len(entries)} entries FAILED.")
        sys.exit(1)
    else:
        print(f"\nAll {len(entries)} entries PASSED.")
        sys.exit(0)


if __name__ == "__main__":
    main()
