# Universal Compliance & Security Verification Scorecard

Deterministic verification scorecard, regex scanning suite, and compliance standard spanning **OWASP Top 10:2025**, **ASVS 5.0**, **NIST SSDF SP 800-218**, **Thai PDPA 2562**, **ISO/IEC 27001**, and **WCAG 2.2 Accessible Authentication**.

---

## 1. Deterministic Grep Matrix (Pre-Deployment Zero-Dependency Scans)

ก่อน release หรือ deploy ทุกครั้ง ให้รันคำสั่ง Grep ต่อไปนี้เพื่อดักจับข้อผิดพลาดร้ายแรง (Critical Red Flags):

### 1.1 Dangerous Code Execution & Dynamic Evaluation
```bash
# ตรวจจับ eval, Dynamic Function, Unsafe Deserialization ในทุกภาษา
grep -rnE "(eval\(|new Function\(|unserialize\(|pickle\.loads\(|marshal\.loads\(|yaml\.load\([^,)]+\))" --include="*.js" --include="*.ts" --include="*.py" --include="*.php" src/
```

### 1.2 Insecure Transport & SSL Verification Bypass
```bash
# ตรวจจับการปิด SSL Verification (CRITICAL BLOCK DEPLOY)
grep -rnE "(verify\s*=\s*False|rejectUnauthorized\s*:\s*false|CURLOPT_SSL_VERIFYPEER.*(?:0|false)|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0)" src/
```

### 1.3 SQL Injection Sinks (Raw String Concatenation)
```bash
# ตรวจจับ String interpolation หรือ formatting ใน SQL query
grep -rnE "(execute\(f[\"']SELECT|execute\([\"'].*%s|query\(f[\"']|SELECT\s+.*\+\s*['\"]|\bWHERE\s+.*=\s*['\"]\s*\+)" src/
```

### 1.4 Hardcoded Secrets & Private Credentials
```bash
# ตรวจจับ API Keys, Bearer Tokens, Private Keys, Passwords ในโค้ด
grep -rnE "(password|api_key|secret|token|private_key)\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{8,}['\"]" --exclude-dir={node_modules,.git,dist,__pycache__} src/
```

### 1.5 DOM XSS Sinks (Client-Side)
```bash
# ตรวจจับการยัด HTML โดยตรงไม่ผ่าน Sanitizer
grep -rnE "(dangerouslySetInnerHTML|innerHTML\s*=|v-html|document\.write\()" src/
```

### 1.6 Thai PDPA & Sensitive Data Exposure in Logs
```bash
# ตรวจจับเลขบัตรประชาชนไทย 13 หลัก หรือ รหัสผ่าน/Token หลุดไปใน Logger หรือ Console
grep -rnE "(console\.(log|info|warn|error)|print\(|logger\.(info|debug|warn|error))\([\"'].*(password|secret|token|otp)" src/
grep -rnE "\b[0-9]{13}\b" --exclude-dir={node_modules,.git,dist,__pycache__} src/
```

---

## 2. Multi-Stack Automated Audit Suites

### 2.1 JavaScript / TypeScript / Node.js
```bash
# 1. Dependency Vulnerability Audit
npm audit --audit-level=high

# 2. SAST Taint & OWASP Top 10 Scan (Semgrep)
npx semgrep --config "p/security-audit" --config "p/owasp-top-ten" --error src/

# 3. Secret Leakage Detection
gitleaks detect --source . --no-banner
```

### 2.2 Python (FastAPI / Cadastre / GIS)
```bash
# 1. Known Vulnerability Scanning in Dependencies
pip-audit

# 2. AST Static Security Analysis
bandit -r src/ -ll -ii

# 3. Code Quality & Formatting
ruff check src/
```

### 2.3 Cloud & VPS Hardening (Linux / Ubuntu)
```bash
# 1. ตรวจสอบ SSH Configuration (ห้ามใช้ Password, ห้าม Root login)
grep -E "^(PasswordAuthentication|PermitRootLogin|MaxAuthTries)" /etc/ssh/sshd_config
# Baseline: PasswordAuthentication no, PermitRootLogin no, MaxAuthTries 3

# 2. UFW Firewall Baseline
ufw status verbose
# Baseline: Default deny incoming, Allow 443/tcp, Allow 80/tcp, Limit 22/tcp (SSH)

# 3. Database Listening Interface
# Baseline: ต้อง bind เฉพาะ 127.0.0.1 หรือ internal Docker network (ห้ามเปิด 0.0.0.0 สู่ Public IP)
```

---

## 3. Thai PDPA 2562 Compliance Standard (พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล)

| หัวข้อ | ข้อกำหนด | การตรวจสอบ (Audit Criteria) |
| :--- | :--- | :--- |
| **ฐานความยินยอม (Consent)** | ม.19: ขอความยินยอมชัดแจ้ง แยกวัตถุประสงค์ ห้าม Pre-ticked box | หน้าสมัคร/ฟอร์มห้ามติ๊กยอมรับล่วงหน้า และต้องบันทึก `consent_version`, `timestamp` |
| **การปกปิดข้อมูล (Masking)** | ม.26: ข้อมูลระบุตัวตน (เลขบัตร 13 หลัก, เบอร์โทร, เลขบัญชี) | **ห้ามพ่นลง Log เด็ดขาด** แสดงผลใน UI ได้เฉพาะ 4 ตัวท้าย (เช่น `xxx-xxx-1234`) |
| **การแจ้งเหตุละเมิด (Breach)** | ม.37(4): แจ้งสำนักงาน สคส. ภายใน 72 ชั่วโมงเมื่อมีเหตุข้อมูลรั่ว | ต้องมี Workflow จัดเตรียมเอกสารระบุขอบเขตข้อมูลและแนวทางเยียวยา |
| **สิทธิเจ้าของข้อมูล (DSAR)** | ม.30–36: ขอเข้าถึง, แก้ไข, ขอสำเนา, หรือขอลบข้อมูล | ระบบต้องมี API หรือขั้นตอนส่งออกข้อมูล (Export) และลบข้อมูล (Purge/Anonymize) |
| **ความมั่นคงปลอดภัย (Security)** | ม.37(1): เข้ารหัสข้อมูลขณะจัดเก็บ (At Rest: AES-256) และส่งผ่าน (In Transit: TLS 1.3) | ห้ามเก็บ Plaintext Passwords และต้องบังคับใช้ HTTPS ทุก Endpoint |

---

## 4. Security UX Standards (WCAG 2.2 §3.3.8 Accessible Authentication)

1. **ห้ามบล็อก Paste / Clipboard (Strict Invariant):**
   - ❌ **Bad:** `<input type="password" onpaste="return false;" oncopy="return false;">`
   - ✅ **Good:** รองรับ Password Managers (1Password, Bitwarden, Apple Keychain) ให้ Paste ได้อย่างอิสระ
2. **ระบุแอตทริบิวต์ Semantics ชัดเจน:**
   - ช่องใส่ชื่อผู้ใช้: `autocomplete="username"`
   - ช่องใส่รหัสผ่านปัจจุบัน: `autocomplete="current-password"`
   - ช่องตั้งรหัสผ่านใหม่: `autocomplete="new-password"`
   - ช่องใส่ OTP: `autocomplete="one-time-code"`
3. **ลดภาระความจำทางสมอง (No Cognitive Memory Tests):**
   - ห้ามบังคับจำรหัสปริศนาหรือแก้พัซเซิลภาพโดยไม่มีทางเลือกสำรอง เช่น Passkeys (WebAuthn), Magic Link หรือ OTP
4. **ความชัดเจนของ Focus & Touch Target:**
   - กล่อง Input และปุ่ม Login ต้องมี Hit-Target $\ge 44 \times 44\text{px}$
   - เส้น Focus Visible ต้องเห็นชัดเจน (`outline: 2px solid Highlight; outline-offset: 2px;`) ไม่ถูกกลืนไปกับพื้นหลัง
