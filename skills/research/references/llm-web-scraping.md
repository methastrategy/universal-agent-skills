# LLM-Ready Web Scraping & Content Extraction Guide

แนวปฏิบัติและเทคนิคการดึงข้อมูลจากหน้าเว็บให้เป็น Markdown คุณภาพสูงที่พร้อมป้อนเข้าสู่โมเดล LLM โดยตรง (อ้างอิงจากสถาปัตยกรรมของ `crawl4ai` และ `firecrawl`)

---

## 1. ปัญหาของ Web Scraping ทั่วไป vs LLM-Ready Markdown

| มิติ | Raw HTML / Basic Scraper | LLM-Ready Markdown (Crawl4AI / Firecrawl) |
| :--- | :--- | :--- |
| **Token Waste** | ขยะ HTML, CSS, SVG, Nav, Cookie Banner กิน 70-90% ของ Token | สกัดเฉพาะ Main Content เหลือเฉพาะแก่นสาระสำคัญ |
| **ตารางข้อมูล** | `<table>` แท็กซ้อนกันจน LLM สับสน | แปลงเป็น GFM Markdown Table (`\| Col1 \| Col2 \|`) ที่จัดระเบียบชัดเจน |
| **Code Snippets** | หลุด Tag `<pre><code>` หรือ Indentation หาย | สกัดเป็น Fenced Code Block พร้อมระบุภาษา (` ```python `) |
| **Dynamic SPAs** | ได้เฉพาะหน้าว่างเปล่าก่อน hydration | รองรับ Headless Browser Render ก่อนสกัด DOM |

---

## 2. ขั้นตอนการกลั่นกรองเนื้อหา (Content Distillation Pipeline)

1. **Noise Pruning (กำจัดสิ่งรบกวน):**
   - ตัดแท็ก `<header>`, `<footer>`, `<nav>`, `<aside>`, `<script>`, `<style>`, `<iframe>`
   - ลบ Modal/Banner คุกกี้ (`consent`, `popup`, `gdpr`)
   - กรอง Attribute ส่วนเกิน (`class`, `style`, `data-*`, `onclick`) ออกทั้งหมด
2. **Main Article Extraction (ระบุแกนหลัก):**
   - ตรวจหา Container หลัก เช่น `<main>`, `<article>`, `[role="main"]`, หรือ Node ที่มี Text Density สูงสุด
3. **Structured Semantic Conversion (แปลงสู่ Markdown):**
   - Headers: แปลง `<h1>`-`<h6>` เป็น `#`-`######` ตามลำดับชั้นที่ถูกต้อง
   - Tables: รักษาโครงสร้างแถวและคอลัมน์ ห้ามแปลงตารางข้อมูลตัวเลขเป็นข้อความบรรยายร้อยแก้ว
   - Code Blocks: ดึงคลาสของ `<pre><code>` เพื่อระบุภาษาโปรแกรม
   - Links & Citations: แปลง Link อ้างอิงสำคัญเป็น Markdown Links `[Text](URL)` แต่ตัด Internal Anchor ทิ้งหากไม่จำเป็น
4. **Token Compaction & Normalization:**
   - รวม White spaces และ Newlines ที่ซ้ำซ้อนให้เหลือไม่เกิน 2 บรรทัด (`\n\n`)
   - ลบอักขระขยะ (Zero-width spaces, UTF-8 BOM, Phantom entities)

---

## 3. กลยุทธ์การ Crawl เอกสาร API และคู่มือเทคนิค (Multi-Page Crawling)

- **Breadth-First Exploration (BFS):** สำหรับสารบัญคู่มือ API ที่มีหน้าย่อย ให้สกัดลิงก์สารบัญ (Table of Contents / Sidebar) ก่อน แล้ววนดึงเฉพาะหน้าที่มีคำสำคัญตรงเป้าหมาย
- **Depth Limiting:** กำหนดความลึกในการแกะรอยลิงก์ไม่เกิน 2 ระดับ เพื่อป้องกันไม่ให้หลุดออกไปยัง External Domains หรือหน้าเว็บบอร์ดที่ไม่มีประโยชน์
- **Pagination Batching:** ดึงข้อมูลแบบ Pagination ควบคุมขนาด Batch ละไม่เกิน 5-10 หน้าต่อการสังเคราะห์ 1 รอบ

---

## 4. Checklist ตรวจรับ Markdown จาก Web Scraping
- [ ] มีเฉพาะเนื้อหาหลัก ไม่มีเมนู Navbar, Footer หรือข้อความ Copyright กวนใจ
- [ ] ตารางเปรียบเทียบสเปกหรือตัวเลขคงรูป Markdown Table 100%
- [ ] ตัวอย่างโค้ดคำสั่งหรือ API request อยู่ในบล็อกโค้ดพร้อมภาษา
- [ ] มี Link ต้นทางของเอกสาร (Source URL) ระบุไว้อย่างชัดเจน
