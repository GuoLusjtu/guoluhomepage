# Cloudflare Web Analytics Design

## Goal

Add private, privacy-focused traffic analytics to the complete static GitHub Pages site without displaying a public visitor counter or changing hosting, DNS, or the site URL.

## Integration

Audit all 31 repository-filesystem HTML files outside the ignored `.worktrees` directory, partitioned as 19 full content pages and 12 Hugo redirect stubs. Insert the following Cloudflare Web Analytics beacon exactly once in each of the 19 full content pages, immediately before the closing `</body>` tag:

```html
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "7f0b11c30fc344bfb55c572509aea6d0"}'></script><!-- End Cloudflare Web Analytics -->
```

The 19 content pages cover the homepage, 404 page, News archive, Publication and Project archives, and canonical tag pages. The 12 small `tags/*/page/1/index.html` files are meta-refresh/canonical redirect stubs without a closing `</body>` tag. Preserve these redirect stubs byte-for-byte and do not install a beacon in them; their canonical destination pages are already instrumented, and adding analytics to the redirects could produce duplicate or unreliable events.

The Cloudflare token is a public site identifier intended to appear in page source; no Cloudflare login, API token, password, cookie, or secret is stored in the repository.

## Legacy analytics removal

All 19 content pages currently contain the obsolete Google Analytics Universal Analytics integration for property `UA-88925956-1`, including the `analytics.js` loader and an outbound-link event handler that calls `ga(...)`. Remove each complete legacy Google Analytics block. After this change, visitor analytics must be sent only to Cloudflare, with no remaining references to `www.google-analytics.com/analytics.js`, `UA-88925956-1`, `GoogleAnalyticsObject`, or `ga(...)` in audited repository-filesystem HTML outside `.worktrees`.

## User experience and privacy

- Add no visible counter, banner, widget, cookie prompt, or analytics link to the site.
- Keep the site layout and content unchanged.
- Load the beacon as a JavaScript module, matching the exact Cloudflare-generated snippet.
- View aggregated analytics only in the owner's private Cloudflare dashboard.
- Do not collect, expose, or store raw visitor IP addresses in this repository.
- Analytics begin only after deployment and cannot reconstruct historical visits.

## Dashboard

The owner will use Cloudflare Dashboard → Analytics & Logs → Web Analytics → `guolusjtu.github.io` to view visits, page views, paths, referrers, countries, devices, browsers, operating systems, and performance information.

## Verification

Extend the existing standard-library regression suite so it fails before implementation and then verifies:

- exactly 31 repository-filesystem HTML pages are audited, excluding project-local `.worktrees`, and partition into 19 content pages with `</body>` plus 12 redirect stubs without it;
- every content page contains exactly one complete beacon snippet using the expected Cloudflare script URL and token, placed before `</body>`;
- all 12 redirect stubs remain byte-for-byte unchanged and contain no Cloudflare beacon;
- the legacy Google Analytics loader, property ID, object initializer, and `ga(...)` calls are absent from all audited repository-filesystem HTML outside `.worktrees`;
- no public visitor-counter markup is added;
- all existing homepage cleanup and preservation tests continue to pass.

Serve the site locally and smoke-test the homepage, `/news/`, and one nested tag page before committing. Local smoke tests verify renderability and snippet presence but do not attempt to validate Cloudflare collection from `localhost`, whose hostname differs. Push only after the complete test suite, diff checks, and whole-branch review pass. After deployment, verify the live GitHub Pages source contains the correct beacon and confirm the first visit appears in the private Cloudflare dashboard after its normal processing delay.
