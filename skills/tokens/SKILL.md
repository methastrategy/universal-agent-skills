---
name: tokens
description: "[ตรวจวัดโทเค็นสด] เช็ค Input/Output Token, Prompt Cache Hit Rate, และขนาดบริบทจริงจาก Log (Live token telemetry, cache hit rate, context budget)"
---

# /tokens — ศูนย์ตรวจวัดสถิติ Token เชิงประจักษ์แบบเรียลไทม์

อ่านตัวเลขที่บันทึกจริงจาก transcript ของ AGY ด้วย `scripts/telemetry.py` ที่อยู่ในสกิลนี้ รองรับไฟล์ตรงในโฟลเดอร์ conversation และไฟล์ใต้ `.system_generated/logs/`

---

## 1. วิธีการทำงาน (Operational Flow)

เมื่อมีคำสั่ง `/tokens` หรือผู้ใช้ถามเรื่องการใช้งานโทเค็นในเซสชัน:
1. รันสคริปต์ตรวจวัด Telemetry สด:
   รัน `python` ตามด้วยพาธจริงของ `scripts/telemetry.py` จากโฟลเดอร์สกิลที่โหลด
2. ดึงข้อมูล 5 มิติหลักมารายงานแบบ High-Density:
   - **Base Input (Turn 1):** ค่า input รวม cache ของ record แรกที่มี input
   - **Fresh Input Tokens:** โทเค็นอินพุตสดที่ต้องส่งเข้าโมเดลใหม่
   - **Prompt Cache Read:** โทเค็นที่อ่านผ่านแคช และอัตรา **Cache Hit Rate (%)**
   - **Output Tokens:** จำนวนโทเค็นที่โมเดลตอบทั้งหมด และค่าเฉลี่ยต่อสเต็ป
   - **Latest Step Tokens:** สถิติเฉพาะรอบล่าสุด (Input / Cache / Output)

---

## 2. ทางเลือกคำสั่งเพิ่มเติม (Optional Flags)

- ระบุ conversation ID ด้วย `--conv <CONVERSATION_ID>` หรือเพิ่ม `--json` เพื่ออ่านผลแบบ JSON
- ตรวจ `status` และ `observed_metrics` ก่อนรายงานยอด `partial` หมายถึงบรรทัดสุดท้ายยังอ่านไม่ครบ ส่วน `empty` และ `no_usage` หมายถึงไม่มีตัวเลขที่ใช้สรุปได้

---

## 3. กฎเหล็กประจำสคิล (Operating Invariants)

- **Pure Truth:** รายงานเฉพาะตัวเลขจริงจาก Log ห้ามคาดเดาหรือประเมินเอาเอง
- **Lightweight System 1:** ทำงานแบบ Read-Only คืนค่าทันที ไม่แก้ไขไฟล์ระบบใดๆ ทั้งสิ้น
