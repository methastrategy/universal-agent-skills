#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const skillsDir = path.join(repoRoot, 'skills');

let violations = 0;
const log = (tag, msg) => console.log(`[${tag}] ${msg}`);
const fail = (msg) => { console.error(`[FAIL] ${msg}`); violations++; };

console.log('[*] Universal Agent Skills — Invariant Verification Gate v2');
console.log(`[*] Repo: ${repoRoot}\n`);

// ─── Gate 1: Skills directory exists ──────────────────────────────────────
if (!fs.existsSync(skillsDir)) {
  console.error(`[ERROR] Skills directory not found: ${skillsDir}`);
  process.exit(1);
}

const skills = fs.readdirSync(skillsDir, { withFileTypes: true })
  .filter(d => d.isDirectory() && fs.existsSync(path.join(skillsDir, d.name, 'SKILL.md')));

// ─── Gate 2: Skill count ceiling (≤ 23) ───────────────────────────────────
if (skills.length > 23) {
  fail(`Skill ceiling violated: ${skills.length} found (max 23)`);
} else {
  log('PASS', `Skill count: ${skills.length} / 23`);
}

// ─── Gate 3: Description length (≤ 220 chars) ─────────────────────────────
let descErrors = 0;
for (const s of skills) {
  const filePath = path.join(skillsDir, s.name, 'SKILL.md');
  const content = fs.readFileSync(filePath, 'utf8');
  // Match both single-line and block-scalar (>) descriptions
  const match = content.match(/^description:\s*["']?([^\r\n"']+)/m)
    || content.match(/^description:\s*>\-?\n\s+(.+)/m);
  if (match) {
    const desc = match[1].trim();
    if (desc.length > 220) {
      fail(`Description too long in '${s.name}': ${desc.length} chars (limit 220)`);
      descErrors++;
    }
  } else {
    fail(`Missing or unparseable description in '${s.name}/SKILL.md'`);
    descErrors++;
  }
}
if (descErrors === 0) log('PASS', `Description length: 0 violations across ${skills.length} skills`);

// ─── Gate 4: SKILL.md body size (≤ 6000 chars recommended, warn at > 8000) ─
let sizeWarnings = 0;
for (const s of skills) {
  const filePath = path.join(skillsDir, s.name, 'SKILL.md');
  const content = fs.readFileSync(filePath, 'utf8');
  if (content.length > 8000) {
    console.warn(`[WARN] SKILL.md too large in '${s.name}': ${content.length} chars (recommended ≤ 6000, hard limit 8000 — move excess to references/)`);
    sizeWarnings++;
  }
}
if (sizeWarnings === 0) log('PASS', `SKILL.md body sizes: all within recommended 8000-char ceiling`);
else log('WARN', `${sizeWarnings} skills exceed 8000 chars — consider offloading to references/`);

// ─── Gate 5: Dangling references ──────────────────────────────────────────
let danglingErrors = 0;
for (const s of skills) {
  const filePath = path.join(skillsDir, s.name, 'SKILL.md');
  const content = fs.readFileSync(filePath, 'utf8');
  const refMatches = [...content.matchAll(/references\/([a-zA-Z0-9_\-\.]+\.md)/g)];
  for (const m of refMatches) {
    const refFile = path.join(skillsDir, s.name, 'references', m[1]);
    if (!fs.existsSync(refFile)) {
      fail(`Dangling reference in '${s.name}/SKILL.md' -> 'references/${m[1]}' not found`);
      danglingErrors++;
    }
  }
}
if (danglingErrors === 0) log('PASS', `Reference integrity: 0 dangling references`);

// ─── Gate 6: JSON file validity ───────────────────────────────────────────
let jsonErrors = 0;
const jsonFiles = [];
function findJsonFiles(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
      findJsonFiles(full);
    } else if (entry.isFile() && entry.name.endsWith('.json')) {
      jsonFiles.push(full);
    }
  }
}
findJsonFiles(repoRoot);

for (const jf of jsonFiles) {
  try {
    JSON.parse(fs.readFileSync(jf, 'utf8'));
  } catch (e) {
    fail(`Invalid JSON: ${path.relative(repoRoot, jf)} — ${e.message}`);
    jsonErrors++;
  }
}
if (jsonErrors === 0) log('PASS', `JSON validity: all ${jsonFiles.length} JSON files are valid`);

// ─── Gate 7: Required AGENTS.md & GEMINI.md rules files ───────────────────
const requiredRules = ['AGENTS.md', 'GEMINI.md'];
for (const rf of requiredRules) {
  if (!fs.existsSync(path.join(repoRoot, 'rules', rf))) {
    fail(`Required rules file missing: rules/${rf}`);
  }
}
if (violations === 0) log('PASS', `Rules files: all required files present`);

// ─── Gate 8: Multi-agent support files ────────────────────────────────────
const multiAgentFiles = [
  'rules/CLAUDE.md',
  'rules/CODEX.md',
  'rules/HERMES.md',
  'rules/OPENCLAW.md',
  'plugin.json',
];
let multiAgentMissing = 0;
for (const mf of multiAgentFiles) {
  if (!fs.existsSync(path.join(repoRoot, mf))) {
    console.warn(`[WARN] Multi-agent support file missing: ${mf} (run installer to generate)`);
    multiAgentMissing++;
  }
}
if (multiAgentMissing === 0) log('PASS', `Multi-agent support: all compatibility files present`);

// ─── Final Result ──────────────────────────────────────────────────────────
console.log('');
if (violations > 0) {
  console.error(`🚨 CI BLOCKED: ${violations} invariant violation(s). Fix all [FAIL] items above.`);
  process.exit(1);
} else {
  console.log(`✅ CI PASSED: All invariants verified (${sizeWarnings} size warnings — see [WARN] above).\n`);
}
