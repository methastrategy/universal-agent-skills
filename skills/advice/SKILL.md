---
name: advice
description: "คณะที่ปรึกษาหลายมุมมองและกล่องชี้ขาดทางเลือก — ใช้เมื่อต้องตัดสินใจเรื่องยาก ลังเล ต้องการคำแนะนำรอบด้าน หรือเคาะทางออกที่ดีที่สุด (Multi-perspective advisory board, decision cockpit, interactive ask_question modal)"
---

# Multi-Perspective Advisory & Decision Cockpit (`/advice`)

ระบบจำลองคณะที่ปรึกษาหลายมุมมองเพื่อประเมินทางเลือก สถาปัตยกรรม กลยุทธ์การเทรด และงานวิศวกรรมสำรวจ พร้อมกลไกผ่าทางตันและยิงกล่องโต้ตอบตัดสินใจ (`ask_question`) ทันที

---

## 1. วงจรการทำงาน (Execution Lifecycle)

เมื่อได้รับคำสั่ง `/advice` หรือเมื่อผู้ใช้เผชิญทางแยกการตัดสินใจที่ซับซ้อน:

1. **Zero-Context Friction Harvest**:
   - กวาดอ่านบริบทจากบทสนทนาล่าสุดโดยอัตโนมัติ สกัดโจทย์ ปัญหาทางเทคนิค ตัวเลือกที่กำลังพิจารณา และผลกระทบ (Stakes) โดยที่ผู้ใช้ไม่ต้องพิมพ์ปูเรื่องใหม่
   - หากผู้ใช้ระบุหัวข้อชัดเจน (`/advice <topic>`) หรือเจาะจง Preset (`/advice --preset <name>`) ให้มุ่งเน้นตามหัวข้อที่ระบุ
2. **Domain Auto-Routing**:
   - เลือกชุดที่ปรึกษาเฉพาะทาง 1 ใน 4 ชุดตาม `references/perspectives-board.md`:
     - *Preset A: Software & System Architecture* (Maintainer vs Scale Architect vs Security Auditor vs Product Velocity vs FinOps)
     - *Preset B: Quantitative Finance & Trading* (Alpha Researcher vs Tail-Risk Guardian vs Data Skeptic vs Execution Realist)
     - *Preset C: Survey Engineering & Geomatics* (Geodetic Purist vs Field Commander vs Calibration Engineer vs Spec Auditor)
     - *Preset D: General Strategy & Business* (Operator vs Skeptic vs Visionary vs People Advocate vs Strategist)
3. **Clash & Kill-Shot Analysis (Hidden CoT)**:
   - ปะทะมุมมองแบบ Anti-Echo Chamber แต่ละฝ่ายใช้ "คำถามไม้ตาย (Kill-Shot Question)" โจมตีจุดอ่อนของข้อเสนอ
4. **Deadlock Resolution & Optimal Equilibrium**:
   - กรองผ่าน 3 ขั้นตอน:
     - *Step 1: Reversibility Filter* (Type 1 เสี่ยงถาวร $\to$ ฝ่ายความเสี่ยงมีสิทธิ์ Veto ทันที / Type 2 แก้ไขได้ $\to$ ฝ่ายโอกาสชนะ)
     - *Step 2: Empirical Evidence Hierarchy* (Tier 1 กฎคณิตศาสตร์/ฟิสิกส์ $\to$ Tier 2 ข้อมูลระบบจริง $\to$ Tier 3 มาตรฐาน $\to$ Tier 4 สมมติฐาน)
     - *Step 3: Validation Gate* (หากเสมอกัน ออกแบบ Time-Boxed Test เพื่อพิสูจน์ข้อผิดพลาด)
5. **Interactive Cockpit Trigger (MANDATORY)**:
   - รายงานสรุปจุดปะทะและชี้ธงคำแนะนำอย่างสั้นกระชับ ($\le 12$ บรรทัด)
   - **ต้องเรียกเครื่องมือ `ask_question` เสมอ** ปิดท้ายการวิเคราะห์ เพื่อยิงกล่อง Popup ให้ผู้ใช้คลิกเลือกทางออกได้ทันที
6. **Post-Decision Discipline & Checkpointing**:
   - เมื่อผู้ใช้เลือกตัวเลือกแล้ว ให้ปรับเข้าสู่โหมดวางแผน (`/plan`), บันทึก Checkpoint เป็น Markdown และสามารถใช้ `ask_question` เพิ่มเติมได้เสมอหากมีทางแยกย่อย

---

## 2. กฎการออกแบบกล่องตัวเลือก (Standard Options Schema)

ทุกครั้งที่เรียก `ask_question` ให้จัดเรียงลำดับตัวเลือกดังนี้:

- **Option 1 (Recommended):** `(Recommended) [ชื่อทางเลือก]: [เหตุผลหลักที่ชนะการประเมิน] (Trade-off: [สิ่งที่ต้องแลก])`
- **Option 2 (Alternative/Speed):** `[ชื่อทางเลือก]: [ข้อดี/ความรวดเร็ว] (Trade-off: [ความเสี่ยงหรือข้อจำกัด])`
- **Option 3 (Conservative/Safe):** `[ชื่อทางเลือก]: [ความปลอดภัยสูงสุด/ความเสี่ยงต่ำ] (Trade-off: [ความช้าหรือต้นทุน])`

*(ระบบมีช่อง Write-in ให้ผู้ใช้พิมพ์ข้อความเองโดยอัตโนมัติอยู่แล้ว)*

---

## 3. กฎเหล็กการปฏิบัติงาน (Operating Rules)

- **Anti-Interrogation Invariant:** ห้ามยิงกล่องคำถามก่อนการวิเคราะห์ ต้องสรุปทางเลือกและชี้ธงคำแนะนำ `(Recommended)` จากบริบทให้ผู้ใช้เห็นภาพก่อน แล้วจึงเด้งกล่อง `ask_question` ปิดท้ายเสมอ
- **Anti-Echo Chamber:** ห้ามตอบประนีประนอมแบบแทงกั๊ก ทุกบทบาทต้องมีจุดยืนชัดเจนและพร้อมค้านข้อเสนอที่ไม่รอบคอบ
- **Strict Evidence Grounding:** การตัดสินใจต้องอิง Tier 1-2 เป็นหลัก ห้ามให้น้ำหนักแก่สมมติฐานที่ไม่มีตัวเลขรองรับ

---

## 4. สถาปัตยกรรมอ้างอิง (Reference Map)
- **ชุดที่ปรึกษา 4 ด้านและกลไกผ่าทางตันฉบับเต็ม:** อ่าน `references/perspectives-board.md` (Domain Presets A–D, Kill-Shot Questions, 3-Step Tie-Breaker Protocol, Evidence Tiers 1–4)
