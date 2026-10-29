# Global Operating Rules — Token-Smart Skill & Context Governance

## Progressive Skill Loading
- Only load a skill's full SKILL.md when directly matched to task intent
- Skill names and descriptions are always loaded (lightweight index)
- Full skill content loaded just-in-time on activation
- Deep references (references/*.md) read only when needed during implementation

## Skill Creation Guardrail
- SKILL.md body: ≤ 6,000 chars (hard warn at 8,000 chars)
- Description: ≤ 220 chars — format: "[verb+category] — use when [symptom] (EN triggers)"
- Create new skill ONLY for recurring multi-step workflows too complex to memorize
- Maximum: 23 skills total
- Offload detailed guides and fixtures to `references/` for compaction resilience

## Zero-Flag Intuitive Routing
Skills must never force the user to recall CLI flags or sub-commands.
Implement dual-layer dispatch:
1. **Auto-Detect Intent Engine** — infer and switch to sub-mode from natural language/context
2. **Interactive Cockpit Gate** — if invoked bare without context, launch `ask_question` with structured options

## Compaction Resilience (Lean-Core Pattern)
Keep root SKILL.md files strictly lean (≤ 6,000 chars) with only:
- Execution engines and protocols
- Interface contracts and triggers
- Reference pointers (link to references/*.md)
Offload detailed guides, fixtures, and examples to `references/` so critical rules survive `/compact`.

## Autonomous Knowledge Registry
When inspecting, analyzing, or absorbing a new external repository or benchmark:
Automatically append the entry with timestamp, commit/version, and absorbed invariants to:
- `Knowledge_Absorption_Checklist.md`
- `KNOWLEDGE_REGISTRY.md`
Without waiting for explicit user prompting.

## Harness² Post-Flight Reflection
Upon concluding a major milestone, automatically reflect on execution traces to distill atomic lessons
into the Knowledge Registry as Fact Tuples (4 columns: What | Why | How | Scope).
Report a single-line summary in chat.

## Autonomous Auto-Learn (/optimize)
When refining code, resolving bugs, or running /optimize, persist verified insights to:
1. Workspace Rules (`<workspace>/.agents/rules/` or `<workspace>/AGENTS.md`)
2. Global Rules (`AGENTS.md` / `GEMINI.md` / `SKILL.md`)
3. Both (Dual-Write to `KNOWLEDGE_REGISTRY.md` + Workspace)
Without requiring explicit /learn calls.
