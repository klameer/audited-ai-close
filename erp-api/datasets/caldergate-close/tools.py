"""Caldergate ERP Cloud — the month-end close demo dataset (close-v2 canon).

Exposed by demo-api/app.py as /mcp/caldergate-close (MCP custom connector)
and /v1/caldergate-close/... (REST twin). Read-only, fictional.
"""
import csv
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

DATA = Path(__file__).resolve().parent / "data"

TRIAL_BALANCE = json.loads((DATA / "trial_balance_2026-05.json").read_text())
CASHBOOK = json.loads((DATA / "cashbook_2026-05.json").read_text())
ACCOUNTS = json.loads((DATA / "bank_accounts.json").read_text())
STATEMENT_ROWS = list(csv.DictReader((DATA / "bank_statement_2026-05.csv").open()))

PERIODS = ["May-26"]


def _check_period(period: str) -> None:
    if period not in PERIODS:
        raise ValueError(f"No data for period '{period}'. Available: {', '.join(PERIODS)}")


def trial_balance(period: str) -> dict:
    _check_period(period)
    return TRIAL_BALANCE


def cashbook(period: str) -> dict:
    _check_period(period)
    return CASHBOOK


def bank_statement(period: str, account: str = "main") -> dict:
    _check_period(period)
    if account != "main":
        raise ValueError("Unknown account. Available: main")
    return {"system": "Caldergate ERP (mock)", "dataset": "bank_statement",
            "period": period, "account": ACCOUNTS["accounts"][0], "currency": "GBP",
            "row_count": len(STATEMENT_ROWS), "rows": STATEMENT_ROWS}


# Public HTTPS service behind key auth: DNS-rebinding Host checks (a
# localhost-server protection) would 421 every request on the run.app host.
mcp = FastMCP("caldergate-erp-cloud", stateless_http=True,
              transport_security=TransportSecuritySettings(
                  enable_dns_rebinding_protection=False))
mcp.settings.streamable_http_path = "/"


@mcp.tool()
def get_trial_balance(period: str = "May-26") -> str:
    """P&L trial balance for a period (GBP thousands, MTD + YTD actuals).
    Ties to the issued Monthly Reporting Packs."""
    return json.dumps(trial_balance(period))


@mcp.tool()
def get_cashbook(period: str = "May-26") -> str:
    """Cashbook (book of record) for the operating account, actual pounds.
    book_date = posting date; value_date = when it hits the bank (null =
    not yet presented); bank_narrative = the statement text it appears as."""
    return json.dumps(cashbook(period))


@mcp.tool()
def get_bank_statement(period: str = "May-26", account: str = "main") -> str:
    """Bank statement lines for the operating account with running balance,
    as issued by Pennine Commercial Bank."""
    return json.dumps(bank_statement(period, account))


rest = APIRouter()


def _rest(fn, **kwargs):
    try:
        return fn(**kwargs)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@rest.get("/trial-balance")
def rest_trial_balance(period: str = "May-26"):
    return _rest(trial_balance, period=period)


@rest.get("/cashbook")
def rest_cashbook(period: str = "May-26"):
    return _rest(cashbook, period=period)


@rest.get("/bank-statement")
def rest_bank_statement(period: str = "May-26", account: str = "main"):
    return _rest(bank_statement, period=period, account=account)
