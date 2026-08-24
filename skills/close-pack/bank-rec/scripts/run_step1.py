"""Run the whole step-1 pipeline in one invocation (speed: one call, not four).

Usage: run_step1.py <prior_rec.xlsx> <statement.json> <cashbook.json> <outdir> <period> "<period_label>"
  e.g. run_step1.py "Bank Reconciliation - Operating Account - Apr-26.xlsx" \
       step1/statement.json step1/cashbook.json step1 May-26 "31 May 2026"

parse_rec -> reconcile -> checks -> write_rec (DRAFT). Each stage's output is
echoed verbatim; any failing stage stops the pipeline with exit 1 (checks
failures included — never present results past a failed check). Writes:
  <outdir>/opening_rec.json, <outdir>/reconciliation.json,
  "<outdir>/Bank Reconciliation - Operating Account - <period> DRAFT.xlsx"
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str, *args) -> None:
    result = subprocess.run([sys.executable, str(HERE / script), *map(str, args)],
                            capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="", file=sys.stderr)
        print(f"STEP 1 STOPPED at {script} (exit {result.returncode}) - do not present results")
        sys.exit(1)


def main(prior_rec, statement, cashbook, outdir, period, period_label) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    opening = out / "opening_rec.json"
    rec = out / "reconciliation.json"
    draft = out / f"Bank Reconciliation - Operating Account - {period} DRAFT.xlsx"

    run("parse_rec.py", prior_rec, opening)
    run("reconcile.py", statement, cashbook, opening, rec)
    run("checks.py", statement, cashbook, opening, rec)
    run("write_rec.py", rec, period_label, "DRAFT - pending sign-off", draft)
    print(f"step 1 pipeline complete: {rec} + {draft}")


if __name__ == "__main__":
    main(*sys.argv[1:7])
