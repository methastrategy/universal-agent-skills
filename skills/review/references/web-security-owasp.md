# Web Security, OWASP WSTG & SAST Taint Analysis Standards

Essential security practices, vulnerability mitigation protocols, and testing methodologies derived from **OWASP Top 10**, **OWASP Web Security Testing Guide (WSTG v4.2)**, and **Semgrep AST Taint Analysis**.

---

## 1. SAST Taint Analysis Protocol (Source-to-Sink Tracking)

When auditing code, trace untrusted data flows end-to-end like a Static Application Security Testing (SAST) engine:

- **Sources (Untrusted Ingress):** `req.body`, `req.query`, `req.params`, `req.headers`, file uploads, WebSocket messages, external third-party webhook payloads.
- **Sanitizers / Validators:** Strict schema validation (Zod, Joi, Pydantic), parameterization, escaping, whitelist matching.
- **Sinks (Critical Execution Points):**
  - Database queries: Raw string concatenation $\rightarrow$ **SQLi / NoSQLi**
  - OS command execution: `child_process.exec()`, `os.system()` $\rightarrow$ **Command Injection**
  - DOM insertion: `innerHTML`, `v-html`, `dangerouslySetInnerHTML` $\rightarrow$ **Cross-Site Scripting (XSS)**
  - Dynamic code evaluation: `eval()`, `new Function()`, `pickle.loads()` $\rightarrow$ **Remote Code Execution (RCE)**
  - File system access: `fs.readFile(path)`, `open(path)` without canonical path resolution $\rightarrow$ **Path Traversal**

> [!CAUTION]
> **Taint Invariant:** If data flows from a **Source** to a **Sink** without passing through an explicit, verified **Sanitizer**, flag as **CRITICAL VULNERABILITY** immediately.

---

## 2. OWASP WSTG Advanced Testing Checklist (Beyond Top 10)

### 2.1 Business Logic Flaws (WSTG-BUSL)
- **Data Integrity & Numerical Tampering:** Enforce server-side checks against negative values, fractional amounts, or integer overflows in prices, quantities, and balances.
- **Workflow & Step Bypass:** Ensure multi-step operations (checkout, onboarding, password reset) enforce strict sequential state machines on the backend; verify that steps cannot be skipped directly via API.
- **Rate Limit & Concurrency Abuse:** Guard against race conditions (double-spend, coupon reuse) using transactional row locking (`SELECT FOR UPDATE`) or atomic database operations.

### 2.2 Authorization & Access Control (WSTG-ATHZ)
- **IDOR / BOLA Prevention (WSTG-ATHZ-04):** Never trust object IDs (`id`, `uuid`) supplied in URLs or request payloads without asserting tenant/user ownership (`WHERE id = :id AND user_id = :current_user_id`).
- **Function-Level Access Control (WSTG-ATHZ-01):** Verify role boundaries (`ADMIN`, `USER`, `EDITOR`) on EVERY individual route and server action; never rely on UI button hiding.
- **Privilege Escalation:** Verify that users cannot alter their own roles or scopes during profile update requests.

### 2.3 Authentication & Session Management (WSTG-ATHN / SESS)
- **Token Storage Hygiene:** Store session tokens / refresh tokens in `HttpOnly`, `Secure`, `SameSite=Strict` cookies to neutralize XSS extraction. Never place JWTs in `localStorage`.
- **JWT Cryptographic Rules:**
  - Reject tokens with `alg: "none"`.
  - Enforce asymmetric validation (`RS256`, `EdDSA`) or secure high-entropy secrets for symmetric (`HS256`).
  - Short-lived Access Tokens (5–15 min) with cryptographic Refresh Token rotation.
- **Session Termination:** Invalidate tokens server-side upon logout; maintain revocation lists or sliding token version counters.

### 2.4 Error Handling & Information Disclosure (WSTG-ERRH / INFO)
- **Zero Stack Traces in Production:** Sanitize API error responses (`500 Internal Server Error`); log stack traces internally to secure telemetry, never return database schema, table names, or SQL fragments to the client.
- **Sensitive File Exposure:** Ensure `.env`, `.git`, `.bak`, and internal configuration files are blocked by the web server / reverse proxy.

---

## 3. Defense-in-Depth & Header Invariants

- **Content-Security-Policy (CSP):** `default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none';`
- **Security Headers:**
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **CORS Invariant:** Never set `Access-Control-Allow-Origin: *` in combination with `Access-Control-Allow-Credentials: true`. Whitelist explicit trusted origins only.
- **Input Sanitization & Output Encoding:** Sanitize upon ingress via typed schemas; contextually encode upon egress to prevent injection.

---

## 4. DAST & Dynamic Scanning Playbook (Nuclei & ZAP Integration)

When testing live staging environments or public-facing deployments, complement SAST/WSTG with automated Dynamic Application Security Testing (DAST):

### 4.1 Nuclei Fast Vulnerability & Misconfig Scanning
- **Best For:** Fast reconnaissance, exposed endpoints, zero-day CVE templates, and sensitive file leak detection.
- **Workflow & Commands:**
  ```bash
  # ตรวจจับ Critical Misconfiguration และ Exposure เบื้องต้น
  nuclei -u https://staging.example.com -tags exposure,misconfig,cve -severity critical,high

  # ตรวจสอบการหลุดของไฟล์คอนฟิก (.env, .git, backup archives)
  nuclei -u https://staging.example.com -id git-config,env-file,backup-files
  ```
- **Rule of Engagement:** รันเฉพาะบน Staging / Sandbox environment ที่ได้รับอนุญาตเท่านั้น ห้ามยิง production โดยไม่ได้รับอนุมัติ

### 4.2 OWASP ZAP (ZAProxy) Full Dynamic Fuzzing
- **Best For:** Deep session fuzzing, spidering, and parameter injection (SQLi/XSS/CSRF).
- **Workflow:**
  1. **Spidering:** สแกนหา endpoint และ parameter ทั้งหมดในเว็บ
  2. **Passive Scan:** ตรวจจับ headers, cookie flags (`HttpOnly`, `Secure`), และ information disclosure
  3. **Active Scan:** ยิง fuzzing payload ทดสอบ input fields และ API parameters ก่อน release
