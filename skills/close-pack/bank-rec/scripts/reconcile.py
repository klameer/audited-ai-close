"""Bank reconciliation: statement vs cashbook + last month's rec b/f. Stdlib.

Usage: reconcile.py statement.json cashbook.json opening_rec.json out.json

Model (mirrors how the close actually works):
  every May statement line is explained by either a May cashbook entry
  (matched on bank narrative + amount, else amount + value date) or an
  opening reconciling item clearing this month (matched on amount).
  Closing items = cashbook entries valuing after month-end (unpresented /
  uncleared by direction) + opening items that still haven't cleared —
  those are flagged STALE when older than STALE_DAYS, with a question the
  reviewer must answer.
"""
import json
import sys
from datetime import date

STALE_DAYS = 42
PERIOD_END = date(2026, 5, 31)


def _net(row: dict) -> float:
    return round(float(row["paid_in_gbp"] or 0) - float(row["paid_out_gbp"] or 0), 2)


def main(statement_path: str, cashbook_path: str, opening_path: str, out_path: str) -> None:
    stmt = json.load(open(statement_path))
    cb = json.load(open(cashbook_path))
    opening = json.load(open(opening_path))

    stmt_lines = [{"idx": i, "date": r["date"], "description": r["description"], "net": _net(r)}
                  for i, r in enumerate(stmt["rows"])]
    entries = [dict(e, net=round(e["money_in_gbp"] - e["money_out_gbp"], 2)) for e in cb["rows"]]

    unused_entries = list(range(len(entries)))
    unused_opening = list(range(len(opening["items"])))
    matches, unmatched_stmt = [], []
    for s in stmt_lines:
        hit = None
        for j in unused_entries:  # narrative+amount, then amount+value-date
            e = entries[j]
            if e["net"] == s["net"] and e["bank_narrative"] == s["description"]:
                hit = ("cashbook", j); break
        if hit is None:
            for j in unused_entries:
                e = entries[j]
                if e["net"] == s["net"] and e["value_date"] == s["date"]:
                    hit = ("cashbook", j); break
        if hit is None:
            for j in unused_opening:  # opening item clearing this month
                if opening["items"][j]["amount_gbp"] == s["net"]:
                    hit = ("opening", j); break
        if hit is None:
            unmatched_stmt.append(s)
        elif hit[0] == "cashbook":
            unused_entries.remove(hit[1])
            matches.append({"statement": s, "cashbook_ref": entries[hit[1]]["entry_ref"]})
        else:
            unused_opening.remove(hit[1])
            matches.append({"statement": s, "opening_item": opening["items"][hit[1]]["description"]})

    closing_items = []
    for j in unused_entries:
        e = entries[j]
        closing_items.append({
            "description": e["description"], "book_date": e["book_date"],
            "expected_clearing": e["value_date"] or "OPEN",
            "amount_gbp": e["net"], "source": "cashbook",
            "kind": "unpresented_payment" if e["net"] < 0 else "uncleared_lodgement",
            "stale": False,
            "reading": "Booked in May; hits the bank after month-end. Timing difference.",
        })
    for j in unused_opening:
        item = opening["items"][j]
        age = (PERIOD_END - date.fromisoformat(item["item_date"])).days if item["item_date"] else None
        stale = age is not None and age > STALE_DAYS
        closing_items.append({
            "description": item["description"], "book_date": item["item_date"],
            "expected_clearing": "OPEN", "amount_gbp": item["amount_gbp"],
            "source": "opening_rec", "kind": item["kind"], "stale": stale,
            "age_days": age,
            "reading": ("Carried forward from last month's rec and STILL not cleared."
                        if stale else "Carried forward from last month's rec."),
            "reviewer_question": (
                f"Outstanding {age} days. Stop and reissue, write back, or carry forward?"
                if stale else None),
        })

    unpresented = round(-sum(i["amount_gbp"] for i in closing_items if i["amount_gbp"] < 0), 2)
    uncleared = round(sum(i["amount_gbp"] for i in closing_items if i["amount_gbp"] > 0), 2)
    bank_close = round(float(stmt["rows"][-1]["balance_gbp"]), 2)
    result = {
        "reconciliation": "bank statement vs cashbook (Operating Account)",
        "period": stmt.get("period"),
        "statement_lines": len(stmt_lines), "matched": len(matches),
        "unmatched_statement_lines": unmatched_stmt,
        "statement_close_gbp": bank_close,
        "closing_items": closing_items,
        "reconciliation_statement": {
            "balance_per_bank_gbp": bank_close,
            "less_unpresented_payments_gbp": unpresented,
            "add_uncleared_lodgements_gbp": uncleared,
            "derived_book_balance_gbp": round(bank_close - unpresented + uncleared, 2),
            "cashbook_closing_balance_gbp": cb["closing_balance_gbp"],
        },
        "stale_item_count": sum(1 for i in closing_items if i["stale"]),
        "matches": matches,
    }
    json.dump(result, open(out_path, "w"), indent=1)
    rs = result["reconciliation_statement"]
    agreed = abs(rs["derived_book_balance_gbp"] - rs["cashbook_closing_balance_gbp"]) < 0.01
    print(f"{result['matched']}/{result['statement_lines']} statement lines explained; "
          f"{len(closing_items)} closing item(s), {result['stale_item_count']} stale; "
          f"rec {'AGREES' if agreed else 'DOES NOT AGREE'} to the cashbook -> {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
