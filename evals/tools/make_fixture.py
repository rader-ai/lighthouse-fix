"""Generate the 'Trailmark' fixture: a realistic SaaS landing page with planted
Lighthouse problems across all five fix lanes. Answer key lives in
tools/answer_key.md, never inside the fixture repo."""
import os, random, shutil, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else 'fixture-a'
random.seed(7)
if os.path.exists(OUT):
    shutil.rmtree(OUT)
for d in ['img', 'styles', 'scripts', 'fonts']:
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def noisy(w, h, base, accent, label, noise, path):
    img = Image.new('RGB', (w, h), base)
    px = img.load()
    for y in range(h):
        t = y / h
        for x in range(w):
            n = random.randint(-noise, noise)
            r = int(base[0] * (1 - t) + accent[0] * t) + n
            g = int(base[1] * (1 - t) + accent[1] * t) + n
            b = int(base[2] * (1 - t) + accent[2] * t) + n
            px[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, max(18, w // 18))
    d.text((w // 12, h // 2 - w // 36), label, fill=(255, 255, 255), font=f)
    img.save(path, 'PNG')

# Hero: huge PNG (P1, P5)
noisy(2400, 1500, (24, 40, 92), (12, 120, 160), 'Trailmark dashboard', 34, f'{OUT}/img/hero-dashboard.png')
# Feature images: oversized PNGs, no dimensions in HTML (P4, P5)
feats = [('Recruit testers', (60, 20, 90), (200, 80, 120)), ('Collect feedback', (20, 70, 40), (90, 170, 90)),
         ('Spot patterns', (90, 50, 10), (220, 150, 40)), ('Prioritize fixes', (10, 50, 90), (40, 140, 220)),
         ('Share results', (70, 10, 30), (210, 60, 80)), ('Ship with confidence', (30, 30, 30), (120, 120, 140))]
for i, (lab, a, b) in enumerate(feats, 1):
    noisy(1200, 800, a, b, lab, 22, f'{OUT}/img/feature-{i}.png')
# Logos: small, missing alt in HTML (A1)
for i, name in enumerate(['Acme', 'Globex', 'Initech', 'Umbrella', 'Hooli'], 1):
    img = Image.new('RGB', (320, 120), (245, 245, 245))
    d = ImageDraw.Draw(img)
    d.text((30, 35), name, fill=(80, 80, 80), font=ImageFont.truetype(FONT, 40))
    img.save(f'{OUT}/img/logo-{i}.png', 'PNG')
# Testimonial avatar, wrong aspect ratio in HTML (B2)
noisy(600, 600, (120, 90, 70), (200, 160, 130), 'JM', 18, f'{OUT}/img/avatar-jm.png')

# Brand font: large TTF with font-display: block (P6)
shutil.copy('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', f'{OUT}/fonts/brand-bold.ttf')
shutil.copy('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', f'{OUT}/fonts/brand-serif.ttf')

# CSS: main.css @imports a large mostly-unused vendor.css (P2)
vendor_rules = []
for i in range(4200):
    vendor_rules.append(f'.u-{i}{{margin:{i % 40}px;padding:{i % 13}px;color:#{(i * 2654435761) % 0xFFFFFF:06x}}}')
    if i % 7 == 0:
        vendor_rules.append(f'.grid-col-{i}{{flex:0 0 {i % 100}%;max-width:{i % 100}%}}')
open(f'{OUT}/styles/vendor.css', 'w').write('/* UI kit v3.2 (full build) */\n' + '\n'.join(vendor_rules) + '\n')

open(f'{OUT}/styles/main.css', 'w').write('''@import url("vendor.css");
@font-face { font-family: "Brand"; src: url("../fonts/brand-bold.ttf") format("truetype"); font-weight: 700; font-display: block; }
@font-face { font-family: "BrandSerif"; src: url("../fonts/brand-serif.ttf") format("truetype"); font-weight: 400; font-display: block; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "BrandSerif", Georgia, serif; color: #1d2433; background: #fff; line-height: 1.5; }
header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid #eee; }
.logo { font-family: "Brand", Arial, sans-serif; font-size: 22px; }
.menu-toggle { width: 40px; height: 40px; border: 0; background: #f2f2f2 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 6h18M3 12h18M3 18h18' stroke='%23333' stroke-width='2'/%3E%3C/svg%3E") center/24px no-repeat; border-radius: 8px; }
nav.links { display: none; }
.promo { background: #ffe58a; padding: 18px 24px; font-size: 18px; text-align: center; }
.hero { padding: 40px 24px; text-align: center; }
.hero h1 { font-family: "Brand", Arial, sans-serif; font-size: 34px; line-height: 1.2; margin: 0 0 12px; }
.hero p { font-size: 18px; max-width: 640px; margin: 0 auto 20px; }
.hero .cta { display: inline-block; background: #1554d1; color: #fff; padding: 14px 22px; border-radius: 10px; text-decoration: none; font-family: "Brand", Arial, sans-serif; }
#hero-media img { width: 100%; height: auto; border-radius: 12px; margin-top: 24px; }
.logos { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; padding: 24px; }
.logos img { width: 96px; }
.features { display: grid; grid-template-columns: 1fr; gap: 24px; padding: 24px; }
.feature img { width: 100%; border-radius: 10px; }
.feature h3 { font-family: "Brand", Arial, sans-serif; margin: 12px 0 4px; }
.testimonial { padding: 32px 24px; background: #fafafa; }
.testimonial blockquote { color: #b9b9b9; font-size: 18px; margin: 0 0 12px; }
.testimonial img { width: 64px; height: 40px; border-radius: 50%; }
.signup { padding: 32px 24px; }
.signup input { width: 100%; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px; }
.signup button { margin-top: 12px; padding: 12px 18px; background: #1554d1; color: #fff; border: 0; border-radius: 8px; font-size: 16px; }
footer { padding: 24px; font-size: 14px; color: #555; border-top: 1px solid #eee; }
''')

# JS: vendor bundle with legacy polyfills + a duplicated carousel lib (P3)
carousel = '''/* tinyslide 2.4.1 */
(function(w){function TinySlide(el,o){this.el=el;this.i=0;this.o=o||{};}
TinySlide.prototype.next=function(){this.i=(this.i+1)%this.el.children.length;this.render();};
TinySlide.prototype.render=function(){for(var k=0;k<this.el.children.length;k++){this.el.children[k].style.display=k===this.i?"block":"none";}};
w.TinySlide=TinySlide;})(window);
'''
polys = []
for i in range(1800):
    polys.append(f'if(!Array.prototype.__p{i}){{Object.defineProperty(Array.prototype,"__p{i}",{{value:function(a,b){{var r=[];for(var j=0;j<this.length;j++){{r.push(this[j]+{i % 17});}}return r.concat(a||[],b||[]);}},configurable:true}});}}')
open(f'{OUT}/scripts/vendor.js', 'w').write('/* vendor bundle: es5 polyfills + ui libs */\n' + '\n'.join(polys) + '\n' + carousel)

open(f'{OUT}/scripts/app.js', 'w').write(carousel + '''
/* app.js: Trailmark marketing site */
(function () {
  // A/B test: choose hero variant, then insert the hero image
  var variant = Math.random() < 2 ? "dashboard" : "team";
  document.addEventListener("DOMContentLoaded", function () {
    var media = document.getElementById("hero-media");
    var img = document.createElement("img");
    img.src = "img/hero-" + variant + ".png";
    img.loading = "lazy";
    img.alt = "Trailmark dashboard showing tester feedback grouped by theme";
    media.appendChild(img);
  });

  // Build the client-side search index for the docs search box
  function buildSearchIndex() {
    var docs = [];
    for (var i = 0; i < 60000; i++) {
      docs.push("feedback item " + i + " about onboarding checkout pricing reliability performance " + (i * 31 % 997));
    }
    var index = {};
    for (var d = 0; d < docs.length; d++) {
      var words = docs[d].split(" ");
      for (var w = 0; w < words.length; w++) {
        var key = words[w].toLowerCase();
        (index[key] = index[key] || []).push(d);
      }
    }
    var sorted = Object.keys(index).sort(function (a, b) { return index[b].length - index[a].length; });
    window.__searchIndex = { index: index, top: sorted.slice(0, 50) };
  }
  window.addEventListener("load", buildSearchIndex);

  // Promo banner from the marketing team, injected at the top of the page
  setTimeout(function () {
    var bar = document.createElement("div");
    bar.className = "promo";
    bar.textContent = "New: Trailmark AI summaries are live. Try them free for 30 days.";
    document.body.insertBefore(bar, document.body.firstChild);
  }, 1500);

  // Search box
  document.addEventListener("DOMContentLoaded", function () {
    var box = document.getElementById("search");
    if (box) box.addEventListener("input", function () {
      var hits = (window.__searchIndex.index[box.value.toLowerCase()] || []).length;
      document.getElementById("search-hits").textContent = hits + " results";
    });
  });

  // Analytics
  trackPageview("home");
})();
''')

open(f'{OUT}/index.html', 'w').write('''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trailmark</title>
<link rel="stylesheet" href="styles/main.css">
<script src="scripts/vendor.js"></script>
<script src="scripts/app.js"></script>
</head>
<body>
<header>
  <span class="logo">Trailmark</span>
  <button class="menu-toggle"></button>
  <nav class="links"><a href="#features">Features</a> <a href="#signup">Pricing</a></nav>
</header>
<section class="hero">
  <h1>Turn beta feedback into a launch you can trust</h1>
  <p>Trailmark recruits the right testers, collects their feedback in one place, and shows your team what to fix before launch.</p>
  <a class="cta" href="#signup">Start a free beta</a>
  <div id="hero-media"></div>
</section>
<section class="logos">
  <img src="img/logo-1.png"><img src="img/logo-2.png"><img src="img/logo-3.png"><img src="img/logo-4.png"><img src="img/logo-5.png">
</section>
<section class="features" id="features">
  <div class="feature"><img src="img/feature-1.png" alt="Tester recruiting screen"><h3>Recruit testers</h3><p>Find testers who match your customers, not just whoever signs up first.</p></div>
  <div class="feature"><img src="img/feature-2.png" alt="Feedback inbox"><h3>Collect feedback</h3><p>Bugs, ideas and praise land in one inbox, tagged automatically.</p></div>
  <div class="feature"><img src="img/feature-3.png" alt="Themes chart"><h3>Spot patterns</h3><p>See which problems come up again and again.</p></div>
  <div class="feature"><img src="img/feature-4.png" alt="Priority board"><h3>Prioritize fixes</h3><p>Rank issues by how many testers hit them and how badly.</p></div>
  <div class="feature"><img src="img/feature-5.png" alt="Shareable report"><h3>Share results</h3><p>Send leadership a one-page readout with the numbers that matter.</p></div>
  <div class="feature"><img src="img/feature-6.png" alt="Launch checklist"><h3>Ship with confidence</h3><p>Know what's fixed, what's left, and what testers think of it.</p></div>
</section>
<section class="testimonial">
  <blockquote>"We cut our post-launch bug reports in half after one Trailmark beta."</blockquote>
  <img src="img/avatar-jm.png" alt="Jordan M."> <span>Jordan M., VP Product</span>
</section>
<section class="signup" id="signup">
  <h2>Start a free beta</h2>
  <input id="email" type="email" placeholder="you@company.com">
  <button type="button">Get started</button>
  <p>Questions about plans? <a href="/pricing">Click here</a>.</p>
  <p><input id="search" type="search" placeholder="Search the docs"> <span id="search-hits"></span></p>
</section>
<footer>&copy; 2026 Trailmark, Inc.</footer>
</body>
</html>
''')

open(f'{OUT}/server.mjs', 'w').write('''// Trailmark static server (production)
import http from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";

const root = new URL(".", import.meta.url).pathname;
const port = Number(process.argv[2] || 8080);
const types = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif",
  ".svg": "image/svg+xml", ".ttf": "font/ttf", ".woff2": "font/woff2", ".json": "application/json" };

http.createServer(async (req, res) => {
  let path = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (path.endsWith("/")) path += "index.html";
  const file = normalize(join(root, path));
  if (!file.startsWith(root)) { res.writeHead(403); return res.end(); }
  try {
    const body = await readFile(file);
    res.writeHead(200, { "Content-Type": types[extname(file)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(body);
  } catch {
    res.writeHead(404); res.end("not found");
  }
}).listen(port, () => console.log("listening on " + port));
''')

open(f'{OUT}/README.md', 'w').write('''# Trailmark marketing site

Static landing page for trailmark.example. Serve locally with `node server.mjs 8080` and open http://localhost:8080/.

- `index.html`: the page
- `styles/`: site CSS and the UI kit
- `scripts/`: vendor bundle and site scripts
- `img/`, `fonts/`: assets
- `server.mjs`: the production static server
''')
print('fixture written to', OUT)
for root, _, files in os.walk(OUT):
    for f in files:
        p = os.path.join(root, f)
        print(f'{os.path.getsize(p) / 1024:9.0f} KB  {os.path.relpath(p, OUT)}')
