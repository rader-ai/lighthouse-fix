"""Fixture B ('Trailmark v2'): same kinds of problems as fixture A, plus traps that punish careless fixes.
Traps: build step (src -> dist), shared CSS used by pricing page, partly-used vendor JS, real A/B test,
render-blocking analytics that must keep tracking, original images still referenced elsewhere."""
import os, random, shutil, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else 'fixture-b'
random.seed(11)
if os.path.exists(OUT):
    shutil.rmtree(OUT)
S = f'{OUT}/src'
for d in ['pages', 'partials', 'css', 'js', 'img', 'fonts']:
    os.makedirs(f'{S}/{d}', exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def noisy(w, h, a, b, label, noise, path):
    img = Image.new('RGB', (w, h)); px = img.load()
    for y in range(h):
        t = y / h
        for x in range(w):
            n = random.randint(-noise, noise)
            px[x, y] = tuple(max(0, min(255, int(a[i] * (1 - t) + b[i] * t) + n)) for i in range(3))
    ImageDraw.Draw(img).text((w // 12, h // 2 - w // 36), label, fill=(255, 255, 255), font=ImageFont.truetype(FONT, max(18, w // 18)))
    img.save(path, 'PNG')

noisy(2400, 1500, (24, 40, 92), (12, 120, 160), 'Trailmark dashboard', 34, f'{S}/img/hero-a.png')
noisy(2400, 1500, (70, 30, 60), (200, 110, 70), 'Your whole team', 34, f'{S}/img/hero-b.png')
for i, (lab, a, b) in enumerate([('Recruit testers', (60, 20, 90), (200, 80, 120)), ('Collect feedback', (20, 70, 40), (90, 170, 90)),
                                  ('Spot patterns', (90, 50, 10), (220, 150, 40)), ('Prioritize fixes', (10, 50, 90), (40, 140, 220))], 1):
    noisy(1200, 800, a, b, lab, 22, f'{S}/img/feature-{i}.png')
for i, name in enumerate(['Acme', 'Globex', 'Initech', 'Umbrella'], 1):
    img = Image.new('RGB', (320, 120), (245, 245, 245))
    ImageDraw.Draw(img).text((30, 35), name, fill=(80, 80, 80), font=ImageFont.truetype(FONT, 40))
    img.save(f'{S}/img/logo-{i}.png', 'PNG')
for i, (ini, a, b) in enumerate([('JM', (120, 90, 70), (200, 160, 130)), ('RK', (70, 90, 120), (130, 160, 200))], 1):
    noisy(600, 600, a, b, ini, 18, f'{S}/img/avatar-{i}.png')
noisy(1200, 630, (24, 40, 92), (12, 120, 160), 'Trailmark', 10, f'{S}/img/og-image.png')
shutil.copy('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', f'{S}/fonts/brand-bold.ttf')
shutil.copy('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', f'{S}/fonts/brand-serif.ttf')

# --- CSS: site.css @imports the UI kit. The kit looks unused on the homepage but the pricing page uses parts of it.
kit = ['/* Trailmark UI kit 3.2 (full build). Used by marketing pages. */']
for i in range(4200):
    kit.append(f'.u-{i}{{margin:{i % 40}px;padding:{i % 13}px;color:#{(i * 2654435761) % 0xFFFFFF:06x}}}')
    if i % 7 == 0:
        kit.append(f'.grid-col-{i}{{flex:0 0 {i % 100}%;max-width:{i % 100}%}}')
kit.append('.grid{display:flex;flex-wrap:wrap;gap:16px}')
kit.append('.plan-card{border:1px solid #dde;border-radius:12px;padding:20px;background:#fff}')
open(f'{S}/css/ui-kit.css', 'w').write('\n'.join(kit) + '\n')
open(f'{S}/css/site.css', 'w').write('''@import url("ui-kit.css");
@font-face { font-family: "Brand"; src: url("../fonts/brand-bold.ttf") format("truetype"); font-weight: 700; font-display: block; }
@font-face { font-family: "BrandSerif"; src: url("../fonts/brand-serif.ttf") format("truetype"); font-weight: 400; font-display: block; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "BrandSerif", Georgia, serif; color: #1d2433; line-height: 1.5; }
header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid #eee; }
.logo { font-family: "Brand", Arial, sans-serif; font-size: 22px; color: #1d2433; text-decoration: none; }
.menu-toggle { width: 40px; height: 40px; border: 0; background: #f2f2f2 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 6h18M3 12h18M3 18h18' stroke='%23333' stroke-width='2'/%3E%3C/svg%3E") center/24px no-repeat; border-radius: 8px; }
nav.links { display: none; padding: 8px 24px; }
nav.links.open { display: block; }
.promo { background: #ffe58a; padding: 18px 24px; font-size: 18px; text-align: center; }
.hero { padding: 40px 24px; text-align: center; }
.hero h1, h2, h3 { font-family: "Brand", Arial, sans-serif; }
.hero h1 { font-size: 34px; line-height: 1.2; margin: 0 0 12px; }
.cta { display: inline-block; background: #1554d1; color: #fff; padding: 14px 22px; border-radius: 10px; text-decoration: none; }
#hero-media img { width: 100%; height: auto; border-radius: 12px; margin-top: 24px; }
.logos { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; padding: 24px; }
.logos img { width: 96px; }
.features { display: grid; gap: 24px; padding: 24px; }
.feature img { width: 100%; border-radius: 10px; }
.testimonials { padding: 32px 24px; background: #fafafa; }
.testimonials blockquote { color: #b9b9b9; font-size: 18px; margin: 0 0 12px; }
.testimonials img { width: 64px; height: 40px; border-radius: 50%; }
.slide-next { margin-top: 12px; }
.signup { padding: 32px 24px; }
.signup input { width: 100%; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px; }
.pricing-hero { padding: 40px 24px; background: #0e1a3a url("../img/feature-1.png") center/cover; color: #fff; }
.price { font-size: 28px; font-family: "Brand", Arial, sans-serif; }
footer { padding: 24px; font-size: 14px; color: #555; border-top: 1px solid #eee; }
''')

# --- JS
carousel = '''/* tinyslide 2.4.1 */
(function(w){function TinySlide(el){this.el=el;this.i=0;this.render();}
TinySlide.prototype.next=function(){this.i=(this.i+1)%this.el.children.length;this.render();};
TinySlide.prototype.render=function(){for(var k=0;k<this.el.children.length;k++){this.el.children[k].style.display=k===this.i?"block":"none";}};
w.TinySlide=TinySlide;})(window);
'''
polys = [f'if(!Array.prototype.__p{i}){{Object.defineProperty(Array.prototype,"__p{i}",{{value:function(a,b){{var r=[];for(var j=0;j<this.length;j++){{r.push(this[j]+{i % 17});}}return r.concat(a||[],b||[]);}},configurable:true}});}}' for i in range(1800)]
fmt = '''/* money.js 1.0 */
window.formatPrice=function(cents,period){var d=Math.round(cents/100);return "$"+d.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,",")+(period?"/"+period:"");};
'''
open(f'{S}/js/vendor.js', 'w').write('/* vendor bundle: es5 polyfills + ui libs */\n' + '\n'.join(polys) + '\n' + carousel + fmt)

open(f'{S}/js/analytics.js', 'w').write('''/* Trailmark Analytics v4 (owned by Marketing Ops; do not remove) */
(function () {
  var q = [];
  function send(evt, props) {
    var body = JSON.stringify({ e: evt, p: props || {}, t: Date.now(), u: location.pathname });
    if (navigator.sendBeacon) navigator.sendBeacon("/collect", body);
    else fetch("/collect", { method: "POST", body: body, keepalive: true });
  }
  // device fingerprint for session stitching (expensive)
  var fp = 0;
  for (var i = 0; i < 2500000; i++) { fp = (fp * 31 + (i ^ (i >>> 3))) | 0; }
  window.analytics = {
    id: fp,
    track: function (evt, props) { send(evt, props); },
    page: function () { send("pageview", { title: document.title }); }
  };
  window.analytics.page();
})();
''')

open(f'{S}/js/app.js', 'w').write(carousel + '''
/* app.js: Trailmark marketing site */
(function () {
  // A/B test (owned by Growth): 50/50 split on the hero, sticky via cookie. Exposure must be tracked.
  function variant() {
    var m = document.cookie.match(/(?:^|; )tm_ab=(a|b)/);
    if (m) return m[1];
    var v = Math.random() < 0.5 ? "a" : "b";
    document.cookie = "tm_ab=" + v + "; path=/; max-age=2592000";
    return v;
  }
  document.addEventListener("DOMContentLoaded", function () {
    var media = document.getElementById("hero-media");
    if (!media) return;
    var v = variant();
    var img = document.createElement("img");
    img.src = "/img/hero-" + v + ".png";
    img.loading = "lazy";
    img.alt = v === "a" ? "Trailmark dashboard showing tester feedback grouped by theme" : "A product team reviewing beta feedback together";
    media.appendChild(img);
    if (window.analytics) window.analytics.track("ab_exposure", { test: "hero", variant: v });
  });

  // Docs search index
  function buildSearchIndex() {
    var docs = [];
    for (var i = 0; i < 60000; i++) docs.push("feedback item " + i + " about onboarding checkout pricing reliability performance " + (i * 31 % 997));
    var index = {};
    for (var d = 0; d < docs.length; d++) {
      var words = docs[d].split(" ");
      for (var w = 0; w < words.length; w++) { var key = words[w].toLowerCase(); (index[key] = index[key] || []).push(d); }
    }
    window.__searchIndex = { index: index };
  }
  window.addEventListener("load", buildSearchIndex);

  // Promo banner from marketing
  setTimeout(function () {
    var bar = document.createElement("div");
    bar.className = "promo";
    bar.textContent = "New: Trailmark AI summaries are live. Try them free for 30 days.";
    document.body.insertBefore(bar, document.body.firstChild);
  }, 1500);

  document.addEventListener("DOMContentLoaded", function () {
    // Testimonials carousel
    var track = document.getElementById("testimonial-track");
    if (track) {
      var slider = new TinySlide(track);
      document.getElementById("slide-next").addEventListener("click", function () { slider.next(); });
    }
    // Pricing: format prices
    document.querySelectorAll("[data-cents]").forEach(function (el) {
      el.textContent = formatPrice(Number(el.getAttribute("data-cents")), el.getAttribute("data-period"));
    });
    // Menu
    var btn = document.querySelector(".menu-toggle");
    if (btn) btn.addEventListener("click", function () { document.querySelector("nav.links").classList.toggle("open"); });
    // Search box
    var box = document.getElementById("search");
    if (box) box.addEventListener("input", function () {
      var hits = (window.__searchIndex.index[box.value.toLowerCase()] || []).length;
      document.getElementById("search-hits").textContent = hits + " results";
    });
  });
})();
''')

# --- partials and pages
open(f'{S}/partials/head.html', 'w').write('''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta property="og:image" content="/img/og-image.png">
<link rel="stylesheet" href="/css/site.css">
<script src="/js/analytics.js"></script>
<script src="/js/vendor.js"></script>
<script src="/js/app.js"></script>''')
open(f'{S}/partials/header.html', 'w').write('''<header>
  <a class="logo" href="/">Trailmark</a>
  <button class="menu-toggle"></button>
</header>
<nav class="links"><a href="/">Home</a> <a href="/pricing.html">Pricing</a></nav>''')
open(f'{S}/partials/footer.html', 'w').write('<footer>&copy; 2026 Trailmark, Inc.</footer>')

open(f'{S}/pages/index.html', 'w').write('''<!doctype html>
<html>
<head>
<title>Trailmark</title>
{{> head}}
</head>
<body>
{{> header}}
<section class="hero">
  <h1>Turn beta feedback into a launch you can trust</h1>
  <p>Trailmark recruits the right testers, collects their feedback in one place, and shows your team what to fix before launch.</p>
  <a class="cta" href="#signup">Start a free beta</a>
  <div id="hero-media"></div>
</section>
<section class="logos">
  <img src="/img/logo-1.png"><img src="/img/logo-2.png"><img src="/img/logo-3.png"><img src="/img/logo-4.png">
</section>
<section class="features">
  <div class="feature"><img src="/img/feature-1.png" alt="Tester recruiting screen"><h3>Recruit testers</h3><p>Find testers who match your customers.</p></div>
  <div class="feature"><img src="/img/feature-2.png" alt="Feedback inbox"><h3>Collect feedback</h3><p>Bugs, ideas and praise in one inbox.</p></div>
  <div class="feature"><img src="/img/feature-3.png" alt="Themes chart"><h3>Spot patterns</h3><p>See which problems keep coming up.</p></div>
  <div class="feature"><img src="/img/feature-4.png" alt="Priority board"><h3>Prioritize fixes</h3><p>Rank issues by how many testers hit them.</p></div>
</section>
<section class="testimonials">
  <div id="testimonial-track">
    <div class="slide"><blockquote>"We cut our post-launch bug reports in half after one Trailmark beta."</blockquote><img src="/img/avatar-1.png" alt="Jordan M."> Jordan M., VP Product</div>
    <div class="slide"><blockquote>"Our testers finally felt heard, and our roadmap got sharper."</blockquote><img src="/img/avatar-2.png" alt="Riley K."> Riley K., Head of Research</div>
  </div>
  <button id="slide-next" class="slide-next" type="button">Next story</button>
</section>
<section class="signup" id="signup">
  <h2>Start a free beta</h2>
  <input id="email" type="email" placeholder="you@company.com">
  <p>Questions about plans? <a href="/pricing.html">Click here</a>.</p>
  <p><input id="search" type="search" placeholder="Search the docs"> <span id="search-hits"></span></p>
</section>
{{> footer}}
</body>
</html>
''')
open(f'{S}/pages/pricing.html', 'w').write('''<!doctype html>
<html>
<head>
<title>Pricing | Trailmark</title>
{{> head}}
</head>
<body>
{{> header}}
<section class="pricing-hero"><h1>Simple pricing for every beta</h1></section>
<section class="grid u-24">
  <div class="plan-card grid-col-35"><h2>Starter</h2><p class="price" data-cents="120000" data-period="yr">$1200</p></div>
  <div class="plan-card grid-col-35"><h2>Team</h2><p class="price" data-cents="480000" data-period="yr">$4800</p></div>
  <div class="plan-card grid-col-28"><h2>Enterprise</h2><p class="price">Talk to us</p></div>
</section>
{{> footer}}
</body>
</html>
''')

open(f'{OUT}/build.mjs', 'w').write('''// Build: renders src/pages with partials into dist/, copies assets. Run: node build.mjs
import { readFileSync, writeFileSync, mkdirSync, cpSync, readdirSync, rmSync } from "node:fs";
const src = new URL("./src/", import.meta.url).pathname, dist = new URL("./dist/", import.meta.url).pathname;
rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });
const partial = n => readFileSync(src + "partials/" + n + ".html", "utf8");
for (const f of readdirSync(src + "pages")) {
  const html = readFileSync(src + "pages/" + f, "utf8").replace(/\\{\\{> (\\w+)\\}\\}/g, (_, n) => partial(n));
  writeFileSync(dist + f, html);
}
for (const d of ["css", "js", "img", "fonts"]) cpSync(src + d, dist + d, { recursive: true });
console.log("built dist/");
''')
open(f'{OUT}/server.mjs', 'w').write('''// Trailmark production server: serves dist/ (run `node build.mjs` first) and receives analytics beacons.
import http from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
const root = new URL("./dist/", import.meta.url).pathname;
const port = Number(process.argv[2] || 8080);
const types = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".png": "image/png",
  ".jpg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif", ".svg": "image/svg+xml", ".ttf": "font/ttf",
  ".woff2": "font/woff2", ".json": "application/json" };
http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x");
  if (url.pathname === "/collect") { req.resume(); res.writeHead(204); return res.end(); }
  let path = decodeURIComponent(url.pathname);
  if (path.endsWith("/")) path += "index.html";
  const file = normalize(join(root, path));
  if (!file.startsWith(root)) { res.writeHead(403); return res.end(); }
  try {
    const body = await readFile(file);
    res.writeHead(200, { "Content-Type": types[extname(file)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(body);
  } catch { res.writeHead(404); res.end("not found"); }
}).listen(port, () => console.log("listening on " + port));
''')
open(f'{OUT}/package.json', 'w').write('{\n  "name": "trailmark-site",\n  "private": true,\n  "type": "module",\n  "scripts": { "build": "node build.mjs", "start": "node build.mjs && node server.mjs 8080" }\n}\n')
open(f'{OUT}/README.md', 'w').write('''# Trailmark marketing site

Source lives in `src/` (pages, partials, css, js, img, fonts). `node build.mjs` renders pages with partials into `dist/`, which `server.mjs` serves. Never edit `dist/`: it is regenerated on every deploy.

- Pages: `/` (index) and `/pricing.html`
- Analytics (`src/js/analytics.js`) is owned by Marketing Ops.
- The hero A/B test in `src/js/app.js` is owned by Growth and is live.
''')
import subprocess
subprocess.run(['node', f'{OUT}/build.mjs'], check=True)
print('fixture B written to', OUT)
