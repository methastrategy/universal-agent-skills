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
Reference `rules/CLAUDE.md` or copy it directly into your project root's `CLAUDE.md`. Skills reside in `.claude/skills/`.

## 4. OpenAI Codex / o3 / GPT (AGENTS.md)
Deploy `rules/CODEX.md` as `AGENTS.md` in your project root or workspace. Skills reside in `.codex/skills/`.

## 5. Hermes (Discord Agent)
Hermes loads `rules/HERMES.md` as `AGENTS.md` context when cwd is `~`. For project-specific work, drop an `AGENTS.md` in the repo root or place rules in `.agents/rules/`.

## 6. OpenClaw & Generic OpenAI-Compatible Agents
Place skills in `.agents/skills/` and copy `rules/OPENCLAW.md` into `.agents/rules/AGENTS.md`.

## 7. LangGraph / n8n / AutoGen Orchestrators
Each skill in `skills/<name>/SKILL.md` is self-contained and can be treated as a specialized Subagent System Prompt:
- **Triaging Agent:** Uses `skills/jev/SKILL.md`
- **Architect Agent:** Uses `skills/architect/SKILL.md`
- **Coder Agent:** Uses `skills/build/SKILL.md`
- **Security & QA Agent:** Uses `skills/review/SKILL.md`
- **Debugger Agent:** Uses `skills/debug/SKILL.md`
- **Quant / Finance Agent:** Uses `skills/quant/SKILL.md`
- **Circuit Breaker Gate:** Uses `skills/wait-what/SKILL.md`
