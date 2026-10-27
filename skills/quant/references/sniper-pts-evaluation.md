# Quantitative Expectancy Scoring & 3-Tier Edge Governance

## 1. Mathematical Expectancy Formulation

In quantitative evaluation of algorithmic trading systems (EAs), raw win rate or profit factor in isolation is vulnerable to selection bias and curve fitting. The **Sniper Expectancy Formulation** computes true per-trade edge:

$$\text{Expectancy } E = (\text{WinRate} \times \text{PayoffRatio}) - (1 - \text{WinRate})$$

Where:
- $\text{WinRate} \in [0, 1]$: Total winning trades / Total trades
- $\text{PayoffRatio} = \frac{\text{Average Win}}{\text{Average Loss}}$

### Multi-Horizon Composite Formulation

$$\text{PTS} = \text{Base}(100) + \Delta_{\text{Lifetime Expectancy}} + \Delta_{\text{Recent Momentum}} + \Delta_{\text{Drawdown Resilience}} - \sum \text{Penalties}$$

1. **Lifetime Alpha ($\Delta_{\text{Lifetime}}$):**
   $$\Delta_{\text{Lifetime}} = 50 \times \tanh(E_{\text{Lifetime}} \times 0.7)$$
   Ensures smooth asymptotic bounds between $[-50, +50]$.

2. **Recent Horizon Alpha ($\Delta_{\text{Recent}}$):**
   Evaluates recent 7D/30D trading performance.
   $$\Delta_{\text{Recent}} = 30 \times \tanh(E_{\text{Recent}} \times 0.7)$$

3. **Profit Factor Boost:**
   $$\Delta_{\text{PF}} = 20 \times \min(\text{PF} - 1.0, 3.0) \quad \text{if } \text{PF} \ge 1.0$$
   $$\Delta_{\text{PF}} = -40 \times (1.0 - \text{PF}) \quad \text{if } \text{PF} < 1.0$$

4. **Relaxed Linear Drawdown Scaling ($\Delta_{\text{Drawdown}}$):**
   Using a benchmark $\text{DD}^* = 25.0\%$:
   $$\Delta_{\text{DD}} = 30.0 \times \left(1.0 - \frac{\text{PeakDD}}{25.0}\right)$$
   Clamped between $[-40.0, +30.0]$.

5. **Sample Size & Failure Penalties:**
   - Small Sample ($N < 30$ trades): $-25$ pts
   - Micro Sample ($N < 10$ trades): $-45$ pts
   - Blown / Margin Call ($\text{PeakDD} \ge 90\%$): $-100$ pts hard penalty (permitting scores down to negative)

---

## 2. 3-Tier Quantitative Classification Gate

| Tier | Score Range | Expected Characteristics | Action / Recommendation |
| :---: | :---: | :--- | :--- |
| **`champ`** | $\ge 150$ pts | Top-elite alpha, multi-horizon consistency, DD $\le 10\%$, positive expectancy across all stress regimes | Primary live capital candidates |
| **`ready`** | $100 \text{ to } 149$ pts | Solid statistical edge, controlled risk profile, verified live micro trades | Deployable on live micro accounts ($30–$100) |
| **`dump`** | $< 100$ pts | Sub-benchmark edge, elevated drawdown, small sample size, or blown margin | Archive / Quarantine; requires parameter re-engineering |

---

## 3. Data Integrity & Multi-Period Fallback Invariant

When aggregating quantitative metrics across multiple horizons (e.g. `last_1w` vs `last_5td`):
- **Empty-Object Shadowing Bug:** In JavaScript/TypeScript, `{}` is truthy, so `obj1 ?? obj2` fails to fall back to `obj2` when `obj1` is `{ total_trades: 0 }`.
- **Validation Invariant:** Always enforce `(window?.total_trades ?? 0) > 0` before accepting a period's metrics.
