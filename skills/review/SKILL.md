---
name: review
description: "[ตรวจรับงาน QA/QC] ตรวจคุณภาพโค้ด ช่องโหว่ OWASP คอนทราสต์ UI — ใช้เมื่อเขียนโค้ดเสร็จและตรวจรับงานก่อนปล่อยจริง (Comprehensive code, OWASP security, UI accessibility, architecture audit)"
---

# /review — ศูนย์ตรวจรับงานและประกันคุณภาพครบวงจร (Unified QA & Verification Hub)

ตรวจสอบคุณภาพซอฟต์แวร์รอบด้านแบบ One-Stop Inspection ครอบคลุมทั้งความถูกต้องของโค้ด (Logic & Bugs), ความปลอดภัย (OWASP Security & Compliance), ความสมบูรณ์ของหน้าเว็บ (UI/UX & Accessibility), และโครงสร้างสถาปัตยกรรม (Architectural Seams)

---

## โหมดการทำงาน (Operational Modes)

| โหมด | คำสั่ง | การทำงาน |
| :--- | :--- | :--- |
| **Comprehensive QA (Default)** | `/review` | ตรวจสอบคุณภาพโค้ด 4 มิติ (Logic, OWASP Security, UI Accessibility, Architectural Health) |
| **Unified Deep Audit** | `/review --audit` (หรือ `/audit`) | เชื่อมโยงกับ `/analyze`: รันการตรวจรับงานครบวงจร ผสานการคัดกรองความจริงเชิงประจักษ์และการผ่ารากเหง้าปัญหาเชิงระบบ ร่วมกับด่านตรวจ 4 มิติ |

---

## สถาปัตยกรรมอ้างอิง (Reference Map)
- **การรีวิวแบบคู่ต่อสู้และการป้องกันเชิงประจักษ์:** อ่าน `references/adversarial-code-review.md` ( Superpowers Adversarial Reviewer, 5-Vector Attack Checklist, Peer Defense )
- **การตรวจจับ PR Smells และการตรวจจับเทสต์หลอก:** อ่าน `references/adversarial-pr-smells.md` ( The 3-Minute PR Smells, Anti-Mock Drills, Concurrency Yield Points )
- **ความปลอดภัยเว็บและการตรวจช่องโหว่:** อ่าน `references/web-security-owasp.md` ( OWASP Top 10, WSTG v4.2 Checklist, Semgrep SAST Taint Analysis, JWT & IDOR )
- **ตรวจสอบดีไซน์และคอนทราสต์:** อ่าน `references/ui-review.md` ( WCAG AAA Contrast, Typography & Spacing audit )
- **เช็กลิสต์ความสมบูรณ์หน้าเว็บ:** อ่าน `references/frontend-checklist.md` ( Core Web Vitals, Responsive, SEO & Meta Tags )
- **สแกนผ่าตัดสถาปัตยกรรมโค้ด:** อ่าน `references/architectural-scan.md` ( Shallow Modules & Visual HTML Report in `%TEMP%` )
- **การทดสอบ E2E และความทนทานต่อการแสดงผล:** อ่าน `references/e2e-playwright-testing.md` ( Playwright Auto-Wait, User-Centric Role Locators, API Mocking & Snapshot QA )
- **การวิเคราะห์ AST และกฎ SAST เฉพาะทาง:** อ่าน `references/ast-taint-sast-rules.md` ( Semgrep Declarative Rules, Source-to-Sink Taint Mode )
- **สแกนความลับและป้องกัน Git รั่วไหล:** อ่าน `references/entropy-secret-scanning.md` ( TruffleHog Shannon Entropy, Regex Signatures, Pre-Commit Hooks )
- **การตรวจสอบมาตรฐานความปลอดภัยและสแกนเชิงประจักษ์:** อ่าน `references/compliance-scorecard.md` ( Deterministic Grep Matrix, Multi-Stack Scanners, Thai PDPA 2562, WCAG 2.2 Accessible Auth )
- **ตรวจรับงานที่ผู้ใช้อ้างว่า “ปิดเสร็จแล้ว”:** อ่าน `references/claimed-remediation-verification.md` ( ยืนยันทีละข้อด้วยหลักฐานจากการรันจริง )

---

## ด่านตรวจรับงาน 4 มิติ (The 4-Dimensional Audit Protocol)

### 1. ความถูกต้องและตรรกะของโค้ด (Logic & Defect Integrity)
- ตรวจสอบ Off-by-one errors, การจัดการค่า `null`/`undefined`, และ Edge cases
- ตรวจจับ Concurrency issues, Race conditions และ State synchronization
- ตรวจสอบ Resource Leaks (การลืมถอด Event Listener, การไม่ปิด Connection, Memory Leaks)
- ตรวจสอบ Error Boundaries: ห้ามใช้ `catch` ว่างๆ ที่กลืนข้อผิดพลาดจนระบบพังเงียบ
- **Anti-Mock & Assertion Integrity:** ตรวจสอบว่าไม่มีการแก้ Test Assertion ให้อ่อนลงเพื่อปกปิดบั๊ก และไม่มีการใส่ Shallow Mock ปลอมแปลงผลลัพธ์ใน Seams สำคัญ
- **Dual-Implementation Oracle & Bit-Exact Passthrough:** เมื่อมีอัลกอริทึมซับซ้อน (Math/Shaders/Transforms) ต้องมี Simple Reference Oracle เทียบผลลัพธ์ $\le \epsilon$; เมื่อแก้ไขไฟล์โครงสร้างซับซ้อน ต้องคงสภาพบล็อกเดิม Byte-for-byte เสมอ (ห้าม Rebuild ทั้งบล็อก)

### 2. ความปลอดภัยและช่องโหว่ (Security, WSTG, SAST Taint Analysis & PDPA)
- ตรวจจับช่องโหว่สำคัญตาม OWASP Top 10: SQL Injection, XSS, CSRF, Path Traversal
- **Deterministic Grep Verification:** รันชุดคำสั่ง Grep ตาม `references/compliance-scorecard.md` ตรวจจับ Dangerous Functions (`eval`, `unserialize`, `pickle.loads`), SSL bypass (`verify=False`, `rejectUnauthorized: false`), และ Unsafe SQL concatenation
- **SAST Taint Analysis:** ลากสายข้อมูล Source-to-Sink (ห้าม untrusted input ไหลเข้าสู่ DB/Shell/DOM โดยไม่มี Validator/Sanitizer)
- **OWASP WSTG Business Logic:** ป้องกันการดัดแปลงราคา/จำนวนติดลบ, การ Bypass Workflow สเต็ปงาน, และ Race conditions
- ตรวจสอบ IDOR/BOLA: ห้ามเชื่อ `id` จาก URL โดยไม่อ้างอิง `current_user.id`
- ตรวจสอบการตั้งค่า CORS (ห้ามเปิด `*` ใน Route ที่ต้องการความปลอดภัย)
- ตรวจสอบ Secret & API Keys: ห้ามมี Secret หลุดไปใน Client-side bundle หรือ Git commit
- **Thai PDPA Data Masking Invariant:** ตรวจสอบว่าไม่มีเลขบัตรประชาชน 13 หลัก (`\b[0-9]{13}\b`), เบอร์โทรศัพท์, หรือรหัสผ่านหลุดไปใน Log/Telemetry และต้อง Masking ให้เหลือเฉพาะ 4 ตัวท้ายเสมอ

### 3. คุณภาพหน้าตาและส่วนติดต่อผู้ใช้ (UI/UX, Accessibility & Security UX)
- ตรวจสอบ Contrast Ratio ตามมาตรฐาน WCAG AAA (ข้อความปกติ ≥ 7:1, ข้อความใหญ่ ≥ 4.5:1)
- ตรวจสอบความถูกต้องบนจอมือถือ (Responsive, Touch target ≥ 44px, Viewport units `dvh`/`svh`)
- **Security UX & Accessible Auth (WCAG 2.2 §3.3.8):** ห้ามบล็อกการวางรหัสผ่าน/OTP (`onpaste="return false"`), บังคับใส่ `autocomplete` ที่ถูกต้องสำหรับ Password Managers (`username`, `current-password`, `new-password`, `one-time-code`)
- กวาดล้างกลิ่นอาย AI (Anti-AI-Tells): ห้ามตัวเลขเสแสร้ง (`99.8%`), ห้ามฟอนต์ Inter โหลๆ, ห้ามขีด Em-dash ใน UI

### 4. สุขภาพสถาปัตยกรรม (Architectural Health & Deep Modules)
- ตรวจจับ Shallow Modules (ไฟล์ย่อยที่แค่ส่งผ่านข้อมูลโดยไม่ลดความซับซ้อน)
- ตรวจสอบ Circular Imports และการแหกกฎ Dependency Inversion
- หากโค้ดเริ่มซับซ้อน ให้สร้าง Visual HTML Report เปรียบเทียบ Before/After ในโฟลเดอร์ Temp ตามคู่มือสถาปัตยกรรม

---

FINAL STEP & POST-FLIGHT REFLECTION:
1. **Summary & Diffs:** สรุปผลการตรวจสอบอย่างกระชับ จัดลำดับตามความรุนแรง (Critical / Warning / Improvement) พร้อมโค้ด Diff ชัดเจนตรงจุดที่ต้องแก้ไข
2. **Harness² Reflection Loop:** เมื่อตรวจรับงานผ่านเรียบร้อย สกัดบทเรียน (Lessons Learned) บันทึกลงใน KNOWLEDGE_REGISTRY.md รูปแบบ Fact Tuple 4 คอลัมน์ พร้อมสรุป 1 บรรทัดเสมอ (💡 บทเรียนที่บันทึก: <สรุปสั้น>)
