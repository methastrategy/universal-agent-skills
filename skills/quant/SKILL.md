---
name: quant
description: "วิเคราะห์ตลาดการเงิน หุ้น คริปโต ด้วย Multi-Agent Debate และ Data Pipelines — ใช้เมื่อต้องการวิเคราะห์หุ้น/เหรียญ ประเมินสัญญาณพื้นฐานและเทคนิค (Quantitative financial intelligence, multi-agent debate, data pipelines)"
---

# /quant — Quantitative Market Intelligence & Multi-Agent Financial Engine

ศูนย์กลางวิเคราะห์ตลาดการเงินเชิงปริมาณสำหรับ หุ้น, คริปโต, ทองคำ และดัชนี ผสานขุมพลัง **Multi-Agent Adversarial Debate** (Bullish, Bearish, Risk Arbiter จาก TradingAgents), **Data Pipeline Redundancy** (YFinance, AkShare, CCXT), และ **Jev Pre-Execution Gating** คืนค่าผลการตัดสินใจแบบมีโครงสร้างตัวเลขชัดเจน

---

## สถาปัตยกรรมอ้างอิง (Reference Map)
- **การถกเถียงคานอำนาจ 3 ฝ่าย:** อ่าน `references/multi-agent-debate.md` (Bullish Advocate vs Bearish Skeptic vs Risk Arbiter Judge)
- **ระบบท่อส่งข้อมูลและตั้งระบบรันอัตโนมัติ:** อ่าน `references/data-pipelines-and-automation.md` (Data Redundancy, GitHub Actions Cron)
- **สถาปัตยกรรมบอทเทรด Python & Signal Gate:** อ่าน `references/python-strategy-engine.md` (Freqtrade, CCXT, QuantDinger V2 Lifecycle)
- **คู่มือสเปก 6 กลยุทธ์เชิงปริมาณ:** อ่าน `references/quantitative-strategy-playbook.md` (SMC Sweep, FVG Retest, Asian Breakout, EMA Pullback, Bollinger Squeeze)
- **สคริปต์ดึงประวัติ MT5 Trading Journal & พล็อตกราฟ:** เรียกใช้ `scripts/mt5_journal.py` (แยก Magic Number, Win Rate, Profit Factor, Equity Curve PNG)
- **โมดูลประมวลผลประวัติเทรด Zero-Dependency:** เรียกใช้ `scripts/trade_processor.py` (Pure Python: Chunking, GroupBy Magic/Symbol/Session, DD)
- **ดัชนีวัดผลงานและความเสี่ยงระดับสถาบัน:** อ่าน `references/institutional-risk-metrics.md` ( Sortino, Calmar, Omega, Daily VaR/CVaR 99% Tail Risk )
- **การคัดกรอง Alpha Factor ด้วย IC/IR:** อ่าน `references/factor-evaluation-ic-ir.md` ( Spearman Rank IC, ICIR Consistency, Quantile Monotonicity )
- **สถิติอนุพันธ์และการเทรดคู่สินทรัพย์:** อ่าน `references/statistical-arbitrage-cointegration.md` ( Engle-Granger Cointegration, Spread Z-Score, Half-Life )

---

## 3 มิติการวิเคราะห์เชิงปริมาณ (The 3-Dimensional Analysis Protocol)

### 1. การสกัดข้อมูลและคำนวณอินดิเคเตอร์ (Data & Technical Signal Engine)
- ดึงข้อมูลราคาและงบการเงินผ่าน Data Redundancy Cascade (YFinance $\rightarrow$ AkShare/Tushare $\rightarrow$ CCXT)
- คำนวณอินดิเคเตอร์หลัก:
  - **Trend**: EMA 20, 50, 200 (Golden Cross / Death Cross / Alignment)
  - **Momentum**: RSI 14 (Overbought/Oversold และ Regular/Hidden Divergence)
  - **Volatility & Bands**: Bollinger Bands (Squeeze vs Expansion) และ ATR Multiplier สำหรับ Stop-Loss
  - **Volume & Institutional Footprint**: On-Balance Volume (OBV) และ Volume Spike (> 2.5× ค่าเฉลี่ย 20 วัน)

### 2. กระบวนการถกเถียง 3 ฝ่าย (Multi-Agent Adversarial Debate)
เพื่อป้องกันอคติ ให้แบ่งบทบาทการวิเคราะห์ออกเป็น 3 ฝ่าย:
1. **Bullish Advocate**: นำเสนอ Catalyst ข่าวดี การเติบโต และโมเมนตัมขาขึ้น (3 ข้อหลัก)
2. **Bearish Skeptic**: โจมตีจุดอ่อน หนี้สิน Valuation ตึงตัว และ Divergence ขาลง (3 ข้อหลัก)
3. **Risk Arbiter & Judge**: ชั่งน้ำหนักหลักฐานและตัวเลข ตัดสินอย่างเป็นกลางด้วย LLM-as-a-Judge

### 3. ผลลัพธ์แบบ Structured Decision Gating (Quantitative Score)
- **Quantitative Score**: `-100` (Extreme Bearish) ถึง `+100` (Extreme Bullish)
- **Confidence Gating ($P \ge 0.85$):** ประเมินความมั่นใจเชิงประพจน์ หาก $P < 0.85$ บังคับปรับเป็น `NEUTRAL_HOLD` ทันที
- **Action Recommendation**: `STRONG_BUY` | `ACCUMULATE` | `NEUTRAL_HOLD` | `TRIM_POSITION` | `STRONG_SELL`
- **Asymmetric Risk/Reward**: อัตราส่วนผลตอบแทนต่อความเสี่ยง (RRR) ต้อง $\ge 1:2$ เสมอจึงจะแนะนำ Entry
- **Hard Invalidation**: ระบุจุดตัดขาดทุน (Stop-Loss / Invalidation Price) ที่ชัดเจนทุกครั้ง

### 4. การทดสอบแบบ Multi-Parameter Grid Sweep (`--sweep`)
- เมื่อได้รับโจทย์ทดสอบพารามิเตอร์หลากหลาย (เช่น RSI 7, 9, 14 $\times$ TF M5, M15, H1) หรือมี Flag `--sweep`:
- **Ranked Scorecard Matrix:** เจนตารางเปรียบเทียบผลลัพธ์ลงในแชตโดยตรง เรียงลำดับตาม Expectancy / Profit Factor
- **Top 3 Actionable Picks:** สรุปชี้เป้า 3 อันดับพารามิเตอร์ที่ทนทานต่อข้อมูลนอกกลุ่มตัวอย่าง (Out-of-Sample) สูงสุดให้ผู้ใช้นำไปใช้งานได้ทันที

### 5. กฎเหล็กพรมแดนการเทรด (Anti-Vibe Trading & Execution Boundary Invariant)
- **Zero Prompt-to-Broker Execution:** ห้ามปล่อยให้ LLM ตัดสินใจเปิดออเดอร์ในตลาดจริงโดยตรงเด็ดขาด การวิเคราะห์ทั้งหมดของ `/quant` ต้องทำหน้าที่เป็นเพียง Decision Support เท่านั้น
- **Deterministic Broker Seam:** การเปิดออเดอร์อัตโนมัติบนพอร์ตจริง ต้องผ่านโค้ด MQL5/C++ ที่คอมไพล์แล้ว มี Hard Stop Loss, Max Drawdown Guard ($\le 5\%$), และตรวจสอบ Slippage/Spread ในระดับไมโครสตรักเจอร์เท่านั้น

---

## รูปแบบการเรียกใช้งาน (Invocation Patterns)

| รูปแบบ | ตัวอย่างคำสั่ง | ผลลัพธ์ที่ได้ |
| :--- | :--- | :--- |
| **`/quant [ticker]`** | `/quant NVDA` หรือ `/quant BTC/USDT` | รัน Multi-Agent Debate และออกรายงาน Quantitative Score |
| **`/quant --sweep [ticker]`** | `/quant --sweep XAUUSD` | รัน Grid Search Matrix เปรียบเทียบหลาย Indicator/TF พร้อมตาราง Ranked Scorecard |
| **`/quant [เปรียบเทียบ]`** | `/quant เปรียบเทียบ AAPL vs MSFT` | วิเคราะห์เปรียบเทียบ 2 สินทรัพย์แบบ Head-to-Head |
| **ภาษาธรรมชาติ** | "ช่วยวิเคราะห์สัญญาณทางเทคนิคและงบการเงินของ PTT" | Agent เรียกใช้สกิล `/quant` ประมวลผลทันที |
