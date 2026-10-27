# Architecture & Cognitive Invariants

This repository houses a modular, production-hardened suite of 22 AI agent skills and deterministic operating rules. Designed for AI coding assistants (Google Antigravity, Claude Code, Cursor, Windsurf) and agent orchestrators (LangGraph, n8n, AutoGen).

---

## 1. The 3-Tier Progressive Disclosure Model

Loading massive system prompts creates high token costs and attention drift ("Lost in the Middle"). This architecture uses 3-tier progressive disclosure:

1. **L1: Frontmatter Discovery (`name` & `description` <= 220 chars):**
   Lightweight descriptors loaded permanently in the system index to route queries without consuming prompt tokens.
2. **L2: Core Protocol (`SKILL.md`):**
   The execution state machine and critical safety invariants loaded just-in-time when the skill is called.
3. **L3: Deep Reference Manuals (`references/*.md`):**
   Heavy patterns, cheatsheets, and specific API contracts read on-demand during implementation.

---

## 2. The Internal Rigor vs. External Output Invariant

All philosophical, epistemic, and analytical heuristics operate strictly as **internal cognitive engines**:
- Never project abstract philosophical or theological terminology into user-facing output headers.
- Always output using clean, standard, elite engineering sections:
  1. **Symptom & Defect Signature** (อาการและผลกระทบ)
  2. **Root Cause & Mechanism** (ต้นตอและกลไกปัญหา)
  3. **Target State & Invariants** (เป้าหมายและเกณฑ์ความสำเร็จ)
  4. **Remediation & Action Plan** (แผนปฏิบัติการแก้ไข)

---

## 3. Cognitive Seams & Ponytail Hierarchy

Before mutating any codebase, agents lock boundaries:
- **Target Seam:** The isolated target file or public interface.
- **Forbidden Surfaces:** Lock tests, configurations, and unrelated modules.
- **Ponytail Selection Order:**
  1. Skip if unrequested
  2. Reuse codebase helper
  3. Standard library
  4. Installed dependency
  5. 1-liner
  6. Smallest complete diff
