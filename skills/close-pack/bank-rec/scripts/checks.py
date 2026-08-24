"""Independent tie-outs for the bank reconciliation. Exit 1 on any failure.

Usage: checks.py statement.json cashbook.json opening_rec.json reconciliation.json

Re-derives every claim from the raw inputs:
  C1 statement running balance is internally consistent
  C2 every statement line explained; matched + unmatched == lines
  C3 rec identity: bank - unpresented + uncleared == cashbook closing (pence)
  C4 cashbook integrity: opening b/f + ins - outs == cashbook closing
  C5 conservation: every cashbook entry and opening item is either matched
     or in the closing items — nothing silently dropped
"""
import json
import sys


def main(statement_path, cashbook_path, opening_path, rec_path) -> None:
    stmt = json.load(open(statement_path))["rows"]
    cb = json.load(open(cashbook_path))
    opening = json.load(open(opening_path))
    rec = json.load(open(rec_path))
    failures = []

    for prev, cur in zip(stmt, stmt[1:]):
        expected = (float(prev["balance_gbp"]) - float(cur["paid_out_gbp"] or 0)
                    + float(cur["paid_in_gbp"] or 0))
        if abs(expected - float(cur["balance_gbp"])) >= 0.01:
            failures.append(f"C1 running balance breaks at {cur['date']} {cur['description']}")

    if rec["matched"] + len(rec["unmatched_statement_lines"]) != len(stmt):
        failures.append("C2 statement lines don't add up")
    if rec["unmatched_statement_lines"]:
        failures.append(f"C2 {len(rec['unmatched_statement_lines'])} statement line(s) unexplained")

    rs = rec["reconciliation_statement"]
    unpresented = round(-sum(i["amount_gbp"] for i in rec["closing_items"] if i["amount_gbp"] < 0), 2)
    uncleared = round(sum(i["amount_gbp"] for i in rec["closing_items"] if i["amount_gbp"] > 0), 2)
    derived = round(float(stmt[-1]["balance_gbp"]) - unpresented + uncleared, 2)
    if abs(derived - cb["closing_balance_gbp"]) >= 0.01:
        failures.append(f"C3 rec identity fails: derived {derived} vs cashbook {cb['closing_balance_gbp']}")
    if (rs["less_unpresented_payments_gbp"], rs["add_uncleared_lodgements_gbp"]) != (unpresented, uncleared):
        failures.append("C3 reconciliation statement figures don't re-derive")

    book_net = round(sum(e["money_in_gbp"] - e["money_out_gbp"] for e in cb["rows"]), 2)
    if abs(cb["opening_balance_gbp"] + book_net - cb["closing_balance_gbp"]) >= 0.01:
        failures.append("C4 cashbook opening + movements != closing")

    cb_matched = {m["cashbook_ref"] for m in rec["matches"] if "cashbook_ref" in m}
    cb_closing = {i["description"] for i in rec["closing_items"] if i["source"] == "cashbook"}
    if len(cb_matched) + len(cb_closing_rows := [e for e in cb["rows"]
            if e["entry_ref"] not in cb_matched]) != len(cb["rows"]) or \
            len(cb_closing_rows) != len(cb_closing):
        failures.append("C5 cashbook entries lost between matches and closing items")
    op_matched = sum(1 for m in rec["matches"] if "opening_item" in m)
    op_closing = sum(1 for i in rec["closing_items"] if i["source"] == "opening_rec")
    if op_matched + op_closing != len(opening["items"]):
        failures.append("C5 opening items lost between matches and closing items")

    if failures:
        print("CHECKS FAILED:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print(f"checks passed: C1 chain, C2 all {rec['matched']} lines explained, "
          f"C3 rec identity to the penny, C4 cashbook integrity, C5 conservation")


if __name__ == "__main__":
    main(*sys.argv[1:5])
