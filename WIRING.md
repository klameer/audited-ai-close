# Wiring the close into claude.ai

One-time setup, roughly ten minutes.

## 1. Host the mock ERP

Anywhere that runs a container works. Cloud Run free tier:

```bash
gcloud run deploy caldergate-erp --source erp-api --region europe-west2 --allow-unauthenticated --set-env-vars DEMO_API_KEY=<pick-a-key>
```

The service is read-only fictional data behind the key, so it is safe to
leave up. `/health` is open and lists datasets — use it to warm the
instance before a session (cold start adds ~2s to the first call).

Local alternative (REST only, no claude.ai connector):
`cd erp-api && pip install -r requirements.txt && uvicorn app:app`.

## 2. Custom connector — Caldergate ERP Cloud

claude.ai → Settings → Connectors → **Add custom connector**
- Name: `Caldergate ERP Cloud`
- URL: `https://<your-service>/mcp/caldergate-close/?key=<your-key>`
- No OAuth. Save.

## 3. The document estate

Put `drive-seed/seed/Caldergate Finance - Month End` somewhere Claude can
read and write:

- **Google Drive**: drag the folder into My Drive (top level) and enable the
  Drive connector; or
- **Connected local folder** (Claude desktop app): keep a local copy —
  pairing it with Google Drive for Desktop means every filing syncs to the
  shared Drive where the team sees it.

Keep the folder name exact — the skills reference it.

## 4. Skills

Settings → Capabilities → Skills → **Upload skill**, once per zip in
`dist/`: `close-pack-close-checklist.zip` · `close-pack-bank-rec.zip` ·
`close-pack-variance-report.zip` · `close-pack-pack-build.zip`

(Rebuild a zip after editing a skill: zip the skill's folder so `SKILL.md`
sits at the zip root.)

## 5. Project

Projects → New project → **Caldergate — Month End Close**.
Project knowledge: add `guardrails/GUARDRAILS.md` + `handover/RUNBOOK.md`.
Project instructions — paste, filling in your reviewer's name and initials:

> This project runs the Caldergate Distribution Group month-end close using
> the close-pack skills. The named reviewer is <NAME> (initials <XX>) — no
> output is posted or filed without their sign-off at each gate; judgment
> items are put to them as explicit questions. Every figure comes from the
> skills' bundled scripts, never computed in-chat. Working files live in
> the folder "Caldergate Finance - Month End"; file outputs there only
> after sign-off. Data connections: the Caldergate ERP Cloud connector
> (read-only) and the document folder. Follow GUARDRAILS.md in the project
> knowledge; if a check fails or a connector errors, stop and report —
> never reconstruct figures from memory. "Run the May 2026 close" starts
> the checklist; "Close out May 2026" generates the audit binder; "Rerun
> the golden set" verifies after any modification.

## 6. Smoke test

New chat in the project, connectors toggled: Caldergate ERP Cloud on, the
document folder on, everything else off. Type: *"Call get_trial_balance on
the Caldergate ERP and tell me May-26 total revenue."* Expect **£21,063k**,
cited from the trial balance. Then: *"Run the May 2026 close."*
