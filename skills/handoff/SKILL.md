---
name: handoff
description: สรุปและส่งต่องานค้างข้ามแชตหรือข้ามโมเดล — ใช้เมื่อ Token ใกล้หมด เปลี่ยนโมเดล งานยาว หรือจะหยุดทำงานชั่วคราว (session handoff, context compacting, resume)
---

# Handoff
เขียนที่เดียว: `D:\WSL\.gemini\handoffs\` (นอก workspace) ห้ามสร้างในโปรเจกต์ ห้ามเขียนทับ plan.md
- `latest-<ชื่อโฟลเดอร์ workspace>.md` (เขียนทับได้) + สำเนา `handoff-<ชื่อ>-yyyyMMdd-HHmm.md` (ไม่ลบสำเนาเก่าเอง)
- บรรทัดแรก: `workspace: <พาธเต็ม> | created: yyyy-MM-dd HH:mm | model: <ชื่อ>`
เนื้อหา (เฉพาะที่ตรวจแล้ว):
1. Goal + ข้อจำกัดที่ยังมีผล
2. ทำเสร็จแล้ว: พาธไฟล์ที่สร้าง/แก้ + คำสั่งที่รันพร้อมผลจริง
3. ข้อเท็จจริงที่พิสูจน์แล้ว / สิ่งที่ลองแล้วไม่เวิร์ก
4. งานค้างเรียงตามสำคัญ + blockers
5. Next action เดียวที่ทำต่อได้ทันที (พาธ/คำสั่งที่ตรวจแล้ว)
ห้ามใส่ secret/API key/token; ห้ามเขียนจากความจำเมื่อมีไฟล์หรือ output ให้ตรวจ; ตอบผู้ใช้เป็นพาธไฟล์ที่เขียน

---

## Progressive Disclosure Format (claude-mem Pattern)

เพื่อประหยัด Token เวลา `/continue` อ่านไฟล์ Handoff ให้จัดโครงสร้างไฟล์ใน `D:\WSL\.gemini\handoffs\` เป็น 2 ชั้น:

**ชั้น 1 — Fast Index (≤ 30 บรรทัด, อ่านเป็นลำดับแรกเสมอ):**
```text
GOAL: <ประโยคเดียว>
STATUS: <DONE | IN_PROGRESS | BLOCKED>
LAST_ACTION: <คำสั่งหรือไฟล์ล่าสุดที่แก้>
NEXT_ACTION: <คำสั่งเดียวที่ทำต่อได้ทันที พร้อม full path>
BLOCKERS: <ระบุถ้ามี หรือใส่ none>
```

**ชั้น 2 — Deep Context (อ่านเมื่อจำเป็นต้องแกะรายละเอียดเพิ่ม):**
รายละเอียดเต็ม 5 ข้อตามข้อกำหนดด้านบน (Goals, Completed, Verified Facts, Pending Tasks, Next Action)

---

## Clean Domain Handoff (ข้ามโปรเจกต์ / รีเซ็ต Context Window)

เมื่อผู้ใช้ต้องการสลับงานข้ามโปรเจกต์หรือข้ามโดเมนใหญ่ (เช่น จาก System Engineering ไป Project วิจัย/สำรวจ) ให้สร้าง **Handoff Block สำเร็จรูป** ให้ผู้ใช้คัดลอกไปเปิดแชตใหม่:

```text
/plan /architect
สวัสดีครับ ตอนนี้ผมอยู่ที่ Workspace: [Path เต็มของโปรเจกต์ใหม่]
เป้าหมายของเซสชันนี้คือ: [ระบุผลลัพธ์ที่ต้องการ]
บริบทและสถานะล่าสุด:
1. [สรุป 3 ข้อหลักที่ตกลงกันไว้]
ไฟล์อ้างอิงสำคัญ: [ระบุไฟล์ 1-2 ไฟล์ในโฟลเดอร์นั้น]
```
