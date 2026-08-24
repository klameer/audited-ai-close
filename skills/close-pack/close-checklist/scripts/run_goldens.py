"""Rerun the golden set: six known-answer checks, fresh from the raw inputs.

Usage: run_goldens.py <workdir> [bank_rec_scripts_dir] [variance_scripts_dir]

<workdir> must contain step1/{statement,cashbook,opening_rec}.json and
step2/{tb.json,budget.xlsx} (the close's gathered inputs). The script
re-executes reconcile.py and variance.py into <workdir>/golden/ and asserts
the six facts in golden-set.yaml. Values, not flags — so threshold edits
pass, arithmetic breakage fails. Exit 1 on any red.

Script dirs default to the close-pack sibling skills; pass them explicitly
if the skills are mounted elsewhere (e.g. /mnt/skills/...).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS_ROOT = HERE.parents[1]  # .../close-pack/


def run(script: Path, *args) -> None:
    result = subprocess.run([sys.executable, str(script), *map(str, args)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"golden pre-step failed: {script.name}\n{result.stdout}{result.stderr}")


def main(workdir: str, bank_rec_dir: str | None = None, variance_dir: str | None = None) -> None:
    wd = Path(workdir)
    golden = wd / "golden"
    golden.mkdir(exist_ok=True)
    rec_scripts = Path(bank_rec_dir) if bank_rec_dir else SKILLS_ROOT / "bank-rec" / "scripts"
    var_scripts = Path(variance_dir) if variance_dir else SKILLS_ROOT / "variance-report" / "scripts"

    run(rec_scripts / "reconcile.py", wd / "step1" / "statement.json",
        wd / "step1" / "cashbook.json", wd / "step1" / "opening_rec.json",
        golden / "reconciliation.json")
    run(var_scripts / "variance.py", wd / "step2" / "tb.json",
        wd / "step2" / "budget.xlsx", "May-26", "100", golden)

    stmt = json.load(open(wd / "step1" / "statement.json"))
    cb = json.load(open(wd / "step1" / "cashbook.json"))
    rec = json.load(open(golden / "reconciliation.json"))
    var = json.load(open(golden / "variance.json"))
    results = []

    def check(gid: str, name: str, ok: bool, detail: str):
        results.append((gid, name, ok, detail))

    bank_close = round(float(stmt["rows"][-1]["balance_gbp"]), 2)
    check("G1", "statement closes to canon", bank_close == 9882613.23, f"{bank_close:,.2f}")

    net = round(sum(e["money_in_gbp"] - e["money_out_gbp"] for e in cb["rows"]), 2)
    book = round(cb["opening_balance_gbp"] + net, 2)
    check("G2", "cashbook closes to canon",
          book == cb["closing_balance_gbp"] == 8911388.92, f"{book:,.2f}")

    rs = rec["reconciliation_statement"]
    check("G3", "rec identity to the penny",
          abs(rs["derived_book_balance_gbp"] - rs["cashbook_closing_balance_gbp"]) < 0.01,
          f"derived {rs['derived_book_balance_gbp']:,.2f}")

    stale = [i for i in rec["closing_items"] if i["stale"]]
    check("G4", "closing items and the stale cheque",
          len(rec["closing_items"]) == 6 and len(stale) == 1
          and "004182" in stale[0]["description"] and stale[0]["amount_gbp"] == -1850.00,
          f"{len(rec['closing_items'])} items, {len(stale)} stale")

    by_line = {l["line"]: l["variance_k"] for l in var["lines"]}
    check("G5", "Industrial Consumables variance",
          by_line.get("Industrial Consumables & Packaging") == 103.0,
          f"{by_line.get('Industrial Consumables & Packaging'):+,.1f}")

    check("G6", "COGS and total variance",
          by_line.get("Cost of goods sold") == 244.0 and var["total_variance_k"] == 545.0,
          f"COGS {by_line.get('Cost of goods sold'):+,.1f}, total {var['total_variance_k']:+,.1f}")

    red = [r for r in results if not r[2]]
    for gid, name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {gid}  {name}  ({detail})")
    print(f"golden set: {len(results) - len(red)}/{len(results)} green")
    if red:
        sys.exit(1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
