---
name: tokens
description: "[ตรวจวัดโทเค็นสด] เช็ค Input/Output Token, Prompt Cache Hit Rate, และขนาดบริบทจริงจาก Log (Live token telemetry, cache hit rate, context budget)"
---

# /tokens — ศูนย์ตรวจวัดสถิติ Token เชิงประจักษ์แบบเรียลไทม์

ดึงตัวเลขการใช้งาน Token สดจริง 100% จากไฟล์บันทึกระบบ [transcript.jsonl](file:///~/.gemini/antigravity/brain/) ด้วยเอนจิน `telemetry.py` โดยไม่มีการคาดเดาหรือประมาณการหลอก

---

## 1. วิธีการทำงาน (Operational Flow)

เมื่อมีคำสั่ง `/tokens` หรือผู้ใช้ถามเรื่องการใช้งานโทเค็นในเซสชัน:
1. รันสคริปต์ตรวจวัด Telemetry สด:
   `python "~\.gemini\config\skills\tokens\scripts\telemetry.py"`
2. ดึงข้อมูล 5 มิติหลักมารายงานแบบ High-Density:
   - **Base Input (Turn 1):** ขนาดของ System Prompt เริ่มต้นในเซสชัน
   - **Fresh Input Tokens:** โทเค็นอินพุตสดที่ต้องส่งเข้าโมเดลใหม่
   - **Prompt Cache Read:** โทเค็นที่อ่านผ่านแคช และอัตรา **Cache Hit Rate (%)**
   - **Output Tokens:** จำนวนโทเค็นที่โมเดลตอบทั้งหมด และค่าเฉลี่ยต่อสเต็ป
   - **Latest Step Tokens:** สถิติเฉพาะรอบล่าสุด (Input / Cache / Output)

---

## 2. ทางเลือกคำสั่งเพิ่มเติม (Optional Flags)

- **ดูเฉพาะเซสชันที่ระบุ:**
  `python "~\.gemini\config\skills\tokens\scripts\telemetry.py" --conv <CONVERSATION_ID>`
- **ดึงผลลัพธ์เป็น Raw JSON:**
  `python "~\.gemini\config\skills\tokens\scripts\telemetry.py" --json`

---

## 3. กฎเหล็กประจำสคิล (Operating Invariants)

- **Pure Truth:** รายงานเฉพาะตัวเลขจริงจาก Log ห้ามคาดเดาหรือประเมินเอาเอง
- **Lightweight System 1:** ทำงานแบบ Read-Only คืนค่าทันที ไม่แก้ไขไฟล์ระบบใดๆ ทั้งสิ้น
