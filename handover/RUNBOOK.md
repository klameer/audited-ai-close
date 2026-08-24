# AI Close — Runbook (what you keep)

The close runs in the Claude desktop app with four skills (`close-pack-*`),
one read-only ERP connector, and your month-end **estate folder** — the
Google Drive for Desktop copy of `Caldergate Finance — Month End` on the
reviewer's machine, connected to the session. Files move as normal file
copies (fast, no size limits); Google's own sync publishes every filing to
the team's shared Drive within seconds. Everything below is yours to run
and change — no vendor required.

## Running the close (monthly)

1. Start a new session in the Claude desktop app with the estate folder
   connected (Google Drive for Desktop running, so filings sync).
2. Type **"Run the ⟨month year⟩ close."** — e.g. "Run the June 2026
   close.", matching the period due. The checklist runs step 1 (bank rec)
   → step 2 (variance) → step 3 (pack). At each gate it files **the
   document itself** (rec workbook / variance report / pack) into the
   month folder **marked DRAFT** — open it there, review it, and sign the
   file you've seen with your initials; the signed, reviewer-named copy
   then files beside it. The folder always tells the truth about status.
   Judgment items (e.g. a stale cheque) come to you as explicit questions,
   and your decisions are recorded in the close log.
3. When all three steps are signed, type **"Close out ⟨month year⟩."**
   Close-out first verifies every signed output actually landed in the
   estate folder, then the audit binder (PDF) and close log land there too.
4. Type **"where are we?"** at any point for the status board — done / next
   / blocked per step, printed from the close log (a step only counts as
   done when its signed record is in the log). The same board appears at
   every gate and after every sign-off.

Everything a script computed, a check re-derived; everything filed, you
signed first. If a connector is down or a check fails, the close stops and
says so — it never improvises.

## Changing it (the point of this document)

The skills are plain-English markdown + small Python scripts. Change recipe:
edit → **rerun the golden set** → all green = safe.

| Want to… | Edit |
|---|---|
| Raise/lower the variance flag threshold | `close-pack-variance-report/SKILL.md` — the "Flag threshold" line (one number) |
| Change the stale-item age | `close-pack-bank-rec/scripts/reconcile.py` — `STALE_DAYS` |
| New month | The period in your prompt + that month's budget column / statements; periods served by the ERP are listed in its error messages |
| Change pack layout | `Management Pack Template.pptx` in `01 Templates & Budget/` (placeholders: `{{PERIOD}}`, `{{CASH_TABLE}}`, `{{VARIANCE_TABLE}}`, `{{COMMENTARY}}`, `{{SIGNOFFS}}`; keep the DRAFT status line — sign-off swaps it for the reviewer's name) |
| Add a golden check | `close-pack-close-checklist/scripts/golden-set.yaml` + `run_goldens.py` |

**Golden set:** say **"Rerun the golden set"** in the project. Six
known-answer checks recompute the close from raw inputs (values, not
thresholds — so tuning materiality passes; broken arithmetic fails). Never
accept a modification while any check is red.

## Failure modes

| Symptom | Meaning | Do |
|---|---|---|
| "ERP connector failed / 401" | Service down or key rotated | Check `<service>/health`; re-enter key in the connector config |
| "Checks failed" at a gate | An output didn't re-derive from raw inputs | Don't sign. Read the named check; rerun the step; escalate if it persists |
| Signed output missing from the estate folder | A filing failed mid-run | The step is not done — have the run re-file from its working files; close-out refuses to seal the binder until every signed output is filed |
| Filed output not appearing in the shared Drive | Google Drive for Desktop paused or offline | The estate folder on disk is the source of truth; check the sync client is running — files publish once it is |
| Skill won't stop at a gate | Prompt-injection or skill edit gone wrong | Stop the run; restore SKILL.md from the kit copy; rerun goldens |
| Cold first response | Cloud Run scale-to-zero warm-up | Normal; retry once |

## What lives where

The estate folder (local, synced to the shared Drive): inputs (budget,
template, prior recs, statements) + everything the close files (reports,
pack, binder, close log). Skills: Claude → Settings → Capabilities.
Connector + key: Settings → Connectors. Kit source of record: the
`close-kit/` folder handed over with this document. Guardrails:
`GUARDRAILS.md` (signed copy in the folder).
