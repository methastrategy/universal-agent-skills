# Local Kev Runner Guide (TypeSafe System 1 Decision Models)

คู่มือการรันและใช้งานโมเดลตระกูล **Kev** (`jaredpalmer/kev`) แบบ Local Offline 100% เพื่อทำหน้าที่เป็น System 1 Co-Processor ประมวลผลการตัดสินใจระดับอะตอม (`choice`, `score`, `noul`) ด้วยความเร็วสูงและแม่นยำตามหลัก Brier score calibration

---

## 1. Kev Model Weights Overview

| Model | Architecture / Base | VRAM / RAM | Recommended Hardware | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **`jaredpalmer/kev-0.8b`** | Qwen2.5-0.5B base | ~2 GB | Standard Laptop / CPU / iGPU | Instant triaging, command routing, simple Boolean gates |
| **`jaredpalmer/kev-4b`** | Qwen2.5-3B base | ~6-8 GB | Apple Silicon (M1-M4) / RTX 3060+ | Complex architectural scoring, code triage, high-accuracy gating |
| **`jaredpalmer/kev-27b`** | Qwen2.5-14B/32B base | ~24-32 GB | RTX 4090 / Multi-GPU / Workstation | Enterprise-grade calibration, mission-critical execution gating |

---

## 2. Local Installation & Serving (Port 8009)

Kev ให้บริการ API สเปกเดียวกับ TypeSafe Cloud แต่ทำงานบน Local Server ผ่าน `uv`:

### Step 1: Install uv and Kev CLI
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone or install kev with serve dependencies
uv pip install "kev[serve]"
```

### Step 2: Start Local Inference Server
```bash
# macOS (Apple Silicon via MLX / Metal):
uv run --extra serve python -m kev.serve --model jaredpalmer/kev-4b --device mps --port 8009

# Linux / Windows (NVIDIA CUDA):
uv run --extra serve python -m kev.serve --model jaredpalmer/kev-4b --device cuda --port 8009

# CPU Fallback (Laptop/Lightweight with Kev-0.8B):
uv run --extra serve python -m kev.serve --model jaredpalmer/kev-0.8b --device cpu --port 8009
```
*เซิร์ฟเวอร์จะเปิด listening ที่ `http://localhost:8009` พร้อม Health check endpoint ที่ `GET /health`*

---

## 3. Python Client Integration

ตัวอย่างการเรียกใช้ Local Kev จาก Python script:

```python
import os
import requests

KEV_ENDPOINT = os.getenv("KEV_ENDPOINT", "http://localhost:8009/v1")

class KevLocalClient:
    def __init__(self, endpoint: str = KEV_ENDPOINT):
        self.endpoint = endpoint

    def noul(self, proposition: str, context: str) -> float:
        """Evaluate a True/False statement with calibrated probability P in [0.0, 1.0]"""
        res = requests.post(
            f"{self.endpoint}/noul",
            json={"proposition": proposition, "context": context, "temperature": 0.0},
            timeout=2.0
        )
        res.raise_for_status()
        return res.json().get("probability", 0.0)

    def choice(self, question: str, options: list[str], context: str) -> str:
        """Select exactly one option from discrete bounded choices"""
        res = requests.post(
            f"{self.endpoint}/choice",
            json={"question": question, "options": options, "context": context},
            timeout=2.0
        )
        res.raise_for_status()
        return res.json().get("selected_option", "")

    def score(self, rubric: str, value_range: tuple[int, int], context: str) -> int:
        """Return an integer score based on rubric"""
        res = requests.post(
            f"{self.endpoint}/score",
            json={"rubric": rubric, "min": value_range[0], "max": value_range[1], "context": context},
            timeout=2.0
        )
        res.raise_for_status()
        return res.json().get("score", 0)

# Example Usage:
if __name__ == "__main__":
    client = KevLocalClient()
    # Gating check
    p_safe = client.noul(
        proposition="The requested shell command will NOT cause data loss or system mutation.",
        context="Command: git clean -fdx"
    )
    print(f"Safety probability: {p_safe:.2f}")
    if p_safe < 0.85:
        print("Blocked by Kev System 1 Gate!")
```

---

## 4. Antigravity System 1 Co-Processor Pattern

เมื่อเปิด Kev บนพอร์ต 8009:
1. Main agent หรือ Subagent สามารถ query Local Kev endpoint เพื่อทำ **Atomic Pre-Gating** ก่อนสั่งคำสั่ง high blast radius
2. หาก Kev ไม่ได้รันอยู่ ให้ fallback อัตโนมัติไปยัง **In-Context System 1 Triaging** (คำนวณใน CoT ตามกฎใน `GEMINI.md` และ `/jev`) โดยไม่ทำให้การทำงานหยุดชะงัก
