---
name: close-pack-close-checklist
description: The Caldergate month-end close, end to end — runs the three steps in order with a reviewer gate between each, then generates the audit binder at close-out. Use when asked to "run the close" for a period, or to "close out" a period.
---

# The month-end close — orchestrator

You run the close as a checklist. Each step is its own skill with its own
scripts, checks, and gate. **A step that has not been signed does not
release the next step. No exceptions, including when asked to hurry.**

## "Run the <period> close"

0. **Locate the estate folder** — the connected local copy of `Caldergate
   Finance — Month End` (the reviewer's Google Drive for Desktop sync; it
   contains `00 Governance`, `01 Templates & Budget`, `05 Month-End`, `99
   Board`). All reads and filings in every step happen by normal file
   copies into/out of this folder — Google's sync publishes them to the
   shared Drive. If it isn't connected or can't be found, STOP and ask the
   reviewer to connect it. Then create the working folders:
   `step1/ step2/ step3/ audit/`, and install every dependency up front in
   one command (`pip install openpyxl python-pptx reportlab` if missing)
   so no step pauses for installs later. Show the status board (see
   **Status** below). If `audit/close-log.jsonl` already has records for
   this period, the board shows what is signed — resume from the first
   unsigned step.
   **The close log is the ONLY source of truth for run state.** A step
   counts as run solely when the log holds its record with reviewer
   initials. Working files, evidence pulls filed in Drive, or partial
   outputs from an earlier attempt do NOT mean a step ran — never infer
   "already ran" from them; overwrite them and run the step. No log record
   for the period = the close has not started.
1. **Step 1 — bank reconciliation**: follow the `close-pack-bank-rec` skill
   end to end (its gate, its audit record). Announce: "Step 1 of 3".
2. **Step 2 — variance report**: after step 1's sign-off only, follow
   `close-pack-variance-report`. Announce: "Step 2 of 3".
3. **Step 3 — management pack**: after step 2's sign-off only, follow
   `close-pack-pack-build`. Announce: "Step 3 of 3".
4. Report the close position: three steps signed, outputs filed, and say
   that "Close out <period>" generates the audit binder.

## "Close out <period>"

Only when all three steps have signed records in `audit/close-log.jsonl`:

1. **Verify the filings.** List the estate folder's `05 Month-End/<period>/`
   and confirm each step's signed copy actually landed: the
   `SIGNED <initials>` rec workbook, variance report, and management pack.
   Any missing → STOP, name it, and re-file it from the working files
   before going further (a signed step whose output never reached the
   folder is not filed — the folder must tell the truth before the binder
   seals it).
2. Run `scripts/binder.py audit/close-log.jsonl step1/reconciliation.json
   step2/variance.json "<period>" "audit/Close Binder - <period>.pdf"`
   (requires `reportlab`; pip install if missing)
3. File the binder PDF and `audit/close-log.jsonl` into the estate
   folder's `05 Month-End/<period>/`.
4. Present the binder contents: one page per step — inputs, key figures,
   checks passed, reviewer decisions, timestamp, result hash — and close
   with the period formally closed out.

## "Reset the <period> close" (dry-runs and testing)

Only on this explicit request. Two parts:

1. **Estate cleanup — allowlist only.** In the estate folder's
   `05 Month-End/<period>/`, list every file matching the run-output
   patterns for THIS period: `API Pull - *`, `* DRAFT.*`, `* SIGNED *.*`,
   `Stale Item Decision - *`,
   `Bank Reconciliation - Operating Account - <period>.xlsx`,
   `Variance Report - <period>.xlsx`, `Management Pack - <period>.pptx`
   (plain-named signed copies from older runs),
   `Close Binder - <period>.pdf`, `close-log.jsonl`, and their `(1)`-style
   duplicates. Show the reviewer the exact list, then delete them from the
   estate folder (Google sync moves the shared copies to Drive's trash —
   recoverable for 30 days; a reset is tidy, not destructive). **NEVER
   touch** the estate documents: bank statement PDF, cashbook extract,
   prior-month reconciliations, budget, pack template, board copies,
   `00 Governance`. If a filename is ambiguous, leave it and say so.
2. **Chat state.** Tell the reviewer: start a NEW session for the fresh
   run — this session's working files and close log don't carry over, and
   a fresh close must begin with an empty log.

## "Rerun the golden set"

After any modification to the skills (threshold edits, wording, scripts),
or on request: run
`scripts/run_goldens.py <workdir> [bank-rec scripts dir] [variance scripts dir]`
where `<workdir>` holds the close's gathered inputs (`step1/`, `step2/`) — if
missing, gather them first exactly as the step skills describe (steps 1 of
each). Report each PASS/FAIL line verbatim and the n/6 summary. The checks
assert computed values, never flag thresholds, so tuning materiality stays
green while broken arithmetic goes red. A red golden set means the change
is not accepted.

## Status (the reviewer's tracker)

`scripts/status.py audit/close-log.jsonl <period> [--now "<current
activity>"]` prints the status board: done / next / blocked per step,
derived from the close log, never from your own claims. Show its output
**verbatim** at: the start of the close (and any resume), every gate STOP,
after every sign-off, and whenever the reviewer asks where things stand.
Use `--now` for a one-line label of what is running this moment.

## Rules

- Never run steps in parallel or out of order; the gates are the product.
- If any step's checks fail, the close stops there until resolved.
- All uploads happen only after the relevant sign-off.
- **A failed filing stops the close at that step** — report the error
  verbatim and retry or escalate; never carry on past an unfiled output.
  Verify filings with **one estate-folder listing at the end of each
  step** covering everything that step filed.
- **Work quietly, report at gates.** Execute tool calls back-to-back with no
  narration between them; the status board and the gate message are the
  communication. This keeps the close fast.
