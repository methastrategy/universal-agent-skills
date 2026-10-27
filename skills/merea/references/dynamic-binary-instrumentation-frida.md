# Dynamic Binary Instrumentation & Runtime Hooking Engine

> [!NOTE]
> สถาปัตยกรรมระดับสูงสำหรับการแกะรอยและดักจับพฤติกรรมของไบนารีขณะทำงานจริง (Dynamic Binary Instrumentation - DBI) โดยไม่ต้องแตกไฟล์หรือ Patch โค้ดไบนารี ถอดแบบองค์ความรู้จาก **Frida**, **Mandiant Capa**, และ **Radare2**

---

## 1. ปรัชญา Dynamic Instrumentation vs. Static Disassembly

การ Decompile แบบ Static มักติดอุปสรรคเรื่อง Code Obfuscation, Dynamic Imports, และ Packed Code การใช้ Dynamic Binary Instrumentation (DBI) ช่วยให้เราสามารถ:
- **Inject JavaScript Engine:** ฝัง QuickJS/V8 เข้าไปรันใน Address Space เดียวกับโพรเซสเป้าหมาย
- **Non-Destructive Hooking:** แทนที่ Instruction หัวฟังก์ชันด้วย Trampoline Jump ชั่วคราวเพื่อดักฟังพารามิเตอร์แล้วคืนสภาพเดิม
- **Clear-Text Interception:** ดักอ่านข้อมูลในหน่วยความจำก่อนที่จะถูกเข้ารหัส (เช่น ก่อนเรียก `SSL_write` หรือ `CryptEncrypt`)

```
Native Process Memory Space
┌────────────────────────────────────────────────────────┐
│  Target Native Function (e.g. WSASend / HttpSendReq)   │
│  ├── [Trampoline Hook] ──► Frida JavaScript Engine     │
│  │                          ├── onEnter(args)          │
│  │                          │    └─ Read memory/buf    │
│  │                          └── onLeave(retval)        │
│  │                               └─ Mutate / Trace     │
│  └── Original Function Body (Executes safely)          │
└────────────────────────────────────────────────────────┘
```

---

## 2. Frida JavaScript Hooking Architecture

ตัวอย่างการเขียน Frida Script เพื่อ Hook เนทีฟฟังก์ชันของ Windows (WinAPI) หรือ POSIX:

```javascript
// frida_hook.js

// 1. ดักจับการส่งข้อมูลผ่านเครือข่ายของ Windows (ws2_32.dll -> send)
const pSend = Module.findExportByName('ws2_32.dll', 'send');

if (pSend) {
  Interceptor.attach(pSend, {
    onEnter: function (args) {
      const socketFd = args[0].toInt32();
      const pBuf = args[1];
      const len = args[2].toInt32();

      console.log(`\n[+] send(socket=${socketFd}, len=${len})`);
      
      // อ่านข้อมูลดิบใน Buffer
      if (len > 0) {
        console.log(hexdump(pBuf, {
          offset: 0,
          length: Math.min(len, 64),
          header: true,
          ansi: true
        }));
      }

      // ตรวจสอบเส้นทาง Call Stack ย้อนกลับหาต้นตอฟังก์ชันที่เรียก
      console.log('Call Stack:\n' +
        Thread.backtrace(this.context, Backtracer.ACCURATE)
          .map(DebugSymbol.fromAddress).join('\n')
      );
    },
    onLeave: function (retval) {
      // ตรวจสอบผลลัพธ์ของฟังก์ชัน (จำนวนไบต์ที่ส่งสำเร็จ)
      // console.log(`[+] Returned: ${retval.toInt32()}`);
    }
  });
}
```

---

## 3. Dynamic Memory Scanning & Signature Hunting

การค้นหา Pattern หรือ String ที่ถูกถอดรหัสออกมาอยู่ใน RAM แบบ Real-Time:

```javascript
// memory_scanner.js
function scanForPattern(pattern) {
  // สแกนทุก Memory Region ที่มีสิทธิ์อ่าน (r--)
  Process.enumerateRanges('r--').forEach(function (range) {
    Memory.scan(range.base, range.size, pattern, {
      onMatch: function (address, size) {
        console.log(`[!] Found signature at: ${address}`);
        console.log(hexdump(address, { length: 32 }));
      },
      onError: function (reason) {
        // ข้ามหน้าที่ติด Bad memory page
      },
      onComplete: function () {
        // สแกนครบช่วง
      }
    });
  });
}

// ค้นหา Hex Signature (เช่น '48 8b ?? ?? ?? 48 85 c0')
// scanForPattern('48 8b ?? ?? ?? 48 85 c0');
```

---

## 4. Behavioral Capability Analysis (Capa Mapping)

การจับคู่พฤติกรรมขณะรัน (Runtime Behaviors) เข้ากับหมวดหมู่ตามมาตรฐาน MITRE ATT&CK:

| พฤติกรรมที่ตรวจจับ (Trait) | APIs / Syscalls ที่ใช้ตรวจสอบ | ความหมายทางความปลอดภัย (Capability) |
| :--- | :--- | :--- |
| **Anti-Debugging** | `IsDebuggerPresent`, `CheckRemoteDebuggerPresent`, `NtQueryInformationProcess` | ป้องกันการดีบั๊ก / หลบเลี่ยง Sandbox |
| **Process Injection** | `VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread` | ฝังโค้ดแปลกปลอมลงใน Process อื่น |
| **Persistence** | `RegSetValueExA` (CurrentVersion\Run), Startup folders | ฝังตัวถาวรเพื่อรันตอนเปิดเครื่องใหม่ |
| **Credential Dumping** | Access Token Manipulation, `OpenProcess` บน `lsass.exe` | ลักลอบดึงรหัสผ่านหรือ Token บัญชีผู้ใช้ |
