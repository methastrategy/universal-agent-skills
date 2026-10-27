---
name: matt5
description: "[ขั้นเสริม: ผ่าตัดโครงสร้างโค้ด] วิเคราะห์และตรวจสอบสถาปัตยกรรมโค้ดเดิมเพื่อหาจุดยุบเป็น Deep Modules พร้อมสร้างรายงาน HTML เปิดดูในเบราว์เซอร์ — ใช้เมื่อโค้ดเริ่มรก ซับซ้อน หรือต้องการ Refactor โครงสร้างใหญ่ (Step 5 Bonus: Scan codebase for shallow modules and architectural friction with visual HTML report)"
---

# /matt5 — ขั้นเสริม: วิเคราะห์และผ่าตัดสถาปัตยกรรมโค้ดเดิม (Improve Codebase Architecture)

สแกนโค้ดในโปรเจกต์เพื่อค้นหาจุดฝืดเชิงสถาปัตยกรรม (Architectural Friction) และเสนอแนะ **Deepening Opportunities** (การยุบรวมโมดูลตื้นๆ ที่กระจัดกระจายให้กลายเป็น Deep Modules ที่ดูแลรักษาง่ายและทดสอบง่าย)

## กระบวนการทำงาน (Process)

1. **สำรวจจุดที่มีความซับซ้อน (Explore & Apply the Deletion Test):**
   - อ่านหลักการและคำศัพท์จาก [`codebase-design`](../../architect/references/deep-modules.md) (`Module`, `Interface`, `Depth`, `Seam`, `Adapter`, `Leverage`, `Locality`)
   - หากผู้ใช้ระบุโฟลเดอร์หรือระบบย่อย ให้โฟกัสจุดนั้นก่อน หากไม่ระบุ ให้สำรวจจุดที่โค้ดถูกแก้ไขบ่อย (`git log --oneline -n 30`) หรือจุดที่มีความซับซ้อนสูง
   - มองหาอาการเหล่านี้:
     - การทำความเข้าใจเรื่องเดียวต้องกระโดดข้ามไฟล์เล็กๆ หลายไฟล์
     - โมดูลแบบ **Shallow** ที่ Interface ซับซ้อนพอๆ กับ Implementation ข้างใน
     - โมดูลที่พึ่งพากันแน่นเกินไป (Tightly-coupled across seams) หรือทดสอบผ่าน Public Interface ได้ยาก

2. **สร้างรายงาน Visual HTML Report ในโฟลเดอร์ชั่วคราว (`%TEMP%`):**
   - อ้างอิงรูปแบบจากไฟล์ [HTML-REPORT.md](HTML-REPORT.md)
   - เขียนไฟล์ HTML แบบ Self-contained (ใช้ Tailwind CDN และแผนภาพ Mermaid / SVG เปรียบเทียบ **Before vs After**) ลงใน `%TEMP%\architecture-review-<timestamp>.html` **เพื่อไม่ให้มีไฟล์ขยะหลงเหลือในโฟลเดอร์โปรเจกต์**
   - เปิดไฟล์ HTML ให้ผู้ใช้ดูทันทีผ่านคำสั่ง `Start-Process "<path>"` และแจ้ง Path ของไฟล์
   - ในการ์ดแต่ละข้อให้ระบุ:
     - **Files:** ไฟล์/โมดูลที่เกี่ยวข้อง
     - **Problem:** ทำไมโครงสร้างเดิมถึงดูแลยากหรือแก้ไขลำบาก
     - **Solution:** แนวทางการยุบรวมเป็น Deep Module
     - **Benefits:** ประโยชน์ด้าน Locality, Leverage และการเขียนเทสต์ที่ง่ายขึ้น
     - **Before / After Diagram:** แผนภาพเปรียบเทียบก่อนและหลังปรับโครงสร้าง
     - **Recommendation Strength:** `Strong` / `Worth exploring` / `Speculative`

3. **ให้ผู้ใช้เลือกจุดที่จะผ่าตัด:**
   - ถามผู้ใช้ว่าต้องการเลือกปรับปรุงข้อไหน จากนั้นใช้กระบวนการ [`/matt1`](../../architect/SKILL.md) (เจาะลึกรูปแบบ Interface ใหม่) -> [`/matt2`](../../architect/SKILL.md) (วางแผนใน `plan.md`) -> [`/matt4`](../../build/SKILL.md) (ลงมือ Refactor และรันเทสต์) ตามลำดับ
