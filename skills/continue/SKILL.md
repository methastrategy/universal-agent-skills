---
name: continue
description: "กู้คืนงานค้าง ฟื้นฟูบริบท และทำต่อจากเดิมทันที — ใช้เมื่อแชตค้าง หลุดกลางคัน สลับโมเดล หรือ Token หมดแล้วต้องต่องาน (Seamless session recovery, context restoration, execution resumption after handoff)"
---

# Continue & Execution Resumption Protocol

Use this skill whenever the user invokes `/continue` (or "continue", "รันต่อ", "ทำต่อ"), or immediately after a session recovery where an agent execution was terminated due to an error, timeout, token exhaustion, or AI model switch (e.g. Claude to Gemini).

## Core Objective
Seamlessly pick up where the previous turn left off without hallucinating, without skipping planned steps, without repeating already-completed work, and without asking redundant questions.

## สถาปัตยกรรมอ้างอิง (Reference Map)
- **การจัดการความจำระยะยาวและการสังเคราะห์บริบท:** อ่าน `references/dynamic-memory-consolidation.md` ( Mem0 Graph Memory, Entity Extraction, Temporal Decay )

## Execution Sequence

### Phase 1: Context & State Introspection
0. **Handoff:** อ่าน `D:\WSL\.gemini\handoffs\latest-<ชื่อ workspace ปัจจุบัน>.md` ถ้ามี ใช้เมื่อ header `workspace:` ตรงกับ workspace ปัจจุบันและ `created` ไม่เกิน 48 ชม.; ไม่ตรงหรือเก่ากว่านั้น → บอกผู้ใช้แล้วถามก่อน แจ้งเสมอว่าอ่านไฟล์ไหน และตรวจสถานะจริงของไฟล์/คำสั่งที่ระบุก่อนทำต่อ
1. **Read Continuation Context & Transcript:**
   - Inspect the recent conversation summary, user's latest prompt, and last planner response.
   - Read active tracking artifacts in the artifact directory, especially `plan.md` and `walkthrough.md`.
2. **Ground Truth Directory & Git Inspection:**
   - Verify the actual filesystem path and CWD before running any command (never blindly trust stale workspace URIs).
   - Execute `git status` and `git diff --stat` to ascertain what files were already edited or committed vs. left unstaged.
2.5. **Hindsight Reflection (Learning from Past Failures - Hindsight Pattern):**
   - สแกนประวัติการรันล่าสุดใน `plan.md` หรือ Transcript: มีคำสั่งใดที่เคยรันแล้ว Error ซ้ำๆ หรือมี Approach ใดที่เคยล้มเหลวหรือไม่
   - **ห้ามลองวิธีเดิมที่เคยพังแล้วเกิน 1 ครั้ง** หากตรวจพบ ให้ทำการ Epistemic Reset และเปลี่ยนสมมติฐานทันทีก่อนลงมือเขียนโค้ด
3. **Isolate Completed vs. Pending Tasks:**
   - Compare active working tree changes against the checklist in `plan.md`.
   - Identify the exact pending step or sub-phase that was interrupted.

### Phase 1.5: Quality Gate (Health-Check Trinity — MANDATORY before any file edit)
Before touching any file or reporting final status, run ALL three in this order:
1. `git status` — confirm working tree state and which files were already modified/untracked.
2. `npx tsc --noEmit` (or `tsc --noEmit` if available) — zero TypeScript errors expected; record any pre-existing errors as a baseline before proceeding.
3. `npx vitest run` (or project-equivalent: `npm test`, `pytest`) — all tests must pass, or failures noted as pre-existing blockers.

4. **Half-applied edit check** — ถ้าไฟล์ที่ค้างแก้อยู่มีอาการเขียนทับซ้อน (JSX/tag ไม่บาลานซ์, ฟังก์ชันซ้ำสองชุด, โค้ดเก่าหลงเหลือกลางไฟล์, `import` ชี้ symbol ที่ย้ายไปแล้ว) ห้ามไล่ patch ทับ ให้ `git checkout -- <ไฟล์>` กลับไป HEAD แล้วแก้ใหม่แบบ minimal เพราะ patch ที่รายงาน success ยังทิ้งไฟล์ครึ่ง ๆ กลาง ๆ ได้ และการ patch ทับซ้อนทำให้ anchor ของ `old_string` เลื่อนจนไม่รู้ว่าไฟล์อยู่สถานะไหน — หลัง structural edit ทุกครั้งต้อง `tsc --noEmit` + build ก่อนไปต่อ

Only after all four complete should the agent proceed to Phase 2. This prevents layering new changes on top of a silently broken build.

### Phase 2: Autonomous Resume & Execution
1. **Immediate Resumption:**
   - Proceed directly with the next unfinished step in `plan.md`.
   - Do NOT ask the user for permission to continue what was already requested.
2. **Deterministic Verification:**
   - Run relevant test suites (`npm test`, `vitest`, `pytest`) and production build commands (`npm run build`) to ensure the codebase remains clean.
3. **Plan Reconciliation:**
   - Verify all items from `plan.md` are fulfilled.

### Phase 3: Consolidated Reporting
- Report completed steps concisely.
- Highlight any pending items or recommendations.
- State the deployment status (e.g., GitHub/Vercel sync status) per workspace rules.
