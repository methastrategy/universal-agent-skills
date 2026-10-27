# Architectural Diagram Catalog (44 Archetypes Framework)

แค็ตตาล็อกรูปแบบไดอะแกรมสถาปัตยกรรม (อ้างอิงจาก `diagram-design` archetypes) สังเคราะห์และคัดกรองให้เหมาะสมกับการวิเคราะห์ระบบและสื่อสารทางเทคนิคของ Coding Agent

---

## 1. Flow & Pipeline Archetypes (การไหลของข้อมูลและขั้นตอนประมวลผล)

ใช้เมื่อต้องการอธิบาย Data Pipelines, Event Streaming, ETL หรือ Background Task Execution

### 1.1 Sequential Ingestion Pipeline
```mermaid
flowchart LR
    Raw["Raw Ingress Stream"] --> Val["Schema Validation (safeParse)"]
    Val --> Filter["Sanitization & Deduplication"]
    Filter --> Batch["Micro-Batch Buffer"]
    Batch --> Sink[("Persistent Data Store")]
```

### 1.2 Fan-Out / Fan-In Parallel Worker Pipeline
```mermaid
flowchart TD
    Ingress["Job Dispatcher"] --> Q1["Worker Queue A"]
    Ingress --> Q2["Worker Queue B"]
    Ingress --> Q3["Worker Queue C"]
    Q1 --> Agg["Aggregator Node"]
    Q2 --> Agg
    Q3 --> Agg
    Agg --> Result["Unified Response"]
```

---

## 2. Structural & Topology Archetypes (ผังสถาปัตยกรรมและโครงสร้างโมดูล)

ใช้เมื่อวิเคราะห์ขอบเขตของ Deep Modules, Package Dependencies หรือ Network Topology

### 2.1 Hexagonal Architecture (Ports & Adapters)
```mermaid
flowchart TD
    subgraph Drivers["Driving Adapters"]
        HTTP["REST / GraphQL API"]
        CLI["Admin CLI"]
    end

    subgraph Core["Core Application Domain"]
        PortIn["Input Ports (Use Cases)"]
        Domain["Domain Entities & Logic"]
        PortOut["Output Ports (Gateways)"]
        PortIn --> Domain
        Domain --> PortOut
    end

    subgraph Driven["Driven Adapters"]
        DB[("PostgreSQL / Prisma")]
        Queue["Message Broker (Kafka)"]
    end

    HTTP --> PortIn
    CLI --> PortIn
    PortOut --> DB
    PortOut --> Queue
```

### 2.2 Monorepo Boundary & Dependency Flow
```mermaid
flowchart TD
    AppA["apps/web"] --> LibUI["packages/ui"]
    AppA --> LibAPI["packages/api-client"]
    AppB["apps/mobile"] --> LibAPI
    LibUI --> LibTokens["packages/tokens"]
    LibAPI --> LibSchema["packages/shared-schema"]
```

---

## 3. Sequence & Protocol Handshake Archetypes (ลำดับการสื่อสาร)

ใช้เมื่ออธิบาย OAuth flows, API Authentication, Handshake หรือ Real-time WebSockets

### 3.1 Gated Auth & Token Refresh Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Gateway as API Gateway
    participant Auth as Auth Service
    participant Resource as Protected Resource

    Client->>Gateway: Request with Access Token
    Gateway->>Gateway: Verify Token Expiry
    alt Token Valid
        Gateway->>Resource: Forward Request
        Resource-->>Client: 200 OK + Payload
    else Token Expired
        Gateway-->>Client: 401 Unauthorized
        Client->>Auth: Request Refresh (Refresh Token)
        Auth-->>Client: New Access Token
        Client->>Gateway: Retry Request with New Token
        Gateway->>Resource: Forward Request
        Resource-->>Client: 200 OK + Payload
    end
```

---

## 4. State Machine & Lifecycle Archetypes (สถานะและวงจรชีวิต)

ใช้เมื่อระบุวงจรชีวิตของ Entity (Orders, Connection pools, Job status)

### 4.1 Order & Payment Finite State Machine
```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> PendingPayment: Checkout Submitted
    PendingPayment --> Paid: Webhook Verified
    PendingPayment --> Cancelled: Payment Timeout
    Paid --> Processing: Order Dispatched
    Processing --> Delivered: Carrier Confirmed
    Delivered --> [*]
    Processing --> Refunded: Dispute Approved
    Refunded --> [*]
    Cancelled --> [*]
```

---

## 5. Decision & Risk Triage Trees (การตัดสินใจและการประเมินความเสี่ยง)

ใช้เมื่อออกแบบทางแยกตรรกะ, Confidence Gating, หรือ TDD Seam triage

### 5.1 System 1 vs System 2 Execution Gating
```mermaid
flowchart TD
    Req["Incoming Task"] --> RiskCheck{"Blast Radius >= 2 or Financial?"}
    RiskCheck -- No --> ConfCheck{"Model Confidence P >= 0.85?"}
    RiskCheck -- Yes --> GateAsk["ask_question Modal (Confirm with User)"]
    ConfCheck -- Yes --> FastExec["Autonomous Fast Execution"]
    ConfCheck -- No --> EpistemicReset["Epistemic Reset (4-Probes Triage)"]
    EpistemicReset --> GateAsk
    GateAsk --> Approved["Proceed with Execution"]
```

---

## 6. Component Anatomy Archetypes (โครงสร้างส่วนประกอบ UI)

ใช้เมื่ออธิบายสัดส่วนของ Component, Slot compositions, และ Visual Seams

```mermaid
flowchart TD
    subgraph Card["Interactive Card Anatomy"]
        Header["Card Header (Title + Action Pill)"]
        Divider1["1px Border Divider"]
        Body["Card Body (Dynamic Data Slot)"]
        Divider2["1px Border Divider"]
        Footer["Card Footer (Metadata + Secondary Buttons)"]
    end
```

---

## 7. กฎการเลือกใช้ไดอะแกรม (Selection Heuristics)
1. **ลำดับเวลา / ขั้นตอน:** ใช้ Flowchart หรือ Sequence Diagram
2. **ขอบเขตโมดูล / ความสัมพันธ์:** ใช้ Hexagonal หรือ Package Dependency Flowchart
3. **การเปลี่ยนสถานะ:** ใช้ State Diagram เสมอ (ห้ามใช้ Flowchart สับสน)
4. **การประเมินความเสี่ยง:** ใช้ Decision Tree ชี้แจงทางแยกเงื่อนไข
