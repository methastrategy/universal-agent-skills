---
name: ea-audit
description: "วิเคราะห์รายงาน Backtest MT5 เจาะลึก 5-Vector REA และรันลูปปรับแต่งพารามิเตอร์อัตโนมัติในพื้นหลัง (MT5 EA Backtest Forensic Audit, Bayesian Loop)"
---

# MT5 EA Backtest Forensic Audit & Optimization Lab (`/ea-audit`)

ชุดเครื่องมือสกัดผลการทดสอบ Backtest ของ MetaTrader 5 สังเคราะห์สถิติเชิงปริมาณ (28 ตัวแปร), ถอดรหัสพฤติกรรม 5 มิติ (5-Vector REA), ประเมินความเสี่ยง Block-Bootstrap Monte Carlo, และรันลูปค้นหาพารามิเตอร์อัตโนมัติด้วย Bayesian TPE (Optuna) แบบ Headless ซ่อนหน้าต่าง 100%

---

## 1. Zero-Flag Intuitive Dispatch & Interactive Cockpit Gate

> [!IMPORTANT]
> **ผู้ใช้ไม่ต้องจำคำสั่งยาว**: ระบบจะจัดเส้นทางงานให้อัตโนมัติ 2 รูปแบบ:
> 1. **Auto-Detect Intent (เมื่อพิมพ์พร้อมไฟล์หรือคำสั่ง):** AI วิเคราะห์ข้อความและสั่งรันคำสั่ง CLI ที่ถูกต้องทันที
> 2. **Interactive Cockpit Gate (เมื่อพิมพ์ `/ea-audit` เปล่า):** AI จะเปิด `ask_question` Modal ให้คลิกเลือกทันที 1 วินาที

### A. Auto-Detection Matrix

| สิ่งที่ตรวจพบในข้อความ / บริบท | โหมดที่ระบบเลือกใช้อัตโนมัติ | คำสั่งเบื้องหลัง |
| :--- | :--- | :--- |
| **มีพาธไฟล์ `.htm` หรือ `.html` หรือคำว่า "วิเคราะห์", "ตรวจผล"** | **Single Report Forensic Audit** | `python ea_audit.py analyze --report "<path>"` |
| **มีคำว่า "loop", "ปรับแต่ง", "จูน", "30m", "2h", "ออโต้"** | **Autonomous Optimization Loop** | `python ea_audit.py loop --ea <EA> --ini <INI> --set <SET> --time <TIME>` |
| **มีคำว่า "test", "เช็คระบบ", "ตรวจโค้ด"** | **Self-Test Suite Verification** | `python tests/test_ea_lab.py` |

### B. Interactive Cockpit Gate (เมื่อพิมพ์ `/ea-audit` เปล่า)
AI จะเปิด `ask_question` Modal ให้คลิกเลือกทันที:
1. `(Recommended) 🔍 วิเคราะห์รายงาน Backtest MT5 (.htm / .html) พร้อมถอดรหัส 5-Vector REA`
2. `🧬 รันลูปปรับแต่งพารามิเตอร์อัตโนมัติในพื้นหลัง (Bayesian TPE Unattended Loop)`
3. `🧪 ตรวจสอบความพร้อมของระบบ (Run 10 Test Suites)`

---

## 2. พาธระบบและคำสั่งหลัก (Execution CLI)

- **Python Runtime:** `C:\Users\hotme\AppData\Local\Programs\Python\Python312\python.exe`
- **Project Root:** `C:\Users\hotme\.gemini\antigravity\scratch\ea_lab\`
- **CLI Script:** `C:\Users\hotme\.gemini\antigravity\scratch\ea_lab\ea_audit.py`

### รูปแบบคำสั่ง PowerShell:
```powershell
$py = "C:\Users\hotme\AppData\Local\Programs\Python\Python312\python.exe"
$eaLab = "C:\Users\hotme\.gemini\antigravity\scratch\ea_lab"

# 1. วิเคราะห์รายงาน
& $py "$eaLab\ea_audit.py" analyze --report "<path_to_report.html>"

# 2. รันลูปปรับแต่ง 30 นาที
& $py "$eaLab\ea_audit.py" loop --ea Universal_Matrix_Engine --ini "<path_to_ini>" --set "<path_to_set>" --time 30m
```

---

## 3. มิติการวิเคราะห์ 5-Vector REA & Quant Robustness

1. **V1 Temporal:** ความถี่เวลาเข้าเทรดรายชั่วโมง GMT, ระยะเวลาถือออเดอร์ (Holding Duration)
2. **V2 Entry Dynamics:** สัดส่วน Long/Short, Win Rate แยกฝั่ง, ความแม่นยำของจุดเข้า
3. **V3 Sizing & Capital Risk:** ตรวจจับ Fixed Lot, Dynamic Risk %, Martingale หรือ Grid
4. **V4 Risk Invalidation:** ระยะ Stop Loss, การคำนวณ ATR, ตรวจจับ Zero-SL
5. **V5 Exit & Trailing:** ระยะ Take Profit, การตรวจจับ Break-Even / Trailing Stop, Risk:Reward จริง
6. **Monte Carlo 1,000 Iterations:** Block-Bootstrap หา Median DD, P95 Stress DD, P99 Tail Risk, Probability of Ruin
7. **Composite Score:** วัดความคุ้มค่าผลตอบแทนเทียบกับ Drawdown พร้อม Hard Reject Gates
