# Signal Validation & OOS Gates

Practical gates for judging whether an indicator/EA actually has edge — applies to fleet screens, single-EA validation, and signal-level research. Statistical theory lives in `quant-robustness.md`; this file is the operational checklist.

---

## 1. Deposit discipline (the most common misread)

At fixed lot size, per-trade PnL in USD is roughly constant. A small deposit therefore caps *total* profit: once cumulative loss reaches the deposit, the account is liquidated and the rest of the window contributes zero. Two consequences:

- **Never compare PnL across deposit levels.** A $30 account "earning" $40 and a $10,000 account earning $40 are not the same strategy; the small one was truncated.
- **Judge edge at deposit ≥ $1,000** with lot 0.01. Report **DD in both $ and %**: DD$ stays constant while DD% scales inversely with deposit. Minimum viable deposit ≈ `DD$ / 0.30`.

**Ruin signature:** cumulative result ≈ negative of the deposit (e.g. −$30 on a $30 account). Read that as *account blown*, not *strategy loses money* — the measurement instrument failed, not the strategy. On gold at 0.01 lot a normal single loss is ≈ $16, which is 55% of a $30 account; a $30 deposit cannot measure edge at all.

When a fleet screen shows most candidates at exactly "deposit × −1", re-run the screen at the higher deposit before drawing any conclusion about which EAs work.

### 1.1 Capital feasibility — decide this BEFORE any parameter sweep

Some account/instrument combinations cannot carry any strategy, so sweeping them burns days and returns noise. Compute four numbers first and stop if they fail:

1. **Contract risk:** XAUUSDm 0.01 lot = 1 oz ⇒ a $1 gold move is $1 of P&L. (FX 0.01 lot = 1,000 units ⇒ a 10-pip stop ≈ $1.)
2. **Stop-vs-noise ratio:** max allowed risk (e.g. 3% of $30 = $0.90) expressed in ATR. Gold H1 ATR(14) 2024-2026: p10 $4.97, median $9.49 ⇒ a $0.90 stop is **0.09 ATR**.
3. **Noise stop-out rate:** random entry, $1.00 adverse move within 96 H1 bars ⇒ **98.1%** of cases. A stop under ~0.3 ATR is decided by noise, not by the signal.
4. **Cost share:** spread $0.30 is 33% of a $0.90 stop and 3.2% of median ATR — a third of the risk budget is paid before the trade starts.

If (2) lands below ~0.3 ATR or (4) above ~10%, the answer is **not more tuning**: report it as structurally impossible and name the capital floor (`DD$ / 0.30`), a cent account (0.01 lot = 0.01 oz, risk ≈ $0.14 of a 3,000-cent balance), or a cheaper instrument. Measured on gold: 90 precision-filter configurations at $0.60–$1.00 stops produced **0 profitable configs in any year**, with 46–106 consecutive losses — entry precision moved hit rate by tenths of a percent, not by tens.

**Corollary:** precision filters cannot rescue a stop that sits inside the spread-plus-noise band. When a defensive sweep returns all-negative with tiny variance across filters, stop filtering and fix the sizing/contract constraint instead.

**Ruin arithmetic to quote in the report:** average loss per losing trade ÷ deposit. Measured: $11.76 on $30 (39% ⇒ 3 consecutive losses ends the account) and $19.87 on $30 (66% ⇒ 2 losses). Green windows from such configs are early-compounding artefacts, not robustness.

---

## 2. In-sample vs OOS boundary

Any window used to pick parameters (entry logic variants, indicator settings, filters, lot) is **in-sample**, no matter how many windows there are. Four horizons of the same instrument are four in-sample views, not four independent tests.

- **Mandatory:** one OOS window strictly outside the tuning range (e.g. tuning 2019–2023 → OOS `2024.01.01–2025.04.01`), run with the frozen preset.
- **Pass gate:** profit > 0, PF ≥ 1.10, DD ≤ 30%, trades ≥ 100.
- **Anchored walk-forward** when the sample is long enough: 3+ folds, each fit on prior data only, gate on the concatenated OOS segments.

### 2.1 Walk-forward recipe that has worked here

```
IS = 6 months, OOS = next 3 months, roll +3 months, repeat to the end of data
per fold : run the whole parameter grid on IS only, pick best IS config
           (require IS profit > 0; score = profit − 2×DD)
           trade that exact config on the untouched OOS segment
           if no IS config is profitable -> stand aside (zero trades) for that OOS
report   : each fold's chosen config + OOS PnL, stitched OOS equity,
           positive-window ratio, worst window, and the best FIXED geometry over
           the full period as the baseline
```

Two properties make this worth the runtime: (a) the selection is mechanical, so no hand-picked geometry survives on the same windows used to judge it; (b) standing aside is itself a real signal — folds that skip because the IS edge was negative are what keep the drawdown low. Measured example: +$1,267 stitched OOS on $1,000 with 6/7 windows positive and worst window −$37, versus a best fixed geometry at +$1,113 that carried 56% drawdown.

Walk-forward is not a Champion gate by itself: it lives on the same data that produced the earlier in-sample windows, so pair it with the OOS gate above and say which windows overlapped. A walk-forward that beats the fixed baseline on profit *and* drawdown is evidence; one that only beats it on profit is fold luck.

### Curve-fit signature

| Pattern | Reading | Action |
|---|---|---|
| In-sample passes 3/3, OOS negative every config | Overfit to regime | Mark `dump`, stop tuning |
| In-sample 2/3, OOS marginal positive | Fragile but real | Keep `lab`, no Champion |
| In-sample 2/3+, OOS ≥ gate | Credible | Eligible for Champion review |
| OOS great, in-sample weak | Suspect window luck | Re-run on a third window |

**Once a window is used for OOS, never tune on it.** Touching it converts it to in-sample and destroys the only unbiased measurement you have. If a change is needed, find a fresh forward window.

---

## 3. Pipeline order (do not skip stages)

1. **Screen** — 3 horizons per EA, cheap configs, deposit high enough to avoid truncation.
2. **Dedupe** — normalize comments / `#property` / string literals / magic numbers and hash the body; identical logic means one representative, the rest get `duplicate_of`.
3. **Signal harness** — test the raw signal (entry on bar close, fixed hold, ATR-relative TP/SL, next-bar entry to avoid look-ahead) before writing EA code. It isolates "does the signal predict direction" from "is the EA plumbing correct".
4. **Build the EA** — only for signals that survived the harness.
5. **OOS / walk-forward** — gate before Champion.

Skipping stage 2 inflates every downstream count; skipping stage 3 means EA bugs and signal weakness get conflated in the same report.

### Dedupe normalization recipe

Strip before hashing: line comments and block comments, `#property ...` lines, all string literals (EA display names differ per clone), and numeric magic constants in `OrderSend`/trade calls. Hash what remains. A 80-file library commonly collapses to ~57 unique bodies with 13 clone groups — dedupe before reporting "N EAs tested", or the same logic gets counted five times.

---

## 4. Signal harness metrics

Run per timeframe, per instrument, report the whole table rather than one number:

- **Win rate** — raw directional hit rate; baseline is 50% for symmetric setups.
- **Expectancy (R)** — mean outcome in R units where 1R = the ATR-based stop distance. Gate: > 0.05R after costs.
- **Profit factor** — gross win / gross loss.
- **Max adverse excursion** — how deep the trade goes against before resolving; sets the stop distance and reveals whether the stop is inside noise.
- **Trade count** — below ~100 per cell the metrics are noise; widen the window or drop the cell.

Include spread/commission in the harness. A signal that only works at zero cost is not a signal.

---

## 5. Reporting rules

- Every claim of "pass" carries the actual metric line from the report — no verdict without the numbers.
- Per-EA findings go to `reports/<EA>_<TF>_FINDINGS.md`; keep one row per EA per timeframe so later sessions can diff against it.
- State the deposit, lot, and window in the finding itself. A result without its capital context is unreadable six months later.
