# Fractals & Structural Turning-Point Detection (MT5)

How to use MT5's built-in Fractals as an objective structure detector, what it is worth, and how not to waste a week on the obvious (wrong) usage. Labs: `scripts/research_lab/fractal_lab.py`, `scripts/research_lab/fractal_sweep_lab.py`.

---

## 1. Mechanics that decide everything

- Standard mark is the **5-bar Bill Williams fractal**: `high[i]` is the strict maximum of `high[i-2 .. i+2]` (up mark), mirror for lows.
- MT5 only **confirms** the mark **2 bars after** the extreme, and it **repaints** the last 2 bars. Any EA reading `iFractals(..., shift 0 or 1)` is reading a value that can disappear — read shift ≥ 2 only.
- Because of that lag, entering on the confirmation bar means entering 2 bars late while the stop must sit beyond the wick: late entry + widest stop, the worst combination available.
- Fractal density is a free, non-repainting regime read: marks every ~2–3 bars = trend; wide spacing = chop.

## 2. Measured value as a turning-point detector (XAUUSDm, 2024-2026)

"Mark followed by a ≥1 ATR move in the reversal direction within 24 bars":

| TF | swing-high mark | random bar | swing-low mark | random bar |
|---|---|---|---|---|
| M15 | 72.2% (n≈8.9k) | 60.4% | 74.7% | 65.9% |
| H1 | 70.5% (n≈2.2k) | 59.6% | 76.7% | 68.4% |

The **location** carries +10–12 points over a random bar. The mark is information; the confirmation timing is not.

## 3. Fading the confirmation bar — measured, does not pay

Entry at the close of the confirmation bar, stop beyond the wick + 0.15 ATR, TP at R multiples: **−0.14R to −0.16R** on M15 and H1 at RR 1.0–2.0; only H1 "buy the swing low at 2R" reached +0.074R and still failed a calendar year. Adding CCI divergence on top made it worse, so divergence is not the missing filter.

## 4. The structural version that does pay — sweep and reclaim

Event: a bar trades beyond a confirmed level (sweep), then closes back through it within N bars (reclaim).

```
level  = last confirmed swing high/low
sweep  = a later bar's high > level (short side) / low < level (long side)
reclaim= close back through the level within N bars (N = 3 works best here)
entry  = LIMIT at the level  (not the reclaim close)
stop   = 0.30 ATR beyond the level  (not beyond the sweep extreme)
target = 3R
```

Measured (XAUUSDm, spread $0.30 deducted, 36 variants per TF):

| TF | side | n | hit | expectancy | 2024 | 2025 | 2026 | max loss streak |
|---|---|---|---|---|---|---|---|---|
| H1 | long | 389 | 29.1% | **+0.162R** | +0.270 | +0.135 | +0.082 | 14 |
| M15 | long | 1,779 | 27.2% | **+0.088R** | + | + | + | — |
| H1 | short | 488 | 25.8% | +0.033R | −0.099 | +0.050 | +0.197 | 18 |

Two levers produced the entire improvement: **limit entry** (removes the 2-bar lag) and **stop beyond the level, not the sweep extreme** (halves the stop). Confirmation entry with the wide stop is negative in every variant.

## 5. Caveats to carry into any report

- **Bull-market bias:** only the long side is consistent, and gold rose through most of the sample. "Buy the swept low" may be beta; a bear-regime window is not in the data and must be stated as missing.
- **Multiple testing:** 36 variants per timeframe — one surviving family is expected by chance at this scale. Walk-forward before it becomes an EA.
- **14 consecutive losses** at 3R ⇒ risk per trade ≤0.3% ⇒ minimum capital ≈ DD$/0.30; a $30 gold account is excluded by the arithmetic in `signal-validation-and-oos-gates.md` §1.1.

## 6. Building an EA from a structural detector

1. Maintain the level list from confirmed fractals only (`shift ≥ 2`), one active level per direction.
2. Place **pending limit orders** at the level (with expiry); do not wait for a reclaim close.
3. Stop beyond the level by a fixed ATR fraction; target as an R multiple.
4. Add the fractal-spacing regime filter as a switch, not as an entry condition.
5. Re-run the lab tables after ANY geometry change — at 27–29% hit rate the 3R target is the whole edge, and moving TP by 0.5R flips the sign.
