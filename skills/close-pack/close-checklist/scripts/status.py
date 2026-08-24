"""Print the close status checklist, derived from the close log — never claimed.

Usage: status.py <close-log.jsonl> <period> [--now "<what is happening right now>"]

A step counts as DONE solely when its signed record is in the log (same rule
as the checklist skill). The optional --now line is a label supplied by the
run for what it is doing this moment; everything else is script-derived.
Missing or empty log = close not started. Always exits 0.
"""
import json
import sys
from pathlib import Path

STEPS = [("step1", "Step 1  Bank reconciliation"),
         ("step2", "Step 2  Variance report"),
         ("step3", "Step 3  Management pack")]


def main(argv: list[str]) -> None:
    log_path, period = argv[0], argv[1]
    now = argv[3] if len(argv) > 3 and argv[2] == "--now" else None

    signed: dict[str, dict] = {}
    p = Path(log_path)
    if p.exists():
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                signed[r["step"]] = r

    print(f"CLOSE STATUS - {period}")
    next_seen = False
    for i, (step_id, label) in enumerate(STEPS):
        r = signed.get(step_id)
        if r:
            when = r["signed_at_utc"][:16].replace("T", " ")
            print(f"[x] {label:<28} signed {r['reviewer']} {when}Z")
        elif not next_seen:
            print(f"[ ] {label:<28} <- next")
            next_seen = True
        else:
            prev = STEPS[i - 1][1].split("  ")[0]
            print(f"[ ] {label:<28} blocked (needs {prev} signed)")
    if len(signed) == len(STEPS):
        print(f'[ ] Close-out (audit binder)     ready - say "Close out {period}"')
    else:
        print("[ ] Close-out (audit binder)     blocked (needs all three steps signed)")
    if now:
        print(f"now: {now}")
    print("derived from the close log - a step is done only when its signed record is in the log")


if __name__ == "__main__":
    main(sys.argv[1:])
