---
name: analyze
description: "วิเคราะห์ระบบ โค้ด สถาปัตยกรรม และรากเหง้าปัญหาเชิงลึก — ใช้เมื่อตรวจหาคอขวด ผ่าโครงสร้าง หรือวิเคราะห์สาเหตุแท้จริง (Deep system architecture audit, root-cause diagnostics, structural blueprint)"
---

# Deep System Analysis & Root-Cause Architecture (`/analyze`)

วิเคราะห์ระบบ โค้ด สถาปัตยกรรม และเส้นทางเดินข้อมูลเชิงลึก ผสานขุมพลังการวินิจฉัยรากเหง้าปัญหาเชิงวิศวกรรม (4-Stage Root-Cause Diagnostics) และการสร้างพิมพ์เขียวผ่ากายวิภาคโปรเจกต์ (Structural Blueprint)

---

## 1. การทำงานแบบ Zero-Flag Intuitive Dispatch

> [!IMPORTANT]
> **ผู้ใช้ไม่ต้องจำหรือพิมพ์ `--flag` ใดๆ ทั้งสิ้น**: ระบบจะจัดเส้นทางงานให้โดยอัตโนมัติ 2 ระดับ:
> 1. **Auto-Detect Intent (เมื่อสั่งพร้อมข้อความ):** AI วิเคราะห์เนื้อหาและตัดเข้าโหมดย่อยที่ถูกต้องทันที
> 2. **Interactive Cockpit Gate (เมื่อสั่ง `/analyze` เปล่า):** AI จะเปิด `ask_question` Modal ให้คลิกเลือกทันที 1 วินาที

### A. Auto-Detection Matrix (ทำงานอัตโนมัติตามบริบท)

| สิ่งที่ตรวจพบในข้อความ / บริบท | โหมดที่ระบบเลือกใช้อัตโนมัติ | กลไกเบื้องหลัง |
| :--- | :--- | :--- |
| **มี Error / Crash / Stack Trace / คำว่า "แก้บั๊ก", "พัง"** | **Defect Isolation & Fix** | ล่าต้นตอปัญหา 5 ขั้นตอน ซ่อมโค้ดถึงรากเหง้าและตรวจ regression ทันที |
| **มีคำว่า "โครงสร้าง", "ภาพรวมระบบ", "แผนที่", "สถาปัตยกรรม"** | **Graph-First Memory Map** | เรียกใช้ `codebase-memory` (`index_repository`, `get_architecture`) สรุป God Nodes และคลัสเตอร์ |
| **มีคำว่า "ตรวจสอบ", "audit", "เช็คระบบ", "security", "ช่องโหว่"** | **Unified Deep Audit** | รันตรวจสอบ 4 มิติ (Architecture + Security OWASP + Logic Seams + Code Quality) |
| **มีคำว่า "ทำไม", "สาเหตุ", "วิเคราะห์", "ช้า", "คอขวด"** | **Root-Cause Diagnostics** | วิเคราะห์รากเหง้าด้วย 4-Stage Root Cause Chaining และ Epistemic Filtering |
| **คำถามทั่วไปเกี่ยวกับโค้ด / สถาปัตยกรรม** | **Diagnostic Audit (Default)** | สรุปคอขวด, หนี้ทางเทคนิค, และ Risk Severity Matrix |

### B. Interactive Cockpit Gate (เมื่อพิมพ์ `/analyze` โดดๆ)
หากผู้ใช้พิมพ์ `/analyze` เปล่าโดยไม่มีข้อความบริบท ให้รันเครื่องมือ `ask_question` ทันทีเพื่อให้คลิกเลือกใน 1 คลิก:
- `(Recommended) 🔍 วิเคราะห์รากเหง้าปัญหา & คอขวดระบบ (Deep Root-Cause Diagnostics)`
- `🗺️ สำรวจแผนที่สถาปัตยกรรมระบบ (Graph-First Memory Map via codebase-memory)`
- `🛡️ ตรวจสอบระบบรอบด้าน 4 มิติ (Unified Codebase & Security Audit)`
- `🐞 ล่าบั๊กและซ่อมโค้ดด่วน (Defect Isolation & Autonomous Fix)`

### C. Optional Headless Flags (สำหรับผู้ใช้ขั้นสูงที่ต้องการระบุเจาะจง)
รองรับเป็นทางเลือกเพิ่มเติม: `--root-cause`, `--graph`, `--audit`, `--debug`, `--blueprint` (`--teardown`)

---

## 2. เสาหลักการวินิจฉัยรากเหง้าปัญหา (The 4-Stage Root-Cause Framework)

> [!IMPORTANT]
> **Internal Rigor, External Elegance Invariant (กฎเหล็กการนำเสนอผลลัพธ์):**
> ระเบียบวิธีคิดเชิงลึก (เช่น การสืบค้นสายโซ่เหตุ-ผล และการตัดสมมติฐาน) ทำหน้าที่เป็น **เลนส์คิดวิเคราะห์ภายในสมองของ AI เท่านั้น**  
> **ห้ามนำคำศัพท์ทางปรัชญาหรือศาสนามาแสดงเป็นหัวข้อในคำตอบเด็ดขาด** ให้ใช้หัวข้อวิศวกรรมสากล 4 มิติเสมอ:

1. **Epistemic Filtering (คัดกรองความจริง):** แยกข้อเท็จจริงเชิงประจักษ์ (Evidence Tier 1-2 จากคำสั่งจริง/โค้ดจริง) ออกจากสมมติฐานลอยๆ (Tier 4) ห้ามเดาจากความจำ
2. **Causal Backward Chaining (แกะรอยย้อนกลับ):** แยกแยะองค์ประกอบระบบและสืบค้นสายโซ่เหตุ-ผลอย่างน้อย 3 ระดับ ($T_0 \leftarrow T_{-1} \leftarrow T_{\text{Origin}}$)
3. **4-Stage Presentation Protocol (การจัดโครงสร้างรายงานตอบกลับผู้ใช้):**
   - **1. อาการและผลกระทบ (Symptom & Defect Signature):** สรุปอาการ คอขวด และความเสียหายเชิงประจักษ์
   - **2. ต้นตอและกลไกปัญหา (Root Cause & Mechanism):** ชี้ชัดเงื่อนไขและบั๊กที่เป็นต้นกำเนิดของปัญหา
   - **3. เป้าหมายและเกณฑ์ความสำเร็จ (Target State & Invariants):** นิยามสภาวะที่พึงประสงค์ และเงื่อนไขที่ต้องผ่าน 100%
   - **4. แผนปฏิบัติการแก้ไข (Remediation & Action Plan):** ขั้นตอนการแก้โค้ดหรือสถาปัตยกรรมแบบ Smallest Working Diff
4. **Optimal Equilibrium (มัชฌิมาปฏิปทา):** ชั่งน้ำหนักทางสายกลาง หลีกเลี่ยงทั้ง Over-engineering ที่เกินจำเป็น และ Negligence ที่ก่อหนี้ระยะยาว

---

## 3. ขั้นตอนการวิเคราะห์เชิงวินิจฉัย (Diagnostic Steps)

1. **Map System Boundaries**: ระบุขอบเขต Dependency หลัก, ข้อจำกัดทางสถาปัตยกรรม, และสัญญาเชื่อมต่อ (Input/Output Contracts)
2. **Deconstruct Data Pipelines**: แกะรอยคอขวด, จุดประมวลผลหนัก, และ Critical Blocking Paths
3. **Audit Against Quality Invariants**: ตรวจสอบตรรกะโค้ดเทียบกับเกณฑ์ความปลอดภัย (ห้าม Silent Failures, Deterministic State Mutations)
4. **Synthesize Findings**: จัดทำ Risk & Bottleneck Matrix ตามระดับความรุนแรง พร้อมเสนอแนวทางแก้ไขเป็นขั้นตอนเชิงโค้ด (Actionable Remediation)

---

## 4. สถาปัตยกรรมอ้างอิง (Reference Map)
- **คู่มือระเบียบวิธีคิดเชิงลึก 6 ขั้น:** อ่าน [references/buddha-method.md](references/buddha-method.md) (Internal Epistemic Reasoning Manual)
- **การสร้างพิมพ์เขียวและผ่าโครงสร้างระบบเต็มรูปแบบ:** อ่าน [references/system-blueprint.md](references/system-blueprint.md)
- **การจำแนกประเภทเส้นและความสัมพันธ์ไดอะแกรม:** อ่าน [references/graph-edge-typing.md](references/graph-edge-typing.md)
- **แค็ตตาล็อกรูปแบบไดอะแกรมสถาปัตยกรรม 44 แบบ:** อ่าน [references/diagram-catalog.md](references/diagram-catalog.md)
- **สถาปัตยกรรมแผนผังนำทาง AST Codebase:** อ่าน [references/repo-map-protocol.md](references/repo-map-protocol.md)
- **AST Knowledge Graph & โครงสร้างเชิงลึก:** เรียกใช้ `codebase-memory` MCP tools (`index_repository`, `search_graph`, `trace_path`, `get_architecture`)
- **Quant Trading Dashboard Patterns:** อ่าน [references/quant-trading-dashboard-patterns.md](references/quant-trading-dashboard-patterns.md)

---

## 5. กฎเหล็กการปฏิบัติงาน (Operating Rules)

- **ห้ามให้คำแนะนำลอยๆ:** ทุกข้อสังเกตต้องอ้างอิงไฟล์จริง บรรทัดโค้ดจริง หรือตัวเลข Telemetry ที่วัดผลได้
- **แก้ที่ต้นตอถาวร (Permanent Eradication):** หากจำเป็นต้องใช้ Workaround ชั่วคราว ต้องระบุข้อจำกัดและเงื่อนไขการอัปเกรดให้ชัดเจนเสมอ
- **เน้นจุดที่มีผลกระทบสูง (High-Impact):** จัดลำดับความสำคัญของคอขวดระบบมากกว่าเรื่องรูปแบบการเขียนโค้ดทั่วไป
- **Visual-First:** นำเสนอความเชื่อมโยงด้วยไดอะแกรม Mermaid หรือตารางเปรียบเทียบเสมอ
