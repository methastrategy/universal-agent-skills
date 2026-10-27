---
name: build
description: "[สร้างและเขียนโค้ด] พัฒนาโค้ดตามแผนด้วย TDD ที่ Seams และ Deep Modules — ใช้เมื่อมีแผนแล้วและพร้อมสร้างระบบจริง (Granular implementation, TDD at seams, React 19 actions, build verification)"
---

# /build — ลงมือสร้างและพัฒนาซอฟต์แวร์ตามแผน (Implementation & Verification Hub)

เปลี่ยนแผนงาน สเปก หรือรายการ Ticket ให้กลายเป็นโค้ดจริงระดับ Production ด้วยวินัยทางวิศวกรรมซอฟต์แวร์สูงสุด (TDD + Deep Modules + Zero Regressions)

## สถาปัตยกรรมอ้างอิง (Reference Map)
- **การซอยชิ้นงานเป็นแนวตั้ง:** อ่าน `references/vertical-slices.md` (Tracer-bullet vertical slice tickets)
- **การเขียนเทสต์นำร่อง:** อ่าน `references/tdd-seams.md` (Test-Driven Development at Public Seams)
- **การออกแบบโมดูลแบบลึก:** อ่าน `references/deep-module-implementation.md` (Deep Modules over Shallow Wrappers)
- **วิศวกรรม React 19 / Full-Stack:** อ่าน `references/react-modern-engineering.md` (Server Actions, `server-only`, Zod)
- **ระเบียบวิธีแก้ไขโค้ดเฉพาะจุด:** อ่าน `references/surgical-diff-protocol.md` (Single Mutable Surface, Syntax Gate)
- **คู่มือชุดเครื่องมือเร่งความเร็วสูง:** อ่าน `references/fast-toolchain-uv-ruff.md` (Rust-based uv, ruff, biome, bun)
- **Quant Trading Dashboard Patterns:** อ่าน `references/quant-trading-dashboard-patterns.md` (Multi-capital verification)

---

## กระบวนการสร้าง 4 ขั้นตอน (The 4-Step Build Protocol)

### 0. Ponytail Pre-Code Selection Order (ต้องทำก่อนเริ่มเขียนโค้ดใหม่)
ลำดับการเลือกโค้ด — หยุดที่ข้อแรกที่ทำงานได้:
1. **Skip it?** — Feature ที่ไม่มีใครขอ ให้ตัดทิ้งทันที ระบุ 1 บรรทัดว่าข้ามอะไร
2. **Already in codebase?** — ใช้ Helper, Component, Service เดิมในโปรเจกต์
3. **Standard Library / Platform Feature?** — ใช้ฟังก์ชันมาตรฐานของภาษา/แพลตฟอร์ม
4. **Installed dependency?** — ใช้ Dependency ที่มีอยู่แล้ว ห้ามเพิ่มแพ็กเกจใหม่เพื่อโค้ดไม่กี่บรรทัด
5. **One-liner ที่อ่านเข้าใจทันที?** — เขียนโค้ดสั้น 1 บรรทัด
6. **Otherwise** — เขียนโค้ดใหม่ขั้นต่ำที่ทำงานได้สมบูรณ์ (The smallest complete change)
- *Shortcut Invariant:* ใส่ tag กำกับเมื่อใช้ shortcut: `// shortcut: <ขีดจำกัด>, <เงื่อนไขที่ควร upgrade>`
- *Immutable Eval Harness (Karpathy Pattern):* แยก "Target Seam" ออกจาก "Evaluation Harness" ห้ามดัดแปลงหรือลดทอนความเข้มงวดของ Test Suite เดิมเด็ดขาด
- *Archon Cognitive Seam Checkpoint:* ก่อนแก้ไฟล์ ประเมิน 3 ขอบเขตในใจ: (1) Target Seam, (2) Forbidden Surfaces (ห้ามแตะคอนฟิก/เทสต์นอกขอบเขต), และ (3) Blast Radius Budget

### 0.5. Pre-Ship Expansion Checklist (Zero Drip-Feeding Mandate)
ตรวจว่าได้ implement ครบตาม context หรือไม่:
- **UI States:** Loading State, Error State, Empty State, Disabled State
- **Responsive & A11y:** Mobile breakpoints (md/lg), `aria-label`, keyboard navigation
- **Error & Validation:** try/catch + user-facing error message, `safeParse` บน external input ทุกจุด
- **Proportionality Boundary:** อนุญาตเฉพาะ Direct Component States และ Local Input Validation ห้ามติดตั้งไลบรารีเพิ่มหรือ Refactor นอก Seam โดยไม่ได้รับคำสั่ง (ข้อยกเว้น: ผู้ใช้สั่งชัดเจนว่าต้องการ "minimal/prototype")

### 1. อ่านสเปกและระบุจุดเชื่อมต่อ (Inspect Seams)
- อ่านเป้าหมายจาก Artifact `plan.md` หรือคำสั่งของผู้ใช้
- กำหนด **Seam (รอยต่อระบบ)**: Public Interface, API Endpoint, หรือฟังก์ชันหลัก
- ตรวจสอบ Type Contracts ให้สอดคล้องกันทั้งระบบ

### 2. วงรอบ TDD แนวตั้ง (Vertical Slice Red-Green Loop)
1. **Red Stage:** เขียน Unit/Integration Test ที่ Seam ล่วงหน้า รันแล้วต้องล้มเหลว (Expected Failure)
2. **Green Stage:** เขียนโค้ดเฉพาะส่วนที่จำเป็นเพื่อให้เทสต์ผ่าน
3. **Deep Refactor:** ซ่อนตรรกะซับซ้อนไว้เบื้องหลัง Public API ที่เรียบง่าย (Deep Interface)

### 3. มาตรฐานวิศวกรรม Full-Stack & Modern React 19
- **Server Component First:** รันบน Server เป็นค่าเริ่มต้น เพื่อความเร็วและลด Bundle size
- **Server Action Protection:** ใส่ `import 'server-only'` ในไฟล์ที่แตะ DB หรือ Secret เสมอ
- **Type-Safe Validation:** ตรวจสอบ Input ด้วย Zod Schema (`schema.safeParse()`) บน Server ทุกครั้ง
- **Discriminated Union:** คืนค่า `{ success: true, data } | { success: false, error, fieldErrors }`
- **Deterministic Contracts:** ฟังก์ชัน LLM Classifier ต้องครอบด้วย Typed Schema (Pydantic / Zod) ห้าม Parse Free-text

### 4. ด่านตรวจสอบความสมบูรณ์ (Compilation & Health-Check)
ก่อนส่งมอบงาน ต้องรันการตรวจสอบ 3 ประการเสมอ:
1. `git status` — ยืนยันว่าไม่มีไฟล์แปลกปลอมหลุดออกไป
2. `tsc --noEmit` (หรือ linter ประจำโปรเจกต์) — ผ่านโดยไม่มี Type Error
3. `test suite` (`vitest` / `pytest` / `npm test`) — ทุกเทสต์ต้องเป็นสีเขียว (Pass 100%)

### 5. Self-Healing Loop (Autonomous Error Recovery)
ถ้าด่าน §4 ไม่ผ่าน → **ห้ามรายงานผู้ใช้ทันที** ให้:
1. อ่าน error output อย่างละเอียด — ระบุ root cause ให้แม่นก่อน
2. แก้ต้นตอโดยตรง (ไม่ใช่ workaround, ห้ามแก้ Test Assertion ให้อ่อนลง, และห้ามใส่ Mock หลอกตา)
3. **Epistemic Reset:** หากแก้รอบที่ 1 ไม่ผ่าน ห้ามแก้ซ้ำทางเดิม ให้ Reset สมมติฐานใหม่ด้วย Debug 4-Probes (Env / Boundary / Concurrency / Drift)
4. รันด่านตรวจสอบซ้ำบน In-process / Live runtime จริง (วน Loop สูงสุด 3 รอบ หากยังไม่ผ่านให้ Circuit Break ทันที)

---

FINAL STEP: ส่งมอบงานด้วย **10-Second Executive Judge Scorecard** (ตาม [`references/judge-scorecard-template.md`](references/judge-scorecard-template.md)) และแนะนำให้ผู้ใช้รัน `/review` สำหรับ Security Audit รอบสุดท้าย
