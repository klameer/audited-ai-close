# Caldergate ERP Cloud (mock)

A small FastAPI service that plays the company's ERP for the close: trial
balance, cashbook, and bank statement for May-26, served over MCP (for the
claude.ai custom connector) and a REST twin. Read-only, fictional data —
safe to leave internet-reachable behind its key.

```
app.py                      generic host: discovers datasets/, mounts each
datasets/<name>/tools.py    the dataset: a FastMCP (`mcp`) + optional REST router (`rest`)
datasets/<name>/data/       its bundled data (prebuilt, checked in)
```

**Auth:** `X-API-Key` header or `?key=`; per-dataset env
`DEMO_API_KEY_<DATASET>` (upper-snake) overrides shared `DEMO_API_KEY`;
unset = auth off (local dev only). `/health` is open and lists datasets.

**Endpoints:** MCP `/mcp/caldergate-close/` (streamable HTTP — the claude.ai
custom connector URL; the `?key=` form works there) · REST
`/v1/caldergate-close/trial-balance|cashbook|bank-statement`.

**Tests:** `pip install -r requirements.txt && python -m pytest tests -q`

**Deploy** (Cloud Run free tier, scales to zero):

```bash
gcloud run deploy caldergate-erp --source . --region europe-west2 --allow-unauthenticated --set-env-vars DEMO_API_KEY=<key>
```
