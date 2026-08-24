"""demo-api tests (caldergate-close dataset, close-v2 canon) — run with the
app backend venv:  cd demo-api && <venv>/python -m pytest tests -q
"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as demo  # noqa: E402

DS = "/v1/caldergate-close"
BOOK_CLOSE = 8911388.92     # May rec / pack BS canon
BANK_CLOSE = 9882613.23     # statement canon


# module scope: MCP's StreamableHTTP session manager only allows one .run()
# per process, so all tests share one app lifespan
@pytest.fixture(scope="module")
def client():
    with TestClient(demo.app) as c:
        yield c


def test_health_lists_datasets(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert "caldergate-close" in body["datasets"]


def test_auth_shared_and_per_dataset_keys(client):
    os.environ["DEMO_API_KEY"] = "shared"
    try:
        assert client.get(f"{DS}/trial-balance").status_code == 401
        assert client.get(f"{DS}/trial-balance", headers={"X-API-Key": "shared"}).status_code == 200
        os.environ["DEMO_API_KEY_CALDERGATE_CLOSE"] = "specific"
        assert client.get(f"{DS}/trial-balance", headers={"X-API-Key": "shared"}).status_code == 401
        assert client.get(f"{DS}/trial-balance", params={"key": "specific"}).status_code == 200
        assert client.get("/health").status_code == 200
    finally:
        os.environ.pop("DEMO_API_KEY", None)
        os.environ.pop("DEMO_API_KEY_CALDERGATE_CLOSE", None)


def test_trial_balance_has_canon_lines(client):
    tb = client.get(f"{DS}/trial-balance").json()
    assert tb["period"] == "May-26"
    assert "Industrial Consumables & Packaging" in tb["lines"]
    assert all({"mtd_actual", "ytd_actual"} <= set(v) for v in tb["lines"].values())


def test_statement_is_canon_and_chains(client):
    rows = client.get(f"{DS}/bank-statement").json()["rows"]
    assert not any("FLEETSERV" in r["description"] for r in rows)  # nothing planted
    assert float(rows[-1]["balance_gbp"]) == BANK_CLOSE
    for prev, cur in zip(rows, rows[1:]):
        expected = (float(prev["balance_gbp"]) - float(cur["paid_out_gbp"] or 0)
                    + float(cur["paid_in_gbp"] or 0))
        assert abs(expected - float(cur["balance_gbp"])) < 0.01


def test_cashbook_ties_to_canon(client):
    cb = client.get(f"{DS}/cashbook").json()
    net = sum(e["money_in_gbp"] - e["money_out_gbp"] for e in cb["rows"])
    assert abs(cb["opening_balance_gbp"] + net - BOOK_CLOSE) < 0.01
    assert cb["closing_balance_gbp"] == BOOK_CLOSE
    late = [e for e in cb["rows"] if e["value_date"] is None or e["value_date"] > "2026-05-31"]
    assert len(late) == 5  # the derived timing differences (cards split in two)


def test_rec_identity_bank_to_book(client):
    """bank close - unpresented + uncleared == book close (the May rec)."""
    cb = client.get(f"{DS}/cashbook").json()["rows"]
    late = [e for e in cb if e["value_date"] is None or e["value_date"] > "2026-05-31"]
    unpresented = sum(e["money_out_gbp"] for e in late)
    uncleared = sum(e["money_in_gbp"] for e in late)
    stale_cheque = 1850.00  # April opening item, still unpresented (Drive rec doc)
    assert abs(BANK_CLOSE - (unpresented + stale_cheque) + uncleared - BOOK_CLOSE) < 0.01


def test_unknown_period_404(client):
    r = client.get(f"{DS}/cashbook", params={"period": "Jun-26"})
    assert r.status_code == 404 and "May-26" in r.json()["detail"]


def test_mcp_endpoint_mounted(client):
    r = client.post("/mcp/caldergate-close/", json={})
    assert r.status_code != 404
