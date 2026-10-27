---
name: refactor
description: "จัดระเบียบและปรับโครงสร้างโค้ดให้คลีนโดยไม่เปลี่ยนผลลัพธ์เดิม — ใช้เมื่อโค้ดรก ซับซ้อน หรือต้องการแยกโมดูลให้ดูแลง่าย (Zero-regression refactoring, modular extraction, cyclomatic reduction)"
---

# Zero-Regression Codebase Refactoring

Refactor code to enhance modularity, readability, and maintainability while preserving 100% functional equivalence and verifying against automated test suites.

## Steps

1. **Identify Target Areas**: Locate high-complexity blocks, code duplication, or poorly structured modules.
2. **Isolate Logic Components**: Extract targets into focused, modular, single-purpose functions.
3. **Verify Boundary Conditions**: Ensure that refactored blocks expose exact identical APIs and typings.
4. **Execute Regression Testing**: Compile and run full test suites to guarantee absolute functional preservation.

---

## Shared-Base Extraction (extracting a common helper from N sibling scripts)

Pulling duplicated scaffolding into one `base_<x>.py` is the highest-yield refactor for script families, but it is where behavior silently disappears. The extracted helper owns only what the author noticed; every side effect living in the per-caller code is at risk.

Before/after extraction checklist:

- **Diff behavior, not just imports.** After extraction, compare each caller's pre-refactor version against the new shared helper for every side effect the caller used to perform: `git show <sha>^:<file>` reveals them. Extra output copies, artifact-directory exports, log lines, return values, and cleanup steps are the usual casualties. Rule: the union of all caller behaviors must be present in the shared helper.
- **Keep the caller's leftover imports honest.** After extraction the caller may still import what the helper now owns. Delete it, or the module keeps a dependency it no longer uses. Grep each caller for the symbol the helper now provides.
- **Check for duplicate import lines.** Automated edits that insert an import block often leave the same import repeated two or three times in one file. Grep each file for the import statement and require exactly one occurrence.
- **Prove byte-identical output, not "it ran".** Re-run one caller that produces a deterministic artifact and compare the artifact's md5 against the committed blob (`md5sum <file>` vs `git show HEAD:<file> | md5sum`). Identical hashes are the evidence that the refactor preserved behavior; a clean exit code is not.
- **Update the call graph evidence.** Confirm the new edges actually appear in the dependency graph (or import scan) so downstream tooling sees the shared module.

```bash
git show <sha>^:<file> | grep -nE "artifact_dir|copy|export|save"   # pre-refactor side effects
grep -cE "^from base_.* import" <file>                              # exactly 1 per caller
md5sum <artifact>; git show HEAD:<artifact> | md5sum                 # byte-identical proof
```

## Operating Rules
- Absolutely zero modifications to external APIs, input parameter specifications, or business logic outputs.
- Never refactor without active compile checks and immediate test runs.
- When the environment lacks a dependency the refactored code needs (e.g. a browser automation library for a screenshot pipeline), locate the interpreter that has it (`python3 -c "import <pkg>"` across candidate interpreters) before concluding the refactor broke — the module-not-found error may be the wrong interpreter, not the code.

---

## Large-File Extraction Mechanics (files over ~800 lines)

Extracting a helper out of a 2,000-line component is a different exercise from editing a small module. The
edit chain, not the logic, is what breaks.

- **Write the new module first, as a brand-new file.** Then change the host with one surgical patch per call
  site whose `old_string` spans the whole function boundary. Import swap, body deletion, and call-site rename
  are three separate patches — a combined patch leaves the old body orphaned inside whatever declaration sits
  at that offset (an interface absorbs a function body, an options array swallows `return { ... }` literals).
- **Never chain patches against a file you have only read through `offset`/`limit`.** Line numbers shift after
  every accepted edit and fuzzy matching will land a hunk at the wrong brace level. Re-read the exact region
  right before patching it, and re-read after any patch that changes the line count.
- **Run the type checker after each file, not at the end.** `tsc --noEmit` points at the first broken brace
  with a file:line; that five-second signal stops the next patch from building on rubble.
- **A corrupted file is cheaper to redo than to repair.** `git checkout -- <file>` restores the pre-refactor
  version when the work is uncommitted; re-apply only the changes still needed. Do not unwind brace soup hunk
  by hunk.
- **Sweep for leftovers from an interrupted write.** An aborted write can leave an empty `.hermes-tmp.*` beside
  the target; it shows up as untracked in `git status`. Delete it before it lands in a commit.

---

## Coverage Checklist
> เนื้อหาที่ต้องครอบคลุม ไม่ใช่หัวข้อที่ต้องพิมพ์ — ห้ามตอบเป็นหัวข้อเลขข้อ รูปแบบตอบตาม GEMINI.md §1
- **Refactoring Scope**: List of modules, interfaces, and complexity metrics targeted.
- **Complexity Improvements**: Explicit before/after cyclomatic complexity metrics and nesting depth reduction.
- **Regression Report**: Complete log of integration and unit tests validating functional identicalness.

---


