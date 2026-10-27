# Next-Gen Audio-Visual Engineering Reference: WebCodecs, Advanced DSP & Cinematic Shaders

คู่มือวิศวกรรมขั้นสูงสำหรับทักษะ `code-video` ยกระดับการผลิต Motion Graphics และ Algorithmic Audio สู่มาตรฐานสตูดิโอ

---

## 1. WebCodecs Zero-IPC Pipeline (เร่งความเร็วการเรนเดอร์ 5-10 เท่า)

### ปัญหาของ DevTools Screenshot IPC
การเรียก `page.locator().screenshot()` ใน Playwright ต้องส่งข้อมูลภาพผ่าน Chrome DevTools Protocol (CDP) ทีละเฟรม ก่อให้เกิด Latency ~30-50ms ต่อเฟรม (900 เฟรมใช้เวลา ~45-60 วินาที)

### สถาปัตยกรรม WebCodecs + MP4-Muxer ในตัวเบราว์เซอร์
- ใช้ `VideoEncoder` API ภายใน Chrome ร่วมกับ `mp4-muxer.js` (Client-side)
- แต่ละเฟรมจะถูกเข้ารหัสแบบ Hardware-accelerated ผ่าน GPU บนหน่วยความจำ VRAM โดยไม่ต้องส่งภาพข้าม IPC
- เมื่อครบกำหนด เฟรมทั้งหมดจะถูกบันทึกเป็น MP4 Blob คืนให้ระบบในเสี้ยววินาที

```javascript
// WebCodecs Zero-Copy Implementation
import { Muxer, ArrayBufferTarget } from 'mp4-muxer';

const target = new ArrayBufferTarget();
const muxer = new Muxer({
  target, fastStart: 'in-memory', firstTimestampBehavior: 'strict',
  video: { codec: 'avc', width: W, height: H }
});

const enc = new VideoEncoder({
  output: (chunk, meta) => muxer.addVideoChunk(chunk, meta),
  error: e => console.error(e)
});

enc.configure({
  codec: 'avc1.64002A', // High@4.2
  width: W, height: H, framerate: FPS, bitrate: 16_000_000,
  latencyMode: 'quality', hardwareAcceleration: 'prefer-hardware'
});

for (let i = 0; i < N; i++) {
  window.renderFrame(i / FPS);
  const ts = Math.round(i * 1e6 / FPS);
  const dur = Math.round((i + 1) * 1e6 / FPS) - ts;
  const frame = new VideoFrame(outCanvas, { timestamp: ts, duration: dur });
  enc.encode(frame, { keyFrame: i % FPS === 0 });
  frame.close(); // ป้องกัน GPU Memory Leak
  while (enc.encodeQueueSize > 4) {
    await new Promise(r => enc.addEventListener('dequeue', r, { once: true }));
  }
}
await enc.flush();
muxer.finalize();
```

---

## 2. Advanced DSP Audio Synthesis (ระดับ Professional VST)

### ก. 7-Voice Stereo Supersaw (Roland JP-8000 Model with PolyBLEP)
รวมคลื่น Sawtooth 7 ตัวที่มีการ Detune ตามสมการ Polynomial พร้อมตัด Aliasing ด้วย PolyBLEP:

```python
OFFS = np.array([-0.11002313, -0.06288439, -0.01952356, 0.0,
                  0.01991221,  0.06216538,  0.10745242])
_DC = [10028.73, -50818.86, 111363.48, -138150.68, 106649.67, -53046.96,
       17019.95, -3425.08, 404.27, -24.19, 0.67, 0.003]
detune_curve = lambda x: np.polyval(_DC, x)

def polyblep(t, dt):
    x = t / dt
    y = np.where(t < dt, x + x - x * x - 1.0, 0.0)
    x = (t - 1.0) / dt
    return np.where(t > 1.0 - dt, x * x + x + x + 1.0, y)
```

### ข. Schroeder-Moorer Reverb (Block-Vectorized via SciPy)
ประมวลผลเป็นบล็อกขนาดความยาว $D$ แทนการวนลูปทีละตัวอย่าง ช่วยลดจำนวนลูปจาก 660,000 เหลือเพียง ~600 รอบ:

```python
from scipy.signal import lfilter

def comb(x, D, g, d=0.25):
    xp, n = _pad(x, D); y = np.zeros(n)
    prev = np.zeros(D); zi = np.zeros(1)
    for k in range(0, n, D):
        blk = xp[k:k+D] + g * prev
        y[k:k+D] = blk
        prev, zi = lfilter([1 - d], [1, -d], blk, zi=zi)
    return y[:len(x)]
```

### ค. Moog 24dB/octave Ladder Filter (Hammerstein Saturation)
ใช้แบบจำลอง Linear 4-pole อัปเดต Cutoff ทีละบล็อก (16-32 ตัวอย่าง) พร้อม $\tanh$ Saturation หัวท้าย:
$$\text{Output} = \tanh\left(1.5 \cdot \text{LadderLinear}(\tanh(\text{Drive} \cdot x), f_c, k)\right)$$

---

## 3. Cinematic Visuals: ACES Tone Mapping & Dithering

### ก. Hill/ACES Fit (RRT+ODT) พร้อม Chroma Re-injection
แก้ปัญหาแสงนีออนสว่างจนกลายเป็นสีขาวล้วน โดยรักษาสีสันเดิมของนีออนไว้ในส่วน Shoulder:

```glsl
const mat3 ACES_IN  = mat3(0.59719, 0.07600, 0.02840,
                           0.35458, 0.90834, 0.13383,
                           0.04823, 0.01566, 0.83777);
const mat3 ACES_OUT = mat3( 1.60475,-0.10208,-0.00327,
                           -0.53108, 1.10813,-0.07276,
                           -0.07367,-0.00605, 1.07602);
vec3 rrt_odt(vec3 v){
  vec3 a = v*(v + 0.0245786) - 0.000090537;
  vec3 b = v*(0.983729*v + 0.4329510) + 0.238081;
  return a/b;
}
vec3 tonemap(vec3 c, float exposure, float sat){
  c *= exposure / 0.6;
  c = ACES_OUT * rrt_odt(ACES_IN * c);
  float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
  c = mix(vec3(l), c, sat); // sat ~ 1.25 คืนค่าความสดของสีนีออน
  return clamp(c, 0.0, 1.0);
}
// Triangular Dithering เพื่อป้องกันอาการ Color Banding ใน H.264
vec3 encode(vec3 c, vec2 fragCoord, float frame){
  c = pow(c, vec3(1.0/2.2));
  float n = fract(sin(dot(fragCoord, vec2(12.9898,78.233)) + frame*1.618)*43758.5453);
  float m = fract(sin(dot(fragCoord, vec2(39.3468,11.135)) + frame*2.718)*24634.6345);
  return c + (n + m - 1.0) / 255.0;
}
```

### ข. 4-Tap Tetrahedron Normal Calculation
ประหยัดการคำนวณ `map(p)` ได้ 33% เมื่อเทียบกับ 6-tap central difference:

```glsl
vec3 calcNormal(vec3 p) {
  const vec2 e = vec2(1.0, -1.0) * 0.5773 * 0.0005;
  return normalize(e.xyy * map(p + e.xyy) + e.yyx * map(p + e.yyx) +
                   e.yxy * map(p + e.yxy) + e.xxx * map(p + e.xxx));
}
```

### ค. Step-Length Weighted Volumetric Glow
การสะสมแสงนีออนในอุโมงค์โดยไม่ขึ้นกับจำนวนก้าว Raymarch:
```glsl
float w = exp(-9.0 * g_emit) * min(d, 0.5);
glow += neonPalette(p, uTime) * w * (0.12 + 0.6 * uKickEnv) * exp(-0.04 * t);
```

---

## 4. Audio-Visual Contract: Compile-Once Signals & Splines

1. **Author in Music Ticks (PPQ 960):** เขียนจังหวะในหน่วย Tick และ Tempo Map ห้ามเขียนวินาทีลอยๆ
2. **Compile to `compiled.json`:** คำนวณ Exact Rational Seconds, Sample Index (`round(sec * sr)`), และ Fractional Frame
3. **Pre-Sampled Signal Tables:** สัญญาณ Envelope และ Sidechain Ducking ถูกคำนวณครั้งเดียวใน Python แล้วแปลงเป็น Base64 Float32 ส่งให้ WebGL Shader เป็น Uniform Array ทำให้ภาพและเสียงไม่มีวันขัดแย้งกัน
4. **Hermite / Catmull-Rom Camera Splines:** มุมกล้องเคลื่อนที่อย่างราบรื่นแบบ $C^1$ Continuity แม้ระยะห่างของ Keyframe จะไม่เท่ากัน
