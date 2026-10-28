---
name: domain-modeling
description: "ออกแบบและสรุปคำศัพท์โดเมนโค้ด (GLOSSARY.md) และบันทึกการตัดสินใจสถาปัตยกรรม (ADR) — ใช้เมื่อต้องการจัดระเบียบภาษากลางของโปรเจกต์ (Ubiquitous domain language modeling, GLOSSARY.md, and ADR documentation)"
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `GLOSSARY.md` for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

Most repos have a single context:

```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `GLOSSARY-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── GLOSSARY-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── GLOSSARY.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── GLOSSARY.md
│       └── docs/adr/
```

Create files lazily: only when you have something to write. If no `GLOSSARY.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `GLOSSARY.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update GLOSSARY.md inline

When a term is resolved, update `GLOSSARY.md` right there. Don't batch these up: capture them as they happen. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

`GLOSSARY.md` should be totally devoid of implementation details. Do not treat `GLOSSARY.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

---

## Domain-Logic Alignment & Build-vs-Buy Threshold (The One-Person SaaS Invariant)

เมื่อออกแบบระบบภายในสำหรับธุรกิจ (Internal Operations, POS, CRM, Logistics, Workflow Automation):

### 1. The Domain-Logic Mismatch Principle
- **สาเหตุของความล้มเหลวส่วนใหญ่:** ความไม่ตรงกันระหว่าง "ตรรกะหน้างานจริงของธุรกิจ (Shop-Floor Reality)" กับ "ข้อจำกัดของซอฟต์แวร์สำเร็จรูป" หรือ "การตีความผิดของโปรแกรมเมอร์ภายนอก"
- **The Invariant:** สถาปัตยกรรมของซอฟต์แวร์ภายในต้องจำลอง (Mirror) ลำดับขั้นตอนจริงของธุรกิจ 1:1 เสมอ ห้ามดัดแปลงหรือบิดเบือนกระบวนการทำงานของคนหน้างานเพื่อให้เข้ากับกรอบจำกัดของซอฟต์แวร์สำเร็จรูป

### 2. Build vs. Buy Decision Rubric
| มิติ | เลือกสร้างเองด้วย AI (Build In-House Micro-Tool) | เลือกซื้อ/เช่าบริการสำเร็จรูป (Buy Commodity SaaS) |
| :--- | :--- | :--- |
| **ความได้เปรียบทางธุรกิจ** | เป็นหัวใจของกระบวนการทำกำไร (Core Moat / Domain Secret) | เป็นงานสาธารณูปโภคทั่วไป (Non-Differentiating Commodity) |
| **ตัวอย่างงาน** | • ระบบตัดสต็อกเฉพาะทาง (เช่น อาหารแช่แข็ง, จิวเวลรี่)<br>• ระบบ POS/Order Flow ที่ออกแบบตามพฤติกรรมลูกค้าจริง<br>• ตัวคำนวณราคา/สูตรเฉพาะของโรงงาน | • Payment Gateway (Stripe, Omise)<br>• Transactional Email / SMS (Resend, Twilio)<br>• Cloud Infrastructure (Cloudflare Pages, Cloud Run) |
| **การประเมิน TCO** | ไร้ค่า Subscription รายเดือนต่อเนื่อง, ไร้ Key-Person Risk (ดูแลผ่าน AI Prompt & Git) | คุ้มกว่าการมาเขียน Compliance/Security/Banking เอง |

