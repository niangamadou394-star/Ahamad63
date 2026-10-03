#!/usr/bin/env node
/* ==========================================================================
   Rendu image par image → MP4 (H.264, 1080×1920, 30 i/s) + bande-son.
   Usage :
     node render.mjs                 # tous les épisodes
     node render.mjs 1 4 7           # épisodes choisis
     node render.mjs --stills 1      # captures de contrôle (PNG)
   Requiert : Playwright (Chromium) et ffmpeg.
   ========================================================================== */
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { mkdirSync, existsSync, rmSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import os from 'node:os';
import { writeSoundtrack } from './sound.mjs';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(path.join(path.dirname(process.execPath), '../lib/node_modules/playwright'))); }

const DIR = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(DIR, 'exports');
const FPS = 30;
const args = process.argv.slice(2);
const stills = args.includes('--stills');
let eps = args.filter(a => /^\d+$/.test(a)).map(Number);
if (!eps.length) eps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
mkdirSync(OUT, { recursive: true });

const pad = n => String(n).padStart(2, '0');

async function open(browser, n) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error(`[ép.${n}]`, e.message));
  await page.goto(pathToFileURL(path.join(DIR, 'player.html')).href + `?ep=${n}&capture`);
  await page.waitForFunction(() => window.__ready === true);
  return page;
}

const seek = (page, t) => page.evaluate(t => new Promise(r => { window.__seek(t); requestAnimationFrame(() => r()); }), t);

function run(cmd, argv, opts = {}) {
  return new Promise((res, rej) => {
    const p = spawn(cmd, argv, { stdio: ['pipe', 'ignore', 'inherit'], ...opts });
    p.on('error', rej);
    p.on('close', c => (c === 0 ? res() : rej(new Error(`${cmd} → code ${c}`))));
    if (opts.feed) opts.feed(p.stdin);
  });
}

async function renderEpisode(browser, n) {
  const page = await open(browser, n);
  const { duration, cues, starts } = await page.evaluate(() => ({ duration: window.__duration, cues: window.__cues, starts: window.__starts }));
  const name = `ep${pad(n)}`;

  if (stills) {
    const dir = path.join(OUT, 'stills');
    mkdirSync(dir, { recursive: true });
    for (let i = 0; i < starts.length; i++) {
      const end = i + 1 < starts.length ? starts[i + 1] : duration;
      const t = end - .7;
      await seek(page, t);
      await page.screenshot({ path: path.join(dir, `${name}-s${i + 1}.png`) });
    }
    console.log(`✓ ${name} : ${starts.length} captures (durée ${duration.toFixed(1)} s)`);
    await page.close();
    return;
  }

  // Couverture (fin de l'accroche)
  await seek(page, Math.min(starts[1] ?? 3, 4) - .45);
  await page.screenshot({ path: path.join(OUT, `${name}-cover.jpg`), type: 'jpeg', quality: 92 });

  // Bande-son
  const wav = path.join(os.tmpdir(), `${name}-${process.pid}.wav`);
  writeSoundtrack(wav, duration, cues);

  // Vidéo
  const frames = Math.round(duration * FPS);
  const mp4 = path.join(OUT, `${name}.mp4`);
  const t0 = Date.now();
  await run('ffmpeg', [
    '-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', wav,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-r', String(FPS), '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', mp4,
  ], {
    feed: async stdin => {
      for (let f = 0; f < frames; f++) {
        await seek(page, f / FPS);
        const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
        if (!stdin.write(buf)) await new Promise(r => stdin.once('drain', r));
        if (f % 150 === 0) process.stdout.write(`  ${name} ${Math.round((f / frames) * 100)}%\n`);
      }
      stdin.end();
    },
  });
  rmSync(wav, { force: true });
  console.log(`✓ ${name}.mp4 — ${duration.toFixed(1)} s, ${frames} images, ${((Date.now() - t0) / 1000).toFixed(0)} s de rendu`);
  await page.close();
}

const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-lcd-text'] });
const workers = Math.max(1, Math.min(stills ? 1 : 3, eps.length));
const queue = [...eps];
await Promise.all(Array.from({ length: workers }, async () => {
  while (queue.length) await renderEpisode(browser, queue.shift());
}));
await browser.close();
