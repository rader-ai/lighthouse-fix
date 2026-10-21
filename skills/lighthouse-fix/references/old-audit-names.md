# Pre-Lighthouse-13 audit names mapped to current insights

| Old audit (Lighthouse ≤ 12) | Lighthouse 13+ insight |
|---|---|
| render-blocking-resources | render-blocking-insight |
| uses-optimized-images, modern-image-formats, uses-responsive-images, efficient-animated-content | image-delivery-insight |
| largest-contentful-paint-element, lcp-lazy-loaded, prioritize-lcp-image | lcp-breakdown-insight, lcp-discovery-insight |
| layout-shift-elements, layout-shifts (cause detail) | cls-culprits-insight |
| font-display | font-display-insight |
| server-response-time, redirects, uses-text-compression | document-latency-insight |
| uses-long-cache-ttl | cache-insight |
| critical-request-chains, uses-rel-preconnect | network-dependency-tree-insight |
| legacy-javascript | legacy-javascript-insight |
| duplicated-javascript | duplicated-javascript-insight |
| third-party-summary | third-parties-insight |
| dom-size | dom-size-insight |
| viewport | viewport-insight |
| uses-http2 | modern-http-insight |

Retired metrics: FID (replaced by INP in 2024), TTI, First Meaningful Paint, First CPU Idle. Never report them as current. The PWA category was removed in Lighthouse 12.
