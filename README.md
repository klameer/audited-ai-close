# The Audited AI Close

**Review the project:** [case study, implementation and control boundaries](CASE_STUDY.md) ·
[finance-team runbook](handover/RUNBOOK.md) · [setup](WIRING.md).

A complete month-end close — bank reconciliation, variance report, management
pack, sealed audit binder — run by Claude inside a standard claude.ai
licence, with a human reviewer gate between every step.

This is a working kit, not a demo video. Upload the four skills, connect the
mock ERP and the document folder, say *"Run the May 2026 close"*, and Claude
closes the books for a fictional company the way a controller would want it
done: every figure computed by a script, every step stopped for sign-off,
every sign-off sealed with a hash into an audit binder.

Built by [Karim Lameer](https://github.com/klameer) — CIMA-qualified
accountant building AI systems for finance teams at
[codelessops.com](https://codelessops.com).

## Why this exists

Finance teams don't need AI that answers faster. They need AI whose work an
auditor can follow. The design rules this kit demonstrates:

1. **The model never computes a figure.** Every number comes from a bundled
   Python script (`reconcile.py`, `variance.py`, `build_pack.py`); the model
   orchestrates, narrates, and asks.
2. **Nothing advances without a named reviewer's initials.** Each step ends
   in a hard STOP presenting the output document itself. Judgment calls (a
   stale cheque, an unexplained variance) are put to the human as explicit
   questions.
3. **The audit trail is the product.** Every sign-off appends a sealed
   record (sha256 of the signed file, reviewer, timestamp) to a close log;
   close-out compiles the binder PDF from those records.
4. **Known-answer verification.** A six-check golden set re-derives the
   close's key facts from raw inputs. Change anything, rerun it; a red
   golden set means the change is rejected.

## What's in the box

```
skills/close-pack/     Four Claude skills:
  close-checklist/       orchestrator — runs the steps in order, gates, binder
  bank-rec/              step 1 — bank rec with brought-forward opening rec
  variance-report/       step 2 — variance vs budget, scripted figures only
  pack-build/            step 3 — fills the management pack template, verifies
dist/                  The same four skills zipped, ready to upload to claude.ai
erp-api/               "Caldergate ERP Cloud" — FastAPI mock ERP serving the
                       trial balance, cashbook and bank statement over MCP
                       (claude.ai custom connector) and REST. Deployable to
                       Cloud Run free tier; runs locally too.
drive-seed/            The company's document estate, prebuilt: bank statement
                       PDF, cashbook extract, prior-month rec, budget workbook,
                       pack template, board reports — plus the generators.
guardrails/            One-page guardrails & data policy for the setup
handover/              The runbook a finance team would actually receive
```

All data is for **Caldergate Distribution Group Ltd — a fictional UK
distribution company**. Nothing here derives from any real organisation.
The reconciling items aren't hand-planted either: the bank statement and
cashbook are generated with real timing differences, so step 1's findings
(including a stale cheque that needs a human decision) fall out of the data.

## Run it yourself

Requirements: a claude.ai plan with skills + custom connectors, and
somewhere to host the mock ERP (Cloud Run free tier works; localhost works
for the REST twin).

The click-by-click setup is in [WIRING.md](WIRING.md). The short version:

1. Deploy `erp-api/` and add it as a custom connector.
2. Put `drive-seed/seed/Caldergate Finance - Month End` where Claude can
   reach it (Google Drive connector, or a connected local folder).
3. Upload the four zips from `dist/`.
4. Create a project with the instructions in WIRING.md, add
   `GUARDRAILS.md` + `RUNBOOK.md` as project knowledge.
5. Say **"Run the May 2026 close."**

The close stops at three gates. You are the reviewer: open the draft, check
it, give your initials. At the end, **"Close out May 2026"** produces the
audit binder.

## Verify it

```bash
python -m pip install -r erp-api/requirements.txt pytest httpx
python -m pytest erp-api/tests -q
```

The golden set (`skills/close-pack/close-checklist/scripts/run_goldens.py`)
re-runs the reconciliation and variance engines from raw inputs and asserts
six known answers — values, not flags, so tuning a materiality threshold
stays green while broken arithmetic goes red.

## License

MIT. Use it, adapt it, run it for your own team. If you want a close like
this built around your actual systems, that's what I do:
[codelessops.com](https://codelessops.com).
