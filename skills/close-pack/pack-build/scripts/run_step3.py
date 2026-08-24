"""Run the whole step-3 pipeline in one invocation (speed: one call, not three).

Usage: run_step3.py <template.pptx> <rec.json> <var.json> <commentary.txt> <close-log.jsonl> <period> <outdir>
  e.g. run_step3.py step3/template.pptx step1/reconciliation.json \
       step2/variance.json step3/commentary.txt audit/close-log.jsonl May-26 step3

build_pack -> checks -> DRAFT copy. Each stage's output is echoed verbatim
(including any REVIEWER MUST VERIFY list — carry it into the gate message);
hard check failures stop the pipeline with exit 1. Writes:
  "<outdir>/Management Pack - <period>.pptx",
  "<outdir>/Management Pack - <period> DRAFT.pptx"
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
        print(f"STEP 3 STOPPED at {script} (exit {result.returncode}) - do not present results")
        sys.exit(1)


def main(template, rec, var, commentary, log, period, outdir) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    pack = out / f"Management Pack - {period}.pptx"
    draft = out / f"Management Pack - {period} DRAFT.pptx"

    run("build_pack.py", template, rec, var, commentary, log, period, pack)
    run("checks.py", pack, rec, var, commentary)
    shutil.copyfile(pack, draft)
    print(f"step 3 pipeline complete: {pack} + {draft}")


if __name__ == "__main__":
    main(*sys.argv[1:8])
