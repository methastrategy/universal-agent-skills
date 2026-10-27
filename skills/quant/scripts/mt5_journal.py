#!/usr/bin/env python3
"""
MT5 Automated Trading Journal & Performance Analytics Engine
Connects to MetaTrader 5 via Python API, extracts closed deal history,
computes quantitative performance metrics, and outputs Markdown, CSV, and Equity Curve plots.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import csv

def parse_args():
    parser = argparse.ArgumentParser(description="MT5 Automated Trading Journal & Equity Plotter")
    parser.add_argument("--days", type=int, default=30, help="Lookback period in days (default: 30)")
    parser.add_argument("--all", action="store_true", help="Fetch all available history")
    parser.add_argument("--magic", type=int, default=None, help="Filter by specific Magic Number")
    parser.add_argument("--output-dir", type=str, default=".", help="Directory to save journal files (default: .)")
    parser.add_argument("--no-chart", action="store_true", help="Skip generating equity curve plot")
    parser.add_argument("--terminal-path", type=str, default=None, help="Custom path to terminal64.exe")
    parser.add_argument("--demo-mock", action="store_true", help="Generate mock report for testing without MT5 connection")
    return parser.parse_args()

def generate_mock_deals():
    """Generates synthetic deal data for offline testing."""
    import random
    random.seed(42)
    deals = []
    base_time = datetime.now() - timedelta(days=30)
    balance = 10000.0
    symbols = ["XAUUSD", "EURUSD", "GBPUSD"]
    magics = [0, 10101, 20202] # 0 = manual, 10101 = Trend EA, 20202 = Scalp EA
    
    for i in range(1, 45):
        trade_time = base_time + timedelta(hours=i * 14 + random.randint(1, 10))
        symbol = random.choice(symbols)
        magic = random.choice(magics)
        lot = round(random.choice([0.05, 0.1, 0.2]), 2)
        is_win = random.random() < 0.62
        profit = round(random.uniform(30, 150) if is_win else -random.uniform(20, 120), 2)
        comm = -round(lot * 6.0, 2)
        swap = round(random.uniform(-3, 1), 2)
        net = round(profit + comm + swap, 2)
        balance += net
        deals.append({
            "ticket": 100000 + i,
            "order": 50000 + i,
            "time": trade_time,
            "symbol": symbol,
            "type": "BUY" if random.random() > 0.5 else "SELL",
            "volume": lot,
            "price": round(random.uniform(2300, 2400) if symbol == "XAUUSD" else 1.08, 4),
            "profit": profit,
            "commission": comm,
            "swap": swap,
            "net_profit": net,
            "magic": magic,
            "comment": "Mock EA" if magic != 0 else "Manual order"
        })
    return deals

def fetch_mt5_deals(days, fetch_all, magic_filter, terminal_path):
    try:
        import MetaTrader5 as mt5
    except ImportError:
        print("[ERROR] MetaTrader5 package is not installed. Install via: pip install MetaTrader5")
        sys.exit(1)

    init_kwargs = {}
    if terminal_path:
        init_kwargs["path"] = terminal_path

    if not mt5.initialize(**init_kwargs):
        err = mt5.last_error()
        print(f"[ERROR] MT5 initialize failed: {err}")
        print("Tip: Ensure MT5 Terminal is running or specify --terminal-path, or use --demo-mock to test.")
        sys.exit(1)

    now = datetime.now()
    if fetch_all:
        from_date = datetime(2000, 1, 1)
    else:
        from_date = now - timedelta(days=days)

    raw_deals = mt5.history_deals_get(from_date, now)
    mt5.shutdown()

    if raw_deals is None or len(raw_deals) == 0:
        print(f"[WARN] No deals found in MT5 from {from_date.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
        return []

    # Filter closed trades (entry out / inout)
    trades = []
    for d in raw_deals:
        # entry 1 = DEAL_ENTRY_OUT, entry 2 = DEAL_ENTRY_INOUT
        if getattr(d, 'entry', -1) in (1, 2) and getattr(d, 'volume', 0) > 0:
            if magic_filter is not None and getattr(d, 'magic', 0) != magic_filter:
                continue
            
            profit = float(getattr(d, 'profit', 0.0))
            comm = float(getattr(d, 'commission', 0.0))
            swap = float(getattr(d, 'swap', 0.0))
            net_profit = profit + comm + swap
            deal_time = datetime.fromtimestamp(getattr(d, 'time', 0))
            deal_type = "BUY" if getattr(d, 'type', 0) == 0 else "SELL"
            
            trades.append({
                "ticket": getattr(d, 'ticket', 0),
                "order": getattr(d, 'order', 0),
                "time": deal_time,
                "symbol": getattr(d, 'symbol', "UNKNOWN"),
                "type": deal_type,
                "volume": float(getattr(d, 'volume', 0.0)),
                "price": float(getattr(d, 'price', 0.0)),
                "profit": profit,
                "commission": comm,
                "swap": swap,
                "net_profit": round(net_profit, 2),
                "magic": getattr(d, 'magic', 0),
                "comment": getattr(d, 'comment', "")
            })
    return trades

def compute_metrics(trades):
    if not trades:
        return {}

    total_trades = len(trades)
    wins = [t for t in trades if t["net_profit"] > 0]
    losses = [t for t in trades if t["net_profit"] < 0]
    evens = [t for t in trades if t["net_profit"] == 0]

    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total_trades * 100.0) if total_trades > 0 else 0.0

    gross_profit = sum(t["net_profit"] for t in wins)
    gross_loss = abs(sum(t["net_profit"] for t in losses))
    net_profit = sum(t["net_profit"] for t in trades)

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    else:
        profit_factor = float('inf') if gross_profit > 0 else 0.0

    avg_win = (gross_profit / win_count) if win_count > 0 else 0.0
    avg_loss = (gross_loss / loss_count) if loss_count > 0 else 0.0
    rr_ratio = (avg_win / avg_loss) if avg_loss > 0 else float('inf')
    expected_payoff = net_profit / total_trades if total_trades > 0 else 0.0

    # Drawdown calculation
    equity_curve = []
    current_equity = 0.0
    peak = 0.0
    max_dd_dollars = 0.0
    max_dd_pct = 0.0

    for t in sorted(trades, key=lambda x: x["time"]):
        current_equity += t["net_profit"]
        equity_curve.append((t["time"], current_equity))
        if current_equity > peak:
            peak = current_equity
        dd = peak - current_equity
        if dd > max_dd_dollars:
            max_dd_dollars = dd
        if peak > 0:
            dd_pct = (dd / peak) * 100.0
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct

    # Breakdown by Magic Number
    magic_map = {}
    for t in trades:
        m = t["magic"]
        magic_map.setdefault(m, []).append(t)

    magic_stats = {}
    for m, m_trades in magic_map.items():
        m_wins = len([x for x in m_trades if x["net_profit"] > 0])
        m_net = sum(x["net_profit"] for x in m_trades)
        m_gross_p = sum(x["net_profit"] for x in m_trades if x["net_profit"] > 0)
        m_gross_l = abs(sum(x["net_profit"] for x in m_trades if x["net_profit"] < 0))
        m_pf = (m_gross_p / m_gross_l) if m_gross_l > 0 else (float('inf') if m_gross_p > 0 else 0.0)
        magic_stats[m] = {
            "name": "Manual Trading" if m == 0 else f"EA (Magic: {m})",
            "trades": len(m_trades),
            "net_profit": round(m_net, 2),
            "win_rate": round(m_wins / len(m_trades) * 100.0, 1),
            "profit_factor": round(m_pf, 2) if m_pf != float('inf') else "Inf"
        }

    # Breakdown by Symbol
    symbol_map = {}
    for t in trades:
        s = t["symbol"]
        symbol_map.setdefault(s, []).append(t)

    symbol_stats = {}
    for s, s_trades in symbol_map.items():
        s_wins = len([x for x in s_trades if x["net_profit"] > 0])
        symbol_stats[s] = {
            "trades": len(s_trades),
            "net_profit": round(sum(x["net_profit"] for x in s_trades), 2),
            "win_rate": round(s_wins / len(s_trades) * 100.0, 1)
        }

    return {
        "total_trades": total_trades,
        "win_count": win_count,
        "loss_count": loss_count,
        "even_count": len(evens),
        "win_rate": round(win_rate, 2),
        "net_profit": round(net_profit, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "Inf",
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "rr_ratio": round(rr_ratio, 2) if rr_ratio != float('inf') else "Inf",
        "expected_payoff": round(expected_payoff, 2),
        "max_drawdown_dollars": round(max_dd_dollars, 2),
        "max_drawdown_pct": round(max_dd_pct, 2),
        "equity_curve": equity_curve,
        "magic_stats": magic_stats,
        "symbol_stats": symbol_stats
    }

def save_csv(trades, csv_path):
    keys = ["ticket", "order", "time", "symbol", "type", "volume", "price", "profit", "commission", "swap", "net_profit", "magic", "comment"]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for t in trades:
            row = dict(t)
            row["time"] = row["time"].strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow(row)

def save_markdown(metrics, md_path, date_str):
    content = f"""# MT5 Automated Trading Journal & Performance Report
**Generated at:** {date_str}

---

## 1. Executive Performance Summary

| Metric | Value | Target Benchmark | Status |
| :--- | :--- | :--- | :---: |
| **Total Closed Trades** | `{metrics['total_trades']}` | $\\ge 30$ trades | {'✅' if metrics['total_trades'] >= 30 else '⚠️'} |
| **Net Profit** | `\\${metrics['net_profit']:.2f}` | $> 0` | {'✅ PASS' if metrics['net_profit'] > 0 else '❌ LOSS'} |
| **Win Rate** | `{metrics['win_rate']:.1f}%` ({metrics['win_count']}W / {metrics['loss_count']}L) | $\\ge 50.0\\%$ | {'✅ PASS' if metrics['win_rate'] >= 50 else '⚠️ LOW'} |
| **Profit Factor** | `{metrics['profit_factor']}` | $\\ge 1.50$ | {'✅ STRONG' if isinstance(metrics['profit_factor'], (int, float)) and metrics['profit_factor'] >= 1.5 else '⚠️ WEAK'} |
| **Avg Win / Avg Loss** | `\\${metrics['avg_win']:.2f} / \\${metrics['avg_loss']:.2f}` | RRR $\\ge 1.2$ | `{metrics['rr_ratio']}` |
| **Expected Payoff** | `\\${metrics['expected_payoff']:.2f}` / trade | $> 0` | {'✅' if metrics['expected_payoff'] > 0 else '❌'} |
| **Max Drawdown** | `\\${metrics['max_drawdown_dollars']:.2f}` ({metrics['max_drawdown_pct']:.1f}%) | $\\le 10.0\\%$ | {'✅ SAFE' if metrics['max_drawdown_pct'] <= 10 else '⚠️ HIGH'} |

---

## 2. Segregation by Execution Source (EA Bots vs Manual Trades)

| Source / EA Name | Magic ID | Closed Trades | Net Profit | Win Rate | Profit Factor |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""
    for m, s in metrics['magic_stats'].items():
        content += f"| **{s['name']}** | `{m}` | {s['trades']} | `\\${s['net_profit']:.2f}` | {s['win_rate']}% | {s['profit_factor']} |\n"

    content += """
---

## 3. Breakdown by Traded Symbol

| Symbol | Trades | Net Profit | Win Rate |
| :--- | :---: | :---: | :---: |
"""
    for sym, s in metrics['symbol_stats'].items():
        content += f"| **{sym}** | {s['trades']} | `\\${s['net_profit']:.2f}` | {s['win_rate']}% |\n"

    content += """
---

## 4. Quantitative Recommendations
- **Risk Gate:** หาก Max Drawdown สูงเกิน 8% ให้ปรับลด Lot Size ลง 30% ทันที
- **EA vs Manual Evaluation:** เปรียบเทียบค่า Profit Factor ข้างต้น หากการเทรดมือมี Win Rate ต่ำกว่า EA ให้ปรับกลยุทธ์ตามสัญญาณของ EA Playbook
"""
    with open(md_path, mode="w", encoding="utf-8") as f:
        f.write(content)

def plot_equity_curve(metrics, chart_path):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("[WARN] matplotlib is not installed. Skipping equity curve plot.")
        return

    curve = metrics.get("equity_curve", [])
    if len(curve) < 2:
        print("[INFO] Not enough trades to plot equity curve.")
        return

    times = [pt[0] for pt in curve]
    equities = [pt[1] for pt in curve]

    # Calculate drawdown series
    peaks = []
    drawdowns = []
    curr_peak = 0.0
    for eq in equities:
        if eq > curr_peak:
            curr_peak = eq
        peaks.append(curr_peak)
        drawdowns.append(eq - curr_peak)

    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    fig.patch.set_facecolor('#09090b')
    ax1.set_facecolor('#121216')
    ax2.set_facecolor('#121216')

    # Top: Cumulative Net Profit
    line_color = '#10b981' if equities[-1] >= 0 else '#ef4444'
    ax1.plot(times, equities, color=line_color, linewidth=2.0, label='Net Cumulative Equity ($)')
    ax1.plot(times, peaks, color='#6366f1', linestyle='--', alpha=0.6, linewidth=1.2, label='High Water Mark')
    ax1.axhline(0, color='gray', linestyle=':', linewidth=0.8, alpha=0.7)
    ax1.set_title("MT5 Portfolio Cumulative Performance & Drawdown", fontsize=14, fontweight='bold', pad=12, color='#f4f4f5')
    ax1.set_ylabel("Profit / Loss ($)", fontsize=11, color='#a1a1aa')
    ax1.grid(True, color='#27272a', linestyle='--', alpha=0.5)
    ax1.legend(loc='upper left', frameon=True, facecolor='#18181b', edgecolor='#3f3f46')

    # Bottom: Drawdown
    ax2.fill_between(times, drawdowns, 0, color='#f43f5e', alpha=0.4, label='Drawdown ($)')
    ax2.plot(times, drawdowns, color='#f43f5e', linewidth=1.2)
    ax2.set_ylabel("Drawdown ($)", fontsize=10, color='#a1a1aa')
    ax2.set_xlabel("Trade Close Time", fontsize=11, color='#a1a1aa')
    ax2.grid(True, color='#27272a', linestyle='--', alpha=0.5)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(chart_path, dpi=160, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Equity curve saved to: {chart_path}")

def main():
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(args.output_dir, exist_ok=True)

    if args.demo_mock:
        print("[INFO] Running in --demo-mock mode (Synthetic Data)...")
        trades = generate_mock_deals()
    else:
        trades = fetch_mt5_deals(args.days, args.all, args.magic, args.terminal_path)

    if not trades:
        print("[WARN] No trades to analyze.")
        return

    metrics = compute_metrics(trades)

    md_filename = f"trading_journal_{timestamp}.md"
    csv_filename = f"trades_history_{timestamp}.csv"
    png_filename = f"equity_curve_{timestamp}.png"

    md_path = os.path.join(args.output_dir, md_filename)
    csv_path = os.path.join(args.output_dir, csv_filename)
    png_path = os.path.join(args.output_dir, png_filename)

    save_markdown(metrics, md_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    save_csv(trades, csv_path)
    print(f"[OK] Markdown Journal saved to: {md_path}")
    print(f"[OK] Trades CSV saved to: {csv_path}")

    if not args.no_chart:
        plot_equity_curve(metrics, png_path)

    print("\n--- Summary ---")
    print(f"Total Trades: {metrics['total_trades']} | Win Rate: {metrics['win_rate']}% | Net Profit: ${metrics['net_profit']}")
    print(f"Profit Factor: {metrics['profit_factor']} | Max Drawdown: ${metrics['max_drawdown_dollars']} ({metrics['max_drawdown_pct']}%)")

if __name__ == "__main__":
    main()
