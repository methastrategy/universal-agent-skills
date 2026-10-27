# Systematic 4-Phase Defect Investigation & Scientific Root Cause Eradication

> **Origin:** Grounded in `obra/superpowers/skills/systematic-debugging` and the SWE-Bench defect isolation discipline.
> **Mandate:** Eliminate the "guess-and-check" anti-pattern. Never mutate implementation code on hunches, trial-and-error edits, or superficial symptom masking.

---

## 1. The Anti-Pattern: Speculative "Guess-and-Check"

The most destructive behavior in debugging is making trial-and-error edits hoping the error disappears:
- Wrapping failing lines in empty `try/catch` or nil-checks without understanding why `null` arrived.
- Adding arbitrary `setTimeout`, `sleep()`, or retry loops around race conditions.
- Speculatively modifying regexes, boundary operators (`<` vs `<=`), or type assertions without proof.
- Churning multiple files in a single edit, polluting git history and obscuring the actual cause.

**The Golden Invariant:** If you cannot deterministically explain *why* the failure occurs and reproduce it on demand, you cannot know whether your fix actually solves the defect or merely masks the symptom.

---

## 2. The 4-Phase Scientific Investigation Lifecycle

```
[ Phase 1: Problem Characterization & Seam Isolation ]
       │  (Deterministic reproduction, boundary inputs, failure logs)
       ▼
[ Phase 2: Pattern, Invariant & Anomaly Analysis ]
       │  (Git bisect, orthogonal 4-probes, state divergence point)
       ▼
[ Phase 3: Scientific Hypothesis Testing (Controlled Falsification) ]
       │  (1 variable at a time, testable prediction, revert if refuted)
       ▼
[ Phase 4: Surgical Eradication & Regression Pinning ]
          (Minimal diff, fail-to-pass test, pass-to-pass verification)
```

---

### Phase 1: Problem Characterization & Minimal Seam Isolation

Before opening any implementation file or proposing a code change:
1. **Deterministic Reproduction:**
   - Extract the exact input payload, command line arguments, environment variables, and configuration flags that trigger the defect.
   - If reproduction is non-deterministic (e.g. flaky test or concurrency glitch), build a stress harness that runs the seam in a tight loop ($N = 100$) until the failure rate is measured.
2. **Divergence Point vs Root Cause Distinction:**
   - *Symptom:* "Cannot read properties of undefined (reading 'status') at line 48".
   - *Divergence Point:* Line 48 where `res` is undefined.
   - *Root Cause:* The upstream HTTP client on line 12 dropped the response body when the server returned HTTP 204 No Content.
   - Never fix the divergence point (e.g. `res?.status`); fix the root cause upstream.

---

### Phase 2: Pattern, Invariant & Anomaly Analysis

1. **State Invariant Audit:**
   - Identify which system contract or invariant was broken (e.g., "Cache entry must have a valid TTL", "Database transaction must either commit or rollback completely").
2. **Temporal & Diff Analysis (When Did It Last Work?):**
   - Run `git log -p -S "<function_name>"` or `git bisect` to find the exact commit that introduced the behavioral delta.
   - Compare the environment, dependency versions (`package-lock.json`, `uv.lock`), and platform specifics between the passing and failing states.
3. **Speculative Fan-Out (Parallel 4-Probe Triage):**
   - **Probe A (Environment & Encoding):** Windows backslashes `\` vs POSIX `/`, UTF-8 with BOM, missing environment secrets, OS permissions.
   - **Probe B (Boundary & Nil-Leap):** Off-by-one indices, zero values treated as falsey, unexpected empty arrays, JSON schema coercion.
   - **Probe C (Lifecycle & Concurrency):** Promise race conditions, unhandled rejections, closure memory leaks, event listener duplication.
   - **Probe D (Cache & Build Drift):** Stale build artifacts (`.next/`, `dist/`), desynced node_modules, uncompiled TypeScript types.

---

### Phase 3: Scientific Hypothesis Generation & Controlled Falsification

1. **Formulate Explicit Hypotheses:**
   - State the hypothesis in falsifiable terms:
     > *"Hypothesis: The worker pool drops jobs because job IDs containing underscores are rejected by the dispatch regex in `worker.ts:24`."*
2. **Strict Single-Variable Isolation:**
   - Change exactly **one variable at a time**.
   - If testing a regex fix, do not touch error handling or logging in the same edit.
3. **Falsification & Epistemic Reversion:**
   - If the single-variable test does not resolve the failure or fails to confirm the hypothesis:
     - **Revert the edit immediately** (`git checkout -- <file>`).
     - Never stack speculative edits on top of unverified assumptions.
     - Perform an Epistemic Reset: discard the disproven theory and pick the next ranked probe.

---

### Phase 4: Surgical Eradication & Regression Pinning

1. **Write the Fail-to-Pass (F2P) Test First:**
   - Create a minimal unit or integration test targeting the public seam.
   - Run the test suite on unpatched code to observe the test fail with the exact expected error signature (**RED**).
2. **Apply the Minimal Structural Fix (Ponytail Hierarchy):**
   - Apply the smallest complete diff that solves the underlying architectural defect.
   - Do not add unrequested abstractions, helper utilities, or third-party libraries.
3. **Verify Green & Non-Regression:**
   - Run the target test to confirm transition to **GREEN**.
   - Run the full test suite (`npm test`, `pytest`, `cargo test`) to ensure zero Pass-to-Pass (P2P) regressions.
4. **Postmortem Ledger Entry:**
   - Document the failure signature, root cause, and regression test identifier for future reference.

---

## 3. Operational Verification Checklist

| Step | Action | Required Evidence |
| :--- | :--- | :--- |
| **1. Repro** | Reproduce on demand without manual clicking | Verbatim CLI command & exit code != 0 |
| **2. Isolate** | Pinpoint exact divergence point vs root cause | Stack trace + data flow trace |
| **3. F2P Test** | Automated test failing on unpatched code | Verbatim test output showing expected failure |
| **4. Patch** | Smallest surgical diff fixing root cause | Git diff showing single mutable surface |
| **5. Green** | Automated test passes on patched code | Verbatim test output showing exit code 0 |
| **6. Non-Regression** | Entire project test suite green | Zero test regressions across repo |
