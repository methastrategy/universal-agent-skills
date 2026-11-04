# Knowledge Registry (Universal MemOS Brain)

A persistent log of distilled architectural insights, benchmark evaluations, and empirical invariants recorded as Fact Tuples.

---

## Fact Tuples Register

| Timestamp | What (Lesson / Invariant) | Why (First Principles) | How (Operational Mechanism) | Scope |
| :--- | :--- | :--- | :--- | :--- |
| **2026-11-01** | **6-Vector Pre-Flight Bug Radar** | Heavyweight model audits are slow/expensive; syntax checks alone miss runtime nulls & race conditions | Run fast System 1 defect radar (Logic, Null, Resource, Race, Security, Regression) producing calibrated probabilities in ~1s; gate execution with `CRITICAL_FIX_REQUIRED` until `APPROVED (clean)` | Global (`/jev`, `/build`) |
| **2026-10-30** | **Modular Rule Budget Cap** | Antigravity truncates rule files exceeding 24,000 bytes at line boundaries silently | Refactor monolithic `AGENTS.md` into ≤24KB hub + modular `.agents/rules/*.md` extensions | Global (All Agents) |
| **2026-10-30** | **Strict Subagent Cleanup Invariant** | Lingering background subagents accumulate memory and cause token leakage | Always call `manage_subagents(Action='kill_all')` immediately upon completing verification gates | Global (`AGENTS.md`) |
| **2026-11-04** | **Structural Sweep & OOS Boundary Gate** | Small deposits cap total profit and distort edge; entry on confirmed fractals loses to noise | Sweep and reclaim confirmed levels at Limit with >=$1,000 capital; freeze preset and validate on strictly out-of-sample window before claiming edge | Quant (`/mql5-ea`) |
