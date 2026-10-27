# Real-Time Trend & Community Signals Research Guide

คู่มือการสืบค้นข้อมูลเชิงลึกและเทรนด์เทคโนโลยีล่าสุด 30 วัน สกัดจากระเบียบวิธีของ **last30days-skill** (`mvanhorn/last30days-skill`)

---

## 1. ปรัชญาการค้นหา (The last30days Philosophy)

> "Google aggregates editors. We search people."

การค้นหาข้อมูลทางเทคนิค AI, เครื่องมือใหม่, หรือตลาดการเงิน (`/quant`) ผ่าน Search Engine แบบเดิม มักเจอบทความ SEO ขยะ, เอกสารล้าหลัง, หรือ Sponsored Content ที่ไม่ได้สะท้อนความจริงหน้างาน
การค้นหาตามแนวทางนี้เน้นดึงข้อมูลจาก **"แหล่งที่คนลงคะแนนด้วยความสนใจ เวลา หรือเงินจริง"**:

| แหล่งข้อมูล | สัญญาณความจริง (Truth Signal) | เมื่อใดที่ควรใช้ |
| :--- | :--- | :--- |
| **GitHub Trending & Releases** | Star velocity, Release commit logs, Breaking changes | ตรวจสอบการอัปเดตเครื่องมือ, Libs, Frameworks |
| **Hacker News (Algolia HN Search)** | ความคิดเห็นวิศวกรอาวุโส, การถกเถียงข้อเสียเชิงสถาปัตยกรรม | ประเมิน Production readiness, Security trade-offs |
| **Reddit (Community Upvotes)** | ปัญหาการใช้งานจริง (Pain points), Workarounds ที่คนเจอบ่อย | Debug ปัญหาแปลกๆ, User sentiment |
| **Polymarket Odds** | ราคาต่อรองที่มีเงินจริงหนุนหลัง (Incentivized Probabilities) | ประเมินความน่าจะเป็นของเหตุการณ์ในอนาคต (Tech/Macro) |
| **YouTube Transcripts** | คำพูดสดของผู้สร้าง (Creator / Maintainer talk) | ฟัง Deep-dive demo, Keynote, Architecture teardown |

---

## 2. ขั้นตอนการสังเคราะห์ข้อมูล (4-Step Trend Synthesis)

1. **Parallel Source Querying**: ยิงค้นหาข้อมูลคู่ขนานข้าม GitHub API, Web Search, และ Official Forum
2. **Engagement Weighting**: กรองเอาเฉพาะข้อมูลที่มี Upvotes, Stars, หรือ Comments จากผู้ใช้จริง ไม่เอาบล็อกที่ปั่นด้วย AI
3. **Delta Extraction**: สกัดเฉพาะสิ่งที่ **เปลี่ยนแปลงใน 30 วันล่าสุด** (New features, Removed APIs, Known regressions)
4. **Actionable Synthesis**: สรุปเป็น Brief สั้น กระชับ อ้างอิงลิงก์จริง และระบุผลกระทบต่อโปรเจกต์ของผู้ใช้
