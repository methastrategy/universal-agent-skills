---
name: matt2
description: "[ขั้นที่ 2/4: ออกใบสเปก] สรุปและวางแผนแปลงสิ่งที่คุยกันเป็นไฟล์สเปกโค้ด (Spec) พร้อมจุดเทสต์ Seam ลงใน Artifact plan.md — ใช้เมื่อต้องการออกใบสเปกต่อจาก /architect เสร็จแล้วไป /build หรือ /build (Step 2: Synthesize conversation into formal Spec and test seams in plan.md artifact)"
---

# /matt2 — ขั้นที่ 2: สังเคราะห์ใบสเปกและกำหนดจุดเทสต์ (To-Spec in Artifact `plan.md`)

นำสิ่งที่สรุปไว้จากการสนทนา (หรือจาก `/matt1`) และความเข้าใจในโครงสร้างโค้ด มาเขียนเป็น **ใบสเปกมาตรฐาน (Formal Specification)** โดย **ไม่ต้องสัมภาษณ์ซ้ำ**

## กฎเหล็ก (Zero-Clutter Artifact Storage)
- **บันทึกใบสเปกไว้ในระบบ Artifact (`<appDataDir>\brain\<conversation-id>\plan.md`) เป็นค่าเริ่มต้น** เพื่อรักษาความสะอาดของโฟลเดอร์โปรเจกต์ (Zero-Clutter Discipline) ไม่สร้างไฟล์ `.md` แปลกปลอมทิ้งไว้ใน Repo ของผู้ใช้ (ยกเว้นโปรเจกต์ที่มีไฟล์ `docs/agents/issue-tracker.md` กำหนดไว้เป็นอย่างอื่น หรือผู้ใช้สั่งให้เซฟลงโปรเจกต์โดยตรง)
- อ้างอิงหลักการแยกโมดูลและจุดเทสต์จากสกิล [`codebase-design`](deep-modules.md)

## กระบวนการทำงาน (Process)

1. **สำรวจสถานะโค้ดปัจจุบัน (หากยังไม่ได้ทำ):**
   - ตรวจสอบโครงสร้างไฟล์และโมดูลที่เกี่ยวข้องในโปรเจกต์เพื่อให้สเปกสอดคล้องกับระบบจริง

2. **กำหนดจุด Seam สำหรับเขียนเทสต์ (Identify Test Seams):**
   - เลือกจุด **Seam** (Public Interface ของ Deep Module) ในระดับที่สูงและครอบคลุมพฤติกรรมจริงมากที่สุด โดยใช้จำนวน Seam ให้น้อยที่สุดเท่าที่จำเป็น (หลีกเลี่ยงการผูกเทสต์กับ Implementation ภายใน)

3. **สร้างไฟล์สเปกใน Artifact `plan.md` ตามโครงสร้างต่อไปนี้:**

```markdown
# Specification & Pre-Flight Plan: <ชื่อฟีเจอร์/งาน>

## 1. Problem Statement & Domain Glossary
- **ปัญหาที่ต้องการแก้ (มุมมองผู้ใช้):** ...
- **คำศัพท์โดเมนและโมดูลหลัก (Ubiquitous Language):** ...

## 2. Solution Overview
- **ภาพรวมวิธีแก้ปัญหา:** ...

## 3. User Stories
1. As an <actor>, I want <feature>, so that <benefit>
2. ... (ครอบคลุมทุกกรณีใช้งานและ Edge Cases)

## 4. Implementation Decisions & Deep Modules
- **Modules & Interfaces ที่จะสร้าง/แก้ไข:** (เน้นออกแบบเป็น Deep Module: Interface เล็กและเรียบง่าย ซ่อนความซับซ้อนไว้ภายใน)
- **Architectural & Schema/API Contracts:** ...
- **Defect/Issue Matrix & Granular Blueprint:** ระบุไฟล์และจุดที่จะแก้ไขอย่างชัดเจน

## 5. Testing Decisions & Agreed Seams
- **Pre-Agreed Test Seams:** ระบุ Public Interface ที่จะใช้เขียนเทสต์ตรวจสอบพฤติกรรม
- **Verification Criteria:** คำสั่งรันเทสต์ / Typecheck / Build เพื่อยืนยันผล

## 6. Out of Scope
- สิ่งที่ไม่รวมอยู่ในรอบการทำงานนี้
```

4. **ยืนยันกับผู้ใช้และแนะนำขั้นต่อไป:**
   - แสดงลิงก์ Artifact `plan.md` ให้ผู้ใช้ตรวจสอบจุด Seam และรายละเอียดสเปก
   - แนะนำขั้นตอนถัดไป:
     - หากเป็น **งานใหญ่/หลายส่วน** แนะนำให้พิมพ์ **`/matt3`** เพื่อหั่น Spec เป็น Ticket แนวตั้ง (Vertical Slices)
     - หากเป็น **งานขนาดเล็ก-กลาง** ที่ทำจบได้ในรอบเดียว แนะนำให้พิมพ์ **`/matt4`** เพื่อเริ่มเขียนโค้ดตาม Spec ทันที
