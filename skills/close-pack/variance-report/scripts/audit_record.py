"""Append one signed audit record to the close log. Stdlib only.

Usage: audit_record.py <step> <result.json> <reviewer_initials> <log.jsonl> ["<decision note>"]

The record carries a sha256 of the result file so the binder can prove the
signed figures are the filed figures. The optional note records reviewer
decisions made at the gate (e.g. "stale cheque 004182: reissue") so the
close log carries them; the binder prints it on the step page.
"""
import datetime
import hashlib
import json
import sys


def main(step: str, result_path: str, reviewer: str, log_path: str, note: str = "") -> None:
    raw = open(result_path, "rb").read()
    try:
        result = json.loads(raw)
        summary = {k: v for k, v in result.items()
                   if isinstance(v, (str, int, float)) and k != "matches"}
    except (UnicodeDecodeError, json.JSONDecodeError):
        summary = {"file": result_path.replace("\\", "/").rsplit("/", 1)[-1],
                   "bytes": len(raw)}
    record = {
        "step": step,
        "signed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "reviewer": reviewer,
        "result_file": result_path,
        "result_sha256": hashlib.sha256(raw).hexdigest(),
        "summary": summary,
    }
    if note:
        record["note"] = note
    with open(log_path, "a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"audit record appended: {step} signed by {reviewer}"
          + (f" ({note})" if note else ""))


if __name__ == "__main__":
    main(*sys.argv[1:6])
