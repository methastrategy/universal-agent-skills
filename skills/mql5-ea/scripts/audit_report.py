"""Read an exported MT5 Strategy Tester HTML report without starting MetaTrader."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
import json
import math
from pathlib import Path
from random import Random
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


class ReportRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = self.cell = None


def read_report(path):
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    if data[:400].count(b"\0") > 20:
        encoding = "utf-16le" if data[1:400:2].count(b"\0") > data[:400:2].count(b"\0") else "utf-16be"
        return data.decode(encoding)
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252")


def amount(value):
    """Parse MT5 decimal fields, which can use space groupings and a decimal comma."""
    raw = value.replace(" ", "")
    if not re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", raw):
        return None
    try:
        return Decimal(raw.replace(",", "."))
    except InvalidOperation:
        return None


def sections(rows):
    summary = {}
    orders = []
    deals = []
    section = ""
    header = None
    for row in rows:
        values = [cell for cell in row if cell]
        if len(values) == 1 and values[0] in {"Orders", "Deals"}:
            section = values[0]
            header = None
        elif section:
            columns = {"Open Time", "Order"} if section == "Orders" else {"Time", "Order", "Symbol", "Type", "Direction", "Volume"}
            if columns.issubset(row):
                header = row
            elif header is not None and len(row) == len(header):
                (orders if section == "Orders" else deals).append(dict(zip(header, row)))
        else:
            for name, value in zip(values, values[1:]):
                if name.endswith(":") and not value.endswith(":"):
                    summary[name[:-1]] = value
    return summary, orders, deals


def deal_time(deal):
    try:
        return datetime.strptime(deal["Time"], "%Y.%m.%d %H:%M:%S")
    except (KeyError, ValueError):
        return None


def round_trips(deals):
    """Match only unambiguous, complete entries and exits for a symbol."""
    by_symbol = defaultdict(list)
    for deal in deals:
        by_symbol[deal["Symbol"]].append(deal)
    finished = []
    ambiguous = []
    for symbol, rows in by_symbol.items():
        matches = []
        entry = None
        for deal in rows:
            direction = deal["Direction"].lower()
            if direction == "in" and entry is None:
                entry = deal
                continue
            if direction != "out" or entry is None or deal["Type"].lower() == entry["Type"].lower():
                break
            size = amount(deal["Volume"])
            opened, closed = deal_time(entry), deal_time(deal)
            if size is None or size <= 0 or size != amount(entry["Volume"]) or not opened or not closed or closed < opened:
                break
            amounts = []
            for trade in (entry, deal):
                for field in ("Profit", "Commission", "Swap", "Fee"):
                    if field in trade:
                        amounts.append(amount(trade[field]))
            if any(value is None for value in amounts) or "Profit" not in entry or "Profit" not in deal:
                break
            matches.append((closed, (closed - opened).total_seconds(), sum(amounts)))
            entry = None
        else:
            if entry is None:
                finished.extend(matches)
                continue
        ambiguous.append(symbol)
    return sorted(finished, key=lambda event: event[0]), sorted(ambiguous)


def bootstrap(returns, deposit, block, iterations, seed):
    rng = Random(seed)
    drawdowns = []
    depleted = 0
    for _ in range(iterations):
        equity = peak = deposit
        max_drawdown = 0
        for offset in range(0, len(returns), block):
            start = rng.randrange(len(returns) - block + 1)
            for result in returns[start:start + min(block, len(returns) - offset)]:
                equity += result
                peak = max(peak, equity)
                max_drawdown = max(max_drawdown, (peak - equity) / peak)
                if equity <= 0:
                    break
            if equity <= 0:
                depleted += 1
                break
        drawdowns.append(round(float(max_drawdown) * 100, 6))
    drawdowns.sort()
    return {
        "status": "ok", "iterations": iterations, "block_size": block, "seed": seed,
        "drawdown_percent": {str(q): drawdowns[math.ceil(q * iterations / 100) - 1] for q in (50, 95, 99)},
        "probability_of_zero_balance": depleted / iterations,
    }


def audit(path, block, iterations, seed):
    parser = ReportRows()
    parser.feed(read_report(path))
    summary, orders, raw_deals = sections(parser.rows)
    if "Total Trades" not in summary or "Total Net Profit" not in summary:
        raise ValueError("Expected an English MT5 Strategy Tester HTML summary with Total Trades and Total Net Profit.")
    deals = [row for row in raw_deals if row.get("Type", "").lower() in {"buy", "sell"} and row.get("Symbol")]
    entries = [row for row in deals if row["Direction"].lower() == "in"]
    exits = [row for row in deals if row["Direction"].lower() == "out"]
    trips, ambiguous = round_trips(deals)
    orders_by_id = {row["Order"]: row for row in orders}
    stops = [amount(orders_by_id.get(row.get("Order"), {}).get("S / L", "")) for row in entries]
    targets = [amount(orders_by_id.get(row.get("Order"), {}).get("T / P", "")) for row in entries]
    deposit = amount(summary.get("Initial Deposit", ""))
    if deposit is None or deposit <= 0:
        risk = {"status": "unavailable", "reason": "Missing positive initial deposit"}
    elif ambiguous or len(trips) < max(2, block):
        risk = {"status": "unavailable", "reason": "Incomplete trade matching or insufficient trades for the block size"}
    else:
        net = amount(summary["Total Net Profit"])
        returns = [event[2] for event in trips]
        if net is None or abs(sum(returns) - net) > Decimal("0.01"):
            risk = {"status": "unavailable", "reason": "Matched net returns do not reconcile to report profit"}
        else:
            risk = bootstrap(returns, deposit, block, iterations, seed)
    entry_times = [value for row in entries if (value := deal_time(row)) is not None]
    return {
        "report": path.name,
        "summary": summary,
        "vectors": {
            "temporal": {"entries_by_report_hour": dict(sorted(Counter(t.hour for t in entry_times).items())),
                         "holding_seconds_for_matched_trades": [trip[1] for trip in trips]},
            "entry": {"side_counts": dict(Counter(row["Type"].lower() for row in entries))},
            "sizing": {"entry_volume_counts": dict(Counter(row["Volume"] for row in entries))},
            "invalidation": {"entries_with_recorded_stop": sum(v is not None and v > 0 for v in stops),
                             "entries_with_recorded_zero_stop": sum(v == 0 for v in stops),
                             "entries_without_stop_evidence": sum(v is None for v in stops)},
            "exit": {"out_deals": len(exits), "entries_with_recorded_target": sum(v is not None and v > 0 for v in targets),
                     "exit_comments": dict(Counter(row["Comment"] for row in exits if row.get("Comment")))},
        },
        "matched_trades": len(trips),
        "unmatched_symbols": ambiguous,
        "bootstrap": risk,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--iterations", type=int, default=1000)
    parser.add_argument("--block-size", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if not 1 <= args.iterations <= 10000 or args.block_size < 1:
        parser.error("Iterations must be 1–10000 and block size must be positive.")
    try:
        print(json.dumps(audit(args.report, args.block_size, args.iterations, args.seed), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Audit failed: {error}\n")


if __name__ == "__main__":
    main()
