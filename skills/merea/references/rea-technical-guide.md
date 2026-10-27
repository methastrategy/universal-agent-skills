# REA Technical Integration Guide (Reverse Engineer Anything)

คู่มือใช้ REA (`rea-agents` จาก `github.com/morluto/rea`) แกะไบนารี แอป JS/Electron, .NET assembly, artefact และ runtime behaviour — พร้อมกติกาที่ทำให้ต่อกับ merea engine ได้แบบสอบทานได้

---

## 1. REA Tool Dispatch Matrix

| Target Type | Primary Command | Purpose |
|:---|:---|:---|
| **Managed Assembly (.NET/CLI)** | `inspect-managed-artifact` → `inspect-managed-members --format json` → `project-managed-application-graph` | metadata, IL anchors, call graph — ใช้ได้โดยไม่ต้องมี native engine |
| **Electron / JS bundle** | `analyze-javascript-application` (absolute path, extracted dir) | statically reconstruct module graph, source maps |
| **Native PE/ELF/Mach-O** | `analyze` / `decompile` / `instructions` | ต้องมี Ghidra หรือ Hopper — ไม่มี = fail closed `provider_unavailable` |
| **Archive / package** | `inspect-artifact` / `extract-artifact` | inventory + safe extraction |
| **Runtime (browser/Electron)** | `inspect-web-page` / `list-electron-targets` / `observe-web-session` | CDP/V8 observation |
| **Evidence ops** | `evidence-export` / `compare` / `compare-managed-members` | reproducible comparison ระหว่างสอง observation |

---

## 1.1 Triage packaging class ก่อนเลือก tool (ห้ามเดาจากชื่อโฟลเดอร์)

REA เห็นแค่ managed CLR, native (ต้องมี engine) และ artefact container — อะไรที่ถูก freeze/pack ต้องแตกก่อน ตรวจจาก **ไฟล์จริง** ไม่ใช่ marker ในโฟลเดอร์ เพราะโฟลเดอร์มักมีของค้างจาก build เก่า (`.pyd` ของ cp39 อยู่ในแอปที่ archive เป็น 3.12) หรือมี `node_modules`/`python-embed` ปนจน heuristic ผิด — ตัวอย่างจริง: exe ที่ดูเหมือน native x64 ทั้งโฟลเดอร์ กลายเป็น PyInstaller Python 3.12 เมื่อเปิด MEI cookie

| สัญญาณที่อ่านจากไฟล์ | Class | ทางที่ใช้ได้ |
|:---|:---|:---|
| `BSJB` ใน ~600KB แรกของ PE | managed .NET | managed pipeline (§3) |
| `MEI` cookie ท้ายไฟล์ (`MEI\x0c\x0b\x0a\x0b\x0e`) | PyInstaller-frozen Python | `python -m pyinstxtractor_ng <exe>` + interpreter ที่ minor version ตรงกับ `Python version:` ที่มันรายงาน (§5) |
| `resources\app.asar` หรือ `v8_context_snapshot.bin` | Electron | `inspect-artifact --integrity-policy record-and-continue` → ตัด `node_modules` → `analyze-javascript-application` |
| `Inno Setup` / `Nullsoft` / WiX Burn strings | installer SFX | `innoextract` / `7z x` ก่อน แล้วค่อยวิเคราะห์ payload |
| มีแต่ `.jar` | Java | ต้องมี `REA_JADX_MCP_JAR` ไม่งั้นได้แค่ inventory |
| PE machine `0x8664` ไม่มี CLR | native x64 | ต้องมี Ghidra/Hopper ก่อน (§4) |
| PE machine `0x14c` | native x86 | บน Windows decompile ไม่ได้เลย (§4) — แจ้งผู้ใช้ทันที ไม่ต้องรอลง engine |

PE machine อ่านจาก `e_lfanew` ที่ offset `0x3c` → FileHeader.Machine; เก็บ `sha256` + `mvid` ไว้ทุกครั้งเพราะ token ของ managed เป็น build-local

## 1.2 Fleet audit ("ในเครื่องมีอะไร แกะอะไรได้บ้าง")

1. เก็บรายการจาก registry `Uninstall` ทั้ง `HKLM/HKCU` × `KEY_WOW64_64KEY/32KEY` แล้ว dedupe ด้วย DisplayName (ของจริงหลักร้อย entry และเกือบครึ่งเป็น runtime/redist ที่ไม่ต้องวิเคราะห์)
2. `InstallLocation` ว่างบ่อย — fallback ไป `dirname` ของ executable ใน `UninstallString`
3. ไล่ `*.exe` ลึกไม่เกิน 2 ชั้นต่อโฟลเดอร์ แล้วจำแนกด้วยตาราง §1.1 (อ่าน PE header จริง ไม่ใช่ดูชื่อ)
4. รายงานเป็น **กลุ่ม capability: ทำได้เต็ม / บางส่วน / ไม่ได้ + เหตุผลกลไก + ตัวอย่าง 1 ตัว** ไม่ใช่ list ยาวทั้งเครื่อง — ผู้ใช้ต้องการรู้ว่าอะไรใช้ได้ ไม่ใช่ทะเบียนโปรแกรม
5. คลัง installer มักไม่ได้อยู่ Downloads — เช็กไดรฟ์อื่นด้วย และรายงาน packer ของแต่ละไฟล์

---

## 2. Version & Invocation Hygiene (ทำก่อนทุกครั้ง)

- ตรวจว่า CLI ตรงกับ package ที่ลงจริง: `rea --version` ต้องเท่ากับ `npm view rea-agents version`. ถ้าไม่ตรง แปลว่ามี global install เก่าค้าง — แก้ด้วย `npm install -g rea-agents@<latest>` แล้วตรวจซ้ำ **อย่าถือว่า mismatch เป็นเรื่องปกติ** (capability ที่เอกสารพูดถึงจะยังไม่มีจริงบนเครื่อง)
- `npm` อาจเตือน `EBADENGINE` เมื่อ Node ต่ำกว่า engine ที่ประกาศ — managed/artefact path ยังรันได้ แต่ provider ที่พึ่ง API ใหม่ (เช่น `sqlite` ซึ่งต้อง `DatabaseSync.limits`) จะถูกปิด; ดูสรุปจริงจาก `rea doctor`
- บน Windows/git-bash ให้เรียกผ่าน `cmd /c "C:\Users\<user>\AppData\Roaming\npm\rea.cmd <cmd>"` — การเรียก binary ตรง ๆ มีโอกาสพังเรื่อง process spawn
- Path ที่มีช่องว่างจะถูกตัดเป็นหลาย argument (`Unexpected positional arguments: ...`) — คัดลอก target ไปไว้ที่ path ปลอดช่องว่างก่อนวิเคราะห์ หรืออ้าง absolute path ด้วย forward slash
- หลังอัปเกรด/ติดตั้ง global package ใหม่ ให้ respawn MCP bridge ก่อนใช้ MCP tools (toggle `mcp_servers.rea.enabled` false → true) ไม่งั้นจะเจอ error module export ไม่ครบจากชุดไฟล์ที่ถูกสลับระหว่างที่ process ยังโหลดของเก่าอยู่
- งานที่ใช้เวลาเกิน ~3 นาที ให้ใช้ CLI แทน MCP (MCP call timeout ~300s) และเขียนผลลงไฟล์ JSON แทนการถือไว้ใน context (evidence ของ assembly กลาง ๆ แตะหลาย MB)

---

## 3. Managed .NET Pipeline (verified end-to-end)

```
rea inspect-managed-artifact <file>                     # identity, CLI header, runtime family, managed arch
rea inspect-managed-members <file> --format json > m.json   # types/fields/methods + IL anchors + call_edges
rea project-managed-application-graph <wrapped.json> --format json > graph.json
```

- **Contract ของ graph:** CLI รับ JSON ที่ห่อ Evidence ไว้เป็น `{"managed_members": <full evidence record>}` (หรือ `managed_artifact` / `managed_native_boundaries`). ส่ง record เปล่า ๆ หรือส่ง path ตรง ๆ จะได้ `unknown_argument: evidence_id`
- `--format json` เป็น global flag ของ CLI ทุกคำสั่ง (`--schema` ดู argument shape, `--filter-output` ตัด field ก่อนพิมพ์)
- Graph คืน `normalized_result.graph` = nodes (`managed-method`, `managed-field`, `managed-type`, `artifact`, `managed-module`) + edges ที่ `relation: "calls"`, พร้อม `summary` (counts) และ `coverage`
- วิธีอ่านให้ได้ insight: สร้าง map `node_id → observations[0].label` แล้ว BFS ตาม `calls` จาก method เป้าหมายลึก 2–3 ชั้น. ชั้น 1 มักเป็น property getter (`get_IsSrcPMCoor`, `get_UseGeoidModel`) ซึ่งจริง ๆ คือ flag/config ที่บอกโหมดการทำงาน; ตัวคณิตศาสตร์จริงมักอยู่คนละ assembly — สังเกตจาก `pinvoke_imports: 0` และชื่อ type ภายนอก (`Matrix.ComputeDetGauss`, `InvertGaussJordan`, `EllipsoidParams`) แล้วค่อยเปิด DLL ตัวนั้นต่อ
- IL anchors (`il_offset`, `opcode`, `operand`) พอสำหรับ reconstruct control flow เมื่อไม่มี decompiler; ใช้ `import-managed-reconstruction` เมื่อมี output จาก decompiler ภายนอก
- Metadata token เป็น build-local — ทุกข้อสรุปต้องอ้างคู่กับ `sha256` และ `mvid` ของ artefact เดียวกันเสมอ
- Evidence identity เปลี่ยนตั้งแต่รุ่น 6.6 (เพิ่ม `analysis_profile`, `relationship_coverage`) — bundle เก่าจะถูกปฏิเสธเป็น integrity mismatch. **เก็บ observation ใหม่ ไม่ใช่พยายาม migrate**

---

## 4. Native Scope (ตัดสินก่อนรับปากผู้ใช้)

- `rea providers` บอกตามจริงว่า provider ไหนพร้อม; ถ้าไม่มี Ghidra/Hopper/IDA คำสั่งกลุ่ม `search_procedures`, `analyze_function`, `procedure_*`, `decompile` จะ fail closed ด้วย `provider_unavailable` พร้อม diagnostics บอกว่า缺อะไร (เช่น `GHIDRA_INSTALL_DIR`, `HOPPER_LAUNCHER_PATH`)
- Ghidra provider บน Windows รับเฉพาะ **PE x86-64** — target x86 (32-bit) ถูกปฏิเสธ `architecture_unsupported` แม้ติดตั้ง Ghidra แล้ว จึงต้องเช็ก architecture จาก `inspect-managed-artifact`/`binary_overview` ก่อนสัญญาว่าจะ decompile ได้
- `extract-artifact` รับเฉพาะ `.7z/.rar/.asar/.bz2/.xz/.zst/.dmg/.pkg`; นามสกุลอื่น (`.zip/.gz/.tar/.apk/.ipa/.deb/.rpm`) ให้แตกด้วย 7z เองก่อน แล้วค่อย `inspect-artifact` บนโฟลเดอร์ที่แตก
- `.asar`: `open_binary` รับไฟล์ archive ได้ แต่ analyse production bundle มักถูกปฏิเสธ `unsafe or conflicting internal path` — แตกก่อนด้วย `npx --yes @electron/asar extract app.asar out_dir` แล้ววิเคราะห์โฟลเดอร์ absolute และตัด `node_modules` ออกเมื่อ bundle ใหญ่จน analyse ไม่จบ

---

## 5. Supply-chain & Provenance

- ต้นทางจริงคือ `github.com/morluto/rea` + npm `rea-agents` (MIT). repo อื่นที่ README เหมือนกันทุกตัวอักษรเป็นสำเนา — ตัดสินจาก `npm view rea-agents repository.url` ไม่ใช่จากชื่อ repo หรือจำนวนดาว
- ทุก operation คืน `evidence_id` + `subject.digest.sha256` + `limitations`; เก็บสามอย่างนี้ไว้เป็นหลักฐานชั้น Stage 1 ของ merea และอ้าง limitation ตรง ๆ ในรายงาน แทนการสรุปเกินข้อมูล
- จับคู่กับ merea: `evidence_id`/sha256 → Stage 1, call graph จาก graph JSON → Stage 2, Stage 5 ต้องออกมาเป็น clean-room rebuild ที่ทำ behaviour เดิมได้ ไม่ใช่โค้ดที่ decompile แล้วแปะ

### Target classes REA cannot see (unpack first)

- **PyInstaller-frozen Python** (e.g. Surveyor Pocket Tools): `inspect-artifact` returns only `root-manifest` and `next_probes: []`. Unpack with `python -m pyinstxtractor_ng <exe>`, then read `main.pyc` with a Python whose minor version matches the archive header (`Pyinstaller version: 2.1+ / Python version: 3.12`). Get the interpreter from `uv python install 3.12`, then `marshal.loads(open(pyc,'rb').read()[16:])` + `dis` to recover class/function names, module names and all string constants (PROJ definitions, API keys, UI strings).
- **Electron/ASAR**: works via `inspect-artifact`, but real-world builds need `--integrity-policy record-and-continue` because unpacked native modules (`node_modules/btime/binding.node` etc.) contradict declared ASAR integrity. Then `analyze-javascript-application` still needs a trimmed tree.
- **Installers** (Inno/NSIS/WiX Burn): REA refuses SFX; unpack with `innoextract` / `7z x` before any inspection.
