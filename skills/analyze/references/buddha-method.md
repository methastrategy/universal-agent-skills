# Disciplined Reasoning & Complex Root-Cause Resolution (Buddha Method)

Apply disciplined reasoning using Buddhist working principles to resolve complex engineering bottlenecks, difficult debugging scenarios, critical claim verification, and high-uncertainty architecture decisions.

Use for:
- Complex multi-layered reasoning
- Debugging elusive or non-deterministic problems
- Verifying critical claims and system invariants
- Resolving high-stakes architectural dilemmas

---

## The 4 Buddhist Pillars of Engineering

1. **Epistemic Filtering (กาลามสูตร):** คัดกรองความจริง แยกข้อเท็จจริงเชิงประจักษ์ (Evidence Tier 1-2) ออกจากสมมติฐานลอยๆ (Tier 4) ห้ามเดาจากความจำ
2. **Systems & Causal Decomposition (โยนิโสมนสิการ & อิทัปปัจจยตา):** แยกแยะองค์ประกอบระบบและสืบค้นสายโซ่เหตุ-ผล อย่างน้อย 3 ระดับ ไม่หยุดแค่การปะผุอาการภายนอก
3. **4-Stage Diagnostic Framework (อริยสัจ 4):**
   - **ทุกข์ (Dukkha - Defect/Bottleneck):** ระบุอาการและผลกระทบเชิงประจักษ์
   - **สมุทัย (Samudaya - Root Cause):** ต้นตอและเงื่อนไขตายตัวที่ทำให้เกิดปัญหานี้
   - **นิโรธ (Nirodha - Target State):** สภาวะความสำเร็จที่ปัญหานี้ถูกกำจัดถาวร พร้อม Invariants ที่ต้องเป็นจริง
   - **มรรค (Magga - Remediation Path):** แผนปฏิบัติการแก้โค้ด/สถาปัตยกรรมเป็นขั้นตอน
4. **Optimal Equilibrium (มัชฌิมาปฏิปทา):** ชั่งน้ำหนักทางสายกลาง หลีกเลี่ยงทั้ง Over-engineering ที่เกินจำเป็น และ Negligence ที่ก่อหนี้ระยะยาว

---

## The 6-Step Disciplined Process

### Step 1 — Kalāma (Verification / กาลามสูตร)
- **Identify claims** that require empirical verification.
- **Differentiate** between verified facts and assumptions.
- **Do not trust memory** or past patterns blindly.
- **If uncertain**, explicitly state uncertainty.

### Step 2 — Yoniso Manasikāra (Root Cause Analysis / โยนิโสมนสิการ)
- **Identify at least 3** potential root causes.
- **Focus on the source**, never stop at symptoms.
- **Ask**: *What conditions must be true for this behavior to occur?*

### Step 3 — Sati-Sampajañña (State Awareness / สติสัมปชัญญะ)
- **Verify current state**, live telemetry, and execution context.
- **Do not rely** on assumptions from previous runs or stale states.
- **Stay present** with the actual observed runtime behavior.

### Step 4 — Anatta (Resetting Thinking / อนัตตา)
- **Discard flawed approaches** immediately without ego or attachment.
- **Rethink from the beginning** if the foundation is broken.
- **Avoid patching** fundamentally flawed logic.

### Step 5 — Pahāna (Eradication / True Fix / ปหานะ)
- **Determine** if a solution is a permanent root fix or a temporary workaround.
- **Prefer absolute eradication** of the root cause.
- **If a workaround is necessary**, clearly document its limits.

### Step 6 — Upekkhā (Equanimity & Objectivity / อุเบกขา)
- **Ignore emotional pressure**, rush, or fatigue.
- **Base decisions strictly** on evidence and observed data.
- **Maintain direction** unless new evidence demands a change.

---

## Output Structure

- **Verified Facts**: Empirical data from codebase and runtime execution.
- **Root Cause**: The underlying condition leading to the issue.
- **Trade-Off Matrix**: Comparative analysis of at least 2 architectural choices.
- **Recommended Action**: The optimal, permanent path forward.
- **Risks & Invariants**: Trade-offs or remaining boundary considerations.
- **Immediate Next Step**: The specific next operational move.

---

## Operating Rules

- **Concise & Dense**: Say more with fewer, high-density words.
- **Structured**: Clean bullet points, comparative matrices, or Mermaid diagrams.
- **Evidence-Based**: No guessing or speculating without empirical data.
