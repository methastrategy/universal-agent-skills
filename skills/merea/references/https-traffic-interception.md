# Interactive HTTPS Proxy & Protocol Traffic Dissection

> [!NOTE]
> สถาปัตยกรรมระดับสูงสำหรับการดักจับ ตรวจสอบ และดัดแปลงทราฟฟิกเครือข่ายความเร็วสูง (HTTPS, HTTP/2, WebSocket, และ Binary Streams) เพื่อการวิเคราะห์คิดย้อนรอย (Reverse Engineering) ถอดแบบองค์ความรู้จาก **mitmproxy** และ **Wireshark**

---

## 1. สถาปัตยกรรม Man-In-The-Middle (MITM) SSL/TLS Decryption

การเข้ารหัสแบบ TLS ถูกออกแบบมาเพื่อป้องกัน Eavesdropping หากต้องการดักอ่านและแก้ไข Request/Response ในระดับ Application Layer ระบบ Proxy จะต้องสวมบทบาทเป็น Dynamic CA:

```
Client (App / Browser) ──[TLS Session A]──► Mitmproxy (Local CA) ──[TLS Session B]──► Target Server
                                            ├── Decrypt Cleartext
                                            ├── Run Python Addon
                                            └── Re-encrypt for Client
```

1. **Client Handshake:** ไคลเอนต์พยายามต่อ TLS กับเซิร์ฟเวอร์ปลายทาง โดยมี Mitmproxy ทำหน้าที่เป็น Transparent/Explicit Proxy
2. **On-the-Fly Cert Generation:** Mitmproxy ออก Certificate ปลอมสำหรับโดเมนนั้นๆ โดยเซ็นกำกับด้วย Local Root CA ของตัวเอง (ซึ่งถูกติดตั้งใน OS Trust Store)
3. **Dual Session Decryption:** ข้อมูลฝั่งขาเข้าถูกถอดรหัสเป็น Cleartext ให้อ่าน/แก้ได้แบบเรียลไทม์ ก่อนจะถูกส่งต่อไปยังเซิร์ฟเวอร์จริงผ่าน Session ปกติ

---

## 2. In-Flight Traffic Mutation ด้วย Python Addon (mitmproxy)

การเขียน Python Script เพื่อดักฟังและปรับแต่ง Payload กลางอากาศ:

```python
# addons/traffic_interceptor.py
from mitmproxy import http
import json

class APITrafficDissector:
    def request(self, flow: http.HTTPFlow) -> None:
        # 1. กรองเฉพาะโดเมนและ Path ที่สนใจ
        if "api.trading.internal" in flow.request.pretty_host:
            print(f"[>] Intercepted Request: {flow.request.method} {flow.request.path}")
            
            # 2. ปรับแต่ง Header หรือแทรก Token อัตโนมัติ
            flow.request.headers["X-Custom-Audit-Hook"] = "Active"

    def response(self, flow: http.HTTPFlow) -> None:
        if "api.trading.internal" in flow.request.pretty_host:
            # 3. ดักจับและดัดแปลง Response Payload ทันที
            if flow.response.headers.get("content-type") == "application/json":
                try:
                    data = json.loads(flow.response.get_text())
                    
                    # ปลดล็อกฟีเจอร์จำลอง หรือ Inject สัญญาณทดสอบ
                    if "user_tier" in data:
                        data["user_tier"] = "institutional_pro"
                        flow.response.set_text(json.dumps(data))
                        print("[+] Injected mock institutional tier into response!")
                except Exception as e:
                    pass

addons = [APITrafficDissector()]
```

---

## 3. WebSocket & Binary Frame Dissection

การดักจับข้อความ WebSocket ที่ส่งข้อมูลแบบ Binary (เช่น Protobuf หรือ MessagePack) แบบสองทิศทาง:

```python
# addons/websocket_dissector.py
from mitmproxy import websocket

def websocket_message(flow: websocket.WebSocketFlow):
    message = flow.websocket.messages[-1]
    direction = "Client -> Server" if message.from_client else "Server -> Client"
    
    print(f"[*] WS Frame ({direction}) | Length: {len(message.content)} bytes")
    
    # หากเป็น Binary ให้พิมพ์ Hexdump ย่อ
    if message.type == 2:  # Binary Frame
        hex_preview = message.content[:32].hex()
        print(f"    Hex: {hex_preview}...")
```

---

## 4. Replay Machine & Deterministic Mocking Protocol

1. **Traffic Recording (`mitmdump -w dump.flow`):** บันทึกการสื่อสารทั้งหมดลงไฟล์ Flow
2. **Replay Execution (`mitmproxy --server-replay dump.flow`):** ให้ Proxy จำลองตัวเองเป็นเซิร์ฟเวอร์เสมือน โดยตอบสนองด้วยข้อมูลเดิมที่เคยบันทึกไว้ ช่วยให้สามารถดีบั๊ก Client ซ้ำๆ ได้โดยไม่ต้องยิง API จริง
3. **Latency Emulation:** แทรกคำสั่งจำลอง Network Jitter หรือ Slow 3G เพื่อทดสอบ Timeouts ในระบบเทรดหรือแอปพลิเคชัน
