---
name: react-modern-engineering
description: "เขียนโค้ดพัฒนาเว็บและแก้ปัญหาด้วย React 19 และ Next.js App Router — ใช้เมื่อสร้างหน้าเว็บคอมโพเนนต์ React, จัดการ Hooks/State หรือปรับจูนความเร็วการเรนเดอร์ (Modern React 19, Server Components, Next.js App Router, Suspense, TanStack Query/Zustand, and render optimization)"
---

# Modern React 19 & Next.js Architecture Standards

Production-grade engineering principles for building robust, scalable, and ultra-performant React applications.

## 1. React 19 Core & Server Architecture
- **React Server Components (RSC):**
  - By default, all components in Next.js App Router / React 19 are Server Components.
  - Server Components execute ONLY on the server: direct access to databases, filesystem, API secrets; zero bundle size sent to the client.
  - Push `'use client'` to the leaf nodes of your component tree (only where interactive events `onClick`, `onChange`, browser APIs, or React hooks `useState`, `useEffect` are required).
- **Server Actions (`'use server'`) & Form Mutation Protocol:**
  - Asynchronous functions defined on the server callable directly from Client Components or `<form action={...}>`.
  - **Boundary & Secret Isolation:** Put `import 'server-only'` at the top of DB, auth, and secret-handling files to fail-fast at build time if leaked to client bundles.
  - **Type-Safe Validation (Zod / Valibot):** Always execute `schema.safeParse(rawInput)` on the server before mutating DB or calling services; never rely solely on client checks.
  - **Standard Action Contract:** Return predictable discriminated unions instead of throwing unhandled exceptions:
    `type ActionResult<T> = { success: true; data: T } | { success: false; error: string; fieldErrors?: Record<string, string[]> }`
  - **Client Form Pairing:** Pair with React 19 `useActionState` or React Hook Form to orchestrate pending state, button disabling, and inline field error mapping.
- **New React 19 Hooks:**
  - `use(Promise)`: Read promises directly in render with `<Suspense>`.
  - `useActionState(action, initialState)`: Manage pending states, errors, and return values from Server Actions.
  - `useOptimistic(state, updateFn)`: Render instant optimistic UI feedback while background mutation is pending.

## 2. Component Design & Composition Patterns
- **Separation of Concerns:**
  - **Container / Smart Components:** Handle data fetching, orchestration, and business logic.
  - **Presentational / Dumb Components:** Pure functions receiving props; highly reusable and easily testable.
- **Compound Components Pattern:**
  - Build flexible UI component groups that share implicit state via Context (e.g., `<Tabs>`, `<Tabs.List>`, `<Tabs.Tab>`, `<Tabs.Panel>`).
- **Custom Hooks Best Practices:**
  - Encapsulate reusable stateful logic into focused custom hooks (`useDebounce`, `useLocalStorage`, `useIntersectionObserver`).
  - Keep hooks pure; avoid mixing multiple unrelated side effects in a single custom hook.

## 3. State Management Strategy
- **Categorize State Before Writing Code:**
  1. **Server Cache State:** Remote data from APIs/DB. Do NOT duplicate into `useState`. Use **TanStack Query** (React Query) or RSC caching (`fetch` cache, `revalidateTag`).
  2. **Global Client State:** Complex shared UI state across far branches (e.g., theme, sidebar open, multi-step builder). Use **Zustand** (lightweight, zero boilerplate, no unnecessary provider nesting).
  3. **Local Component State:** UI-only state scoped to a single component (e.g., dropdown open, input value). Use `useState` or `useReducer`.
  4. **URL State:** Filter, sort, pagination, search queries. Store in URL query params (`useSearchParams`) to ensure shareable links and browser back-button support.

## 4. Performance & Re-render Optimization
- **Do Not Prematurely Memoize:**
  - Avoid wrapping every primitive function in `useCallback` or every simple calculation in `useMemo`.
  - Use `useMemo` only when:
    1. Calculating expensive operations (e.g., sorting/filtering 1,000+ items).
    2. Providing stable object/array references passed as dependencies to `useEffect` or memoized child components (`React.memo`).
- **Composition Over Memoization:**
  - Pass expensive components as `children` or props to a stateful wrapper. When the wrapper re-renders, React reuses the existing `children` element reference without re-rendering it.
- **Dynamic Imports & Code Splitting:**
  - Lazy load heavy modals, rich text editors, and charts via `next/dynamic` or `React.lazy` with `<Suspense fallback={<Skeleton />}>`.

## 5. Modern Hooks Rules & Pitfalls
- **`useEffect` Discipline:**
  - `useEffect` is for **synchronizing with external systems** (DOM listeners, WebSockets, canvas), NOT for calculating derived state or fetching data that belongs in RSC/React Query.
  - Always provide cleanup functions to unsubscribe listeners, clear intervals, or abort `fetch` requests with `AbortController`.
- **Key Prop Rule:**
  - Never use array indices as `key` for lists that can be reordered, filtered, or mutated. Use stable unique IDs (`id`).
