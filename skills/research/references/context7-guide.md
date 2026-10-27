# Context7 Live API Documentation Guide

คู่มือการดึงเอกสารคู่มือโค้ดและตัวอย่าง API ล่าสุดตรงจาก Source ผ่าน **Context7** (`upstash/context7`)

---

## 1. ปัญหาของ Static Training Data vs ทางออกของ Context7

- **ปัญหา:** LLM อาศัยข้อมูลใน Training set ซึ่งเก่ากว่าความเป็นจริง มักสร้างภาพหลอน API (Hallucinated APIs), แนะนำฟังก์ชันที่ Deprecated ไปแล้ว, หรือใช้ Patterns ของเวอร์ชันเก่า (เช่น Next.js App Router vs Pages Router, Tailwind v3 vs v4)
- **ทางออก:** Context7 ดึงเอกสารคู่มือและตัวอย่างโค้ดเวอร์ชันล่าสุดตรงจากผู้พัฒนา เข้ามาใน Prompt บริบท ทำให้โค้ดที่สร้างขึ้นตรงกับเวอร์ชันปัจจุบันเสมอ

---

## 2. วิธีเรียกใช้งาน (CLI & Direct Access)

เมื่อต้องการศึกษาหรือเขียนโค้ดด้วย Library ที่เปลี่ยนแปลงบ่อย ให้ใช้คำสั่ง `ctx7`:

```bash
# รูปแบบคำสั่ง CLI
npx ctx7 use <library-name> --topic <specific-feature>
```

### ตัวอย่างการประยุกต์ใช้งาน
1. **Next.js Middleware & Server Actions:**
   `npx ctx7 use nextjs --topic "middleware cookie session"`
2. **Cloudflare Workers:**
   `npx ctx7 use cloudflare-workers --topic "cache api json response"`
3. **Supabase Auth:**
   `npx ctx7 use supabase --topic "auth passwordless signup"`
4. **Tailwind CSS v4:**
   `npx ctx7 use tailwindcss --topic "theme css variables v4"`

---

## 3. กฎเกณฑ์การใช้งานใน Agent Workflow (Grounding Invariant)

- เมื่อผู้ใช้สั่งให้พัฒนาหรือรีแฟกเตอร์ฟีเจอร์ที่ผูกกับ Third-party Framework เวอร์ชันใหม่ ห้ามเดาชื่อ Option หรือ Argument
- ตรวจสอบเวอร์ชันใน `package.json`, `pyproject.toml`, หรือ `go.mod` ก่อน
- ดึงเอกสารผ่าน `read_url_content` / `npx ctx7` เพื่อให้มั่นใจว่า API ที่ใช้มีอยู่จริงในเวอร์ชันนั้น
