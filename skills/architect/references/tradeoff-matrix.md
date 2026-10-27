---
name: tradeoff
description: "วิเคราะห์เปรียบเทียบข้อดี-ข้อเสีย จุดแข็ง-จุดตาย เพื่อตัดสินใจเลือกทางที่ดีที่สุด — ใช้เมื่อลังเลว่าจะเลือกใช้เครื่องมือ อัลกอริทึม โค้ด หรือแนวทางไหนดี (Objective multi-dimensional tradeoff analysis and architectural decision matrix)"
---

# Objective Architectural Tradeoff Analysis

Evaluate competing technical options, libraries, architectures, or designs through structured metric matrices and objective evidence to determine the optimal choice.

## Steps

1. **Define Competing Options**: Explicitly detail Option A and Option B, including setup, complexity, and dependencies.
2. **Perform Multi-Dimensional Audit**: Analyze both options against performance, maintainability, scalability, and delivery time.
3. **Compare Trade-Off Metrics**: Create a direct comparative matrix showing where each option excels or fails.
4. **Justify Technical Selection**: Make a definitive recommendation backed strictly by architectural metrics and constraints.

---

## Output Structure

- **Comparative Options Matrix**: Structural mapping of alternatives and their core properties.
- **Dimensional Scorecard**: Metrics comparing complexity, performance, and maintenance overhead.
- **Architectural Decision**: Recommended choice with clear, logic-based justifications.

---

## Operating Rules

- Must compare at least 2 highly viable options; do not construct a weak strawman option to bias the selection.
- Base all scoring and tradeoffs on measurable evidence, profiles, or strict requirements.
