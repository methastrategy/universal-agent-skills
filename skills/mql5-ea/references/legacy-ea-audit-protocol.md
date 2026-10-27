# โปรโตคอลการตรวจชันสูตรและปลดประจำการ EA (Legacy EA Audit, Screening & Purge Protocol)

ระเบียบปฏิบัติมาตรฐานสำหรับ Antigravity ในการตรวจสอบ คัดกรอง และสังคายนาคลังโค้ด EA เก่า เพื่อกำจัดความสับสน "EA เก่า/ใหม่" และรักษาความปลอดภัยของพอร์ตการลงทุน

---

## 1. ด่านที่ 1: การตรวจสอบไวยากรณ์และการคอมไพล์ (CLI Compilation Gate)
ก่อนนำ EA เก่าใดๆ ไปทดสอบ ต้องทำการคอมไพล์ผ่าน MetaEditor 64 CLI ในโหมด Headless เสมอ:
1. คัดลอกซอร์สโค้ด `.mq5` ไปยังโฟลเดอร์ชั่วคราวใน Roaming (`Legacy_Audit/`)
2. รันคำสั่งคอมไพล์พร้อมแนบไฟล์ include:
   ```powershell
   & "C:\Program Files\MetaTrader 5\metaeditor64.exe" /compile:"<dst_mq5>" /inc:"<MQL5_DIR>" /log:"<log_path>"
   ```
3. อ่าน log ด้วย Unicode encoding และตรวจสอบว่าได้ `0 errors`
4. หากคอมไพล์ไม่ผ่านเนื่องจากฟังก์ชัน MQL4 ตกค้างหรือขาด Library ให้ออกรายงานระบุข้อผิดพลาดและจัดเก็บเข้าหมวด Uncompilable ทันที

---

## 2. ด่านที่ 2: การทดสอบคัดกรองบนข้อมูลจริง (Real-Tick Screening Benchmark)
นำไฟล์ `.ex5` ที่ผ่านการคอมไพล์มารัน Strategy Tester บนข้อมูล Real Ticks ของโบรกเกอร์ (100% Every Tick Based on Real Ticks) ในกรอบเวลาสั้นมาตรฐาน 2 เดือน (60 วัน) ทุน Cent 1,000 USC:

### เกณฑ์การคัดกรอง (Go / No-Go Decision Gate):
- **ผ่านเกณฑ์ (PASS):**
  - Net Profit > 0
  - Profit Factor $\ge 1.05$
  - Max Equity Drawdown $< 40.0\%$
  - ต้องมี Stop Loss หรือ Risk Control ชัดเจน
- **ตกรอบทันที (FAIL & DECOMMISSION):**
  - **กฎเหล็ก Zero-Martingale:** ห้ามใช้ระบบเบิ้ลล็อต (Martingale / Grid Aggressive) บนทองคำเด็ดขาด หากพบว่าติด Drawdown ล้างพอร์ต ให้ปรับสถานะเป็น Fatal Defect ทันที
  - **โอเวอร์เทรด / ขนาดไม้คงที่ใหญ่เกินตัว:** หากพบว่า Fixed Lot ทำให้พอร์ตติด Margin Call ในช่วง Sideway ให้ถือว่าไม่ผ่านเกณฑ์

---

## 3. ด่านที่ 3: การย้ายเข้าคลังกักกันถาวร (_decommissioned_archive)
ห้ามลบไฟล์ซอร์สโค้ดของผู้ใช้ทิ้งแบบถาวร (Zero Data Destruction Invariant) ให้ใช้การย้ายไฟล์ (Move) เข้าสู่โฟลเดอร์กักกันถาวร `experts/_decommissioned_archive/` ตามหมวดหมู่:
1. `_decommissioned_archive/failed_research_eas/`: สำหรับ EA ที่ผ่านการวิจัยแล้วพบว่า Edge พังทลายหรือติดลบในระยะยาว
2. `_decommissioned_archive/legacy_all_iterations/`: สำหรับเวอร์ชันย่อยในอดีต (เช่น Samurai v0.0 ถึง v5.16, MEA v1.0)
3. `_decommissioned_archive/legacy_audited_losers/`: สำหรับผู้ท้าชิงที่รันคัดกรองแล้วไม่ผ่านเกณฑ์กำไร
4. `_decommissioned_archive/obsolete_binaries/`: สำหรับไฟล์ `.ex5` เก่าหรือบิลด์บั๊กที่ไม่ได้ใช้งาน
5. ลบไฟล์ไบนารี `.ex5` ของตัวที่ตกรอบออกจากโฟลเดอร์ MT5 Roaming เพื่อไม่ให้รกใน Navigator ของโปรแกรม MT5

---

## 4. ด่านที่ 4: การรวมศูนย์ Active Production Fleet หนึ่งเดียว
พื้นที่ทำงานหลัก `experts/` ต้องคงไว้เฉพาะ **Modern Active Fleet** ที่ผ่านการพิสูจน์แล้วเท่านั้น:
- แยก 1 โฟลเดอร์ต่อ 1 บทบาทกลยุทธ์ (`Breakout`, `Trend_Runner`, `Reversion_Sniper`, `Scalping_Grid`, `Core_Framework`)
- ทุก EA ต้องใช้ไลบรารีแกนกลางร่วมกัน (`MeAntiTradeCore.mqh`)
- ติดตั้งระบบ **Dynamic Equity Risk Sizing** (คำนวณ Lot อัตโนมัติจากขนาด Stop Loss จริง) และ **Daily Loss Circuit Breaker** เสมอ
