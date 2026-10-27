---
name: architect
description: "[วางแผนสถาปัตยกรรม] วางผังระบบ ออกแบบ Deep Modules และฐานข้อมูล — ใช้เมื่อเริ่มระบบใหม่หรือปรับโครงสร้างเดิม (System architecture, deep modules, clean backend, decision tree grilling, ADR, tradeoffs)"
---

# /architect — ศูนย์รวมการวางแผนและสถาปัตยกรรมระบบ (Unified Planning & Architecture Hub)

วางพิมพ์เขียว ออกแบบโครงสร้างซอฟต์แวร์ และเกลา Requirement ให้ตกผลึกทุกมิติ (System Topology + Deep Modules + Clean Backend + DB Schema) ก่อนเริ่มลงมือเขียนโค้ด

## สถาปัตยกรรมอ้างอิง (Reference Map)
- **การสัมภาษณ์เจาะลึก Requirement:** อ่าน `references/decision-tree-grilling.md` ( Decision Tree Grilling & Frontier )
- **การออกแบบโมดูลแบบลึก:** อ่าน `references/deep-modules.md` ( John Ousterhout's Deep Modules & Seams )
- **ระบบหลังบ้านและฐานข้อมูล:** อ่าน `references/backend-clean-architecture.md` ( Clean Architecture, DDD & SQL Indexing )
- **ภาษากลางและการตัดสินใจ:** อ่าน `references/domain-modeling.md` ( GLOSSARY.md & ADR records )
- **ตารางเปรียบเทียบชั่งน้ำหนัก:** อ่าน `references/tradeoff-matrix.md` ( Multi-dimensional Tradeoff Analysis )
- **รูปแบบใบสเปกและจุดทดสอบ:** อ่าน `references/spec-format.md` ( Formal Spec & Test Seams in plan.md )
- **การรองรับขยายตัว:** อ่าน `references/scalability.md` ( Stateless services & Caching topology )
- **วิศวกรรมสร้างเลียนแบบและการวัดความสมบูรณ์:** อ่าน `references/clean-room-parity-engineering.md` ( Clean-Room Reverse Engineering, Dual-Implementation Oracle, Parity Checklist Matrix, Agent-Drivable Interface )
- **จุดเชื่อมต่อ Agent ชนิดข้อมูลเข้มงวด:** อ่าน `references/typed-agent-boundary.md` ( PydanticAI / Instructor Schemas, Validation Retry Loops, Discriminated Unions )
- **กราฟกระบวนการ Agent แบบมีวงรอบ:** อ่าน `references/cyclic-agent-state-machines.md` ( LangGraph Cyclic States, Checkpointing, Conditional Edges )
- **การจัดทัพ Multi-Agent ด้วย SOPs:** อ่าน `references/multi-agent-sop-orchestration.md` ( MetaGPT / CrewAI SOP Primitives, Consensus Voting )
- **ลำดับชั้นสลับโหมดโมเดลสำรอง:** อ่าน `references/model-fallback-cascade.md` ( LiteLLM / vLLM / Ollama 3-Tier Fallback Cascade )
- **สถาปัตยกรรม Edge SQL และความปลอดภัย RLS:** อ่าน `references/edge-sql-and-rls-architecture.md` ( Drizzle / Kysely Type-Safe SQL, PostgreSQL Row Level Security )
- **เครือข่าย Zero-Trust และแทนแนลเสมือน:** อ่าน `references/zero-trust-tunnels-and-mesh.md` ( Tailscale WireGuard Mesh, Cloudflare Tunnels, ChaCha20 Crypto )
- **การเลือกโฮสติ้งและข้อจำกัดเชิงพาณิชย์:** อ่าน `references/frontend-hosting-matrix.md` ( Frontend Hosting, Cloudflare-First & Vercel Commercial TOS Invariants )

---

## กระบวนการวางแผน 5 ขั้นตอน (The Architecture Protocol)

### 1. เจาะลึกโจทย์และตีกรอบขอบเขต (Grill the Requirements)
- สำรวจโค้ดและสภาพแวดล้อมเดิมด้วยตัวเองก่อนเสมอ ห้ามถามสิ่งที่อ่านเองได้จากไฟล์ในเครื่อง
- หากโจทย์ยังคลุมเครือหรือมีหลายทางเลือก ให้ไล่ถามทีละกิ่งของ Decision Tree (ใช้ `ask_question` เมื่อมีตัวเลือกชัดเจน)
- กำหนด **Frontier**: ถามเฉพาะสิ่งที่จำเป็นต้องรู้ในรอบนั้น พร้อมระบุคำตอบที่แนะนำ (`(Recommended)`)

### 2. วางผังสถาปัตยกรรมและทางเดินข้อมูล (System Topology & Data Flow)
- ออกแบบ Component Boundaries และ Interface Contracts ระหว่าง Frontend ↔ Backend
- ยึดหลัก **Stateless Service**: แยก Application State ออกจาก Data Storage เพื่อความ Scalable
- กำหนด API Schema และรูปแบบการแลกเปลี่ยนข้อมูล (REST / gRPC / JSON-RPC / Zod Types)
- **Structured Decision Gating:** หากระบบมี AI Workflow ให้แยก Decision Node ออกมาตรวจคัดกรองด้วย Typed Schema (Score, Enum, Flags) ก่อนส่งต่อ Worker เพื่อคุม Latency, ค่า Token และ Determinism


### 3. โครงสร้างโค้ดแบบ Deep Modules (Codebase Design)
- ออกแบบโมดูลให้มี **Interface เล็กและเรียบง่าย** แต่ซ่อนตรรกะซับซ้อนไว้ภายในอย่างลึกซึ้ง
- กำหนด **Seam (รอยต่อของระบบ)**: จุดต่อภายนอกที่สามารถนำ Test หรือ Mock เข้ามาประกบได้
- หลีกเลี่ยง Shallow Modules (ไฟล์ย่อยๆ ที่แค่ส่งผ่านข้อมูลไปมาโดยไม่ลดทอนความซับซ้อน)

### 4. สถาปัตยกรรมหลังบ้านและฐานข้อมูล (Backend Clean Architecture & DB)
- ใช้โครงสร้าง **Feature-Driven (Vertical Slice)** รวมไฟล์ที่เกี่ยวข้องไว้ในโดเมนเดียวกัน เพื่อคุม Context Window ของ AI ให้โฟกัสตรงจุด ไม่แตกกระจัดกระจายแบบ Layer-by-Type
- บังคับใช้ **TypeScript Strict + Schema-First (Zod/Drizzle/Prisma)** ดักจับ Runtime Type Errors ทุกจุดเชื่อมต่อ
- แยก Domain Entity ออกจาก Framework และฐานข้อมูลภายนอก (Dependency Inversion)
- ออกแบบตาราง SQL พร้อมวางแผน Indexing (B-Tree สำหรับ Query หลัก, GiST สำหรับข้อมูลเชิงพื้นที่/พิกัด)
- วางขอบเขต ACID Transactions ป้องกัน Data Corruption หรือปัญหา N+1 Query

### 5. สรุปพิมพ์เขียวลง Artifact (`plan.md`)
- บันทึก Specification, ทางเดินข้อมูล, จุด Seams และรายการงานย่อยลงใน Artifact `plan.md`
- สรุป Domain Glossary คำศัพท์สำคัญของระบบ

---

FINAL STEP: เมื่อวางแผนและออกสเปกเรียบร้อย ให้แนะนำผู้ใช้สั่ง **`/build`** เพื่อเริ่มสร้างระบบตามแผนด้วย TDD ทันที
