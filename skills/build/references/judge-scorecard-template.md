# Judge Scorecard Template

Template มาตรฐานสำหรับส่งมอบงานทุก milestone ตาม GEMINI.md §2 Judge Scorecard Delivery Standard

---

## ⚖️ Executive Judge Scorecard

### 1. ✅ What & Why
**Delivered:** [สิ่งที่ทำสำเร็จ — ระบุ file/feature ที่จับต้องได้ พร้อม hyperlink]

**Pre-Ship Polish:** [สิ่งที่เพิ่มเติมโดยไม่ต้องรอให้สั่ง เช่น loading state, error boundary, keyboard nav]

---

### 2. 🔬 Verification Proof

**Proof Grounding Level:** `[In-Process Real I/O]` | `[Unit / Integration Suite]` | `[Static Compilation & Lint]` *(Zero-Mock Assurance)*

```
[วาง verbatim output ของ test runner / tsc / lint ที่นี่ — ห้ามสรุปด้วยคำพูด ต้องเป็น raw output]

ตัวอย่าง:
✓ 24/24 tests passed in 0.8s
tsc: 0 errors
eslint: 0 errors, 0 warnings
```

---

### 3. ⚠️ Attention Flags

```
[ความเสี่ยง / Breaking Changes / Dependencies ใหม่ที่ต้องรู้]
[หรือ "🟢 Clean — 0 flags, backward-compatible"]
```

---

### 4. 🔗 Links

| Type | Link |
|---|---|
| **Files Changed** | [filename](file:///absolute/path/to/file) |
| **Commit** | `git SHA` — `commit message` |
| **Preview** | `https://...` (ถ้ามี) |

---

## Usage Notes

- ใช้ template นี้ทุกครั้งหลังงานสำคัญเสร็จ (feature, bugfix, architecture change)
- Section 2 ต้องเป็น verbatim raw output เสมอ — ห้ามแทนด้วยคำอธิบาย
- Section 3 ถ้า clean จริงให้เขียน "🟢 Clean" อย่างชัดเจน ไม่ใช่แค่เว้นว่าง
- Goal: ผู้ใช้ควรอ่านและตัดสินใจ approve/reject ได้ใน 10 วินาที
