#!/usr/bin/env node
/* Export des carrousels LinkedIn : un PDF par épisode (à publier comme « document »)
   + les slides en PNG.  Usage : node render.mjs [n° d'épisodes…] */
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(path.join(path.dirname(process.execPath), '../lib/node_modules/playwright'))); }

const DIR = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(DIR, 'exports');
const SLUGS = { 1: 'idee', 2: 'valider', 3: 'cible', 4: 'offre', 5: 'chiffres', 6: 'mvp', 7: 'statut-financement', 8: 'marque', 9: 'pre-lancement', 10: 'lancement' };
let eps = process.argv.slice(2).filter(a => /^\d+$/.test(a)).map(Number);
if (!eps.length) eps = Object.keys(SLUGS).map(Number);
mkdirSync(path.join(OUT, 'png'), { recursive: true });

const pad = n => String(n).padStart(2, '0');
const browser = await chromium.launch();
for (const n of eps) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  page.on('pageerror', e => console.error(`[${n}]`, e.message));
  await page.goto(pathToFileURL(path.join(DIR, 'carousel.html')).href + `?ep=${n}&print`);
  await page.waitForFunction(() => window.__ready === true);
  const name = `carrousel-${pad(n)}-${SLUGS[n]}`;
  await page.pdf({ path: path.join(OUT, `${name}.pdf`), width: '1080px', height: '1350px', printBackground: true, pageRanges: '' });
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    await slides[i].screenshot({ path: path.join(OUT, 'png', `${name}-${pad(i + 1)}.png`) });
  }
  console.log(`✓ ${name}.pdf — ${slides.length} slides`);
  await page.close();
}
await browser.close();
