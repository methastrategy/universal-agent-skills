# Zero-Dependency Native Patterns & 1-Liners
> คลังตัวอย่างโค้ดมาตรฐานระดับ Standard Library ไร้ Dependency ภายนอก (สอดคล้องกับ Ponytail Step 2-3 และ 30-Seconds-of-Code) เพื่อตัด Bloat และป้องกันการติดตั้ง Third-party library โดยไม่จำเป็น

---

## ⚡ 1. Modern JavaScript / TypeScript Native Patterns

### 1.1 Deep Cloning (แทนที่ `lodash.clonedeep`)
```typescript
// Native Web API / Node 17+
const deepCopy = structuredClone(originalObject);
```

### 1.2 Cryptographic UUID (แทนที่แพ็กเกจ `uuid`)
```typescript
// Native Web Crypto API / Node 19+
const id = crypto.randomUUID();
```

### 1.3 Collection Grouping (แทนที่ `lodash.groupBy`)
```typescript
// ES2024 Object.groupBy
const grouped = Object.groupBy(items, item => item.category);
```

### 1.4 Array Chunking (แบ่งก้อนอาร์เรย์เป็นชุดย่อย)
```typescript
// Native 1-Liner Chunk
const chunk = <T>(arr: T[], size: number): T[][] =>
  Array.from({ length: Math.ceil(arr.length / size) }, (_, i) =>
    arr.slice(i * size, i * size + size)
  );
```

### 1.5 Debounce & Throttle (แทนที่ `lodash.debounce`)
```typescript
// Native Clean Debounce
function debounce<T extends (...args: any[]) => any>(fn: T, delayMs: number) {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delayMs);
  };
}

// Native Clean Throttle
function throttle<T extends (...args: any[]) => any>(fn: T, limitMs: number) {
  let inThrottle = false;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limitMs);
    }
  };
}
```

### 1.6 URL Query Serialization & Parsing (แทนที่แพ็กเกจ `qs` หรือ `query-string`)
```typescript
// Parsing query string
const params = Object.fromEntries(new URLSearchParams(window.location.search));

// Serializing to query string
const queryString = new URLSearchParams(recordObject as Record<string, string>).toString();
```

### 1.7 Async Sleep & Polling
```typescript
// Native Promise Delay
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
```

### 1.8 Object Pick & Omit
```typescript
// Native Pick
const pick = <T extends object, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> =>
  Object.fromEntries(keys.filter(k => k in obj).map(k => [k, obj[k]])) as Pick<T, K>;

// Native Omit
const omit = <T extends object, K extends keyof T>(obj: T, keys: K[]): Omit<T, K> =>
  Object.fromEntries(Object.entries(obj).filter(([k]) => !keys.includes(k as K))) as Omit<T, K>;
```

---

## 🐍 2. Modern Python 3.12+ Native Patterns

### 2.1 Batched Chunking (Python 3.12+)
```python
from itertools import batched

# Chunk list into batches of size N
for chunk in batched(data_list, n=100):
    process_batch(chunk)
```

### 2.2 In-Memory Caching (แทนที่การเขียน Cache เอง)
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_compute(param: str) -> dict:
    return fetch_data(param)
```

### 2.3 Type-Safe Structured Records
```python
from dataclasses import dataclass, asdict

@dataclass(slots=True, frozen=True)
class TradeExecution:
    ticket: int
    symbol: str
    volume: float
    price: float
```

---

## 🚫 3. Escalation Boundary: เมื่อไหร่ที่อนุญาตให้ติดตั้ง Library เพิ่ม?

อนุญาตให้ติดตั้ง Third-party library เพิ่มได้เฉพาะกรณี:
1. **Security & Cryptography**: รหัสผ่าน แฮช Argon2 หรือ JWT verification (ห้ามเขียน crypto เอง)
2. **Complex Timezone Math**: การคำนวณวันหยุดทำการตลาดการเงินข้าม Daylight Saving Time ที่ต้องการฐานข้อมูล IANA
3. **Hardware / Protocol Drivers**: เช่น MT5 Native C-API wrapper หรือ Serial port scanner
