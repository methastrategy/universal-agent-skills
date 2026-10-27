---
name: merea
description: "วิเคราะห์คิดย้อนรอย ถอดรหัสกลไกต้นกำเนิด และสิ่งที่ควรจะเป็น — ใช้เมื่อแกะรอยระบบ ธุรกิจ โค้ด หรือไบนารี (Universal reverse engineering, REA binary deconstruction, backward causality)"
---

# /merea — Universal Reverse Engineering & REA Binary Engine

Deconstruct any observed outcome, system state, human behavior, business outcome, complex phenomenon, software binary, or packaged application back to its prime origins. Dissects underlying mechanics, models branching probabilities, exposes the causal chain, and synthesizes what **"should be"** according to first principles and natural laws.

> *"Invert, always invert: Turn a situation or problem upside down. Look at it backward. What happens if all our plans go wrong? Where don't we want to go, and how do you get there?"* — Carl Jacobi / Charlie Munger

---

## Tri-Modal Architecture (Auto-Detection)

1. **Universal Conceptual & Systems Mode (Default)**: Triggered by abstract questions, confusing ideas, business dilemmas, life situations, philosophical concepts, or societal trends. Deconstructs hidden incentives and First Principles. Reads [conceptual-reverse-engineering.md](references/conceptual-reverse-engineering.md).
2. **Software, Web & Binary Artifact Mode (Powered by REA)**: Triggered when inspecting software artifacts (`.exe`, `.dll`, `.so`, `.dylib`, `.apk`, `.asar`, `.wasm`, `.pyc`, web bundles, network logs, or raw code). Activates REA MCP tools and local binary deconstruction. Reads [rea-technical-guide.md](references/rea-technical-guide.md). ก่อนเริ่มทุกครั้ง: (a) เช็ก `rea --version` ตรงกับ `npm view rea-agents version` — mismatch = install เก่า ต้องอัปเกรดก่อน ไม่งั้น capability ที่จะใช้ยังไม่มีจริงบนเครื่อง; (b) รัน `rea providers` เพื่อดูว่ามี native engine ไหม ถ้าไม่มี ให้จำกัดขอบเขตไปที่ managed `.NET/CLI` หรือ artifact graph แทนการสัญญาว่าจะ decompile native. (c) **จำแนก packaging class จากไฟล์จริงก่อนเสมอ** (CLR / PyInstaller / Electron asar / installer SFX / Java / native arch) — REA มองไม่เห็น Python/PyInstaller หรือ installer เลย การเดาจากชื่อโฟลเดอร์หรือ marker ข้างเคียงทำให้สรุปผิด class และเสียเวลาหนึ่งรอบเต็ม; ตารางสัญญาณอยู่ใน section 1.1. Workflow หลักคือ managed pipeline: `inspect-managed-artifact` → `inspect-managed-members --format json` → ห่อเป็น `{"managed_members": <evidence>}` → `project-managed-application-graph` แล้ว BFS ตาม edge `calls` เพื่อเอา feature pipeline. Windows invocation, graph contract, .asar/archive, native scope และ fleet-audit recipe อยู่ใน section 1.1–5 ของ reference นั้น
3. **Quantitative EA & Strategy Reconstruction Mode**: Triggered by trading statements, MT5 Strategy Tester reports, deal logs, or trade histories. Deconstructs 5-vector execution invariants and synthesizes complete, runnable MQL5 (`.mq5`) code. Reads [ea-strategy-reverse-engineering.md](references/ea-strategy-reverse-engineering.md).

---

## Reference Map

| Component | Path | Description |
| :--- | :--- | :--- |
| **REA Technical Guide** | [rea-technical-guide.md](references/rea-technical-guide.md) | เครื่องมือ MCP, Disassembly, Dynamic Inspection, และหลักการสกัดไบนารี |
| **Conceptual Reverse Eng** | [conceptual-reverse-engineering.md](references/conceptual-reverse-engineering.md) | แกะรอยแนวคิดซับซ้อน ปรัชญา และระบบนามธรรมด้วย First Principles |
| **EA Strategy Reverse Eng** | [ea-strategy-reverse-engineering.md](references/ea-strategy-reverse-engineering.md) | แกะรอยระบบเทรดและสร้างโค้ด MQL5 จากผลทดสอบ Backtest/ประวัติเทรด |
| **Report Template** | [report-template.md](references/report-template.md) | โครงสร้างรายงานมาตรฐาน 6 ส่วน พร้อม Mermaid Reverse Causal Map |
| **Dynamic DBI & Frida** | [dynamic-binary-instrumentation-frida.md](references/dynamic-binary-instrumentation-frida.md) | Dynamic runtime hooking, JavaScript injection, and Capa behaviors |
| **HTTPS Interception** | [https-traffic-interception.md](references/https-traffic-interception.md) | Mitmproxy SSL/TLS decryption, Python addons, and traffic replay |

---

## 5-Stage Multi-Model Reasoning Engine

### 1. The Phenomenon & Empirical Grounding (ผลปลายทาง / สภาพปัจจุบัน)
- Pinpoint the exact observed outcome or current system state ($T_0$).
- Apply **Kalāma principle**: Separate indisputable empirical facts from subjective assumptions. Attach exact Evidence IDs / SHA-256 for binaries.

### 2. Causal Backward Chaining (ปฏิจจสมุปบาท / Dependent Origination)
- Trace the chain of conditionality backward: *"When this exists, that exists; with the arising of this, that arises."*
- Step backwards sequentially: $T_0 \leftarrow T_{-1} \leftarrow T_{-2} \dots \leftarrow T_{\text{Origin}}$.

### 3. Branching Timeline & Inflection Points (จุดพลิกผัน / Tipping Points)
- Map the historical bifurcation tree: Identify critical moments where a minor fluctuation caused reality to divert.
- Identify **Counterfactuals**: What was the most probable alternative path, and what specific force tipped the scale?

### 4. System Dynamics & First Principles (พลวัตระบบ / แก่นแท้รากเหง้า)
- **First Principles Decomposition**: Strip away domain jargon; reduce the system to fundamental truths (physics, economics, psychology, math).
- **Feedback Loops & Latent Incentives**: What reinforcing or balancing loops governed the system? Who benefited?

### 5. Probability Space & "Should Be" Synthesis (ความน่าจะเป็น & สิ่งที่ควรจะเป็น)
- **Bayesian Inverse Probability**: Given current evidence $E$, what prior state $P(\text{Path} \mid E)$ carried the highest likelihood?
- **The "Should Be" Directive**: Based on immutable natural laws and efficiency frontiers, determine what the ideal state **should** be, and the precise vector to transition toward it.

---

## Output Protocol

เวลา user ถามว่า "ในเครื่องมีอะไร แกะอะไรได้บ้าง" ให้ตอบเป็น**กลุ่ม capability** (ทำได้เต็ม / บางส่วน / ทำไม่ได้ + เหตุผลกลไก + ตัวแทน 1 ตัวอย่าง) และปิดด้วยเส้นทางถัดไปที่เดียว — ไม่ใช่ทะเบียนโปรแกรมทั้งหมด และไม่ใช่ตาราง native/Electron ดิบ ๆ

When `/merea` is invoked, format reports according to the 6-part structure detailed in [report-template.md](references/report-template.md):
1. **Executive Core & Working Mechanism**
2. **Structural Anatomy & Invariants**
3. **Visual Reverse Causal Map (Mermaid)**
4. **Decomposition & Probabilistic Space Table**
5. **The "Should Be" Verdict & Actionable Leverage**
6. **Thai Executive Wrap-Up**
