# Parallel Swarm Dispatch — Reference Guide

ส่วนขยายของ `/jev` สำหรับ Dispatch Subagent Swarms แบบคู่ขนานตาม Agentic CEO Protocol

---

## เมื่อใดควร Fan-Out เป็น Swarm

- งานมีขอบเขตแยกกันชัด (Frontend / Backend / DB / Security Review) ที่ไม่มี Shared Mutable State
- แต่ละงานใช้เวลา > 3 นาทีถ้าทำเรียงแถว
- ผลของแต่ละ Subagent สามารถ Verify แยกกันได้ก่อน Merge

---

## Scope Invariant สำหรับ Swarm (Critical)

แต่ละ Subagent ต้องได้รับ Explicit Scope Manifest ก่อนเริ่มทำงาน:

```text
Agent: [Frontend Commander]
Scope (Directory Whitelist): src/components/ และ src/app/ เท่านั้น (Exclusive Write Lock)
Forbidden Paths: src/lib/, src/api/, tests/shared/
Deliverable: Component ครบ + unit test + Judge Scorecard 4-block
```

- ห้าม Subagent ออกนอก Scope แม้จะ "เห็น" ว่าน่าแก้
- **No Concurrent File Writes:** ซับเอเจนต์ 2 ตัวห้ามมีสิทธิ์เขียนไฟล์ใน Directory เดียวกันเด็ดขาด หากจำเป็นต้องแตะไฟล์ร่วมกัน ต้องใช้ Git Branch Isolation (`Workspace: 'branch'`)
- **Swarm Circuit Breaker:** หาก Subagent ไม่มีการคืบหน้าภายใน 3 Turn หรือติดสถานะรอคอยไม่สิ้นสุด ให้สั่ง `manage_subagents(Action='kill')` ทันที ป้องกัน Token รั่วไหล
- Subagent ต้องส่ง Judge Scorecard กลับมาก่อน Main Agent จะ Merge
- Main Agent เป็นผู้เดียวที่มีสิทธิ์ดำเนินการ Irreversible Action

---

## 3-Tier Cognitive Budget Routing

| Role | Model Hint | งานที่เหมาะสม |
| :--- | :--- | :--- |
| Scout / Globber | `flash` | ค้นหาโครงสร้าง, กวาดไฟล์, ลิสต์ deps, อ่าน logs |
| Workhorse | `inherit` | โค้ดมาตรฐาน, refactor, bugfix, unit tests |
| Deep Architect | `pro` | สถาปัตยกรรม, schema migration, critical business logic |

---

## ตัวอย่าง Swarm Dispatch

```text
/jev → Fan-Out: 3 Subagents
  [flash]   Scout: อ่านโครงสร้างโปรเจกต์ ลิสต์ไฟล์ที่ต้องแก้
  [inherit] Frontend Commander: แก้ src/components/ ครบ + เทสต์
  [inherit] Backend Specialist: แก้ /api/ + integration test
→ รอ Scorecard จากทั้ง 3 → Main Agent Merge & รายงาน
```
