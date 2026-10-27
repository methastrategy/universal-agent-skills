---
name: research
description: "วิจัยและค้นหาข้อมูล คู่มือทางการ และมาตรฐานวิศวกรรมสำรวจ — ใช้เมื่อต้องการเจาะลึกหลักการ วิธีใช้อุปกรณ์ หรือตรวจเอกสารอ้างอิง (Hybrid deep research, official manuals, engineering standards, operational guides)"
---

# Hybrid Internal-External Deep Research & Mechanism Synthesis

Autonomously investigate technical topics, engineering equipment (e.g., Survey Engineering, GNSS, Total Station, LiDAR, GIS), software documentation, standards, and scientific principles by combining local workspace context with mandatory external verification. Deliver high-density synthesis covering both theoretical mechanisms and practical operations.

---

## โหมดการทำงาน (Operational Modes)

| โหมด | คำสั่ง | การทำงาน |
| :--- | :--- | :--- |
| **Deep Research (Default)** | `/research` | วิจัยเจาะลึกมาตรฐานวิศวกรรม เอกสาร API และคู่มือทางการแบบ Hybrid พร้อมการอ้างอิงแหล่งที่มา |
| **External AI Relay** | `/research --relay` | สกัดแก่นความรู้จาก Gemini 4.0/ภายนอก $\to$ วิเคราะห์จุดต่าง $\to$ **สร้างบล็อก Prompt พร้อมก๊อปปี้ไปถามต่อปิดท้าย** |

---

## Steps

1. **Map Internal Context & Knowledge Gaps**:
   - **When workspace files are present**: Scan relevant local files, code, or documents first to understand current usage, assumptions, equations, or specs, and identify missing details or claims requiring verification.
   - **When given a standalone topic**: Deconstruct the query into precise technical keywords (both English and Thai) targeting primary documentation, datasheets, and standards.

2. **Mandatory External Grounding & Cross-Verification**:
   - **Never rely solely on local files or static model memory.** Always execute external searches using `search_web` and `read_url_content` (or dispatch the `research` subagent for broad parallel investigation).
   - **Enforce Source Hierarchy**:
     1. **Official Manuals, Datasheets & Docs**: Manufacturer user manuals (e.g., Leica, Trimble, Topcon, Sokkia), official API/SDK documentation, and hardware specifications.
     2. **Official Standards & Academic Sources**: National/international standards (e.g., กรมที่ดิน, กรมแผนที่ทหาร, RTSD, FIG, ISO, OGC, IEEE) and peer-reviewed literature.
     3. **Field & Engineering Best Practices**: Verified operational workflows and practitioner case studies.
     4. **Real-Time Trend & Community Signals**: GitHub Trending, HN upvotes, Reddit engagement, Polymarket odds, and practitioner transcripts สำหรับเทคโนโลยีหรือเทรนด์ล่าสุด 30 วัน (ดู `references/trend-research-sources.md`).
     5. **Live API Documentation via Context7**: ดึงเอกสารโค้ดและ API เวอร์ชันปัจจุบันผ่าน `npx ctx7` เพื่อป้องกัน Training data เก่าหรือภาพหลอน API (ดู `references/context7-guide.md`).
     6. **LLM-Ready Web Scraping**: กลยุทธ์การสกัดเนื้อหาเว็บเป็น Markdown ที่ปราศจากขยะ HTML/CSS/Navbars และคงรูปตาราง/โค้ด (ดู `references/llm-web-scraping.md`).
     7. **Hybrid Retrieval & Reciprocal Rank Fusion (RRF)**: ผสานการค้นหาคำตรงตัว (BM25/Ripgrep) ร่วมกับ Dense Vector และ Reranker (ดู `references/hybrid-retrieval-rrf.md`).
     8. **Multi-Perspective Research & Citation Grounding (STORM)**: จำลองผู้เชี่ยวชาญหลากมุมมองตั้งคำถามเจาะลึกพร้อมตรึงที่มาอ้างอิงทุกประเด็น (ดู `references/storm-multi-perspective-research.md`).
   - **Cross-Check**: Compare external facts against local project files (if any) to validate accuracy, spot outdated practices, or fill missing parameters.

3. **Deconstruct Mechanism & Practical Operation**:
   Synthesize findings far beyond surface-level definitions across four mandatory dimensions:
   - **Core Concept & Role**: What it is, why it exists, and the exact problem it solves.
   - **Inner Mechanism & Working Principle**: How it works under the hood (physical principles, mathematical models, signal/data flow, or algorithmic steps from input to output).
   - **Practical Operation, Workflow & Specs**: Step-by-step field/system operating procedures, critical parameters/settings, and standard accuracy/tolerance thresholds.
   - **Error Sources, Pitfalls & Verification**: Root causes of measurement or system errors, environmental/operational constraints, and calibration or quality-check routines.

4. **Synthesize Delta & Citations**:
   - Explicitly highlight how external findings enrich, confirm, or correct existing workspace files or initial assumptions.
   - Provide verifiable source URLs for every critical specification, manual, or standard referenced.

5. **External AI Relay (เฉพาะเมื่อมี Flag `--relay` หรือสั่งเจาะจง)**:
   - เมื่อวิเคราะห์ข้อมูลความรู้จากภายนอกเสร็จสิ้น ให้สร้างบล็อก Prompt ปิดท้าย (Ready-to-Copy Prompt Block) ที่ออกแบบมาอย่างดีสำหรับการนำไปก๊อปปี้ถามต่อใน Gemini 4.0 ทันที (โหมดทั่วไปไม่ต้องแสดง เพื่อคุมขนาดคำตอบ)

---

## Coverage Checklist
> เนื้อหาที่ต้องครอบคลุม ไม่ใช่หัวข้อที่ต้องพิมพ์ — ห้ามตอบเป็นหัวข้อเลขข้อ รูปแบบตอบตาม GEMINI.md §1
- **Executive Concept & Context**: Crisp definition, purpose, and (if applicable) comparison against existing local project files.
- **Working Principle & Inner Mechanism**: Deep-dive breakdown of the underlying physics, math, architecture, or data flow.
- **Practical Operation & Key Specifications**: Step-by-step usage workflow, configuration parameters, and accuracy/tolerance standards.
- **Error Sources, Limitations & Check Procedures**: Critical pitfalls, sources of error, and verification/calibration methods.
- **Verified References**: Direct clickable links to official manuals, standards, and primary sources consulted.

---

## Operating Rules

- **Zero Unverified Guessing**: Never fabricate hardware specs, tolerance thresholds, or regulatory standards. Always verify via `search_web` / `read_url_content`.
- **Beyond Definitions**: Never stop at "what it means"—always explain *how it works internally* and *how to operate/apply it in practice*.
- **High-Density Clarity**: Keep explanations sharp, structured, and free of conversational fluff, adapting language naturally to the user's prompt.
