# Resilient E2E Visual Testing & Auto-Wait Assertions

> [!NOTE]
> มาตรฐานระดับสูงสำหรับการเขียนและตรวจรับงาน End-to-End Testing ที่ทนทาน ไม่เปราะบาง (Zero-Flake) และยึดพฤติกรรมผู้ใช้เป็นหลัก ถอดแบบองค์ความรู้จาก **Microsoft Playwright**, **Testing Library**, และ **Vitest**

---

## 1. ปรัชญา User-Centric Testing Hierarchy

> *"ยิ่งการทดสอบของคุณจำลองพฤติกรรมเสมือนผู้ใช้จริงมากเท่าไหร่ คุณยิ่งมั่นใจในความถูกต้องของซอฟต์แวร์มากเท่านั้น"*

### ลำดับความสำคัญในการเลือก Locator (Locator Selection Priority)
1. **`getByRole(role, { name })` (แนะนำสูงสุด):** สะท้อนสิ่งที่ผู้ใช้และ Screen Reader มองเห็น เช่น ปุ่ม, ลิงก์, ช่องกรอก
2. **`getByLabel(text)`:** สำหรับช่อง Input ในฟอร์มที่มี Label กำกับชัดเจน
3. **`getByPlaceholder(text)` / `getByText(text)`:** ใช้เมื่อไม่มี Role เฉพาะ
4. **`getByTestId('...')` (ทางเลือกสุดท้าย):** อนุญาตเฉพาะเมื่อองค์ประกอบนั้นเป็น Dynamic Canvas หรือโครงสร้างที่ไม่มี Accessibility Role

```typescript
// ❌ ผิดมหันต์: เปราะบาง พังทันทีที่แก้ CSS/DOM structure
await page.locator('div.btn-wrapper > button.bg-blue-600').click();

// ✅ ถูกต้อง: ยึดตาม Accessibility Role เสมือนผู้ใช้จริงคลิก
await page.getByRole('button', { name: /ยืนยันคำสั่งซื้อ/i }).click();
```

---

## 2. Web-First Auto-Wait Assertions (Zero-Flake Architecture)

ห้ามใช้ `page.waitForTimeout(3000)` หรือคำสั่ง Sleep สุ่มเดาเด็ดขาด Playwright มีระบบ **Web-First Assertions** ที่จะวนทดสอบซ้ำอัตโนมัติ (Polling Auto-Wait) จนกว่าเงื่อนไขจะเป็นจริง หรือ Timeout 5,000ms:

```typescript
import { test, expect } from '@playwright/test';

test('เปิดปิด Modal และตรวจสอบ Focus Management', async ({ page }) => {
  await page.goto('/dashboard');

  const openBtn = page.getByRole('button', { name: 'สร้างออเดอร์ใหม่' });
  await openBtn.click();

  const dialog = page.getByRole('dialog', { name: 'ตั้งค่าออเดอร์' });
  // Auto-wait: รอจนกว่า Dialog จะ render และมี opacity/visibility พร้อม
  await expect(dialog).toBeVisible();

  // ตรวจสอบว่า Focus กระโดดไปที่ช่องแรกของ Dialog ทันที
  await expect(dialog.getByLabel('คู่เงิน (Symbol)')).toBeFocused();

  // กดปุ่ม Escape
  await page.keyboard.press('Escape');

  // ตรวจสอบว่า Dialog หายไป และ Focus กลับคืนปุ่มเปิด
  await expect(dialog).toBeHidden();
  await expect(openBtn).toBeFocused();
});
```

---

## 3. Network Interception & Deterministic API Mocking

ทดสอบ Edge Cases (Network Failure, 500 Server Error, Rate Limit) ได้โดยไม่ต้องพึ่งพาเซิร์ฟเวอร์จริง:

```typescript
test('แสดง Error Banner เมื่อ API ล่ม', async ({ page }) => {
  // ดักจับและจำลอง Network 500 Error
  await page.route('**/api/v1/orders', async (route) => {
    await route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Internal Server Error' }),
    });
  });

  await page.goto('/trade');
  await page.getByRole('button', { name: 'ส่งคำสั่ง' }).click();

  // ตรวจสอบ Error Banner
  const alert = page.getByRole('alert');
  await expect(alert).toContainText('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
});
```

---

## 4. Visual Regression Snapshot Protocol

การจับภาพหน้าจอเทียบความต่างระดับพิกเซล (Pixel-by-pixel Diffs) พร้อมการมาสก์จุดที่เปลี่ยนแปลงตามเวลา (Timestamp, UUID):

```typescript
test('หน้าจอ Terminal ต้องคงอัตลักษณ์ Pixel-Perfect', async ({ page }) => {
  await page.goto('/terminal');

  // ซ่อนองค์ประกอบที่ขยับตามเวลา เพื่อไม่ให้เกิด False-Positive Diff
  await page.addStyleTag({
    content: '.live-clock, .ticker-tape { visibility: hidden !important; }',
  });

  // เทียบภาพกับ Snapshot แม่แบบ (Threshold ไม่เกิน 1%)
  await expect(page).toHaveScreenshot('terminal-golden-baseline.png', {
    maxDiffPixelRatio: 0.01,
  });
});
```
