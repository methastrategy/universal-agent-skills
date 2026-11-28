'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');

const repoRoot = path.resolve(__dirname, '..');
const rulesDir = path.join(repoRoot, 'rules');

test('Behavioral Suite — L1-L4 Universal Adaptive Response Protocol & Core Invariants', async (t) => {
  const agentsMd = fs.readFileSync(path.join(rulesDir, 'AGENTS.md'), 'utf8');
  const geminiMd = fs.readFileSync(path.join(rulesDir, 'GEMINI.md'), 'utf8');
  const codexMd = fs.readFileSync(path.join(rulesDir, 'CODEX.md'), 'utf8');
  const hermesMd = fs.readFileSync(path.join(rulesDir, 'HERMES.md'), 'utf8');

  await t.test('1. L1 direct answer: verifies 1-3 lines specification', () => {
    for (const [name, content] of Object.entries({ AGENTS: agentsMd, GEMINI: geminiMd, CODEX: codexMd, HERMES: hermesMd })) {
      assert.match(content, /L1\s*[-—]\s*Direct Answer\s*\(1[–-]3 lines\)/i, `${name} must define L1 (1-3 lines)`);
    }
  });

  await t.test('2. L2 standard task: verifies 5-15 lines specification', () => {
    for (const [name, content] of Object.entries({ AGENTS: agentsMd, GEMINI: geminiMd, CODEX: codexMd, HERMES: hermesMd })) {
      assert.match(content, /L2\s*[-—]\s*Standard Task\s*\(5[–-]15 lines\)/i, `${name} must define L2 (5-15 lines)`);
    }
  });

  await t.test('3. L3 complex engineering task: verifies adaptive budget & next action', () => {
    for (const [name, content] of Object.entries({ AGENTS: agentsMd, GEMINI: geminiMd, CODEX: codexMd, HERMES: hermesMd })) {
      assert.match(content, /L3\s*[-—]\s*Complex Task\s*\(Adaptive\)/i, `${name} must define L3 Adaptive`);
      assert.match(content, /Executive Summary/i, `${name} must require Executive Summary on major tasks`);
    }
  });

  await t.test('4. L4 full audit: verifies uncapped depth with evidence grounding', () => {
    for (const [name, content] of Object.entries({ AGENTS: agentsMd, GEMINI: geminiMd, CODEX: codexMd, HERMES: hermesMd })) {
      assert.match(content, /L4\s*[-—]\s*Deep Analysis/i, `${name} must define L4 Deep Analysis`);
      assert.match(content, /No artificial line caps|Unlimited by quality|Uncapped length/i, `${name} must uncap L4`);
    }
  });

  await t.test('5. Explicit user override of response length: rule as guideline not hard constraint', () => {
    assert.match(agentsMd, /Budget is a guideline, not a hard truncation limit/i);
    assert.match(geminiMd, /Budget is a guideline, not a hard truncation limit/i);
  });

  await t.test('6. Conflicting instructions: single recommended path enforced', () => {
    assert.match(agentsMd, /Single Recommended Path/i);
    assert.match(geminiMd, /Single Recommended Path/i);
    assert.match(codexMd, /Recommend ONE (best|primary) path/i);
  });

  await t.test('7. Unverified execution claims: empirical grounding & anti-hallucination', () => {
    for (const [name, content] of Object.entries({ AGENTS: agentsMd, GEMINI: geminiMd, CODEX: codexMd, HERMES: hermesMd })) {
      assert.match(content, /Verified facts|Empirical Grounding/i, `${name} must enforce empirical verification`);
      assert.match(content, /UNTRUSTED DATA/i, `${name} must enforce untrusted data boundary`);
    }
  });

  await t.test('8. Long-running task progress reporting: meaningful milestones allowed', () => {
    assert.match(agentsMd, /Meaningful Progress Reporting/i);
    assert.match(geminiMd, /Progress Reporting/i);
    assert.match(codexMd, /Progress Reporting/i);
    assert.match(hermesMd, /Progress Visibility/i);
  });

  await t.test('9. Memory preservation: USER.md & MEMORY.md strictly guarded', () => {
    const installPs1 = fs.readFileSync(path.join(repoRoot, 'install.ps1'), 'utf8');
    assert.match(installPs1, /\[MEMORY-ISOLATION\] USER\.md and MEMORY\.md are strictly preserved/i);
    assert.ok(!installPs1.match(/Copy-Rule\s+['"](USER|MEMORY)\.md['"]/i), 'Install script must never copy into USER.md or MEMORY.md');
  });

  await t.test('10. Installer rollback & backup functions present', () => {
    const installPs1 = fs.readFileSync(path.join(repoRoot, 'install.ps1'), 'utf8');
    assert.match(installPs1, /function Backup-File/i);
    assert.match(installPs1, /function Rollback-File/i);
    assert.match(installPs1, /function Show-Diff/i);
  });

  await t.test('11. Skill ceiling invariant (23 skills)', () => {
    const skillsDir = path.join(repoRoot, 'skills');
    const skills = fs.readdirSync(skillsDir, { withFileTypes: true })
      .filter(d => d.isDirectory() && fs.existsSync(path.join(skillsDir, d.name, 'SKILL.md')));
    assert.equal(skills.length, 23, 'Must have exactly 23 canonical skills');
  });
});
