---
name: backend-clean-architecture
description: "ออกแบบและเขียนโค้ดระบบหลังบ้าน (Backend API) และฐานข้อมูล — ใช้เมื่อสร้าง API (FastAPI/Node/Go/Python), ออกแบบตาราง DB หรือปรับจูน Query (Production backend Clean Architecture, DDD, REST/gRPC API, SQL indexing, and ACID transactions)"
---

# Production Backend & Clean Architecture Standards

Engineering guidelines for robust, maintainable, and high-performance backend systems.

## 1. Clean Architecture & Layered Boundaries
- **Entities & Value Objects (Domain Layer):** Core business logic with zero framework dependencies.
- **Use Cases / Interactors (Application Layer):** Orchestrates domain logic, executes transactions, defines DTO inputs/outputs.
- **Interface Adapters (Controller & Presenter Layer):** Converts HTTP/gRPC requests into use-case parameters, maps use-case results into JSON responses.
- **Frameworks & Drivers (Infrastructure Layer):** Database connections (SQLAlchemy, Prisma, GORM), external APIs, message brokers.

## 2. API Design & Standards (RESTful & gRPC)
- **Status Codes Discipline:**
  - `200 OK`: Successful read or update.
  - `201 Created`: Successful creation (include `Location` header where applicable).
  - `204 No Content`: Successful deletion or mutation with no response body.
  - `400 Bad Request`: Input validation failed (return structured validation errors with field paths).
  - `401 Unauthorized`: Missing or invalid authentication token.
  - `403 Forbidden`: Authenticated user lacks permission/scope for this resource.
  - `404 Not Found`: Resource does not exist.
  - `409 Conflict`: Duplicate key, version mismatch, or state conflict.
  - `429 Too Many Requests`: Rate limit exceeded (return `Retry-After` header).
- **Pagination Standard:** Use Cursor-based pagination (`cursor`, `limit`) for high-volume or dynamic lists instead of Offset-based pagination (`offset`, `limit`) to avoid performance degradation and skipped items.

## 3. Database Optimization & Indexing Strategies
- **Index Selection:**
  - Create B-Tree indexes on columns used in `WHERE`, `JOIN ON`, and `ORDER BY`.
  - Composite Indexes: Order columns by Equality first (`WHERE status = 'active'`), then Range (`AND created_at >= '...'`).
  - Avoid over-indexing: Every index slows down `INSERT`, `UPDATE`, and `DELETE`.
- **Transaction Safety & Locking:**
  - Wrap multi-table state changes in atomic transactions.
  - Use Optimistic Locking (version column) for high-read/low-write concurrency.
  - Use Pessimistic Locking (`SELECT ... FOR UPDATE`) with short timeouts for sensitive balance or inventory deductions.
  - Guard against Deadlocks: Always acquire locks on multiple resources in a consistent, deterministic order.

## 4. LLM-as-a-Judge & Structured Decision Gating Protocol
- **Decoupled Architecture (แยกคิดกับทำ):** ห้ามรวมงาน "ตรวจประเมิน/คัดกรอง" เข้ากับงาน "เขียนเนื้อหา/แก้โค้ด" ใน Prompt เดียวกัน ให้แยกเป็น **Decision Node** (ใช้โมเดลเล็ก/เร็ว เช่น Flash/SLM) และ **Execution Node** (Worker)
- **Strict Output Schema:** บังคับผลลัพธ์การตัดสินใจเป็น Typed Schema (Pydantic / Zod) เสมอ เพื่อให้โค้ด backend ทำ `if/else` ได้ทันทีแบบ 100% Deterministic:
  ```typescript
  interface EvaluationDecision {
    score: number;             // 0 - 10
    passed: boolean;           // boolean สำหรับ branching ทันที
    category: string;          // Enum ชัดเจน
    confidence: number;        // 0.0 - 1.0
    flags: string[];           // แฟล็กข้อบกพร่องสั้นๆ สำหรับส่งให้ Worker แก้ไขถูกจุด
  }
  ```
- **Zero Chat Free-Text Invariant:** ปิดการพ่นคำอธิบายยาวๆ ใน Decision Node เพื่อลด Latency จากหลักวินาทีเหลือระดับเสี้ยววินาที (~200ms) และประหยัดค่า Token ลงกว่า 95-99%

## 5. AI-Native Backend & Vertical Slice Architecture
เมื่อออกแบบหรือขึ้นโครงสร้าง Backend ร่วมกับ AI/LLM หรือ Vibe Coding:
- **Anti-Pattern (Horizontal Layer-by-Type):** หลีกเลี่ยงการแยกโฟลเดอร์ตามประเภทไฟล์ (`controllers/`, `services/`, `models/`, `routes/`) แบบเดิม เพราะทำให้ Context Window แตกกระจาย AI ต้องค้นและเปิดไฟล์ข้ามโฟลเดอร์ไปมา ส่งผลให้เกิด Hallucination ใน Signature ฟังก์ชัน และกิน Token สูง
- **Target Standard (Co-located Feature Slices):** จัดโครงสร้างแบบ Feature-Driven / Modular Monolith โดยรวมไฟล์ที่เกี่ยวข้องในโดเมนเดียวกันไว้ด้วยกัน:
  ```text
  src/modules/<feature>/
  ├── <feature>.routes.ts
  ├── <feature>.controller.ts
  ├── <feature>.service.ts
  └── <feature>.schema.ts      # Zod validation & Request/Response DTOs
  ```
- **Type-Safe Contract Invariant:** บังคับใช้ **TypeScript Strict Mode** ควบคู่กับ Schema Validation (Zod, TypeBox หรือ Drizzle/Prisma) ทุกจุดเข้า-ออกของ API เพื่อให้ Compiler และ Runtime Parser ทำหน้าที่เป็น Guardrail อัตโนมัติคอยดักตบ AI ทันทีที่มีการ hallucinate ชนิดข้อมูล
- **Anti-Premature Scaling Ladder:** ห้ามเพิ่มความซับซ้อนของโครงสร้างระบบก่อนมีคอขวดเชิงประจักษ์:
  1. *Tier 1 (เริ่มต้น - รองรับผู้ใช้หลักแสน):* Modular Monolith + Single RDBMS (PostgreSQL/SQLite) พร้อม Indexing ที่ถูกต้อง
  2. *Tier 2 (พบ Read/Write Bottleneck ชัดเจน):* Read Replicas + Redis Cache-Aside สำหรับ Hot Keys
  3. *Tier 3 (High Concurrency / Distributed Domain):* Event Streams (Kafka/RabbitMQ) + Sharded Storage (ทำเมื่อมี Telemetry พิสูจน์เท่านั้น)



