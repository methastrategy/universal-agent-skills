# Institutional Risk Metrics & Tear Sheet Analytics

คู่มือสูตรคณิตศาสตร์และเกณฑ์การวัดผลงานการเทรดระดับสถาบันการเงิน (ดัดแปลงจากโมเดลของ `Pyfolio`, `Empyrical`, และ `QuantConnect LEAN`) เพื่อก้าวข้ามการดูแค่ Win Rate หรือ Sharpe Ratio แบบผิวเผิน สู่การวิเคราะห์ความเสี่ยงส่วนหาง (Tail Risk) และประสิทธิภาพของเงินทุนที่แท้จริง

---

## 1. ข้อจำกัดของ Traditional Metrics (ทำไม Win Rate และ Sharpe ถึงหลอกตา)

1. **Win Rate Mirage**: ระบบที่มี Win Rate 90% อาจล้างพอร์ตได้ในไม้เดียวหากมีปัญหา Asymmetric Loss (ได้ทีละนิด เสียทีละก้อนโต)
2. **Sharpe Ratio Symmetrical Penalty**: Sharpe Ratio คิดความผันผวนขาขึ้น (Upside Volatility) เป็นความเสี่ยงเท่ากับขาลง ทั้งที่ความผันผวนขาขึ้นคือกำไร
3. **Tail Risk Blindness**: ไม่สามารถบอกได้ว่าในวันที่เลวร้ายที่สุด 1% ของตลาด (Black Swan Event) พอร์ตจะสูญเสียเงินสูงสุดเท่าใด

---

## 2. 5 ดัชนีวัดผลงานระดับสถาบัน (The Institutional Quintet)

### 1. Sortino Ratio (ประเมินเฉพาะความผันผวนขาลง)
ประเมินผลตอบแทนส่วนเกินเทียบกับ Downside Deviation เท่านั้น โดยไม่ลงโทษกำไรขาขึ้น:

$$\text{Sortino Ratio} = \frac{R_p - R_f}{\sigma_d}$$

- $R_p$: อัตราผลตอบแทนของพอร์ตการลงทุน
- $R_f$: อัตราผลตอบแทนไร้ความเสี่ยง (Risk-Free Rate)
- $\sigma_d$: Downside Standard Deviation (คำนวณเฉพาะผลตอบแทนที่เป็นลบ)
- *เกณฑ์สถาบัน:* $> 1.5$ (ยอมรับได้), $> 2.0$ (ยอดเยี่ยม)

### 2. Calmar Ratio (อัตราส่วนผลตอบแทนต่อการติดลบสูงสุด)
วัดความสามารถในการสร้างผลตอบแทนรายปีเทียบกับ Max Drawdown ในอดีต:

$$\text{Calmar Ratio} = \frac{\text{Annualized Return}}{|\text{Max Drawdown}|}$$

- *เกณฑ์สถาบัน:* $> 2.0$ (ดีมาก), $> 3.0$ (ระดับ Hedge Fund ชั้นนำ)

### 3. Omega Ratio (การแจกแจงผลตอบแทนแบบไม่สมมาตร)
พิจารณาทุก Moment ของผลตอบแทน (Skewness และ Kurtosis) โดยไม่ต้องสมมติว่าเป็นการแจกแจงแบบปกติ (Normal Distribution):

$$\Omega(L) = \frac{\int_L^\infty (1 - F(r)) \, dr}{\int_{-\infty}^L F(r) \, dr}$$

- เปรียบเทียบพื้นที่กำไรสะสมเหนือเกณฑ์ $L$ กับพื้นที่ขาดทุนสะสมใต้เกณฑ์ $L$

### 4. Value-at-Risk (VaR 95%) & Conditional VaR (CVaR 99% / Expected Shortfall)
- **VaR 95%**: ตัวเลขขาดทุนสูงสุดที่คาดว่าจะเกิดขึ้นด้วยระดับความเชื่อมั่น 95% ในกรอบเวลา 1 วัน
- **CVaR 99% (Expected Shortfall)**: ค่าเฉลี่ยของความเสียหายที่จะเกิดขึ้นจริง **เมื่อพอร์ตหลุดเข้าสู่เขตวิกฤต 1% ที่เลวร้ายที่สุด**:
  $$\text{CVaR}_\alpha = \mathbb{E}[R \mid R \le \text{VaR}_\alpha]$$
- *เกณฑ์สถาบัน:* CVaR 99% ต้องไม่เกินเพดาน Risk per Day ของกองทุน (เช่น ไม่เกิน 3.0% ของ Equity)

---

## 3. โครงสร้างรายงาน Tear Sheet ประจำสัปดาห์

```text
================ INSTITUTIONAL PERFORMANCE TEAR SHEET ================
Period: 2026-01-01 to 2026-10-15 | Capital: $100,000.00
----------------------------------------------------------------------
Total Closed Trades      : 248         | Win Rate             : 62.1%
Cumulative Net Return    : +38.4%      | Annualized Return    : +48.2%
Max Drawdown (Daily Close): -6.4%      | Max DD Duration      : 14 Days
----------------------------------------------------------------------
Sharpe Ratio (Rf=3.5%)   : 2.14        | Sortino Ratio        : 3.42
Calmar Ratio             : 7.53        | Omega Ratio (L=0%)   : 1.88
Daily VaR (95%)          : -0.85%      | Daily CVaR / ES (99%): -1.65%
Profit Factor            : 2.18        | Payoff Ratio (Win/Loss): 1.34
======================================================================
```
