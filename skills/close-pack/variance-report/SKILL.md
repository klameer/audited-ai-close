---
name: close-pack-variance-report
description: Step 2 of the Caldergate month-end close — build the month's variance report against budget with a script computing every figure, narrate only the flagged lines citing authoritative sources, and stop at the reviewer gate. Use when running the close or when asked for the variance report.
---

# Variance report — Step 2 of the close

You orchestrate; **the script computes every variance. Never compute, round,
or estimate a figure yourself.** Your job is the narrative on top of the
script's numbers. Requires `openpyxl` (pip install if missing).

## Materiality

**Flag threshold: 100 (£'000, absolute MTD variance).** Pass it to the
script exactly as stated here — this line is the tunable the runbook points
at.

## Steps

Execute 1–4 back-to-back with **no narration between tool calls** — the
gate message is the report.

1. Gather the two inputs:
   - **Caldergate ERP Cloud** connector → `get_trial_balance(period="May-26")`
     saved to `step2/tb.json`; then **file the evidence**: copy the pull
     into the estate folder's `05 Month-End/May-26/` as
     `API Pull - Trial Balance - May-26.json` (raw system data files on
     receipt; only AI-produced outputs wait for sign-off)
   - copy `Budget FY26 - by line.xlsx` from the estate folder's
     `01 Templates & Budget/` to `step2/budget.xlsx` (an estate document —
     no refile)
2. Run the whole pipeline in ONE call —
   `scripts/run_step2.py step2/tb.json step2/budget.xlsx May-26 100 step2`
   (the `100` is the flag threshold from **Materiality** above) — variance →
   checks → DRAFT copy; writes `step2/variance.json`,
   `step2/Variance Report - May-26.xlsx` and the `... DRAFT.xlsx` copy. If
   it stops (a failed check included), STOP and report its output verbatim.
3. Write the commentary — one short paragraph per **flagged** line only,
   grounded in the estate documents (read them from the estate folder):
   - figures come from `step2/variance.json` verbatim
   - **Industrial Consumables & Packaging**: if flagged or discussed, you
     MUST use the reissued **April v2 FINAL** report and say why (the £620k
     cutoff restatement) — never quote April v1.
   - **Warehouse & Logistics / carriers**: the £285k Ridgway Freight April
     accrual context applies if the line is discussed.
   - No cause you cannot source: write "driver not evidenced in the pack —
     [owner] to comment" rather than inventing one.
4. **File `step2/Variance Report - May-26 DRAFT.xlsx` into the estate
   folder's `05 Month-End/May-26/`** (the folder is the review surface;
   DRAFT mark = unsigned) and point the reviewer at it there — the
   reviewer opens and signs the document, not a chat message — then
   present the variance table + your commentary, each flagged line citing
   its sources.
5. **GATE — say exactly this and stop:**
   > Reviewer sign-off required. The variance report is not filed until a
   > named reviewer signs. Reply with your initials to sign off step 2, or
   > raise a query.
6. Only after sign-off (back-to-back, one report at the end): copy the
   report to the reviewer-named filing name
   `step2/Variance Report - May-26 SIGNED <initials>.xlsx` and file it
   into the estate folder's `05 Month-End/May-26/` (nothing signed files
   under a name a DRAFT could carry), append the audit record —
   `scripts/audit_record.py step2 step2/variance.json "<initials>" audit/close-log.jsonl`
   — then **one listing** of the estate folder's `05 Month-End/May-26/`
   confirming this step's filings landed (evidence pull, DRAFT, SIGNED
   copy); anything missing stops the close here. Then hand back to the
   close-checklist skill (or finish, if run alone).

## Rules

- Read-only against the ERP; writes are only the estate-folder filings
  these steps name.
- A failed filing stops the step: report the error verbatim and get the
  file into the estate folder before continuing — the step is not done
  while an output is unfiled. Verify with the single end-of-step folder
  listing, not a listing per file.
- Commentary states facts with sources or names the open question — never a
  guessed cause.
