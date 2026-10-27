---
name: matt3
description: "[ขั้นที่ 3/4: ซอย Ticket] วางแผนหั่นสเปกโค้ดออกเป็นงานย่อยแนวตั้ง (Vertical Slice Tickets) พร้อมลำดับ Dependency ใน Artifact plan.md — ใช้เมื่อต้องการซอยงานต่อจาก /matt2 เสร็จแล้วไป /matt4 (Step 3: Break spec into tracer-bullet vertical slice tickets with blocking edges)"
---

# /matt3 — ขั้นที่ 3: ซอยสเปกเป็น Ticket แนวตั้ง (To-Tickets / Tracer-Bullet Slices)

นำใบสเปกจาก `/matt2` (ใน Artifact `plan.md` หรือจากบริบทการสนทนา) มาหั่นออกเป็น **Tracer-Bullet Vertical Slice Tickets** ที่มีขนาดพอเหมาะ ทำจบและทดสอบได้จริงทีละใบ

## กฎการซอยงานแนวตั้ง (Vertical Slice Rules)
- **ผ่าแนวตั้งครบทุกเลเยอร์ (Vertical, NOT Horizontal):** แต่ละ Ticket ต้องตัดผ่านตั้งแต่ต้นจนจบของพฤติกรรมย่อยหนึ่งอย่าง (เช่น Data/Logic + Interface/UI + Test ที่จุด Seam) ห้ามแบ่งแนวนอนแบบ "Ticket 1 ทำแต่ Database, Ticket 2 ทำแต่ API, Ticket 3 ทำแต่หน้าเว็บ"
- **ตรวจสอบผลได้ในตัวเอง (Demoable/Verifiable):** เมื่อจบ 1 Ticket โค้ดต้องรันผ่านและพิสูจน์พฤติกรรมส่วนนั้นได้ทันที
- **Prefactor First:** หากต้องจัดโครงสร้างโค้ดเดิมเพื่อให้เพิ่มฟีเจอร์ง่ายขึ้น ("Make the change easy, then make the easy change") ให้แยกเป็น Ticket แรกสุด
- **ระบุลำดับการพึ่งพา (`Blocked by`):** ระบุชัดเจนว่า Ticket ใดเริ่มทำได้ทันที (`None`) และ Ticket ใดต้องรอใบไหนเสร็จก่อน

## กระบวนการทำงาน (Process)

1. **ร่างรายการ Vertical Slice Tickets เสนอผู้ใช้:**
   แสดงรายการ Ticket เรียงตามลำดับ Dependency โดยแต่ละใบระบุ:
   - **Ticket `<NN>`: `<ชื่อ Ticket>`**
   - **Blocked by:** `<เลข Ticket ที่ต้องเสร็จก่อน หรือ None (ทำได้ทันที)>`
   - **What it delivers:** พฤติกรรมตั้งแต่ต้นจนจบที่ Ticket นี้ทำให้ทำงานได้จริง
   - **Acceptance Criteria & Verification:** เงื่อนไขผ่านงานและเทสต์ที่ใช้ตรวจ

2. **อัปเดตตารางและรายละเอียด Tickets ลงใน Artifact `plan.md`:**
   - บันทึกรายการ Ticket ทั้งหมดพร้อมสถานะ (`[ ] Ready`, `[~] In Progress`, `[x] Done`) ลงในส่วน `## Implementation Tickets (Vertical Slices)` ของไฟล์ Artifact `plan.md` (ไม่สร้างไฟล์ `.md` แปลกปลอมลงในโฟลเดอร์โปรเจกต์ของผู้ใช้ ยกเว้นผู้ใช้สั่ง)

3. **ถามยืนยันและชี้ทางไปขั้นที่ 4:**
   - ถามผู้ใช้ว่าขนาดการซอย Ticket และลำดับ Dependency เหมาะสมหรือไม่
   - แนะนำให้พิมพ์ **`/matt4 Ticket 01`** (หรือ **`/matt4`** เพื่อรันใบแรกที่พร้อมทำทันที)
