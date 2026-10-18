#!/usr/bin/env node
// One-time setup per sandbox: checks tools, installs the editing engine (Herk Edit Kit) into
// <workspace>/engine, and reports what is ready. Safe to re-run.
//
//   node setup.mjs [workspace]        (default workspace: /tmp/video-editor)
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

const root = resolve(process.argv[2] || '/tmp/video-editor');
const engine = join(root, 'engine');
const ENGINE_REPO = 'https://github.com/nateherkai/herk-edit-kit.git';
// Pinned so an upstream change cannot break a working setup. Bump deliberately.
const ENGINE_COMMIT = '10511e5af86fc47756ea89803b397422e2d89284';
// The engine's showcase and teaching-project media is about 380 MB and is not needed to edit.
const SPARSE = ['/*', '!/examples/showcase/', '!/video-projects/**/*.mp4', '!/video-projects/**/*.mov',
  '!/video-projects/**/*.webm', '!/video-projects/**/*.mp3', '!/video-projects/**/*.wav'];

const step = (msg) => console.log(`\n== ${msg}`);
const run = (cmd, args, cwd = root, quiet = false) => {
  const r = spawnSync(cmd, args, { cwd, stdio: quiet ? 'pipe' : 'inherit', encoding: 'utf8' });
  return !r.error && r.status === 0;
};
const fail = (msg) => { console.error(`\nSETUP STOPPED: ${msg}`); process.exit(1); };

mkdirSync(join(root, 'outbox'), { recursive: true });

step('Checking tools');
const missing = [];
if (Number(process.versions.node.split('.')[0]) < 22) missing.push('Node.js 22 or newer');
for (const [tool, flag] of [['git', '--version'], ['ffmpeg', '-version'], ['ffprobe', '-version']]) {
  if (!run(tool, [flag], root, true)) missing.push(tool);
}
if (missing.length) fail(`missing ${missing.join(', ')}. Install them, then run setup again.`);
console.log(`Node ${process.versions.node}, git, ffmpeg, ffprobe: OK`);

step(`Installing the editing engine (Herk Edit Kit) into ${engine}`);
if (!existsSync(join(engine, '.git'))) {
  if (!run('git', ['clone', '--quiet', '--no-checkout', '--depth', '1', '--filter=blob:limit=1m', ENGINE_REPO, engine])) {
    fail('could not download Herk Edit Kit. Check network access and run setup again.');
  }
  run('git', ['-C', engine, 'fetch', '--quiet', '--depth', '1', '--filter=blob:limit=1m', 'origin', ENGINE_COMMIT]);
  run('git', ['-C', engine, 'sparse-checkout', 'set', '--no-cone', ...SPARSE]);
  if (!run('git', ['-C', engine, '-c', 'advice.detachedHead=false', 'checkout', '--quiet', ENGINE_COMMIT])) {
    fail(`could not check out engine commit ${ENGINE_COMMIT}.`);
  }
} else {
  console.log('engine/ already installed.');
}

step('Installing engine packages (npm ci)');
if (!existsSync(join(engine, 'node_modules', 'hyperframes')) && !run('npm', ['ci', '--no-audit', '--no-fund'], engine)) {
  fail('npm ci failed in engine/. Read the error above.');
}
run('npm', ['run', 'setup', '--silent'], engine);

step('Transcription');
const whisper = run('python3', ['-c', 'import faster_whisper'], root, true);
console.log(`Local faster-whisper: ${whisper ? 'yes' : 'no (run: python3 -m pip install faster-whisper)'}`);

console.log(`\nSETUP COMPLETE${whisper ? '' : ' (transcription not installed yet)'}`);
console.log(`Workspace: ${root}\nEngine: ${engine}\nDrafts go to: ${join(root, 'outbox')}`);
