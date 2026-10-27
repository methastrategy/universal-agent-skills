---
name: matt4
description: "[ขั้นที่ 4/4: เขียนโค้ด] เขียนโค้ดตาม Ticket หรือ Spec ด้วย TDD ที่จุด Seam และออกแบบเป็น Deep Modules พร้อมรันเทสต์และตรวจสอบโค้ด — ใช้เมื่อเริ่มลงมือเขียนโค้ดต่อจาก /matt2 หรือ /matt3 (Step 4: Implement ticket or spec using TDD, deep modules, typechecking, and review)"
---

# /matt4 — ขั้นที่ 4: ลงมือเขียนโค้ดแบบ Deep Modules + TDD (Implement & Verify)

ลงมือพัฒนาโค้ดตาม Ticket ที่ระบุ (จาก `/matt3`) หรือตามใบสเปก (จาก `/matt2`) ด้วยวินัยทางวิศวกรรมซอฟต์แวร์สูงสุด ไม่เร่งรีบเขียนโค้ดแบบลวกๆ

## กฎเหล็กของการลงมือเขียนโค้ด (Strict Engineering Harness)

1. **อ่านและยึดตามแผน (`plan.md`) อย่างเคร่งครัด:**
   - ตรวจสอบใบสเปกหรือ Ticket ที่กำลังทำใน Artifact `plan.md` (และ `GLOSSARY.md` / `docs/adr/` หากมีในโปรเจกต์)
   - ห้ามแก้ไขโค้ดนอกเหนือขอบเขตที่ตกลงไว้โดยพลการ

2. **บังคับออกแบบเป็น Deep Modules ([`codebase-design`](../../architect/references/deep-modules.md)):**
   - อ่านและใช้หลักการใน [`codebase-design`](../../architect/references/deep-modules.md): สร้างโมดูลที่มี **Interface เล็กและเรียบง่าย (Small Interface)** แต่ซ่อนตรรกะที่ซับซ้อนไว้ภายใน (**Deep Implementation**)
   - รับ Dependency เข้ามาทางพารามิเตอร์ (Accept dependencies, don't hardcode internal coupling) และเน้นคืนค่าผลลัพธ์ที่ตรวจสอบง่าย
   - หลีกเลี่ยง Shallow Modules (การแยกฟังก์ชัน/ไฟล์ย่อยพร่ำเพรื่อที่แค่ส่งผ่านข้อมูลไปมาโดยไม่ลดความซับซ้อน)

3. **บังคับวงจร TDD ที่จุด Seam ([`tdd`](tdd-seams.md)):**
   - อ่านหลักการใน [`tdd`](tdd-seams.md)
   - **Red -> Green Loop (Vertical Slice):** เขียนเทสต์ที่จุด Seam (Public Interface ที่ตกลงไว้) ให้รันไม่ผ่านก่อน (Red) แล้วเขียนโค้ดเท่าที่จำเป็นเพื่อให้เทสต์ผ่าน (Green) ทีละพฤติกรรมย่อย
   - ห้ามเขียนเทสต์ที่ผูกติดกับโครงสร้างภายใน (Implementation-coupled) หรือเทสต์ที่ลอกสูตรคำนวณเดียวกันมาเช็กตัวเอง (Tautological)

4. **ตรวจสอบคุณภาพอย่างต่อเนื่อง (Continuous Verification & Code Review):**
   - รัน Typecheck, Linter, และไฟล์เทสต์เฉพาะจุดระหว่างทำอย่างสม่ำเสมอ
   - เมื่อครบทุกข้อใน Ticket/Spec ให้รัน Test Suite / Build ตรวจสอบความถูกต้องทั้งหมด
   - ตรวจทานโค้ดของตัวเอง (Self-Review): เช็กความสะอาดของโค้ด ความปลอดภัย ขอบเขตโมดูล และติ๊กเครื่องหมาย `[x]` อัปเดตความคืบหน้าใน Artifact `plan.md`

5. **รายงานสรุปและสถานะการนำขึ้นระบบ:**
   - สรุปสิ่งที่ทำสำเร็จ ผลการรันเทสต์ และแจ้ง Ticket ลำดับถัดไปที่พร้อมทำต่อ (หากยังมีค้างใน `plan.md`)
   - สำหรับโปรเจกต์เว็บ ให้ระบุสถานะชัดเจนเสมอว่า:
     `📌 สถานะการนำขึ้นระบบ: ยังไม่ได้อัปเดตขึ้น GitHub / Vercel` (หรืออัปเดตแล้วหากผู้ใช้สั่งให้ Commit/Push)
