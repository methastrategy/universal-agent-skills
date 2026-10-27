# Unattended MT5 Tester Batch (invisible, many EAs × many windows)

ใช้เมื่อต้องสร้าง report จริงให้ EA หลายตัว (เช่น เติมหลักฐาน 12M/2Y ให้ทั้ง catalog) โดยผู้ใช้ยังทำงานอยู่บนเครื่อง
และ **ไม่ต้องการให้หน้าต่าง MetaTrader เด้งขึ้นมาบังหน้าจอ**

runner ที่ใช้ได้จริงใน workspace นี้: `scripts/research_lab/run_provenance_backtests.py` (โหมด `--list`, `--only N`, `--exclude a,b`)

---

## 1. สร้างรายการงานจาก manifest ไม่ใช่ list มือ

1. เลือก EA ตามเงื่อนไข (เช่น `tier == CHAMPION`) แล้วสร้าง 2 งานต่อตัว: `12M` และ `2Y`
2. **ตัด EA ที่ `ex5_rel` ไม่ลงท้ายด้วย `.ex5`** — portfolio/ensemble wrapper หลายตัวชี้ไปที่ `.json` / `.csv` / `.png`
   เพราะเป็นตะกร้าสังเคราะห์ที่ประกอบจาก EA สมาชิก ไม่มีไบนารีให้รัน ถ้าฝืนรันไบนารีของสมาชิกแล้วติดป้ายชื่อ wrapper
   จะกลายเป็นผลเดียวถูกนับเป็นสอง EA
3. **Timeframe ที่ใช้รัน = token TF ตัวแรกในสตริง** (`"M15 (Execution) / H1 (Macro)"` → 15) เพราะตัวแรกคือ execution TF
   ถ้า parse แบบหา H ก่อนจะได้ 60 แล้วได้ผลของหน้าต่างผิด timeframe
4. **Preset:** เอา `is_recommended` ที่ไม่มีคำว่า `Cent` ก่อน; ถ้ามีแต่ preset cent ให้รันได้แต่ต้องติดป้ายว่า
   PnL ไม่เทียบเท่าบัญชี USD (DD% ยังเทียบได้) อย่าเอาไปปนคอลัมน์เดียวกับ USD30
5. ตรวจก่อนว่าทุก preset มีไฟล์จริงใน `presets/` และทุก `.ex5` มีอยู่ใต้ `MQL5\Experts\`

## 2. INI ที่ใช้จริง

```ini
[Tester]
Expert=EA_METHA\MeAnti_M5_Adaptive_Pyramid.ex5   ; relative ใต้ MQL5\Experts
ExpertParameters=MeAnti_M5_Adaptive_Pyramid_USD30_Standard.set   ; ไฟล์ต้องอยู่ใน MQL5\Profiles\Tester\
Symbol=XAUUSDm
Period=5
FromDate=2025.04.14
ToDate=2026.04.14
Model=4                 ; 4 = real ticks (ตรวจ History Quality ใน report ว่า 100% real ticks)
Optimization=0
FromBar=0
ToBar=0
ForwardMode=0
UseDate=1               ; ขาดบรรทัดนี้ ช่วงวันที่อาจไม่ถูกใช้
Deposit=30.00
Currency=USD
Leverage=100
Report=prov_0           ; ชื่อเพียว ๆ -> เขียน prov_0.htm ใต้ data dir (absolute path = ไม่มีไฟล์)
ShutdownTerminal=1      ; จบแล้วปิด terminal เอง ไม่ต้อง kill ใคร
```

ลบ `prov_N.htm` ที่ค้างจากรอบก่อนก่อนเริ่มทุกรอบ ไม่งั้นรอบที่ล้มจะถูกอ่านว่า "สำเร็จ" จากไฟล์เก่า

ก่อนยิงทั้งชุด รัน `--list` และตรวจ job list (EA, preset, TF, window) รอบเดียว — ถูกกว่ามาเจอ TF ผิดหรือ preset
หายกลางชุด 22 งาน (~11 นาที)

## 3. ซ่อนหน้าต่าง (และไม่แตะ terminal ของผู้ใช้)

```python
import ctypes, ctypes.wintypes as wt, subprocess, threading

SW_HIDE = 0
TARGETS = {"terminal64.exe", "metatester64.exe"}

def _img(pid):
    k = ctypes.windll.kernel32
    h = k.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024); n = wt.DWORD(1024)
        return k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)) and buf.value.split("\\")[-1].lower()
    finally:
        k.CloseHandle(h)

def hide_pass():
    u = ctypes.windll.user32
    CB = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if u.IsWindowVisible(hwnd):
            pid = wt.DWORD(); u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value and _img(pid.value) in TARGETS:
                u.ShowWindow(hwnd, SW_HIDE)
        return True
    u.EnumWindows(CB(cb), 0)

def hider(stop):
    while not stop.is_set():
        try: hide_pass()
        except Exception: pass
        stop.wait(0.2)

stop = threading.Event(); threading.Thread(target=hider, args=(stop,), daemon=True).start()
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
si.wShowWindow = SW_HIDE
proc = subprocess.Popen([TERMINAL, f"/config:{ini}"], startupinfo=si,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
proc.wait(timeout=timeout_s)
stop.set()
```

- `SW_HIDE` อย่างเดียวไม่พอ — MT5 สร้างหน้าต่างเองหลัง startup จึงต้องมี thread วน `ShowWindow(h, SW_HIDE)` จนจบงาน
- **ก่อนเริ่มทั้งชุด:** ถ้า `Get-Process terminal64,metatester64` คืนค่ามากกว่า 0 ให้หยุดทันทีและแจ้งผู้ใช้ ห้ามฆ่า
  เพราะอาจเป็น terminal ที่เขากำลังเทรดอยู่ — `ShutdownTerminal=1` จัดการปิดเฉพาะ instance ที่เราสั่งเอง
- timeout ต่อรอบ: วัดจริงบน XAUUSDm real ticks ที่ cache ครบ — 12M 16–31s, 2Y 21–47s (เฉลี่ย ~30s/งาน; 22 งาน = 658s)
  เพดาน 2400/5400s มีไว้กันค้างเท่านั้น อย่าเอาไปใช้เป็นเวลาที่คาดหวัง
- log เป็น JSON บรรทัดละ event (`start` / `done` / `summary`) เพื่อให้อ่านความคืบหน้าของ background job ได้โดยไม่ต้องรอจบ

## 4. ตั้งชื่อและเก็บ report

- ชื่อไฟล์ต้องเป็น `<ea_id>_12M02_Annual_Cycle_2.html` / `<ea_id>_2Y.html` เพื่อให้ provenance matcher จับคู่ด้วย **id** ได้
  (การ match ด้วย basename ของ `.mq5` ใช้ไม่ได้เมื่อหลาย EA ใช้ไบนารีร่วมกัน — ดู `ea-dashboard-verification` → `references/provenance-audit.md` §3)
- ย้ายไฟล์จาก data dir เข้า `reports/<stem>_benchmark/` แล้ว commit เข้า repo ที่ track `reports/` — flag `verified` ที่ชี้ไปยังไฟล์
  ที่ไม่ได้ commit จะขาดหลักฐานทันทีที่ย้ายเครื่อง

## 5. อ่านผลให้ถูก

| อาการใน report | ความหมาย |
|---|---|
| `History Quality: 100% real ticks`, `Ticks` หลักสิบล้าน | ข้อมูลจริงครบ ใช้ได้ |
| `Bars:` น้อยกว่าที่หน้าต่างควรมีมาก + `DD ≈ 100%` | บัญชีถูกล้าง tester หยุดเอง ผลครอบคลุมแค่ช่วงแรก |
| `Total Trades: 0` | EA เงียบในหน้าต่างนั้น — เป็นผลจริง ไม่ใช่ parse พลาด |
| `Equity Drawdown Maximal: 30.64 (41.32%)` | ตัวเลขแรกคือเงิน ตัวในวงเล็บคือ % ที่ต้องเก็บ |

### 5.1 ตรวจว่า preset มีผลจริง

เปิด section `Inputs:` ใน report เทียบกับ `.set` ที่ส่งไป — MT5 **เมิน input ที่ไม่รู้จักอย่างเงียบ** ไม่ error
ถ้าค่าใน report เป็น default ทั้งหมด แปลว่า preset ไม่ถูกใช้ และที่ได้คือ EA รันด้วยค่าดิบ

- สอง EA ที่ใช้ไบนารีเดียวกันแล้วได้ผล **เหมือนกันทุกหลัก** (trades เท่ากัน, DD เท่ากันถึงทศนิยมสองตำแหน่ง)
  = preset ไม่ได้เปลี่ยนพฤติกรรม หรือ EA นั้นไม่ implement กลยุทธ์ตามชื่อ — นับเป็นหลักฐานเดียว ไม่ใช่สอง
- `.set` ที่ decode ด้วย encoding ผิดจะกลายเป็นตัวอักษรขยะ (`⼯䴠䅥...`): ลอง `utf-16` ก่อน `utf-8`/`cp1252`;
  ไฟล์ที่อ่านแล้วไม่เป็นบรรทัด `Key=Value` คือ preset ที่ใช้ไม่ได้ — อย่าส่งต่อให้ MT5 แล้วสรุปว่า EA พัง
