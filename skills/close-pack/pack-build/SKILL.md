---
name: close-pack-pack-build
description: Step 3 of the Caldergate month-end close — fill the management pack template from the reviewer-signed outputs of steps 1 and 2, verify every figure, and stop at the reviewer gate. Use when running the close or when asked to build the monthly pack.
---

# Management pack — Step 3 of the close

You orchestrate; **the script fills every figure from the signed step
outputs. Never type a number into the pack yourself.** Requires
`python-pptx` (pip install if missing).

## Preconditions

Steps 1 and 2 are signed (records in `audit/close-log.jsonl`). If either is
missing, STOP: the pack is built from signed figures only.

## Steps

Execute 1–4 back-to-back with **no narration between tool calls** — the
gate message is the report.

1. Copy `Management Pack Template.pptx` from the estate folder's
   `01 Templates & Budget/` to `step3/template.pptx`.
2. Write the pack commentary to `step3/commentary.txt` — the flagged-line
   paragraphs from step 2 (already reviewer-signed wording if available),
   plus one line on the bank position. Every number must carry its source
   document citation in the text.
3. Run the whole pipeline in ONE call —
   `scripts/run_step3.py step3/template.pptx step1/reconciliation.json
   step2/variance.json step3/commentary.txt audit/close-log.jsonl May-26
   step3`
   — build → checks → DRAFT copy. If it stops (a hard check failure),
   STOP and report its output verbatim. If the output lists numbers under
   "REVIEWER MUST VERIFY", carry that list into the gate message: those are
   commentary citations the reviewer confirms against the named documents.
4. **File `step3/Management Pack - May-26 DRAFT.pptx` into the estate
   folder's `05 Month-End/May-26/`** (the folder is the review surface;
   DRAFT mark = unsigned) and point the reviewer at it there — the
   reviewer opens and signs the document, not a chat message — then
   present: slide summary, where each figure came from, and the
   reviewer-must-verify list (if any).
5. **GATE — say exactly this and stop:**
   > Reviewer sign-off required. The pack is not filed until a named
   > reviewer signs. Reply with your initials to sign off step 3, or raise
   > a query.
6. Only after sign-off (back-to-back, one report at the end): write the
   signed filing copy — the DRAFT status line on the title slide becomes
   the reviewer's sign-off (nothing signed carries a DRAFT mark, inside
   the file or on it) —
   `scripts/sign_pack.py "step3/Management Pack - May-26.pptx" "<initials>" "step3/Management Pack - May-26 SIGNED <initials>.pptx"`
   — file it into the estate folder's `05 Month-End/May-26/`, then append
   the audit record **on the signed copy** (its sha256 seals the file that
   was filed) —
   `scripts/audit_record.py step3 "step3/Management Pack - May-26 SIGNED <initials>.pptx" "<initials>" audit/close-log.jsonl`
   — then **one listing** of the estate folder's `05 Month-End/May-26/`
   confirming this step's filings landed (DRAFT and SIGNED pack); anything
   missing stops the close here. Then hand back to the close-checklist
   skill (or finish, if run alone).

## Rules

- The pack contains no figure that isn't in a signed step output, and no
  commentary number without a document citation.
- Read-only against the ERP; writes are only the estate-folder filings
  these steps name.
- A failed filing stops the step: report the error verbatim and get the
  file into the estate folder before continuing — the step is not done,
  and the close does not advance, while the pack is unfiled. Verify with
  the single end-of-step folder listing, not a listing per file.
