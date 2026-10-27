# Disciplined Branch Finishing & Safe Release Protocol

> **Origin:** Grounded in `obra/superpowers/skills/finishing-a-development-branch` and Google Trunk-Based Engineering Standards.
> **Mandate:** Eliminate messy merges, broken pipelines, dangling WIP commits, and unverified git branches. Ensure every feature merges cleanly with verified proof.

---

## 1. The Anti-Pattern: Unfinished & Rushed Branch Merges

Merging a development branch without systematic finishing leads to:
- Committing temporary debugging code, console logs, or scratch files into `main`.
- Hidden type errors or broken integration tests that passed locally due to stale build caches.
- Stale dangling branches cluttering the repository.
- Non-reproducible commits with vague messages ("fix stuff", "update", "wip").
- Breaking production or main branch health for all team members and downstream agents.

---

## 2. The 5-Step Branch Finishing Protocol

```
[ Step 1: Automated Verification Pass ]
       │  (tsc --noEmit, test suite 100% green, pre-commit invariants)
       ▼
[ Step 2: Working Tree Cleanliness Audit ]
       │  (Zero untracked files, zero secret leaks, zero stray scratch scripts)
       ▼
[ Step 3: Git History Hygiene & Conventional Commit ]
       │  (Atomic commits, standard conventional prefixes: feat/fix/chore)
       ▼
[ Step 4: Safe Merge & Feature Branch Teardown ]
       │  (Fast-forward/squash merge to main, delete local & remote feature branch)
       ▼
[ Step 5: Executive Delivery & Handoff Summary ]
          (10-Second Judge Scorecard, test evidence, copy-ready next prompt)
```

---

### Step 1: Automated Verification Pass

Before initiating any merge or declaring a task complete, run the complete project verification pipeline:
1. **Type & Syntax Check:**
   - Execute the project's static type checker (e.g., `npx tsc --noEmit`, `mypy`, `cargo check`).
   - Must return **0 errors**.
2. **Automated Test Suite:**
   - Run unit and integration tests (e.g., `npm test`, `pytest`, `cargo test`).
   - Every single test must pass cleanly (**100% Green**).
3. **Repository Invariant Gates:**
   - Run local validation scripts (e.g., `node scripts/verify_invariants.cjs`).
   - Ensure skill descriptions $\le 220$ characters, exact skill counts, and zero dangling markdown links.

---

### Step 2: Working Tree Cleanliness Audit

Run `git status` to verify the repository surface:
1. **Zero Untracked Junk:**
   - Ensure no `.tmp`, `.orig`, `.DS_Store`, `Thumbs.db`, or temporary log dumps remain.
   - Clean up any scratch files in root or skill directories.
2. **Untrusted Data & Secret Ingress Audit:**
   - Ensure no `.env`, API keys, private tokens, or sensitive production credentials were staged.
   - Verify that any newly created files follow project naming conventions and gitignore policies.

---

### Step 3: Git History Hygiene & Conventional Commits

1. **Atomic & Structured Commits:**
   - Every commit must represent an atomic, coherent unit of work.
   - Rebase or squash messy experimental commits into a clean logical sequence before merging.
2. **Conventional Commit Standard:**
   - Format: `<type>(<scope>): <concise description>`
   - Supported types:
     - `feat`: New capability or architectural component.
     - `fix`: Defect resolution or bugfix.
     - `refactor`: Code reorganization with zero behavioral change.
     - `chore`: Maintenance, dependency updates, tooling configuration.
     - `docs`: Documentation updates and architecture reference notes.
     - `data`: Dataset, fixture, or configuration dictionary updates.

---

### Step 4: Safe Merge & Feature Branch Teardown

1. **Switch to Target Branch:**
   ```powershell
   git checkout main
   ```
2. **Merge Feature Branch:**
   - Use clean fast-forward or squash merge:
     ```powershell
     git merge feature/<branch-name>
     ```
3. **Proactive Branch Teardown (Zero Branch Clutter):**
   - Delete the local feature branch immediately upon successful merge:
     ```powershell
     git branch -d feature/<branch-name>
     ```
   - Never leave stale, merged feature branches in the local repository.

---

### Step 5: Executive Delivery & Handoff Summary

Conclude work with a high-density, factual summary:
1. **10-Second Executive Judge Scorecard:**
   - Pass/Fail verdict.
   - Total files created, modified, or removed.
   - Verbatim verification commands and exit codes (e.g., `tsc: exit 0`, `tests: 42 passed`).
2. **Zero-Friction Copy Box:**
   - Provide the exact next-step prompt or deployment command ready for the user to execute without manual text editing.

---

## 3. Pre-Merge Verification Checklist

| Gate | Check Item | Pass Criteria | Command / Evidence |
| :---: | :--- | :--- | :--- |
| **G1** | Static Type Check | 0 type errors | `npx tsc --noEmit` (Exit 0) |
| **G2** | Test Suite | 100% passing tests | `npm test` or `pytest` (Exit 0) |
| **G3** | Invariant Guard | 0 broken rules/links | `node scripts/verify_invariants.cjs` |
| **G4** | Git Cleanliness | No untracked debris | `git status --short` (Clean) |
| **G5** | Branch Teardown | Feature branch deleted | `git branch` (Only main remaining) |
