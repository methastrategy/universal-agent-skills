# Institutional Quant Robustness & Edge Validation Protocol

Methodologies and statistical standards for validating algorithmic strategies and Expert Advisors (EA), derived from **Marcos López de Prado (Advances in Financial Machine Learning)**, **Stefan Jansen (Machine Learning for Trading)**, **QuantDinger v5 Architecture**, and **Hummingbot Execution Dynamics**.

---

## 1. Multiple Testing & Deflated Sharpe Ratio (DSR)

When an algorithmic strategy or EA is discovered by testing hundreds of parameter variations or indicators, standard Sharpe Ratio is heavily inflated by **Selection Bias (Data Snooping)**.

### 1.1 The Haircut & Deflated Sharpe Ratio (DSR)
DSR computes the probability that the estimated Sharpe Ratio exceeds what could be achieved purely by random luck across $N$ independent trials:

$$DSR = P\left[\widehat{SR} > SR_0 \mid \{SR_k\}_{k=1}^N\right]$$

Key inputs:
- $\widehat{SR}$: Annualized Sharpe Ratio of the chosen strategy.
- $N$: Total number of backtest runs / parameter combinations explored.
- $\sigma_{SR}$: Variance of Sharpe ratios across all tested trials.
- $\gamma_3, \gamma_4$: Skewness and Kurtosis of the strategy return distribution (penalizing fat tails and left-side crashes).
- $T$: Track record length (number of observed trading bars).

> [!IMPORTANT]
> **DSR Invariant:** An EA strategy is only certified as having an institutional statistical edge if its **Deflated Sharpe Ratio $\ge 0.95$ (95% confidence)**. Any strategy passing traditional backtests with $DSR < 0.90$ must be flagged as **Overfitted Artifact**.

---

## 2. Combinatorial Purged & Embargoed Cross-Validation (CPCV)

Traditional K-Fold CV fails in financial time series due to serial correlation and trade overlap leakage.

### 2.1 Purging (ลบข้อมูลเหลื่อม)
- In continuous trading, a position entered at bar $t$ may close at $t+h$. The label / return depends on future bars.
- **Purging Rule:** Remove all training samples whose evaluation window overlaps with the test set's entry-to-exit horizon to guarantee zero lookahead leakage.

### 2.2 Embargoing (เว้นวรรคหลังเหตุการณ์)
- Financial volatility clusters in regimes (Autoregressive conditional heteroskedasticity).
- **Embargo Rule:** Enforce an embargo buffer (e.g., 1–5% of sample size) immediately following the testing period before training data resumes, preventing post-trade regime spillover.

---

## 3. Microstructure & Execution Friction Modeling

Real-market execution differs drastically from naive backtests due to market microstructure friction.

### 3.1 News & Toxic Spread Widening
- Never assume fixed spreads (e.g., 15 points on Gold/EURUSD).
- Model dynamic spread multipliers during liquidity vacuums:
  - Asian Session Rollover (21:00 - 23:00 UTC): Spread widens $2.5\times - 5.0\times$.
  - High Impact News (CPI, NFP, FOMC): Spread spikes $5.0\times - 10.0\times$ with intermittent requotes.
  - Hard Invariant: EA must automatically widen Slippage tolerance or halt new order placement during pre-scheduled high-impact news windows.

### 3.2 Asymmetric Slippage Skew
- Slippage is non-linear and asymmetrical: adverse slippage occurs on breakout fills, while favorable slippage rarely offsets it.
- Model stress-test slippage as:
  $$\text{Effective Fill Price} = P_{\text{signal}} + \text{Sign}(\text{Dir}) \times \left(\text{Base Spread} + \text{Slippage Skew} \times \frac{\sigma_{\text{recent}}}{\sigma_{\text{baseline}}}\right)$$

---

## 4. Information Coefficient (IC) & Alpha Decay Tracking

Monitor signal degradation over rolling windows to detect structural regime breakdown before capital depletion:
$$\text{IC}_t = \text{Corr}\left(\text{Signal}_t, \text{Forward Return}_{t+h}\right)$$
- $\text{IC} > 0.05$: Viable alpha engine.
- $\text{IC} \in [0.01, 0.05]$: Moderate predictive capacity (requires low execution turnover).
- $\text{IC} < 0.01$: Degraded noise; trigger automatic execution circuit breaker.

---

## 5. Block-Bootstrap Monte Carlo Simulation (Anti-Serial Correlation)

Standard IID trade shuffling breaks the underlying volatility clustering and sequential market regimes.
- **Block-Bootstrap Rule:** Resample trade returns in blocks of $k$ consecutive trades ($k \in [5, 15]$) across 3,000–5,000 iterations.
- **Stress Metrics:**
  - `Median Max Drawdown` (50th percentile)
  - `Severe Stress Drawdown` (95th percentile)
  - `Tail Risk Extreme Drawdown` (99th percentile)
  - `Probability of Ruin (PoR)`: Probability of equity dropping below hard margin stop-out.

---

## 6. TPE Parameter Evolution & Transaction-Cost Stress Testing

- **TPE (Tree-structured Parzen Estimator):** Replace naive grid-search with Bayesian non-parametric density estimation to explore parameter spaces efficiently without dense overfitting.
- **Fixed Friction Baseline (QuantDinger Standard):**
  - All strategy backtests must be subjected to a stress run applying **0.05% commission on executed notional** and **0.05% adverse slippage on every fill**.
  - If the Net Profit shrinks by $> 50\%$ or Sharpe drops by $> 40\%$ under this friction, the strategy lacks structural edge and is declared unfit for live execution.
