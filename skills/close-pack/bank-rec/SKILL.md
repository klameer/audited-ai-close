---
name: close-pack-bank-rec
description: Step 1 of the Caldergate month-end close — reconcile the bank statement to the cashbook with last month's rec brought forward, classify the timing differences, flag stale items for a human decision, and stop at the reviewer gate. Use when running the close or when asked to reconcile the bank.
---

# Bank reconciliation — Step 1 of the close

You orchestrate; **the scripts do all matching and arithmetic. Never match,
total, or classify figures yourself.** Every number you show must come from a
script's output file. Requires `openpyxl` (pip install if missing).

## Steps

Execute 1–3 back-to-back with **no narration between tool calls** — the
gate message is the report.

1. Gather the three inputs:
   - **Caldergate ERP Cloud** connector → `get_bank_statement(period="May-26")`
     saved to `step1/statement.json`, and `get_cashbook(period="May-26")` saved
     to `step1/cashbook.json`
   - **File the evidence:** copy both pulls into the estate folder's
     `05 Month-End/May-26/` as `API Pull - Bank Statement - May-26.json`
     and `API Pull - Cashbook - May-26.json`. Raw system data is filed on
     receipt, unmodified — it is evidence, not AI output, so it does not
     wait for sign-off.
   - Last month's reconciliation from the estate folder's
     `05 Month-End/Apr-26/`: `Bank Reconciliation - Operating Account -
     Apr-26*.xlsx`, preferring a `SIGNED <initials>` copy over a
     plain-named one (older months are plain-named)
2. Run the whole pipeline in ONE call —
   `scripts/run_step1.py "<downloaded prior rec>" step1/statement.json step1/cashbook.json step1 May-26 "31 May 2026"`
   — parse → reconcile → checks → DRAFT workbook. If it stops (a failed
   check included), STOP and report its output verbatim. Never present
   results from a run whose checks failed.
3. **File the DRAFT workbook into the estate folder's
   `05 Month-End/May-26/`** (clearly DRAFT-named: the folder is the review
   surface, and it must always tell the truth about status) and point the
   reviewer at it there — the reviewer opens and signs a document, not a
   chat message. Alongside it, summarise from `step1/reconciliation.json`
   only:
   - the reconciliation statement: balance per bank → unpresented payments →
     uncleared lodgements → balance per cashbook
   - any item flagged `stale`: put the script's question to the reviewer as
     a decision (e.g. a cheque unbanked for months: stop and reissue?) —
     that decision belongs to the human, not to you
4. **GATE — say exactly this and stop:**
   > The draft reconciliation is above — open it before signing. Nothing
   > is posted and nothing is filed until a named reviewer signs. Reply
   > with your initials to sign off step 1 (note any stale-item
   > decisions), or raise a query.
5. Only after sign-off (again back-to-back, one report at the end):
   - append the audit record, **carrying every stale-item decision in the
     note** so the close log holds it —
     `scripts/audit_record.py step1 step1/reconciliation.json "<initials>" audit/close-log.jsonl "stale cheque 004182: <reviewer's decision>"`
   - write the signed filing copy (reviewer-named, in the filename AND the
     status cell — nothing signed files under a name a DRAFT could carry) —
     `scripts/write_rec.py step1/reconciliation.json "31 May 2026" "<reviewer name>" "step1/Bank Reconciliation - Operating Account - May-26 SIGNED <initials>.xlsx"`
     — and file it into the estate folder's `05 Month-End/May-26/`. Same
     layout the skill reads back as next month's opening position: the
     close feeds itself.
   - **one listing** of the estate folder's `05 Month-End/May-26/`
     confirming everything this step filed is there (2 evidence pulls,
     DRAFT, SIGNED copy) — anything missing stops the close here.
   - then hand back to the close-checklist skill (or finish, if run alone).

## Rules

- Read-only: never call any tool that writes to the ERP.
- If a connector or file fetch fails, report the error and stop — never
  reconstruct data from memory.
- A failed filing stops the step: report the error verbatim and get the
  file into the estate folder before continuing — the step is not done
  while an output is unfiled. Verify with the single end-of-step folder
  listing, not a listing per file.
- Timing differences are normal close mechanics, not errors; stale items are
  findings for a human decision. Present both neutrally with the evidence.
