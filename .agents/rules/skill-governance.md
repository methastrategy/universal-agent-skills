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

## Knowledge registry
When the user asks to record a lesson or the work explicitly includes learning,
record verified findings in the owning repository's `KNOWLEDGE_REGISTRY.md`.
Use the existing format and include the source, revision when available, observed
result and scope. If the user asks for analysis alone, put the recommendation
in the report. Update rules only within the authorized implementation scope.
