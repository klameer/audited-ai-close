# AI Close — Guardrails & Data Policy (one page)

**Org:** Caldergate Distribution Group Ltd (demo estate — fictitious data)
**Scope:** the month-end close run in the Claude desktop app with the close-pack skills
**Owner / signatory:** Financial Controller · **Review:** annually or on any connector change

## 1. What the AI can reach (least access)

| Connection | Access | Enforced by |
|---|---|---|
| Caldergate ERP Cloud (custom connector) | **Read-only** — trial balance, cashbook, bank statement. The API has no write endpoints. | The service itself (no write code deployed); per-dataset API key |
| The estate folder (connected local folder) | Read and file within `Caldergate Finance — Month End` **only** — the reviewer's Google Drive for Desktop copy of the shared folder; Google's own sync publishes filings to the team's Drive | Session file access granted per session and scoped to this folder; nothing outside it is connected |

Keys live in the connector configuration, never in the chat window, so they
can never appear in a transcript. The ERP key unlocks **only** this
dataset. Folder isolation is structural: the session is given the estate
folder and nothing else, and every filing lands there in the open —
visible in the shared Drive within seconds, where any team member can see
(and challenge) it.

## 2. What may enter the chat window

Close working data (statements, cashbooks, TBs, budgets, packs) — yes.
**Never:** payroll or personal data, credentials or keys, customer-named
exports, anything outside the close's need-to-know. If a document would be
redacted for an auditor, it does not enter the window.

## 3. Human-in-the-loop gates (nothing bypasses these)

1. Each close step ends in a hard STOP **presenting the output document
   itself** (the rec workbook, the report, the pack) for the reviewer to
   open; a **named reviewer signs with initials** before anything advances
   or is filed.
2. Judgment items (e.g. a stale cheque) are put to the reviewer as an
   explicit question; the AI never decides them.
3. **The folder always tells the truth about status.** Raw system pulls are
   filed on receipt, unmodified — they are evidence. AI-produced documents
   land for review **clearly marked DRAFT**; the final, reviewer-named copy
   files **only after sign-off**. Nothing unsigned ever appears without the
   DRAFT mark, and estate documents are never modified — filings only add
   files, every one immediately visible in the shared Drive.
4. Any failed automated check stops the close at that step — and so does
   any failed filing: an output that never landed in the folder is not
   filed, and the close does not advance past it.

## 4. Show-your-working (the audit trail)

Every figure is computed by a bundled script — never by the model. Each step
re-derives its own outputs through independent tie-out checks before the
gate. Every sign-off appends a sealed record (sha256 of the signed result,
reviewer, timestamp) to the close log; close-out compiles the **audit
binder** (PDF) from those records. Commentary numbers that are not in the
signed sources are listed for the reviewer to verify against the cited
document — unattributed numbers do not ship.

## 5. Provider & data handling

Anthropic commercial terms apply to the workspace (no training on business
data per the applicable no-training tier — confirm tier on the account
before relying on this line). Chat history retention follows workspace
settings. The mock ERP holds fictitious data only and is safe to leave
internet-reachable behind its key.

## 6. If something goes wrong

Any suspected wrong figure: stop the close, keep the thread (it is the
evidence), rerun the step's checks and the golden set, and escalate to the
owner. Revoking access = delete the connector (ERP) / remove the estate
folder from the session's file access — both take effect immediately.

**Signed (CFO / owner):** ______________________  **Date:** ____________
