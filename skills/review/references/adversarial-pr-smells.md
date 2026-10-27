# Adversarial PR Smells & Anti-Mock Verification Guide

คู่มือการตรวจรับโค้ดเชิงปฏิปักษ์ (Adversarial Code Review) และการตรวจจับเทสต์หลอก เพื่อยกระดับความมั่นคงปลอดภัยและเสถียรภาพของระบบก่อนการผสานรวมโค้ด

---

## 1. The 3-Minute PR Smells (ตรวจจับสัญญาณอันตรายใน Diff)

ก่อนเริ่มอ่าน Business Logic ให้สแกนหา 5 สัญญาณอันตรายด้วยคำสั่งเชิงโครงสร้าง:

### A. Guardrails ถูกแอบแก้ไขหรือทำให้อ่อนลง (Relaxed Guardrails)
ตรวจสอบทันทีว่ามีการแทรกสิ่งเหล่านี้ใน diff หรือไม่:
```bash
git diff -U0 origin/main | grep -nE '^\+.*(\.skip|xit\(|nosec|ts-ignore|eslint-disable|nolint|--no-verify|// ?TODO|catch *\(?\w*\)? *\{ *\})'
```
*   **สัญญาณเตือน:** มีการลบ Assertion ทิ้ง, แก้ไข Snapshot เพื่อหนีเทสต์ตก, ขยาย Timeout ของเทสต์ให้นานขึ้น, หรือปรับลดระดับ Code Coverage ใน CI Config
*   **กฎเหล็ก:** การผ่อนปรนเกณฑ์ตรวจวัดเพื่อให้ Build ผ่าน ถือเป็น Red Flag ร้ายแรงทันที

### B. ขอบเขตความปลอดภัยและความเชื่อถือเปลี่ยนไป (Trust Boundaries Moved)
*   มีการเพิ่มแพ็กเกจ Dependency ภายนอกใหม่โดยไม่ Pin Version
*   มีการแก้ไขสิทธิ์ IAM หรือเปิดกว้าง CORS (`*`), ปิด TLS Verification, หรือสคริปต์ที่รันด้วยสิทธิ์ Root/Admin

### C. ประตูทางเดียวที่ไร้ทางถอย (One-Way Doors with No Rollback)
*   การ Drop Column หรือทำลายโครงสร้างฐานข้อมูลโดยไม่มี Rehearsed Rollback Plan
*   การแก้ไข Wire Format หรือ Enum ที่ทำให้ระบบเวอร์ชันก่อนหน้า ($N-1$) พังทันที

### D. การเปลี่ยนแปลงพฤติกรรมโดยไร้หลักฐานประจักษ์ (No Verifiable Proof)
*   แก้ Production Code หลายสิบบรรทัดแต่ไม่มี Test เพิ่มขึ้นแม้แต่บรรทัดเดียว หรือคำอธิบาย PR มีเพียงคำว่า *"minor fixes"*

---

## 2. Anti-Mock Guardrail Detection (การตรวจจับเทสต์หลอก)

คำถามหลักของการรีวิวเทสต์: **"ถ้าลบหรือทำลายโค้ดที่เพิ่งเขียน เทสต์ชุดนี้จะตกด้วยเหตุผลที่ถูกต้องหรือไม่?"**

### ก. การทดสอบเชิงประจักษ์ (Empirical Checks)
1. **Revert-the-Fix Drill:** Stash โค้ดที่แก้ทิ้ง เหลือไว้แต่ไฟล์เทสต์ใหม่ แล้วสั่งรัน หากเทสต์ยังคง "เขียว" แปลว่าเทสต์นั้นไม่ได้ทดสอบอะไรเลย
2. **Return-Null Drill:** ลองเปลี่ยน Body ของฟังก์ชันให้คืนค่า `return null;` หากทั้ง Suite ยังคงผ่าน แปลว่าเป็น Decorative Tests
3. **Mutation Drill:** พลิกเครื่องหมายจาก `<` เป็น `<=` หรือลบ `if-guard` ออกหนึ่งบรรทัด เทสต์ต้องตรวจจับได้ทันที

### ข. กลิ่นตุของม็อค (Static Mock Smells)
*   **Assert แต่ Collaborator ไร้ Assert ผลลัพธ์:** เทสต์มีแต่ `expect(mock).toHaveBeenCalledWith(...)` แต่ไม่เคยตรวจ State หรือ Return Value จริง
*   **Mock สิ่งที่ตัวเองเป็นเจ้าของ (Mocking What You Own):** ม็อคโมดูลภายในของตัวเองแทนที่จะม็อคเฉพาะ IO ภายนอกที่ควบคุมไม่ได้
*   **Tautological Tests:** ค่า Expected Value ถูกคำนวณด้วยตรรกะชุดเดียวกันกับที่ใช้ใน Implementation

---

## 3. Concurrency & Reentrancy Smells

1. **Check-then-act ข้ามจุด Yield (Await Point):**
   * ใน JavaScript/TypeScript **ทุกจุดที่มี `await` ถือเป็นการปล่อย Lock** ข้อมูลที่อ่านมาก่อนหน้าอาจถูกแก้ไขโดย Event อื่นใน Event Loop
   * *วิธีแก้:* ใช้ Atomic Upsert, Compare-And-Swap (CAS), หรือ Single-Flight de-duplication
2. **การเรียกฟังก์ชันภายนอกขณะถือ Lock (Calling Out Under Lock):**
   * ก่อให้เกิดปัญหา Deadlock จาก Lock-order inversion (A $\to$ B vs B $\to$ A)
3. **Concurrency ไร้ Backpressure:**
   * การใช้ `Promise.all(items.map(fetch))` โดยไม่มี Semaphore หรือจำกัด Concurrency Pool ทำให้เกิด Resource Exhaustion ภายใต้โหลดสูง
