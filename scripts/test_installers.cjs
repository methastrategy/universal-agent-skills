'use strict';

const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { createHash } = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { test } = require('node:test');

const root = path.resolve(__dirname, '..');
const shell = process.argv[2];
assert.ok(['powershell', 'bash'].includes(shell), 'Use powershell or bash');
const script = shell === 'powershell' ? 'install.ps1' : 'install.sh';
const command = shell === 'powershell' ? 'pwsh' : (process.env.INSTALL_TEST_BASH || 'bash');

const targetPaths = {
  codex: ['project', '.agents/skills', 'AGENTS.md'],
  claude: ['project', '.claude/skills', 'CLAUDE.md', '.claude/AGENTS.md'],
  cursor: ['project', '.cursor/skills', '.cursorrules'],
  windsurf: ['project', '.windsurf/skills', '.windsurfrules'],
  openclaw: ['project', '.agents/skills', '.agents/AGENTS.md', '.agents/rules/AGENTS.md'],
  antigravity: ['home', '.gemini/config/skills', '.gemini/AGENTS.md', '.gemini/GEMINI.md',
    '.gemini/CLAUDE.md', '.gemini/CODEX.md', '.gemini/HERMES.md', '.gemini/OPENCLAW.md'],
};

function write(rootPath, relative, text) {
  const file = path.join(rootPath, relative);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, text);
}

function snapshot(dir) {
  return Object.fromEntries(fs.readdirSync(dir, { recursive: true }).sort().map(relative => {
    const file = path.join(dir, relative);
    const info = fs.lstatSync(file);
    const value = info.isSymbolicLink() ? fs.readlinkSync(file)
      : info.isDirectory() ? 'directory' : createHash('sha256').update(fs.readFileSync(file)).digest('hex');
    return [relative, value];
  }));
}

function fixture(t) {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), 'universal skills test '));
  t.after(() => fs.rmSync(base, { recursive: true, force: true }));
  const dirs = Object.fromEntries(['source repo', 'project', 'home', 'runtime'].map(name => {
    const dir = path.join(base, name);
    fs.mkdirSync(dir);
    return [name === 'source repo' ? 'source' : name, dir];
  }));
  fs.copyFileSync(path.join(root, script), path.join(dirs.source, script));
  fs.cpSync(path.join(root, 'rules'), path.join(dirs.source, 'rules'), { recursive: true });
  write(dirs.source, 'skills/alpha/SKILL.md', '# Alpha\n');
  write(dirs.source, 'skills/alpha/references/guide.md', 'Read this reference.\n');
  write(dirs.source, 'skills/beta/SKILL.md', '# Beta\n');
  write(dirs.source, 'skills/not-a-skill/readme.md', 'Should be ignored.\n');
  return dirs;
}

function run(dirs, target, dryRun = false, extra = []) {
  const source = path.join(dirs.source, script).split(path.sep).join('/');
  const env = { ...process.env, HOME: dirs.home, USERPROFILE: dirs.home };
  let args = [source, target, ...(dryRun ? ['--dry-run'] : []), ...extra];
  if (shell === 'powershell') {
    // Isolate PowerShell startup files from the home directory the installer sees.
    Object.assign(env, {
      HOME: dirs.runtime, USERPROFILE: dirs.runtime, INSTALL_TEST_HOME: dirs.home,
      INSTALL_TEST_SCRIPT: source, INSTALL_TEST_TARGET: target, POWERSHELL_TELEMETRY_OPTOUT: '1',
    });
    const invocation = '$env:USERPROFILE = $env:INSTALL_TEST_HOME\n' +
      '& $env:INSTALL_TEST_SCRIPT -Target $env:INSTALL_TEST_TARGET' +
      (dryRun ? ' -DryRun' : '') + (extra.length ? ' -WrongFlag' : '');
    args = ['-NoProfile', '-NonInteractive', '-Command', invocation];
  }
  const result = spawnSync(command, args, { cwd: dirs.project, env, encoding: 'utf8' });
  if (result.error) throw result.error;
  return { status: result.status, output: result.stdout + result.stderr };
}

function success(result) {
  assert.equal(result.status, 0, result.output);
  return result.output;
}

for (const [target, [scope, destination, ...rules]] of Object.entries(targetPaths)) {
  test(`${target} preserves custom rules and skills and installs missing files`, t => {
    const dirs = fixture(t);
    for (const rule of rules) write(dirs[scope], rule, 'user rules\n');
    write(dirs[scope], `${destination}/alpha/SKILL.md`, 'user skill\n');
    const prior = snapshot(dirs[scope]);
    const planned = success(run(dirs, target, true));
    assert.deepEqual(snapshot(dirs[scope]), prior);
    assert.match(planned, /\[DRY\] would install: .*beta/i);
    assert.match(planned, /\[KEEP\].*alpha/);
    const installed = success(run(dirs, target));
    assert.match(installed, /\[INSTALL\].*beta/);
    assert.match(installed, /2 skills.*1 installed.*1 kept/);
    const after = snapshot(dirs[scope]);
    for (const [file, hash] of Object.entries(prior)) assert.equal(after[file], hash, file);
    assert.ok(fs.existsSync(path.join(dirs[scope], destination, 'beta/SKILL.md')));
    assert.ok(!fs.existsSync(path.join(dirs[scope], destination, 'alpha/references')));
    assert.ok(!fs.existsSync(path.join(dirs[scope], destination, 'not-a-skill')));
    assert.match(success(run(dirs, target)), /2 skills.*0 installed.*1 present.*1 kept/);
    assert.deepEqual(snapshot(dirs[scope]), after);
  });
}

test('all installs missing rules and shares the Codex and OpenClaw skill destination', t => {
  const dirs = fixture(t);
  write(dirs.project, '.codex/skills/alpha/SKILL.md', 'old layout\n');
  const before = [snapshot(dirs.project), snapshot(dirs.home)];
  const planned = success(run(dirs, 'all', true));
  assert.deepEqual([snapshot(dirs.project), snapshot(dirs.home)], before);
  const installed = success(run(dirs, 'all'));
  assert.match(installed, /\.codex[/\\]skills/);
  assert.equal((installed.match(/^.*2 skills.*2 installed.*$/gm) || []).length, 5);
  const planPaths = [...planned.matchAll(/^\s*\[DRY\] would install: (.+)$/gmi)].map(match => match[1]);
  const installedPaths = [...installed.matchAll(/^\s*\[INSTALL\] (.+)$/gm)].map(match => match[1]);
  assert.ok(planPaths.length > 0);
  assert.deepEqual(planPaths.sort(), installedPaths.sort());
  for (const [scope, destination, ...rules] of Object.values(targetPaths)) {
    assert.ok(fs.existsSync(path.join(dirs[scope], destination, 'alpha/references/guide.md')));
    for (const rule of rules) assert.ok(fs.existsSync(path.join(dirs[scope], rule)), rule);
  }
  assert.equal(fs.readFileSync(path.join(dirs.project, '.codex/skills/alpha/SKILL.md'), 'utf8'), 'old layout\n');
  const after = [snapshot(dirs.project), snapshot(dirs.home)];
  success(run(dirs, 'all'));
  assert.deepEqual([snapshot(dirs.project), snapshot(dirs.home)], after);
});

test('wrong destination type fails with the destination and preserves the original', t => {
  const dirs = fixture(t);
  write(dirs.project, '.agents', 'existing file\n');
  const before = snapshot(dirs.project);
  for (const dryRun of [true, false]) {
    const result = run(dirs, 'codex', dryRun);
    assert.notEqual(result.status, 0, result.output);
    assert.match(result.output, /\.agents/);
    assert.deepEqual(snapshot(dirs.project), before);
  }
});

test('a destination link is preserved without writing through it', t => {
  const dirs = fixture(t);
  write(dirs.home, 'external.md', 'external file\n');
  try {
    fs.symlinkSync(path.join(dirs.home, 'external.md'), path.join(dirs.project, 'AGENTS.md'), 'file');
  } catch (error) {
    if (error.code === 'EPERM') return t.skip('File symlinks require additional privileges');
    throw error;
  }
  const prior = snapshot(dirs.home);
  assert.match(success(run(dirs, 'codex')), /\[KEEP\].*AGENTS\.md/);
  assert.ok(fs.lstatSync(path.join(dirs.project, 'AGENTS.md')).isSymbolicLink());
  assert.deepEqual(snapshot(dirs.home), prior);
});

test('a linked destination parent fails before writing through it', t => {
  const dirs = fixture(t);
  fs.symlinkSync(dirs.home, path.join(dirs.project, '.agents'), 'junction');
  const before = snapshot(dirs.project);
  const result = run(dirs, 'codex');
  assert.notEqual(result.status, 0, result.output);
  assert.match(result.output, /\.agents/);
  assert.deepEqual(snapshot(dirs.project), before);
  assert.deepEqual(snapshot(dirs.home), {});
});

test('a failed copy leaves no partial skill and a retry succeeds', {
  skip: process.platform === 'win32' || process.getuid?.() === 0,
}, t => {
  const dirs = fixture(t);
  const file = path.join(dirs.source, 'skills/alpha/references/guide.md');
  fs.chmodSync(file, 0o000);
  try {
    const result = run(dirs, 'codex');
    assert.notEqual(result.status, 0, result.output);
    assert.match(result.output, /\.agents\/skills\/alpha/);
    assert.deepEqual(fs.readdirSync(path.join(dirs.project, '.agents/skills')), []);
  } finally {
    fs.chmodSync(file, 0o644);
  }
  success(run(dirs, 'codex'));
  assert.ok(fs.existsSync(path.join(dirs.project, '.agents/skills/alpha/references/guide.md')));
});

test('invalid arguments leave both destinations untouched', t => {
  const dirs = fixture(t);
  assert.notEqual(run(dirs, 'wrong-target').status, 0);
  assert.notEqual(run(dirs, 'codex', false, ['--wrong-flag']).status, 0);
  assert.deepEqual(snapshot(dirs.project), {});
  assert.deepEqual(snapshot(dirs.home), {});
});
