# Storyboard & Narrative Templates for `/genflow`

## 1. โครงสร้างละครสั้น 10 ตอน (10-Episode Mini-Drama Arc)

เมื่อผู้ใช้สั่ง *"ทำคลิปละครสั้น 10 ตอน"* ให้แตกตามโครงสร้าง 10 Beats สากลดังนี้:

| Episode | Narrative Beat | บทบาทในเรื่อง | ตัวอย่าง Prompt Visual Action |
| :---: | :--- | :--- | :--- |
| **01** | The Hook / Ordinary World | เปิดตัวละครเอก และชีวิตประจำวัน | ตัวละครอยู่ในสถานการณ์ปกติ แต่มีสัญญาณแปลกๆ |
| **02** | Inciting Incident | เหตุการณ์จุดชนวนความเปลี่ยนแปลง | ค้นพบเบาะแสสำคัญ แผนที่โบราณ หรือความท้าทาย |
| **03** | Hesitation & Crossing | ลังเลก่อนตัดสินใจก้าวข้ามสู่โลกใหม่ | จัดเตรียมสัมภาระ อุปกรณ์ และก้าวออกจาก Safe Zone |
| **04** | The First Obstacle | เผชิญอุปสรรคแรกและการทดสอบ | ฝนตกหนัก น้ำท่วม หรือทางตัน ต้องใช้ไหวพริบแก้ |
| **05** | Finding an Ally | พบเพื่อนร่วมทางหรือไอเทมลับ | ได้รับอุปกรณ์พิเศษ (เช่น กล้องสำรวจวิเศษ หรือแผนที่) |
| **06** | Midpoint Reversal | จุดพลิกผันกลางเรื่อง (เดิมพันสูงขึ้น) | ความจริงเปิดเผย สิ่งที่ตามหาซ่อนอยู่ในที่อันตราย |
| **07** | The Dark Moment | วิกฤตการณ์ถึงขีดสุด (ความพ่ายแพ้) | อุปกรณ์พัง หลงทาง หรือหมดหวัง |
| **08** | The Epiphany | ค้นพบแสงสว่างและการตื่นรู้ | นึกถึงคำสอน หรือสังเกตเห็นจุดเชื่อมโยงที่เคยมองข้าม |
| **09** | The Climax | ช็อตปะทะตัดสิน / แก้ปริศนาสำเร็จ | รวมพลังความสามารถทั้งหมด แก้ปัญหาสำเร็จอย่างงดงาม |
| **10** | Resolution & Celebration | ฉลองชัยชนะและการเติบโต | ยิ้มรับความสำเร็จ ยืนเคียงข้างมิตรสหายอย่างภาคภูมิ |

---

## 2. Character Consistency Locker (กฎเหล็กการล็อกตัวละคร)

เพื่อไม่ให้หน้าตา สีผิว หรือชุดของตัวละครเปลี่ยนไปมาระหว่างตอน:
1. **Name & Exact Species**: ต้องระบุคำเดิมเป๊ะๆ ทุก Prompt เช่น `chibi baby green dragon`
2. **Fixed Anchor Accessories**: ไอเทมประจำตัว 2-3 ชิ้นที่ต้องมีเสมอ เช่น `wearing a vivid red military beret, golden horn tips`
3. **Rendering Style Anchor**: กำหนดสไตล์หลัก เช่น `3D voxel Minecraft aesthetic` หรือ `Claymation stop-motion style`
4. **Clothing Invariant**: ระบุชุดสีและทรงเดิม เช่น `brown safari vest over cream shirt`

---

## 3. Zero-Fluff Prompting Formula (สูตรเขียน Prompt มาตรฐานสตูดิโอ)

สูตรการเขียน Prompt แบบ Zero-Fluff เรียงตามลำดับน้ำหนักความสำคัญ (Slot 1 ถึง 8):

```text
[1 Subject + State] -> [2 Setting (1 clause)] -> [3 Composition] -> [4 Camera + Lens] -> [5 Light (Source, Direction, Hardness, Kelvin, Falloff)] -> [6 Color Grade / Stock] -> [7 Material + 1 Asymmetric Imperfection] -> [8 Engine Params]
```

### รายละเอียดและตัวอย่างแต่ละ Slot:

| Slot | องค์ประกอบ | คำอธิบาย & ตัวเลือกที่แนะนำ | ตัวอย่างคำศัพท์ |
| :---: | :--- | :--- | :--- |
| **1** | **Subject + State** | ประธาน, อารมณ์, ท่าทาง, การเคลื่อนไหว | `weathered female surveyor wiping sweat from forehead with linen cloth` |
| **2** | **Setting (1 clause)** | บริบทฉากจบในประโยคเดียว กระชับ ไม่อธิบายเวิ่นเว้อ | `on muddy construction hillside at twilight` |
| **3** | **Composition** | โครงสร้างการจัดองค์ประกอบภาพ | `tight three-quarter medium shot, rule of thirds, leading lines` |
| **4** | **Camera + Lens** | รุ่นกล้องและเลนส์ทำหน้าที่เป็น Style Token | `ARRI Alexa 35, Cooke S4/i 50mm T2.0 at T2.8` |
| **5** | **Light** | แหล่งกำเนิด, ทิศทาง, ความแข็ง/นุ่ม, อุณหภูมิสี, การกระจายตัว | `low 45-degree golden-hour key light from camera left at 3200K, soft ambient skylight 5600K, subtle natural falloff` |
| **6** | **Color Grade / Stock** | โทนสีและฟิล์มสต็อก | `Kodak Vision3 5219 500T, muted olive and warm amber palette, filmic s-curve contrast` |
| **7** | **Material + Imperfection** | เนื้อสัมผัสจริง พร้อมความไม่สมบูรณ์แบบอสมมาตร 1 จุด | `heavy canvas vest with mud splatter on left pocket, visible skin pores and stray flyaway hair strands` |
| **8** | **Engine Params** | พารามิเตอร์ของเอนจิน AI ปลายทาง | `--ar 16:9 --style raw --s 75` (Midjourney) หรือ `--v 6.1` |

---

## 4. แบนคำขยะ (Quality-Spam Banned Words)

> [!CAUTION]
> **ห้ามใช้คำศัพท์ต่อไปนี้เด็ดขาด:**
> `8k`, `masterpiece`, `hyperrealistic`, `perfect skin`, `smooth skin`, `cinematic lighting`
>
> **เหตุผล:** คำเหล่านี้ทำให้โมเดลยุคใหม่ (Flux, Midjourney v6, SDXL, Imagen 3) เกิดอาการ Over-baking, พลาสติกเลี่ยมจัด, ผิวคนไร้รูขุมขนแบบหุ่นขี้ผึ้ง, และแสงประดิษฐ์ไร้ทิศทาง ให้แทนที่ด้วย **Camera/Lens specifications**, **Physical lighting parameters (Kelvin, direction)**, และ **Micro-textures** เสมอ

---

## 5. Camera as Style Tokens (จับคู่กล้อง/เลนส์กับสไตล์งาน)

การระบุชื่อกล้องและเลนส์ไม่ได้แค่บอกมุมกล้อง แต่ทำงานเป็น **Style Latent Token** กำหนด Color Science และ Texture:

| กล้อง / เลนส์ | ลักษณะเด่น & อารมณ์ภาพ | การใช้งานที่เหมาะสม | ข้อควรระวัง |
| :--- | :--- | :--- | :--- |
| **`ARRI Alexa 35 / Mini LF`** | ผิวคนนุ่มนวลเป็นธรรมชาติ ไดนามิกเรนจ์สูง Roll-off แสงไฮไลต์สมจริง | งานภาพยนตร์ ละครสั้น เล่าเรื่องที่เน้นอารมณ์คน | เหมาะกับเลนส์ Cooke หรือ Arri Signature Prime |
| **`Hasselblad X2D / GFX100 II`** | Medium format เซนเซอร์ใหญ่ Micro-contrast สูง ลึก คมกริบระดับไมครอน | งานสินค้าพรีเมียม ถ่ายวัตถุ รถ เครื่องประดับ | ห้ามใช้กับงานดิบ/Candid เพราะภาพจะดูเนี๊ยบเกินไป |
| **`Leica M11 / 35mm f/1.4`** | โทนสารคดี คอนทราสต์แบบ Street Photo ภาพมีชีวิตชีวา ไม่จัดฉาก | งาน Candid สารคดี ช็อตเบื้องหลัง ช็อตบังเอิญ | ไม่เหมาะกับช็อตสตูดิโอทางการ |
| **`85mm f/1.4`** | ช็อตพอร์ตเทรตแยกตัวแบบจากฉากหลัง (Subject Separation) โบเก้กลมละมุน | Hero Portrait ตัวละครเดี่ยว ช็อตอารมณ์ | ไม่เหมาะกับฉากหมู่อันกว้าง |
| **`100mm macro f/2.8-f/5.6`** | ถ่ายเจาะเนื้อวัสดุ ผิวสัมผัส ลวดลายหิน โลหะ ดิน หยดน้ำ | งาน Macro เจาะ Detail วัตถุ | **ห้ามใช้ f/1.4 ในงาน Macro** เด็ดขาด เพราะ Depth of Field จะบางเกินจนภาพเบลอไร้จุดโฟกัส |

---

## 6. Engine-Specific Handling (การปรับแต่งตามเอนจิน AI)

### 1. Flux.1 (ห้ามใช้ Negative Prompt)
โมเดล Flux.1 ถูกเทรนด้วย Rectified Flow Transformer ไม่รองรับ Negative Prompting การใส่ Negative Prompt จะทำให้ภาพเพี้ยน ให้ใช้ **Positive Substitutions** ระบุสิ่งที่ต้องการเห็นแทน:
- **แทนที่ `perfect skin` / `no smooth plastic` ด้วย:**
  `"visible skin pores, fine vellus hair, subtle uneven skin tone, natural under-eye texture, fine expression lines, flyaway hair strands"`
- **แทนที่ `no blur` ด้วย:**
  `"f/4.0 deep focus, crisp edge clarity across frame"`

### 2. Midjourney v6
- **ใช้คำสั่ง:** `--style raw --s 0-100` (แนะนำค่า `--s 50` หรือ `--s 75` เพื่อรักษาความสมจริงและคงรูปทรงเรขาคณิต)
- **หลีกเลี่ยง:** การสแปมคำสั่ง `--no` พร่ำเพรื่อ (เช่น `--no blur, ugly, deformed`) ให้ใช้วิธีบรรยายสิ่งที่ต้องการเห็นให้ชัดเจนแทน

### 3. Stable Diffusion / SDXL
- **รูปแบบ:** Comma-separated tags เรียงตามน้ำหนักความสำคัญ
- **Negative Baseline มาตรฐาน:**
  `"plastic skin, wax figure, CGI, 3D render, oversharpened, airbrushed, cartoon, extra limbs, mutated hands, watermark, signature"`

---

## 7. ตารางเปรียบเทียบตัวอย่าง Prompt (Bad vs Good)

| จุดประสงค์ | ❌ Bad Prompt (Quality-Spam เกลื่อน) | ✅ Good Prompt (Zero-Fluff Formula) |
| :--- | :--- | :--- |
| **ตัวละครเอกกลางแจ้ง** | `a beautiful female surveyor, masterpiece, 8k, realistic, perfect smooth skin, cinematic lighting, hyperrealistic, ultra detailed` | `tired Southeast Asian female surveyor in olive hi-vis vest, standing on dusty gravel quarry road at sunset, medium shot, ARRI Alexa 35, 85mm f/2.0, low 3200K key light from right with gentle skylight fill, Kodak Vision3 500T warm palette, visible skin pores, fine vellus hair, sweat beads along hairline, subtle dust on cheek, natural fabric texture` |
| **เจาะเนื้อวัสดุอุปกรณ์** | `close up of modern survey total station, 8k, masterpiece, shiny, photorealistic, amazing quality, f/1.4 macro` | `macro detail of brass leveling tribrach on Leica total station, workshop workbench setting, tight macro composition, Hasselblad X2D, 100mm macro f/4.0, diffuse North-facing window daylight 5200K with soft silver reflector fill, neutral clean color grade, anodized matte metal with fine micro-machining scratches, single oil smudge near calibration knob` |
