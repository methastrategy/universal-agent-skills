# Reference Guide: 4-Horizon Multi-Objective Matrix Sweep & Regime-Adaptive Standards

## 1. Context & Motivation
การ Sweep และประเมินผล EA โดยใช้เพียงหน้าต่างเดียว (เช่น 3M Sprint) มีความเสี่ยงสูงต่อภาวะ Curve-Fitting / Overfitting เมื่อนำไปเทรดจริงจะล้มเหลวทันทีที่สภาวะตลาดเปลี่ยน
ระบบ MethaStrategy จึงกำหนดให้ใช้ **4-Horizon Multi-Objective Genetic Sweep** เป็นมาตรฐานหลักถาวร

---

## 2. The 4 Non-Overlapping Horizons (Recent 2 Years on XAUUSDm)

| Horizon ID | Calendar Range | Market Regime | Stress Test Focus |
| :---: | :---: | :--- | :--- |
| **H1** | `2026.01.15` - `2026.04.14` | ATH Super-Bull Breakout & Expansion | Trend Capturing & Compounding Growth |
| **H2** | `2025.07.01` - `2025.09.30` | Summer Chop & Tight Range | False-Break Defense & Drawdown Compression |
| **H3** | `2024.10.01` - `2024.12.31` | US Election & High-Impact Macro Pivot | Hard Stop, Volatility Shock & Margin Safety |
| **H4** | `2025.02.01` - `2025.05.01` | Mean Reversion & Liquidity Grabs | Reversion Accuracy & Liquidity Void Fill |

---

## 3. Regime-Adaptive Quality Gate (3x Compensation Rule)

1. **In-Regime Edge:**
   - ในสภาวะตลาดที่ EA ถนัด ต้องทำ **Profit Factor (PF) $\ge 1.80$**
   - กำไรสุทธิจากช่วงที่ถนัดต้องชดเชยการขาดทุนในตลาดที่ไม่ถนัดได้อย่างน้อย 3 เท่า:
     $$\text{Profit}_{\text{In-Regime}} \ge 3 \times |\text{Loss}_{\text{Off-Regime}}|$$
2. **Off-Regime Defense:**
   - ห้ามเกิด Margin Call / Stop Out แม้แต่ช่วงเดียวบนทุน $30.00 USD
   - Max Drawdown ของแต่ละช่วง 90 วัน ต้องไม่เกิน **30.0%**
3. **Composite Annual Profitability:**
   - ผลรวม 4 ช่วงสุทธิ $\sum_{i=1}^4 \text{PnL}_i > 0$
   - ค่าเฉลี่ย PF รวม 4 ช่วง $\ge 1.35$

---

## 4. Multi-Objective Genetic Fitness Function
เมื่อคอนฟิกรันบน MT5 Strategy Tester ในโหมด Genetic Multi-Objective ให้ใช้ฟังก์ชัน Composite Balance ควบคู่ Penalty Drawdown:
$$F = \text{Balance}_{\text{Composite}} \times \left(1 - \frac{\text{MaxDD}_{\text{Peak}}}{100}\right) \times \min(\text{PF}_{\text{avg}}, 3.0)$$
