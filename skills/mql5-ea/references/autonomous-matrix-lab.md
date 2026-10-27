# MeEA Autonomous Matrix Lab & Universal Modular Architecture (Zero-Token Lab)

คู่มือสถาปัตยกรรมและสัญญาการทำงานของระบบ Matrix Lab สำหรับการ Sweep พารามิเตอร์และทดสอบคู่ Indicator แบบ Offline 100% โดยไม่ต้องพึ่งพา AI หรือใช้ Token

---

## 1. ปัญหาเดิม & สถาปัตยกรรมใหม่ (Paradigm Shift)
* **ปัญหาเดิม:** เมื่อต้องการทดสอบคู่ Indicator ใหม่ หรือกวาดค่า Matrix (เช่น SL, TP, Breakeven, Sessions) มักสั่ง AI ในแชตเขียนสคริปต์รายครั้ง (`sweep_*.py` งอกกว่า 58 ตัวในโปรเจกต์) ซึ่งรันช้าแบบ Single Pass และสิ้นเปลือง Token มหาศาล
* **สถาปัตยกรรมใหม่:**
  1. **MQL5 Universal Modular Engine (`MeAnti_Universal_Matrix_Engine.mq5`):** แยก 90% Shared Armor (Risk $30 USD, Max Spread, Breakeven, Trailing, Session Gating) ออกจาก 10% Variable Strategy แล้วควบคุมผ่าน `enum` ใน Inputs
  2. **Python Standalone Lab Engine (`matrix_engine.py`):** สมองกลควบคุมการคอมไพล์ รัน Sweep สกัดผล กรอง Drawdown และส่งออก Preset เข้า MT5 อัตโนมัติ

---

## 2. Universal Modular EA Design Pattern

```
┌────────────────────────────────────────────────────────┐
│   90% SHARED ARMOR (Fixed Institutional Protection)     │
│  - Capital: $30 USD / Cent (0.01 lot)                  │
│  - Hard Stop Loss Clamp ($0.50 - $2.50)                │
│  - Breakeven Ratchet (+0.8R - +1.2R)                   │
│  - Trailing Stop Distance                              │
│  - Daily Loss Cap & Loss Streak Circuit Breaker        │
│  - Session Time Window (Asia, London, NY Overlap)      │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│      10% VARIABLE MATRIX LOGIC (Select via ENUM)        │
│                                                        │
│  Layer 1: Macro Trend Filter (ENUM_MACRO_FILTER)       │
│   ├── [0] MACRO_FILTER_NONE                            │
│   ├── [1] MACRO_FILTER_HTF_EMA (Price vs HTF EMA)      │
│   ├── [2] MACRO_FILTER_EMA_CROSS (Fast vs Slow Cross)  │
│   └── [3] MACRO_FILTER_ADX_REGIME (ADX Trend + DI)     │
│                                                        │
│  Layer 2: Setup / Trigger (ENUM_TRIGGER_STRATEGY)      │
│   ├── [0] TRIGGER_EMA_CROSS                            │
│   ├── [1] TRIGGER_RSI_HOOK                             │
│   ├── [2] TRIGGER_CCI_HOOK                             │
│   ├── [3] TRIGGER_MACD_CROSS                           │
│   └── [4] TRIGGER_BOLLINGER_BOUNCE                     │
└────────────────────────────────────────────────────────┘
```

---

## 3. Dual-Engine Matrix Optimization Protocol

### โหมด 1: ⚡ Fast Multi-Core Optimization (`Optimization=2` Genetic)
* สร้างไฟล์ INI ระบุ `Optimization=2` และแปลงตัวแปรเป็นช่วง `Value||Start||Step||Stop||Y`
* MT5 สปอว์น Agent ทุก Core ใน CPU (`metatester64`) ทำงานคู่ขนาน
* กวาดค่าหลักร้อยถึงพันรอบเสร็จสิ้นภายใน 2-3 นาที
* สกัดรายงาน XML/HTML หา Champion Preset ที่ได้กำไรสูงสุดภายใต้ Drawdown $\le 25\%$

### โหมด 2: 🎯 Detailed Targeted Sequential Sweep (`Optimization=0`)
* รันตามตาราง Cartesian Product ทีละรอบอย่างแม่นยำ
* แสดง Progress Bar แบบสด `[Combo X/Total] -> Profit, PF, WR, DD, Trades`
* เก็บบันทึกไฟล์รายงาน HTML แยกเฉพาะทุกรอบ
* สร้างตาราง Leaderboard สรุปผลเป็น `.csv`

---

## 4. Preset Deployment & Walk-Forward Validation Contract

1. **Auto-Deployment to MT5 Profiles:**
   * สคริปต์ต้องบันทึกไฟล์ `.set` สองที่เสมอ:
     * `presets/matrix_champions/<preset_name>.set` (ใน Workspace)
     * `%APPDATA%\MetaQuotes\Terminal\<HASH>\MQL5\Profiles\Tester\<preset_name>.set` (ใน MT5)
   * ผู้ใช้สามารถเปิด MT5 Strategy Tester แล้วโหลด Preset มาเทรดหรือทดสอบต่อได้ทันทีโดยไม่ต้องก็อปปี้ไฟล์มือ
2. **Walk-Forward Cross-Window Stress Gate:**
   * ห้ามเชื่อผลลัพธ์จากการ Sweep ช่วงเวลาเดียว
   * ต้องผ่านการทดสอบ 3 หน้าต่างมาตรฐาน:
     * `1W_Latest` (สภาวะตลาดสด 5-7 วันทำการ)
     * `30D_Latest` (สภาวะฐาน 1 เดือน)
     * `4M_Summer_Surge` (สภาวะเทรนด์ยาว 4 เดือน)
   * **เกณฑ์ผ่าน:** กำไรสุทธิ $> 0$, Max DD $\le 25\%$, และ Trades รวม $\ge 15$ ทุกหน้าต่าง
