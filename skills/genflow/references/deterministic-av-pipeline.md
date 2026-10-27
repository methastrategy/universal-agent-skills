# Deterministic Audio-Visual Pipeline & Mathematical Reference

เอกสารอ้างอิงทางเทคนิคสำหรับทักษะ `code-video` รวบรวมสูตรคณิตศาสตร์สำหรับการสังเคราะห์เสียง (DSP) และการเขียน Shader เรนเดอร์ภาพ 3 มิติ

---

## 1. คณิตศาสตร์การซิงก์จังหวะ (Audio-Visual Phase Alignment)

เพื่อให้ภาพและเสียงตรงกันระดับเฟรม ต้องแปลงหน่วยเวลา $t$ (วินาที) ให้เป็นดัชนีของแต่ละสื่อ:

$$\text{Sample Index } n = \lfloor t \cdot f_s \rfloor \quad (f_s = 44,100\text{ Hz})$$

$$\text{Frame Index } k = \lfloor t \cdot \text{FPS} \rfloor \quad (\text{FPS} = 60)$$

### Beat Phase Calculation (BPM Grid)
ความยาวของ 1 บีต (วินาที):
$$T_{\text{beat}} = \frac{60}{\text{BPM}}$$

เฟสของจังหวะ ณ เวลา $t$ สำหรับใช้คุมแอนิเมชันให้เต้นตามบีต ($\phi \in [0.0, 1.0)$):
$$\phi(t) = \frac{t \pmod{T_{\text{beat}}}}{T_{\text{beat}}}$$

---

## 2. สูตรคณิตศาสตร์การสังเคราะห์เสียง (DSP Sound Synthesis)

### ก. รูปคลื่นพื้นฐาน (Waveforms at frequency $f$)
- **Sine Wave:**
  $$y(t) = \sin(2\pi f t)$$
- **Sawtooth Wave (คม ใส มี Harmonic ครบ):**
  $$y(t) = 2 \left( f t - \lfloor f t + 0.5 \rfloor \right)$$
- **Square Wave (เสียงสังเคราะห์แบบ 8-bit/Synth):**
  $$y(t) = \text{sgn}\left(\sin(2\pi f t)\right)$$
- **White Noise (สำหรับ Snare และ Hi-hat):**
  $$y(t) \sim \mathcal{U}(-1.0, 1.0)$$

### ข. กลอง Kick Drum (Exponential Pitch Drop)
เสียง Kick ไม่ใช่คลื่นความถี่คงที่ แต่เป็นการทิ้งดิ่งของความถี่จากสูงลงต่ำอย่างรวดเร็ว:
$$f(t) = f_{\text{start}} \cdot e^{-\alpha t} + f_{\text{end}}$$
- ตัวอย่าง: $f_{\text{start}} = 160\text{ Hz}, f_{\text{end}} = 45\text{ Hz}, \alpha = 25$
- เฟสสะสม: $\theta(t) = 2\pi \int_0^t f(\tau) d\tau$
- แอมพลิจูด Envelope: $A(t) = e^{-\beta t}$ ($\beta = 10 \sim 15$)

### ค. ADSR Envelope (Attack, Decay, Sustain, Release)
ใช้ควบคุมความดังของเครื่องดนตรีสังเคราะห์:
```text
Amplitude
   ^
1.0|      /\
   |     /  \
S  |    /    \________
   |   /              \
0.0+--+---+---+-------+---> Time
      A   D      S       R
```

---

## 3. Shader เรนเดอร์ 3D แบบ Procedural (GLSL Raymarching SDF)

การใช้ Signed Distance Function (SDF) ใน Fragment Shader ช่วยสร้างฉากสามมิติและอุโมงค์อนันต์ได้โดยไม่ต้องโหลด 3D Model:

### ฟังก์ชันระยะทางพื้นฐาน (Distance Functions)
```glsl
// ระยะทางถึงทรงกลม
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

// ระยะทางถึงกล่องสี่เหลี่ยม
float sdBox(vec3 p, vec3 b) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

// อุโมงค์ทำซ้ำอนันต์ (Space Repetition)
vec3 opRep(vec3 p, vec3 c) {
    return mod(p + 0.5 * c, c) - 0.5 * c;
}
```

### การคำนวณแสงนีออน (Neon Volumetric Glow)
สะสมค่าแสงตามระยะทางที่ Ray เคลื่อนผ่าน:
$$\text{Glow} = \sum_{i=0}^{N} \frac{\text{GlowIntensity}}{1.0 + d_i^2 \cdot \text{Falloff}}$$

---

## 4. โครงสร้างคำสั่ง FFmpeg สำเร็จรูป

```bash
ffmpeg -y \
  -framerate 60 \
  -i frames/f_%04d.png \
  -i audio.wav \
  -c:v libx264 \
  -preset slow \
  -crf 18 \
  -pix_fmt yuv420p \
  -c:a aac \
  -b:a 192k \
  -movflags +faststart \
  output.mp4
```
- `-crf 18`: คุณภาพวิดีโอระดับ Visually Lossless
- `-pix_fmt yuv420p`: เข้ากันได้กับเครื่องเล่นวิดีโอและเว็บบราวเซอร์ทุกรุ่น
- `-movflags +faststart`: ย้าย Metadata MOOV Atom มาไว้ต้นไฟล์สำหรับการสตรีมทันที
