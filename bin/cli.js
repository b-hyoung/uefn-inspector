#!/usr/bin/env node
/**
 * uefn-inspector installer.
 *
 *   npx uefn-inspector install     install slash skills + register the MCP server
 *   npx uefn-inspector skills      skills only
 *   npx uefn-inspector mcp         MCP registration only
 *   npx uefn-inspector doctor      check the environment
 *   npx uefn-inspector uninstall   remove what install added
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync, spawnSync } = require('child_process');

const PKG = path.resolve(__dirname, '..');
const KIT = path.join(PKG, 'game-loop-kit');
const SKILL_SRC = path.join(KIT, 'skills');
const SKILLS = ['uefn-game-loop', 'uefn-intake', 'uefn-level', 'uefn-review'];
const SKILL_DEST = process.env.CLAUDE_SKILLS_DIR || path.join(os.homedir(), '.claude', 'skills');
const SERVER = path.join(PKG, 'mcp_server.py');

const c = {
  ok: (s) => console.log(`  \x1b[32m✓\x1b[0m ${s}`),
  warn: (s) => console.log(`  \x1b[33m!\x1b[0m ${s}`),
  err: (s) => console.log(`  \x1b[31m✗\x1b[0m ${s}`),
  head: (s) => console.log(`\n\x1b[1m${s}\x1b[0m`),
};

function findPython() {
  if (process.env.UEFN_PYTHON) return process.env.UEFN_PYTHON;
  const candidates = process.platform === 'win32'
    ? ['python', 'py', 'python3']
    : ['python3', 'python'];
  for (const cmd of candidates) {
    const r = spawnSync(cmd, ['-c', 'import sys; print(sys.version_info[0]*100+sys.version_info[1])'],
      { encoding: 'utf8' });
    if (r.status === 0 && parseInt(r.stdout.trim(), 10) >= 311) {
      const real = spawnSync(cmd, ['-c', 'import sys; print(sys.executable)'], { encoding: 'utf8' });
      return (real.status === 0 ? real.stdout.trim() : cmd);
    }
  }
  return null;
}

function installSkills() {
  c.head('Installing slash skills');
  fs.mkdirSync(SKILL_DEST, { recursive: true });
  for (const name of SKILLS) {
    const src = path.join(SKILL_SRC, name, 'SKILL.md');
    if (!fs.existsSync(src)) { c.err(`missing ${name}`); continue; }
    // point the skill at THIS installation's kit
    const body = fs.readFileSync(src, 'utf8')
      .replace(/^\*\*KIT\*\* = .*$/m, `**KIT** = \`${KIT}\``);
    fs.mkdirSync(path.join(SKILL_DEST, name), { recursive: true });
    fs.writeFileSync(path.join(SKILL_DEST, name, 'SKILL.md'), body);
    c.ok(`/${name}`);
  }
  console.log(`  → ${SKILL_DEST}`);
}

function ensureMcpDep(py) {
  const r = spawnSync(py, ['-c', 'import mcp'], { encoding: 'utf8' });
  if (r.status === 0) return true;
  c.warn('python package "mcp" missing — installing');
  const i = spawnSync(py, ['-m', 'pip', 'install', '-q', 'mcp'], { stdio: 'inherit' });
  return i.status === 0;
}

function registerMcp() {
  c.head('Registering MCP server');
  const py = findPython();
  if (!py) { c.err('Python 3.11+ not found (set UEFN_PYTHON=<path>)'); return; }
  c.ok(`python: ${py}`);
  if (!ensureMcpDep(py)) { c.err('could not install the "mcp" package'); return; }
  try {
    execFileSync('claude', ['mcp', 'add', 'uefn-inspector', '-s', 'user', '--', py, SERVER],
      { stdio: 'pipe' });
    c.ok('registered as "uefn-inspector" (user scope)');
  } catch (e) {
    const msg = String(e.stderr || e.message);
    if (/already exists/i.test(msg)) c.ok('already registered');
    else {
      c.warn('could not run `claude mcp add` — register manually:');
      console.log(`      claude mcp add uefn-inspector -s user -- "${py}" "${SERVER}"`);
    }
  }
}

function doctor() {
  c.head('Environment');
  const py = findPython();
  py ? c.ok(`Python 3.11+: ${py}`) : c.err('Python 3.11+ not found');
  if (py) {
    const m = spawnSync(py, ['-c', 'import mcp'], { encoding: 'utf8' });
    m.status === 0 ? c.ok('python package: mcp') : c.warn('python package "mcp" not installed');
  }
  try {
    execFileSync('claude', ['--version'], { stdio: 'pipe' });
    c.ok('claude CLI');
  } catch { c.warn('claude CLI not found (skills still work; MCP needs manual registration)'); }
  fs.existsSync(path.join(SKILL_DEST, 'uefn-game-loop', 'SKILL.md'))
    ? c.ok(`skills installed: ${SKILL_DEST}`)
    : c.warn('skills not installed yet');
  fs.existsSync(path.join(PKG, 'data', 'engine_device_catalog.json'))
    ? c.ok('engine device catalog present')
    : c.warn('engine catalog absent — `engine_devices` disabled (see cue4parse_cli/README.md)');
}

function uninstall() {
  c.head('Uninstalling');
  for (const name of SKILLS) {
    const dir = path.join(SKILL_DEST, name);
    if (fs.existsSync(dir)) { fs.rmSync(dir, { recursive: true, force: true }); c.ok(`removed /${name}`); }
  }
  try {
    execFileSync('claude', ['mcp', 'remove', 'uefn-inspector'], { stdio: 'pipe' });
    c.ok('unregistered MCP server');
  } catch { c.warn('MCP server not registered (or claude CLI unavailable)'); }
}

function usage() {
  console.log(`
uefn-inspector — offline UEFN analyzer + Claude Code skills

  npx uefn-inspector install     skills + MCP server   (recommended)
  npx uefn-inspector skills      slash skills only
  npx uefn-inspector mcp         MCP registration only
  npx uefn-inspector doctor      check the environment
  npx uefn-inspector uninstall   undo install
`);
}

const cmd = (process.argv[2] || 'install').toLowerCase();
if (['-h', '--help', 'help'].includes(cmd)) { usage(); process.exit(0); }

switch (cmd) {
  case 'install': installSkills(); registerMcp(); break;
  case 'skills': installSkills(); break;
  case 'mcp': registerMcp(); break;
  case 'doctor': doctor(); break;
  case 'uninstall': uninstall(); break;
  default: usage(); process.exit(1);
}

if (['install', 'skills', 'mcp'].includes(cmd)) {
  console.log('\n\x1b[1mNext:\x1b[0m restart Claude Code, then run \x1b[36m/uefn-game-loop\x1b[0m');
  console.log('      (MCP tools appear after `/mcp` reconnect or a restart)\n');
}
