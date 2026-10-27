# High-Entropy Secret Scanning & Pre-Commit Git Defense

> [!NOTE]
> มาตรฐานระดับสูงสำหรับการตรวจจับรหัสผ่าน, API Keys, และ Private Certificates ที่หลุดรอดเข้าไปในซอร์สโค้ดและ Git History ด้วยการคำนวณ Shannon Entropy และ Regex Signature ถอดแบบองค์ความรู้จาก **TruffleHog** และ **Gitleaks**

---

## 1. ทฤษฎี Shannon Entropy สำหรับตรวจจับ Secret

รหัสผ่านหรือ API Keys ที่ถูกสุ่มขึ้นโดยระบบเข้ารหัส (Cryptographically Secure Randomness) จะมีระดับความไร้ระเบียบ (Entropy) สูงกว่าข้อความภาษาอังกฤษหรือชื่อตัวแปรทั่วไปอย่างมีนัยสำคัญ:

$$\mathcal{H}(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$

- **ข้อความภาษาอังกฤษทั่วไป:** $\mathcal{H} \approx 1.5 - 3.0$
- **ชื่อฟังก์ชัน/ตัวแปรในโค้ด:** $\mathcal{H} \approx 2.5 - 3.5$
- **Hex Encoded Keys (เช่น MD5/SHA256):** เกณฑ์แจ้งเตือนเมื่อ $\mathcal{H} \ge 3.0$
- **Base64 Encoded Keys / Token สุ่ม:** เกณฑ์แจ้งเตือนเมื่อ $\mathcal{H} \ge 4.5$

```typescript
// utils/entropy.ts
export function calculateShannonEntropy(str: string): number {
  const len = str.length;
  if (len === 0) return 0;

  const frequencies = new Map<string, number>();
  for (const char of str) {
    frequencies.set(char, (frequencies.get(char) || 0) + 1);
  }

  let entropy = 0;
  for (const count of frequencies.values()) {
    const p = count / len;
    entropy -= p * Math.log2(p);
  }

  return entropy;
}
```

---

## 2. Signature Patterns ของคีย์สำคัญ (Known Signatures)

| ผู้ให้บริการ (Provider) | รูปแบบ Regular Expression | ตัวอย่าง Token Prefix |
| :--- | :--- | :--- |
| **AWS Access Key** | `AKIA[0-9A-Z]{16}` | `AKIAIOSFODNN7EXAMPLE` |
| **OpenAI Secret Key** | `sk-[a-zA-Z0-9]{48}` หรือ `sk-proj-[a-zA-Z0-9_-]{80,}` | `sk-proj-abc123...` |
| **GitHub Personal Token** | `ghp_[0-9a-zA-Z]{36}` | `ghp_16DigitsAndLetters...` |
| **Stripe Live Secret** | `sk_live_[0-9a-zA-Z]{24,}` | `sk_live_51A...` |
| **RSA / EC Private Key** | `-----BEGIN (RSA \|EC \|OPENSSH )?PRIVATE KEY-----` | Private Key PEM block |

---

## 3. Pre-Commit Hook Defense Script

สคริปต์ป้องกันการ Commit ไฟล์ที่มี Secret ติดไปด้วยในระดับ Local Git Hook:

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit

echo "[*] Auditing staged files for high-entropy secrets and credentials..."

# 1. ตรวจสอบคีย์สำคัญด้วย Regex Signatures บน Staged Diff
SECRETS_FOUND=$(git diff --cached --unified=0 | grep -E -i \
  "AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{32,}|ghp_[0-9a-zA-Z]{36}|BEGIN (RSA|OPENSSH)? PRIVATE KEY" \
  | grep "^+")

if [ -n "$SECRETS_FOUND" ]; then
  echo "🚨 CRITICAL ERROR: ตรวจพบคีย์หรือรหัสผ่านที่มีลักษณะคล้าย API Secret ใน Staged Changes!"
  echo "$SECRETS_FOUND"
  echo "กรุณาลบคีย์ออกจากโค้ดและย้ายไปใส่ใน Environment Variable (.env) ก่อน Commit!"
  exit 1
fi

echo "✅ Pre-commit Secret Audit: PASS"
exit 0
```

---

## 4. Playbook เมื่อพบคีย์รั่วไหล (Incident Response)

1. **Invalidate & Rotate ทันที:** สั่ง Revoke คีย์ที่หลุดผ่าน Console ของ Provider ทันทีโดยไม่ต้องเสียเวลาแก้ Git (ถือว่าคีย์ Compromised ทันทีที่ Commit หรือ Push)
2. **ห้ามใช้วิธี Commit ทับ:** การสร้าง Commit ใหม่เพื่อลบไฟล์ ไม่ได้ลบคีย์ออกจากประวัติ Git (`git log` ยังเห็นไบต์เดิม)
3. **Purge History:** ใช้เครื่องมือ `git-filter-repo` หรือ BFG Repo-Cleaner เพื่อตัดสายประวัติของ Secret นั้นทิ้งอย่างถาวร:
   ```bash
   git-filter-repo --replace-text expressions-to-strip.txt
   ```
