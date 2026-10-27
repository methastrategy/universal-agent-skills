---
name: mql5-ea
description: "พัฒนา คอมไพล์ ตรวจสอบ และรันลูป MT5 EA — ใช้เมื่อต้องการเขียนหรือปรับโค้ด EA คอมไพล์ CLI และรันลูปปรับแต่งอัตโนมัติ (MQL5 EA lifecycle: development, CLI compilation, quant edge, backtest loop)"
---

# MQL5 Expert Advisor & Autonomous Matrix Lab (`/mql5-ea`)

ชุดเครื่องมือครบวงจรสำหรับการพัฒนา, ดีบัก, คอมไพล์, แบ็กเทสต์ และค้นหาพารามิเตอร์แบบ Multi-Objective Genetic Algorithm (4-Horizon Walk-Forward) ของ Expert Advisor (MQL5) บน MetaTrader 5 ทำงานแบบ Zero-Token 100% ภายในเครื่อง

---

## 1. Zero-Flag Intuitive Dispatch & Interactive Cockpit Gate

> [!IMPORTANT]
> **ผู้ใช้ไม่ต้องจำหรือพิมพ์ `--flag` ใดๆ ทั้งสิ้น**: ระบบจะจัดเส้นทางงานให้โดยอัตโนมัติ 2 ระดับ:
> 1. **Auto-Detect Intent (เมื่อสั่งพร้อมบริบท):** AI วิเคราะห์ข้อความและสั่งรันโหมดย่อยที่ถูกต้องทันที
> 2. **Interactive Cockpit Gate (เมื่อสั่งสั้นๆ หรือสั่ง `/mql5-ea` เปล่า):** AI จะเปิด `ask_question` Modal ให้คลิกเลือกทันที 1 วินาที

### A. Auto-Detection Matrix (ทำงานอัตโนมัติตามคำสั่ง)

| สิ่งที่ตรวจพบในข้อความ / บริบท | โหมดที่ระบบเลือกใช้อัตโนมัติ | คำสั่งเบื้องหลัง |
| :--- | :--- | :--- |
| **มีคำว่า "optimize", "GA", "จูน", "all-weather", "genetic"** | **Multi-Objective 4-Horizon GA** | `python scripts/matrix_lab/matrix_engine.py --multi-4h <EA> <TF>` |
| **มีคำว่า "ตรวจผล", "scorecard", "validate", "ประเมิน 4H"** | **4-Horizon Walk-Forward Scorecard** | `python scripts/matrix_lab/matrix_engine.py --validate-4h <EA> <TF>` |
| **มีคำว่า "sweep", "กวาดพารามิเตอร์", "matrix sweep"** | **Full-Dimensional Matrix Sweep** | `python scripts/matrix_lab/matrix_engine.py --full-sweep <EA>` |
| **มีคำว่า "คอมไพล์", "compile", "บิลด์", "ex5"** | **MetaEditor CLI Compilation** | MetaEditor CLI compile & log verification |
| **มีคำว่า "sync", "meahub", "อัปเดตเว็บ", "manifest"** | **MeaHub Manifest & Preset Sync** | `python scripts/matrix_lab/sync_manifest_4h.py` + vitest |

### B. Interactive Cockpit Gate (เมื่อพิมพ์สั่งสั้นๆ เช่น "รัน EA", "เทสหน่อย", หรือพิมพ์ `/mql5-ea` เปล่า)
AI ต้องไม่พิมพ์ถามกลับเป็นข้อความยาว แต่ต้องเรียกใช้เครื่องมือ `ask_question` ทันทีเพื่อให้ผู้ใช้คลิกเลือก:
1. `(Recommended) 🧬 Multi-Objective 4-Horizon GA (ค้นหาพารามิเตอร์ All-Weather ที่รอดทั้ง 4 สภาวะตลาด H1..H4)`
2. `⚡ Full-Dimensional 16-Core Matrix Sweep (กวาดพารามิเตอร์ทุกมิติผ่าน MT5 Agent Swarm)`
3. `🏆 Walk-Forward 4-Horizon Scorecard (ตรวจสอบผลงานข้าม 4 สภาวะตลาด H1, H2, H3, H4)`
4. `📊 Sync MeaHub Dashboard (อัปเดต Manifest + Presets + ตรวจสอบ Vitest)`

---

## 2. มาตรฐานการทดสอบ Walk-Forward 4-Horizon & Regime-Adaptive Gate

ทุกการทดสอบและ Optimize ต้องผ่าน 4 หน้าต่าง 90 วันไม่ทับซ้อนกัน บนทุน $30.00 USD (Leverage 1:1000):
- **H1 (Sprint ATH Breakout):** `2026.01.15` – `2026.04.14` (Super-Bull Expansion)
- **H2 (Summer Chop & Range):** `2025.07.01` – `2025.09.30` (Chop & False Breaks)
- **H3 (US Election Shock):** `2024.10.01` – `2024.12.31` (Macro Volatility & News)
- **H4 (Spring Mean Reversion):** `2025.02.01` – `2025.05.01` (Mean Reversion & Liquidity Void)

### เกณฑ์ตัดสินผ่าน (Regime-Adaptive Quality Gate):
1. **Consistency:** กำไรบวก $\ge 2 / 4$ ช่วง (หากได้ 4/4 ถือเป็นระดับ `All-Weather Champion`)
2. **3x Compensation Rule:** กำไรช่วงตามสเปกต้องชดเชยการขาดทุนช่วงนอกสเปก $\ge 3.0\times$
3. **Max Drawdown:** ไม่เกิน $30.0\%$ ในทุกหน้าต่าง และห้ามเกิด Margin Call เด็ดขาด
4. **Composite Performance:** กำไรรวม $\sum \text{PnL} > 0$ และ Average Profit Factor $\ge 1.35$

---

## 3. MetaEditor CLI Compilation Workflow

คอมไพล์ใน Tree ของ Terminal (`%APPDATA%\MetaQuotes\Terminal\<HASH>\MQL5\Experts\...`) เสมอ:
```powershell
& "C:\Program Files\MetaTrader 5\MetaEditor64.exe" /compile:"<abs .mq5>" /log:"<abs .log>"
```
- **ห้ามเชื่อ exit code:** ตรวจสอบจากบรรทัด `Result: 0 errors` ใน log UTF-16LE เท่านั้น
- **Log Path:** วางใต้ `%LOCALAPPDATA%\Temp\mt5c\` ห้ามมีช่องว่างเด็ดขาด
- **Sync Binary:** เมื่อคอมไพล์ผ่าน ให้คัดลอก `.ex5` กลับเข้า `experts/EA_METHA/` ทันที

---

## 4. มาตรฐานความปลอดภัยของโค้ด MQL5 (Robustness Invariants)

1. **Trade Execution Hardening:** กรองผ่าน `CJevExecutionGate` และตรวจ Bar-Level Execution Guard
2. **Deterministic Risk:** คำนวณ Lot Size ตาม ATR Stop Loss และ % Risk ห้าม Martingale หรือ Unhedged Grid
3. **Multi-Timeframe Isolation:** แยกตัวแปร `IsNewBar` ของแต่ละ Timeframe เด็ดขาด ป้องกัน Intra-Bar Bleed
4. **Resource Management:** ปล่อย Handle ตัวชี้วัดใน `OnDeinit()` ผ่าน `IndicatorRelease()` ทุกครั้ง

---

## 5. สถาปัตยกรรมอ้างอิง (Reference Map)

- **โมเดล Asymmetric High-Payoff และ Standalone EA:** อ่าน `references/standalone_asymmetric_payoff.md`
- **การค้นหาพารามิเตอร์ 4-Horizon GA:** อ่าน `references/multi_objective_sweep.md`
- **ระบบ Matrix Lab & Universal Engine:** อ่าน `references/autonomous-matrix-lab.md`
- **การทดสอบแบบชุดเบื้องหลังไม่เด้งจอ:** อ่าน `references/unattended-tester-batch.md`
- **การตรวจชันสูตรและกู้คืน EA เก่า:** อ่าน `references/legacy-ea-audit-protocol.md`
- **โมดูลตัวกรองความเสี่ยงก่อนส่งคำสั่ง:** อ่าน `references/pre-execution-gate-pattern.md`
- **การวิเคราะห์ความทนทานเชิงปริมาณ:** อ่าน `references/quant-robustness.md`
