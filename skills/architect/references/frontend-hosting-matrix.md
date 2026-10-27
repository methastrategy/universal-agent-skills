# Frontend Hosting & Cloud Deployment Decision Matrix

คู่มือการเลือกผู้ให้บริการโฮสติ้งสำหรับ Frontend & Full-Stack Apps พร้อมการประเมินความเสี่ยงด้านค่าใช้จ่าย และข้อจำกัดทางกฎหมายเชิงพาณิชย์ (Terms of Service)

---

## 1. การเปรียบเทียบผู้ให้บริการหลัก (Provider Comparison Matrix)

| ผู้ให้บริการ | จุดเด่น (Strengths) | ข้อจำกัด / กับดักแอบแฝง (Gotchas & Risks) | เชิงพาณิชย์ (Commercial Use) | Best Fit |
| :--- | :--- | :--- | :---: | :--- |
| **Cloudflare Pages** ⭐ | • Unlimited Bandwidth (Fair Use)<br>• Global Anycast Edge Network<br>• Custom Domain + Free SSL + DDoS | • Edge Runtime มีข้อจำกัด Node.js APIs บางตัว<br>• SSR ซับซ้อนกว่า (ต้องพึ่ง OpenNext/Workers) | ✅ ฟรี 100% | Static Web, SPA (Vite/React/Vue), งานลูกค้ารับเงิน, เว็บไซต์ธุรกิจ |
| **Vercel** | • สุดยอด Developer Experience (DX)<br>• Zero-config สำหรับ Next.js SSR / Actions<br>• Preview Deployments ทุก PR | 🚨 **Hobby Plan ห้ามใช้เชิงพาณิชย์เด็ดขาด** (TOS Sec 4.1): ห้ามรับงานลูกค้า, เว็บขายของ, ติด Ads, ลิงก์ Affiliate หากละเมิดเสี่ยงโดนแบนหรือคิดเงิน Pro $20/user/mo ย้อนหลัง | ❌ เฉพาะ Non-Commercial | โปรเจกต์ส่วนตัว, POC, Demo งานวิจัย, งานทดสอบ |
| **Netlify** | • มีฟังก์ชัน Form Handling / Auth ในตัว<br>• จัดการ Headers / Redirects สะดวก | ⚠️ **Bandwidth Cap 100 GB/เดือน:** หากเกินจะคิดเงินเพิ่ม $55 ต่อ 100 GB ทันที มีความเสี่ยง Bill Shock หากถูก Bot สูบ | ✅ อนุญาตใน Free Plan | เว็บโปรโมตสินค้าขนาดเล็กที่ต้องการ Form ติดต่อโดยไม่เขียน Backend |
| **GitHub Pages** | • ผูกติดกับ Git Push แล้วออนไลน์ทันที<br>• เชื่อม GitHub Actions สบาย | • Private Repo บน Free Account ใช้ไม่ได้ (ต้องเปิด Public)<br>• Bandwidth soft cap 100 GB/เดือน, Repo size <= 1 GB | ✅ อนุญาต (ภายใต้ GitHub AUP) | เว็บเอกสาร Docs (VitePress, Docusaurus), Open-Source Showcase |
| **Render** | • Static Sites ฟรี 100% ไม่หลับ (No Sleep)<br>• มีบริการ Managed DB & Backend ในตัว | • ฝั่ง Web Service / Backend (Node/Python) จะเข้าสู่ Sleep Mode หลังไม่มี Traffic 15 นาที (Cold start ~50s) | ✅ อนุญาต | Full-Stack แบบเบ็ดเสร็จ (Frontend Static + Backend Container ในที่เดียว) |
| **Firebase Hosting** | • เร็วมากบน Google CDN<br>• ลิงก์กับ Firebase Auth / Firestore / Functions ราบรื่น | • พื้นที่จัดเก็บ 10 GB, Data Transfer ฟรี 360 MB/วัน (10 GB/เดือน) หากเกินต้องเปิดระบบ Pay-as-you-go | ✅ อนุญาต | เว็บแอปพลิเคชันที่ใช้ Firebase Stack เป็นแกนหลัก |

---

## 2. Invariants & กฎเหล็กการเลือกสถาปัตยกรรม (Architecture Selection Rules)

1. **The Vercel Commercial Prohibition Invariant:**
   - ห้ามแนะนำ Vercel Hobby Plan (Free) สำหรับงานที่มีธุรกรรมการเงิน, รับจ้างทำเว็บลูกค้า, หรือหารายได้จาก Ads/Affiliate เด็ดขาด
   - หากผู้ใช้ต้องการทำ Production สำหรับธุรกิจ ให้เลือก **Cloudflare Pages** (สำหรับ Static/SPA) หรือย้าย Next.js ไปรันบน **Google Cloud Run (Serverless Container)**

2. **The Bandwidth Spike Immunity Invariant:**
   - สำหรับเว็บไซต์ที่มีความเสี่ยงต่อการโดน Scraping, Bot Crawl, หรือ Viral Traffic ให้เลือก **Cloudflare Pages** เป็นค่าเริ่มต้นเสมอ เพื่อป้องกันการถูกชาร์จค่า Bandwidth Overages มหาศาลเหมือนใน Netlify ($55/100GB)

3. **Zero-Cost Production Golden Stack:**
   - **Frontend:** Cloudflare Pages (ฟรี, แบนด์วิธไม่จำกัด, Edge SSL, คุ้มครองเชิงพาณิชย์)
   - **Backend API:** Google Cloud Run (ฟรี 2,000,000 requests/เดือน, Scale-to-Zero, Containerized Node/Python/Go)
   - **Database:** Supabase / Neon PostgreSQL (Free Tier สำหรับ Managed DB พร้อม Connection Pooling)
