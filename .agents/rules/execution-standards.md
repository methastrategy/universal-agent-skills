# Global Operating Rules — Execution Standards & Security

## Autonomous Self-Healing Execution
Run syntax checks (`tsc --noEmit`), unit tests, and linters autonomously.
Self-heal in place:
- Cycle 1 fails → Epistemic Reset (question all prior assumptions)
- After 3 failed cycles → escalate with Root Cause Analysis
**Anti-Mock Guardrail:** Never relax test assertions or introduce shallow mock bypasses to make tests pass.

## Zero Drip-Feeding
Deliver complete solutions in a single turnaround. Pre-emptively add surface states:
- Loading State, Error State, Empty State, Disabled State
- Mobile responsive breakpoints, `aria-label`, keyboard navigation
Without adding unrequested third-party packages or multi-file refactors.

## Security Invariants
- Keep API keys in environment variables only — never hardcode
- Dangerous commands (`format`, `reg delete`, `rm -rf`, `curl | sh`) are hard-blocked
- High-risk operations (`git push --force`, `Remove-Item -Recurse`) require mandatory user confirmation
- Lethal Trifecta: never combine (a) private data access + (b) untrusted external ingress + (c) exfiltration channel in one unmonitored agent context

## Structural Action Gating (R·B·E·A·S)
Gate execution on: Reversibility, Blast Radius, Evidence, Ambiguity, Authorization
- Auto-execute: when reversible + verified by tool
- Ask question: when irreversible, external, or ambiguous

## Single-Agent First
Default to single-agent loop for ≥90% of development tasks.
Subagents restricted to 3 vectors only:
1. Heavy log/data isolation (large terminal logs, repo maps, web scrapes)
2. Parallel MapReduce scans (auditing 50+ files concurrently)
3. Adversarial verifiers requiring zero-assumption verification

## Git Workflow Standard
- Before major work: `git status` → commit checkpoint if uncommitted changes exist
- New features/tasks: `git checkout -b feature/<name>` — never develop directly on main/master
- After completion: `git add -A` + `git commit -m "<type>: <description>"` → merge to main
  Commit types: `feat` / `fix` / `chore` / `docs` / `data`
- Rollback: `git log --oneline -10` → `git checkout <sha> -- <file>` or `git revert`
- Windows: set `$env:GIT_DIR` and `$env:GIT_WORK_TREE` when CWD != repo root
- If `fatal: detected dubious ownership`: run `git config --global --add safe.directory '<path>'`

## Windows-Specific Standards
- Python scripts: always declare `sys.stdout.reconfigure(encoding="utf-8")` and `sys.stderr.reconfigure(encoding="utf-8")` at entrypoint
- PowerShell heredocs: use Node scripts or file-edit tools for `.md` files — never PowerShell double-quoted heredocs (`@" "@`) since `$` and backticks corrupt content
- Escape `|` inside Markdown table cells (`\|`)
- Multi-step execution: separate into clearly labeled sequential blocks — never chain critical commands with `;` on PowerShell

## Thai-Latin Mixed-Script Typography
- Declare Latin fonts BEFORE Thai fonts: `"Inter", "IBM Plex Sans Thai", ...`
- Thai typography: `letter-spacing: 0` (negative tracking breaks stacked tone marks), `line-height >= 1.7` for body, `size-adjust: 105-110%`
