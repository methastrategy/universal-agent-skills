# Exhaustive System Blueprint & Architecture Dissection

มาตรฐานการผ่าซากชำแหละโครงสร้างระบบ โค้ดเบส หรือชุดข้อมูลขนาดใหญ่ (System Architecture Blueprint) ให้เห็นพิมพ์เขียว แผนผังความเชื่อมโยง ทางเดินข้อมูล (Data Flow) และแจกแจงทุกโมดูลแบบไร้กล่องดำ

---

## 1. ระเบียบวิธี 5 ขั้นตอน (5-Stage Deep Dissection)

### Stage 1: Discovery & Perimeter Scanning (สำรวจภาพรวมและขอบเขต)
- **Tech Stack & Inventory:** ตรวจสอบไฟล์คอนฟิกหลัก (`package.json`, `pyproject.toml`, Dockerfile, schemas)
- **Directory Topology:** วาดแผนผังโฟลเดอร์หลัก แยกตาม Tier (UI, API, Domain, Data, Infra)

### Stage 2: Component Decomposition (แจกแจงแยกชิ้นส่วนระดับโมดูล)
- **Entry Points:** หาจุด Bootstrapper และ Routing หลัก
- **Module Dictionary:** ทำตารางระบุความรับผิดชอบ หน้าที่ อินพุต เอาต์พุต และความเชื่อมโยงของทุกโฟลเดอร์
- **Schema Catalog:** ระบุ Data Entities, Tables, และความสัมพันธ์ (1:1, 1:N, N:M)

### Stage 3: Dynamic Data Flow Tracing (แกะรอยทางเดินข้อมูล)
- แกะรอย Flow จากต้นทางไปปลายทาง:
  `Ingress (UI/Trigger/API) -> Middleware/Auth -> Service/Domain Logic -> Storage/Database -> Egress/Presentation`

### Stage 4: Visual Architecture Mapping (สร้างแผนผังให้เห็นภาพชัดเจน)
- สร้าง Mermaid Diagrams แสดง Layer สถาปัตยกรรม และ Data Flowchart

### Stage 5: Structural Critical Evaluation (ประเมินจุดวิกฤต)
- ระบุ Single Points of Failure (SPOF), Invariants, และ Technical Debt

---

## 2. รูปแบบรายงานพิมพ์เขียวมาตรฐาน (Standard Output Blueprint)

เมื่อเรียกใช้งานโหมดพิมพ์เขียว ให้ส่งมอบรายงานตามโครงสร้างนี้:

```markdown
# 🗺️ Structural Architecture Blueprint: [ชื่อระบบ/โปรเจกต์]

## 1. Executive Essence & System Topology
- **System Purpose**: วัตถุประสงค์หลักของระบบ
- **Tech Stack Matrix**: Runtimes, Frameworks, Databases, Libraries
- **Architectural Paradigm**: (Clean Architecture, Modular Monolith, Pipeline ELT ฯลฯ)

## 2. Visual Architecture & Component Topology
[Mermaid Diagram แสดง Architecture Layers, Services และ Database]

## 3. Exhaustive Directory & Module Dictionary
| Directory / Module Path | Tier / Role | Core Responsibility | Key Files / Entry Points | Depends On |
| :--- | :--- | :--- | :--- | :--- |

## 4. Data Architecture & Schema Dissection
- **Data Entities & Schema Models**: Tables, Key Fields, Types, Relations
- **Data Lifecycle Flowchart**: [Mermaid Diagram: Source Ingestion -> Storage -> Output]

## 5. End-to-End Execution & Data Flow
- **Primary Execution Flow**: การเดินทางของข้อมูลทีละขั้นตอน
- **State & Caching Strategy**: การเก็บ Session, State และ Cache

## 6. Infrastructure, Environments & Secrets
- **Configuration & Env**: ตัวแปรสภาพแวดล้อมและ Config สำคัญ
- **External Integrations**: Third-party APIs และ Cloud Services

## 7. Critical Invariants & Bottlenecks
- **System Invariants**: กฎเหล็กที่ห้ามละเมิดในโค้ดเบสนี้
- **Bottlenecks / Risks**: จุดเปราะบางที่ต้องระวัง

## 8. Thai Structural Synthesis
- บทวิเคราะห์และสรุปภาพรวมโครงสร้างภาษาไทย
```
