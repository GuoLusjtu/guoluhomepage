# Homepage SEO Title Design

## Goal

Update only the homepage document title to improve search-result clarity while preserving all other metadata, content, styling, scripts, and behavior.

## Change

- Modify only the existing `<title>` element in root `index.html`.
- Replace `<title>GUO LU&#39;s Homepage</title>` with:

  `<title>Guo Lu (&#40065;&#22269;) | SJTU | Video Coding &amp; Generative AI</title>`

- The decoded browser/search-engine title must be exactly `Guo Lu (` followed by the two Chinese characters for the name, then `) | SJTU | Video Coding & Generative AI`.
- Use HTML character references for the Chinese name and ampersand so the source remains ASCII-safe and valid HTML while rendering the requested title exactly.

## Metadata boundary

- The current homepage has no `og:title` or `twitter:title`; do not add either field.
- Preserve the existing meta description, canonical URL, all other head markup, schema-related markup, CSS, JavaScript, layout, and visible body content byte-for-byte.
- Do not reformat `index.html` or touch any production file other than root `index.html`.

## Verification

- Add a regression test before changing production and observe the expected RED failure.
- Assert exactly one `<title>` exists and its decoded text equals the requested title.
- Assert no `og:title` or `twitter:title` field exists.
- Protect the remainder of `index.html` by canonicalizing only the old/new title element before a fixed byte-level hash comparison.
- Run the complete test suite, strict UTF-8 decoding, and `git diff --check`.
- Report the changed file, changed field, and the exact before/after diff. Do not push unless separately requested.
