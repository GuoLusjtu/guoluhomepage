# Cloudflare Web Analytics Design

## Goal

Add private, privacy-focused traffic analytics to the complete static GitHub Pages site without displaying a public visitor counter or changing hosting, DNS, or the site URL.

## Integration

Insert the following Cloudflare Web Analytics beacon exactly once in every repository HTML page, immediately before the closing `</body>` tag:

```html
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "7f0b11c30fc344bfb55c572509aea6d0"}'></script><!-- End Cloudflare Web Analytics -->
```

The current repository contains 31 deployable HTML pages. The beacon will therefore cover the homepage, 404 page, News archive, Publication and Project archives, and tag pages. The Cloudflare token is a public site identifier intended to appear in page source; no Cloudflare login, API token, password, cookie, or secret is stored in the repository.

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

- exactly 31 repository HTML pages are audited, excluding project-local `.worktrees`;
- every audited HTML page contains exactly one complete beacon snippet;
- each beacon uses the expected Cloudflare script URL and token;
- each beacon appears before the page's closing `</body>` tag;
- no public visitor-counter markup is added;
- all existing homepage cleanup and preservation tests continue to pass.

Serve the site locally and smoke-test the homepage, `/news/`, and one nested tag page before committing. Push only after the complete test suite, diff checks, and whole-branch review pass.
