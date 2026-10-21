// integrity.mjs <siteDir> <outDir>
// Loads the page in mobile emulation and checks that nothing the visitor relies on broke.
import chromium from '@sparticuz/chromium';
import puppeteer from 'puppeteer-core';
import { FLAGS } from './chrome_flags.mjs';
import { spawn } from 'node:child_process';
import http from 'node:http';
import zlib from 'node:zlib';
import { writeFileSync, mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

const dir = resolve(process.argv[2]);
const outDir = resolve(process.argv[3] || dir + '-integrity');
mkdirSync(outDir, { recursive: true });
const port = 9100 + Math.floor(Math.random() * 800);
const srv = spawn(process.execPath, [join(dir, 'server.mjs'), String(port)], { cwd: dir, stdio: ['ignore', 'pipe', 'pipe'] });
await new Promise(ok => { srv.stdout.on('data', ok); setTimeout(ok, 3000); });

function head(path) {
  return new Promise(res => {
    const req = http.get({ host: 'localhost', port, path, headers: { 'Accept-Encoding': 'gzip, deflate, br' } }, r => {
      r.resume(); r.on('end', () => res({ status: r.statusCode, enc: r.headers['content-encoding'] || '', cache: r.headers['cache-control'] || '' }));
    });
    req.on('error', () => res({ status: 0 }));
  });
}

const browser = await puppeteer.launch({ executablePath: await chromium.executablePath(), args: FLAGS, headless: true });
const page = await browser.newPage();
await page.emulate({ viewport: { width: 412, height: 823, deviceScaleFactor: 1.75, isMobile: true, hasTouch: true },
  userAgent: 'Mozilla/5.0 (Linux; Android 11; moto g power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0 Mobile Safari/537.36' });
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message.slice(0, 160)));
page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 160)); });
await page.evaluateOnNewDocument(() => {
  window.__lt = 0;
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt += e.duration; }).observe({ type: 'longtask', buffered: true }); } catch {}
});
const checks = {};
let ok = true;
try {
  await page.goto(`http://localhost:${port}/`, { waitUntil: 'load', timeout: 60000 });
  await new Promise(r => setTimeout(r, 2500));
  const top = await page.evaluate(() => {
    const h1 = document.querySelector('h1')?.textContent.trim();
    const imgs = [...document.querySelectorAll('img')];
    const hero = imgs.find(i => /hero/i.test(i.currentSrc || i.src) || i.closest('#hero-media, .hero'));
    const hr = hero?.getBoundingClientRect();
    return {
      h1, heroSrc: hero ? (hero.currentSrc || hero.src).split('/').pop() : null,
      heroLoaded: !!(hero && hero.complete && hero.naturalWidth >= 300), heroPath: hero ? new URL(hero.currentSrc || hero.src).pathname : null, heroTop: hr ? Math.round(hr.top + scrollY) : null,
      heroRatio: hero && hero.naturalWidth ? +(hero.naturalWidth / hero.naturalHeight).toFixed(2) : null,
      promo: document.body.innerText.includes('Trailmark AI summaries are live'),
      h1Font: getComputedStyle(document.querySelector('h1')).fontFamily,
      brandLoaded: [...document.fonts].some(f => /Brand/.test(f.family) && f.status === 'loaded'),
      longTaskMs: Math.round(window.__lt || 0),
    };
  });
  // scroll to load lazy images
  for (let y = 0; y < 8000; y += 600) { await page.evaluate(v => scrollTo(0, v), y); await new Promise(r => setTimeout(r, 120)); }
  await new Promise(r => setTimeout(r, 1500));
  const rest = await page.evaluate(() => {
    const feats = [...document.querySelectorAll('.feature')];
    const featOk = feats.filter(f => { const i = f.querySelector('img'); return i && i.complete && i.naturalWidth > 0; }).length;
    const featTitles = feats.map(f => f.querySelector('h3')?.textContent.trim());
    const logos = [...document.querySelectorAll('.logos img')].filter(i => i.complete && i.naturalWidth > 0).length;
    const t = document.body.innerText;
    return { features: feats.length, featuresLoaded: featOk, featTitles, logos,
      testimonial: t.includes('post-launch bug reports in half'), signup: !!document.querySelector('input[type=email]'),
      footer: t.includes('2026 Trailmark'), searchBox: !!document.querySelector('input[type=search], #search') };
  });
  // search must still work
  const sel = await page.$('#search') ? '#search' : 'input[type=search]';
  let searchOk = false;
  if (await page.$(sel)) {
    await page.focus(sel);
    await page.type(sel, 'pricing', { delay: 20 });
    await new Promise(r => setTimeout(r, 2500));
    searchOk = await page.evaluate(() => /[1-9]\d* results/.test(document.getElementById('search-hits')?.textContent || ''));
  }
  await page.evaluate(() => scrollTo(0, 0));
  await page.screenshot({ path: join(outDir, 'top.png') });
  Object.assign(checks, top, rest, { searchWorks: searchOk });
} catch (e) {
  checks.loadError = String(e).slice(0, 200); ok = false;
}
const jsPath = await (async () => { try { return null; } catch { return null; } })();
const hdr = {
  html: await head('/'), js: await head('/scripts/app.js'),
  img: checks.heroPath ? await head(checks.heroPath) : { status: 0 },
};
await browser.close(); srv.kill();
const must = {
  h1: checks.h1 === 'Turn beta feedback into a launch you can trust',
  heroVisibleNearTop: !!checks.heroLoaded && checks.heroTop !== null && checks.heroTop < 1400,
  sixFeatures: checks.features === 6 && checks.featuresLoaded === 6,
  logos: checks.logos === 5,
  promoBanner: !!checks.promo,
  testimonial: !!checks.testimonial,
  signup: !!checks.signup,
  searchWorks: !!checks.searchWorks,
  footer: !!checks.footer,
  brandFont: /Brand/.test(checks.h1Font || ''),
};
const result = { ok: ok && Object.values(must).every(Boolean), must, checks, errors: errors.slice(0, 10), headers: hdr };
writeFileSync(join(outDir, 'integrity.json'), JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
