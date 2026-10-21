// measure.mjs <siteDir> [runs=3] [outDir]
// Serves siteDir with its own server.mjs, runs Lighthouse (mobile, default simulated throttling) N times,
// prints median summary JSON, saves the median LHR as <outDir>/lhr.json.
import chromium from '@sparticuz/chromium';
import { FLAGS } from './chrome_flags.mjs';
import * as chromeLauncher from 'chrome-launcher';
import lighthouse from 'lighthouse';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

const dir = resolve(process.argv[2]);
const runs = Number(process.argv[3] || 3);
const outDir = resolve(process.argv[4] || dir + '-measure');
mkdirSync(outDir, { recursive: true });
const port = 8100 + Math.floor(Math.random() * 800);
const srv = spawn(process.execPath, [join(dir, 'server.mjs'), String(port)], { cwd: dir, stdio: ['ignore', 'pipe', 'pipe'] });
await new Promise((ok, bad) => { srv.stdout.on('data', ok); srv.on('exit', c => bad(new Error('server exited ' + c))); setTimeout(ok, 3000); });
const exe = await chromium.executablePath();
const chrome = await chromeLauncher.launch({ chromePath: exe, chromeFlags: FLAGS });
const results = [];
try {
  for (let i = 0; i < runs; i++) {
    const r = await lighthouse(`http://localhost:${port}/`, { port: chrome.port, output: 'json', logLevel: 'error',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'] });
    results.push(r.lhr);
  }
} finally { await chrome.kill(); srv.kill(); }
const perf = l => l.categories.performance.score ?? 0;
results.sort((a, b) => perf(a) - perf(b));
const med = results[Math.floor(results.length / 2)];
writeFileSync(join(outDir, 'lhr.json'), JSON.stringify(med));
const m = id => med.audits[id]?.numericValue;
const summary = {
  lighthouse: med.lighthouseVersion,
  scores: Object.fromEntries(Object.entries(med.categories).map(([k, v]) => [k, Math.round((v.score ?? 0) * 100)])),
  perfRuns: results.map(r => Math.round(perf(r) * 100)),
  metrics: { FCP_ms: Math.round(m('first-contentful-paint')), LCP_ms: Math.round(m('largest-contentful-paint')),
    TBT_ms: Math.round(m('total-blocking-time')), CLS: +(m('cumulative-layout-shift') ?? 0).toFixed(3), SI_ms: Math.round(m('speed-index')) },
  failing: Object.values(med.audits).filter(a => a.score !== null && a.score < 0.9 && !['notApplicable', 'informative', 'manual'].includes(a.scoreDisplayMode)).map(a => a.id).sort(),
};
writeFileSync(join(outDir, 'summary.json'), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
