// integrity_b.mjs <siteDir> <outDir> : functional checks for fixture B (served from siteDir/server.mjs)
import chromium from '@sparticuz/chromium';
import puppeteer from 'puppeteer-core';
import { FLAGS } from './chrome_flags.mjs';
import { spawn } from 'node:child_process';
import http from 'node:http';
import { writeFileSync, mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

const dir = resolve(process.argv[2]);
const outDir = resolve(process.argv[3] || dir + '-integrity');
mkdirSync(outDir, { recursive: true });
const port = 9100 + Math.floor(Math.random() * 800);
const srv = spawn(process.execPath, [join(dir, 'server.mjs'), String(port)], { cwd: dir, stdio: ['ignore', 'pipe', 'pipe'] });
await new Promise(ok => { srv.stdout.on('data', ok); setTimeout(ok, 3000); });
const base = `http://localhost:${port}`;
const head = path => new Promise(res => {
  const req = http.get({ host: 'localhost', port, path, headers: { 'Accept-Encoding': 'gzip, deflate, br' } }, r => {
    r.resume(); r.on('end', () => res({ status: r.statusCode, enc: r.headers['content-encoding'] || '', cache: r.headers['cache-control'] || '' }));
  });
  req.on('error', () => res({ status: 0 }));
});

const browser = await puppeteer.launch({ executablePath: await chromium.executablePath(), args: FLAGS, headless: true });
const errors = [];
async function openPage(path, cookie) {
  const ctx = await browser.createBrowserContext();
  const page = await ctx.newPage();
  await page.emulate({ viewport: { width: 412, height: 823, deviceScaleFactor: 1.75, isMobile: true, hasTouch: true },
    userAgent: 'Mozilla/5.0 (Linux; Android 11; moto g power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0 Mobile Safari/537.36' });
  const beacons = [];
  page.on('request', r => { if (new URL(r.url()).pathname === '/collect') { try { beacons.push(JSON.parse(r.postData() || '{}')); } catch { beacons.push({ raw: r.postData() }); } } });
  page.on('pageerror', e => errors.push(path + ' pageerror: ' + e.message.slice(0, 140)));
  await page.evaluateOnNewDocument(() => { window.__lt = 0; try { new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt += e.duration; }).observe({ type: 'longtask', buffered: true }); } catch {} });
  if (cookie) await page.setCookie({ name: 'tm_ab', value: cookie, url: base });
  await page.goto(base + path, { waitUntil: 'load', timeout: 60000 });
  await new Promise(r => setTimeout(r, 2500));
  return { ctx, page, beacons };
}
const checks = {};
try {
  for (const v of ['a', 'b']) {
    const { ctx, page, beacons } = await openPage('/', v);
    const r = await page.evaluate(() => {
      const hero = [...document.querySelectorAll('#hero-media img, .hero img, img')].find(i => /hero/.test(i.currentSrc || i.src));
      return { heroSrc: hero ? (hero.currentSrc || hero.src).split('/').pop() : null, heroOk: !!(hero && hero.complete && hero.naturalWidth > 0),
        heroTop: hero ? Math.round(hero.getBoundingClientRect().top + scrollY) : null, lt: Math.round(window.__lt || 0),
        h1: document.querySelector('h1')?.textContent.trim(), h1Font: getComputedStyle(document.querySelector('h1')).fontFamily,
        promo: document.body.innerText.includes('Trailmark AI summaries are live') };
    });
    checks['variant_' + v] = { ...r, beacons: beacons.map(b => b.e + (b.p && b.p.variant ? ':' + b.p.variant : '')) };
    if (v === 'a') {
      // carousel, menu, search, lazy images
      const first = await page.evaluate(() => [...document.querySelectorAll('#testimonial-track > *')].map(s => getComputedStyle(s).display).join(','));
      const btn = await page.$('#slide-next');
      if (btn) await btn.click();
      await new Promise(r => setTimeout(r, 300));
      const second = await page.evaluate(() => [...document.querySelectorAll('#testimonial-track > *')].map(s => getComputedStyle(s).display).join(','));
      checks.carousel = { before: first, after: second, works: !!btn && first !== second && /none/.test(second) };
      const mt = await page.$('.menu-toggle');
      if (mt) await mt.click();
      await new Promise(r => setTimeout(r, 300));
      checks.menuOpens = await page.evaluate(() => { const n = document.querySelector('nav.links'); return !!n && getComputedStyle(n).display !== 'none'; });
      for (let y = 0; y < 6000; y += 600) { await page.evaluate(y => scrollTo(0, y), y); await new Promise(r => setTimeout(r, 100)); }
      await new Promise(r => setTimeout(r, 1200));
      checks.featuresLoaded = await page.evaluate(() => [...document.querySelectorAll('.feature img')].filter(i => i.complete && i.naturalWidth > 0).length);
      checks.logosLoaded = await page.evaluate(() => [...document.querySelectorAll('.logos img')].filter(i => i.complete && i.naturalWidth > 0).length);
      const sb = await page.$('#search');
      if (sb) { await sb.focus(); await page.type('#search', 'pricing', { delay: 20 }); await new Promise(r => setTimeout(r, 2500)); }
      checks.searchWorks = await page.evaluate(() => /[1-9]\d* results/.test(document.getElementById('search-hits')?.textContent || ''));
      checks.ogImage = await page.evaluate(() => document.querySelector('meta[property="og:image"]')?.content || null);
      await page.evaluate(() => scrollTo(0, 0));
      await page.screenshot({ path: join(outDir, 'top-a.png') });
    }
    await ctx.close();
  }
  { // first visit, no cookie: variant chosen, sticky cookie set, exposure tracked
    const { ctx, page, beacons } = await openPage('/', null);
    const cookies = await page.cookies();
    checks.firstVisit = { cookie: cookies.find(c => c.name === 'tm_ab')?.value || null, beacons: beacons.map(b => b.e + (b.p && b.p.variant ? ':' + b.p.variant : '')) };
    await ctx.close();
  }
  { // pricing page
    const { ctx, page, beacons } = await openPage('/pricing.html', 'a');
    checks.pricing = await page.evaluate(() => {
      const card = document.querySelector('.grid-col-35');
      const ph = document.querySelector('.pricing-hero');
      const bg = ph ? getComputedStyle(ph).backgroundImage : '';
      return { prices: [...document.querySelectorAll('.price')].map(p => p.textContent.trim()),
        colMaxWidth: card ? getComputedStyle(card).maxWidth : null, gridDisplay: getComputedStyle(document.querySelector('.grid') || document.body).display,
        bg: (bg.match(/url\("?([^")]+)"?\)/) || [])[1] || null, h1: document.querySelector('h1')?.textContent.trim() };
    });
    checks.pricing.beacons = beacons.map(b => b.e);
    await page.screenshot({ path: join(outDir, 'pricing.png') });
    await ctx.close();
  }
} catch (e) { checks.loadError = String(e).slice(0, 240); }
await browser.close();
const bgPath = checks.pricing?.bg ? new URL(checks.pricing.bg, base).pathname : null;
const ogPath = checks.ogImage ? new URL(checks.ogImage, base).pathname : null;
const hdr = { html: await head('/'), js: await head('/js/app.js'), heroA: checks.variant_a?.heroSrc ? await head('/img/' + checks.variant_a.heroSrc) : { status: 0 },
  og: ogPath ? await head(ogPath) : { status: 0 }, pricingBg: bgPath ? await head(bgPath) : { status: 0 } };
srv.kill();
const va = checks.variant_a || {}, vb = checks.variant_b || {}, pr = checks.pricing || {};
const must = {
  T_ab_variant_a: /hero-a/.test(va.heroSrc || '') && va.heroOk,
  T_ab_variant_b: /hero-b/.test(vb.heroSrc || '') && vb.heroOk,
  T_ab_exposure_tracked: (va.beacons || []).includes('ab_exposure:a') && (vb.beacons || []).includes('ab_exposure:b'),
  T_ab_first_visit: !!checks.firstVisit?.cookie && (checks.firstVisit?.beacons || []).some(b => b.startsWith('ab_exposure')),
  T_pageview_tracked: (va.beacons || []).includes('pageview') && (pr.beacons || []).includes('pageview'),
  T_carousel: !!checks.carousel?.works,
  T_menu: !!checks.menuOpens,
  T_search: !!checks.searchWorks,
  T_pricing_layout: pr.colMaxWidth === '35%',
  T_prices_formatted: (pr.prices || []).includes('$1,200/yr') && (pr.prices || []).includes('$4,800/yr'),
  T_pricing_bg: hdr.pricingBg.status === 200,
  T_og_image: hdr.og.status === 200,
  T_content: va.h1 === 'Turn beta feedback into a launch you can trust' && !!va.promo && checks.featuresLoaded === 4 && checks.logosLoaded === 4,
  T_brand_font: /Brand/.test(va.h1Font || ''),
};
const result = { ok: Object.values(must).every(Boolean), must, checks, errors: errors.slice(0, 10), headers: hdr };
writeFileSync(join(outDir, 'integrity.json'), JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
