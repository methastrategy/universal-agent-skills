# Quant Trading Dashboard & Multi-Account Verification Patterns

รูปแบบการตรวจสอบและแสดงผลข้อมูลการเทรด/บอทแยกตามประเภทพอร์ตโฟลิโอ (Multi-Account & Multi-Capital Verification)

---

## 1. Per-Account Verification Pattern (MeEA Dashboard)
เมื่อ Dashboard ต้องแสดงสถานะ Verified / Unverified แยกตาม Account Type (เช่น USD, USC, Cent):

### กฎการออกแบบฟังก์ชันตรวจสอบ (Audit Functions)
- Audit function ต้องรับ parameter `accountCategory: 'ALL' | 'USD' | 'USC'` อย่างชัดเจน
- **Verification Logic แยกตามประเภทพอร์ต:**
  - USD: ใช้ `empirical_usd_standard` (DD < 25% & Profit > 0)
  - USC: ใช้ `empirical_usc_cent` (DD < 25% & Profit > 0)
- **Status Badges & Metrics:**
  - แสดง completedCount / totalRequired ตามหมวดหมู่: USD = 6/6, USC = 6/6, ALL = 7/7
  - Account Compatibility badge แยก 2 ช่อง: `💵 USD ✅/❌` | `🪙 Cent ✅/❌` พร้อม Tooltip แสดงค่าจริง (DD% และ Profit)
  - ใช้ Conditional Rendering: `auditEATestCompleteness(ea, accountCategory)` ภายใน scope map callback ที่มี `ea` และ `accountCategory` รองรับ

---

## 2. Invariant & Data Integrity
- ห้ามนำเกณฑ์ความเสี่ยงหรือเกณฑ์กำไรของ Standard USD ไปปะปนกับบัญชี Cent/Micro โดยไม่แปลงหน่วย
- ทุก Data Contract ที่ส่งเข้า Dashboard ต้องมี Unit Definition ชัดเจน (`currency`, `drawdown_metric`, `verified_timestamp`)
