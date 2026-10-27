---
name: debug
description: "แก้บั๊ก ล่าต้นตอปัญหา และซ่อมโค้ดที่พังให้หายขาด — ใช้เมื่อโค้ดพัง รันไม่ผ่าน ติด Error ค่าเพี้ยน หรือระบบทำงานผิดปกติ (Systematic defect isolation, root cause analysis, bug eradication, and regression prevention)"
---

# Systematic Defect Isolation & Bug Eradication

Isolate, analyze, and fundamentally eradicate software bugs, race conditions, memory leaks, and logic flaws without resorting to band-aid patches or symptom masking.

## สถาปัตยกรรมอ้างอิง (Reference Map)
- **การสืบสวนและล่าต้นตอแบบเป็นระบบ 4 ขั้นตอน:** อ่าน `references/systematic-defect-investigation.md` ( Superpowers 4-Phase Lifecycle, Scientific Hypothesis Testing, Single-Variable Falsification )
- **การตรึงบั๊กและกระบวนการ Fail-to-Pass:** อ่าน `references/regression-pinning-protocol.md` ( SWE-Bench discipline, F2P Verification, Zero P2P Regressions )
- **การแกะรอยประวัติและ Telemetry Spans:** อ่าน `references/telemetry-spans-and-breadcrumbs.md` ( OpenTelemetry Spans, Sentry Error Breadcrumbs, Failure Context )
- **เกณฑ์วัดความผิดพลาดและ Postmortem Harness:** อ่าน `references/postmortem-harness.md` ( Epistemic Reset, Incident Ledger, Invariant Pinning )

## Steps

0. **Speculative Fan-Out (Parallel 4-Probe Triage)**: Evaluate 4 orthogonal failure probes (Env/Encoding, Boundary/Nil, Concurrency/Lifecycle, Cache/Drift) before linear tracing to eliminate trial-and-error loops.
1. **Isolate and Reproduce**: Establish a minimal, deterministic reproduction case.
2. **Trace System Execution**: Trace execution flows and data values step-by-step to the exact point of divergence.
3. **Analyze Root Cause**: Determine the underlying architectural, logical, or data condition causing the failure.
4. **Implement Permanent Fix**: Design and apply a structural fix that completely eliminates the failure vector.
5. **Regression Verification**: Validate that the bug is gone under original test conditions and no side-effects are introduced.

---

## Step 0: Speculative Fan-Out Protocol (Parallel 4-Probe Triage)

ก่อนเริ่ม Trace โค้ดแบบเรียงแถว ให้ทำการคัดแยกสมมติฐานคู่ขนาน 4 มิติ (Inspired by Jev Speculative Evaluation):
- **Probe A (Environment & Encoding):** มีปัญหาเรื่อง Path resolution (Windows `\` vs POSIX `/`), Environment Variable, File Encoding (BOM / UTF-8 / NUL-byte), หรือ File/Process Permissions หรือไม่?
- **Probe B (Boundary & Nil-Leap):** เกิดค่า `null`/`undefined`, Missing Key, Type Coercion, หรือ Boundary Off-by-one ที่จุดเชื่อมต่อ API/Data Seam หรือไม่?
- **Probe C (Lifecycle & Concurrency):** เกิด Race Condition, Unhandled Async/Promise, Stale State/Closure, หรือ Event Listener Cleanup หลุดหรือไม่?
- **Probe D (Cache & Build Drift):** มีปัญหา Stale Cache, Stale Build Artifacts, Dependency Version Drift, หรือ Lockfile Desync หรือไม่?

เลือก Probe ที่มีคะแนนความน่าจะเป็นสูงสุด ($P \ge 0.80$) แล้วพุ่งเป้าไปที่จุดรอยต่อ (Seam) นั้นทันที

---

## Coverage Checklist
> เนื้อหาที่ต้องครอบคลุม ไม่ใช่หัวข้อที่ต้องพิมพ์ — ห้ามตอบเป็นหัวข้อเลขข้อ รูปแบบตอบตาม GEMINI.md §1
- **Reproduction Protocol**: Exact inputs/actions needed to trigger the bug.
- **Root Cause Analysis**: Structural explanation of why the failure occurred.
- **Permanent Solution**: Implementation diff eliminating the core issue.
- **Workaround Exclusions**: List of temporary fixes explicitly rejected in favor of the permanent fix.

---

## Operating Rules

- Absolutely zero usage of temporary workarounds, arbitrary try/catch wrappers, or time-delay patches.
- The bug must be fundamentally resolved at its logical source.
- Verify using real data, logs, or execution results whenever possible.
