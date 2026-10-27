# Fast Toolchain Acceleration Protocol (uv, ruff, biome)

คู่มือการยกระดับความเร็วในการพัฒนาและทดสอบระบบด้วย Toolchain ยุคใหม่ที่เขียนด้วยภาษา **Rust** (เช่น `uv`, `ruff`, และ `biome`) เพื่อลดรอบเวลาการรอคอย (Feedback Loop Latency) จากหลักนาทีเหลือเพียงเสี้ยววินาที

---

## 1. การปฏิวัติความเร็วด้วย Rust-Based Tooling

ในกระบวนการทำงานแบบ Agentic Autonomous Execution ความเร็วในการติดตั้ง Package, ตรวจสอบไวยากรณ์ (Linting), และรันชุดทดสอบ คือตัวกำหนดว่า Agent จะทำงานสำเร็จได้รวดเร็วเพียงใด

| งานที่ต้องทำ | เครื่องมือยุคเดิม (ช้า) | เครื่องมือยุคใหม่ (Rust-backed เร็ว 10–100x) |
| :--- | :--- | :--- |
| **Python Package Resolution** | `pip` / `poetry` (15–60 วินาที) | **`uv`** (< 500 มิลลิวินาที) |
| **Python Lint & Autofix** | `flake8` / `black` / `isort` (5–15 วินาที) | **`ruff`** (< 100 มิลลิวินาที) |
| **JS/TS Lint & Format** | `eslint` + `prettier` (8–20 วินาที) | **`biome`** / **`oxlint`** (< 200 มิลลิวินาที) |
| **JS/TS Build & Bundle** | `webpack` / `babel` (30–90 วินาที) | **`esbuild`** / **`swc`** / **`bun`** (< 1 วินาที) |

---

## 2. มาตรฐานการใช้งาน `uv` (Ultra-Fast Python Package Management)

เมื่อต้องจัดการ Virtual Environment หรือติดตั้ง Library ในโปรเจกต์ Python:
- **สร้าง Virtualenv ในพริบตา:**
  ```powershell
  uv venv .venv
  ```
- **ติดตั้ง Dependency ด้วยความเร็วระดับ Caching สูงสุด:**
  ```powershell
  uv pip install <package_name>
  ```
- **รันสคริปต์แบบแยก Environment ชั่วคราว (Ephemeral):**
  ```powershell
  uv run python script.py
  ```

---

## 3. มาตรฐานการใช้งาน `ruff` (Sub-Millisecond Python Linting)

แทนที่การลง linter หลายตัว ให้ใช้ `ruff` เพียงตัวเดียวครอบคลุมทั้ง Flake8, Black, Isort, และ Pyupgrade:
- **สแกนหาข้อผิดพลาดและช่องโหว่ทันที:**
  ```powershell
  ruff check .
  ```
- **สั่งแก้และจัดรูปแบบโค้ดอัตโนมัติ (Safe Autofix):**
  ```powershell
  ruff check --fix .
  ruff format .
  ```

---

## 4. มาตรฐานการใช้งาน `biome` ในโปรเจกต์ TypeScript/JavaScript

ในฝั่ง Node/Web ให้แนะนำการใช้ `biome` แทนคู่หูเดิม `eslint + prettier`:
- **สแกนและจัดระเบียบ Import:**
  ```powershell
  npx @biomejs/biome check --write .
  ```
- **จุดเด่น:** ประหยัด Token ในแชต เนื่องจากข้อความ Error ของ Biome ถูกออกแบบให้ตรงจุดและสั้นกระชับกว่า ESLint แบบดั้งเดิม
