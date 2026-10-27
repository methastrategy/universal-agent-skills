# Adversarial Code Review, Subagent Verification & Peer Defense Protocol

> **Origin:** Grounded in `obra/superpowers/skills/requesting-code-review` and `receiving-code-review`.
> **Mandate:** Eliminate author bias, blind spots, and rubber-stamp reviews. Subject all complex changes to independent, adversarial verification before declaring victory.

---

## 1. The Anti-Pattern: Self-Review Confirmation Bias

When authors review their own code or perform shallow self-checks:
- They unconsciously verify that the "happy path" works, ignoring hostile inputs.
- They overlook subtle edge cases, concurrency race conditions, and error-handling bypasses.
- They accept tests that pass by virtue of shallow mocks rather than genuine execution.
- They exhibit cognitive anchoring, assuming their architectural choices are without flaw.

**The Adversarial Principle:** The goal of the code reviewer is not to confirm that the code works under ideal conditions, but to find the pathological conditions under which it fails.

---

## 2. Multi-Agent Adversarial Verification Architecture

```
[ Author Agent ] ──( Hands off completed feature & test suite )──► [ Fresh Adversarial Verifier ]
                                                                        │
                                      ┌─────────────────────────────────┴─────────────────────────────────┐
                                      ▼                                                                   ▼
                          [ Stress Attack Vectors ]                                           [ Empirical Verification ]
                          - Malicious/extreme inputs                                          - Anti-mock assertion check
                          - Concurrency & race yields                                         - Live execution & leak test
                          - Resource leak & bounds                                            - Bit-exact state verification
                                      │                                                                   │
                                      └─────────────────────────────────┬─────────────────────────────────┘
                                                                        ▼
                                                   [ Review Verdict & Required Remediation ]
                                                   (Pass: Ship / Fail: Reject with Proof)
```

---

### Decoupled Subagent Dispatch (`Role: "Adversarial Verifier"`)

For non-trivial features, deep refactors, or security-sensitive changes, dispatch an independent subagent with fresh context:
```python
invoke_subagent(
    TypeName="research",  # or self in branch/isolated mode
    Role="Adversarial Verifier",
    Prompt="""
    Conduct an aggressive adversarial review of the latest code changes.
    Your goal is to stress-test edge cases, find input validation bypasses, race conditions,
    and verify that test assertions are genuine (anti-mock audit).
    Do NOT offer polite praise. Return findings prioritized by severity: Critical, High, Medium.
    """
)
```

---

## 3. The 5-Vector Adversarial Attack Checklist

Every adversarial review must systematically probe five distinct attack surfaces:

### Vector 1: Malicious & Pathological Input Stress
- **Extreme Boundary Values:** Empty arrays, 0, negative integers, MAX_SAFE_INTEGER, `NaN`, `Infinity`, `null`, `undefined`.
- **String Pathology:** Strings containing null bytes (`\0`), unescaped quotes, SQL injection metacharacters, directory traversal (`../`), and invalid UTF-8 sequences.
- **Payload Bloat:** Unbounded request payloads, deeply nested JSON objects causing stack overflow during parsing.

### Vector 2: Concurrency, Reentrancy & Lifecycle Race
- **Asynchronous Yield Points:** What happens if two async operations trigger simultaneously? Is there a mutex or atomic gate?
- **State Invalidation during Await:** Does state mutate while waiting for an external promise to resolve?
- **Double-Invocation:** What happens if the user double-clicks or triggers the event handler twice within 10ms?

### Vector 3: Anti-Mock & Test Assertion Integrity
- **Assertion Strictness:** Are tests using exact equality (`expect(result).toBe(42)`) or loose checks (`expect(result).toBeDefined()`)?
- **Mock Bypass Audit:** Are core architectural seams mocked out so heavily that the test passes without testing any real logic?
- **Negative Test Coverage:** Does the test suite verify that the system correctly fails and throws on invalid inputs?

### Vector 4: Resource Leaks & Teardown Integrity
- **Connection & File Descriptor Leaks:** Are database connections, sockets, and file handles closed in a `finally` block?
- **Event Listener Accumulation:** Are DOM listeners, timers (`setInterval`), and background subscriptions cleanly removed?
- **Memory Footprint:** Do in-memory caches or collections grow unboundedly over time without eviction policies (LRU/TTL)?

### Vector 5: Silent Degradation & Error Swallowing
- **Empty Catch Blocks:** Are exceptions swallowed or logged without proper propagation or user notification?
- **Fallback Masking:** Does a default fallback value hide a serious underlying database corruption or schema mismatch?
- **Type Coercion Hazards:** Are truthy checks (`if (x)`) inadvertently dropping valid `0` or `""` inputs?

---

## 4. Peer Defense & Evidence-Based Remediation Protocol

When responding to an adversarial review, the author agent must adhere to strict defense rules:
1. **No Defense Without Verbatim Proof:**
   - Never respond with "This is safe because..." or "I handled this earlier."
   - Every rebuttal must link to the exact line of code, automated test output, or live execution log proving safety.
2. **Acceptance of Genuine Flaws:**
   - If the adversarial verifier identifies a reproducible defect, immediately acknowledge the root cause, write a failing regression test (F2P), and apply a surgical fix.
3. **Closing Condition:**
   - A change may only be merged when the adversarial verifier confirms zero Critical or High findings, and all test suites pass with 100% green status.
