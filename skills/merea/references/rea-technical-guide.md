# REA Technical Integration Guide (Reverse Engineer Anything)

คู่มือการใช้ขุมพลัง REA (Reverse Engineer Anything) และเครื่องมือ MCP เพื่อวิเคราะห์ ซ่อมแซม แกะรอยโค้ด ไบนารี แอปพลิเคชัน และระบบที่ซับซ้อน

---

## 1. REA Tool Dispatch Matrix

เมื่อตรวจพบไฟล์ไบนารี (`.exe`, `.dll`, `.so`, `.dylib`), โมบายล์แพ็กเกจ (`.apk`, `.ipa`), หรือเว็บ/เดสก์ท็อปแพ็กเกจ (`.asar`, `.wasm`, `.zip`):

| Target Type | Primary REA Tool / Command | Investigation Purpose |
|:---|:---|:---|
| **Electron App / JS Bundle** | `rea analyze <path>` / `rea analyze-javascript-application` | สกัด `.asar` กู้ source maps วิเคราะห์สถาปัตยกรรม |
| **Native Binary (PE/ELF/Mach-O)**| `rea analyze <binary>` / `rea decompile` / `rea instructions` | ถอด Assembly, Xrefs, Call Graph, CFG ผ่าน Ghidra/Hopper |
| **Managed Assembly (.NET/CLI)** | `rea inspect-managed-artifact` / `inspect-managed-members` | ตรวจสอบ metadata, signatures, P/Invoke boundaries |
| **Desktop / Web Runtime** | `rea list-electron-targets` / `rea list-browser-targets` | ดักฟัง V8 Inspector, CDP network และ DOM state |
| **Evidence Validation** | `rea evidence-export` / `rea compare` | สร้างและเปรียบเทียบ Evidence bundle แบบ reproducible |

---

## 2. Investigation Protocol for Binaries

### Step 1: Binary Identification & Overview
- อ่าน Magic Bytes และ Architecture ผ่าน `rea binary_overview`
- ตรวจสอบ Hash, File Size, Segment headers, และ Dependencies
- สกัด Strings สำคัญ (URL, API endpoints, Error messages) ผ่าน `rea search_strings`

### Step 2: Control Flow & Function Analysis
- ค้นหาจุดเริ่มต้น (Entry Point) หรือ Procedure หลัก ผ่าน `rea search_procedures`
- ถอดรหัส Pseudo-code ผ่าน `rea procedure_pseudo_code`
- วิเคราะห์ Callers / Callees ผ่าน `rea procedure_callers` และ `rea procedure_callees`

### Step 3: Dynamic Runtime Observation
- สแกนหา Process Targets ที่กำลังรันอยู่ผ่าน `rea list_javascript_runtime_targets` หรือ `rea list_electron_targets`
- เก็บข้อมูล Session Snapshot เพื่อเทียบกับ Static Analysis
