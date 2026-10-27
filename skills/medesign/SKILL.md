---
name: medesign
description: "ออกแบบ UI/UX เว็บ/แอป และสื่อกราฟิกครบวงจร (สไลด์ แบนเนอร์ โลโก้) — ใช้เมื่อสร้างเว็บ สไลด์ หรือสื่อนำเสนอ (Curated UI/UX & Graphic design suite: slides, banners, mockups, brand tokens)"
---

# ME-DESIGN: Personal & Production UI/UX Design Engine (`/medesign`)

ระบบสถาปัตยกรรมการออกแบบ UI/UX และสื่อกราฟิกมาตรฐานสากล รองรับ 74 แบรนด์ดัง และ 38 Argon Archetypes พร้อมระบบ Brief Intake, Anti-AI Invariants และ Deterministic Auto-Compiler

---

> **Router Rule:** อ่านเฉพาะไฟล์ที่งานนั้นต้องใช้ และต้องผ่าน `references/quality-gate.md` ก่อนส่งมอบโค้ดเสมอ

## 1. Unified Routing & Command Table

| คำสั่ง / หมวดงาน | การทำงานหลัก | เอกสารอ้างอิงที่ต้องอ่าน |
|---|---|---|
| `/medesign new` | ออกแบบ UI ใหม่จากศูนย์ (เสนอ Direction A/B) | `references/brief-intake.md` -> `design-core.md` |
| `/medesign revamp` | รีดีไซน์ UI เดิม ปรับ Layout & Spacing คง Logic เดิม | `references/brief-intake.md` -> `redesign-audit.md` |
| `/medesign like [แบรนด์]` | อ้างอิงสุนทรียภาพจากเว็บดัง/แบรนด์ (linear, apple, stripe) | `references/brand-design-tokens.md` -> `design-core.md` |
| `/medesign audit [path]` | ตรวจจับ AI Tells, สแกน Accessibility, คืนคะแนน Q-Score | `references/redesign-audit.md` -> `quality-gate.md` |
| `/medesign polish [path]` | ซ่อมโค้ดอัตโนมัติ (Google Fonts, Bento, OKLCH, 44px Halo) | รัน `node bin/medesign.js polish [path]` |
| `/medesign metha` | **Metha Cockpit:** สไตล์วิศวกรรมรังวัด (3-Pane, Tabular Mono) | `presets/metha/guidelines.md` + `design-tokens.css` |
| `/medesign slides` | สไลด์นำเสนอ Interactive (รับทั้ง `slides` และ `--slides`) | `references/slides.md` |
| `/medesign report` | รายงานบริหาร (Executive PDF & Print-ready) | `references/executive-reports.md` |
| `/medesign banner` | แบนเนอร์ โฆษณา ปกโซเชียลตามขนาดมาตรฐาน | `references/banner-sizes-and-styles.md` |
| `/medesign social` | ภาพถ่ายและกราฟิกโซเชียลมีเดีย | `references/social-photos-design.md` |
| `/medesign logo` | ออกแบบโลโก้ AI และระบบอัตลักษณ์ CIP | `references/logo-design.md` + `references/cip-design.md` |
| `/medesign icon` | ไอคอน SVG และ Icon Sets พร้อมสเกลพิกเซล | `references/icon-design.md` |
| `/medesign extract [url]` | ถอด Style Tokens จากภาพ/URL เป็น CSS Variables | `references/style-extraction.md` |
| `/medesign mockup` | สร้างภาพต้นแบบ Mockup (Web/Mobile) | `references/image-mockup-direction.md` |
| `/medesign to-code` | แปลงภาพ Mockup เป็นโค้ดจริงระดับ Production | `references/image-to-code.md` -> `quality-gate.md` |
| `/medesign snapshot` | จับภาพเรนเดอร์จริง High-DPI (Mobile, Tablet, Desktop) | `references/modern-craft-invariants.md` |

---

## 2. ลำดับความสำคัญในการเลือกโหมด (Mode Precedence Hierarchy)

1. **คำสั่งชัดเจนชนะทุกกรณี:** `/medesign new`, `/medesign revamp`, `/medesign like` ข้ามการเดาทั้งหมด แล้วเข้าสู่ `references/brief-intake.md` ทันที
2. **การอนุมานเมื่อไม่ได้ระบุโหมด:** อิงตาม `references/brief-intake.md` (อ้างอิงแบรนด์ -> `like`, มีโค้ดเดิม -> `revamp`, ทำใหม่หมด -> `new`)
3. **โหมด audit:** ตรวจจับจุดบกพร่อง/AI Tells ในหน้าเดิม (เมื่อสั่ง `/medesign audit` หรือถูกเรียกต่อจาก `revamp`)
4. **Interactive Cockpit Gate:** เมื่อสั่ง `/medesign` เปล่า ให้เปิด `ask_question` ให้เลือกหมวดหมู่งานทันที

---

## 3. Execution Protocol (5 ขั้นตอนมาตรฐาน)

1. **Step 0 — Brief Intake Gate (`references/brief-intake.md`):**
   - บรรทัดแรกของคำตอบต้องประกาศ `โหมด: new` (หรือ `revamp` / `like`) เสมอ
   - สรุป Brief 5 ช่อง และเสนอ 2 ทิศทางสั้นๆ (Direction A ใกล้ brief / Direction B ต่างชัดเจน ไม่เกิน 5 บรรทัดต่อทิศทาง)
   - *One-Shot Alignment:* หาก Brief ครบ เสนอทิศทางทันที; หากไม่ครบ ถาม $\le 3$ คำถาม พร้อม Direction ชั่วคราว (ตอบ "ok" = เลือก A)
   - *Escape Hatch:* ข้ามได้ทันทีเมื่อผู้ใช้ระบุ "ลุยเลย" หรือแก้งาน "จุดเล็ก" ($\le 1$ ไฟล์ และไม่เปลี่ยน layout/สี/ฟอนต์)
2. **Step 1 — Triage Stack:** ตรวจสอบเทคโนโลยีปลายทาง (Tailwind, Pure CSS, React, Next.js, HTML)
3. **Step 2 — Token Injection:**
   - **Neutral Craft (Default):** อ้างอิง 74 แบรนด์ หรือ 38 Archetypes และ Closed Spacing (2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128px)
   - **Personal DNA Sync:** ใช้เมื่อผู้ใช้สั่ง `/medesign auto` หรือ `/medesign metha` เท่านั้น
4. **Step 3 — Build & Deliver:** ส่งโค้ดที่สมบูรณ์ ไร้ Placeholders พร้อมรายงาน Visual Highlights สั้นๆ
5. **Step 4 — Quality Gate:** ตรวจสอบกับ `references/quality-gate.md` (Squint Test, Grayscale, 10-State Matrix) ปิดท้ายด้วย `Gate: quality-gate.md - pass` เสมอ **เฉพาะข้อความที่ส่งมอบโค้ดเท่านั้น**
