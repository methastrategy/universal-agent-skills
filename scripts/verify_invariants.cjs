#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const skillsDir = path.join(repoRoot, 'skills');

let hasViolations = false;
console.log('[*] Running Universal Agent Skills Invariant Gate...');

// 1. Check Skill Count (Ceiling <= 23)
if (!fs.existsSync(skillsDir)) {
  console.error(`[ERROR] Skills directory not found: ${skillsDir}`);
  process.exit(1);
}

const skills = fs.readdirSync(skillsDir, { withFileTypes: true })
  .filter(d => d.isDirectory() && fs.existsSync(path.join(skillsDir, d.name, 'SKILL.md')));

if (skills.length > 23) {
  console.error(`[FAIL] Skill ceiling violated: Expected at most 23 skills, found ${skills.length}!`);
  hasViolations = true;
} else {
  console.log(`[PASS] Skill count invariant: ${skills.length} / 23 (Ceiling respected)`);
}

// 2. Check Skill Description Length (<= 220 chars)
let descErrors = 0;
for (const s of skills) {
  const filePath = path.join(skillsDir, s.name, 'SKILL.md');
  const content = fs.readFileSync(filePath, 'utf8');
  const match = content.match(/^description:\s*["\']?([^\r\n"\']+)/m);

  if (match) {
    const desc = match[1].trim();
    if (desc.length > 220) {
      console.error(`[FAIL] Description too long in '${s.name}': ${desc.length} chars (Limit: 220)`);
      descErrors++;
    }
  } else {
    console.error(`[FAIL] Missing description in '${s.name}/SKILL.md'`);
    descErrors++;
  }
}

if (descErrors > 0) {
  hasViolations = true;
} else {
  console.log(`[PASS] Description length invariant: 0 violations across ${skills.length} skills`);
}

// 3. Check Dangling References
let danglingErrors = 0;
for (const s of skills) {
  const filePath = path.join(skillsDir, s.name, 'SKILL.md');
  const content = fs.readFileSync(filePath, 'utf8');
  const refMatches = [...content.matchAll(/references\/([a-zA-Z0-9_\-\.]+\.md)/g)];

  for (const m of refMatches) {
    const refFile = path.join(skillsDir, s.name, 'references', m[1]);
    if (!fs.existsSync(refFile)) {
      console.error(`[FAIL] Dangling reference in '${s.name}/SKILL.md' -> 'references/${m[1]}' not found!`);
      danglingErrors++;
    }
  }
}

if (danglingErrors > 0) {
  hasViolations = true;
} else {
  console.log(`[PASS] Reference integrity invariant: 0 dangling references`);
}

if (hasViolations) {
  console.error('\n🚨 CI BLOCKED: Invariant check failed! Fix violations.');
  process.exit(1);
} else {
  console.log('✅ CI PASSED: All 3 Invariants verified successfully.\n');
}
