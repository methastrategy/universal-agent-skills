# Agentic Workflows & Multi-Agent Integration

How to adapt these 22 skills into various agent frameworks:

---

## 1. Antigravity 2.0 / Gemini CLI
Copy the `skills/` folder into your workspace `.gemini/config/skills/` or home directory `~/.gemini/config/skills/`.

## 2. Cursor IDE (.cursorrules)
Add the following to your `.cursorrules` or `.cursor/rules/`:
```markdown
# Agent Directives
Always enforce the rules defined in `rules/AGENTS.md`.
When requested to debug, architect, build, or review code, activate the respective skill protocol from `skills/<name>/SKILL.md`.
```

## 3. Claude Code (CLAUDE.md)
Reference `rules/AGENTS.md` directly in your project root's `CLAUDE.md`.

## 4. LangGraph / n8n / AutoGen Orchestrators
Each skill in `skills/<name>/SKILL.md` is self-contained and can be treated as a specialized Subagent System Prompt:
- **Triaging Agent:** Uses `skills/jev/SKILL.md`
- **Architect Agent:** Uses `skills/architect/SKILL.md`
- **Coder Agent:** Uses `skills/build/SKILL.md`
- **Security & QA Agent:** Uses `skills/review/SKILL.md`
- **Debugger Agent:** Uses `skills/debug/SKILL.md`
