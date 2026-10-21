# Platform notes for fix prompts

Detect the platform from URLs in the report, then write fixes the owner can actually apply.

| Signal in the report | Platform | Where fixes go |
|---|---|---|
| `cdn.prod.website-files.com`, `data-wf-*` attributes | Webflow | Webflow Designer (element/image settings, lazy load toggle, alt text), Page settings, Site settings > Custom code (head/footer), Site settings > Localization for `lang`. No repo; never edit generated CSS/JS. |
| `wp-content/`, `wp-includes/` | WordPress | Child theme templates, `functions.php` enqueue (defer, remove), caching/optimization plugin settings, media library. Name the file or setting. |
| `/_next/`, `/chunks/` | Next.js | `next/image` (priority on the hero), `next/font`, `next/script` strategy, server components to cut client JS, avoid hero entrance animations that start at opacity 0. |
| `hsappstatic.net`, `hs-scripts`, `hsforms`, `hubspot` | HubSpot (embeds or CMS) | HubSpot settings: tracking code, chat widget, forms embed. Owner: marketing ops. Load chat after interaction; reserve space for embedded forms. |
| `googletagmanager.com`, `gtag` | Google Tag Manager | Tag manager container: remove unused tags, change triggers to after load/consent. Owner: marketing ops. |
| Ad networks, `optimizely`, `doubleclick`, many third parties | Ad/experimentation stack | Owners: ad ops / growth. Fixes are vendor configuration, not app code. |
| `localhost` or files in a repo you can see | Code you can edit | Name files and functions. |

## Click-path hand-off format (no-code owners)
1. Where: the exact screen or menu path.
2. What to change: the setting and the new value, or the snippet to paste.
3. Check: what should look or measure different afterwards.
