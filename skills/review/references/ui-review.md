---
name: ui-review
description: "ตรวจสอบความสวยงามและการใช้งานหน้าเว็บ/แอป (UI/UX Review) — ใช้เมื่อต้องการให้ช่วยตรวจเช็กวิจารณ์การจัดวางหน้าเว็บ สี ฟอนต์ และการรองรับหน้าจอมือถือ/คอม (Comprehensive UI/UX design audit, responsiveness, typography, color harmony, and interaction ergonomics)"
---

# Comprehensive UI/UX Design & Responsiveness Review

Perform a meticulous visual and interactive audit of user interfaces across typography hierarchy, design tokens, responsive breakpoints, layout shifting, and interaction ergonomics.

## Steps

1. **Evaluate Visual Architecture**: Inspect typography hierarchies, color harmonies, and alignment spacing.
2. **Audit Device Responsiveness**: Test component behavior on multiple virtual breakpoints (desktop, tablet, mobile).
3. **Assess Interaction Ergonomics**: Evaluate transitions, hovering cues, micro-animations, and visual feedback.
4. **Identify User Friction**: Locate confusing components, slow inputs, or layout shifting (CLS) bugs.

---

## Coverage Checklist
> เนื้อหาที่ต้องครอบคลุม ไม่ใช่หัวข้อที่ต้องพิมพ์ — ห้ามตอบเป็นหัวข้อเลขข้อ รูปแบบตอบตาม GEMINI.md §1
- **Visual Quality Rating**: Critique of style guidelines and visual consistency.
- **Responsiveness Report**: Detailed analysis of breakpoints, text scaling, and mobile alignment.
- **Interactive Friction Log**: Direct checklist of visual bugs, poor micro-interactions, or layout shifting.

---

## UI Ergonomics Audit Checklist (Cognitive Friction QA)
- [ ] **Single Primary Action:** แต่ละหน้าจอหรือการ์ดมี Primary CTA เด่นเพียงปุ่มเดียว ปุ่มรองใช้ Outline หรือ Ghost
- [ ] **Whitespace & Padding:** คอนเทนเนอร์และการ์ดมีระยะหายใจเพียงพอ (p-4 ถึง p-6) และเว้นระยะห่างตาม Gestalt
- [ ] **Action Overflow:** เมนูการทำงานมี Action บนหน้าจอไม่เกิน 2–3 ปุ่ม ปุ่มที่ใช้ไม่บ่อยถูกย้ายเข้า Overflow Menu (`...`)
- [ ] **Typographic Scanability:** มีลำดับชั้นฟอนต์ชัดเจน (Size, Weight, Muted tint) ปราศจากย่อหน้าตัวหนังสือแบนราบ
- [ ] **Form Chunking:** ฟอร์มที่มี Input $\ge 6$ รายการ ถูกจัดกลุ่มลงในการ์ดย่อยหรือแบ่งเป็น Multi-step Stepper

---

## Operating Rules

- Analyze strictly from a user-centric perspective; prioritize polished details and visual excellence.
- Ensure all interactive elements provide instant, clear visual cues on action.
