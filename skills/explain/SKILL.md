---
name: explain
description: "อธิบายโค้ด สมการ และทฤษฎียากให้เข้าใจง่าย — ใช้เมื่อต้องการให้สอน สรุปหลักการ เปรียบเทียบเห็นภาพ หรือยกตัวอย่างโค้ด (High-density technical explanation, intuitive analogies, code examples for algorithms)"
---

# Technical Deconstruction & Concept Explanation

Explain complex software architectures, subtle algorithms, or tricky code patterns with razor-sharp clarity, intuitive analogies, and production-grade examples.

---

## โหมดการทำงาน (Operational Modes)

| โหมด | คำสั่ง | การทำงาน |
| :--- | :--- | :--- |
| **Concept Explanation (Default)** | `/explain` | อธิบายแก่นทฤษฎี เทียบเคียง Metaphor ตัวอย่างโค้ดสั้น และดักทาง Gotchas |
| **Interactive Course Teaching** | `/explain --teach` (หรือ `/teach`) | จัดการสอนเป็นคอร์สหลายเซสชัน วัดระดับความเข้าใจ ให้แบบฝึกหัด และบันทึกประวัติการเรียนรู้ |

---

## Steps

1. **Deconstruct Concept Matrix**: Break down the concept into basic, highly-isolated components.
2. **Formulate Intuitive Metaphors**: Draw comparisons between the abstract concept and simple real-world scenarios.
3. **Draft a Minimal Example**: Provide a highly-simplified, production-quality code snippet or data model.
4. **Identify Gotchas**: List common pitfalls, misconceptions, and anti-patterns associated with the concept.
5. **Interactive Course Progression (เฉพาะเมื่อใช้ Flag `--teach` หรือสั่งให้สอน)**:
   - แบ่งเนื้อหาเป็นเซสชันย่อยๆ (Bite-sized modules)
   - มีแบบฝึกหัดให้ผู้ใช้ทดลองคิด/เขียนโค้ดท้ายบทเรียน
   - สรุปจุดที่ผู้ใช้เข้าใจแล้วและจุดที่ต้องเน้นในรอบถัดไป

---

## Coverage Checklist
> เนื้อหาที่ต้องครอบคลุม ไม่ใช่หัวข้อที่ต้องพิมพ์ — ห้ามตอบเป็นหัวข้อเลขข้อ รูปแบบตอบตาม GEMINI.md §1
- **Core Concept Definition**: Extremely simple, high-density description of the principle.
- **Real-World Metaphor**: Easily understood comparison.
- **Minimal Code Example**: Functional, minimal code representation of the concept.
- **Target Gotchas**: Crucial warnings to prevent typical usage mistakes.

---

## Operating Rules

- Avoid all unnecessary academic jargon; describe complex ideas using high-density, accessible terms.
- Every explanation must contain at least one visual flow or code-based example.
