---
name: frontend-checklist
description: "ตรวจสอบมาตรฐานหน้าเว็บและโค้ด HTML/CSS ก่อนใช้งานจริง (SEO, ความเร็ว, ความปลอดภัย) — ใช้เมื่อต้องการตรวจเช็กคุณภาพเว็บและ Core Web Vitals ให้ครบทุกจุด (Front-end QA checklist: performance, Core Web Vitals, SEO, Open Graph, security, and WCAG accessibility)"
---

# Front-End Production Checklist & Quality Standards

Meticulous guidelines for shipping production-ready web interfaces, based on the industry-standard *Front-End Checklist*.

## 1. Document Head & Metadata (Mandatory)
- **Doctype:** `<!DOCTYPE html>` as the very first line.
- **Charset:** `<meta charset="utf-8">` declared before `<title>`.
- **Viewport:** `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`. Never disable zoom (`user-scalable=no` is forbidden).
- **Title Tag:** Unique, descriptive title between 45–60 characters with business keywords.
- **Meta Description:** Compelling summary between 120–155 characters.
- **Social Sharing:** Complete Open Graph (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`) and Twitter Card (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`).
- **Favicons:** Modern SVG favicon, 32x32 PNG, and 180x180 `apple-touch-icon`.

## 2. Semantic HTML & Content Architecture
- **Heading Hierarchy:** Exactly one `<h1>` per page. Ensure logical `<h2>` → `<h3>` nesting without skipping levels.
- **Semantic Tags:** Use `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, and `<footer>` instead of unsemantic `<div>` soup.
- **Buttons vs. Links:**
  - Use `<a>` only for navigation that changes the URL.
  - Use `<button>` for actions that trigger logic/state (forms, modals, toggles).
- **Forms & Inputs:**
  - Every `<input>` MUST have an associated `<label for="...">` or `aria-label`.
  - Proper `type` (`email`, `tel`, `number`, `url`) and `autocomplete` attributes.
  - Clear inline error messages associated via `aria-describedby`.

## 3. CSS & Responsive Design
- **Mobile-First Breakpoints:** Build base styles for small screens; scale up with `@media (min-width: ...)`.
- **Fluid Layouts:** Use `rem`/`em` for typography and spacing, percentages/`fr` for grid tracks. Avoid fixed pixel widths (`width: 800px`) that cause horizontal overflow.
- **Box Sizing:** Global reset `*, *::before, *::after { box-sizing: border-box; margin: 0; }`.
- **Web Fonts:** Use `font-display: swap;` to prevent Flash of Invisible Text (FOIT). Preload primary brand fonts via `<link rel="preload" as="font" crossorigin>`.

## 4. Performance & Core Web Vitals
- **Images:**
  - Modern formats: Serve WebP or AVIF with fallback.
  - Explicit Dimensions: Always specify `width` and `height` attributes (or CSS aspect-ratio) to prevent Cumulative Layout Shift (CLS < 0.1).
  - Lazy Loading: Add `loading="lazy"` on all images below the fold. Add `fetchpriority="high"` on hero images (LCP element).
- **JavaScript Delivery:**
  - Defer non-critical scripts (`<script defer src="...">` or type="module").
  - Tree-shake dependencies; avoid importing entire libraries when single utility functions suffice.
  - Remove `console.log`, debugger statements, and dead code before shipping.

## 5. Accessibility (a11y - WCAG 2.1 AA)
- **Contrast Ratio:** Minimum 4.5:1 for normal text (< 18pt), 3:1 for large text (≥ 18pt) and UI components.
- **Keyboard Navigation:** All interactive elements must be focusable via `Tab`. Never remove outline without providing a visible `:focus-visible` state.
- **Images & Icons:** Every `<img>` requires an `alt` attribute. Decorative images use `alt=""` and `aria-hidden="true"`.
- **ARIA:** First rule of ARIA: Do not use ARIA when native HTML semantics exist.

## 6. Security & Best Practices
- **External Links:** All `<a target="_blank">` MUST include `rel="noopener noreferrer"` to prevent window.opener hijacking.
- **Content Security Policy (CSP):** Prevent XSS by restricting allowed origins for scripts, styles, and frames.
- **HTTPS:** Ensure all external resources (fonts, CDNs, APIs) are loaded securely over HTTPS.
