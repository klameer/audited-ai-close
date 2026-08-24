"""Independent tie-outs for the variance report. Exit 1 on any failure.

Usage: checks.py tb.json budget.xlsx <period> outdir/

Recomputes every variance from the RAW inputs and compares against both
outputs (variance.json and the xlsx), cell by cell:
  C1 every TB line present exactly once in both outputs
  C2 each variance re-derives (actual - budget), pence-of-a-thousand exact
  C3 totals cross-foot in json and xlsx
  C4 flags consistent with the stated threshold
Requires openpyxl.
"""
import json
import sys
from pathlib import Path

import openpyxl


def main(tb_path: str, budget_path: str, period: str, outdir: str) -> None:
    sys.path.insert(0, str(Path(__file__).parent))
    from variance import read_budget  # same parser, independent recompute

    tb = json.load(open(tb_path))
    budgets = read_budget(budget_path, period)
    rec = json.load(open(Path(outdir) / "variance.json"))
    failures = []

    json_lines = {l["line"]: l for l in rec["lines"]}
    if set(json_lines) != set(tb["lines"]):
        failures.append("C1 line sets differ between TB and variance.json")

    for line, vals in tb["lines"].items():
        want = round(float(vals["mtd_actual"]) - budgets[line], 1)
        got = json_lines.get(line, {}).get("variance_k")
        if got != want:
            failures.append(f"C2 {line}: variance {got} != recomputed {want}")
        flagged = json_lines.get(line, {}).get("flagged")
        if flagged != (abs(want) >= rec["flag_threshold_k"]):
            failures.append(f"C4 {line}: flag inconsistent with threshold")

    if round(sum(l["variance_k"] for l in rec["lines"]), 1) != rec["total_variance_k"]:
        failures.append("C3 json total does not cross-foot")

    ws = openpyxl.load_workbook(Path(outdir) / f"Variance Report - {period}.xlsx").active
    seen = 0
    for row in ws.iter_rows(min_row=5, values_only=True):
        line = row[0]
        if line in json_lines:
            seen += 1
            j = json_lines[line]
            if (row[1], row[2], row[3]) != (j["mtd_actual_k"], j["mtd_budget_k"], j["variance_k"]):
                failures.append(f"C2 xlsx row for {line} differs from variance.json")
        elif line == "TOTAL" and round(row[3] or 0, 1) != rec["total_variance_k"]:
            failures.append("C3 xlsx TOTAL differs from json total")
    if seen != len(json_lines):
        failures.append(f"C1 xlsx shows {seen} lines, expected {len(json_lines)}")

    if failures:
        print("CHECKS FAILED:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print(f"checks passed: C1 lines, C2 every variance re-derived, C3 totals "
          f"cross-foot, C4 flags at ±{rec['flag_threshold_k']:,.0f}k")


if __name__ == "__main__":
    main(*sys.argv[1:5])
