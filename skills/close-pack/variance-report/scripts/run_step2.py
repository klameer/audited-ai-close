"""Run the whole step-2 pipeline in one invocation (speed: one call, not three).

Usage: run_step2.py <tb.json> <budget.xlsx> <period> <flag_threshold_k> <outdir>
  e.g. run_step2.py step2/tb.json step2/budget.xlsx May-26 100 step2

variance -> checks -> DRAFT copy. Each stage's output is echoed verbatim; any
failing stage stops the pipeline with exit 1. Writes:
  <outdir>/variance.json, "<outdir>/Variance Report - <period>.xlsx",
  "<outdir>/Variance Report - <period> DRAFT.xlsx"
"""
import shutil
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
        print(f"STEP 2 STOPPED at {script} (exit {result.returncode}) - do not present results")
        sys.exit(1)


def main(tb, budget, period, threshold_k, outdir) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    report = out / f"Variance Report - {period}.xlsx"
    draft = out / f"Variance Report - {period} DRAFT.xlsx"

    run("variance.py", tb, budget, period, threshold_k, out)
    run("checks.py", tb, budget, period, out)
    shutil.copyfile(report, draft)
    print(f"step 2 pipeline complete: {out / 'variance.json'} + {draft}")


if __name__ == "__main__":
    main(*sys.argv[1:6])
