---
name: tomd
description: "[แปลงไฟล์เป็น Markdown] สกัดโค้ดและเอกสารทั้งโฟลเดอร์เป็น .md — ใช้เมื่อต้องการทำ Obsidian Vault หรือคู่มือพร้อมคุม Token (Full-fidelity folder to Markdown batch extraction, Obsidian vault, token budgeting)"
---

# `/tomd` — Folder to Markdown Knowledge Base Generator

แปลงและสกัดเนื้อหาเอกสาร โค้ด สคริปต์ และข้อมูลทั้งหมดในโฟลเดอร์ให้เป็นไฟล์ Markdown (`.md`) มาตรฐานสำหรับจัดเก็บลง **Obsidian Vault** หรือนำไปขึ้นเป็นเอกสารคู่มือบน **MESURV Website** โดยคงรายละเอียดเนื้อหาเต็ม 100% (Full Raw Extraction) พร้อมระบบตรวจสอบ Token / Resource Usage

---

## 1. กฎเหล็กและข้อกำหนด (Invariants)

1. **Full Raw Extraction (ไม่ตัดทอนเนื้อหา):**
   - ถอดรหัสเนื้อหาทั้งหมด ไม่ย่อทิ้ง ไม่ตัดสมการ ไม่ละเว้นบรรทัดโค้ด หรือสูตรการคำนวณ
   - สมการคณิตศาสตร์/ฟิสิกส์/การสำรวจ ต้องเขียนเป็น LaTeX (`$...$` หรือ `$$...$$`)
   - ตารางข้อมูลและตัวเลขพิกัด/สเปก ต้องจัดเป็น Markdown Table ให้สมบูรณ์
2. **Isolation & Zero-Clutter:**
   - **ห้ามสร้างไฟล์ `.md` ปนกับไฟล์ดิบเดิมเด็ดขาด**
   - ให้บันทึกไฟล์ผลลัพธ์ลงในโฟลเดอร์เฉพาะ เช่น `_docs_md/` ภายในโฟลเดอร์นั้น หรือบันทึกลงในโฟลเดอร์ Obsidian ที่ผู้ใช้ระบุ
3. **Smart Ignore (ข้ามไฟล์ขยะอัตโนมัติ):**
   - ข้ามไฟล์ Binary, Cache, Build Artifacts: `.git`, `node_modules`, `__pycache__`, `.venv`, `.exe`, `.dll`, `.zip`, `.rar`, `.dxf_cache`, `.bin`
4. **Pre-flight Token & Usage Audit:**
   - ก่อนเริ่มแปลงไฟล์ ให้รายงานสรุป:
     - จำนวนไฟล์ที่พบ
     - ขนาดรวม (KB/MB)
     - ประมาณการ Token Usage ในการประมวลผล

---

## 2. ขั้นตอนการทำงาน (Lifecycle)

### ขั้นที่ 1: สแกนและคำนวณ Token (Pre-flight Inspection)
- สแกนหาไฟล์ที่แปลงได้ (`.txt`, `.py`, `.js`, `.ts`, `.html`, `.css`, `.json`, `.csv`, `.docx`, `.pdf`, `.md`, ฯลฯ)
- คำนวณขนาดและแสดงตารางสรุปให้ผู้ใช้ทราบก่อนลงมือทำ:
  ```text
  📊 รายงานการสแกนโฟลเดอร์: [โฟลเดอร์เป้าหมาย]
  - จำนวนไฟล์ที่รองรับ: X ไฟล์
  - ขนาดรวม: Y KB
  - ประมาณการ Token: ~Z tokens
  - โฟลเดอร์ปลายทาง: [โฟลเดอร์เป้าหมาย]/_docs_md/
  ```

### ขั้นที่ 2: แปลงไฟล์เป็น Markdown ตามโครงสร้าง (Extraction & Formatting)
สร้างไฟล์ `.md` หนึ่งไฟล์ต่อหนึ่งไฟล์ต้นฉบับ โดยมีโครงสร้างมาตรฐาน:

```markdown
---
title: "ชื่อไฟล์ / หัวข้อหลัก"
source_file: "path/to/original/file.ext"
converted_at: "YYYY-MM-DD HH:mm:ss"
type: "code | documentation | data | coursework"
tags:
  - mesurv
  - [หมวดหมู่งาน]
---

# [ชื่อเรื่อง / ชื่อไฟล์]

> [!INFO] ข้อมูลไฟล์ต้นฉบับ
> - **ต้นทาง:** `path/to/original/file.ext`
> - **ประเภท:** [Python Script / Engineering Doc / Data Table]

---

[เนื้อหาเต็ม 100% ตามรูปแบบไฟล์]
```

### ขั้นที่ 3: สรุปสารบัญและดัชนีภาพรวม (`INDEX.md`)
เมื่อแปลงไฟล์ทั้งหมดเสร็จแล้ว ให้สร้างไฟล์ `_docs_md/INDEX.md` เป็นสารบัญรวมที่มี:
- รายชื่อไฟล์ทั้งหมดพร้อมลิงก์ไปยังไฟล์ `.md` แต่ละตัว
- สรุปภาพรวมของโฟลเดอร์และหมวดหมู่เนื้อหา
- รายงานสรุปการใช้ทรัพยากร (Total Files Converted, Final Status)

---

## 3. ตัวเลือกคำสั่งเสริม (Flags & Options)

- `/tomd <folder>` — แปลงไฟล์ทั้งหมดใน `<folder>` ลงใน `<folder>/_docs_md/`
- `/tomd <folder> --out <dest_folder>` — กำหนดโฟลเดอร์ปลายทาง (เช่น ชี้ไปที่ Obsidian Vault โดยตรง)
- `/tomd <folder> --web` — ปรับฟอร์แมตเน้นสำหรับขึ้นเว็บไซต์ MESURV (Clean GFM, Code snippet tags)
