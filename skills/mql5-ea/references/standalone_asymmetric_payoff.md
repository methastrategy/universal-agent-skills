# Standalone EA Architecture & Asymmetric High-Payoff Model

## 1. Standalone Independent System Invariant

### Core Philosophy
Every EA must stand on its own merits as an independent trading machine. 
- **Strict Prohibition on Portfolio Baskets:** Never combine, group, or pool multiple EAs together to compensate for individual weaknesses or drawdowns.
- **Evaluation Isolation:** Every backtest, optimization sweep, forward live demo, and risk audit must evaluate strictly **one EA at a time** (Single Standalone EA).

---

## 2. Micro-Capital Asymmetric High-Payoff Architecture ($30 USD Standard)

On retail micro accounts (e.g., $30.00 USD deposit, Leverage 1:1000, 0.01 lot fixed cap), conventional tight scalping ($1.50 SL, $2.00 TP) fails due to spread friction and gold volatility spikes. The **Asymmetric High-Payoff Model** flips the edge:

```
[Entry] ───► [+0.8R] ─────────────► [+1.5R] ─────────────► [3.5R - 4.0R]
   │          └─ Early BE Lock         └─ Dynamic Trailing      └─ Target TP
   │             (Zero Risk Free Runner)  (Ride Trend +$2 buffer)
   ▼
[-1.0R SL: $3.50 - $6.50 Structure]
   │
   ▼
[Emergency Hard Floor: Equity < $15.00] ──► Immediate Close All
```

### Key Parameter Specifications
1. **Natural Structure Stop Loss:**
   - Range: `$3.50` to `$6.50` USD (35 - 65 pips on Gold 0.01 lot).
   - Never clamp SL tighter than normal ATR(14) swing to avoid spread whipsaws.
2. **High R-Multiple Take Profit:**
   - Target: $\ge 2.5R$ to $4.0R$ (typically `$12.00` to `$25.00` USD on 0.01 lot).
3. **Early Break-Even Ratchet:**
   - Trigger: `+0.7R` to `+0.9R`.
   - Ratchet Stop Loss to `OpenPrice + 1-2 points` (Lock in breakeven, removing all risk).
4. **Dynamic Trailing Engine:**
   - Trail Activation: `+1.3R` to `+1.8R`.
   - Trail Distance: `$1.50` to `$2.50` USD trailing cushioning.
5. **Hard Account Equity Floor (Circuit Breaker):**
   - Line 1 of `OnTick()`:
     ```mql5
     if(AccountInfoDouble(ACCOUNT_EQUITY) < InpHardEquityStopUSD)
     {
         CloseAllCampaignPositions();
         return;
     }
     ```
   - Standard value: `$15.00` USD on `$30.00` capital (50% hard drawdown circuit breaker).
6. **Order Execution Safety:**
   - Dynamic Order Filling Mode detection (IOC / FOK / RETURN) via `SYMBOL_FILLING_MODE`.
   - Single concurrent position cap (`MaxPositions = 1`, 0.01 lot fixed, zero martingale, zero unhedged grid).

---

## 3. Walk-Forward Quality Validation

To pass institutional standards, standalone EAs must survive the 4 non-overlapping Walk-Forward Horizons (`H1..H4`):
1. **Regime Compensation ($3\times$):** Favorable regime profit $\ge 3 \times$ unfavorable regime losses.
2. **Zero Margin Calls:** Margin calls = 0 across all 4 horizons.
3. **Positive Composite PnL:** $\sum_{i=1}^4 \text{PnL}_i > 0$.

---

## 4. Sniper Expectancy Scoring & 3-Tier Quantitative Classification

### 4.1 Sniper Precision PTS Formulation
To evaluate EA precision, reward asymmetric edge, and penalize catastrophic failures, use the calibrated Sniper Alpha formulation:

$$\text{Expectancy Edge } E = (\text{WinRate} \times \text{PayoffRatio}) - (1 - \text{WinRate})$$

$$\text{PTS} = \text{Base}(100) + \Delta_{\text{Lifetime}} + \Delta_{\text{Recent}} + \Delta_{\text{Drawdown}} - \text{Penalties}$$

Key Calibration Invariants:
1. **Mathematical Expectancy Term:** Scales as $\Delta = 50 \times \tanh(E \times 0.7)$ across lifetime and recent trading windows.
2. **Profit Factor Boost:** Adds $+20 \times \min(\text{PF} - 1.0, 3.0)$ when $\text{PF} > 1.0$; applies severe dampening when $\text{PF} < 1.0$.
3. **Relaxed Linear Drawdown Scaling:** Benchmark set to $25\%$. Scaled linearly via $30 \times (1.0 - \text{PeakDD} / 25.0)$ capped at $+30$ to $-40$ pts, preventing binary cliff drops for viable EAs.
4. **Sample Size Guardrail:** If total trade sample $N < 30$, apply a $-25$ pts unverified sample penalty to suppress overfitting.
5. **Catastrophic Failure Floor:** If account suffered Margin Call or $\text{PeakDD} \ge 90\%$, apply hard $-100$ to $-200$ pts penalty, allowing scores to plunge into negative ranges (e.g. down to $-193.9$ pts).

### 4.2 3-Tier Classification Gating
- **`champ` ($\ge 150$ pts):** Institutional elite grade. Extreme multi-regime stability, zero margin call, strong edge.
- **`ready` ($\ge 100$ pts):** Production-ready grade. Positive expectancy edge, acceptable drawdown, validated on live micro accounts.
- **`dump` ($< 100$ pts):** Archive / unviable grade. Blown accounts, negative edge, or inadequate sample size.
